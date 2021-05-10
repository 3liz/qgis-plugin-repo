from collections import namedtuple
from pathlib import Path
from typing import Union
from urllib.parse import urlparse
import requests
import xml.etree.ElementTree as ET


__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


class FileDoesNotExist(Exception):
    pass


Plugin = namedtuple('Plugin', ['name', 'experimental', 'version'])


class Merger:

    @classmethod
    def xml_template(cls):
        return (
            "<?xml version = '1.0' encoding = 'UTF-8'?>\n"
            "<plugins>\n"
            "</plugins>\n"
        )

    def __init__(self, destination: Union[Path, None], input_uri: Union[Path, str, None]):
        self.destination = destination
        self.input_uri = input_uri
        self.input_parser = None
        self.output_tree = None
        self.output_parser = None

    def exists(self) -> bool:
        return self.destination.exists()

    def init(self) -> None:
        print(f"Creating source {self.destination.absolute()}")
        with open(self.destination, 'w', encoding='utf8') as f:
            f.write(self.xml_template())

    def xml_input_parser(self) -> ET.Element:
        if self.input_is_url():
            self.input_parser = ET.fromstring(requests.get(self.input_uri).content)
            return self.input_parser

        else:
            tree = ET.parse(self.input_uri.absolute())
            self.input_parser = tree.getroot()
            return self.input_parser

    def xml_output_parser(self) -> ET.Element:
        if isinstance(self.destination, str):
            self.destination = Path(self.destination)

        if not self.exists():
            self.init()

        self.output_tree = ET.parse(self.destination.absolute())
        self.output_parser = self.output_tree.getroot()
        return self.output_parser

    def input_is_url(self) -> bool:
        if isinstance(self.input_uri, Path):
            return False

        # noinspection PyBroadException
        try:
            urlparse(self.input_uri)
            return True
        except Exception:
            return False

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
    def plugin_element(parser, name: str, experimental: bool) -> ET.Element:
        for plugin in parser:
            if plugin.attrib['name'] != name:
                continue

            for element in plugin:
                element: ET.Element
                if element.tag == "experimental":
                    flag = True if element.text == 'True' else False
                    if flag != experimental:
                        continue

                    return plugin

    @staticmethod
    def diff_plugins(plugins_input, plugins_output):
        new = []
        for plugin in plugins_input:
            if plugin not in plugins_output:
                new.append(plugin)

        return new

    def merge(self):
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
            # Remove old version
            element = self.plugin_element(self.output_parser, plugin.name, plugin.experimental)
            if element:
                print(f"Removing previous {plugin.name} {plugin.experimental} {element.attrib['version']}")
                self.output_parser.remove(element)

            print(f"Adding new version {plugin.name} {plugin.experimental} {plugin.version}")
            self.output_parser.append(
                self.plugin_element(self.input_parser, plugin.name, plugin.experimental))

        self.output_tree.write(self.destination.absolute())
