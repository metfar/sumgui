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
#

from sumgui.easy import *;


CODE = '''#!/usr/bin/env python3
# Tabs are real tab characters and render as indentation.
def greet(name):
	if name:
		print("Hello", name)
	else:
		print("Hello, SumGUI")

for item in [1, 2, 3]:
	greet("coder " + str(item))
''';


def main():
    window("SumGUI TextArea Code Demo", width=720, height=720, font_size=18, theme="dark");
    say("TextArea: real tabs + vi-like syntax colours", 20, 20, 640, 32, bold=True);
    textarea(20, 70, 660, 560, text=CODE, accepts_tab=True, tab_size=4, syntax="python");
    start();


if __name__ == "__main__":
    main();
