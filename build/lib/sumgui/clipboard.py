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

import pygame;

_INTERNAL_CLIPBOARD = "";


def set_clipboard_text(text):
    global _INTERNAL_CLIPBOARD;
    _INTERNAL_CLIPBOARD = str(text);
    try:
        pygame.scrap.init();
        pygame.scrap.put(pygame.SCRAP_TEXT, _INTERNAL_CLIPBOARD.encode("utf-8"));
    except Exception:
        pass;


def get_clipboard_text():
    try:
        pygame.scrap.init();
        data = pygame.scrap.get(pygame.SCRAP_TEXT);
        if data:
            return data.decode("utf-8", errors="ignore").rstrip("\x00");
    except Exception:
        pass;
    return _INTERNAL_CLIPBOARD;
