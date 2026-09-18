#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sumgui.easy import fontpicker, label, start, window;

window("FontPicker",width=640,height=240,base_width=640,base_height=240);
label("Font",30,28,100,34);
picker=fontpicker(130,24,470,84,family="monospace",monospace_only=True);
label("Type part of a family name; use Bold / Italic / Small Caps below it.",30,140,570,50);
start();
