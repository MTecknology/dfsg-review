'''
Main Menu
'''
# Python
import tkinter.ttk
import tkinter.filedialog

# DCheck
import dcheck.gui.about

from dcheck.i18n import t


class MainMenu(tkinter.Menu):
    '''
    Application menu.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # File
        self.file = tkinter.Menu(self, tearoff=0)
        self.add_cascade(label=t('menu_file'), menu=self.file)
        self.file.add_command(
                label=t('menu_pkgnav'), command=self.show_pkgnav)
        self.file.add_separator()
        self.file.add_command(
                label=t('menu_exit'), command=self.master.destroy)

        # Help
        self.help = tkinter.Menu(self, tearoff=0)
        self.add_cascade(label=t('menu_help'), menu=self.help)
        self.help.add_command(label=t('menu_about'), command=self.show_about)

    def show_pkgnav(self):
        '''
        Display the package navigation pane.
        '''
        self.parent.set_mainframe('pkgnav')

    def show_about(self):
        '''
        Display a dialog box with information about this application.
        '''
        about_dialog = dcheck.gui.about.AboutDialog(self)
        about_dialog.wm_attributes('-topmost', True)
        about_dialog.grab_set()
