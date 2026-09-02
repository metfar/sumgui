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

import argparse;
import sys;

import pygame;

from .. import __version__;
from ..dialogs import input_box, message_box, question_box;
from ..theme import make_theme;


def _values(text):
    if text is None:
        return ();
    return tuple(item.strip() for item in str(text).replace("|", ",").split(",") if item.strip());


def build_parser():
    parser = argparse.ArgumentParser(prog="sumgdialog", description="Graphical counterpart to sumdialog using SumGUI/Pygame.");
    mode = parser.add_mutually_exclusive_group(required=True);
    mode.add_argument("--info", metavar="TEXT");
    mode.add_argument("--warning", metavar="TEXT");
    mode.add_argument("--error", metavar="TEXT");
    mode.add_argument("--yesno", metavar="TEXT");
    mode.add_argument("--entry", metavar="TEXT");
    parser.add_argument("--title", default="sumgdialog");
    parser.add_argument("--default", default="");
    parser.add_argument("--max-length", type=int, default=-1);
    parser.add_argument("--valid-values", default="");
    parser.add_argument("--validation-error", default="Invalid value");
    parser.add_argument("--case-sensitive", action="store_true");
    parser.add_argument("--confirm", dest="confirm", action="store_true", default=True);
    parser.add_argument("--no-confirm", dest="confirm", action="store_false");
    parser.add_argument("--theme", default="DOS");
    parser.add_argument("--width", type=int, default=720);
    parser.add_argument("--height", type=int, default=480);
    parser.add_argument("--version", action="version", version="sumgdialog {}".format(__version__));
    return parser;


def main(argv=None):
    args = build_parser().parse_args(argv);
    pygame.init();
    screen = pygame.display.set_mode((max(320, args.width), max(240, args.height)));
    pygame.display.set_caption(args.title);
    clock = pygame.time.Clock();
    theme = make_theme(args.theme);
    try:
        if args.entry is not None:
            value = input_box(
                screen, clock, args.title, args.entry, default_text=args.default, theme=theme,
                max_length=args.max_length, confirm=args.confirm, valid_values=_values(args.valid_values),
                validation_error=args.validation_error, case_sensitive=args.case_sensitive,
            );
            if value is None:
                return 1;
            sys.stdout.write(str(value) + "\n");
            return 0;
        if args.yesno is not None:
            return 0 if question_box(screen, clock, args.title, args.yesno, theme=theme) else 1;
        message = args.info if args.info is not None else args.warning if args.warning is not None else args.error;
        return 0 if message_box(screen, clock, args.title, message or "", theme=theme) else 1;
    finally:
        pygame.quit();


if __name__ == "__main__":
    raise SystemExit(main());
