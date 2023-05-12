import sys
import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import resources.qtextramods as qte
import resources.stackghost as stackghost
import resources.memghost as memghost


# This only contains stuff related to the main window and basic GUI drawing functions.
# Any time you add a new stack to the main window, that stack is actually covered by ghoststack.py
# The password generation stuff is in ghostlogic.py


class main_window(qtw.QMainWindow):

    def __init__(self):
        super().__init__()

        self.memory = memghost.memory()
        self.memory.stack_pass.connect(self.add_stack)
        self.memory.signal_reset.connect(self.reset_scroll_area)


        try:
            size = qtc.QSettings('most_ghost', 'ghostpass').value('config/size')
            size = size.split(',')
            self.resize(qtc.QSize(int(size[0]),int(size[1])))
        except (TypeError, AttributeError):
            self.resize(qtc.QSize(600, 900))
        self.setMinimumSize(qtc.QSize(600, 400))


        font_id = qtg.QFontDatabase.addApplicationFont(
            os.path.join(
            os.path.dirname(__file__), "resources/typewcond_demi.otf"))
        font_family = qtg.QFontDatabase.applicationFontFamilies(font_id)[0]
        font_typewriter_big = qtg.QFont(font_family)
        font_typewriter_big.setPointSize(18)
        self.font = font_typewriter_big

        self.setWindowTitle('ghostpass')
        self.setWindowIconText('ghostpass')
        self.setWindowOpacity(0.98)

        menu_file = self.menuBar().addMenu('File')
        menu_help = self.menuBar().addMenu('Help')
        action_import = menu_file.addAction('Import')
        action_export = menu_file.addAction('Export')
        action_preferences = menu_file.addAction('Preferences')
        action_quit = menu_file.addAction('Quit')
        action_help = menu_help.addAction('Help')
        action_about = menu_help.addAction('About')

        action_export.triggered.connect(self.memory.export_settings)
        action_import.triggered.connect(self.memory.import_settings)
        action_preferences.triggered.connect(self.show_settings)
        action_quit.triggered.connect(sys.exit)

        structure_top = qtw.QWidget(self) 
        # 'Structures' are my name for widgets that hold other widgets but aren't actually used.
        # They are only there to hold a 'layout', which then holds other widgets. Which could themselves
        # be another structure widget, which holds a layout, which holds more widgets.
        # Qt uses this nested structure to build its GUI.
        layout_top = qtw.QVBoxLayout(structure_top)
        self.setCentralWidget(structure_top)

        # Putting 'structure_' and 'layout_' may seem verbose but it's useful for keeping track - I can
        # type in 'structure_' and auto complete will give me a list of all of the structure-type widgets I've got.
        # As long as I know I'm looking for, say, a layout, I can ctrl+F for 'layout_' and cycle through them.
        # It's pretty useful.

        widget_logo = qtw.QLabel('ghostpass')
        widget_logo.setFixedHeight(80)
        widget_logo.setFont(font_typewriter_big)
        widget_logo.setAlignment(qtc.Qt.AlignHCenter | 
                             qtc.Qt.AlignVCenter) #qtc.Qt.AlignRight 
        layout_top.addWidget(widget_logo)

        structure_pass_layer = qtw.QWidget()
        layout_pass = qtw.QHBoxLayout(structure_pass_layer)
        layout_top.addWidget(structure_pass_layer)
        # The 'pass layer' refers to the strip or layer of GUI that is going to hold my password fields.

        self.widget_pass_edit = qte.PasswordEdit()
        self.widget_pass_edit.setPlaceholderText('password')
        self.widget_pass_edit.setFont(font_typewriter_big)
        layout_pass.addWidget(self.widget_pass_edit, 2)
        self.widget_salt_edit = qte.PasswordEdit()
        self.widget_salt_edit.setPlaceholderText('double pass')
        self.widget_salt_edit.setFont(font_typewriter_big)
        layout_pass.addWidget(self.widget_salt_edit, 1)
        widget_gen_all = qtw.QPushButton('generate all')
        widget_gen_all.clicked.connect(self.generate_all)
        widget_gen_all.setFont(font_typewriter_big)
        layout_pass.addWidget(widget_gen_all, 1)
        if (qtc.QSettings('most_ghost', 'ghostpass').value('config/pass_visible')) == 'yes':
            self.widget_pass_edit.on_toggle_password_Action()
            self.widget_salt_edit.on_toggle_password_Action()


        structure_scroll_area = qtw.QScrollArea()
        structure_scroll_widget = qtw.QWidget()
        structure_scroll_widget.setSizePolicy(
            qtw.QSizePolicy.Expanding,
            qtw.QSizePolicy.Fixed
        )
            
        self.layout_scroll = qtw.QVBoxLayout(structure_scroll_widget)        


        widget_add_stack = qtw.QPushButton('+')
        widget_add_stack.setFont(font_typewriter_big)
        widget_add_stack.clicked.connect(
            lambda: self.add_stack() ) 
        # The reason to hide this behind a lambda is because by default 'clicked' attaches a bool,
        # which we do not want since we have a key word argument that gets fed that bool by accident.
        # By making the lambda call to hold the function until later, and specifically saying we do 
        # not want any arguments, we can skip that bool since Qt throws away unused arguments.
        self.layout_scroll.addWidget(widget_add_stack)

        structure_scroll_area.setWidget(structure_scroll_widget)
        structure_scroll_area.setWidgetResizable(True)
        layout_top.addWidget(structure_scroll_area)

        self.memory.settings_init()
        # Now that everything's all set up and ready for us, we're going to load what the user previously 
        # had out of their settings and re-fill the GUI with their stuff.

        # self.timer = qtc.QTimer()
        # self.timer.timeout.connect(lambda: self.memory.settings_update(self.layout_scroll))
        # self.timer.start(1000) # Call the timer, and re-apply our settings, every second (1000 milliseconds).
        # # Maybe this seems excessive, but it doesn't really tax the system so why not? 
        # # This way the settings should pretty much always be in sync.

        self.show()

    def add_stack(self, domain='domain'):
        pass_widget = self.widget_pass_edit
        salt_widget = self.widget_salt_edit
        layout = self.layout_scroll
        self.setUpdatesEnabled(False)
        # I was catching some visual glitchiness where the screen would jitter. 
        # This forces Qt to take a quick break so that it is fully updated before continuing.
        widget_stack = stackghost.class_stack_widget(pass_widget, salt_widget, domain)
        widget_stack.signal_delete.connect(lambda: self.remove_stack(widget_stack))
        widget_stack.signal_update.connect(lambda: self.memory.settings_update(self.layout_scroll))
        layout.insertWidget(layout.count() - 1, widget_stack)
        qtc.QTimer.singleShot(1, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(2, lambda: self.repaint())
        # Wait 1 millisecond before un-stopping yourself. Then after 2 milliseconds, re-make the GUI.
        # It seems to work and forces the GUI to do any jittery thinky things off-screen and in the 
        # background, where it won't bother us.


    def remove_stack(self, widget_stack):
        self.setUpdatesEnabled(False)
        widget_stack.deleteLater()
        qtc.QTimer.singleShot(1, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(2, lambda: self.repaint())
        # Actually this maybe could've been handled within ghoststack.py? Oh well, it's here now.


    def generate_all(self):
        index = self.layout_scroll.count()
        for i in range(index - 1):
            widget = self.layout_scroll.itemAt(i).widget()
            widget.fake_gen_click()
            qtw.QApplication.processEvents()
        # 'Generate all' as in generate all passwords. This just goes ahead and clicks that 'generate'
        # button on each widget for you.


    def reset_scroll_area(self):
        self.setUpdatesEnabled(False)

        index = self.layout_scroll.count()
        for i in range(index - 1):
            widget = self.layout_scroll.itemAt(i).widget()
            widget.deleteLater()
        
        # self.memory.settings_init()
        qtc.QTimer.singleShot(4, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(5, lambda: self.repaint())


    def show_settings(self):
        settings_dialog = memghost.settings_dialog(self) # I'm not entirely sure what the deal with this second 'self' is. It's related to the no parent thing above, but how exactly, I'm not sure.
        settings_dialog.saved.connect(lambda: self.memory.settings_update(self.layout_scroll))
        settings_dialog.exec()
        


    def closeEvent(self, event):

        self.memory.settings_update(self.layout_scroll)
        qtc.QSettings('most_ghost', 'ghostpass').setValue('config/size', f'{self.size().width()},{self.size().height()}')
        super().closeEvent(event)
    # We're overwriting Qt's own 'close' function, just so that we can tack on one last settings update.
    # Just to make extra sure we're up to date.
    

    

if __name__ == '__main__': 
    app = qtw.QApplication(sys.argv)

#    app.setStyle('Fusion')
    styles = qtw.QStyleFactory.keys()
    window_main = main_window()
    sys.exit(app.exec())




### TO DO LIST:

# Comment all of the code
# Thread the dictionary to load it in faster
# Thread the update code as well