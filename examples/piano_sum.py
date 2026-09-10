#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version;
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
import warnings;
warnings.filterwarnings("ignore", category=UserWarning);

import sys;
import time;
from typing import Dict, Tuple, List;
import argparse;

import pygame;

from sumpy import midi_frequency;
from sumgui.audio import tone_sound;
from sumgui.display import set_default_icon;


SAMPLE_RATE = 48000;
BASE_VOLUME = 0.4;
SOURCE_VOLUME = 1.0;

DEFAULT_ATTACK = 0.02;
DEFAULT_DECAY = 0.08;
DEFAULT_SUSTAIN_LEVEL = 0.8;
DEFAULT_RELEASE = 0.20;

KEYS_LEFT = "zsxdcvgbhnjm";
KEYS_RIGHT = "q2w3er5t6y7ui9o0p";

SHIFT_EQUIV = {
    '"': "2",
    "·": "3",
    "%": "5",
    "&": "6",
    "/": "7",
    "(": "9",
    ")": "0",
};


class SoundBank:
    """Lazy MIDI cache using the canonical Sum/BASIC tone generator.""";
    def __init__(self, duration: float = 3.0) -> None:
        self.duration = max(0.05, float(duration));
        self.sounds: Dict[int, pygame.mixer.Sound] = {};

    def get(self, midi: int) -> pygame.mixer.Sound:
        midi = int(midi);
        snd = self.sounds.get(midi);
        if snd is None:
            snd = tone_sound(midi_frequency(midi), duration=self.duration, volume=SOURCE_VOLUME, sample_rate=SAMPLE_RATE);
            self.sounds[midi] = snd;
        return snd;


def build_scale(base_midi: int = 48, n_notes: int = 25) -> List[int]:
    return [base_midi + i for i in range(n_notes)];

def build_keymap() -> Dict[str, int]:
    key_to_index = {};
    all_keys = KEYS_LEFT + KEYS_RIGHT;
    for idx, ch in enumerate(all_keys):
        key_to_index[ch] = idx;
        if ch.isalpha():
            key_to_index[ch.upper()] = idx;
    for shifted, base in SHIFT_EQUIV.items():
        if base in key_to_index:
            key_to_index[shifted] = key_to_index[base];
    return key_to_index;


def normalize_key(event: pygame.event.Event, key_to_index: Dict[str, int]) -> str:
    ch = getattr(event, "unicode", "");
    if ch:
        if ch in key_to_index:
            return ch;
        if ch.isalpha() and ch.lower() in key_to_index:
            return ch.lower();
        if ch in SHIFT_EQUIV:
            base = SHIFT_EQUIV[ch];
            if base in key_to_index:
                return base;
    name = pygame.key.name(event.key);
    if name in key_to_index:
        return name;
    if name.isalpha() and name.lower() in key_to_index:
        return name.lower();
    return "";


class Voice:
    def __init__(self, channel: pygame.mixer.Channel, midi: int, pressed_time: float,
                 adsr: Tuple[float, float, float, float], volume: float) -> None:
        self.channel = channel;
        self.midi = midi;
        self.pressed_time = pressed_time;
        self.released_time = 0.0;
        self.state = "attack";
        self.adsr = adsr;
        self.base_volume = volume;
        self.level_at_release = 0.0;

    def update(self, now: float) -> bool:
        if not self.channel.get_busy():
            return False;
        a, d, s_level, r = self.adsr;
        if self.state == "attack":
            t = now - self.pressed_time;
            if a <= 0.0:
                level = 1.0;
                self.state = "decay";
                self.pressed_time = now;
            else:
                if t >= a:
                    level = 1.0;
                    self.state = "decay";
                    self.pressed_time = now;
                    t = 0.0;
                else:
                    level = t / a;
            self.channel.set_volume(level * self.base_volume);
            return True;
        if self.state == "decay":
            t = now - self.pressed_time;
            if d <= 0.0:
                level = s_level;
                self.state = "sustain";
            else:
                if t >= d:
                    level = s_level;
                    self.state = "sustain";
                else:
                    level = 1.0 + (s_level - 1.0) * (t / d);
            self.channel.set_volume(level * self.base_volume);
            return True;
        if self.state == "sustain":
            self.channel.set_volume(self.base_volume * s_level);
            return True;
        if self.state == "release":
            t = now - self.released_time;
            if r <= 0.0:
                self.channel.stop();
                return False;
            if t >= r:
                self.channel.stop();
                return False;
            frac = 1.0 - (t / r);
            level = max(0.0, self.level_at_release * frac);
            self.channel.set_volume(level * self.base_volume);
            return True;
        return False;

    def note_off(self, now: float) -> None:
        if self.state == "release":
            return;
        current_vol = self.channel.get_volume() / max(self.base_volume, 1e-6);
        self.level_at_release = max(0.0, min(1.0, current_vol));
        self.released_time = now;
        self.state = "release";


