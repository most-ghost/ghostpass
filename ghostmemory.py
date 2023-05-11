
import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import qtwidgets as qte # As in Qt Extra



class SettingsDialog(qtw.QDialog):
    """Dialog for changing settings."""
    def __init__(self, settings, parent=None): # Since we want this to be a floating box unlinked to another, we unset 'parent', I suppose. Since this is going to be a settings box we include our own variable for settings to be input.
        super().__init__(parent, modal=False) # Note how Modal is set.

        
        font_id = qtg.QFontDatabase.addApplicationFont('ghostpass/typewcond_demi.otf')
        font_family = qtg.QFontDatabase.applicationFontFamilies(font_id)[0]
        font_typewriter = qtg.QFont(font_family)
        font_typewriter.setPointSize(15)

        self.setFont(font_typewriter)


        self.setLayout(qtw.QFormLayout())
        
        self.widget_hash_length = qtw.QSpinBox()
        self.widget_word_length = qtw.QSpinBox()
        self.widget_hash_or_word = qtw.QComboBox()
        self.widget_hash_or_word.addItem("hash", 1)
        self.widget_hash_or_word.addItem("word", 2)
        self.widget_visible_pass = qte.AnimatedToggle(
            pulse_checked_color="#00000000", # First two letters are alpha
            pulse_unchecked_color="#00000000"
            )
        self.widget_visible_pass.setFixedHeight(int(self.widget_visible_pass.sizeHint().height() / 2))
        self.widget_disable_logo = qte.AnimatedToggle(
            pulse_checked_color="#00000000", # First two letters are alpha
            pulse_unchecked_color="#00000000"
            )
        self.widget_disable_logo.setFixedHeight(int(self.widget_disable_logo.sizeHint().height() / 2))

        
        

        self.settings = settings
        self.layout().addRow(
            qtw.QLabel('<h1>ghostpass</h1>'),
        )
        self.layout().addRow(
            qtw.QLabel('<h6></h6>'),
        )
        self.layout().addRow(
            qtw.QLabel('<h2>app settings</h3>'),
        )
        self.layout().addRow("passwords visible by default", self.widget_visible_pass)
        self.layout().addRow("disable ghostpass logo", self.widget_disable_logo)
        self.layout().addRow(
            qtw.QLabel('<h6></h6>'),
        )
        self.layout().addRow(
            qtw.QLabel('<h2>stack settings</h3>'),
        )
        self.layout().addRow("default stack type", self.widget_hash_or_word)
        self.layout().addRow("default character length for hash", self.widget_hash_length)
        self.layout().addRow("default number of words for passphrase", self.widget_word_length)
        self.layout().addRow(
            qtw.QLabel('<h6></h6>'),
        )





        # self.show_warnings_cb = qtw.QCheckBox( # cb as in checkbox.
        #     checked = settings.get('show_warnings')
        # )
        # self.layout().addRow("Show Warnings", self.show_warnings_cb)
        # self.test = qte.AnimatedToggle()
        # self.layout().addRow("Toggle", self.test)
        
        # This stuff below is a big reason to use QDialog- it comes with these accept and reject slots, which we're assigning to buttons here.
        self.accept_btn = qtw.QPushButton('Ok', clicked = self.accept)
        self.cancel_btn = qtw.QPushButton('Cancel', clicked = self.reject)
        self.layout().addRow(self.accept_btn, self.cancel_btn)
        
    def accept(self): # We're going to do a slight variant on the built in accept
        self.settings['show_warnings'] = self.show_warnings_cb.isChecked() # ... so that we can alter the settings dict to match our choices
        super().accept() # Then we go ahead and trigger the regular accept() from the parent.



### PLACEHOLDER STUFF DOWN BELOW

class MainWindow (qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Put your code in here



        self.settings = {'show_warnings' : True}


        button = qtw.QPushButton("settings")
        button.clicked.connect(self.show_settings)
        self.setCentralWidget(button)

        self.show()

        self.show_settings()


        # End here

    def show_settings(self):
        settings_dialog = SettingsDialog(self.settings, self) # I'm not entirely sure what the deal with this second 'self' is. It's related to the no parent thing above, but how exactly, I'm not sure.
        settings_dialog.exec()

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())