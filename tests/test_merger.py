import shutil
import unittest
from pathlib import Path

from qgis_plugin_repo.merger import Merger, Plugin

__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


class TestMerger(unittest.TestCase):

    def setUp(self) -> None:

        shutil.copy(Path("fixtures/plugins.xml"), Path("fixtures/plugins_tmp.xml"))

    def tearDown(self) -> None:
        Path("plugins.xml").unlink(missing_ok=True)
        Path("fixtures/plugins_tmp.xml").unlink(missing_ok=True)

    def test_empty_repo(self):
        """ Test to create a new repository. """
        merger = Merger(Path("plugins.xml"), Path("fixtures/pgmetadata_stable.xml"))

        self.assertFalse(merger.exists())
        merger.init()
        self.assertTrue(merger.exists())

        merger.xml_input_parser()
        input_plugins = merger.plugins(merger.input_parser)
        self.assertEqual(len(input_plugins), 1)
        self.assertFalse(merger.input_is_url())

        merger.xml_output_parser()
        output_plugins = []
        self.assertListEqual(output_plugins, merger.plugins(merger.output_parser))

        self.assertListEqual(input_plugins, merger.diff_plugins(input_plugins, output_plugins))

        merger.merge()

        output_plugins = [Plugin(name='PgMetadata', experimental=False, version='0.6.0')]
        self.assertListEqual(input_plugins, output_plugins)
        self.assertListEqual(input_plugins, merger.plugins(merger.output_parser))

    def test_existing_repo_stable(self):
        """ Test to read an existing repository with stable. """
        merger = Merger(Path("fixtures/plugins_tmp.xml"), Path("fixtures/pgmetadata_stable.xml"))

        self.assertTrue(merger.exists())

        merger.xml_input_parser()
        input_plugins = merger.plugins(merger.input_parser)
        self.assertEqual(len(input_plugins), 1)
        self.assertFalse(merger.input_is_url())

        merger.xml_output_parser()
        output_plugins = [
            Plugin(name='PgMetadata', experimental=True, version='0.4.0'),
            Plugin(name='PgMetadata', experimental=False, version='0.5.0'),
            Plugin(name='atlasprint', experimental=False, version='v3.2.2'),
        ]
        self.assertEqual(len(output_plugins), len(merger.plugins(merger.output_parser)))
        for plugin in merger.plugins(merger.output_parser):
            self.assertIn(plugin, output_plugins)

        self.assertListEqual(input_plugins, merger.diff_plugins(input_plugins, output_plugins))

        merger.merge()

        output_plugins = [
            Plugin(name='PgMetadata', experimental=True, version='0.4.0'),
            Plugin(name='PgMetadata', experimental=False, version='0.6.0'),
            Plugin(name='atlasprint', experimental=False, version='v3.2.2')
        ]
        self.assertEqual(len(output_plugins), len(merger.plugins(merger.output_parser)))
        for plugin in merger.plugins(merger.output_parser):
            self.assertIn(plugin, output_plugins)

    def test_existing_repo_experimental(self):
        """ Test to read an existing repository with experimental. """
        merger = Merger(Path("fixtures/plugins_tmp.xml"), Path("fixtures/pgmetadata_experimental.xml"))

        self.assertTrue(merger.exists())

        merger.xml_input_parser()
        input_plugins = merger.plugins(merger.input_parser)
        self.assertEqual(len(input_plugins), 1)
        self.assertFalse(merger.input_is_url())

        merger.xml_output_parser()
        output_plugins = [
            Plugin(name='PgMetadata', experimental=True, version='0.4.0'),
            Plugin(name='PgMetadata', experimental=False, version='0.5.0'),
            Plugin(name='atlasprint', experimental=False, version='v3.2.2'),
        ]
        self.assertEqual(len(output_plugins), len(merger.plugins(merger.output_parser)))
        for plugin in merger.plugins(merger.output_parser):
            self.assertIn(plugin, output_plugins)

        self.assertListEqual(input_plugins, merger.diff_plugins(input_plugins, output_plugins))

        merger.merge()

        output_plugins = [
            Plugin(name='PgMetadata', experimental=True, version='0.7.0'),
            Plugin(name='PgMetadata', experimental=False, version='0.5.0'),
            Plugin(name='atlasprint', experimental=False, version='v3.2.2')
        ]
        self.assertEqual(len(output_plugins), len(merger.plugins(merger.output_parser)))
        for plugin in merger.plugins(merger.output_parser):
            self.assertIn(plugin, output_plugins)

    def test_read(self):
        """ Test to read only. """
        merger = Merger(None, Path("fixtures/plugins_tmp.xml"))
        merger.xml_input_parser()
        output_plugins = [
            Plugin(name='PgMetadata', experimental=True, version='0.4.0'),
            Plugin(name='PgMetadata', experimental=False, version='0.5.0'),
            Plugin(name='atlasprint', experimental=False, version='v3.2.2'),
        ]
        self.assertEqual(len(output_plugins), len(merger.plugins(merger.input_parser)))
        for plugin in merger.plugins(merger.input_parser):
            self.assertIn(plugin, output_plugins)

    def test_url(self):
        """ Test input as URL. """
        merger = Merger(
            Path("fixtures/plugins.xml"),
            "https://github.com/3liz/qgis-pgmetadata-plugin/releases/download/0.2.2/plugins.xml"
        )
        self.assertTrue(merger.input_is_url())
