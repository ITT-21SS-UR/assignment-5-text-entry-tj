from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter

# https://stackoverflow.com/questions/28956693/pyqt5-qtextedit-auto-completion


class MyTextEdit(QtWidgets.QTextEdit):

    def __init__(self,*args):
        #*args to set parent
        QtWidgets.QLineEdit.__init__(self,*args)
        font= QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
        self.completer = None

    def setCompleter(self, completer):
        print('TADA')
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer = completer
#        self.connect(self.completer,
#            QtCore.SIGNAL("activated(const QString&)"), self.insertCompletion)
        self.completer.insertText.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) - len(self.completer.completionPrefix()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    #---override
    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self);
        QtWidgets.QTextEdit.focusInEvent(self, event)

    #---override
    def keyPressEvent(self, event):
        if self.completer and self.completer.popup() and self.completer.popup().isVisible():
            if event.key() in (
            QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Return,
            QtCore.Qt.Key_Escape,
            QtCore.Qt.Key_Tab,
            QtCore.Qt.Key_Backtab):
                event.ignore()
                return
        ## has ctrl-Space been pressed??
        print(event.modifiers())
        print(QtCore.Qt.ControlModifier)

        isShortcut = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_S)
        ## modifier to complete suggestion inline ctrl-e
        inline = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_E)
        ## if inline completion has been chosen
        if inline:
            # set completion mode as inline
            self.completer.setCompletionMode(QtWidgets.QCompleter.InlineCompletion)
            completionPrefix = self.textUnderCursor()
            if (completionPrefix != self.completer.completionPrefix()):
                self.completer.setCompletionPrefix(completionPrefix)
            self.completer.complete()
#            self.completer.setCurrentRow(0)
#            self.completer.activated.emit(self.completer.currentCompletion())
            # set the current suggestion in the text box
            self.completer.insertText.emit(self.completer.currentCompletion())
            # reset the completion mode
            self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            return
        if (not self.completer or not isShortcut):
        # if not self.completer:
            print("here")
            pass
            QtWidgets.QTextEdit.keyPressEvent(self, event)
        # debug
#        print("After controlspace")
#        print("isShortcut is: {}".format(isShortcut))
        # debug over
        ## ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier , QtCore.Qt.ShiftModifier)
        if ctrlOrShift and event.text() == '':
            print('hello')
#             ctrl or shift key on it's own
            return
        # debug
#        print("After on its own")
#        print("isShortcut is: {}".format(isShortcut))
        # debug over
#         eow = QtCore.QString("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=") #end of word
#        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=" #end of word
        eow = "~!@#$%^&*+{}|:\"<>?,./;'[]\\-=" #end of word

        hasModifier = ((event.modifiers() != QtCore.Qt.NoModifier) and not ctrlOrShift)

        completionPrefix = self.textUnderCursor()
#         print('event . text = {}'.format(event.text().right(1)))
#         if (not isShortcut and (hasModifier or event.text()=='' or\
#                                 len(completionPrefix) < 3 or \
#                                 eow.contains(event.text().right(1)))):
        if not isShortcut :
            if self.completer.popup():
                self.completer.popup().hide()
            return
#        print("complPref: {}".format(completionPrefix))
#        print("completer.complPref: {}".format(self.completer.completionPrefix()))
#        print("mode: {}".format(self.completer.completionMode()))
#        if (completionPrefix != self.completer.completionPrefix()):
        self.completer.setCompletionPrefix(completionPrefix)
        popup = self.completer.popup()
        popup.setCurrentIndex(
            self.completer.completionModel().index(0,0))
        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr) ## popup it up!


class EnhanceInput(QtWidgets.QCompleter):

    insertText = QtCore.pyqtSignal(str)

    def __init__(self, word_list):
        super(EnhanceInput, self).__init__()
        self.word_list = word_list
        # self.connect(self, QtCore.SIGNAL("activated(const QString&)"), self.changeCompletion)

    def changeCompletion(self, completion):
        if completion.find("(") != -1:
            completion = completion[:completion.find("(")]
        print(completion)
        self.insertText.emit(completion)

    def set_auto_complete(self, edit_text):
        completer = QCompleter(self.word_list)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        edit_text.setCompleter(completer)
        print('hallo')

