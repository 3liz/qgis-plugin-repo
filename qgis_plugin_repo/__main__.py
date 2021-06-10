#!/usr/bin/env python3

import argparse

from qgis_plugin_repo.merger import Merger

__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-v", "--version", help="Print the version and exit", action="store_true"
    )

    subparsers = parser.add_subparsers(
        title="commands", description="qgis-plugin-repo-merge command", dest="command"
    )

    read = subparsers.add_parser("read", help="Read plugins available in a repository")
    read.add_argument("xml_file", help="The XML file to parse")

    merge = subparsers.add_parser("merge", help="Merge two repository file")
    merge.add_argument("input_xml", help="The XML to append")
    merge.add_argument("output_xml", help="The XML to edit")

    args = parser.parse_args()

    # print the version and exit
    if args.version:
        import pkg_resources

        print(
            "qgis-plugin-manager version: {}".format(
                pkg_resources.get_distribution("qgis-plugin-manager").version
            )
        )
        parser.exit()

    # if no command is passed, print the help and exit
    if not args.command:
        parser.print_help()
        parser.exit()

    exit_val = 0

    if args.command == "read":
        merger = Merger(None, args.xml_file)
        merger.xml_input_parser()
        print(f"List of plugins in {args.xml_file}")
        for plugin in merger.plugins(merger.input_parser):
            if plugin.experimental:
                print(f"{plugin.name} {plugin.version} experimental")
            else:
                print(f"{plugin.name} {plugin.version}")

    elif args.command == "merge":
        merger = Merger(args.output_xml, args.input_xml)
        merger.xml_input_parser()
        merger.xml_output_parser()
        merger.merge()

    return exit_val


if __name__ == "__main__":
    exit(main())
