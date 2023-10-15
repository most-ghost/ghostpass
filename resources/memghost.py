from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import pyqtSlot
import resources.fontghost as fontghost
import json
import os

global_dict_prefs =   {'--ghostconfig/pass_visible':'no', 
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

        self.setLayout(qtw.QVBoxLayout())
        struct_scroll_area = qtw.QScrollArea()
        struct_scroll_area.setWidgetResizable(True)
        self.layout().addWidget(struct_scroll_area)
        struct_scroll = qtw.QWidget()
        struct_scroll_area.setWidget(struct_scroll)

        lo_form = qtw.QFormLayout()
        struct_scroll.setLayout(lo_form)

        self.setWindowTitle('preferences')
        self.setWindowOpacity(0.97)
        self.setWindowIcon(qtg.QIcon(
            os.path.join(
            os.path.dirname(__file__), "ghosticon.svg")))

        font_typewriter_big = fontghost.fontghost.typewriter(15)
        font_roboto = fontghost.fontghost.roboto(12)
        font_roboto_small = fontghost.fontghost.roboto(9)


        self.dict_widgets = {}

        self.dict_widgets['pass_visible'] = qtw.QPushButton(global_dict_prefs['--ghostconfig/pass_visible'])
        self.dict_widgets['second_required'] = qtw.QPushButton(global_dict_prefs['--ghostconfig/second_required'])
        self.dict_widgets['stack_type'] = qtw.QComboBox()
        self.dict_widgets['stack_type'].addItem("hash")
        self.dict_widgets['stack_type'].addItem("word")
        self.dict_widgets['stack_type'].setCurrentText(global_dict_prefs['--ghostconfig/default_type'])
        self.dict_widgets['autoblank'] = qtw.QPushButton(global_dict_prefs['--ghostconfig/autoblank'])
        self.dict_widgets['logo_size'] = qtw.QComboBox()
        self.dict_widgets['logo_size'].addItem("disabled")
        self.dict_widgets['logo_size'].addItem("normal")
        self.dict_widgets['logo_size'].addItem("2x")
        self.dict_widgets['logo_size'].setCurrentText(global_dict_prefs['--ghostconfig/logo_size'])
        self.dict_widgets['char_length'] = qtw.QSpinBox(maximum=256, minimum=20)
        self.dict_widgets['char_length'].setValue(int(global_dict_prefs['--ghostconfig/default_len_hash']))
        self.dict_widgets['word_length'] = qtw.QSpinBox(maximum=20, minimum=6)
        self.dict_widgets['word_length'].setValue(int(global_dict_prefs['--ghostconfig/default_len_word']))
        self.dict_widgets['add_cat'] = qtw.QPushButton('create')
        self.dict_widgets['rem_cat'] = qtw.QPushButton('remove')
        self.dict_widgets['name_cat'] = qtw.QPushButton('modify')

        for key in self.dict_widgets.keys():
            self.dict_widgets[key].setFont(font_roboto)


        dict_top_labels = {}
        dict_top_labels['prefs'] = qtw.QLabel('<h1>preferences</h1>')
        dict_top_labels['app'] = qtw.QLabel('<h2>app settings</h2>')
        dict_top_labels['stack'] = qtw.QLabel('<h2>stack settings</h2>')
        dict_top_labels['cat'] = qtw.QLabel('<h2>category settings</h2>')

        for key in dict_top_labels.keys():
            dict_top_labels[key].setFont(font_typewriter_big)

        dict_label = {}

        dict_label['pass_visible'] = qtw.QLabel("passwords visible by default")
        dict_label['second_required'] = qtw.QLabel("passphrase enforced")
        dict_label['second_warning'] = qtw.QLabel("( you really shouldn't disable the passphrase )")
        dict_label['autoblank'] = qtw.QLabel("passwords blank after 1 minute")
        dict_label['logo_size'] = qtw.QLabel("ghostpass logo size *")
        dict_label['logo_size_warning'] = qtw.QLabel("<h5>(* needs restart )</h5>")
        dict_label['stack_type'] = qtw.QLabel("default stack type")
        dict_label['char_length'] = qtw.QLabel("default character length (hash)")
        dict_label['word_length'] = qtw.QLabel("default number of words (passphrase)")
        dict_label['add_cat'] = qtw.QLabel("add new category")
        dict_label['rem_cat'] = qtw.QLabel("delete category")
        dict_label['name_cat'] = qtw.QLabel("rename category")

        for key in dict_label.keys():
            dict_label[key].setFont(font_roboto)
        dict_label['second_warning'].setFont(font_roboto_small)
        dict_label['logo_size_warning'].setFont(font_roboto_small)



        lo_form.addRow(
            dict_top_labels['prefs']
        )
        lo_form.addRow(
            qtw.QLabel('<h6></h6>')
        )
        lo_form.addRow(
            dict_top_labels['app']
        )
        lo_form.addRow(dict_label['pass_visible'], self.dict_widgets['pass_visible'])
        lo_form.addRow(dict_label['second_required'], self.dict_widgets['second_required'])
        lo_form.addRow(dict_label['second_warning'])
        lo_form.addRow(dict_label['autoblank'], self.dict_widgets['autoblank'])
        lo_form.addRow(dict_label['logo_size'], self.dict_widgets['logo_size'])
        lo_form.addRow(dict_label['logo_size_warning'])
        lo_form.addRow(
            qtw.QLabel('<h6></h6>')
        )
        lo_form.addRow(
            dict_top_labels['stack']
        )
        lo_form.addRow(dict_label['stack_type'], self.dict_widgets['stack_type'])
        lo_form.addRow(dict_label['char_length'], self.dict_widgets['char_length'])
        lo_form.addRow(dict_label['word_length'], self.dict_widgets['word_length'])
        lo_form.addRow(
            qtw.QLabel('<h6></h6>')
        )
        lo_form.addRow(
            dict_top_labels['cat']
        )
        lo_form.addRow(dict_label['add_cat'], self.dict_widgets['add_cat'])
        lo_form.addRow(dict_label['rem_cat'], self.dict_widgets['rem_cat'])
        lo_form.addRow(dict_label['name_cat'], self.dict_widgets['name_cat'])


        wgt_close_button = qtw.QPushButton('save', clicked = self.close)
        wgt_close_button.setFont(font_typewriter_big)
        lo_form.addRow(wgt_close_button)

        self.dict_widgets['pass_visible'].clicked.connect(self.hook_up_visible_pass)
        self.dict_widgets['second_required'].clicked.connect(self.hook_up_second_pass)
        self.dict_widgets['autoblank'].clicked.connect(self.hook_up_autoblank)
        self.dict_widgets['stack_type'].currentTextChanged.connect(self.hook_up_hash_or_word)
        self.dict_widgets['logo_size'].currentTextChanged.connect(self.hook_up_logo_size)
        self.dict_widgets['char_length'].valueChanged.connect(self.hook_up_hash_length)
        self.dict_widgets['word_length'].valueChanged.connect(self.hook_up_word_length)
        self.dict_widgets['add_cat'].clicked.connect(self.hook_up_add_cat)
        self.dict_widgets['rem_cat'].clicked.connect(self.hook_up_del_cat)
        self.dict_widgets['name_cat'].clicked.connect(self.hook_up_mod_cat)


        default_width = self.sizeHint().width()
        self.setFixedWidth(default_width)




    @pyqtSlot()
    def hook_up_visible_pass(self):
        if global_dict_prefs['--ghostconfig/pass_visible'] == 'yes':
            global_dict_prefs['--ghostconfig/pass_visible'] = 'no'
        elif global_dict_prefs['--ghostconfig/pass_visible'] == 'no':
            global_dict_prefs['--ghostconfig/pass_visible'] = 'yes'
        self.dict_widgets['pass_visible'].setText(global_dict_prefs['--ghostconfig/pass_visible'])
        
    @pyqtSlot()
    def hook_up_second_pass(self):
        if global_dict_prefs['--ghostconfig/second_required'] == 'yes':
            global_dict_prefs['--ghostconfig/second_required'] = 'no'
        elif global_dict_prefs['--ghostconfig/second_required'] == 'no':
            global_dict_prefs['--ghostconfig/second_required'] = 'yes'
        self.dict_widgets['second_required'].setText(global_dict_prefs['--ghostconfig/second_required'])

    @pyqtSlot()
    def hook_up_autoblank(self):
        if global_dict_prefs['--ghostconfig/autoblank'] == 'yes':
            global_dict_prefs['--ghostconfig/autoblank'] = 'no'
        elif global_dict_prefs['--ghostconfig/autoblank'] == 'no':
            global_dict_prefs['--ghostconfig/autoblank'] = 'yes'
        self.dict_widgets['autoblank'].setText(global_dict_prefs['--ghostconfig/autoblank'])

    @pyqtSlot()
    def hook_up_hash_or_word(self):
        global_dict_prefs['--ghostconfig/default_type'] = self.dict_widgets['stack_type'].currentText()

    @pyqtSlot()
    def hook_up_hash_length(self):
        global_dict_prefs['--ghostconfig/default_len_hash'] = self.dict_widgets['char_length'].value()
    
    @pyqtSlot()
    def hook_up_word_length(self):
        global_dict_prefs['--ghostconfig/default_len_word'] = self.dict_widgets['word_length'].value()

    @pyqtSlot()
    def hook_up_logo_size(self):
        global_dict_prefs['--ghostconfig/logo_size'] = self.dict_widgets['logo_size'].currentText()

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

        for key in global_dict_prefs.keys():
            existing = self.settings.value(key)
            if key in var_existing_keys and existing != '': 
                global_dict_prefs[key] = self.settings.value(key)
            else:
                self.settings.setValue(key, global_dict_prefs[key])

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

        for key, value in global_dict_prefs.items():
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
                    global_dict_prefs[key] = value # This makes sure our running app is in sync
            
            self.sig_reset.emit()
            self.func_settings_init()