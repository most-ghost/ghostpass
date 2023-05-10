from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import qtwidgets as qte # As in Qt Extra
import ghostlogic

logic = ghostlogic.logic()


class Q_stack_widget(qtw.QFrame):

    signal_delete = qtc.pyqtSignal(qtc.QObject)

    def __init__(self, pass_widget, salt_widget, settings, domain):
        super().__init__()
        self.settings = settings

        self.pass_widget = pass_widget
        self.salt_widget = salt_widget

        self.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Fixed
        )
        self.setFixedHeight(95)
        self.setMinimumWidth(50)

        self.setLineWidth(2)
        self.setFrameStyle(qtw.QFrame.Panel | qtw.QFrame.Sunken)

        layout_stack = qtw.QHBoxLayout()
        self.setLayout(layout_stack)

        self.widget_domain = qtw.QLineEdit(domain)
        self.widget_domain.setFixedWidth(100)
        self.widget_domain.textEdited.connect(
            lambda : self.widget_domain.setText(self.widget_domain.text().lower()))
        # This is a bit of a clunky way to force lower case, but it works without having to set a validator.
        # Maybe there's a potential use where a user needs to have passwords for both Google and google,
        # but I think it's more likely that having the option to mix and match, when a single letter capitalized
        # means a totally different hash, is just going to lead to potential headaches.
        layout_stack.addWidget(self.widget_domain)

        self.widget_gen_field = qtw.QLineEdit(
            self,
            readOnly = True,
            placeholderText = ''
            )
        self.widget_gen_field.mouseReleaseEvent = lambda _: self.force_highlight(self.widget_gen_field)
        layout_stack.addWidget(self.widget_gen_field) 

        structure_phrase = qtw.QWidget()
        structure_phrase.setFixedWidth(75)
        layout_phrase = qtw.QVBoxLayout(structure_phrase)
        self.widget_phrase_toggle = qte.AnimatedToggle(
            pulse_checked_color="#00000000", # First two letters are alpha
            pulse_unchecked_color="#00000000"
            )
        self.widget_phrase_toggle.clicked.connect(self.phrase_clicked)
        layout_phrase.addWidget(self.widget_phrase_toggle)
        self.widget_size_phrase = qtw.QSpinBox()
        self.widget_size_phrase.wheelEvent = lambda _: None 
        # I'm sure there are 4 or 5 people who use the mouse wheel to activate one of these. 
        # For everyone else, the mouse wheel is there to scroll the window, not screw with values.
        # There's nothing worse than trying to scroll the window and instead the mouse catches on a
        # value box for a moment and stops scrolling and starts adjusting the thing in the box instead.
        layout_phrase.addWidget(self.widget_size_phrase)
        layout_stack.addWidget(structure_phrase)
        layout_phrase.widget

        self.widget_gen_button = qtw.QPushButton('Gen')
#        self.widget_gen_button.setSizePolicy(
#            qtw.QSizePolicy.Fixed,
#            qtw.QSizePolicy.Maximum)
        self.widget_gen_button.setFixedSize(qtc.QSize(45, 75))
        self.widget_gen_button.clicked.connect(self.generating_pass)
        layout_stack.addWidget(self.widget_gen_button)

        widget_del_button = qtw.QPushButton('-')
        # widget_del_button.setFixedSize(qtc.QSize(30, 75))
        widget_del_button.setFixedWidth(30)
        widget_del_button.setFixedSize
        widget_del_button.clicked.connect(self.requesting_delete)
        layout_stack.addWidget(widget_del_button)


        self.initialize_values()






    def requesting_delete(self):
        self.signal_delete.emit(self)

    def generating_pass(self):
        password = self.pass_widget.text()
        salt = self.salt_widget.text()
        size = self.widget_size_phrase.value()
        domain = self.widget_domain.text()
        if password == '':
            self.widget_gen_field.setPlaceholderText('Please enter a password.')
        else:
            if self.phrase_toggle_state == 2:
                self.widget_gen_field.setText(logic.hash_gen(domain, password, size, salt))
            elif self.phrase_toggle_state == 0:
                self.widget_gen_field.setText(logic.pass_phrase_gen(domain, password, size, salt))
            self.widget_gen_field.setCursorPosition(0)

    def fake_gen_click(self):
        self.widget_gen_button.click()

    def force_highlight(self, gen_field):
        gen_field.end(False)
        gen_field.home(True)

    def phrase_clicked(self):
        self.phrase_toggle_state = self.widget_phrase_toggle.checkState()
        self.change_max_type()
        
    def change_max_type(self, secure=128, phrase=10):
        slider = self.widget_phrase_toggle
        spinbox = self.widget_size_phrase
        if slider.checkState() == 2: # Secure
            spinbox.setMaximum(128)
            spinbox.setMinimum(20)
            spinbox.setValue(secure)
        if slider.checkState() == 0: # Passphrase
            spinbox.setMaximum(20)
            spinbox.setMinimum(6)
            spinbox.setValue(phrase)

    def save_settings(self):
        domain = self.widget_domain.text()
        phrase_state = self.widget_phrase_toggle.checkState()
        gen_size = self.widget_size_phrase.value()
        
        self.settings.setValue(f'Domains/{domain}', f'{phrase_state}|{gen_size}')


        order = self.settings.value('Config/Order')
        updated_order = order + domain + ','
        self.settings.setValue(f'Config/Order', updated_order)

    def initialize_values(self):

        domain = self.widget_domain.text()

        try:
            init_settings = self.settings.value(f'Domains/{domain}')
            init_settings = init_settings.split("|")
        except:
            init_settings = self.settings.value('Config/Default')
            init_settings = init_settings.split("|")

        phrase_state = int(init_settings[0])
        self.widget_phrase_toggle.setCheckState(phrase_state)
        self.phrase_toggle_state = self.widget_phrase_toggle.checkState()
        if phrase_state == 2:
            secure = int(init_settings[1])
            self.change_max_type(secure=secure)
        elif phrase_state == 0:
            phrase = int(init_settings[1])
            self.change_max_type(phrase=phrase)
