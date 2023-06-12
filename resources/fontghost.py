import os
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import pyqtSlot

class fontghost(qtc.QObject):
    """
    Since most of my widgets need a font, we'll put the boilerplate here instead of copy+pasting it every time.
    """

    def typewriter(size):
        font_id = qtg.QFontDatabase.addApplicationFont(
            os.path.join(
            os.path.dirname(__file__), "typewcond_demi.otf"))
        font_family = qtg.QFontDatabase.applicationFontFamilies(font_id)[0]
        final_font = qtg.QFont(font_family)
        final_font.setPointSize(size)
        return final_font
    
    def roboto(size):
        font_id = qtg.QFontDatabase.addApplicationFont(
            os.path.join(
            os.path.dirname(__file__), "roboto.ttf"))
        font_family = qtg.QFontDatabase.applicationFontFamilies(font_id)[0]
        final_font = qtg.QFont(font_family)
        final_font.setPointSize(size)
        return final_font
