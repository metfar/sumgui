#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sumgui.easy import fontpicker, label, start, window;

window("FontPicker",width=640,height=390,base_width=640,base_height=390);
label("Font",30,28,100,34);
picker=fontpicker(130,24,470,220,family="monospace",small_caps_scale=0.65,monospace_only=True,show_scale=True,preview=True);
label("Type part of a family name; preview and Small Caps scale update live.",30,330,570,50);
start();
