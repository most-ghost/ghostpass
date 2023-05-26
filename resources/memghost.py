from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import pyqtSlot
import json
import os

dict_prefs =   {'--ghostconfig/pass_visible':'no', 
                '--ghostconfig/logo_size':'normal',
                 '--ghostconfig/second_required': 'yes',
                 '--ghostconfig/default_type': 'hash', 
                 '--ghostconfig/default_len_hash': '128',
                 '--ghostconfig/default_len_word': '10'}
# If these aren't overwritten, they'll act as our defaults

class cls_popup_settings(qtw.QDialog):

    sig_saved = qtc.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, modal=False)

        temp_font_id = qtg.QFontDatabase.addApplicationFont(
            os.path.join(
            os.path.dirname(__file__), "typewcond_demi.otf"))
        temp_font_family = qtg.QFontDatabase.applicationFontFamilies(temp_font_id)[0]
        var_font = qtg.QFont(temp_font_family)
        var_font.setPointSize(15)
        del temp_font_family
        del temp_font_id

        self.setFont(var_font)

        self.setLayout(qtw.QFormLayout())
        
        self.wgt_pass_visible = qtw.QPushButton(dict_prefs['--ghostconfig/pass_visible'])
        self.wgt_second_required = qtw.QPushButton(dict_prefs['--ghostconfig/second_required'])
        self.wgt_hashword_toggle = qtw.QComboBox()
        self.wgt_hashword_toggle.addItem("hash")
        self.wgt_hashword_toggle.addItem("word")
        self.wgt_hashword_toggle.setCurrentText(dict_prefs['--ghostconfig/default_type'])
        self.wgt_logo_size = qtw.QComboBox()
        self.wgt_logo_size.addItem("disabled")
        self.wgt_logo_size.addItem("normal")
        self.wgt_logo_size.addItem("2x")
        self.wgt_logo_size.setCurrentText(dict_prefs['--ghostconfig/logo_size'])
        self.wgt_hash_length = qtw.QSpinBox(maximum=256, minimum=20)
        self.wgt_hash_length.setValue(int(dict_prefs['--ghostconfig/default_len_hash']))
        self.wgt_word_length = qtw.QSpinBox(maximum=20, minimum=6)
        self.wgt_word_length.setValue(int(dict_prefs['--ghostconfig/default_len_word']))


        
        self.layout().addRow(
            qtw.QLabel('<h1>ghostpass</h1>')
        )
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )
        self.layout().addRow(
            qtw.QLabel('<h2>app settings</h3>')
        )
        self.layout().addRow("passwords visible by default", self.wgt_pass_visible)
        self.layout().addRow("second password required", self.wgt_second_required)
        self.layout().addRow("ghostpass logo size*", self.wgt_logo_size)
        self.layout().addRow(
            qtw.QLabel('<h5>(* needs restart)</h5>'),
        )
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )
        self.layout().addRow(
            qtw.QLabel('<h2>stack settings</h3>'),
        )
        self.layout().addRow("default stack type", self.wgt_hashword_toggle)
        self.layout().addRow("default character length (hash)", self.wgt_hash_length)
        self.layout().addRow("default number of words (passphrase)      ", self.wgt_word_length)
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )

        self.wgt_close_button = qtw.QPushButton('Save', clicked = self.close)
        self.layout().addRow(self.wgt_close_button)

        self.wgt_pass_visible.clicked.connect(self.hook_up_visible_pass)
        self.wgt_second_required.clicked.connect(self.hook_up_second_pass)
        self.wgt_hashword_toggle.currentTextChanged.connect(self.hook_up_hash_or_word)
        self.wgt_logo_size.currentTextChanged.connect(self.hook_up_logo_size)
        self.wgt_hash_length.valueChanged.connect(self.hook_up_hash_length)
        self.wgt_word_length.valueChanged.connect(self.hook_up_word_length)

    @pyqtSlot()
    def hook_up_visible_pass(self):
        if dict_prefs['--ghostconfig/pass_visible'] == 'yes':
            dict_prefs['--ghostconfig/pass_visible'] = 'no'
        elif dict_prefs['--ghostconfig/pass_visible'] == 'no':
            dict_prefs['--ghostconfig/pass_visible'] = 'yes'
        self.wgt_pass_visible.setText(dict_prefs['--ghostconfig/pass_visible'])
        
    @pyqtSlot()
    def hook_up_second_pass(self):
        if dict_prefs['--ghostconfig/second_required'] == 'yes':
            dict_prefs['--ghostconfig/second_required'] = 'no'
        elif dict_prefs['--ghostconfig/second_required'] == 'no':
            dict_prefs['--ghostconfig/second_required'] = 'yes'
        self.wgt_second_required.setText(dict_prefs['--ghostconfig/second_required'])

    @pyqtSlot()
    def hook_up_hash_or_word(self):
        dict_prefs['--ghostconfig/default_type'] = self.wgt_hashword_toggle.currentText()

    @pyqtSlot()
    def hook_up_hash_length(self):
        dict_prefs['--ghostconfig/default_len_hash'] = self.wgt_hash_length.value()
    
    @pyqtSlot()
    def hook_up_word_length(self):
        dict_prefs['--ghostconfig/default_len_word'] = self.wgt_word_length.value()

    @pyqtSlot()
    def hook_up_logo_size(self):
        dict_prefs['--ghostconfig/logo_size'] = self.wgt_logo_size.currentText()


    def closeEvent(self, event):
        self.sig_saved.emit()
        super().closeEvent(event)


