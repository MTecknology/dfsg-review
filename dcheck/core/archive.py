'''
Functions for interacting with archives.
'''
# Python
import tarfile
import zipfile


# Extensions which may be extracted
supported_archives = {
        '.tar.gz': 'tar',
        '.tar.xz': 'tar',
        '.zip': 'zip',
        }


def extract(path, dest):
    '''
    Extract an archive after guessing the correct format.
    '''
    # Unpack archive using first-matched suffix
    for sfx, using in supported_archives.items():
        if str(path).endswith(sfx):
            globals()[f'extract_{using}'](path, dest)
            return


def extract_tar(path, dest):
    '''
    Extract a tar archive into a destination directory.
    '''
    with tarfile.open(path) as fh:
        fh.extractall(dest)


def extract_zip(path, dest):
    '''
    Extract a zip archive into a destination directory.
    '''
    with zipfile.open(path) as fh:
        fh.extractall(dest)
