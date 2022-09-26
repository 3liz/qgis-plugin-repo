#!/usr/bin/env python3

import argparse

from qgis_plugin_repo.__about__ import __version__
from qgis_plugin_repo.dispatcher import Dispatcher
from qgis_plugin_repo.merger import Merger

__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )

    subparsers = parser.add_subparsers(
        title="commands", description="qgis-plugin-repo-merge command", dest="command"
    )

    read = subparsers.add_parser("read", help="Read plugins available in a repository")
    read.add_argument("xml_file", help="The XML file to parse")

    merge = subparsers.add_parser("merge", help="Merge two repository file")
    merge.add_argument("input_xml", help="The XML to append")
    merge.add_argument("output_xml", help="The XML to edit", nargs='*')

    args = parser.parse_args()

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
        if len(args.output_xml) >= 2:
            print(
                "More than one XML file detected for the output. "
                "All these files will be checked for QGIS versions :")
            print(', '.join([f for f in args.output_xml]))
            merger = Merger(None, args.input_xml)
            merger.xml_input_parser()
            if merger.count() >= 2:
                print("Not possible to merge an XML file having many plugin for inputs when using [VERSION]")
                exit(1)

            dispatcher = Dispatcher(args.input_xml, args.output_xml)
            output_files = dispatcher.xml_files_for_plugin()
            for output_file in output_files:
                print(f"Editing {output_file.name}")
                merger = Merger(output_file, args.input_xml)
                merger.xml_input_parser()
                merger.xml_output_parser()
                merger.merge()
        else:
            print(
                "A single XML file detected for the output."
                "This file is going to be edited whatever it's has a QGIS version."
            )
            merger = Merger(args.output_xml[0], args.input_xml)
            merger.xml_input_parser()
            merger.xml_output_parser()
            merger.merge()

    return exit_val


if __name__ == "__main__":
    exit(main())
