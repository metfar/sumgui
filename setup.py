#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
#

from setuptools import find_packages, setup;

setup(
    name="sumgui",
    version="0.2.0a15",
    description="A tiny retro-flavored GUI toolkit for Pygame.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="William Martinez Bas",
    author_email="metfar@gmail.com",
    license="GPL-2.0-or-later",
    packages=find_packages(include=["sumgui*", "udg_painter_reborn*"]),
    include_package_data=True,
    package_data={"udg_painter_reborn": ["*.udg", "*.xpm", "*.ico", "*.png", "*.md", "LICENSE"]},
    python_requires=">=3.8",
    install_requires=["sumui>=0.1.0a12", "pygame>=2.0"],
    extras_require={"matplotlib": ["matplotlib>=3.7"], "seaborn": ["matplotlib>=3.7", "seaborn>=0.13"], "charts": ["matplotlib>=3.7", "seaborn>=0.13"]},
    entry_points={"console_scripts": ["sumgui=sumgui.cli:main", "sumgdialog=sumgui.tools.gdialog:main", "sumudg=udg_painter_reborn.udg_painter_sumgui:main"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: User Interfaces",
    ],
);
