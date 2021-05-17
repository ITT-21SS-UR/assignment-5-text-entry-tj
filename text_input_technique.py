#!usr/bin/python

import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtWidgets import QVBoxLayout, QCompleter

# got ideas of these three links but mostly used the last one, cause it fitted our style the most, used logic is
# in all three basically the same and was adjusted to fit our requirements
# https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion
# http://rowinggolfer.blogspot.com/2010/08/qtextedit-with-autocompletion-using.html
# https://github.com/baoboa/pyqt5/blob/master/examples/tools/customcompleter/customcompleter.py

# the workload was distributed evenly between the two team members


# class implements input method (completer)
class TextEdit(QtWidgets.QTextEdit):
    # init all necessary variables
    def __init__(self, speed_test, parent=None):
        super(TextEdit, self).__init__(parent)
        self.speed_test = speed_test
        self.completer = None
        self.auto_completed = False
        self.word = ''
        self.extra = 0
        self.sentence_count = 0
        self.word_time = []
        self.word = ""
        self.sentence = ""
        self.timer_sentence = QtCore.QTime()
        self.timer_word = QtCore.QTime()
        self.started = False
        self.finished_word = False

    # sets completer
    def set_completer(self, c):
        if self.completer is not None:
            self.completer.activated.disconnect()
        self.completer = c
        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(Qt.CaseInsensitive)
        c.activated.connect(self.insert_completion)

    # returns completer
    def completer(self):
        return self.completer

    # returns index of current sentence
    def get_sentence_count(self):
        return self.sentence_count

    def get_word_time(self):
        return self.word_time

    # inserts the missing piece of word
    def insert_completion(self, completion):
        if self.completer.widget() is not self:
            return
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        if extra == 0:
            tc.insertText('')
        else:
            tc.insertText(completion[-extra:])
        self.setTextCursor(tc)
        self.auto_completed = True
        self.word = completion
        self.extra = len(completion) - extra
        sys.stdout.write('Autocomplete: ' + completion + '\n')

    # returns text which is already written
    def text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    # sets focus
    def focusInEvent(self, e):
        if self.completer is not None:
            self.completer.setWidget(self)
        super(TextEdit, self).focusInEvent(e)

    def keyPressEvent(self, e):
        self.handle_input(e)
        if self.completer is not None and self.completer.popup().isVisible():
            # The following keys are forwarded by the completer to the widget.
            if e.key() in (Qt.Key_Enter, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                # Let the completer do default behavior.
                return
        # use <TAB> to get a auto-complete suggestion
        is_shortcut = ((e.modifiers() & Qt.ControlModifier) != 0 and e.key() == Qt.Key_Tab)
        if self.completer is None or not is_shortcut:
            # Do not process the shortcut when we have a completer.
            super(TextEdit, self).keyPressEvent(e)
        if self.completer is None:
            return
        completion_prefix = self.text_under_cursor()
        if not is_shortcut and (len(e.text()) == 0 or len(completion_prefix) < 3):
            self.completer.popup().hide()
            return
        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) +
                    self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    # handles the input and gets data for logging
    def handle_input(self, event):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                   't', 'u', 'v', 'w', 'x', 'y', 'z', 'ä', 'ö', 'ü']
        # when a sentence has not yet begun
        if not self.started:
            self.started = True
            self.start_time_sentence()
            self.start_time_word()
            self.sentence_count += 1
            self.word_time = []
        # when a word is finished
        if self.finished_word:
            self.start_time_word()
            self.finished_word = False
        # when the sentence has started
        if self.started:
            if event.text() in letters:
                self.word += event.text()
                self.sentence += event.text()
                sys.stdout.write('Key pressed: ' + str(event.text()) + '\n')
            elif event.key() == QtCore.Qt.Key.Key_Space:
                self.word_time.append(self.stop_time_word())
                if self.auto_completed:
                    self.auto_completed = False
                    self.sentence = self.sentence[:-self.extra]
                    self.sentence += self.word
                sys.stdout.write('Key pressed: Space \n')
                sys.stdout.write('Word typed: ' + self.word + '\n')
                self.sentence += ' '
                self.word = ""
                self.finished_word = True
            elif event.key() == QtCore.Qt.Key.Key_Return:
                self.word_time.append(self.stop_time_word())
                if self.auto_completed:
                    self.auto_completed = False
                    self.sentence = self.sentence[:-self.extra]
                    self.sentence += self.word
                sys.stdout.write('Key pressed: Enter \n')
                sys.stdout.write('Word typed: ' + self.word + '\n')
                self.word = ""
                sys.stdout.write('Sentence typed: ' + self.sentence + '\n')
                self.sentence = ""
                self.speed_test.log_data()
                self.started = False
                if self.sentence_count == self.speed_test.get_num_sentences():
                    #sys.stdout.write('Test finished')
                    sys.exit(1)
            elif event.key() == QtCore.Qt.Key.Key_Backspace:
                sys.stdout.write('Key pressed: Delete \n')
                self.word = self.word[:-1]
                self.sentence = self.sentence[:-1]

    # start timer for sentence
    def start_time_sentence(self):
        self.timer_sentence.start()

    # stops timer for sentence
    def stop_time_sentence(self):
        elapsed = self.timer_sentence.elapsed()
        return elapsed

    # starts timer for word
    def start_time_word(self):
        self.timer_word.start()

    # stops timer for word
    def stop_time_word(self):
        elapsed = self.timer_word.elapsed()
        return elapsed


