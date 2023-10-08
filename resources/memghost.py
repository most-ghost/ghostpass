from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import pyqtSlot
import resources.fontghost as fontghost
import json
import os

dict_prefs =   {'--ghostconfig/pass_visible':'no', 
                '--ghostconfig/logo_size':'normal',
                 '--ghostconfig/autoblank': 'yes',
                 '--ghostconfig/second_required': 'yes',
                 '--ghostconfig/default_type': 'hash', 
                 '--ghostconfig/default_len_hash': '128',
                 '--ghostconfig/default_len_word': '10',
                 '--ghostconfig/tab_order' : 'general|social|hobby|entertainment|market|business',
                 '--ghost_tabs/general' : '|google|',
                 '--ghost_tabs/social' : '|facebook|twitter|',
                 '--ghost_tabs/business' : '|email|',
                 '--ghost_tabs/market' : '|amazon|ebay|',
                 '--ghost_tabs/entertainment' : '|netflix|steam|',
                 '--ghost_tabs/hobby' : '|reddit|'
                 }
# If these aren't overwritten, they'll act as our defaults


class cls_popup_settings(qtw.QDialog):
    """
    This class handles the 'preferences' pop up from the system menu.
    """

    sig_saved = qtc.pyqtSignal()
    sig_add_tab = qtc.pyqtSignal(str)
    sig_delete_tab = qtc.pyqtSignal(str)
    sig_rename_tab = qtc.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(modal=False)

        self.setLayout(qtw.QFormLayout())

        self.setWindowTitle('preferences')

        self.setWindowOpacity(0.98)


        self.setWindowIcon(qtg.QIcon(
            os.path.join(
            os.path.dirname(__file__), "ghosticon.svg")))
        
        self.wgt_pass_visible = qtw.QPushButton(dict_prefs['--ghostconfig/pass_visible'])
        self.wgt_second_required = qtw.QPushButton(dict_prefs['--ghostconfig/second_required'])
        self.wgt_hashword_toggle = qtw.QComboBox()
        self.wgt_hashword_toggle.addItem("hash")
        self.wgt_hashword_toggle.addItem("word")
        self.wgt_hashword_toggle.setCurrentText(dict_prefs['--ghostconfig/default_type'])
        self.wgt_autoblank = qtw.QPushButton(dict_prefs['--ghostconfig/autoblank'])
        self.wgt_logo_size = qtw.QComboBox()
        self.wgt_logo_size.addItem("disabled")
        self.wgt_logo_size.addItem("normal")
        self.wgt_logo_size.addItem("2x")
        self.wgt_logo_size.setCurrentText(dict_prefs['--ghostconfig/logo_size'])
        self.wgt_hash_length = qtw.QSpinBox(maximum=256, minimum=20)
        self.wgt_hash_length.setValue(int(dict_prefs['--ghostconfig/default_len_hash']))
        self.wgt_word_length = qtw.QSpinBox(maximum=20, minimum=6)
        self.wgt_word_length.setValue(int(dict_prefs['--ghostconfig/default_len_word']))
        self.wgt_add_category = qtw.QPushButton('create')
        self.wgt_rem_category = qtw.QPushButton('remove')
        self.wgt_mod_category = qtw.QPushButton('modify')




        self.layout().addRow(
            qtw.QLabel('<h1>preferences</h1>')
        )
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )
        self.layout().addRow(
            qtw.QLabel('<h2>app settings</h2>')
        )
        self.layout().addRow("passwords visible by default", self.wgt_pass_visible)
        self.layout().addRow("passphrase required", self.wgt_second_required)
        self.layout().addRow("passwords blank after 1 minute", self.wgt_autoblank)
        self.layout().addRow("ghostpass logo size*", self.wgt_logo_size)
        self.layout().addRow(
            qtw.QLabel('<h5>(* needs restart)</h5>'),
        )
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )
        self.layout().addRow(
            qtw.QLabel('<h2>stack settings</h2>'),
        )
        self.layout().addRow("default stack type", self.wgt_hashword_toggle)
        self.layout().addRow("default character length (hash)", self.wgt_hash_length)
        self.layout().addRow("default number of words (passphrase)", self.wgt_word_length)
        self.layout().addRow(
            qtw.QLabel('<h6></h6>')
        )
        self.layout().addRow(
            qtw.QLabel('<h2>category settings</h2>'),
        )
        self.layout().addRow("add new category", self.wgt_add_category)
        self.layout().addRow("delete category", self.wgt_rem_category)
        self.layout().addRow("rename category", self.wgt_mod_category)


        self.wgt_close_button = qtw.QPushButton('save', clicked = self.close)
        self.layout().addRow(self.wgt_close_button)

        self.wgt_pass_visible.clicked.connect(self.hook_up_visible_pass)
        self.wgt_second_required.clicked.connect(self.hook_up_second_pass)
        self.wgt_autoblank.clicked.connect(self.hook_up_autoblank)
        self.wgt_hashword_toggle.currentTextChanged.connect(self.hook_up_hash_or_word)
        self.wgt_logo_size.currentTextChanged.connect(self.hook_up_logo_size)
        self.wgt_hash_length.valueChanged.connect(self.hook_up_hash_length)
        self.wgt_word_length.valueChanged.connect(self.hook_up_word_length)
        self.wgt_add_category.clicked.connect(self.hook_up_add_cat)
        self.wgt_rem_category.clicked.connect(self.hook_up_del_cat)
        self.wgt_mod_category.clicked.connect(self.hook_up_mod_cat)


        self.font_typewriter = fontghost.fontghost.typewriter(15)
   
        for i in range(self.layout().count()):
            temp_row = self.layout().itemAt(i)
            temp_row.widget().setFont(self.font_typewriter)




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
    def hook_up_autoblank(self):
        if dict_prefs['--ghostconfig/autoblank'] == 'yes':
            dict_prefs['--ghostconfig/autoblank'] = 'no'
        elif dict_prefs['--ghostconfig/autoblank'] == 'no':
            dict_prefs['--ghostconfig/autoblank'] = 'yes'
        self.wgt_autoblank.setText(dict_prefs['--ghostconfig/autoblank'])

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

    @pyqtSlot()
    def hook_up_add_cat(self):
        popup_add_cat = cls_popup_category(
            'add category', 
            'please enter the name of your new category'
            )

        if popup_add_cat.exec() == qtw.QDialog.Accepted:
            new_tab = popup_add_cat.get_results()
            self.sig_add_tab.emit(new_tab.lower())

    def hook_up_del_cat(self):

        popup_del_cat = cls_popup_category(
            'delete category', 
            'this is permanent! deleting a category will delete \nthe whole list inside of it too', 
            line_text="if you're sure, type the name in here"
            )

        if popup_del_cat.exec() == qtw.QDialog.Accepted:
            del_tab = popup_del_cat.get_results()
            self.sig_delete_tab.emit(del_tab.lower())

    def hook_up_mod_cat(self):

        popup_del_cat = cls_popup_category(
            'rename category', 
            'please select your category, \nand then enter the new name \nin the space below', 
            category_list=True
            )

        if popup_del_cat.exec() == qtw.QDialog.Accepted:
            del_tab, old_tab = popup_del_cat.get_results()
            self.sig_rename_tab.emit(del_tab.lower(), old_tab)

            
    def keyPressEvent(self, event):
        event.ignore()
        # For some reason, hitting 'enter' when adjusting a spinbox will activate a button instead.
        # This seems to be some weird Qt bug unrelated to my code? Since we don't need the keyboard
        # in this menu anyway, we'll just ignore it entirely.
        # Note that this doesn't actually disable the number keys from working on the spinbox, so we're
        # all good.

    def closeEvent(self, event):
        self.sig_saved.emit()
        super().closeEvent(event)







