import sys
import xml.etree.ElementTree as ET

from collections import namedtuple
from pathlib import Path
from typing import Optional

import requests

from qgis_plugin_repo.tools import is_url

__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

Plugin = namedtuple('Plugin', ['name', 'experimental', 'version'])


class Merger:

    """ To manage a merge between different XML files. """

    @classmethod
    def xml_template(cls) -> str:
        """ To create an empty XML files. """
        return (
            "<?xml version = '1.0' encoding = 'UTF-8'?>\n"
            "<plugins>\n"
            "</plugins>\n"
        )

    def __init__(self, input_uri: str, destination_uri: Optional[str] = None):
        """ Constructor. """
        # Usually a path as a string (filepath or remote URL)
        if is_url(input_uri):
            self.input_uri = input_uri
            try:
                remote = requests.get(self.input_uri)
            except requests.exceptions.MissingSchema:
                print(f"The input {self.input_uri} is neither a valid file nor a valid URL.")
                exit(2)
            self.input_parser = ET.fromstring(remote.content)
        else:
            self.input_uri = Path(input_uri)
            self.input_parser = ET.parse(self.input_uri.absolute()).getroot()

        # Usually a path, it can be None if we want to read only
        self.destination_uri = None
        self.output_parser = None
        self.output_tree = None
        if destination_uri:
            self.destination_uri = Path(destination_uri)

            if not self.destination_uri.exists():
                self.init()

            try:
                self.output_tree = ET.parse(self.destination_uri.absolute())
            except ET.ParseError:
                print(f"Invalid XML file content {self.destination_uri.absolute()}")
                exit(1)
            self.output_parser = self.output_tree.getroot()

    def init(self) -> None:
        """ Init the XML files with an empty catalog. """
        print(f"Creating source {self.destination_uri.absolute()} because the file did not exist.")
        with open(self.destination_uri, 'w', encoding='utf8') as f:
            f.write(self.xml_template())

    @staticmethod
    def plugins(parser) -> list:
        """ Return the plugins in the XML file. """
        plugins_list = []
        for plugin in parser:
            experimental = False
            for element in plugin:
                element: ET.Element
                if element.tag == "experimental":
                    experimental = True if element.text == 'True' else False
                    break

            plugins_list.append(Plugin(
                plugin.attrib['name'],
                experimental,
                plugin.attrib['version']))

        return plugins_list

    @staticmethod
    def plugin_element(parser: ET.Element, name: str, experimental: bool) -> [ET.Element, int]:
        """ Return the XML element for a given plugin name and its experimental flag. """
        for i, plugin in enumerate(parser):
            if plugin.attrib['name'] != name:
                continue

            for element in plugin:
                element: ET.Element
                if element.tag == "experimental":
                    flag = True if element.text == 'True' else False
                    if flag != experimental:
                        continue

                    return plugin, i

        return None, None

    @staticmethod
    def diff_plugins(plugins_input, plugins_output) -> list:
        """ List of plugins which are in the input and not in the output. """
        new = []
        for plugin in plugins_input:
            if plugin not in plugins_output:
                new.append(plugin)

        return new

    def count(self) -> int:
        """ Count the number of plugins in the XML. """
        return len(self.plugins(self.input_parser))

    def merge(self):
        """ Make the merge. """
        output_plugins = self.plugins(self.output_parser)
        input_plugins = self.plugins(self.input_parser)

        diff = self.diff_plugins(input_plugins, output_plugins)

        print(f"Updating source {self.destination_uri.absolute()}")
        print(f"with {self.input_uri}")

        if len(diff) == 0:
            print("No update is necessary")

        for plugin in diff:
            element, index = self.plugin_element(self.output_parser, plugin.name, plugin.experimental)
            if element:
                print(f"Updating previous {plugin.name} {plugin.experimental} {element.attrib['version']}")
                element.__setstate__(
                    self.plugin_element(
                        self.input_parser, plugin.name, plugin.experimental)[0].__getstate__())
            else:
                print(f"Adding new version {plugin.name} {plugin.experimental} {plugin.version}")
                self.output_parser.append(
                    self.plugin_element(self.input_parser, plugin.name, plugin.experimental)[0])

        if sys.version_info >= (3, 9):
            ET.indent(self.output_tree, space="\t", level=0)
        self.output_tree.write(self.destination_uri.absolute(), encoding="utf-8")

        with open(self.destination_uri, "a", encoding='utf8') as f:
            f.write("\n")
