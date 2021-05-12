#!/usr/bin/python

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout

from text_input_technique import EnhanceInput


class SpeedTest(QtWidgets.QWidget):

    # init all necessary variables
    def __init__(self, text, participant_id):
        super(SpeedTest, self).__init__()
        self.text = text
        self.id = participant_id
        self.word_list = self.text.replace('\n', ' ').split(' ')
        self.sentence_count = 0
        self.sentence_list = self.text.split('\n')
        self.num_sentences = len(self.sentence_list)
        self.word_time = []
        self.word = ""
        self.sentence = ""
        self.timer_sentence = QtCore.QTime()
        self.timer_word = QtCore.QTime()
        self.started = False
        self.finished_word = False
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
        # text edit
        self.text_edit = QtWidgets.QTextEdit(self)
        technique = EnhanceInput(self.word_list)
        technique.set_auto_complete(self.text_edit)
        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.instructions)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        self.show()

    # logs test data
    def log_data(self):
        timestamp = QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)
        word_count, avg_word_len, avg_word_time = self.analyze_sentence(self.sentence_count)
        sentence_length = len(self.sentence_list[self.sentence_count-1])
        sentence_time = self.stop_time_sentence()
        wpm = self.words_per_minute(sentence_length, sentence_time, avg_word_len)
        sys.stdout.write("%s,%s,%d,%d,%d,%d,%d,%d,%d\n" %
                         (timestamp, self.id, self.sentence_count, sentence_length, sentence_time,
                          word_count, avg_word_len, avg_word_time, wpm))

    # analyzes current sentence
    def analyze_sentence(self, num):
        sentence = self.sentence_list[num-1]
        word_count = len(sentence.split(' '))
        avg_word_len = len(sentence.replace(' ', ''))/word_count
        time = 0
        for i in self.word_time:
            time += i
        avg_word_time = time / word_count
        return word_count, avg_word_len, avg_word_time

    # calculates word per minute
    def words_per_minute(self, sentence_len, sentence_time, avg_word_length):
        return ((sentence_len/(sentence_time/1000))*60)/avg_word_length

    # handles event when key is released
    def keyReleaseEvent(self, event):
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
                sys.stdout.write('Key pressed: Space \n')
                sys.stdout.write('Word typed: ' + self.word + '\n')
                self.sentence += ' '
                self.word = ""
                self.finished_word = True
            elif event.key() == QtCore.Qt.Key.Key_Return:
                self.word_time.append(self.stop_time_word())
                sys.stdout.write('Key pressed: Enter \n')
                sys.stdout.write('Word typed: ' + self.word + '\n')
                self.word = ""
                sys.stdout.write('Sentence typed: ' + self.sentence + '\n')
                self.sentence = ""
                self.log_data()
                self.started = False
                if self.sentence_count == self.num_sentences:
                    sys.stdout.write('Test finished')
                    # sys.stderr.write("Finished!")
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
