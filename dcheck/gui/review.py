'''
Package Review
'''
# Python
import logging
import tkinter
import tkinter.font
import tkinter.ttk
import pathlib  # TODO: This should move to the inspect module

# DCheck
import dcheck.core.config
# import dcheck.core.data
import dcheck.checks
import dcheck.images

from dcheck.i18n import t


class PackageReview(tkinter.ttk.Frame):
    '''
    Package Review "Main Frame"
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # Return an error label if to target_package was set
        changes = self.winfo_toplevel().target_package.get()
        if not changes:
            logging.critical('PackageReview loaded without target_package.')
            self.error = tkinter.Label(self, text='ERR: target_package')
            self.error.pack(fill='both', expand=True)
            return
        workspace_dir = pathlib.Path(dcheck.core.config.get('workspace_dir'))
        package = changes[:changes.rindex('_')]

        # Package review "globals"
        self.winfo_toplevel().review_basepath = tkinter.StringVar(self)
        self.winfo_toplevel().review_basepath.set(workspace_dir / package)

        # Workspace container
        self.workspace = tkinter.PanedWindow(
                self, orient='horizontal', sashwidth=4, sashrelief='raised')
        self.workspace.pack(fill='both', expand=True)

        # Create workspace columns
        for column, panels in dcheck.core.config.get('layout').items():
            if not panels:
                if column == 'center':
                    raise Exception('Center column requires a panel.')
                continue

            # Create a column for panes
            ws_column = tkinter.PanedWindow(
                    self, orient='vertical', sashwidth=3, sashrelief='raised')
            self.workspace.add(ws_column, stretch='always', minsize=250)

            # Add configured panels to column
            for panel in panels:
                ws_panel = getattr(dcheck.gui.review, panel)(ws_column)
                # minsize=110 is arbitrary; sync with WorkspacePanel.toggle()
                ws_column.add(ws_panel, stretch='always', minsize=110)

        # Simple starter message
        self.parent.status.config(text=t('status_checkselect'))


class WorkspacePanel(tkinter.ttk.Frame):
    '''
    Provide a reusable and collapsible panel for the workspace.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.oldsize = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Heading titlebar
        self.rowconfigure(0, minsize=25)
        self.heading = tkinter.ttk.Label(
                self, text='', relief='raised', cursor='hand2')
        self.heading.grid(row=0, column=0, sticky='ew')
        self.heading.bind('<Button-1>', self.toggle)

        # Heading expansion
        self.expanded = tkinter.ttk.Label(
                self, text='[ - ]', relief='raised', cursor='hand2')
        self.expanded.grid(row=0, column=1, sticky='ew')
        self.expanded.bind('<Button-1>', self.toggle)

        # Subframe
        self.body = tkinter.ttk.Frame(self)
        self.body.grid(row=1, column=0, sticky='nsew')
        self.body.columnconfigure(0, weight=1)
        self.body.rowconfigure(0, weight=1)

        # Scrollbar
        self.yscroll = tkinter.ttk.Scrollbar(
                self, style='arrowless.Vertical.Scrollbar')
        self.yscroll.grid(row=1, column=1, sticky='ns')

    def set_title(self, text):
        '''
        Set/change text in the panel heading.
        '''
        self.heading.config(text=text)

    def set_yscroll(self, focus):
        '''
        Set focus of the scrollbar to a given tkinter object.
        '''
        self.yscroll.configure(command=focus.yview)
        focus.configure(yscrollcommand=self.yscroll.set)

    def toggle(self, event):
        '''
        Collapse the panel if expanded, or else expand.
        '''
        # Expand
        if self.oldsize:
            # Update heading and add to display
            self.expanded.config(text='[ - ]')
            self.yscroll.grid()
            self.body.grid()
            # Reclaim previous space (PackageReview.ws_column:minsize)
            self.parent.paneconfigure(self, minsize=110, height=self.oldsize)
            self.oldsize = None
        # Collapse
        else:
            # Update heading and hide from display
            self.expanded.config(text='[+]')
            self.yscroll.grid_remove()
            self.body.grid_remove()
            # Reduce pane size
            self.oldsize = self.winfo_reqheight()
            self.parent.paneconfigure(self, minsize=24, height=15)