class cls_popup_category(qtw.QDialog):
    # This is the generic box that will pop up whenever the user selects one of the options related to category tabs.
    # It can be changed to be used for adding, removing or renaming category tabs.

    def __init__(self, window_title, label_main, line_text = '', category_list = False, parent=None):
        super().__init__(parent)
        font = fontghost.fontghost.typewriter(17)

        self.category_list = category_list

        self.setWindowTitle(window_title)
        self.setWindowIcon(qtg.QIcon(
            os.path.join(
            os.path.dirname(__file__), "ghosticon.svg")))
        self.setWindowOpacity(0.98)    

        lo_popup = qtw.QVBoxLayout(self)

        self.setLayout(lo_popup)

        wgt_label_main = qtw.QLabel(label_main)
        self.wgt_text_edit = qtw.QLineEdit()
        self.wgt_text_edit.setPlaceholderText(line_text)
        self.wgt_buttons = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel)
        

        lo_popup.addWidget(wgt_label_main)
        if category_list == True:
            self.wgt_list = qtw.QListWidget()
            categories = qtc.QSettings('most_ghost', 'ghostpass').value('--ghostconfig/tab_order').split('|')
            for tab in categories:
                self.wgt_list.addItem(tab)
            lo_popup.addWidget(self.wgt_list)
        lo_popup.addWidget(self.wgt_text_edit)
        lo_popup.addWidget(self.wgt_buttons)        

        for i in range(lo_popup.count()):
            item = lo_popup.itemAt(i)
            item.widget().setFont(font)

        self.wgt_buttons.accepted.connect(self.accept)
        self.wgt_buttons.rejected.connect(self.reject)

    def get_results(self):
        returnable = str(self.wgt_text_edit.text())
        returnable = returnable.replace('_', '')
        returnable = returnable.replace('|', '')
        returnable = returnable.replace('/', '')

        if self.category_list == True:
            return (returnable, self.wgt_list.currentItem().text())
        else:
            return returnable
        
    def accept(self):
        super().accept()
        
    def reject(self):
        super().reject()


        




