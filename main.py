import sys
import json
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import qtwidgets as qte # As in Qt Extra
import ghostlogic
import ghoststack

import qtstyles as qts


# This only contains stuff related to the main window and basic GUI drawing functions.
# Any time you add a new stack to the main window, that stack is actually covered by ghoststack.py
# The password generation stuff is in ghostlogic.py 



logic = ghostlogic.logic()

class main_window(qtw.QMainWindow):

    def __init__(self):
        super().__init__()

        font_id = qtg.QFontDatabase.addApplicationFont('ghostpass/typewcond_demi.otf')
        font_family = qtg.QFontDatabase.applicationFontFamilies(font_id)[0]
        font_typewriter_big = qtg.QFont(font_family)
        font_typewriter_big.setPointSize(18)


        self.settings = qtc.QSettings('most_ghost', 'ghostpass')

        try:
            test = self.settings.value('config/default')
            test.split('|')
        except:
            self.settings.setValue('config/default', '2|128')



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

        action_export.triggered.connect(self.export_settings)
        action_import.triggered.connect(self.import_settings)
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
        self.widget_pass_edit.on_toggle_password_Action() # These are the magic sauce to force visible
        layout_pass.addWidget(self.widget_pass_edit, 2)
        self.widget_salt_edit = qte.PasswordEdit()
        self.widget_salt_edit.setPlaceholderText('double pass')
        self.widget_salt_edit.on_toggle_password_Action()
        self.widget_salt_edit.setFont(font_typewriter_big)
        layout_pass.addWidget(self.widget_salt_edit, 1)
        widget_gen_all = qtw.QPushButton('generate all')
        widget_gen_all.clicked.connect(self.generate_all)
        widget_gen_all.setFont(font_typewriter_big)
        layout_pass.addWidget(widget_gen_all, 1)

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

        self.settings_init()
        # Now that everything's all set up and ready for us, we're going to load what the user previously 
        # had out of their settings and re-fill the GUI with their stuff.

        self.timer = qtc.QTimer()
        self.timer.timeout.connect(self.settings_update)
        self.timer.start(1000) # Call the timer, and re-apply our settings, every second (1000 milliseconds).
        # Maybe this seems excessive, but it doesn't really tax the system so why not? 
        # This way the settings should pretty much always be in sync.

        self.show()



    def add_stack(self, domain='domain'):
        pass_widget = self.widget_pass_edit
        salt_widget = self.widget_salt_edit
        layout = self.layout_scroll
        settings = self.settings
        self.setUpdatesEnabled(False)
        # I was catching some visual glitchiness where the screen would jitter. 
        # This forces Qt to take a quick break so that it is fully updated before continuing.
        widget_stack = ghoststack.Q_stack_widget(pass_widget, salt_widget, settings, domain)
        widget_stack.signal_delete.connect(lambda: self.remove_stack(widget_stack))
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

    def settings_init(self):
        try:
            size = self.settings.value('config/size')
            size = size.split(',')
            self.resize(qtc.QSize(int(size[0]),int(size[1])))
        except (TypeError, AttributeError):
            self.resize(qtc.QSize(600, 900))

        self.setMinimumSize(qtc.QSize(600, 400))

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

        for i in order: 
            if i in domains:
                continue
            domains.append(i)
        for i in domains:
            self.add_stack(i)
        # Normally I'd use a set to remove duplicates, but in this case the whole point is to keep the 
        # order of the widgets in the list. So this works to remove duplicates instead.
        # What will happen with this is that the last duplicate widget will get deleted, however the settings
        # on that widget are kept. I think this is a feature, not a bug- someone is probably adding their new domain
        # to the bottom because they don't see it on the list above, so we want to keep those newest settings. But
        # we don't want duplicates cluttering up the list if it's already on there.

    def settings_update(self):
        
        self.settings.clear()
        self.settings.setValue('config/size', f'{self.size().width()},{self.size().height()}')
        self.settings.setValue('config/order', '')
        self.settings.setValue('config/default', '2|128')

        index = self.layout_scroll.count()
        for i in range(index - 1):
            widget = self.layout_scroll.itemAt(i).widget()
            widget.save_settings()
        # Each stack is responsible for managing its own settings. It'll also tack its name onto the 'order' setting
        # before passing it along to the next one, so we'll get a handy list of which widgets go in which order.

    def reset_scroll_area(self):
        self.setUpdatesEnabled(False)

        index = self.layout_scroll.count()
        for i in range(index - 1):
            widget = self.layout_scroll.itemAt(i).widget()
            widget.deleteLater()
        
        self.settings_init()
        qtc.QTimer.singleShot(1, lambda: self.setUpdatesEnabled(True))
        qtc.QTimer.singleShot(2, lambda: self.repaint())

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



    def closeEvent(self, event):

        self.settings_update()
        super().closeEvent(event)
    # We're overwriting Qt's own 'close' function, just so that we can tack on one last settings update.
    # Just to make extra sure we're up to date.
    

    

if __name__ == '__main__': 
    app = qtw.QApplication(sys.argv)

#    app.setStyle('Fusion')
    styles = qtw.QStyleFactory.keys()
    app.setStyleSheet(qts.StylePicker("breeze-dark").get_sheet())
    mw = main_window()
    sys.exit(app.exec())




### TO DO LIST:

# Comment all of the code

# Settings dialog:
# Default hash length
# Default word length 
# Default to hash or words?
# Make sure to pull from defaults rather than domain name if domain name is 'domain'
# Can I make the password fields default to visible?

# Thread the dictionary to load it in faster

# Change the password field to a text edit. Change and delete as many of the fixed size widgets as you can.

# Expand the password mechanism to allow for 256 character max password
