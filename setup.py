import sys

from pathlib import Path

from setuptools import setup

from qgis_plugin_repo import __about__

python_min_version = (3, 7)

if sys.version_info < python_min_version:
    sys.exit(
        "qgis-plugin-repo requires at least Python version {vmaj}.{vmin}.\n"
        "You are currently running this installation with\n\n{curver}".format(
            vmaj=python_min_version[0], vmin=python_min_version[1], curver=sys.version
        )
    )

# This string might be updated on CI on runtime with a proper semantic version name with X.Y.Z
VERSION = "__VERSION__"

if "." not in VERSION:
    # If VERSION is still not a proper semantic versioning with X.Y.Z
    # let's hardcode 0.0.0
    VERSION = "0.0.0"

read_me = Path(__file__).parent.joinpath("README.md").read_text()

setup(
    name="qgis-plugin-repo",
    author=__about__.__author__,
    author_email=__about__.__email__,
    description=__about__.__summary__,
    packages=["qgis_plugin_repo"],
    long_description=read_me,
    long_description_content_type="text/markdown",
    url=__about__.__uri__,
    entry_points={"console_scripts": ["qgis-plugin-repo = qgis_plugin_repo.__main__:main"]},
    version=VERSION,
    project_urls={
        "Docs": __about__.__uri__,
        "Bug Reports": "{}issues/".format(__about__.__uri__),
        "Source": __about__.__uri__,
    },
    download_url="https://github.com/3liz/qgis-plugin-repo/archive/{}.tar.gz".format(
        VERSION
    ),
    keywords=["QGIS"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    install_requires=["requests"],
    python_requires=">={vmaj}.{vmin}".format(
        vmaj=python_min_version[0], vmin=python_min_version[1]
    ),
)
