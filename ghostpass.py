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
            self.resize(qtc.QSize(600, 900)) # Default size if no settings are found
        self.setMinimumSize(qtc.QSize(600, 400))

        temp_font_id = qtg.QFontDatabase.addApplicationFont(
            os.path.join(
            os.path.dirname(__file__), "resources/typewcond_demi.otf"))
        temp_font_family = qtg.QFontDatabase.applicationFontFamilies(temp_font_id)[0]
        var_font = qtg.QFont(temp_font_family)
        var_font.setPointSize(13)
        var_font_big = qtg.QFont(temp_font_family)
        var_font_big.setPointSize(18)
        del temp_font_id
        del temp_font_family

        self.setWindowTitle('ghostpass')
        self.menuBar().setFont(var_font)
        self.setWindowIconText('ghostpass')
        self.setWindowOpacity(0.98) # for that ghostly touch

        ### TOP MENU

        menu_file = self.menuBar().addMenu('system')
        menu_file.setFont(var_font)
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
        self.func_set_logo_size(wgt_logo, var_font_big)
        wgt_logo.setAlignment(qtc.Qt.AlignHCenter | 
                             qtc.Qt.AlignVCenter)
        lo_top.addWidget(wgt_logo)

        ### MAIN WIDGET - PASSWORD STRIP

        struct_pass_strip = qtw.QWidget()
        lo_pass_strip = qtw.QHBoxLayout(struct_pass_strip)
        lo_top.addWidget(struct_pass_strip)

        self.wgt_pass_edit = qte.PasswordEdit()
        self.wgt_pass_edit.setPlaceholderText('password')
        self.wgt_pass_edit.setFont(var_font_big)
        lo_pass_strip.addWidget(self.wgt_pass_edit, 2)
        self.wgt_salt_edit = qte.PasswordEdit()
        self.wgt_salt_edit.setPlaceholderText('double pass')
        self.wgt_salt_edit.setFont(var_font_big)
        lo_pass_strip.addWidget(self.wgt_salt_edit, 1)
        wgt_gen_all = qtw.QPushButton('generate all')
        wgt_gen_all.clicked.connect(self.slot_generate_all)
        wgt_gen_all.setFont(var_font_big)
        lo_pass_strip.addWidget(wgt_gen_all, 1)
        if (self.settings.value('--ghostconfig/pass_visible')) == 'yes':
            self.wgt_pass_edit.on_toggle_password_Action()
            self.wgt_salt_edit.on_toggle_password_Action()
        self.wgt_pass_edit.editingFinished.connect(lambda: self.func_autoblank(self.wgt_pass_edit))
        self.wgt_salt_edit.editingFinished.connect(lambda: self.func_autoblank(self.wgt_salt_edit))

        ### MAIN WINDOW - STACK AREA - TABS AND STACKS

        self.struct_tab_widget = qtw.QTabWidget()
        self.struct_tab_widget.setFont(var_font)
        self.struct_tab_widget.setStyleSheet("""
            QTabWidget::pane {border-left: 5px solid #3e2680;
                              border-right: 0px;
                              border-bottom: 0px;
                              border-top: 5px solid #3e2680;
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

        self.func_fill_tab_dict(var_font_big)
        for tab in self.dict_tabs:
            self.struct_tab_widget.addTab(self.dict_tabs[tab]['struct'], tab)
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
        
        temp_index = self.lo_scroll.count()

        for count in range(temp_index - 1): # -1 because there's a '+' button widget at the very end
            widget = self.lo_scroll.itemAt(count).widget()
            widget.slot_fake_gen_click()
            qtw.QApplication.processEvents()
            # 'Process Events' ensures that Qt will stop and update whenever it has generated a password,
            # meaning each password gets shown being filled in sequentially. A better solution would have been
            # multithreading but the design of ghostpass with each stack individually managing itself doesn't
            # lend itself easily to multithreading. Lessons for the future.

    @pyqtSlot()
    def slot_reset_scroll_area(self):
        self.setUpdatesEnabled(False)

        temp_index = self.lo_scroll.count()
        for count in range(temp_index - 1):
            widget = self.lo_scroll.itemAt(count).widget()
            widget.deleteLater()
        
        qtc.QTimer.singleShot(4, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(5, lambda: self.repaint())

    @pyqtSlot()
    def slot_show_settings(self):
        popup_settings = memghost.cls_popup_settings(self)
        for tab in self.dict_tabs.keys():
            popup_settings.sig_saved.connect(lambda: self.ref_memory.func_settings_update(self.dict_tabs))
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

            

    def closeEvent(self, event):
        for tab in self.dict_tabs.keys():
            self.ref_memory.func_settings_update(self.dict_tabs)
        self.settings.setValue('--ghostconfig/size', f'{self.size().width()}|{self.size().height()}')
        self.settings.setValue('--ghostconfig/tab_order', 
                               '|'.join(
            [self.struct_tab_widget.tabText(i) for i in range( self.struct_tab_widget.count() ) ]
                              ))
        super().closeEvent(event)
    

if __name__ == '__main__': 
    app = qtw.QApplication(sys.argv)
    style_file = qtc.QFile(":/dark-spooky/stylesheet.qss")
    style_file.open(qtc.QFile.ReadOnly | qtc.QFile.Text)
    stream = qtc.QTextStream(style_file)
    app.setStyleSheet(stream.readAll())
    window_main = cls_main_window()
    sys.exit(app.exec())