NATURAL_STEPS = (0, 2, 4, 5, 7, 9, 11);


def draw_keyboard(screen: pygame.Surface, scale: List[int],
                  base_midi: int, octave_shift: int,
                  pressed_notes: Dict[int, Voice],
                  recording: bool, rec_seconds: float,
                  has_data: bool) -> Dict[int, pygame.Rect]:
    width, height = screen.get_size();
    screen.fill((30, 30, 30));

    hud_height = 26;
    pygame.draw.rect(screen, (45, 45, 45), pygame.Rect(0, 0, width, hud_height));

    naturals = [m for m in scale if (m % 12) in NATURAL_STEPS];
    white_count = len(naturals) if naturals else 1;
    white_width = width // white_count;
    white_height = height - hud_height;
    black_height = int(white_height * 0.6);

    key_rects: Dict[int, pygame.Rect] = {};
    white_pos: Dict[int, int] = {};

    for idx, midi in enumerate(naturals):
        x = idx * white_width;
        rect = pygame.Rect(x, hud_height, white_width - 2, white_height - 2);
        is_pressed = midi in pressed_notes;
        color = (240, 240, 240) if not is_pressed else (210, 230, 255);
        pygame.draw.rect(screen, color, rect);
        pygame.draw.rect(screen, (0, 0, 0), rect, 1);
        key_rects[midi] = rect;
        white_pos[midi] = idx;

    for midi in scale:
        step = midi % 12;
        if step in NATURAL_STEPS:
            continue;
        prev = midi - 1;
        while prev not in white_pos and prev >= naturals[0]:
            prev -= 1;
        base_idx = white_pos.get(prev, 0);
        x = int((base_idx + 0.7) * white_width);
        rect = pygame.Rect(x, hud_height, int(white_width * 0.6), black_height);
        is_pressed = midi in pressed_notes;
        color = (40, 40, 40) if not is_pressed else (70, 70, 100);
        pygame.draw.rect(screen, color, rect);
        pygame.draw.rect(screen, (10, 10, 10), rect, 1);
        key_rects[midi] = rect;

    font = pygame.font.SysFont("monospace", 14);
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    for midi in naturals:
        rect = key_rects[midi];
        name = note_names[midi % 12] + str(midi // 12 - 1);
        label = font.render(name, True, (0, 0, 0));
        screen.blit(label, (rect.x + 4, rect.y + rect.height - 18));

    base_text = f"Base MIDI={base_midi:+d}  Shift={octave_shift:+d}";
    txt = font.render(base_text, True, (220, 220, 220));
    screen.blit(txt, (6, 4));

    rec_x = width - 260;
    if recording:
        pygame.draw.circle(screen, (220, 40, 40), (rec_x, hud_height // 2), 7);
        rec_label = font.render(f"REC {rec_seconds:4.1f}s", True, (255, 200, 200));
    else:
        color = (80, 80, 80) if has_data else (60, 60, 60);
        pygame.draw.circle(screen, color, (rec_x, hud_height // 2), 7);
        if has_data:
            rec_label = font.render(f"READY {rec_seconds:4.1f}s", True, (210, 210, 210));
        else:
            rec_label = font.render("IDLE", True, (180, 180, 180));
    screen.blit(rec_label, (rec_x + 15, 4));

    help_text = "SPACE: REC/STOP   1: PLAY   +/-: octave   ESC: quit";
    help_label = font.render(help_text, True, (180, 180, 180));
    screen.blit(help_label, (width // 2 - help_label.get_width() // 2, 4));

    pygame.display.flip();
    return key_rects;


def main() -> None:
    parser = argparse.ArgumentParser(description="Piano interactivo SumPY/SumGUI con audio de sumCore.");
    parser.add_argument("--base-midi", type=int, default=48, help="Nota MIDI base para la tecla más grave.");
    parser.add_argument("--vol", type=float, default=BASE_VOLUME);
    args = parser.parse_args();

    pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512);
    pygame.init();
    set_default_icon();

    total_keys = len(KEYS_LEFT) + len(KEYS_RIGHT);
    scale = build_scale(args.base_midi, n_notes=total_keys);
    key_to_index = build_keymap();
    sounds = SoundBank(duration=3.0);

    screen = pygame.display.set_mode((900, 220));
    pygame.display.set_caption("Sum Piano - SumPY / SumGUI");
    clock = pygame.time.Clock();

    octave_shift = 0;
    voices_by_midi: Dict[int, Voice] = {};
    pressed_keys: Dict[str, int] = {};
    recording = False;
    record_start = 0.0;
    recorded: List[Dict[str, float]] = [];
    last_take_len = 0.0;
    adsr = (DEFAULT_ATTACK, DEFAULT_DECAY, DEFAULT_SUSTAIN_LEVEL, DEFAULT_RELEASE);

    key_rects: Dict[int, pygame.Rect] = {};

    running = True;
    while running:
        now = time.time();
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False;
                break;
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False;
                    break;
                if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    octave_shift += 1;
                    continue;
                if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    octave_shift -= 1;
                    continue;
                if event.key == pygame.K_SPACE:
                    if not recording:
                        recording = True;
                        record_start = now;
                        recorded = [];
                    else:
                        recording = False;
                        if recorded:
                            last_take_len = recorded[-1]["time"];
                    continue;
                if event.key == pygame.K_1:
                    if recorded:
                        base_t = recorded[0]["time"];
                        for ev in recorded:
                            delay = ev["time"] - base_t;
                            time.sleep(max(0.0, delay));
                            midi = ev["midi"];
                            base_m = midi;
                            snd = sounds.get(midi);
                            if snd is not None:
                                ch = pygame.mixer.find_channel(True);
                                if ch is not None:
                                    ch.set_volume(args.vol);
                                    ch.play(snd, loops=0);
                    continue;
                k = normalize_key(event, key_to_index);
                if not k:
                    continue;
                if k in pressed_keys:
                    continue;
                idx = key_to_index.get(k);
                if idx is None:
                    continue;
                base_midi = scale[idx];
                midi = base_midi + octave_shift * 12;
                snd = sounds.get(midi);
                if snd is None:
                    continue;
                if midi in voices_by_midi:
                    continue;
                ch = pygame.mixer.find_channel(True);
                if ch is None:
                    continue;
                ch.set_volume(0.0);
                ch.play(snd, loops=0);
                v = Voice(ch, midi, now, adsr, args.vol);
                voices_by_midi[midi] = v;
                pressed_keys[k] = midi;
                if recording:
                    recorded.append({"time": now - record_start, "midi": midi});
            if event.type == pygame.KEYUP:
                k = normalize_key(event, key_to_index);
                if not k:
                    continue;
                midi = pressed_keys.pop(k, None);
                if midi is None:
                    continue;
                v = voices_by_midi.get(midi);
                if v is not None:
                    v.note_off(now);
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos;
                clicked_midi = None;
                for midi, rect in key_rects.items():
                    if (midi % 12) not in NATURAL_STEPS and rect.collidepoint(x, y):
                        clicked_midi = midi;
                        break;
                if clicked_midi is None:
                    for midi, rect in key_rects.items():
                        if (midi % 12) in NATURAL_STEPS and rect.collidepoint(x, y):
                            clicked_midi = midi;
                            break;
                if clicked_midi is not None:
                    base_midi = clicked_midi;
                    midi = base_midi + octave_shift * 12;
                    snd = sounds.get(midi);
                    if snd is not None:
                        if midi in voices_by_midi:
                            continue;
                        ch = pygame.mixer.find_channel(True);
                        if ch is not None:
                            ch.set_volume(0.0);
                            ch.play(snd, loops=0);
                            v = Voice(ch, midi, now, adsr, args.vol);
                            voices_by_midi[midi] = v;
                            if recording:
                                recorded.append({"time": now - record_start, "midi": midi});
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for v in list(voices_by_midi.values()):
                    v.note_off(now);

        now = time.time();
        for midi in list(voices_by_midi.keys()):
            v = voices_by_midi[midi];
            alive = v.update(now);
            if not alive:
                del voices_by_midi[midi];

        if recording:
            rec_seconds = now - record_start;
        else:
            rec_seconds = last_take_len;

        key_rects = draw_keyboard(
            screen,
            scale,
            args.base_midi,
            octave_shift,
            voices_by_midi,
            recording,
            rec_seconds,
            bool(recorded) or (not recording and last_take_len > 0.0),
        );
        clock.tick(60);

    pygame.quit();


if __name__ == "__main__":
    main();

