'''
DFSG Checklists for DCheck
'''
# Python
import importlib
import inspect

# DCheck
import dcheck.core.config
import dcheck.core.data

from dcheck.i18n import t

# Keep track of collected checklists
loaded_checklists = {}


def load_checklists():
    '''
    Load configured checklists.
    '''
    global loaded_checklists

    # Attempt to load each configured checklist
    for checklist in dcheck.core.config.get('checklists'):
        module = importlib.import_module('.' + checklist, __name__)
        if not module:
            raise Exception('Unable to load checklist %s.', checklist)

        # Load information from checklist module
        loaded_checklists[checklist] = {
                'title': t(module.title),
                'priority': module.priority,
                'package': {},
                'file': {},
                }
        # Build index of package/file checks provided by module
        for name, check in inspect.getmembers(module, inspect.isclass):
            collection = getattr(check, 'collection', '')
            if collection in ['package', 'file'] and getattr(check, 'title'):
                loaded_checklists[checklist][collection][name] = {
                    'title': t(check.title),
                    'priority': check.priority,
                    }


def collect(target):
    '''
    Return a collection of loaded checks matching target.
    '''
    checks = []  # (i18n_tag, mod.fun),

    # Sort loaded checklists by priority and name
    for checklist, list_info in sorted(
            loaded_checklists.items(),
            key=lambda item: (item[1]['priority'], item[0])):
        # Skip if checklist module does not provide targeted checks
        if not list_info[target]:
            continue

        # Module (checklist) header
        checks.append((list_info['title'], None))

        # Sort checks in target collection by priority and name
        for name, check in sorted(
                list_info[target].items(),
                key=lambda item: (item[1]['priority'], item[0])):
            checks.append((check['title'], f'{checklist}.{name}'))

    return checks


class PackageCheck:
    '''
    Standard template for a package check function.
    '''
    collection = 'package'
    title = None
    status = None
    priority = 500
    allow_auto = False
    package_name = None

    def __init__(self, workspace):
        # TODO: Get package hash from workspace
        # package_name = dcheck.core.inspect.workspace_info(workspace).package
        pass

    def uuid(self):
        '''
        Returns a unique string for a given package name / check id.
        '''
        return f'{self.package_hash}/{self.id}'

    def save_review(self, outcome):
        '''
        Record outcome of review.
        '''
        # TODO
        USERNAME = 'FakeTestUser'

        if outcome == 'approve':
            outcome = True
        elif outcome == 'reject':
            outcome = False
        if not isinstance(outcome, bool):
            raise Exception('Invalid review outcome; bailing!')
        dcheck.core.data.set(f'review/{self.uuid()}/){USERNAME}', outcome)
        self.status = outcome

    def run_check(self):
        '''
        Returns True if check passes, False if it fails, or None on failure.
        '''
        return None

    def auto_accept(self):
        '''
        Run check and automatically mark accepted if check passes.
        '''
        if not self.allow_auto:
            return None
        if self.run_check():
            self.save_review('approve-auto')


class FileCheck(PackageCheck):
    '''
    The same as PackageCheck with the addition of file-focused logic.
    '''
    collection = 'file'
    filename = None
    filehash = None

    def __init__(self, workspace):
        pass

    def change_file(self, filename):
        '''
        Refresh check for a given filename
        '''
        pass
