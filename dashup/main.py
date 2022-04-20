#!/usr/bin/env python3

import argparse

import dashup.sn_platform as sn_platform
import dashup.mn_platform as mn_platform
import dashup.seednode as seednode
import dashup.masternode as masternode
import dashup.core as core

from dashup.helper.purge import purge 


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="method")
    core_parser = subparsers.add_parser('core')
    seednode_parser = subparsers.add_parser('seednode')
    masternode_parser = subparsers.add_parser('masternode')
    platform_parser = subparsers.add_parser('platform')
    platform_parser.add_argument('type', type=str, choices=['seednode', 'masternode'])
    core_parser = subparsers.add_parser('purge')
    args = parser.parse_args()

    help_str = r'''dash-setup

    Usage: dash-setup <command>

    Commands:
        core       - Installs and configures dash-core
        seednode   - Fund node and generate network keys
        masternode - Configure masternode with sentinel
        platform   - Configuration for seed-/masternode
    '''

    if args.method == 'core':
        core.setup()
    elif args.method == 'seednode':
        seednode.setup()
    elif args.method == 'masternode':
        masternode.setup()
    elif args.method == 'platform':
        if args.type == 'seednode':
            sn_platform.setup()
        elif args.type == 'masternode':
            mn_platform.setup()
    elif args.method == 'purge':
        purge()
    else:
        print(help_str)


if __name__ == '__main__':
    main()