class HorizontalScroll(tkinter.ttk.Frame):
    '''
    Container that provides a horizontal scrollbar.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def fill(self, obj):
        '''
        Build out frame using a provided container object.
        '''
        # Inner container
        self.box = obj
        self.box.grid(row=0, column=0, sticky='nsew')

        # Horizontal scrollbar
        self.xscroll = tkinter.ttk.Scrollbar(
                self, orient='horizontal',
                style='arrowless.Horizontal.Scrollbar')
        self.xscroll.grid(row=1, column=0, sticky='ew')

        # Recheck width when object changes size
        self.box.bind('<Expose>', self.check_width)
        self.box.bind('<Configure>', self.check_width)
        # Recheck width when movement happens
        self.box.bind('<Button-4>', self.check_width)
        self.box.bind('<Button-5>', self.check_width)

        # Scrollbar focus
        self.set_xscroll(obj)

    def set_xscroll(self, focus):
        '''
        Set focus of the scrollbar to a given tkinter object.
        '''
        self.xscroll.configure(command=focus.xview)
        focus.configure(xscrollcommand=self.xscroll.set)
        self.check_width()

    def check_width(self, event=None):
        '''
        Hide/show scrollbar depending on frame width.
        '''
        if self.box.xview() == (0.0, 1.0):
            self.xscroll.grid_remove()
        else:
            self.xscroll.grid()


class ChecklistView(tkinter.ttk.PanedWindow):
    '''
    Build a list of checklist tree from a provided checklist.
    '''
    def __init__(self, parent, checklist, *args, **kwargs):
        super().__init__(parent, orient='vertical', *args, **kwargs)

        # Status icons
        self.green = dcheck.images.tk_photo('bullet_green')
        self.red = dcheck.images.tk_photo('bullet_red')
        self.yellow = dcheck.images.tk_photo('bullet_yellow')
        self.none = dcheck.images.tk_photo('bullet_none')

        # Checklist tree with horizontal scrollbar
        self.hbox = HorizontalScroll(self)
        self.tree = tkinter.ttk.Treeview(self.hbox, columns=None, show='tree')
        self.hbox.fill(self.tree)
        self.add(self.hbox, weight=1)

        # Populate treeview with collected package checks
        maxwidth = 0
        font = tkinter.font.Font()
        for check_i18n, check_fun in checklist:
            check_title = t(check_i18n)
            # TODO: font.measure() is accurate, but very slow
            maxwidth = max(maxwidth, font.measure(check_title) + 15)
            if not check_fun:
                self.tree.insert(
                        '', 'end',
                        iid=check_i18n, text=check_title,
                        image=self.none, open=True)
                last_parent = check_i18n
            else:
                self.tree.insert(
                        last_parent, 'end',
                        iid=check_fun, text=check_title,
                        image=self.none)
        self.tree.column("#0", minwidth=maxwidth)

        # Check Workspace
        self.ws = tkinter.ttk.Notebook(self, height=140)
        self.add(self.ws)

        # Place for "memo" for check (from i18n)
        memo = tkinter.ttk.Label(self.ws, text='')
        self.ws.add(memo, text=t('tab_pkgcheck_memo'))
        # TODO: Place for doing stuff ...
        example = ExampleFrame(self.ws)
        self.ws.add(example, text=t('tab_pkgcheck_action'))


class ExampleFrame(tkinter.ttk.Frame):
    '''
    TODO: REMOVE THIS
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.label1 = tkinter.Label(self, text='Label 1:')
        self.label1.pack()
        self.run_button = tkinter.Button(
                self, text='Run', command=self.run_action)
        self.run_button.pack()
        self.verify_button = tkinter.Button(
                self, text='Verify', command=self.verify_action)
        self.verify_button.pack()
        self.status_label = tkinter.Label(
                self, text='Status: Ready')
        self.status_label.pack()

    def run_action(self):
        self.status_label.config(text='Running...')

    def verify_action(self):
        self.status_label.config(text='Verifying...')


class AllChecklists(WorkspacePanel):
    '''
    Show a collection of checklists
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set panel heading
        self.set_title(t('pane_all_checks'))

        # Checklist notebook
        self.body.lists = tkinter.ttk.Notebook(self.body)
        self.body.lists.grid(row=0, column=0, sticky='nsew')

        # Add package checklist
        package_checks = dcheck.checks.collect('package')
        self.package_list = ChecklistView(self.body.lists, package_checks)
        self.body.lists.add(self.package_list, text=t('tab_allchecks_pkg'))

        # Add file checklist
        file_checks = dcheck.checks.collect('file')
        self.file_list = ChecklistView(self.body.lists, file_checks)
        self.body.lists.add(self.file_list, text=t('tab_allchecks_file'))

        # Scrollbar focus
        self.body.lists.bind(
                '<<NotebookTabChanged>>',
                lambda event: self.update_scrollbar())

    def update_scrollbar(self):
        '''
        Refocus scrollbar when tab selection changes.
        '''
        tabnum = self.body.lists.index(self.body.lists.select())
        if tabnum == 0:
            self.set_yscroll(self.package_list.tree)
        elif tabnum == 1:
            self.set_yscroll(self.file_list.tree)


class PackageChecklist(WorkspacePanel):
    '''
    Show checklist for a .changes file (package).
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set panel heading
        self.set_title(t('pane_pkg_checks'))

        # Add package checklist
        package_checks = dcheck.checks.collect('package')
        self.body.checklist = ChecklistView(self.body, package_checks)
        self.body.checklist.grid(row=0, column=0, sticky='nsew')

        # Scrollbar focus
        self.set_yscroll(self.body.checklist.tree)


