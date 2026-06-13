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
#


import os;
import sys;

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."));
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT);

from sumgui.easy import *;


CODE = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def saludar(nombre):
	print("Hola, " + nombre);

for nombre in ["José", "François", "Jürgen", "Miyuki"]:
	saludar(nombre);
""";


def main():
    window("SumGUI Code TextArea", width=720, height=720, font_size=18);
    label("Python TextArea: real tabs + simple vi-like colours", 20, 20, 660, 36);
    textarea(20, 70, 660, 560, text=CODE, accepts_tab=True, tab_size=4, syntax="python");
    start();


if __name__ == "__main__":
    main();
