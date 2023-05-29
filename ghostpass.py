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

        struct_top = qtw.QWidget(self) 
        # 'Structures' are my name for top level widgets that hold other widgets but aren't actually used.
        # They are only there to hold a layout, which then hold all of the other meaningful widgets.
        lo_top = qtw.QVBoxLayout(struct_top)
        self.setCentralWidget(struct_top)

        wgt_logo = qtw.QLabel()

        temp_logo_size = self.settings.value('--ghostconfig/logo_size')
        if temp_logo_size == 'normal':
            img_logo = qtg.QPixmap(
                os.path.join(
                os.path.dirname(__file__), "resources/ghostlogo.png"))
            wgt_logo.setPixmap(img_logo)
            wgt_logo.setFixedHeight(200)
        elif temp_logo_size == '2x':
            img_logo = qtg.QPixmap(
                os.path.join(
                os.path.dirname(__file__), "resources/ghostdouble.png"))
            wgt_logo.setPixmap(img_logo)
            wgt_logo.setFixedHeight(400)
        elif temp_logo_size == 'disabled':
            wgt_logo.setText('ghostpass')
            wgt_logo.setFont(var_font_big)
            wgt_logo.setFixedHeight(35)
        del temp_logo_size

        wgt_logo.setAlignment(qtc.Qt.AlignHCenter | 
                             qtc.Qt.AlignVCenter)
        lo_top.addWidget(wgt_logo)

        struct_pass_strip = qtw.QWidget() # 'pass strip' as in the strip of gui that holds both password fields
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



        struct_scroll_widget = qtw.QScrollArea()
        struct_stack_area = qtw.QWidget()
        struct_stack_area.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Fixed
        )

        struct_scroll_widget.setWidget(struct_stack_area)
        struct_scroll_widget.setWidgetResizable(True)
        struct_scroll_widget.setStyleSheet("QScrollArea:hover {border: none;}")
        lo_top.addWidget(struct_scroll_widget)  

        self.lo_scroll = qtw.QVBoxLayout(struct_stack_area)

        wgt_add_stack = qtw.QPushButton('+')
        wgt_add_stack.setFont(var_font_big)
        wgt_add_stack.clicked.connect(
            lambda: self.slot_add_stack() ) 
        # We hide this behind a lambda instead of connecting it directly because 
        # the 'clicked' event attaches a bool to the sending signal otherwise.
        self.lo_scroll.addWidget(wgt_add_stack)

        self.ref_memory.func_settings_init()

        self.show()


    def slot_add_stack(self, domain='app or site'):
        wgt_pass = self.wgt_pass_edit
        wgt_salt = self.wgt_salt_edit
        # We're passing a reference to the widget rather than only the text because we want to
        # check the text later on, immediately before generating a password
        
        self.setUpdatesEnabled(False)

        wgt_stack = stackghost.cls_stack_widget(wgt_pass, wgt_salt, domain)
        wgt_stack.sig_delete.connect(lambda: self.slot_remove_stack(wgt_stack))
        wgt_stack.sig_update.connect(lambda: self.ref_memory.func_settings_update(self.lo_scroll))

        self.lo_scroll.insertWidget(self.lo_scroll.count() - 1, wgt_stack)
        
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
        popup_settings.sig_saved.connect(lambda: self.ref_memory.func_settings_update(self.lo_scroll))
        popup_settings.exec()

    def slot_show_about(self):
        popup_about = aboutghost.cls_popup_about(self)
        popup_about.exec()

    def func_autoblank(self, widget):
        if self.settings.value('--ghostconfig/autoblank') == 'yes':
            qtc.QTimer.singleShot(60000, lambda: widget.setText(""))
                # 60000 milliseconds = 1 minute
        

    def closeEvent(self, event):
        self.ref_memory.func_settings_update(self.lo_scroll)
        self.settings.setValue('--ghostconfig/size', f'{self.size().width()}|{self.size().height()}')
        super().closeEvent(event)
    

if __name__ == '__main__': 
    app = qtw.QApplication(sys.argv)
    style_file = qtc.QFile(":/dark-spooky/stylesheet.qss")
    style_file.open(qtc.QFile.ReadOnly | qtc.QFile.Text)
    stream = qtc.QTextStream(style_file)
    app.setStyleSheet(stream.readAll())
    window_main = cls_main_window()
    sys.exit(app.exec())

