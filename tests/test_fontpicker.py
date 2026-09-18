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
import pytest;

pygame=pytest.importorskip("pygame");

from sumgui.fontpicker import FontPicker;


def _picker(max_rows=4):
    pygame.font.init(); font=pygame.font.Font(None,18);
    items=("Zulu","Arial","DejaVu Sans Mono","Liberation Mono","Orator","Courier","Fira Code","IBM Plex Mono","JetBrains Mono","Ubuntu Mono");
    return FontPicker(pygame.Rect(10,10,320,84),font,family="monospace",items=items,max_rows=max_rows);


def test_fontpicker_catalog_is_alphabetical_and_filter_is_substring():
    picker=_picker(); assert picker.items==tuple(sorted(picker.items,key=lambda item:(item.casefold(),item)));
    picker.input.set_value("mono"); picker._update_filter_from_input(); assert picker.filtered_items(); assert all("mono" in item.casefold() for item in picker.filtered_items());


def test_fontpicker_scrollbar_tracks_filtered_result_count():
    picker=_picker(); picker.open_popup(""); bar=picker.scrollbar_rect(); thumb=picker.scrollbar_thumb_rect(); assert thumb.height<bar.height;
    picker.input.set_value("orat"); picker._update_filter_from_input(); bar=picker.scrollbar_rect(); thumb=picker.scrollbar_thumb_rect(); assert thumb.height==bar.height; assert picker.offset==0;


def test_fontpicker_scrollbar_and_keyboard_can_reach_end():
    picker=_picker(); picker.open_popup(""); picker._scroll_to_offset(0); picker._scroll_by(3); assert picker.offset==3;
    picker.drag_scrollbar=True; picker.drag_scroll_y=picker.scrollbar_thumb_rect().centery; picker.drag_scroll_offset=picker.offset; picker._scrollbar_drag_to(picker.scrollbar_rect().bottom); assert picker.offset==len(picker.filtered_items())-picker.max_rows;
    picker.set_focus(True); picker.highlight=0; picker._ensure_highlight_visible(); picker.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_END)); assert picker.highlight==len(picker.filtered_items())-1;
