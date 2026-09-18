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

from types import SimpleNamespace;

from sumui.keyboard import pygame_modifier_state;


def test_altgr_suppresses_synthetic_ctrl_alt_bits():
    fake=SimpleNamespace(KMOD_SHIFT=1,KMOD_CTRL=2,KMOD_ALT=4,KMOD_MODE=8,KMOD_GUI=16);
    state=pygame_modifier_state(2|4|8,fake);
    assert state == {"shift":False,"ctrl":False,"alt":False,"altgr":True,"gui":False};


def test_shift_altgr_keeps_shift_for_level_four_symbols():
    fake=SimpleNamespace(KMOD_SHIFT=1,KMOD_CTRL=2,KMOD_ALT=4,KMOD_MODE=8,KMOD_GUI=16);
    state=pygame_modifier_state(1|2|4|8,fake);
    assert state["shift"] is True;
    assert state["altgr"] is True;
    assert state["ctrl"] is False;
    assert state["alt"] is False;
