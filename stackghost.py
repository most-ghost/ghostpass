from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import qtextramods as qte 
import smartghost as smartghost

logic = smartghost.logic()

class class_stack_widget(qtw.QFrame):

    signal_delete = qtc.pyqtSignal(qtc.QObject)
    signal_update = qtc.pyqtSignal()

    def __init__(self, pass_widget, salt_widget, domain):
        super().__init__()

        font_id = qtg.QFontDatabase.addApplicationFont('ghostpass/typewcond_demi.otf')
        font_family = qtg.QFontDatabase.applicationFontFamilies(font_id)[0]
        font_typewriter = qtg.QFont(font_family)
        font_typewriter.setPointSize(15)

        font_typewriter_small = qtg.QFont(font_family)
        font_typewriter.setPointSize(15)

        self.pass_widget = pass_widget
        self.salt_widget = salt_widget

        self.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Fixed
        )

        self.setLineWidth(2)
        self.setFrameStyle(qtw.QFrame.Panel | qtw.QFrame.Sunken)

        layout_stack = qtw.QVBoxLayout()
        self.setLayout(layout_stack)

        structure_top_strip = qtw.QWidget()
        structure_top_strip.setSizePolicy(
            qtw.QSizePolicy.Preferred,
            qtw.QSizePolicy.Fixed)
        layout_top = qtw.QHBoxLayout()
        structure_top_strip.setLayout(layout_top)
        layout_stack.addWidget(structure_top_strip)

        self.widget_domain = qtw.QLineEdit(domain)
        self.widget_domain.setSizePolicy(
            qtw.QSizePolicy.Maximum,
            qtw.QSizePolicy.Minimum)
        self.widget_domain.textEdited.connect(
            lambda : self.widget_domain.setText(self.widget_domain.text().lower()))
        self.widget_domain.editingFinished.connect(self.signal_update.emit)
        # This is a bit of a clunky way to force lower case, but it works without having to set a validator.
        # Maybe there's a potential use where a user needs to have passwords for both Google and google,
        # but I think it's more likely that having the option to mix and match, when a single letter capitalized
        # means a totally different hash, is just going to lead to potential headaches.
        self.widget_domain.setFont(font_typewriter)
        layout_top.addWidget(self.widget_domain)

        self.widget_gen_field = qtw.QLineEdit(
            self,
            readOnly = True,
            placeholderText = ''
            )
        self.widget_gen_field.mouseReleaseEvent = lambda _: self.force_highlight(self.widget_gen_field)
        layout_stack.addWidget(self.widget_gen_field) 

        # structure_empty_label = qtw.QSpacerItem(100000, 10,
        #                                         qtw.QSizePolicy.Expanding,
        #                                         qtw.QSizePolicy.Minimum)
        structure_spacer = qtw.QSpacerItem(40, 20, qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Minimum)
        layout_top.addSpacerItem(structure_spacer)



        structure_phrase_toggle = qtw.QWidget()
        structure_phrase_toggle.setSizePolicy(
            qtw.QSizePolicy.Fixed,
            qtw.QSizePolicy.Ignored)
        structure_phrase_toggle.setFixedHeight(5)
        # We'll overwrite this later, but for right now I don't want the size of this section messing with
        # the calculated size of the full top strip.
        layout_phrase_toggle = qtw.QVBoxLayout(structure_phrase_toggle)
        self.widget_phrase_toggle = qte.AnimatedToggle(
            pulse_checked_color="#FF000000", # First two letters are alpha
            pulse_unchecked_color="#FF000000"
            )
        self.widget_phrase_toggle.clicked.connect(self.phrase_clicked)
        layout_phrase_toggle.addWidget(self.widget_phrase_toggle)
        self.widget_phrase_label = qtw.QLabel('...')
        self.widget_phrase_label.setFont(font_typewriter_small)
        self.widget_phrase_label.setAlignment(qtc.Qt.AlignHCenter)
        layout_phrase_toggle.addWidget(self.widget_phrase_label) 
        layout_top.addWidget(structure_phrase_toggle)

        self.widget_size_phrase = qtw.QSpinBox()
        self.widget_size_phrase.wheelEvent = lambda _: None 
        # I'm sure there are 4 or 5 people who use the mouse wheel to activate one of these. 
        # For everyone else, the mouse wheel is there to scroll the window, not screw with values.
        # There's nothing worse than trying to scroll the window and instead the mouse catches on a
        # value box for a moment and stops scrolling and starts adjusting the thing in the box instead.
        self.widget_size_phrase.setFont(font_typewriter)
        #self.widget_size_phrase.valueChanged.connect(self.signal_update.emit)
        layout_top.addWidget(self.widget_size_phrase)


        dynamic_height = int(structure_top_strip.sizeHint().height())
        structure_phrase_toggle.setFixedHeight(dynamic_height)



        self.widget_gen_button = qtw.QPushButton('generate')
        self.widget_gen_button.clicked.connect(self.generating_pass)
        self.widget_gen_button.setFont(font_typewriter)
        layout_top.addWidget(self.widget_gen_button)

        widget_del_button = qtw.QPushButton('-')
        widget_del_button.setSizePolicy(
            qtw.QSizePolicy.Maximum,
            qtw.QSizePolicy.Maximum)
        widget_del_button.clicked.connect(self.requesting_delete)
        widget_del_button.setFont(font_typewriter)
        layout_top.addWidget(widget_del_button)


        # structure_top_strip.setStyleSheet("background-color: rgba(255, 0, 0, 0);") ### TEMPORARY
        # self.setStyleSheet("background-color: rgba(0, 0, 0, 127);") ### TEMPORARY


        self.initialize_values()


    def requesting_delete(self):
        self.signal_delete.emit(self)

    def generating_pass(self):
        password = self.pass_widget.text()
        salt = self.salt_widget.text()
        size = self.widget_size_phrase.value()
        domain = self.widget_domain.text()
        salt_required = qtc.QSettings('most_ghost', 'ghostpass').value('config/second_required')
        if password == '':
            self.widget_gen_field.setText('')
            self.widget_gen_field.setPlaceholderText('please enter a password.')
        elif len(password) < 10:
            self.widget_gen_field.setText('')
            self.widget_gen_field.setPlaceholderText('please enter a longer password.')
        elif salt_required == 'yes' and salt == '':
            self.widget_gen_field.setText('')
            self.widget_gen_field.setPlaceholderText('please enter a second password.')
        elif salt_required == 'yes' and len(salt) < 8:
            self.widget_gen_field.setText('')
            self.widget_gen_field.setPlaceholderText('please enter a longer second password.')
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
        #self.signal_update.emit()

        
    def change_max_type(self):
        domain = self.widget_domain.text()
        slider = self.widget_phrase_toggle
        spinbox = self.widget_size_phrase
        secure = int(qtc.QSettings('most_ghost', 'ghostpass').value('config/default_len_hash'))
        phrase = int(qtc.QSettings('most_ghost', 'ghostpass').value('config/default_len_word'))
        if domain != 'domain':
            try:
                existing_type, existing_value = qtc.QSettings('most_ghost', 'ghostpass').value(f'domains/{domain}').split('|')
                if int(existing_type) == 2:
                    secure = int(existing_value)
                elif int(existing_type) == 0:
                    phrase = int(existing_value)
            except AttributeError:
                pass
        if slider.checkState() == 2: # Secure
            spinbox.setMaximum(258)
            spinbox.setMinimum(20)
            spinbox.setValue(secure)
            spinbox.setSuffix(' chars')
            self.widget_phrase_label.setText('hash')
        if slider.checkState() == 0: # Passphrase
            spinbox.setMaximum(20)
            spinbox.setMinimum(6)
            spinbox.setValue(phrase)
            spinbox.setSuffix(' words')
            self.widget_phrase_label.setText('passphrase')



    def save_settings(self):
        domain = self.widget_domain.text()
        phrase_state = self.widget_phrase_toggle.checkState()
        gen_size = self.widget_size_phrase.value()
        
        qtc.QSettings('most_ghost', 'ghostpass').setValue(f'domains/{domain}', f'{phrase_state}|{gen_size}')


        order = qtc.QSettings('most_ghost', 'ghostpass').value('config/order')
        updated_order = order + domain + ','
        qtc.QSettings('most_ghost', 'ghostpass').setValue(f'config/order', updated_order)

    def initialize_values(self):

        domain = self.widget_domain.text()

        try:
            existing = qtc.QSettings('most_ghost', 'ghostpass').value('config/order').split(',')
            existing = existing[:-1]
        except AttributeError:
            existing = []

        if domain not in existing or domain == 'domain':
            default = qtc.QSettings('most_ghost', 'ghostpass').value(f'config/default_type')
            if default == 'hash':
                phrase_state = 2
            elif default == 'word':
                phrase_state = 0
        else:
            init_settings = qtc.QSettings('most_ghost', 'ghostpass').value(f'domains/{domain}')
            init_settings = init_settings.split("|")
            phrase_state = int(init_settings[0])


        self.widget_phrase_toggle.setCheckState(phrase_state)
        self.phrase_toggle_state = self.widget_phrase_toggle.checkState()
        if phrase_state == 2:
            self.change_max_type()
            self.widget_phrase_label.setText('hash')
            self.widget_size_phrase.setSuffix(' chars')
        elif phrase_state == 0:
            self.change_max_type()
            self.widget_phrase_label.setText('passphrase')
            self.widget_size_phrase.setSuffix(' words')

