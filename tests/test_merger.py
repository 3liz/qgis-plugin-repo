import shutil
import unittest

from pathlib import Path

from qgis_plugin_repo.dispatcher import Dispatcher
from qgis_plugin_repo.merger import Merger, Plugin
from qgis_plugin_repo.tools import is_url

__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


class TestMerger(unittest.TestCase):

    def setUp(self) -> None:
        """ Before each test. """
        shutil.copy(Path("fixtures/plugins.xml"), Path("fixtures/plugins_tmp.xml"))
        shutil.copy(Path("fixtures/plugins-3.4.xml"), Path("fixtures/plugins_tmp-3.4.xml"))
        shutil.copy(Path("fixtures/plugins-3.10.xml"), Path("fixtures/plugins_tmp-3.10.xml"))
        shutil.copy(Path("fixtures/plugins-3.16.xml"), Path("fixtures/plugins_tmp-3.16.xml"))
        shutil.copy(Path("fixtures/plugins-3.22.xml"), Path("fixtures/plugins_tmp-3.22.xml"))
        shutil.copy(Path("fixtures/plugins-3.28.xml"), Path("fixtures/plugins_tmp-3.28.xml"))

    def tearDown(self) -> None:
        """ After each test. """
        Path("plugins.xml").unlink(missing_ok=True)
        Path("fixtures/plugins_tmp.xml").unlink(missing_ok=True)
        Path("fixtures/plugins_tmp-3.4.xml").unlink(missing_ok=True)
        Path("fixtures/plugins_tmp-3.10.xml").unlink(missing_ok=True)
        Path("fixtures/plugins_tmp-3.16.xml").unlink(missing_ok=True)
        Path("fixtures/plugins_tmp-3.22.xml").unlink(missing_ok=True)
        Path("fixtures/plugins_tmp-3.28.xml").unlink(missing_ok=True)

    def test_empty_repo(self):
        """ Test to create a new repository. """
        merger = Merger(
            str(Path("fixtures/pgmetadata_stable.xml")),
            str(Path("plugins.xml"))
        )

        self.assertTrue(merger.destination_uri.exists())

        input_plugins = merger.plugins(merger.input_parser)
        self.assertEqual(len(input_plugins), 1)
        self.assertFalse(is_url(merger.input_uri))

        output_plugins = []
        self.assertListEqual(output_plugins, merger.plugins(merger.output_parser))

        self.assertListEqual(input_plugins, merger.diff_plugins(input_plugins, output_plugins))

        merger.merge()

        output_plugins = [Plugin(name='PgMetadata', experimental=False, version='0.6.0')]
        self.assertListEqual(input_plugins, output_plugins)
        self.assertListEqual(input_plugins, merger.plugins(merger.output_parser))

    def test_existing_repo_stable(self):
        """ Test to read an existing repository with stable. """
        merger = Merger(
            str(Path("fixtures/pgmetadata_stable.xml")),
            str(Path("fixtures/plugins_tmp.xml"))
        )

        self.assertTrue(merger.destination_uri.exists())

        input_plugins = merger.plugins(merger.input_parser)
        self.assertEqual(len(input_plugins), 1)
        self.assertFalse(is_url(merger.input_uri))

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
        merger = Merger(
            str(Path("fixtures/pgmetadata_experimental.xml")),
            str(Path("fixtures/plugins_tmp.xml"))
        )

        self.assertTrue(merger.destination_uri.exists())

        input_plugins = merger.plugins(merger.input_parser)
        self.assertEqual(len(input_plugins), 1)
        self.assertFalse(is_url(merger.input_uri))

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
        merger = Merger(str(Path("fixtures/plugins_tmp.xml")))
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
            "https://github.com/3liz/qgis-pgmetadata-plugin/releases/download/0.2.2/plugins.xml",
            str(Path("fixtures/plugins.xml")),
        )
        self.assertTrue(is_url(merger.input_uri))

    def test_count(self):
        """ Test to count plugins in an XML file. """
        merger = Merger(str(Path("fixtures/pgmetadata_stable.xml")))
        self.assertEqual(1, merger.count())

        merger = Merger(str(Path("fixtures/pgmetadata_experimental.xml")))
        self.assertEqual(1, merger.count())

        merger = Merger(str(Path("fixtures/plugins.xml")))
        self.assertEqual(3, merger.count())

    def test_dispatcher_plugin_stable(self):
        """ Test the dispatcher with a stable version. """
        dispatcher = Dispatcher(
            str(Path("fixtures/pgmetadata_stable.xml")),
            [
                str(Path("fixtures/plugins_tmp-3.4.xml")),
                str(Path("fixtures/plugins_tmp-3.10.xml")),
                str(Path("fixtures/plugins_tmp-3.16.xml")),
                str(Path("fixtures/plugins_tmp-3.22.xml")),
                str(Path("fixtures/plugins_tmp-3.28.xml")),
            ]
        )
        qgis_min, qgis_max = dispatcher.versions_for_plugin()
        self.assertEqual("3.10", qgis_min)
        self.assertEqual("3.22", qgis_max)
        self.assertListEqual(
            [
                Path('fixtures/plugins_tmp-3.10.xml'),
                Path('fixtures/plugins_tmp-3.16.xml'),
                Path('fixtures/plugins_tmp-3.22.xml'),
            ],
            dispatcher.xml_files_for_plugin()
        )

    def test_dispatcher_plugin_dev(self):
        """ Test the dispatcher with a dev version. """
        dispatcher = Dispatcher(
            str(Path("fixtures/pgmetadata_experimental.xml")),
            [
                str(Path("fixtures/plugins_tmp-3.4.xml")),
                str(Path("fixtures/plugins_tmp-3.10.xml")),
                str(Path("fixtures/plugins_tmp-3.16.xml")),
                str(Path("fixtures/plugins_tmp-3.22.xml")),
                str(Path("fixtures/plugins_tmp-3.28.xml")),
            ]
        )
        qgis_min, qgis_max = dispatcher.versions_for_plugin()
        self.assertEqual("3.10", qgis_min)
        self.assertEqual("3.99", qgis_max)
        self.assertListEqual(
            [
                Path('fixtures/plugins_tmp-3.10.xml'),
                Path('fixtures/plugins_tmp-3.16.xml'),
                Path('fixtures/plugins_tmp-3.22.xml'),
                Path('fixtures/plugins_tmp-3.28.xml'),
            ],
            dispatcher.xml_files_for_plugin()
        )
