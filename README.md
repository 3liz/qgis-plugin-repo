# QGIS-Plugin-Repo

[![🧪 Tests](https://github.com/3liz/qgis-plugin-repo/actions/workflows/release.yml/badge.svg)](https://github.com/3liz/qgis-plugin-repo/actions/workflows/release.yml)
[![PyPi version badge](https://badgen.net/pypi/v/qgis-plugin-repo)](https://pypi.org/project/qgis-plugin-repo/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/qgis-plugin-repo)](https://pypi.org/project/qgis-plugin-repo/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qgis-plugin-repo)](https://pypi.org/project/qgis-plugin-repo/)

## Presentation

Merge some QGIS plugin repository together

```bash
qgis-plugin-repo merge output_qgis_plugin_ci.xml all_plugins.xml
qgis-plugin-repo merge https://path/to/plugins_to_add.xml all_plugins.xml
```

The file `all_plugins.xml` will be edited, according to the plugin name, plugin 
version and its experimental flag or not. In an XML file, the plugin can have 
two versions : one experimental and the other one not.

Additionally, you can read an XML file :
```bash
qgis-plugin-repo read https://plugins.qgis.org/plugins/plugins.xml?qgis=3.10
```

## GitHub Actions

The main purpose of this tool is to run on CI.

In the plugin repository, after [QGIS-Plugin-CI](https://github.com/opengisch/qgis-plugin-ci) :
```yml
  - name: Repository Dispatch
      uses: peter-evans/repository-dispatch@v1
      with:
        token: ${{ secrets.TOKEN }}
        repository: organisation/repository
        event-type: merge-plugins
        client-payload: '{"name": "NAME_OF_PLUGIN", "version": "${{ env.RELEASE_VERSION }}", "url": "URL_OF_LATEST.xml"}'
```

**Note** that QGIS-Plugin-CI `package` or `release` must be been called with `--create-plugin-repo` because this
tool will use the XML file generated.

In the main repository with a `docs/plugins.xml` to edit :
```yaml
name: 🔀 Plugin repository

on:
  repository_dispatch:
    types: [merge-plugins]

jobs:
  merge:
    runs-on: ubuntu-latest
    steps:
      - run: >
         echo ${{ github.event.client_payload.name }}
         echo ${{ github.event.client_payload.version }}
         echo ${{ github.event.client_payload.url }}

      - name: Get source code
        uses: actions/checkout@v2
        with:
          fetch-depth: 0
          token: ${{ secrets.BOT_HUB_TOKEN }}  # Important to launch CI on a commit from a bot

      - name: Set up Python 3.8
        uses: actions/setup-python@v2.2.2
        with:
          python-version: 3.8

      - name: Install qgis-plugin-repo
        run: pip3 install qgis-plugin-repo

      - name: Merge
        run: qgis-plugin-repo merge ${{ github.event.client_payload.url }} docs/plugins.xml

      - name: Commit changes
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "Publish QGIS Plugin ${{ github.event.client_payload.name }} ${{ github.event.client_payload.version }}"
          commit_user_name: ${{ secrets.BOT_NAME }}
          commit_user_email: ${{ secrets.BOT_MAIL }}
          commit_author: ${{ secrets.BOT_NAME }}
```

### Tests

```bash
cd tests
python -m unittest
```