class cls_obj_memory(qtc.QObject):

    sig_make_stack = qtc.pyqtSignal(str)
    sig_reset = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.settings = qtc.QSettings('most_ghost', 'ghostpass')

        var_existing_keys = self.settings.allKeys()

        for key in dict_prefs.keys():
            if key in var_existing_keys:
                dict_prefs[key] = self.settings.value(key)
            else:
                self.settings.setValue(key, dict_prefs[key])

    def func_settings_init(self):
            # This is separated from the above because it will get loaded at the end of the main window
            # init, after the window is populated, while the above gets loaded in at the beginning while
            # the main window is still populating itself.
        
        domains = []
        order = self.settings.value('--ghostconfig/order')
        try:
            order = order[:-1].split('|')
            if type(order) != list:
                raise ValueError
            if order[0] == '':
                raise ValueError
        except (ValueError, TypeError):
            order = ['facebook', 'google', 'twitter']

        for name in order: 
            if name in domains:
                continue
            domains.append(name)
        for name in domains:
            self.sig_make_stack.emit(name)
        # Normally I'd use a set to remove duplicates, but in this case the whole point is to keep the 
        # order of the widgets in the list. So this works to remove duplicates instead.
        # What will happen with this is that the last duplicate widget will get deleted, however the settings
        # on that widget are kept. I think this is a feature, not a bug- someone is probably adding their new domain
        # to the bottom because they don't see it on the list above, so we want to keep those newest settings. But
        # we don't want duplicates cluttering up the list if it's already on there.


    def func_settings_update(self, stack_layout):
        
        self.settings.clear()
        self.settings.setValue('--ghostconfig/order', '')

        for key, value in dict_prefs.items():
            self.settings.setValue(key, value)

        var_index_count = stack_layout.count()
        for i in range(var_index_count - 1):
            widget = stack_layout.itemAt(i).widget()
            widget.func_save_settings()
            widget.func_save_order()
        # Each stack is responsible for managing its own settings. It'll also tack its name onto the 'order' setting
        # before passing it along to the next one, so we'll get a handy list of which widgets go in which order.
        
        # This was probably a bad idea though. Each stack should have simply saved everything to settings immediately.

    def func_export_settings(self):

        var_filename, _= qtw.QFileDialog().getSaveFileName(
            None,
            "Select the file to export to...",
            qtc.QDir.homePath(),
            'GhostFile (*.woo)',
            'GhostFile (*.woo)')
        
        if var_filename:
            if var_filename[-4:] != '.woo':
                var_filename = var_filename + '.woo'
            list_keys = self.settings.allKeys()
            settings_dict = {}
            for key in list_keys:
                value = self.settings.value(key)
                settings_dict[key] = value
            with open(var_filename, "w") as f:
                json.dump(settings_dict, f, indent=4)


    def func_import_settings(self):
        var_filename, _ = qtw.QFileDialog().getOpenFileName(
            None,
            "Select the file to import...",
            qtc.QDir.homePath(),
            'GhostFile (*.woo)',
            'GhostFile (*.woo)'
        )

        if var_filename:
            self.settings.clear()
            with open(var_filename, "r") as f:
                settings_dict = json.load(f)
            
            for key, value in settings_dict.items():
                self.settings.setValue(key, value)

            
            self.sig_reset.emit()
            self.func_settings_init()