class FileChecklist(WorkspacePanel):
    '''
    Show checklist for a .changes file (package).
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set panel heading
        self.set_title(t('pane_file_checks'))

        # Add package checklist
        file_checks = dcheck.checks.collect('file')
        self.body.checklist = ChecklistView(self.body, file_checks)
        self.body.checklist.grid(row=0, column=0, sticky='nsew')

        # Scrollbar focus
        self.set_yscroll(self.body.checklist.tree)


class FileList(WorkspacePanel):
    '''
    Navigate files within a package.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        review_basepath = self.winfo_toplevel().review_basepath.get()

        # List icons
        self.folder = dcheck.images.tk_photo('folder_none')
        self.file = dcheck.images.tk_photo('bullet_red')

        # Set panel heading
        self.set_title(t('pane_file_nav'))

        # Add directory tree
        self.body.dirtree = tkinter.ttk.Treeview(
                self.body, columns=None, show='tree')
        self.add_directory(pathlib.Path(review_basepath))
        self.body.dirtree.grid(row=0, column=0, sticky='nsew')

        # Scrollbar focus
        self.set_yscroll(self.body.dirtree)

    def add_directory(self, rootdir, parent_iid=''):
        for fullpath in sorted(rootdir.iterdir()):
            if fullpath.is_dir():
                subdir = self.body.dirtree.insert(
                        parent_iid, 'end',
                        iid=fullpath, text=fullpath.name,
                        image=self.folder)
                self.add_directory(fullpath, subdir)
            if fullpath.is_file():
                # TODO: Should iid of file be scancode-toolkit checksum
                self.body.dirtree.insert(
                        parent_iid, 'end',
                        iid=fullpath, text=fullpath.name,
                        image=self.file)


class FileContents(WorkspacePanel):
    '''
    Display contents of a file.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set panel heading
        self.set_title(t('pane_file_view'))

        # Add file display with horizontal scrollbar
        self.hbox = HorizontalScroll(self.body)
        self.body.content = tkinter.Text(
                self.hbox, state='disabled', wrap='none')
        self.hbox.fill(self.body.content)
        self.hbox.grid(row=0, column=0, sticky='nsew')

        # Scrollbar focus
        self.set_yscroll(self.body.content)
        # TODO: Get this from bind+globalString
        self.open_file('/var/cache/dcheck/extracted/tdc_2.0-1/tdc-2.0/tdc.c')

    def open_file(self, path):
        '''
        Open file at a given path.
        '''
        self.body.content.config(state='normal')
        self.body.content.delete('1.0', 'end')

        # TODO: This should use the inspect module
        with open(path, 'r') as fh:
            self.body.content.insert('insert', fh.read())
        self.body.content.config(state='disabled')


class FileInfo(WorkspacePanel):
    '''
    File Information
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set panel heading
        self.set_title(t('pane_file_info'))

        # Plop stuff into the display
        # TODO


class PersistentFiles(WorkspacePanel):
    '''
    Provide a place for persistent d/file display.
    '''
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        review_basepath = self.winfo_toplevel().review_basepath.get()
        self.pageroot = pathlib.Path(review_basepath) / 'debian'
        self.pages = {}

        # Set panel heading
        self.set_title(t('pane_persistent_files'))

        # File notebook
        self.body.pages = tkinter.ttk.Notebook(self.body)
        self.body.pages.grid(row=0, column=0, sticky='nsew')

        # TODO: Get tabs from a selection
        self.new_tab('copyright')
        self.new_tab('control')

        # Scrollbar focus
        self.body.pages.bind(
                '<<NotebookTabChanged>>',
                lambda event: self.update_scrollbar())

    def new_tab(self, page):
        '''
        Add a new tab from a given page (d/filename).
        '''
        newtab = tkinter.Text(self.body.pages, wrap='word')

        # TODO: This should use the inspect module
        with open(self.pageroot / page, 'r') as fh:
            newtab.insert('insert', fh.read())
        newtab.config(state='disabled')

        self.pages[page] = newtab
        self.body.pages.add(newtab, text=page)

    def update_scrollbar(self):
        '''
        Refocus scrollbar when tab selection changes.
        '''
        tabname = self.body.pages.tab(self.body.pages.select(), 'text')
        self.set_yscroll(self.pages[tabname])
