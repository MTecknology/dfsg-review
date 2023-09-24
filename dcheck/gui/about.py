'''
About Dialog
'''
# Python
import tkinter
import tkinter.ttk

# DCheck
from dcheck.i18n import t


class AboutDialog(tkinter.Toplevel):
    '''
    TODO: The about dialog needs lots of love.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.resizable(0, 0)

        app_label = tkinter.ttk.Label(
                self, text=t('about_title'),
                font=('Helvetica', 16))
        app_label.grid(row=0, column=0, stick='ew')

        description_label = tkinter.ttk.Label(
                self, text=t('about_description'),
                font=('Helvetica', 12))
        description_label.grid(row=1, column=0, stick='ew')

        # Create a notebook (tabbed interface)
        self.infopanes = tkinter.ttk.Notebook(self)
        self.infopanes.grid(row=2, column=0, sticky='nsew')

        # Info Tab
        self.info = tkinter.ttk.Frame(self.infopanes)
        self.infopanes.add(self.info, text=t('about_info_tab'))

        self.info.blurb = tkinter.ttk.Label(
                self.info, text=t('about_info_blurb'))
        self.info.blurb.grid(row=0, column=0, sticky='nsew')

        # License Tab
        self.license = tkinter.ttk.Frame(self.infopanes)
        self.infopanes.add(self.license, text=t('about_license_tab'))

        self.license.blurb = tkinter.ttk.Label(
                self.license, text=t('about_license_blurb'))
        self.license.blurb.grid(row=0, column=0, sticky='nsew')

        # Handle hotkeys
        self.bind('<Escape>', self.close_window)

    def close_window(self, event=None):
        '''
        Close dialog window.
        '''
        self.destroy()
