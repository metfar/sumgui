#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  

import math;
import os;
import sys;

import pygame;

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."));
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT);

from sumgui.easy import *;

window("My first SumGUI program", width=800, height=1200, theme="ZX");#width=1072, height=2100,

say("READY.", 20, 20, w=300, h=40, font_size=24, bold=True);
button("HELLO", 20, 60, 180, 70, font_size=40,do=lambda: alert("Hello from SumGUI!"));

start();
