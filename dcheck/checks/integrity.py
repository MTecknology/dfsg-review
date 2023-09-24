'''
Checks which verify the integrity of data being reviewed.
'''
# DCheck
from dcheck.checks import PackageCheck, FileCheck

# Module information
title = 'check_integrity_title'
priority = 0


class ChangesChecksums(PackageCheck):
    '''
    Verify that checksums presented in .changes files are valid/correct.
    '''
    title = 'check_integrity_cksum'
    priority = 10

    def run_check(self):
        pass


class ReadableCopyright(FileCheck):
    '''
    Verify d/copyright can be read using DEP-5 format.
    '''
    title = 'check_integrity_dep5'

    def run_check(self):
        pass
