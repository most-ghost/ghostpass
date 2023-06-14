import sys
import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import pyqtSlot
import resources.qtextramods as qte
import resources.stackghost as stackghost
import resources.memghost as memghost
import resources.aboutghost as aboutghost
import resources.fontghost as fontghost
import resources.breeze_spooky



class cls_main_window(qtw.QMainWindow):
    """ 
    This is the code for the GUI of the main window only. Code to maintain each stack widget is in stackghost.py,
    password generation code is in smartghost and code related to settings management is in memghost.
    """


    def __init__(self):
        super().__init__()

        ### GENERAL WINDOW SETTINGS AND INIT

        self.settings = qtc.QSettings('most_ghost', 'ghostpass')

        self.ref_memory = memghost.cls_obj_memory()
        self.ref_memory.sig_make_stack.connect(self.slot_add_stack)
        self.ref_memory.sig_reset.connect(self.slot_reset_scroll_area)

        self.setStyleSheet("border-radius: 5px")

        self.setWindowIcon(qtg.QIcon(
            os.path.join(
            os.path.dirname(__file__), "resources/ghosticon.svg")))

        try:
            temp_size = self.settings.value('--ghostconfig/size')
            temp_size = temp_size.split('|')
            self.resize(qtc.QSize(int(temp_size[0]),int(temp_size[1])))
            del temp_size
        except (TypeError, AttributeError):
            self.resize(qtc.QSize(800, 1000)) # Default size if no settings are found
        self.setMinimumSize(qtc.QSize(600, 400))

        self.font_typewriter = fontghost.fontghost.typewriter(13)
        self.font_typewriter_big = fontghost.fontghost.typewriter(18)

        self.setWindowTitle('ghostpass')
        self.menuBar().setFont(self.font_typewriter)
        self.setWindowIconText('ghostpass')
        self.setWindowOpacity(0.98) # for that ghostly touch

        ### TOP MENU

        menu_file = self.menuBar().addMenu('system')
        menu_file.setFont(self.font_typewriter)
        act_import = menu_file.addAction('import')
        act_export = menu_file.addAction('export')
        menu_file.addSeparator()
        act_prefs = menu_file.addAction('preferences')
        act_about = menu_file.addAction('readme')
        act_quit = menu_file.addAction('quit')

        act_export.triggered.connect(self.ref_memory.func_export_settings)
        act_import.triggered.connect(self.ref_memory.func_import_settings)
        act_prefs.triggered.connect(self.slot_show_settings)
        act_about.triggered.connect(self.slot_show_about)
        act_quit.triggered.connect(sys.exit)

        ### MAIN WIDGET - TOP LEVEL

        struct_top = qtw.QWidget(self) 
        # 'Structures' are my name for top level widgets that hold other widgets but aren't actually used.
        # They are only there to hold a layout, which then hold all of the other meaningful widgets.
        lo_top = qtw.QVBoxLayout(struct_top)
        self.setCentralWidget(struct_top)

        wgt_logo = qtw.QLabel()
        self.func_set_logo_size(wgt_logo, self.font_typewriter_big)
        wgt_logo.setAlignment(qtc.Qt.AlignHCenter | 
                             qtc.Qt.AlignVCenter)
        lo_top.addWidget(wgt_logo)

        ### MAIN WIDGET - PASSWORD STRIP

        struct_pass_strip = qtw.QWidget()
        lo_pass_strip = qtw.QHBoxLayout(struct_pass_strip)
        lo_top.addWidget(struct_pass_strip)

        self.wgt_pass_edit = qte.PasswordEdit()
        self.wgt_pass_edit.setPlaceholderText('password')
        self.wgt_pass_edit.setFont(self.font_typewriter_big)
        lo_pass_strip.addWidget(self.wgt_pass_edit, 2)
        self.wgt_salt_edit = qte.PasswordEdit()
        self.wgt_salt_edit.setPlaceholderText('double pass')
        self.wgt_salt_edit.setFont(self.font_typewriter_big)
        lo_pass_strip.addWidget(self.wgt_salt_edit, 1)
        wgt_gen_all = qtw.QPushButton('generate all')
        wgt_gen_all.clicked.connect(self.slot_generate_all)
        wgt_gen_all.setFont(self.font_typewriter_big)
        lo_pass_strip.addWidget(wgt_gen_all, 1)
        if (self.settings.value('--ghostconfig/pass_visible')) == 'yes':
            self.wgt_pass_edit.on_toggle_password_Action()
            self.wgt_salt_edit.on_toggle_password_Action()
        self.wgt_pass_edit.editingFinished.connect(lambda: self.func_autoblank(self.wgt_pass_edit))
        self.wgt_salt_edit.editingFinished.connect(lambda: self.func_autoblank(self.wgt_salt_edit))

        ### MAIN WINDOW - STACK AREA - TABS AND STACKS

        self.struct_tab_widget = qtw.QTabWidget()
        self.struct_tab_widget.setFont(self.font_typewriter)
        self.struct_tab_widget.setStyleSheet("""
            QTabWidget::pane {border: 5px solid #3e2680;
                              border-right: 0px;
                              border-bottom: 0px;
                              border-top-left-radius: 15px;
                              }
            QTabWidget::tab-bar {top: 15px;}
            QTabBar::tab {background-color: #0e0d0a; 
                          color: #d4d8e0;
                          padding: 10px;
                          border: 0px none} 
            QTabBar::tab:selected {background-color: #3e2680;
                                   color: #d4d8e0; 
                                   border-color: #9B9B9B;
                                   border-bottom-color: #d4d8e0; }
            """)
        self.struct_tab_widget.setTabPosition(qtw.QTabWidget.West)
        self.struct_tab_widget.setMovable(True)

        self.func_fill_tab_dict(self.font_typewriter_big)
        lo_top.addWidget(self.struct_tab_widget)

        self.ref_memory.func_settings_init()

        self.show()


    def slot_add_stack(self, domain='app or site', tab=''):
        wgt_pass = self.wgt_pass_edit
        wgt_salt = self.wgt_salt_edit
        if tab == '':
            tab = self.struct_tab_widget.tabText(self.struct_tab_widget.currentIndex())
        if domain == '':
            domain = 'app or site'
        scroll_layout = self.dict_tabs[tab]['layout']

        # We're passing a reference to the widget rather than only the text because we want to
        # check the text later on, immediately before generating a password
        # You should probably do this with signals instead, this is not the best method.
        
        self.setUpdatesEnabled(False)

        wgt_stack = stackghost.cls_stack_widget(wgt_pass, wgt_salt, domain, tab)
        wgt_stack.sig_delete.connect(lambda: self.slot_remove_stack(wgt_stack))
        wgt_stack.sig_update.connect(lambda: self.ref_memory.func_settings_update(self.dict_tabs))

        scroll_layout.insertWidget(scroll_layout.count() - 1, wgt_stack)
        
        qtc.QTimer.singleShot(1, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(2, lambda: self.repaint())
        # Qt needs a moment to have a good think and in the meantime it likes to freak out a little.
        # It's a jank solution but just stopping updates for a millisecond is enough time to let it work it out.

    @pyqtSlot(qtc.QMetaObject)
    def slot_remove_stack(self, wgt_stack):
        self.setUpdatesEnabled(False)

        wgt_stack.deleteLater()

        qtc.QTimer.singleShot(1, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(2, lambda: self.repaint())

    @pyqtSlot()
    def slot_generate_all(self):

        list_tabs = [self.struct_tab_widget.tabText(i) for i in range(self.struct_tab_widget.count())]
        print(list_tabs)

        for tab in list_tabs:

            temp_index = self.dict_tabs[tab]['layout'].count()

            for count in range(temp_index - 1): # -1 because there's a '+' button widget at the very end
                widget = self.dict_tabs[tab]['layout'].itemAt(count).widget()
                widget.slot_fake_gen_click()
                qtw.QApplication.processEvents()
                # 'Process Events' ensures that Qt will stop and update whenever it has generated a password,
                # meaning each password gets shown being filled in sequentially.

    @pyqtSlot()
    def slot_reset_scroll_area(self):
        self.setUpdatesEnabled(False)

        for tab in self.dict_tabs.keys():
            temp_index = self.dict_tabs[tab]['layout'].count()
            for count in range(temp_index - 1):
                for count in range(temp_index - 1):
                    widget = self.dict_tabs[tab]['layout'].itemAt(count).widget()
                    widget.deleteLater()
        
        qtc.QTimer.singleShot(4, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(10, lambda: self.repaint())

    @pyqtSlot()
    def slot_show_settings(self):
        popup_settings = memghost.cls_popup_settings(self)
        for tab in self.dict_tabs.keys():
            popup_settings.sig_saved.connect(lambda: self.ref_memory.func_settings_update(self.dict_tabs))
        popup_settings.sig_add_tab.connect(self.hook_up_add_tab)
        popup_settings.sig_delete_tab.connect(self.hook_up_delete_tab)
        popup_settings.sig_rename_tab.connect(self.hook_up_rename_tab)
        popup_settings.exec()

    def slot_show_about(self):
        popup_about = aboutghost.cls_popup_about(self)
        popup_about.exec()

    def func_autoblank(self, widget):
        if self.settings.value('--ghostconfig/autoblank') == 'yes':
            qtc.QTimer.singleShot(60000, lambda: widget.setText(""))
                # 60000 milliseconds = 1 minute
        
    def func_set_logo_size(self, logo, font):
        temp_logo_size = self.settings.value('--ghostconfig/logo_size')
        if temp_logo_size == 'normal':
            img_logo = qtg.QPixmap(
                os.path.join(
                os.path.dirname(__file__), "resources/ghostlogo.png"))
            logo.setPixmap(img_logo)
            logo.setFixedHeight(200)
        elif temp_logo_size == '2x':
            img_logo = qtg.QPixmap(
                os.path.join(
                os.path.dirname(__file__), "resources/ghostdouble.png"))
            logo.setPixmap(img_logo)
            logo.setFixedHeight(400)
        elif temp_logo_size == 'disabled':
            logo.setText('ghostpass')
            logo.setFont(font)
            logo.setFixedHeight(35)

    def func_fill_tab_dict(self, font):
        tab_list = self.settings.value('--ghostconfig/tab_order').split('|')
        self.dict_tabs = {tab:{'struct': qtw.QScrollArea(), # 0 This is the struct that holds everything
                               'list': qtw.QWidget(), # 1 Widget that contains the tabs
                               'layout': qtw.QVBoxLayout(), # 2 Layout for above widget
                               '+': qtw.QPushButton('+') # 3 '+' add button
                               }  for tab in tab_list}
        
        for tab in self.dict_tabs.keys():
            self.dict_tabs[tab]['list'].setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Fixed
            )

            self.dict_tabs[tab]['struct'].setWidget(self.dict_tabs[tab]['list'])
            self.dict_tabs[tab]['struct'].setWidgetResizable(True)
            self.dict_tabs[tab]['struct'].setStyleSheet("QScrollArea:hover {border: none;}")

            self.dict_tabs[tab]['list'].setLayout(self.dict_tabs[tab]['layout'])

            self.dict_tabs[tab]['+'].setFont(font)

            self.dict_tabs[tab]['+'].clicked.connect(
                lambda: self.slot_add_stack() )
            
            self.dict_tabs[tab]['layout'].addWidget(self.dict_tabs[tab]['+'])

        for tab in self.dict_tabs:
            self.struct_tab_widget.addTab(self.dict_tabs[tab]['struct'], tab)


    def func_update_tab_order(self):
        self.settings.setValue('--ghostconfig/tab_order', 
                               '|'.join(
            [self.struct_tab_widget.tabText(i) for i in range( self.struct_tab_widget.count() ) ]
                              ))
        

    def hook_up_add_tab(self, tab_name):
        self.func_update_tab_order()
        self.ref_memory.func_settings_update(self.dict_tabs)
        
        old_tabs = self.settings.value('--ghostconfig/tab_order')
        new_tabs = old_tabs + '|' + tab_name
        self.settings.setValue('--ghostconfig/tab_order', new_tabs)

        self.struct_tab_widget.clear()
        self.dict_tabs = {}
        self.func_fill_tab_dict(self.font_typewriter)
        self.ref_memory.func_settings_init()
        self.func_update_tab_order()


    def hook_up_delete_tab(self, tab_name):
        if tab_name in self.dict_tabs.keys():
            self.settings.beginGroup('--ghost_tabs')
            self.settings.remove(tab_name)
            self.settings.endGroup()

            order = self.settings.value('--ghostconfig/tab_order').split('|')
            order.pop(order.index(tab_name))
            self.settings.setValue('--ghostconfig/tab_order', '|'.join(order))

            to_delete = [x for x in self.settings.childGroups() if x.split('_')[-1] == tab_name]
            for group in to_delete:
                self.settings.beginGroup(group)
                for key in group:
                    self.settings.remove(key)
                self.settings.endGroup()
                self.settings.remove(group)

        self.struct_tab_widget.clear()
        self.dict_tabs = {}
        self.func_fill_tab_dict(self.font_typewriter)
        self.ref_memory.func_settings_init()
        self.func_update_tab_order()


    def hook_up_rename_tab(self, new_tab, old_tab):
        old_value = self.settings.value(f'--ghost_tabs/{old_tab}')
        self.settings.beginGroup('--ghost_tabs')
        self.settings.setValue(new_tab, old_value)
        self.settings.remove(old_tab)
        self.settings.endGroup()

        order = self.settings.value('--ghostconfig/tab_order').split('|')
        index = order.index(old_tab)
        order.pop(index)
        order.insert(index, new_tab)
        self.settings.setValue('--ghostconfig/tab_order', '|'.join(order))

        to_change = [x for x in self.settings.childGroups() if x.split('_')[-1] == old_tab]
        for group in to_change:
            self.settings.beginGroup(group)
            old_values = {key: self.settings.value(key) for key in self.settings.childKeys()}
            for key in group:
                self.settings.remove(key)
            self.settings.endGroup()
            self.settings.remove(group)

            new_group = group.split('_')[:-1]
            new_group.append(new_tab)
            new_group = "_".join(new_group)

            self.settings.beginGroup(new_group)
            for key, value in old_values.items():
                self.settings.setValue(key, value)
            self.settings.endGroup()

        self.struct_tab_widget.clear()
        self.dict_tabs = {}
        self.func_fill_tab_dict(self.font_typewriter)
        self.ref_memory.func_settings_init()
        self.func_update_tab_order()
      

    def closeEvent(self, event):
        # This is a built in Qt method that's being overwritten 
        # So that settings can be updated one last time before the window closes.
        for tab in self.dict_tabs.keys():
            self.ref_memory.func_settings_update(self.dict_tabs)
        self.settings.setValue('--ghostconfig/size', f'{self.size().width()}|{self.size().height()}')
        self.func_update_tab_order()
        super().closeEvent(event)
    

if __name__ == '__main__': 
    app = qtw.QApplication(sys.argv)
    img_splash = qtg.QPixmap(os.path.join(
                             os.path.dirname(__file__), "resources/ghostdouble.png"))
    window_splash = qtw.QSplashScreen(img_splash)
    window_splash.show()
    qtw.QApplication.processEvents()
    style_file = qtc.QFile(":/dark-spooky/stylesheet.qss")
    style_file.open(qtc.QFile.ReadOnly | qtc.QFile.Text)
    stream = qtc.QTextStream(style_file)
    app.setStyleSheet(stream.readAll())
    window_main = cls_main_window()
    window_splash.close()
    sys.exit(app.exec())
