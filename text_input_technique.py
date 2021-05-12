from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter


class EnhanceInput(QtWidgets.QWidget):

    def __init__(self, word_list):
        super(EnhanceInput, self).__init__()
        self.word_list = word_list

    def set_auto_complete(self, edit_text):
        completer = QCompleter(self.word_list)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        edit_text.setCompleter(completer)
        print('hallo')
