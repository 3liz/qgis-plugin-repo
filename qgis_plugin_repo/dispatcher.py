__copyright__ = 'Copyright 2022, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'

import re
import xml.etree.ElementTree as ET

from pathlib import Path
from typing import List, Tuple, Union

import requests

from qgis_plugin_repo.tools import is_url


class Dispatcher:

    def __init__(self, input_uri: Union[Path, str], outputs_uri: List[Union[Path, str]]):
        """ Constructor. """
        self.input_uri = input_uri
        if is_url(input_uri):
            self.input_parser = ET.fromstring(requests.get(self.input_uri).content)
        else:
            if isinstance(self.input_uri, str):
                self.input_uri = Path(self.input_uri)
            self.input_parser = ET.parse(self.input_uri.absolute()).getroot()

        self.outputs_uri = [Path(f) for f in outputs_uri]

    def xml_files_for_plugin(self) -> List[Path]:
        """ Return the list of XML to edit for the given plugin. """
        qgis_min, qgis_max = self.versions_for_plugin()
        qgis_min = qgis_min.split('.')
        qgis_max = qgis_max.split('.')
        if len(qgis_min) >= 3 or len(qgis_max) >= 3:
            print("Only major and minor versions are supported for now.")

        qgis_range = range(int(qgis_min[1]), int(qgis_max[1]) + 1)
        qgis_range = [v for v in qgis_range if v % 2 == 0]
        qgis_range = [fr'{qgis_min[0]}\.{v}' for v in qgis_range]
        qgis_range = '|'.join(qgis_range)
        tmp = []
        for output_uri in self.outputs_uri:
            if re.search(r"{}".format(qgis_range), output_uri.name):
                tmp.append(output_uri)
        return tmp

    def versions_for_plugin(self) -> Tuple[str, str]:
        """ Return the minimum and maximum QGIS version if found in the XML.

        Default values are 3.0 and 3.99.
        """
        qgis_minimum = '3.0'
        qgis_maximum = '3.99'
        for plugin in self.input_parser:
            for element in plugin:
                element: ET.Element
                if element.tag == "qgis_minimum_version":
                    qgis_minimum = element.text
                elif element.tag == "qgis_maximum_version":
                    qgis_maximum = element.text

        return qgis_minimum, qgis_maximum
