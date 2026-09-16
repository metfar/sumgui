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

"""SumGUI adapter for the common sumCore audio service.""";

import io;

import pygame;

from sumcore.audio_api import audio_engine, beep, midi_frequency, play, set_audio_engine, sound, stop_audio, tone_pcm_bytes, tone_wav_bytes, wait_audio;


def tone_sound(frequency, duration=3.0, volume=1.0, sample_rate=48000):
    """Create a Pygame Sound with the exact Sum tone generator.""";
    payload = tone_wav_bytes(float(frequency), float(duration), float(volume), int(sample_rate));
    return pygame.mixer.Sound(file=io.BytesIO(payload));


def midi_sound(midi_note, duration=3.0, volume=1.0, sample_rate=48000):
    return tone_sound(midi_frequency(midi_note), duration=duration, volume=volume, sample_rate=sample_rate);

__all__ = ["audio_engine", "beep", "midi_frequency", "midi_sound", "play", "set_audio_engine", "sound", "stop_audio", "tone_pcm_bytes", "tone_sound", "tone_wav_bytes", "wait_audio"];