# class for logging and setup
class SpeedTest(QtWidgets.QWidget):

    # init all necessary variables
    def __init__(self, text, participant_id):
        super(SpeedTest, self).__init__()
        self.text = text
        self.id = participant_id
        self.word_list = list(set(self.text.replace('\n', ' ').lower().split(' ')))
        self.sentence_list = self.text.split('\n')
        self.num_sentences = len(self.sentence_list)
        self.init_ui()
        sys.stdout.write("timestamp_ISO,id,sentence_count,sentence_length,sentence_time_in_ms,"
                         "word_count,avg_word_length,avg_word_time_in_ms,words_per_minute\n")

    # init interface
    def init_ui(self):
        self.showMaximized()
        self.setWindowTitle('Speed Test')
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # display text to be written
        self.instructions = QtWidgets.QLabel(self)
        self.instructions.setAlignment(QtCore.Qt.AlignCenter)
        self.instructions.setFont(QFont('Arial', 20))
        self.instructions.setText(self.text)
        # text edit with completer
        self.text_edit = TextEdit(self)
        self.completer = QCompleter(self.word_list)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setWrapAround(False)
        self.text_edit.set_completer(self.completer)
        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.instructions)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        self.show()

    # logs test data
    def log_data(self):
        timestamp = QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)
        word_count, avg_word_len, avg_word_time = self.analyze_sentence(self.text_edit.get_sentence_count())
        sentence_length = len(self.sentence_list[self.text_edit.get_sentence_count()-1])
        sentence_time = self.text_edit.stop_time_sentence()
        wpm = self.words_per_minute(sentence_length, sentence_time, avg_word_len)
        sys.stdout.write("%s,%s,%d,%d,%d,%d,%d,%d,%d\n" %
                         (timestamp, self.id, self.text_edit.get_sentence_count(), sentence_length, sentence_time,
                          word_count, avg_word_len, avg_word_time, wpm))

    # analyzes current sentence
    def analyze_sentence(self, num):
        sentence = self.sentence_list[num - 1]
        word_count = len(sentence.split(' '))
        avg_word_len = len(sentence.replace(' ', '')) / word_count
        time = 0
        for i in self.text_edit.get_word_time():
            time += i
        avg_word_time = time / word_count
        return word_count, avg_word_len, avg_word_time

    # calculates word per minute
    def words_per_minute(self, sentence_len, sentence_time, avg_word_length):
        return ((sentence_len/(sentence_time/1000))*60)/avg_word_length

    # returns the amount of sentences
    def get_num_sentences(self):
        return self.num_sentences


def main():
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) < 3:
        sys.stderr.write("Need .txt file with text to be written and an participant id")
        sys.exit(1)
    text = get_text(sys.argv[1])
    speed_test = SpeedTest(text, sys.argv[2])
    sys.exit(app.exec())


# extracts text from file
def get_text(filename):
    text = ""
    file = open(filename).readlines()
    for i in file:
        text += i
    return text


if __name__ == '__main__':
    main()
