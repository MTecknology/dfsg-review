'''
Package List

Navigate list of packages to be reviewed.
'''
# Python
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk

# DCheck
import dcheck.core.data
import dcheck.core.inspect

from dcheck.i18n import t


class PackageSelection(tkinter.ttk.Frame):
    '''
    Package Selection "Main Frame"
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # Package selection "globals"
        self.filename = tkinter.StringVar(self)
        self.directory = tkinter.StringVar(self)
        self.directory.set(dcheck.core.config.get('pending_dir'))

        # Directory information
        self.cancel = tkinter.ttk.Button(
                self, text=u'\U0001f870', command=self.cancel,
                width=5, state='disabled')
        self.cancel.grid(row=0, column=0)
        self.refresh = tkinter.ttk.Button(
                self, text=u'\U0001f5d8', command=self.update_list,
                width=5)
        self.refresh.grid(row=0, column=1)
        self.browse = tkinter.ttk.Button(
                self, text=u'\U0001f4c1', command=self.change_directory,
                width=5)
        self.browse.grid(row=0, column=2)
        self.dir_display = tkinter.ttk.Entry(
                self, textvariable=self.directory,
                state='readonly')
        self.dir_display.grid(row=0, column=3, sticky='ew')
        self.open = tkinter.ttk.Button(
                self, text=u'\U0001f872', command=self.open_package,
                width=20, state='disabled')
        self.open.grid(row=0, column=4)

        # Enable back button if current selection exists
        if self.winfo_toplevel().target_package.get():
            self.parent.bind('<Escape>', self.cancel)
            self.cancel.config(state='enabled')

        # Package list
        self.packages = tkinter.ttk.Frame(self)
        self.packages.grid(row=1, column=0, columnspan=5, sticky='nsew')
        self.packages.container = None
        self.update_list()

        # Bind hotkeys
        self.parent.bind('<Return>', self.open_package)

        # Fill entire area
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)

    def update_list(self, event=None):
        # Clear list
        if self.packages.container:
            self.packages.container.destroy()
        self.open.config(state='disabled')

        # Get a list of .changes files
        self.changeset = dcheck.core.inspect.list_incoming(
                self.directory.get())

        # Return early with a basic label/message if none found
        if not self.changeset:
            self.packages.container = tkinter.ttk.Label(
                    self.packages, text=t('queue_empty'))
            self.parent.status.config(text=t('status_empty'))
            self.filename.set('')
            self.packages.container.pack(expand=True, fill='both')
            return

        # Insert a fresh package list
        self.packages.container = PackageList(self.packages, self.changeset)
        self.packages.container.pack(expand=True, fill='both')

        # Update status message
        self.parent.status.config(text=t('status_pkgselect'))

    def change_directory(self):
        '''
        Provide a directory selection dialog box.
        '''
        selected_directory = tkinter.filedialog.askdirectory()
        if selected_directory:
            self.directory.set(selected_directory)
            self.update_list()

    def open_package(self, event=None):
        '''
        Validate package selection and trigger reload.
        '''
        changesfile = self.filename.get()
        info = self.changeset.get(changesfile)

        # Extract package if not already done
        if not info['extracted']:
            if not dcheck.core.inspect.open_changes(
                    changes=changesfile,
                    rootdir=self.directory.get()):
                tkinter.messagebox.showwarning(
                        t('error_unpack_title'),
                        t('error_unpack_message'))
                return False

        # Switch to review window
        self.winfo_toplevel().target_package.set(self.filename.get())
        self.winfo_toplevel().set_mainframe('review')

    def cancel(self, event=None):
        '''
        Return to review screen without changing package selection.
        '''
        # TODO: This should avoid redrawing (save a temp copy)
        self.winfo_toplevel().set_mainframe('review')


class PackageList(tkinter.ttk.Frame):
    '''
    Display a list of pending packages with current status.
    '''
    def __init__(self, parent, changeset, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.changeset = changeset

        # Column names (i18n tags)
        columns = (
                'pkg_changes',
                'pkg_name',
                'pkg_version',
                'pkg_age',
                'pkg_status')

        # Package list container
        self.package_list = tkinter.ttk.Treeview(
                self,
                columns=columns,
                height=len(self.changeset),
                displaycolumns=columns[1:],
                show='headings',
                selectmode='browse')

        # Add list to display
        self.package_list.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Assign translated heading to each column
        for column in columns[1:]:
            self.package_list.heading(column, text=t(column))

        # Column display settings
        self.package_list.column('pkg_name', width=150)
        self.package_list.column('pkg_version', width=200)
        self.package_list.column('pkg_age', width=100, stretch='no')
        self.package_list.column('pkg_status', width=150, stretch='no')

        # Add each package to the list
        for changefile, info in self.changeset.items():
            file = changefile.split('_')
            age = 'todo'
            status = t(info.get('status', 'changes_status_unknown'))
            row = (changefile, file[0], file[1], age, status)
            self.package_list.insert('', 'end', text=changefile, values=row)

        # Add a scrollbar
        self.scroll = tkinter.ttk.Scrollbar(
                self, style='arrowless.Vertical.TScrollbar')
        self.scroll.configure(command=self.package_list.yview)
        self.package_list.configure(yscrollcommand=self.scroll.set)

        # Handle selection change
        self.package_list.bind('<<TreeviewSelect>>', self.update_filename)
        self.package_list.bind('<Double-1>', self.open_package)

        # Display elements
        self.scroll.grid(row=0, column=1, sticky='ns')

    def open_package(self, event):
        '''
        Trigger parent.open_package via toplevel.
        '''
        self.winfo_toplevel().mainframe.body.open_package(event)

    def update_filename(self, event):
        '''
        Update PackageSelection.filename from pkg_changes column.
        '''
        selected_item = self.package_list.selection()
        if selected_item:
            # Get pkg_name from selected package
            pkg_changes = self.package_list.item(selected_item, 'values')[0]
            # Update parent.filename via toplevel
            self.winfo_toplevel().mainframe.body.filename.set(pkg_changes)
            # Enable package select (open) button
            self.winfo_toplevel().mainframe.body.open.config(state='enabled')
        else:
            # Disable button if we got here without selecting an item
            self.winfo_toplevel().mainframe.body.open.config(state='disabled')
