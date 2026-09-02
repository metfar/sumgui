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

import pygame;


def desktop_size():
    """Return the physical desktop/display size without creating a window.""";
    if not pygame.display.get_init():
        pygame.display.init();
    getter = getattr(pygame.display, "get_desktop_sizes", None);
    if getter is not None:
        try:
            sizes = getter();
            if sizes:
                width, height = sizes[0];
                if int(width) > 0 and int(height) > 0:
                    return int(width), int(height);
        except (pygame.error, TypeError, ValueError):
            pass;
    try:
        info = pygame.display.Info();
        width = int(getattr(info, "current_w", 0) or 0);
        height = int(getattr(info, "current_h", 0) or 0);
        if width > 0 and height > 0:
            return width, height;
    except pygame.error:
        pass;
    return 0, 0;


def fit_window_size(width, height, desktop=None, margin_x=32, margin_y=64, minimum=(240, 180)):
    """Scale a requested window down so it fits the current physical display.

    The requested aspect ratio is preserved.  Windows are never enlarged by
    this helper.  ``desktop`` is injectable so sizing policy can be tested
    without a live Pygame display.
    """;
    requested_w = max(1, int(width));
    requested_h = max(1, int(height));
    if desktop is None:
        desktop = desktop_size();
    desktop_w = max(0, int(desktop[0] if desktop else 0));
    desktop_h = max(0, int(desktop[1] if desktop else 0));
    if desktop_w <= 0 or desktop_h <= 0:
        return requested_w, requested_h;

    max_w = max(1, desktop_w - max(0, int(margin_x)));
    max_h = max(1, desktop_h - max(0, int(margin_y)));
    scale = min(1.0, max_w / float(requested_w), max_h / float(requested_h));
    fitted_w = max(1, int(round(requested_w * scale)));
    fitted_h = max(1, int(round(requested_h * scale)));

    min_w = min(max_w, max(1, int(minimum[0])));
    min_h = min(max_h, max(1, int(minimum[1])));
    fitted_w = max(min_w, min(max_w, fitted_w));
    fitted_h = max(min_h, min(max_h, fitted_h));
    return fitted_w, fitted_h;


def display_size(width, height, fit=True, margin_x=32, margin_y=64):
    if not fit:
        return max(1, int(width)), max(1, int(height));
    return fit_window_size(width, height, margin_x=margin_x, margin_y=margin_y);
