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
from dataclasses import dataclass;


@dataclass(frozen=True)
class FontSelection:
    family: str="monospace";
    bold: bool=False;
    italic: bool=False;
    small_caps: bool=False;
    small_caps_scale: float=0.65;


def sort_font_names(names,current="",aliases=("monospace",)):
    values=[]; seen=set();
    for name in [str(current or "").strip(),*tuple(aliases or ()),*tuple(names or ())]:
        name=str(name or "").strip(); key=name.casefold();
        if not name or key in seen: continue;
        seen.add(key); values.append(name);
    values.sort(key=lambda item:(item.casefold(),item));
    return tuple(values);


def filter_font_names(names,query=""):
    query=str(query or "").strip().casefold();
    values=tuple(names or ());
    if not query: return values;
    return tuple(name for name in values if query in str(name).casefold());


def is_monospace_font(font_api,name,size=16,tolerance=1):
    try:
        font=font_api.SysFont(str(name),int(size));
        widths=[font.size(char)[0] for char in "iMW0@#_"];
    except Exception:
        return False;
    return bool(widths) and max(widths)-min(widths)<=int(tolerance);


def system_font_names(font_api,current="",monospace_only=False):
    try: names=list(font_api.get_fonts());
    except Exception: names=[];
    values=sort_font_names(names,current=current);
    if not monospace_only: return values;
    return tuple(name for name in values if name.casefold()=="monospace" or is_monospace_font(font_api,name));
