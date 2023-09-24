'''
Options Parser
'''
# Python
import argparse

# DCheck
import dcheck.checks

from dcheck.i18n import t


def parser():
    parser = argparse.ArgumentParser(
            usage='dcheck [-h] <options> --check.1 [--check.2 --check.3]',
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=30))

    # Workspace Settings (dcheck.gui.DEFAULT_WORKSPACE)
    parser.add_argument(
        '--filename',
        dest='target_filename',
        action='store',
        metavar='<changes>',
        help=t('cli_opt_filename'))
    parser.add_argument(
        '--directory',
        dest='target_directory',
        action='store',
        metavar='<path>',
        help=t('cli_opt_directory'))

    # Available Checklists
    for collection in ['package', 'file']:
        group = parser.add_argument_group(
                collection,
                t(f'cli_opt_{collection}'))
        for check in dcheck.checks.collect(collection):
            if not check[1]:
                continue
            group.add_argument(
                f'--{check[1]}',
                dest=check[1],
                action='store_true',
                help=t(check[0]))

    return parser
