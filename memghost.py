
import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import json

preferences =   {'config/pass_visible':'no', 
                 'config/second_required': 'yes',
                 'config/default_type': 'hash', 
                 'config/default_len_hash': '128',
                 'config/default_len_word': '10'}

class settings_dialog(qtw.QDialog):

    saved = qtc.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, modal=False)

        dialog_font_id = qtg.QFontDatabase.addApplicationFont('ghostpass/typewcond_demi.otf')
        dialog_font_family = qtg.QFontDatabase.applicationFontFamilies(dialog_font_id)[0]
        dialog_font_typewriter = qtg.QFont(dialog_font_family)
        dialog_font_typewriter.setPointSize(15)

        self.setFont(dialog_font_typewriter)

        self.setLayout(qtw.QFormLayout())
        
        self.widget_visible_pass = qtw.QPushButton(preferences['config/pass_visible'])
        self.widget_second_pass = qtw.QPushButton(preferences['config/second_required'])
        self.widget_hash_or_word = qtw.QComboBox()
        self.widget_hash_or_word.addItem("hash")
        self.widget_hash_or_word.addItem("word")
        self.widget_hash_or_word.setCurrentText(preferences['config/default_type'])
        self.widget_hash_length = qtw.QSpinBox(maximum=256, minimum=20)
        self.widget_hash_length.setValue(int(preferences['config/default_len_hash']))
        self.widget_word_length = qtw.QSpinBox(maximum=20, minimum=6)
        self.widget_word_length.setValue(int(preferences['config/default_len_word']))


        
        self.layout().addRow(
            qtw.QLabel('<h1>ghostpass</h1>')
        )
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )
        self.layout().addRow(
            qtw.QLabel('<h2>app settings</h3>')
        )
        self.layout().addRow("passwords visible by default", self.widget_visible_pass)
        self.layout().addRow("second password required", self.widget_second_pass)
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )
        self.layout().addRow(
            qtw.QLabel('<h2>stack settings</h3>'),
        )
        self.layout().addRow("default stack type", self.widget_hash_or_word)
        self.layout().addRow("default character length (hash)", self.widget_hash_length)
        self.layout().addRow("default number of words (passphrase)      ", self.widget_word_length)
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )

        self.close_btn = qtw.QPushButton('Save', clicked = self.close)
        self.layout().addRow(self.close_btn)

        self.widget_visible_pass.clicked.connect(self.hook_up_visible_pass)
        self.widget_second_pass.clicked.connect(self.hook_up_second_pass)
        self.widget_hash_or_word.currentTextChanged.connect(self.hook_up_hash_or_word)
        self.widget_hash_length.valueChanged.connect(self.hook_up_hash_length)
        self.widget_word_length.valueChanged.connect(self.hook_up_word_length)

    def hook_up_visible_pass(self):
        if preferences['config/pass_visible'] == 'yes':
            preferences['config/pass_visible'] = 'no'
        elif preferences['config/pass_visible'] == 'no':
            preferences['config/pass_visible'] = 'yes'
        self.widget_visible_pass.setText(preferences['config/pass_visible'])
        
    def hook_up_second_pass(self):
        if preferences['config/second_required'] == 'yes':
            preferences['config/second_required'] = 'no'
        elif preferences['config/second_required'] == 'no':
            preferences['config/second_required'] = 'yes'
        self.widget_second_pass.setText(preferences['config/second_required'])

    def hook_up_hash_or_word(self):
        preferences['config/default_type'] = self.widget_hash_or_word.currentText()

    def hook_up_hash_length(self):
        preferences['config/default_len_hash'] = self.widget_hash_length.value()
    
    def hook_up_word_length(self):
        preferences['config/default_len_word'] = self.widget_word_length.value()

    def closeEvent(self, event):
        self.saved.emit()
        super().closeEvent(event)

## Remember to update settings when dialog closed

class memory(qtc.QObject):

    stack_pass = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.settings = qtc.QSettings('most_ghost', 'ghostpass')

        existing_keys = self.settings.allKeys()

        for key in preferences.keys():
            if key in existing_keys:
                preferences[key] = self.settings.value(key)
            else:
                self.settings.setValue(key, preferences[key])

    def settings_init(self):
            # This is separated from the above because it will get loaded at the end of the main window
            # init, after the window is populated, while the above gets loaded in at the beginning while
            # the main window is still populating itself.
        
        domains = []
        order = self.settings.value('config/order')
        try:
            order = order[:-1].split(',')
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
            self.stack_pass.emit(name)
        # Normally I'd use a set to remove duplicates, but in this case the whole point is to keep the 
        # order of the widgets in the list. So this works to remove duplicates instead.
        # What will happen with this is that the last duplicate widget will get deleted, however the settings
        # on that widget are kept. I think this is a feature, not a bug- someone is probably adding their new domain
        # to the bottom because they don't see it on the list above, so we want to keep those newest settings. But
        # we don't want duplicates cluttering up the list if it's already on there.


    def settings_update(self, stack_layout):
        print('Settings are being updated!')
        
        self.settings.clear()
        self.settings.setValue('config/order', '')

        for key, value in preferences.items():
            self.settings.setValue(key, value)

        index = stack_layout.count()
        for i in range(index - 1):
            widget = stack_layout.itemAt(i).widget()
            widget.save_settings()
        # Each stack is responsible for managing its own settings. It'll also tack its name onto the 'order' setting
        # before passing it along to the next one, so we'll get a handy list of which widgets go in which order.

    def export_settings(self):
        self.settings_update()

        filename, _= qtw.QFileDialog().getSaveFileName(
            self,
            "Select the file to export to...",
            qtc.QDir.homePath(),
            'GhostFile (*.woo)',
            'GhostFile (*.woo)')
        
        if filename:
            if filename[-4:] != '.woo':
                filename = filename + '.woo'
            keys = self.settings.allKeys()
            settings_dict = {}
            for key in keys:
                value = self.settings.value(key)
                settings_dict[key] = value
            with open(filename, "w") as f:
                json.dump(settings_dict, f, indent=4)
        # It's vitally important that we use that .woo filename.
        # A lot of functionality is hidden in those 3 letters.

    def import_settings(self):
        filename, _ = qtw.QFileDialog().getOpenFileName(
            self,
            "Select the file to import...",
            qtc.QDir.homePath(),
            'GhostFile (*.woo)',
            'GhostFile (*.woo)'
        )

        if filename:
            self.settings.clear()
            with open(filename, "r") as f:
                settings_dict = json.load(f)
            
            for key, value in settings_dict.items():
                self.settings.setValue(key, value)
            
            self.reset_scroll_area()
            