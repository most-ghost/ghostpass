import sys
import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5.QtCore import pyqtSlot
import resources.qtextramods as qte
import resources.stackghost as stackghost
import resources.memghost as memghost
import resources.breeze_resources as breeze



# This only contains stuff related to the main window and basic GUI drawing functions.
# Any time you add a new stack to the main window, that stack is actually covered by ghoststack.py
# The password generation stuff is in ghostlogic.py


class cls_main_window(qtw.QMainWindow):

    def __init__(self):
        super().__init__()

        self.ref_memory = memghost.cls_obj_memory()
        self.ref_memory.sig_make_stack.connect(self.slot_add_stack)
        self.ref_memory.sig_reset.connect(self.slot_reset_scroll_area)


        try:
            temp_size = qtc.QSettings('most_ghost', 'ghostpass').value('config/size')
            temp_size = temp_size.split('|')
            self.resize(qtc.QSize(int(temp_size[0]),int(temp_size[1])))
            del temp_size
        except (TypeError, AttributeError):
            self.resize(qtc.QSize(600, 900))
            # There's no need to set this in settings yet- when settings are next set this'll get grabbed.
        self.setMinimumSize(qtc.QSize(600, 400))


        temp_font_id = qtg.QFontDatabase.addApplicationFont(
            os.path.join(
            os.path.dirname(__file__), "resources/typewcond_demi.otf"))
        temp_font_family = qtg.QFontDatabase.applicationFontFamilies(temp_font_id)[0]
        var_font_big = qtg.QFont(temp_font_family)
        var_font_big.setPointSize(18)
        self.font = var_font_big
        del temp_font_id
        del temp_font_family


        self.setWindowTitle('ghostpass')
        self.setWindowIconText('ghostpass')
        self.setWindowOpacity(0.98)

        menu_file = self.menuBar().addMenu('File')
        menu_help = self.menuBar().addMenu('Help')
        act_import = menu_file.addAction('Import')
        act_export = menu_file.addAction('Export')
        act_prefs = menu_file.addAction('Preferences')
        act_quit = menu_file.addAction('Quit')
        act_help = menu_help.addAction('Help')
        act_about = menu_help.addAction('About')

        act_export.triggered.connect(self.ref_memory.func_export_settings)
        act_import.triggered.connect(self.ref_memory.func_import_settings)
        act_prefs.triggered.connect(self.slot_show_settings)
        act_quit.triggered.connect(sys.exit)

        struct_top = qtw.QWidget(self) 
        # 'Structures' are my name for top level widgets that hold other widgets but aren't actually used.
        # They are only there to hold a 'layout', which then holds other widgets.
        lo_top = qtw.QVBoxLayout(struct_top)
        self.setCentralWidget(struct_top)

        wgt_logo = qtw.QLabel('ghostpass')
        wgt_logo.setFixedHeight(80)
        wgt_logo.setFont(var_font_big)
        wgt_logo.setAlignment(qtc.Qt.AlignHCenter | 
                             qtc.Qt.AlignVCenter) #qtc.Qt.AlignRight 
        lo_top.addWidget(wgt_logo)

        struct_pass_strip = qtw.QWidget()
        lo_pass_strip = qtw.QHBoxLayout(struct_pass_strip)
        lo_top.addWidget(struct_pass_strip)
        # The 'pass layer' refers to the strip or layer of GUI that is going to hold my password fields.

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
        if (qtc.QSettings('most_ghost', 'ghostpass').value('config/pass_visible')) == 'yes':
            self.wgt_pass_edit.on_toggle_password_Action()
            self.wgt_salt_edit.on_toggle_password_Action()


        struct_scroll_widget = qtw.QScrollArea()
        struct_stack_area = qtw.QWidget()
        struct_stack_area.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Fixed
        )

        struct_scroll_widget.setWidget(struct_stack_area)
        struct_scroll_widget.setWidgetResizable(True)
        lo_top.addWidget(struct_scroll_widget)  

        self.lo_scroll = qtw.QVBoxLayout(struct_stack_area)        

        wgt_add_stack = qtw.QPushButton('+')
        wgt_add_stack.setFont(var_font_big)
        wgt_add_stack.clicked.connect(
            lambda: self.slot_add_stack() ) 
        # We hide this behind a lambda instead of connecting it directly to get rid of the bool
        # which a click event otherwise generates and attaches to the signal
        self.lo_scroll.addWidget(wgt_add_stack)

        self.ref_memory.func_settings_init()
        # Now that everything's all set up and ready for us, we're going to load what the user previously 
        # had out of their settings and re-fill the GUI with their stuff.

        self.show()


    def slot_add_stack(self, domain='domain'):
        wgt_pass = self.wgt_pass_edit
        wgt_salt = self.wgt_salt_edit
        self.setUpdatesEnabled(False)
        # I was catching some visual glitchiness where the screen would jitter. 
        # This forces Qt to take a quick break so that it is fully updated before continuing.
        wgt_stack = stackghost.cls_stack_widget(wgt_pass, wgt_salt, domain)
        wgt_stack.sig_delete.connect(lambda: self.slot_remove_stack(wgt_stack))
        wgt_stack.sig_update.connect(lambda: self.ref_memory.func_settings_update(self.lo_scroll))
        self.lo_scroll.insertWidget(self.lo_scroll.count() - 1, wgt_stack)
        qtc.QTimer.singleShot(1, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(2, lambda: self.repaint())
        # Wait 1 millisecond before un-stopping yourself. Then after 2 milliseconds, re-make the GUI.
        # It seems to work and forces the GUI to do any jittery thinky things off-screen and in the 
        # background, where it won't bother us.

    @pyqtSlot(qtc.QMetaObject)
    def slot_remove_stack(self, wgt_stack):
        self.setUpdatesEnabled(False)
        wgt_stack.deleteLater()
        qtc.QTimer.singleShot(1, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(2, lambda: self.repaint())
        # Actually this maybe could've been handled within ghoststack.py? Oh well, it's here now.

    @pyqtSlot()
    def slot_generate_all(self):
        temp_index = self.lo_scroll.count()
        for count in range(temp_index - 1): # -1 because there's a '+' button widget at the very end
            widget = self.lo_scroll.itemAt(count).widget()
            widget.slot_fake_gen_click()
            qtw.QApplication.processEvents()

    @pyqtSlot()
    def slot_reset_scroll_area(self):
        self.setUpdatesEnabled(False)

        temp_index = self.lo_scroll.count()
        for count in range(temp_index - 1):
            widget = self.lo_scroll.itemAt(count).widget()
            widget.deleteLater()
        
        qtc.QTimer.singleShot(4, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(5, lambda: self.repaint())


    def slot_show_settings(self):
        popup_settings = memghost.cls_popup_settings(self)
        popup_settings.sig_saved.connect(lambda: self.ref_memory.func_settings_update(self.lo_scroll))
        popup_settings.exec()
        

    def closeEvent(self, event):

        self.ref_memory.func_settings_update(self.lo_scroll)
        qtc.QSettings('most_ghost', 'ghostpass').setValue('config/size', f'{self.size().width()}|{self.size().height()}')
        super().closeEvent(event)
    # We're overwriting Qt's own 'close' function, just so that we can tack on one last settings update.
    # Just to make extra sure we're up to date.
    

    

if __name__ == '__main__': 
    app = qtw.QApplication(sys.argv)
    style_file = qtc.QFile(":/dark/stylesheet.qss")
    style_file.open(qtc.QFile.ReadOnly | qtc.QFile.Text)
    stream = qtc.QTextStream(style_file)
    app.setStyleSheet(stream.readAll())
    window_main = cls_main_window()
    sys.exit(app.exec())



### TO DO LIST:

# Comment all of the code
# Thread the settings
# Make delete work on a 2 click system
# Domain name entry widget mucks up
# Got to throw in an about/help section too.
# (although perhaps instead of having that it should have a popup dialog box when you hit +)