#!/usr/bin/env python3

from sumgui.easy import *;

window("My first SumGUI program", width=720, height=720, theme="ZX");

say("READY.", 20, 20, w=300, h=40, font_size=24, bold=True);
button("HELLO", 20, 80, 180, 60, do=lambda: alert("Hello from SumGUI!"));

start();
