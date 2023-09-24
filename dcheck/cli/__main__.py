#!/usr/bin/env python3
'''
Primary entry point for CLI interface.
'''
# Python
import logging

# DCheck
import dcheck.cli.options
import dcheck.core.bootstrap


def main():
    '''
    Process requested dcheck routines.
    '''
    dcheck.core.utils.start()
    options = dcheck.cli.options.parser().parse_args()

    if not options:
        raise Exception('uh oh')
    logging.critical('Not Implemented')


if __name__ == "__main__":
    main()
