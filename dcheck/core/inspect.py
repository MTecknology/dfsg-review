'''
DCheck Package Inspection
The primary "entry point" for investigating package data.
'''
# Python
import gnupg
import hashlib
import logging
import os
import pathlib
import shutil
import yaml

# DCheck
import dcheck.core.config
import dcheck.core.data
import dcheck.core.archive


# Supported hashing algorithms, based on checksum length
supported_algorithms = {
        32: hashlib.md5,
        40: hashlib.sha1,
        64: hashlib.sha256,
        128: hashlib.sha512,
        }


def list_incoming(path=None) -> dict:
    '''
    Return information about changes files in a given directory.
    '''
    if not path:
        path = dcheck.core.config.get('pending_dir')

    if not os.path.isdir(path):
        logging.warning('Review directory (pending_dir) was not found.')
        return {}

    # Collect all correctly-named files ending in _source.changes.
    incoming = {}
    for file in os.listdir(path):
        f = file.split('_')
        if len(f) != 3:
            continue
        if f[2] != 'source.changes':
            continue
        incoming[file] = changes_info(file)

    return incoming


def changes_info(changes, full=False) -> dict:
    '''
    Return a basic set of information from a changes file.
    '''
    workspace_dir = pathlib.Path(dcheck.core.config.get('workspace_dir'))
    workspace_name = changes[:changes.rindex('_')]
    info = {}

    # Check if source package was already extracted.
    info['extracted'] = os.path.exists(workspace_dir / workspace_name)

    # Determine appropriate status message
    info['status'] = 'changes_status_unknown'

    # Return low-impact data if nothing further is required.
    if not full:
        return info

    # Collect cached information
    # info['summary'] = dcheck.core.data.get(f'pkg/{changes}/info')  # uuid
    # info['scancode'] = dcheck.core.data.get(f'pkg/{changes}/scan')  # pkg

    return info


def open_changes(changes, rootdir=None) -> bool:
    '''
    Unpack contents specified in a given changes file.
    '''
    if not rootdir:
        rootdir = dcheck.core.config.get('pending_dir')
    incoming = pathlib.Path(rootdir)
    workspace_dir = pathlib.Path(dcheck.core.config.get('workspace_dir'))
    workspace = workspace_dir / changes[:changes.rindex('_')]
    logging.info('Unpacking %s into %s', incoming / changes, workspace)

    supported_archives = dcheck.core.archive.supported_archives

    # Create destination directory structure and copy changes file.
    # NOTE: 0o775 is ideal for shared review, but should not be managed here.
    copy_to = workspace / 'source'
    copy_to.mkdir(parents=True, exist_ok=True)
    shutil.copy(incoming / changes, copy_to)

    # Verify signature and read signed checksum data
    if not (v := verify_signature(copy_to / changes)):
        logging.critical('Signature verification failed: %s', changes)
        wipe_workspace(workspace)
        return False
    changes_data = yaml.safe_load(v.data)

    # Verify and copy any files mentioned in .changes
    xtra = changes_data['Checksums-Sha256'].split()
    # TODO: PY3.12: for cksum, size, path in batched(xtra, 3):
    for cksum, size, path in [xtra[x:x+3] for x in range(0, len(xtra), 3)]:
        fspath = incoming / path
        if not verify_checksum(fspath, cksum):
            logging.warning('Checksum verification failed: %s', fspath)
            wipe_workspace(workspace)
            return False
        logging.debug('Copying file: %s', path)
        if any(path.endswith(x) for x in supported_archives):
            logging.debug('Extracting file: %s', fspath)
            dcheck.core.archive.extract(fspath, workspace)
        shutil.copy(fspath, copy_to)
    return True


def verify_checksum(path, checksum) -> bool:
    '''
    Verify a given path produces an expected checksum.
    '''
    # Guess hashing algorithm based on checksum length
    if not (algorithm := supported_algorithms.get(len(checksum), None)):
        logging.warning('Invalid checksum size for %s', algorithm)
        return False

    # Build checksum of file using selected algorithm
    hasher = algorithm()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(4096), b''):
            hasher.update(chunk)

    # Check for the expected value
    return hasher.hexdigest() == checksum


def verify_signature(path) -> gnupg.Verify:
    '''
    Verify the PGP signature within a file at a given path.
    '''
    gpg = gnupg.GPG()
    with open(path, 'rb') as fh:
        return gpg.verify_file(fh, extra_args=['-o', '-'])


def wipe_workspace(package) -> bool:
    '''
    Wipe the contents of workspace_dir/package.
    '''
    wipe_path = pathlib.Path(dcheck.core.config.get('workspace_dir')) / package
    logging.info('Removing path: %s', wipe_path)
    try:
        shutil.rmtree(wipe_path)
    except OSError:
        logging.critical('Unable to remove %s', wipe_path)
        return False
    return True
