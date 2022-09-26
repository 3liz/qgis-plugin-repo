import sys
import xml.etree.ElementTree as ET

from collections import namedtuple
from pathlib import Path
from typing import Union
from urllib.parse import urlparse

import requests

from qgis_plugin_repo.tools import is_url

__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


class FileDoesNotExist(Exception):
    pass


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

    def __init__(self, destination: Union[Path, None], input_uri: Union[Path, str, None]):
        """ Constructor. """
        # Usually a path, it can be None if we want to read only
        self.destination = destination
        # Usually a path as a string, or a URL
        self.input_uri = input_uri

        # Internal objects
        self.input_parser = None
        self.output_tree = None
        self.output_parser = None

    def exists(self) -> bool:
        """ If the destination files exists. """
        return self.destination.exists()

    def init(self) -> None:
        """ Init the XML files with an empty catalog. """
        print(f"Creating source {self.destination.absolute()}")
        with open(self.destination, 'w', encoding='utf8') as f:
            f.write(self.xml_template())

    def xml_input_parser(self) -> ET.Element:
        """ Returns the XML parser for the input file. """
        if is_url(self.input_uri):
            self.input_parser = ET.fromstring(requests.get(self.input_uri).content)
        else:
            if not isinstance(self.input_uri, Path):
                self.input_uri = Path(self.input_uri)
            tree = ET.parse(self.input_uri.absolute())
            self.input_parser = tree.getroot()

        return self.input_parser

    def xml_output_parser(self) -> ET.Element:
        """ Returns the XML parser for the output file. """
        if isinstance(self.destination, str):
            self.destination = Path(self.destination)

        if not self.exists():
            self.init()

        try:
            self.output_tree = ET.parse(self.destination.absolute())
        except ET.ParseError:
            self.init()
            self.output_tree = ET.parse(self.destination.absolute())

        self.output_parser = self.output_tree.getroot()
        return self.output_parser

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
        if not self.exists():
            raise FileDoesNotExist

        output_plugins = self.plugins(self.output_parser)
        input_plugins = self.plugins(self.input_parser)

        diff = self.diff_plugins(input_plugins, output_plugins)

        print(f"Updating source {self.destination.absolute()}")
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
        self.output_tree.write(self.destination.absolute(), encoding="utf-8")

        with open(self.destination, "a", encoding='utf8') as f:
            f.write("\n")