class cls_obj_memory(qtc.QObject):
    """ 
    This holds all of our memory management logic.
    Or, well, most of it. Some parts are taken care of by the windows- 
    for example the main window saves its own size.
    """

    sig_make_stack = qtc.pyqtSignal(str, str)
    sig_reset = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.settings = qtc.QSettings('most_ghost', 'ghostpass')

        var_existing_keys = self.settings.allKeys()

        for key in dict_prefs.keys():
            existing = self.settings.value(key)
            if key in var_existing_keys and existing != '': 
                dict_prefs[key] = self.settings.value(key)
            else:
                self.settings.setValue(key, dict_prefs[key])

    def func_settings_init(self):
            # This is seperated from the above as it is used to initialize our settings after the main window
            # has been created, while the above is initialized before the main window has finished being drawn.
        dict_domains = {}
        dict_domains_cleaned = {}

        list_tabs = self.settings.value('--ghostconfig/tab_order').split('|')
        list_tabs_cleaned = []
        for tab in list_tabs:
            if tab in list_tabs_cleaned:
                continue
            else:
                list_tabs_cleaned.append(tab)
        
        for tab in list_tabs_cleaned:
            order = self.settings.value(f'--ghost_tabs/{tab}')
            if order == None:
                order = []
            else:
                order = order[1:-1].split("|")
            dict_domains[tab] = order
            dict_domains_cleaned[tab] = []

        for tab in dict_domains.keys():
            for name in dict_domains[tab]: 
                if name in dict_domains_cleaned[tab]:
                    continue
                dict_domains_cleaned[tab].append(name)
        # I usually like to use sets to remove duplicates, but in this case I really want to keep the order.

        for tab in dict_domains_cleaned.keys():
            for name in dict_domains_cleaned[tab]:
                self.sig_make_stack.emit(name, tab)

    def func_settings_update(self, dict_tabs):
        
        self.settings.clear()

        for key, value in dict_prefs.items():
            self.settings.setValue(key, value)
            
        for tab in dict_tabs.keys():
            var_index_count = dict_tabs[tab]['layout'].count()
            self.settings.setValue(f'--ghost_tabs/{tab}', '')
            
            for i in range(var_index_count - 1):
                widget = dict_tabs[tab]['layout'].itemAt(i).widget()
                widget.func_save_settings()
                widget.func_save_order()
        # Each stack is responsible for managing its own settings. It'll also tack its name onto the 'order' setting
        # before passing it along to the next one, so we'll get a handy list of which widgets go in which order.
        
        # This was probably a bad idea though. Each stack should have simply saved everything to settings immediately
        # and been much simpler in design overall while its logic was managed elsewhere.
        # Doing things this way made it more difficult when trying to implement threading.

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
                if key[:14] == "--ghostconfig/":
                    dict_prefs[key] = value # This makes sure our running app is in sync
            
            self.sig_reset.emit()
            self.func_settings_init()