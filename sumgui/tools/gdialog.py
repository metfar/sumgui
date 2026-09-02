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
from ..dialogs import _dialog_events, input_box, message_box, question_box;
from ..display import fit_window_size;
from ..widgets import draw_clipped_text;
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
    mode.add_argument("--demo", action="store_true", help="open an interactive launcher demonstrating graphical dialog modes");
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



def _demo_menu(screen, clock, theme):
    choices = [
        ("info", "Information"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("yesno", "Question"),
        ("entry", "Entry"),
        ("validated", "Validated entry"),
        ("exit", "Exit demo"),
    ];
    width, height = screen.get_size();
    title_font = pygame.font.SysFont("monospace", max(20, min(30, height // 18)), bold=True);
    font = pygame.font.SysFont("monospace", max(15, min(22, height // 26)), bold=True);
    margin = max(16, min(width, height) // 24);
    gap = max(8, margin // 2);
    columns = 2 if width >= 560 else 1;
    rows = (len(choices) + columns - 1) // columns;
    header_h = title_font.get_height() * 2 + margin;
    usable_h = max(120, height - header_h - margin * 2);
    button_h = max(38, min(64, (usable_h - gap * max(0, rows - 1)) // max(1, rows)));
    button_w = (width - margin * 2 - gap * (columns - 1)) // columns;
    rects = [];
    for index, item in enumerate(choices):
        row = index // columns;
        column = index % columns;
        x = margin + column * (button_w + gap);
        y = header_h + row * (button_h + gap);
        rects.append((item, pygame.Rect(x, y, button_w, button_h)));
    pressed = None;
    while True:
        for event in _dialog_events(screen):
            if event.type == pygame.QUIT:
                return "exit";
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "exit";
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pressed = None;
                for item, rect in rects:
                    if rect.collidepoint(event.pos):
                        pressed = item[0];
                        break;
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                selected = pressed;
                pressed = None;
                if selected is not None:
                    for item, rect in rects:
                        if item[0] == selected and rect.collidepoint(event.pos):
                            return selected;
        screen.fill(theme.bg);
        draw_clipped_text(screen, title_font, "sumgdialog --demo", theme.text, pygame.Rect(margin, margin, width - margin * 2, title_font.get_height() + 4), align="center");
        draw_clipped_text(screen, font, "Choose a modality", theme.text, pygame.Rect(margin, margin + title_font.get_height() + 6, width - margin * 2, font.get_height() + 4), align="center");
        for item, rect in rects:
            color = getattr(theme, "accent", theme.button) if pressed == item[0] else theme.button;
            pygame.draw.rect(screen, color, rect, border_radius=8);
            pygame.draw.rect(screen, theme.line, rect, 2, border_radius=8);
            draw_clipped_text(screen, font, item[1], theme.button_text, rect, align="center", valign="middle");
        pygame.display.flip();
        clock.tick(60);


def _run_demo(screen, clock, theme):
    while True:
        choice = _demo_menu(screen, clock, theme);
        if choice == "exit":
            return 0;
        if choice == "info":
            message_box(screen, clock, "Information", "Operation completed successfully.", theme=theme);
        elif choice == "warning":
            message_box(screen, clock, "Warning", "This is a graphical warning example.", theme=theme);
        elif choice == "error":
            message_box(screen, clock, "Error", "This is a graphical error example.", theme=theme);
        elif choice == "yesno":
            answer = question_box(screen, clock, "Question", "Continue with the demonstration?", theme=theme);
            message_box(screen, clock, "Result", "Answer: {}".format("Yes" if answer else "No"), theme=theme);
        elif choice == "entry":
            value = input_box(screen, clock, "Entry", "Description:", default_text="This is John's house", theme=theme);
            if value is not None:
                message_box(screen, clock, "Entry result", str(value), theme=theme);
        elif choice == "validated":
            value = input_box(
                screen, clock, "Validated entry", "Press S or N:", default_text="N", theme=theme,
                max_length=1, confirm=True, valid_values=("S", "N"), validation_error="Only S or N is accepted",
            );
            if value is not None:
                message_box(screen, clock, "Entry result", str(value), theme=theme);


def main(argv=None):
    args = build_parser().parse_args(argv);
    pygame.init();
    width, height = fit_window_size(max(320, args.width), max(240, args.height));
    screen = pygame.display.set_mode((width, height));
    pygame.display.set_caption(args.title);
    clock = pygame.time.Clock();
    theme = make_theme(args.theme);
    try:
        if args.demo:
            return _run_demo(screen, clock, theme);
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
