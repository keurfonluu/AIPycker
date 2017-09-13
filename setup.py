# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
import pycker

DISTNAME = "pycker"
DESCRIPTION = "Pycker"
LONG_DESCRIPTION = """Pycker provides user-friendly routines to visualize seismic traces and pick first break arrival times."""
AUTHOR = "Keurfon LUU"
AUTHOR_EMAIL = "keurfon.luu@mines-paristech.fr"
URL = "https://github.com/keurfonluu/pycker"
LICENSE = "MIT License"
REQUIREMENTS = [
    "numpy",
    "matplotlib",
    "obspy",
]
CLASSIFIERS = [
    "Programming Language :: Python",
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
]
 
if __name__ == "__main__":
    setup(
        name = DISTNAME,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        url = URL,
        license = LICENSE,
        install_requires = REQUIREMENTS,
        classifiers = CLASSIFIERS,
        version = pycker.__version__,
        packages = find_packages(),
        include_package_data = True,
    )