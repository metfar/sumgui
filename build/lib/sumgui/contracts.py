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

from sumui import BackendCapabilities;


GUI_BACKEND = BackendCapabilities(
    "gui", family="pygame", widgets=True, dialogs=True, charts=True, graphics=True,
    text=True, keyboard=True, pointer=True, touch=True, clipboard=True, audio=True,
    resizable=True, pixel_addressable=True, terminal_cells=False,
    metadata=(("renderer", "pygame"), ("minimum_pygame", "2.0")),
);


def backend_capabilities():
    return GUI_BACKEND;
