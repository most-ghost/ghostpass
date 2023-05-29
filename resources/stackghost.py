import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import pyqtSlot
import resources.qtextramods as qte 
import resources.smartghost as smartghost

ref_logic = smartghost.cls_obj_logic()

class cls_stack_widget(qtw.QFrame):
    """
    This is a custom widget that defines our 'stack', or each strip of gui that holds a domain field, 
    the generate button, the generated password field etc. In web development this might've been called a 'div',
    maybe that would've been a better name for it. Especially since Qt already has a 'stack' data structure.
    Oh well!
    """

    sig_delete = qtc.pyqtSignal(qtc.QObject)
    sig_update = qtc.pyqtSignal()

    def __init__(self, wgt_pass, wgt_salt, var_domain):
        super().__init__()

        temp_font_id = qtg.QFontDatabase.addApplicationFont(
            os.path.join(
            os.path.dirname(__file__), "typewcond_demi.otf"))
        temp_font_family = qtg.QFontDatabase.applicationFontFamilies(temp_font_id)[0]
        var_font = qtg.QFont(temp_font_family)
        var_font.setPointSize(15)
        var_font_small = qtg.QFont(temp_font_family)
        var_font_small.setPointSize(10)
        del temp_font_id
        del temp_font_family

        self.wgt_pass = wgt_pass
        self.wgt_salt = wgt_salt

        self.settings = qtc.QSettings('most_ghost', 'ghostpass')

        self.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Fixed
        )

        self.setLineWidth(5)
        self.setFrameStyle(qtw.QFrame.StyledPanel | qtw.QFrame.Plain)

        lo_vertical = qtw.QVBoxLayout()
        self.setLayout(lo_vertical)

        struct_top_strip = qtw.QWidget()
        struct_top_strip.setSizePolicy(
            qtw.QSizePolicy.Preferred,
            qtw.QSizePolicy.Fixed)
        lo_horizontal = qtw.QHBoxLayout()
        struct_top_strip.setLayout(lo_horizontal)
        lo_vertical.addWidget(struct_top_strip)

        self.wgt_domain_name = qtw.QLineEdit(var_domain)
        self.wgt_domain_name.setSizePolicy(
            qtw.QSizePolicy.Maximum,
            qtw.QSizePolicy.Minimum)
        self.wgt_domain_name.editingFinished.connect(self.slot_domain_format)
        # I don't want to give the option to mix and match upper and lower, so lower only.
        self.wgt_domain_name.setFont(var_font)
        lo_horizontal.addWidget(self.wgt_domain_name)

        self.wgt_generated = qtw.QLineEdit(
            self,
            readOnly = True,
            placeholderText = ''
            )
        self.wgt_generated.mouseReleaseEvent = lambda _: self.slot_force_highlight(self.wgt_generated)
        lo_vertical.addWidget(self.wgt_generated)

        struct_spacer = qtw.QSpacerItem(40, 20, 
                                        qtw.QSizePolicy.Expanding, 
                                        qtw.QSizePolicy.Minimum)
        lo_horizontal.addSpacerItem(struct_spacer)



        struct_toggle_type = qtw.QWidget()
        struct_toggle_type.setSizePolicy(
            qtw.QSizePolicy.Fixed,
            qtw.QSizePolicy.Ignored)
        struct_toggle_type.setFixedHeight(1)
        # We'll overwrite this later, but for right now I don't want the size of this section messing with
        # the calculated size of the full top strip.
        lo_toggle_type = qtw.QVBoxLayout(struct_toggle_type)
        self.wgt_toggle_type_switch = qte.AnimatedToggle()
        self.wgt_toggle_type_switch.clicked.connect(self.func_phrase_clicked)
        lo_toggle_type.addWidget(self.wgt_toggle_type_switch)
        self.wgt_toggle_type_label = qtw.QLabel('...')
        self.wgt_toggle_type_label.setFont(var_font_small)
        self.wgt_toggle_type_label.setAlignment(qtc.Qt.AlignHCenter)
        lo_toggle_type.addWidget(self.wgt_toggle_type_label) 
        lo_horizontal.addWidget(struct_toggle_type)

        self.wgt_size_spinbox = qtw.QSpinBox()
        self.wgt_size_spinbox.wheelEvent = lambda _: None 
        # Who uses the mouse wheel to scroll these? What a dumb feature. You're trying to scroll through
        # your list of stuff and your mouse touches one of these boxes and instantly you stop in place
        # and instead start messing around with some value you weren't trying to touch. Even if the item
        # stays in place I would never use the mouse wheel to adjust a value in a spinbox. It's just an
        # odd design concept.
        self.wgt_size_spinbox.setFont(var_font)
        lo_horizontal.addWidget(self.wgt_size_spinbox)

        var_dynamic_height = int(struct_top_strip.sizeHint().height())
        struct_toggle_type.setFixedHeight(var_dynamic_height)
        # Since the height will change for each user depending on their screen configuration, this is I think the best
        # way to set a fixed stack height that still makes sense for each user's setup.

        self.wgt_generate_button = qtw.QPushButton('generate')
        self.wgt_generate_button.clicked.connect(self.slot_generating_pass)
        self.wgt_generate_button.setFont(var_font)
        lo_horizontal.addWidget(self.wgt_generate_button)

        self.wgt_delete_button = qtw.QPushButton('-')
        self.wgt_delete_button.setSizePolicy(
            qtw.QSizePolicy.Maximum,
            qtw.QSizePolicy.Maximum)
        self.wgt_delete_button.clicked.connect(self.slot_requesting_delete)
        self.wgt_delete_button.setFont(var_font)
        self.wgt_delete_button.setStyleSheet("""
        QPushButton:hover {
            background-color: #7d0f1f;
            border-color: #ff252b;
            } """)
        lo_horizontal.addWidget(self.wgt_delete_button)

        self.var_delete_double_check = False

        self.func_initialize_values()
        self.func_save_settings()

        qtc.QTimer.singleShot(10, self.func_just_slap_the_tv)



    @pyqtSlot()
    def slot_requesting_delete(self):
        if self.var_delete_double_check == True:
            self.sig_delete.emit(self)
        elif self.var_delete_double_check == False:
            self.func_delete_activated()

    def func_delete_activated(self):
        self.var_delete_double_check = True
        self.wgt_delete_button.setText('!')
        self.wgt_delete_button.setStyleSheet("""
        QPushButton:hover {
            background-color: #d3181c;
            border-color: #ff252b;
            } """)
        qtc.QTimer.singleShot(1000, self.func_delete_deactivated)
                              
    def func_delete_deactivated(self):
        self.var_delete_double_check = False
        self.wgt_delete_button.setText('-')
        self.wgt_delete_button.setStyleSheet("""
        QPushButton:hover {
            background-color: #7d0f1f;
            border-color: #ff252b;
            } """)
        

    @pyqtSlot()
    def slot_generating_pass(self):
        var_password = self.wgt_pass.text()
        var_salt = self.wgt_salt.text()
        var_size = self.wgt_size_spinbox.value()
        var_domain = self.wgt_domain_name.text()
        var_salt_toggle = self.settings.value('--ghostconfig/second_required')

        if var_password == '':
            self.wgt_generated.setText('')
            self.wgt_generated.setPlaceholderText('please enter a password.')
        elif len(var_password) < 8:
            self.wgt_generated.setText('')
            self.wgt_generated.setPlaceholderText('please enter a longer password.')
        elif var_salt_toggle == 'yes' and var_salt == '':
            self.wgt_generated.setText('')
            self.wgt_generated.setPlaceholderText('please enter a second password.')
        elif var_salt_toggle == 'yes' and len(var_salt) < 8:
            self.wgt_generated.setText('')
            self.wgt_generated.setPlaceholderText('please enter a longer second password.')
        else:
            if self.var_global_toggle_state == 2:
                self.wgt_generated.setText(ref_logic.func_hash_gen(var_domain, var_password, var_size, var_salt))
            elif self.var_global_toggle_state == 0:
                self.wgt_generated.setText(ref_logic.func_passphrase_gen(var_domain, var_password, var_size, var_salt))
            self.wgt_generated.setCursorPosition(0)

        if self.settings.value('--ghostconfig/autoblank') == 'yes':
            qtc.QTimer.singleShot(60000, lambda: self.wgt_generated.setText(""))
                # 60000 milliseconds = 1 minute


    @pyqtSlot()
    def slot_fake_gen_click(self):
        self.wgt_generate_button.click()

    @pyqtSlot()
    def slot_force_highlight(self, wgt_generated):
        wgt_generated.end(False)
        wgt_generated.home(True)

    def func_phrase_clicked(self):
        self.var_global_toggle_state = self.wgt_toggle_type_switch.checkState()
        self.func_change_max_type()
        self.func_save_settings()

    def func_change_max_type(self):
        wgt_toggle = self.wgt_toggle_type_switch
        wgt_spinbox = self.wgt_size_spinbox
        var_domain = self.wgt_domain_name.text()

        try:
            if var_domain == 'app or domain':
                raise TypeError # We want 'domain' to return default so we'll raise a fake error
            var_hash = int(self.settings.value(f'{var_domain}/hash_length'))
            var_word = int(self.settings.value(f'{var_domain}/word_length'))
        except TypeError:
            var_hash = int(self.settings.value('--ghostconfig/default_len_hash'))
            var_word = int(self.settings.value('--ghostconfig/default_len_word'))



        if wgt_toggle.checkState() == 2: # Secure Hash
            wgt_spinbox.setMaximum(258)
            wgt_spinbox.setMinimum(20)
            wgt_spinbox.setValue(var_hash)
            wgt_spinbox.setSuffix(' chars')
            self.wgt_toggle_type_label.setText('hash')
        if wgt_toggle.checkState() == 0: # Passphrase
            wgt_spinbox.setMaximum(20)
            wgt_spinbox.setMinimum(6)
            wgt_spinbox.setValue(var_word)
            wgt_spinbox.setSuffix(' words')
            self.wgt_toggle_type_label.setText('passphrase')


    def func_save_settings(self):
        var_domain = self.wgt_domain_name.text()
        var_toggle = self.wgt_toggle_type_switch.checkState()
        var_size = self.wgt_size_spinbox.value()
        var_default_hash = self.settings.value('--ghostconfig/default_len_hash')
        var_default_word =self.settings.value('--ghostconfig/default_len_word')


        self.settings.setValue(f'{var_domain}/toggle_state', f'{var_toggle}')
        
        if var_toggle == 2:
           self.settings.setValue(f'{var_domain}/hash_length', f'{var_size}')
           self.settings.setValue(f'{var_domain}/word_length', f'{var_default_word}')
        elif var_toggle == 0:
           self.settings.setValue(f'{var_domain}/hash_length', f'{var_default_hash}')
           self.settings.setValue(f'{var_domain}/word_length', f'{var_size}')

    @pyqtSlot()
    def slot_domain_format(self):
        domain = self.wgt_domain_name.text().lower()
        domain = domain.replace('|', '\\')
        domain = domain.replace('/', '\\')
        self.wgt_domain_name.setText(domain)
        # A) I want to get rid of | since it's used as a delimiter
        # B) I want to get rid of / since it's used in the key itself
        # C) I want to make sure it's always lowercase just to make consistency easier to maintain
        # I could try to work around these but they're pretty uncommon characters so we'll just trash
        # them instead.

    def func_save_order(self):
        var_domain = self.wgt_domain_name.text()
        settings_order = self.settings.value('--ghostconfig/order')
        updated_order = settings_order + var_domain + '|'
        self.settings.setValue(f'--ghostconfig/order', updated_order)

    def func_initialize_values(self):

        var_domain = self.wgt_domain_name.text()

        var_list_domains = set()
        temp_settings_keys = self.settings.allKeys()
        for i in temp_settings_keys:
            var_list_domains.add(i.split('/')[0])

        if var_domain in var_list_domains and var_domain != 'app or domain':
            var_toggle = int(self.settings.value(f'{var_domain}/toggle_state'))
        else:
            var_default = self.settings.value('--ghostconfig/default_type')
            if var_default == 'hash':
                var_toggle = 2
            elif var_default == 'word':
                var_toggle = 0

        self.wgt_toggle_type_switch.setCheckState(var_toggle)
        self.func_phrase_clicked()


    def func_just_slap_the_tv(self):
        self.wgt_size_spinbox.setSuffix('chars ')
        self.wgt_size_spinbox.setMaximum(256)
        self.wgt_size_spinbox.setValue(256)
        self.wgt_size_spinbox.setFixedWidth(
                self.wgt_size_spinbox.sizeHint().width() + 12)
        self.func_change_max_type()
        # I want the spinbox to be set to a fixed size which represents the largest amount of characters
        # the spinbox might hold. This is a sloppy method but since I don't know exactly what the size hint
        # will be on the user's screen in advance, this is one way to get it done.
        # The extra 12 pixels are to accomodate the buttons at the sides of the spinbox, it should be enough probably.