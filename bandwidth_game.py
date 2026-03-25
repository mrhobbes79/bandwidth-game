#!/usr/bin/env python3
"""BAND//WIDTH — A WISP Telecom Platformer Runner"""
import pygame
import numpy as np
import math
import random
import json
import os
import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple

# ============================================================
# SECTION 2: CONSTANTS, COLORS, PHYSICS
# ============================================================
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILE = 32

# Physics constants
GRAVITY = 0.5
MAX_FALL = 15
JUMP_FORCE = -13
DOUBLE_JUMP_FORCE = -10
RUN_SPEED = 7
SPRINT_SPEED = 11
AIR_CONTROL = 0.7
WALL_SLIDE_SPEED = 3.0
COYOTE_TIME = 8
JUMP_BUFFER = 6
WET_FRICTION = 0.4

# Colors
SKY_DAY = (135, 206, 235)
SKY_NIGHT = (15, 15, 40)
CONCRETE = (180, 175, 170)
FIBER_CABLE = (255, 165, 0)
SIGNAL_GOOD = (0, 255, 120)
SIGNAL_BAD = (255, 50, 50)
DIALOG_BG = (20, 20, 35)
DIALOG_BORDER = (0, 220, 180)
UI_PRIMARY = (0, 150, 220)
UI_ACCENT = (180, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Scoring
INSTALL_EXCELLENT = 500
INSTALL_GOOD = 200
CABLE_SWING = 25
PERFECT_LANDING = 100
NO_DAMAGE = 300
BEAT_COMPETITOR = 400
JAMMER_DESTROYED = 250
TIME_BONUS_PER_SEC = 50
SPEED_RUN = 1000


class GameState(Enum):
    BOOT = auto()
    LANG_SELECT = auto()
    MAIN_MENU = auto()
    CHAR_SELECT = auto()
    CITY_MAP = auto()
    PLAYING = auto()
    PAUSED = auto()
    INSTALLING = auto()
    CUTSCENE = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()
    CREDITS = auto()
    BOSS_FIGHT = auto()
    HELP = auto()
    OPTIONS = auto()


class AnimState(Enum):
    IDLE = auto()
    RUN = auto()
    JUMP = auto()
    FALL = auto()
    CLIMB = auto()
    INSTALL = auto()
    DEATH = auto()
    CABLE_SWING = auto()
    WALL_SLIDE = auto()
    SPECIAL = auto()


class SurfaceType(Enum):
    CONCRETE = auto()
    METAL = auto()
    WET = auto()
    GRATE = auto()
    CABLE = auto()
    ANTENNA = auto()


class BubbleType(Enum):
    SPEECH = auto()
    THOUGHT = auto()
    SHOUT = auto()
    RADIO = auto()


# ============================================================
# SECTION 3: LANGUAGE SYSTEM
# ============================================================
STRINGS = {
    "EN": {
        "title": "BAND//WIDTH",
        "start": "NEW GAME",
        "continue_game": "CONTINUE",
        "select_char": "SELECT CHARACTER",
        "options": "OPTIONS",
        "quit": "QUIT",
        "paused": "PAUSED",
        "resume": "RESUME",
        "game_over": "GAME OVER",
        "level_complete": "LEVEL COMPLETE!",
        "excellent": "EXCELLENT!",
        "good": "GOOD",
        "weak": "WEAK SIGNAL",
        "lives": "LIVES",
        "score": "SCORE",
        "time_label": "TIME",
        "install_prompt": "Press E to install antenna",
        "skip": "Press ENTER to skip",
        "connection_lost": "CONNECTION LOST",
        "press_start": "Press ENTER to start",
        "language_select": "SELECT LANGUAGE",
        "controls": "CONTROLS",
        "back": "BACK",
        "city_cdmx": "Mexico City",
        "city_monterrey": "Monterrey",
        "city_guadalajara": "Guadalajara",
        "city_tijuana": "Tijuana",
        "city_dallas": "Dallas",
        "city_chicago": "Chicago",
        "city_rio": "Rio de Janeiro",
        "city_sao_paulo": "São Paulo",
        "city_bogota": "Bogotá",
        "city_buenos_aires": "Buenos Aires",
        "city_miami": "Miami",
        "city_final": "Final Showdown",
        "signal_strength": "SIGNAL STRENGTH",
        "installing": "INSTALLING...",
        "press_space_lock": "Press SPACE to lock signal",
        "retry": "RETRY",
        "main_menu": "MAIN MENU",
        "unlocked": "CHARACTER UNLOCKED!",
        "locked": "LOCKED",
        "speed": "SPEED",
        "jump_stat": "JUMP",
        "grip": "GRIP",
        "install_skill": "INSTALL",
        "special": "SPECIAL",
        "loading": "LOADING...",
        "checkpoint": "CHECKPOINT!",
        "bonus": "BONUS!",
        "perfect": "PERFECT!",
        "combo": "COMBO!",
        "rain_warning": "Rain incoming!",
        "wind_warning": "Strong winds!",
        "help_title": "CONTROLS & INSTRUCTIONS",
        "help_move": "WASD / Arrow Keys - Move",
        "help_jump": "SPACE - Jump / Double Jump",
        "help_sprint": "SHIFT - Sprint",
        "help_interact": "E - Interact / Install Antenna",
        "help_special": "Q - Special Ability",
        "help_pause": "ESC - Pause",
        "help_fullscreen": "F - Toggle Fullscreen",
        "help_skip": "TAB - Skip Dialog / Cutscene",
        "help_info": "H - This Help Screen",
        "help_howto_title": "HOW TO PLAY",
        "help_howto_1": "Run across rooftops, climb poles, and swing on fiber cables.",
        "help_howto_2": "Install antennas at marked locations — time your signal!",
        "help_howto_3": "Avoid competitors, RF jammers, and bad weather.",
        "help_howto_4": "Each character has a unique special ability (Q key).",
        "help_howto_5": "Reach the end of each level to advance to the next city.",
        "help_press_close": "Press H or ESC to close",
        "options_title": "OPTIONS",
        "opt_music_vol": "Music Volume",
        "opt_sfx_vol": "SFX Volume",
        "opt_language": "Language",
        "opt_fullscreen": "Fullscreen",
        "opt_screenshake": "Screen Shake",
        "opt_on": "ON",
        "opt_off": "OFF",
        "opt_back": "Back to Menu",
        "opt_credits": "Credits",
    },
    "ES": {
        "title": "BAND//WIDTH",
        "start": "NUEVO JUEGO",
        "continue_game": "CONTINUAR",
        "select_char": "ELEGIR PERSONAJE",
        "options": "OPCIONES",
        "quit": "SALIR",
        "paused": "PAUSA",
        "resume": "REANUDAR",
        "game_over": "FIN DEL JUEGO",
        "level_complete": "NIVEL COMPLETO!",
        "excellent": "EXCELENTE!",
        "good": "BIEN",
        "weak": "SENAL DEBIL",
        "lives": "VIDAS",
        "score": "PUNTAJE",
        "time_label": "TIEMPO",
        "install_prompt": "Presiona E para instalar antena",
        "skip": "Presiona ENTER para saltar",
        "connection_lost": "CONEXION PERDIDA",
        "press_start": "Presiona ENTER para iniciar",
        "language_select": "SELECCIONAR IDIOMA",
        "controls": "CONTROLES",
        "back": "VOLVER",
        "city_cdmx": "Ciudad de Mexico",
        "city_monterrey": "Monterrey",
        "city_guadalajara": "Guadalajara",
        "city_tijuana": "Tijuana",
        "city_dallas": "Dallas",
        "city_chicago": "Chicago",
        "city_rio": "Rio de Janeiro",
        "city_sao_paulo": "São Paulo",
        "city_bogota": "Bogotá",
        "city_buenos_aires": "Buenos Aires",
        "city_miami": "Miami",
        "city_final": "Enfrentamiento Final",
        "signal_strength": "FUERZA DE SENAL",
        "installing": "INSTALANDO...",
        "press_space_lock": "Presiona ESPACIO para fijar senal",
        "retry": "REINTENTAR",
        "main_menu": "MENU PRINCIPAL",
        "unlocked": "PERSONAJE DESBLOQUEADO!",
        "locked": "BLOQUEADO",
        "speed": "VELOCIDAD",
        "jump_stat": "SALTO",
        "grip": "AGARRE",
        "install_skill": "INSTALACION",
        "special": "ESPECIAL",
        "loading": "CARGANDO...",
        "checkpoint": "PUNTO DE CONTROL!",
        "bonus": "BONUS!",
        "perfect": "PERFECTO!",
        "combo": "COMBO!",
        "rain_warning": "Lluvia en camino!",
        "wind_warning": "Vientos fuertes!",
        "help_title": "CONTROLES E INSTRUCCIONES",
        "help_move": "WASD / Flechas - Mover",
        "help_jump": "ESPACIO - Saltar / Doble Salto",
        "help_sprint": "SHIFT - Correr",
        "help_interact": "E - Interactuar / Instalar Antena",
        "help_special": "Q - Habilidad Especial",
        "help_pause": "ESC - Pausa",
        "help_fullscreen": "F - Pantalla Completa",
        "help_skip": "TAB - Saltar Dialogo / Escena",
        "help_info": "H - Esta Pantalla de Ayuda",
        "help_howto_title": "COMO JUGAR",
        "help_howto_1": "Corre por techos, sube postes y columpia en cables de fibra.",
        "help_howto_2": "Instala antenas en los puntos marcados — sincroniza la senal!",
        "help_howto_3": "Evita competidores, jammers RF y mal clima.",
        "help_howto_4": "Cada personaje tiene una habilidad especial unica (tecla Q).",
        "help_howto_5": "Llega al final de cada nivel para avanzar a la siguiente ciudad.",
        "help_press_close": "Presiona H o ESC para cerrar",
        "options_title": "OPCIONES",
        "opt_music_vol": "Volumen Musica",
        "opt_sfx_vol": "Volumen Efectos",
        "opt_language": "Idioma",
        "opt_fullscreen": "Pantalla Completa",
        "opt_screenshake": "Vibracion de Pantalla",
        "opt_on": "SI",
        "opt_off": "NO",
        "opt_back": "Volver al Menu",
        "opt_credits": "Creditos",
    },
    "PT": {
        "title": "BAND//WIDTH",
        "start": "NOVO JOGO",
        "continue_game": "CONTINUAR",
        "select_char": "ESCOLHER PERSONAGEM",
        "options": "OPCOES",
        "quit": "SAIR",
        "paused": "PAUSADO",
        "resume": "RETOMAR",
        "game_over": "FIM DE JOGO",
        "level_complete": "NIVEL COMPLETO!",
        "excellent": "EXCELENTE!",
        "good": "BOM",
        "weak": "SINAL FRACO",
        "lives": "VIDAS",
        "score": "PONTUACAO",
        "time_label": "TEMPO",
        "install_prompt": "Pressione E para instalar antena",
        "skip": "Pressione ENTER para pular",
        "connection_lost": "CONEXAO PERDIDA",
        "press_start": "Pressione ENTER para iniciar",
        "language_select": "SELECIONAR IDIOMA",
        "controls": "CONTROLES",
        "back": "VOLTAR",
        "city_cdmx": "Cidade do Mexico",
        "city_monterrey": "Monterrey",
        "city_guadalajara": "Guadalajara",
        "city_tijuana": "Tijuana",
        "city_dallas": "Dallas",
        "city_chicago": "Chicago",
        "city_rio": "Rio de Janeiro",
        "city_sao_paulo": "São Paulo",
        "city_bogota": "Bogotá",
        "city_buenos_aires": "Buenos Aires",
        "city_miami": "Miami",
        "city_final": "Confronto Final",
        "signal_strength": "FORCA DO SINAL",
        "installing": "INSTALANDO...",
        "press_space_lock": "Pressione ESPACO para travar sinal",
        "retry": "TENTAR NOVAMENTE",
        "main_menu": "MENU PRINCIPAL",
        "unlocked": "PERSONAGEM DESBLOQUEADO!",
        "locked": "BLOQUEADO",
        "speed": "VELOCIDADE",
        "jump_stat": "PULO",
        "grip": "ADERENCIA",
        "install_skill": "INSTALACAO",
        "special": "ESPECIAL",
        "loading": "CARREGANDO...",
        "checkpoint": "CHECKPOINT!",
        "bonus": "BONUS!",
        "perfect": "PERFEITO!",
        "combo": "COMBO!",
        "rain_warning": "Chuva chegando!",
        "wind_warning": "Ventos fortes!",
        "help_title": "CONTROLES E INSTRUCOES",
        "help_move": "WASD / Setas - Mover",
        "help_jump": "ESPACO - Pular / Pulo Duplo",
        "help_sprint": "SHIFT - Correr",
        "help_interact": "E - Interagir / Instalar Antena",
        "help_special": "Q - Habilidade Especial",
        "help_pause": "ESC - Pausar",
        "help_fullscreen": "F - Tela Cheia",
        "help_skip": "TAB - Pular Dialogo / Cena",
        "help_info": "H - Esta Tela de Ajuda",
        "help_howto_title": "COMO JOGAR",
        "help_howto_1": "Corra pelos telhados, suba postes e balance nos cabos de fibra.",
        "help_howto_2": "Instale antenas nos pontos marcados — sincronize o sinal!",
        "help_howto_3": "Evite concorrentes, jammers RF e mau tempo.",
        "help_howto_4": "Cada personagem tem uma habilidade especial unica (tecla Q).",
        "help_howto_5": "Chegue ao final de cada nivel para avancar para a proxima cidade.",
        "help_press_close": "Pressione H ou ESC para fechar",
        "options_title": "OPCOES",
        "opt_music_vol": "Volume Musica",
        "opt_sfx_vol": "Volume Efeitos",
        "opt_language": "Idioma",
        "opt_fullscreen": "Tela Cheia",
        "opt_screenshake": "Vibracao de Tela",
        "opt_on": "SIM",
        "opt_off": "NAO",
        "opt_back": "Voltar ao Menu",
        "opt_credits": "Creditos",
    },
}

current_language = "ES"


def t(key):
    """Get translated string for current language."""
    return STRINGS.get(current_language, STRINGS["ES"]).get(key, key)


# ============================================================
# SECTION 4: AUDIO ENGINE
# ============================================================
class AudioEngine:
    """Procedural audio generation using numpy and pygame."""

    def __init__(self):
        self.sample_rate = 22050
        self.sounds = {}
        self.initialized = False
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self._current_music_channel = None
        try:
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=1024)
            pygame.mixer.set_num_channels(16)
            self._music_channel = pygame.mixer.Channel(0)
            self._generate_all()
            self.initialized = True
        except Exception:
            self.initialized = False

    def _make_sound(self, samples):
        """Convert numpy float array to pygame Sound."""
        samples = np.clip(samples, -1.0, 1.0)
        int_samples = (samples * 32767).astype(np.int16)
        # Make stereo by duplicating mono channel
        stereo = np.column_stack((int_samples, int_samples))
        sound = pygame.sndarray.make_sound(stereo)
        return sound

    def _envelope(self, length, attack=0.05, decay=0.1, sustain_level=0.7, release=0.2):
        """Generate ADSR envelope."""
        total = int(self.sample_rate * length)
        env = np.zeros(total)
        a = int(self.sample_rate * attack)
        d = int(self.sample_rate * decay)
        r = int(self.sample_rate * release)
        s = total - a - d - r
        if s < 0:
            s = 0
        idx = 0
        for i in range(min(a, total)):
            env[idx] = i / max(a, 1)
            idx += 1
        for i in range(min(d, total - idx)):
            env[idx] = 1.0 - (1.0 - sustain_level) * (i / max(d, 1))
            idx += 1
        for i in range(min(s, total - idx)):
            env[idx] = sustain_level
            idx += 1
        for i in range(min(r, total - idx)):
            env[idx] = sustain_level * (1.0 - i / max(r, 1))
            idx += 1
        return env

    def _sine(self, freq, duration):
        """Generate sine wave."""
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        return np.sin(2 * np.pi * freq * t)

    def _noise(self, duration):
        """Generate white noise."""
        return np.random.uniform(-1, 1, int(self.sample_rate * duration))

    def _generate_jump(self):
        dur = 0.15
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        freq = np.linspace(300, 800, len(t))
        phase = np.cumsum(2 * np.pi * freq / self.sample_rate)
        samples = np.sin(phase)
        env = self._envelope(dur, attack=0.01, decay=0.02, sustain_level=0.6, release=0.05)
        min_len = min(len(samples), len(env))
        samples = samples[:min_len] * env[:min_len] * 0.5
        self.sounds["jump"] = self._make_sound(samples)

    def _generate_land(self):
        dur = 0.1
        noise = self._noise(dur) * 0.4
        low_freq = self._sine(80, dur) * 0.6
        min_len = min(len(noise), len(low_freq))
        combined = noise[:min_len] + low_freq[:min_len]
        env = self._envelope(dur, attack=0.005, decay=0.03, sustain_level=0.2, release=0.04)
        min_len2 = min(len(combined), len(env))
        combined = combined[:min_len2] * env[:min_len2]
        self.sounds["land"] = self._make_sound(combined)

    def _generate_cable_grab(self):
        dur = 0.2
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        freq_mod = np.sin(2 * np.pi * 15 * t) * 200
        base_freq = 600
        phase = np.cumsum(2 * np.pi * (base_freq + freq_mod) / self.sample_rate)
        samples = np.sin(phase) * 0.5
        metallic = np.sin(2 * np.pi * 1200 * t) * 0.3
        combined = samples + metallic
        env = self._envelope(dur, attack=0.005, decay=0.05, sustain_level=0.4, release=0.08)
        min_len = min(len(combined), len(env))
        combined = combined[:min_len] * env[:min_len]
        self.sounds["cable_grab"] = self._make_sound(combined)

    def _generate_install_done(self):
        dur = 0.6
        total_samples = int(self.sample_rate * dur)
        samples = np.zeros(total_samples)
        notes = [523, 659, 784, 1047]
        note_dur = dur / len(notes)
        for idx_n, freq in enumerate(notes):
            start = int(idx_n * note_dur * self.sample_rate)
            end = int((idx_n + 1) * note_dur * self.sample_rate)
            seg_len = end - start
            seg_t = np.linspace(0, note_dur, seg_len, endpoint=False)
            seg = np.sin(2 * np.pi * freq * seg_t)
            seg_env = np.exp(-3 * seg_t / note_dur)
            samples[start:end] += seg * seg_env * 0.5
        self.sounds["install_done"] = self._make_sound(samples)

    def _generate_death(self):
        dur = 0.5
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        freq = np.linspace(500, 80, len(t))
        phase = np.cumsum(2 * np.pi * freq / self.sample_rate)
        samples = np.sin(phase) * 0.5
        buzz = self._noise(dur) * 0.2
        min_len = min(len(samples), len(buzz))
        combined = samples[:min_len] + buzz[:min_len]
        env = self._envelope(dur, attack=0.01, decay=0.1, sustain_level=0.5, release=0.2)
        min_len2 = min(len(combined), len(env))
        combined = combined[:min_len2] * env[:min_len2]
        self.sounds["death"] = self._make_sound(combined)

    def _generate_thunder(self):
        dur = 0.8
        noise = self._noise(dur)
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        low_rumble = np.sin(2 * np.pi * 40 * t) * 0.5
        combined = noise * 0.4 + low_rumble
        env = np.exp(-3 * t / dur)
        combined = combined * env * 0.7
        self.sounds["thunder"] = self._make_sound(combined)

    def _generate_rain_loop(self):
        dur = 2.0
        noise = self._noise(dur)
        total = len(noise)
        filtered = np.zeros(total)
        alpha = 0.05
        filtered[0] = noise[0] * alpha
        for i in range(1, total):
            filtered[i] = filtered[i - 1] * (1 - alpha) + noise[i] * alpha
        filtered = filtered / max(np.max(np.abs(filtered)), 0.001) * 0.15
        self.sounds["rain_loop"] = self._make_sound(filtered)

    def _generate_menu_select(self):
        dur = 0.08
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        samples = np.sin(2 * np.pi * 1000 * t)
        env = np.exp(-20 * t)
        samples = samples * env * 0.4
        self.sounds["menu_select"] = self._make_sound(samples)

    def _generate_excellent_chime(self):
        dur = 0.9
        total_samples = int(self.sample_rate * dur)
        samples = np.zeros(total_samples)
        arpeggio = [523, 659, 784, 1047, 1319]
        note_dur = dur / len(arpeggio)
        for idx_n, freq in enumerate(arpeggio):
            start = int(idx_n * note_dur * self.sample_rate)
            end = min(int((idx_n + 1.5) * note_dur * self.sample_rate), total_samples)
            seg_len = end - start
            seg_t = np.linspace(0, seg_len / self.sample_rate, seg_len, endpoint=False)
            seg = np.sin(2 * np.pi * freq * seg_t) * 0.3
            harmonic = np.sin(2 * np.pi * freq * 2 * seg_t) * 0.1
            seg_env = np.exp(-2 * seg_t)
            combined_seg = (seg + harmonic) * seg_env
            actual_end = min(start + seg_len, total_samples)
            actual_len = actual_end - start
            samples[start:actual_end] += combined_seg[:actual_len]
        samples = np.clip(samples, -1.0, 1.0)
        self.sounds["excellent_chime"] = self._make_sound(samples)

    def _generate_footstep(self):
        dur = 0.06
        noise = self._noise(dur) * 0.3
        t = np.linspace(0, dur, int(self.sample_rate * dur), endpoint=False)
        thud = np.sin(2 * np.pi * 120 * t) * 0.3
        combined = noise + thud[:len(noise)]
        env = np.exp(-30 * t[:len(combined)])
        combined = combined * env
        self.sounds["footstep"] = self._make_sound(combined)

    def _generate_music_menu(self):
        """Generate a chill looping menu track — synth pad + arpeggio."""
        dur = 8.0
        sr = self.sample_rate
        total = int(sr * dur)
        samples = np.zeros(total, dtype=np.float64)
        t = np.linspace(0, dur, total, endpoint=False)
        # Warm pad chord: Cm7 (C3, Eb3, G3, Bb3)
        pad_freqs = [130.81, 155.56, 196.0, 233.08]
        for f in pad_freqs:
            samples += np.sin(2 * np.pi * f * t) * 0.06
            samples += np.sin(2 * np.pi * f * 2 * t) * 0.02  # octave harmonic
        # Slow LFO tremolo on pad
        lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.25 * t)
        samples *= lfo
        # Arpeggio pattern: C4, Eb4, G4, Bb4, C5 repeating
        arp_notes = [261.63, 311.13, 392.0, 466.16, 523.25, 466.16, 392.0, 311.13]
        note_dur = 0.5
        note_samples = int(sr * note_dur)
        for i, freq in enumerate(arp_notes * int(dur / (len(arp_notes) * note_dur) + 1)):
            start = i * note_samples
            if start >= total:
                break
            end = min(start + note_samples, total)
            seg_len = end - start
            seg_t = np.linspace(0, seg_len / sr, seg_len, endpoint=False)
            # Triangle-ish wave for arpeggio
            arp_wave = np.sin(2 * np.pi * freq * seg_t) * 0.08
            arp_wave += np.sin(2 * np.pi * freq * 3 * seg_t) * 0.02
            # Note envelope
            arp_env = np.exp(-3.0 * seg_t / note_dur)
            samples[start:end] += arp_wave * arp_env
        # Bass note pulsing (C2)
        bass = np.sin(2 * np.pi * 65.41 * t) * 0.07
        bass_env = 0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t)
        samples += bass * bass_env
        # Fade in/out for seamless loop
        fade = int(sr * 0.3)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        samples = np.clip(samples, -1.0, 1.0)
        self.sounds["music_menu"] = self._make_sound(samples)

    def _generate_music_gameplay(self):
        """Generate an energetic looping gameplay track — driving beat + synth lead."""
        dur = 6.0
        sr = self.sample_rate
        total = int(sr * dur)
        samples = np.zeros(total, dtype=np.float64)
        t = np.linspace(0, dur, total, endpoint=False)
        # Kick drum pattern: 4 beats per bar, 120 BPM => beat every 0.5s
        beat_interval = 0.5
        beat_samples = int(sr * beat_interval)
        for b in range(int(dur / beat_interval)):
            start = b * beat_samples
            kick_len = min(int(sr * 0.12), total - start)
            if kick_len <= 0:
                break
            kick_t = np.linspace(0, 0.12, kick_len, endpoint=False)
            kick_freq = np.linspace(150, 40, kick_len)
            kick_phase = np.cumsum(2 * np.pi * kick_freq / sr)
            kick = np.sin(kick_phase)
            kick *= np.exp(-25 * kick_t) * 0.15
            end = min(start + kick_len, total)
            samples[start:end] += kick[:end - start]
        # Hi-hat on offbeats
        offbeat_interval = 0.25
        offbeat_samples = int(sr * offbeat_interval)
        for b in range(int(dur / offbeat_interval)):
            if b % 2 == 0:
                continue  # skip on-beats, hats on offbeats only
            start = b * offbeat_samples
            hat_len = min(int(sr * 0.04), total - start)
            if hat_len <= 0:
                break
            hat = np.random.uniform(-1, 1, hat_len) * 0.04
            hat *= np.exp(-60 * np.linspace(0, 0.04, hat_len))
            end = min(start + hat_len, total)
            samples[start:end] += hat[:end - start]
        # Bass line: alternating root and fifth (C2, G2)
        bass_notes = [65.41, 98.0, 65.41, 82.41]  # C2, G2, C2, E2
        bass_note_dur = dur / len(bass_notes)
        bass_note_samps = int(sr * bass_note_dur)
        for i, freq in enumerate(bass_notes):
            start = i * bass_note_samps
            end = min(start + bass_note_samps, total)
            seg_len = end - start
            seg_t = np.linspace(0, seg_len / sr, seg_len, endpoint=False)
            bass = np.sin(2 * np.pi * freq * seg_t) * 0.1
            bass += np.sin(2 * np.pi * freq * 2 * seg_t) * 0.04  # harmonic
            bass_env = np.ones(seg_len)
            release = int(sr * 0.05)
            if seg_len > release:
                bass_env[-release:] *= np.linspace(1, 0, release)
            samples[start:end] += bass * bass_env
        # Synth lead melody: simple repeating motif
        melody_notes = [523.25, 587.33, 659.25, 587.33, 523.25, 392.0, 440.0, 392.0]
        mel_note_dur = dur / len(melody_notes)
        mel_note_samps = int(sr * mel_note_dur)
        for i, freq in enumerate(melody_notes):
            start = i * mel_note_samps
            end = min(start + mel_note_samps, total)
            seg_len = end - start
            seg_t = np.linspace(0, seg_len / sr, seg_len, endpoint=False)
            # Saw-ish wave
            lead = np.sin(2 * np.pi * freq * seg_t) * 0.05
            lead += np.sin(2 * np.pi * freq * 2 * seg_t) * 0.025
            lead += np.sin(2 * np.pi * freq * 3 * seg_t) * 0.012
            mel_env = np.exp(-2.0 * seg_t / mel_note_dur)
            samples[start:end] += lead * mel_env
        # Fade in/out for loop
        fade = int(sr * 0.2)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        samples = np.clip(samples, -1.0, 1.0)
        self.sounds["music_gameplay"] = self._make_sound(samples)

    def _generate_music_boss(self):
        """Generate intense boss fight track — heavy bass + dissonant chords."""
        dur = 5.0
        sr = self.sample_rate
        total = int(sr * dur)
        samples = np.zeros(total, dtype=np.float64)
        t = np.linspace(0, dur, total, endpoint=False)
        # Heavy kick: 140 BPM
        beat_interval = 60.0 / 140
        beat_samples = int(sr * beat_interval)
        for b in range(int(dur / beat_interval)):
            start = b * beat_samples
            kick_len = min(int(sr * 0.1), total - start)
            if kick_len <= 0:
                break
            kick_t = np.linspace(0, 0.1, kick_len, endpoint=False)
            kick_freq = np.linspace(200, 30, kick_len)
            kick_phase = np.cumsum(2 * np.pi * kick_freq / sr)
            kick = np.sin(kick_phase)
            kick *= np.exp(-20 * kick_t) * 0.2
            end = min(start + kick_len, total)
            samples[start:end] += kick[:end - start]
        # Dissonant power chord drone: C2 + Db2 (semitone clash)
        samples += np.sin(2 * np.pi * 65.41 * t) * 0.08
        samples += np.sin(2 * np.pi * 69.30 * t) * 0.06  # Db2
        samples += np.sin(2 * np.pi * 130.81 * t) * 0.04  # C3
        # Pulsing distortion effect
        pulse = 0.6 + 0.4 * np.sin(2 * np.pi * 2.0 * t)
        samples *= pulse
        # Noise hits on every other beat
        for b in range(0, int(dur / beat_interval), 2):
            start = b * beat_samples
            noise_len = min(int(sr * 0.06), total - start)
            if noise_len <= 0:
                break
            noise = np.random.uniform(-1, 1, noise_len) * 0.06
            noise *= np.exp(-40 * np.linspace(0, 0.06, noise_len))
            end = min(start + noise_len, total)
            samples[start:end] += noise[:end - start]
        fade = int(sr * 0.15)
        samples[:fade] *= np.linspace(0, 1, fade)
        samples[-fade:] *= np.linspace(1, 0, fade)
        samples = np.clip(samples, -1.0, 1.0)
        self.sounds["music_boss"] = self._make_sound(samples)

    def _generate_all(self):
        self._generate_jump()
        self._generate_land()
        self._generate_cable_grab()
        self._generate_install_done()
        self._generate_death()
        self._generate_thunder()
        self._generate_rain_loop()
        self._generate_menu_select()
        self._generate_excellent_chime()
        self._generate_footstep()
        self._generate_music_menu()
        self._generate_music_gameplay()
        self._generate_music_boss()

    def play_sound(self, name):
        """Play a sound effect by name."""
        if self.initialized and name in self.sounds:
            channel = pygame.mixer.find_channel(True)
            if channel and channel != self._music_channel:
                channel.set_volume(self.sfx_volume)
                channel.play(self.sounds[name])

    def play_music(self, track_name):
        """Play a music track on loop."""
        self.stop_music()
        key = f"music_{track_name}"
        if self.initialized and key in self.sounds:
            self._music_channel.play(self.sounds[key], loops=-1)
            self._music_channel.set_volume(self.music_volume)

    def stop_music(self):
        """Stop currently playing music."""
        if hasattr(self, '_music_channel') and self._music_channel:
            self._music_channel.stop()

    def set_music_volume(self, vol):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, vol))
        if hasattr(self, '_music_channel') and self._music_channel:
            self._music_channel.set_volume(self.music_volume)

    def set_sfx_volume(self, vol):
        """Set SFX volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, vol))
        for name, snd in self.sounds.items():
            if not name.startswith("music_"):
                snd.set_volume(self.sfx_volume)


# ============================================================
# SECTION 5: BASE CLASSES
# ============================================================
@dataclass
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def add(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def sub(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def mul(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        ln = self.length()
        if ln < 0.0001:
            return Vec2(0, 0)
        return Vec2(self.x / ln, self.y / ln)

    def to_tuple(self):
        return (self.x, self.y)

    def to_int_tuple(self):
        return (int(self.x), int(self.y))


class Camera:
    """Smooth camera with target tracking and screen shake."""

    def __init__(self, width, height):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.width = width
        self.height = height
        self.lerp_speed = 0.08
        self.shake_amount = 0.0
        self.shake_decay = 0.9
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        self.bounds_left = 0
        self.bounds_top = 0
        self.bounds_right = 5000
        self.bounds_bottom = 2000
        self.shake_enabled = True

    def set_bounds(self, left, top, right, bottom):
        self.bounds_left = left
        self.bounds_top = top
        self.bounds_right = right
        self.bounds_bottom = bottom

    def set_target(self, tx, ty):
        self.target_x = tx - self.width // 2
        self.target_y = ty - self.height // 2

    def shake(self, amount):
        if not self.shake_enabled:
            return
        self.shake_amount = max(self.shake_amount, amount)

    def update(self):
        self.x += (self.target_x - self.x) * self.lerp_speed
        self.y += (self.target_y - self.y) * self.lerp_speed
        if self.x < self.bounds_left:
            self.x = self.bounds_left
        if self.y < self.bounds_top:
            self.y = self.bounds_top
        if self.x > self.bounds_right - self.width:
            self.x = self.bounds_right - self.width
        if self.y > self.bounds_bottom - self.height:
            self.y = self.bounds_bottom - self.height
        if self.shake_amount > 0.5:
            self.shake_offset_x = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_offset_y = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_amount *= self.shake_decay
        else:
            self.shake_amount = 0.0
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0

    def world_to_screen(self, wx, wy):
        sx = wx - self.x + self.shake_offset_x
        sy = wy - self.y + self.shake_offset_y
        return (int(sx), int(sy))

    def screen_to_world(self, sx, sy):
        wx = sx + self.x - self.shake_offset_x
        wy = sy + self.y - self.shake_offset_y
        return (wx, wy)


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    particle_type: str = "dust"


class ParticleSystem:
    """Manages and renders particles of various types."""

    def __init__(self):
        self.particles: List[Particle] = []

    def emit_rain(self, x, y, count=5):
        for _ in range(count):
            px = x + random.uniform(-WIDTH // 2, WIDTH // 2)
            py = y + random.uniform(-50, 0)
            vx = random.uniform(-0.5, -1.5)
            vy = random.uniform(8, 14)
            life = random.uniform(0.3, 0.7)
            shade = random.randint(100, 180)
            color = (shade, shade, 255)
            self.particles.append(Particle(px, py, vx, vy, life, life, color, 1.5, "rain"))

    def emit_spark(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.2, 0.5)
            color = random.choice([(255, 255, 100), (255, 200, 50), (255, 150, 0), (255, 255, 255)])
            self.particles.append(Particle(x, y, vx, vy, life, life, color, random.uniform(1, 3), "spark"))

    def emit_dust(self, x, y, count=4):
        for _ in range(count):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-2, -0.5)
            life = random.uniform(0.3, 0.6)
            shade = random.randint(150, 200)
            color = (shade, shade, shade - 20)
            self.particles.append(Particle(x, y, vx, vy, life, life, color, random.uniform(2, 5), "dust"))

    def emit_signal(self, x, y, color=SIGNAL_GOOD, count=1):
        for _ in range(count):
            life = random.uniform(0.5, 1.0)
            self.particles.append(Particle(x, y, 0, 0, life, life, color, 5, "signal"))

    def update(self, dt):
        to_remove = []
        for i, p in enumerate(self.particles):
            p.x += p.vx
            p.y += p.vy
            p.life -= dt
            if p.particle_type == "dust":
                p.vy -= 0.05
                p.size *= 0.98
            elif p.particle_type == "spark":
                p.vy += 0.15
                p.size *= 0.95
            elif p.particle_type == "signal":
                p.size += 2.0
            if p.life <= 0:
                to_remove.append(i)
        for i in reversed(to_remove):
            if i < len(self.particles):
                self.particles.pop(i)

    def draw(self, surface, camera):
        for p in self.particles:
            alpha = max(0.0, min(1.0, p.life / p.max_life))
            sx, sy = camera.world_to_screen(p.x, p.y)
            if sx < -50 or sx > WIDTH + 50 or sy < -50 or sy > HEIGHT + 50:
                continue
            r = max(0, min(255, int(p.color[0] * alpha)))
            g = max(0, min(255, int(p.color[1] * alpha)))
            b = max(0, min(255, int(p.color[2] * alpha)))
            color = (r, g, b)
            if p.particle_type == "rain":
                end_x = sx + int(p.vx * 2)
                end_y = sy + int(p.vy * 2)
                pygame.draw.line(surface, color, (sx, sy), (end_x, end_y), max(1, int(p.size)))
            elif p.particle_type == "spark":
                pygame.draw.circle(surface, color, (sx, sy), max(1, int(p.size)))
            elif p.particle_type == "dust":
                pygame.draw.circle(surface, color, (sx, sy), max(1, int(p.size)))
            elif p.particle_type == "signal":
                radius = max(1, int(p.size))
                pygame.draw.circle(surface, color, (sx, sy), radius, 2)


# ============================================================
# SECTION 6: PLATFORMS & SURFACES
# ============================================================
class Platform:
    """Base platform class."""

    def __init__(self, x, y, w, h, surface_type=SurfaceType.CONCRETE):
        self.rect = pygame.Rect(x, y, w, h)
        self.surface_type = surface_type
        self.friction = 1.0
        if surface_type == SurfaceType.WET:
            self.friction = WET_FRICTION
        elif surface_type == SurfaceType.METAL:
            self.friction = 0.9
        elif surface_type == SurfaceType.GRATE:
            self.friction = 0.85

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        pygame.draw.rect(surface, CONCRETE, (sx, sy, self.rect.width, self.rect.height))
        pygame.draw.rect(surface, DARK_GRAY, (sx, sy, self.rect.width, self.rect.height), 3)


class Rooftop(Platform):
    """Wide rooftop platform with concrete surface and random details."""

    def __init__(self, x, y, w, h=24):
        super().__init__(x, y, w, h, SurfaceType.CONCRETE)
        self.details = []
        num_details = max(1, w // 120)
        for _ in range(num_details):
            dx = random.randint(10, max(11, w - 40))
            detail_type = random.choice(["tinaco", "vent", "pipe"])
            self.details.append((dx, detail_type))
        rng = random.Random(x * 13 + y * 7)
        self.wall_color = (
            140 + rng.randint(-15, 15),
            130 + rng.randint(-15, 15),
            120 + rng.randint(-15, 15)
        )

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        if sx > WIDTH + 100 or sx + self.rect.width < -100:
            return
        w, h = self.rect.width, self.rect.height

        # Building side wall (below roof surface)
        wall_h = 60
        wall_color = self.wall_color
        wall_dark = tuple(max(0, c - 30) for c in wall_color)
        pygame.draw.rect(surface, wall_color, (sx, sy + h, w, wall_h))
        pygame.draw.rect(surface, wall_dark, (sx, sy + h, w, wall_h), 2)

        # Windows on side wall (2 rows)
        win_w, win_h = 10, 12
        win_spacing = 24
        for row in range(2):
            wy = sy + h + 8 + row * 22
            for wx_off in range(12, w - 12, win_spacing):
                wx = sx + wx_off
                is_lit = random.Random(int(wx * 100 + wy)).random() > 0.4
                if is_lit:
                    glow = (255, 230, 150)
                    pygame.draw.rect(surface, glow, (wx, wy, win_w, win_h))
                    pygame.draw.rect(surface, (200, 180, 100), (wx, wy, win_w, win_h), 1)
                else:
                    pygame.draw.rect(surface, (60, 65, 75), (wx, wy, win_w, win_h))
                    pygame.draw.rect(surface, (40, 45, 55), (wx, wy, win_w, win_h), 1)
                # Window cross
                pygame.draw.line(surface, (80, 80, 80), (wx + win_w // 2, wy), (wx + win_w // 2, wy + win_h), 1)
                pygame.draw.line(surface, (80, 80, 80), (wx, wy + win_h // 2), (wx + win_w, wy + win_h // 2), 1)

        # Roof surface
        pygame.draw.rect(surface, CONCRETE, (sx, sy, w, h))

        # Concrete texture dots
        rng = random.Random(self.rect.x * 7 + self.rect.y)
        for _ in range(w // 4):
            tx = sx + rng.randint(0, w)
            ty = sy + rng.randint(0, h)
            tc = rng.randint(-15, 15)
            dot_c = tuple(max(0, min(255, c + tc)) for c in CONCRETE)
            surface.set_at((int(tx), int(ty)), dot_c)

        # Parapet (raised edge)
        parapet_h = 6
        parapet_color = (165, 160, 155)
        pygame.draw.rect(surface, parapet_color, (sx, sy - parapet_h, w, parapet_h))
        pygame.draw.rect(surface, (140, 135, 130), (sx, sy - parapet_h, w, parapet_h), 2)
        # Parapet shadow on roof
        shadow_surf = pygame.Surface((w, 4), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 40))
        surface.blit(shadow_surf, (sx, sy))

        # Side edge outline
        pygame.draw.rect(surface, (120, 115, 110), (sx, sy, w, h), 3)

        # Roof details
        for dx, dtype in self.details:
            bx = sx + dx
            if dtype == "tinaco":
                # Water tank - cylindrical
                tank_w, tank_h = 22, 28
                # Tank body
                pygame.draw.rect(surface, (70, 75, 85), (bx, sy - tank_h, tank_w, tank_h))
                # Highlight stripe
                pygame.draw.rect(surface, (90, 95, 105), (bx + 2, sy - tank_h, 6, tank_h))
                # Lid
                pygame.draw.ellipse(surface, (85, 90, 100), (bx - 2, sy - tank_h - 4, tank_w + 4, 8))
                pygame.draw.ellipse(surface, (60, 65, 75), (bx - 2, sy - tank_h - 4, tank_w + 4, 8), 2)
                # Support legs
                pygame.draw.line(surface, (80, 80, 80), (bx + 3, sy), (bx + 3, sy + 4), 2)
                pygame.draw.line(surface, (80, 80, 80), (bx + tank_w - 3, sy), (bx + tank_w - 3, sy + 4), 2)
                # Pipe
                pygame.draw.line(surface, (100, 100, 100), (bx + tank_w, sy - tank_h // 2), (bx + tank_w + 12, sy - tank_h // 2), 2)
                pygame.draw.line(surface, (100, 100, 100), (bx + tank_w + 12, sy - tank_h // 2), (bx + tank_w + 12, sy), 2)
                # Outline
                pygame.draw.rect(surface, (50, 55, 65), (bx, sy - tank_h, tank_w, tank_h), 2)
            elif dtype == "vent":
                # Louvered vent box
                vent_w, vent_h = 18, 14
                pygame.draw.rect(surface, (155, 155, 165), (bx, sy - vent_h, vent_w, vent_h))
                # Louver slats
                for sl in range(4):
                    sly = sy - vent_h + 2 + sl * 3
                    pygame.draw.line(surface, (120, 120, 130), (bx + 2, sly), (bx + vent_w - 2, sly), 1)
                # Shadow below vent
                shadow_s = pygame.Surface((vent_w + 4, 3), pygame.SRCALPHA)
                shadow_s.fill((0, 0, 0, 30))
                surface.blit(shadow_s, (bx - 2, sy))
                pygame.draw.rect(surface, (100, 100, 110), (bx, sy - vent_h, vent_w, vent_h), 2)
            elif dtype == "pipe":
                # Vertical pipe with elbow
                pipe_h = 20
                pygame.draw.rect(surface, (130, 130, 140), (bx, sy - pipe_h, 6, pipe_h))
                pygame.draw.rect(surface, (145, 145, 155), (bx, sy - pipe_h, 2, pipe_h))  # highlight
                pygame.draw.ellipse(surface, (110, 110, 120), (bx - 2, sy - pipe_h - 3, 10, 6))
                pygame.draw.rect(surface, (100, 100, 110), (bx, sy - pipe_h, 6, pipe_h), 1)


class MetalGrate(Platform):
    """Narrow metal grate platform with grid pattern."""

    def __init__(self, x, y, w, h=12):
        super().__init__(x, y, w, h, SurfaceType.GRATE)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        if sx > WIDTH + 50 or sx + self.rect.width < -50:
            return
        w, h = self.rect.width, self.rect.height
        # Background (see-through feel)
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((40, 45, 50, 180))
        surface.blit(bg, (sx, sy))
        # Grid pattern
        grid_color = (110, 115, 120)
        spacing = 8
        for gx in range(0, w, spacing):
            pygame.draw.line(surface, grid_color, (sx + gx, sy), (sx + gx, sy + h), 1)
        for gy in range(0, h, spacing):
            pygame.draw.line(surface, grid_color, (sx, sy + gy), (sx + w, sy + gy), 1)
        # Highlight dots at intersections
        for gx in range(0, w, spacing):
            for gy in range(0, h, spacing):
                pygame.draw.circle(surface, (140, 145, 150), (sx + gx, sy + gy), 1)
        # Edge frame with rivets
        pygame.draw.rect(surface, (90, 95, 100), (sx, sy, w, h), 3)
        # Corner rivets
        for rx, ry in [(sx + 4, sy + 4), (sx + w - 4, sy + 4),
                       (sx + 4, sy + h - 4), (sx + w - 4, sy + h - 4)]:
            pygame.draw.circle(surface, (130, 135, 140), (rx, ry), 3)
            pygame.draw.circle(surface, (80, 85, 90), (rx, ry), 3, 1)
            pygame.draw.circle(surface, (160, 165, 170), (rx - 1, ry - 1), 1)
        # Side rivets
        for rx in range(int(sx) + 20, int(sx + w) - 10, 30):
            pygame.draw.circle(surface, (120, 125, 130), (rx, sy + 3), 2)
            pygame.draw.circle(surface, (120, 125, 130), (rx, sy + h - 3), 2)


class FiberCable:
    """Swingable fiber optic cable between two points."""

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        self.mid_x = (x1 + x2) / 2
        self.mid_y = (y1 + y2) / 2
        self.swing_angle = 0.0
        self.angular_vel = 0.0
        self.attached_player = None
        self.cable_length = 60.0
        self.glow_phase = random.uniform(0, math.pi * 2)

    def get_grab_rect(self):
        """Rectangle around the cable for grab detection."""
        min_x = min(self.x1, self.x2) - 10
        min_y = min(self.y1, self.y2) - 10
        w = abs(self.x2 - self.x1) + 20
        h = abs(self.y2 - self.y1) + 20
        return pygame.Rect(int(min_x), int(min_y), int(w), int(h))

    def attach(self, player):
        self.attached_player = player
        dx = player.x - self.mid_x
        dy = player.y - self.mid_y
        self.swing_angle = math.atan2(dx, dy)
        self.cable_length = max(40, math.sqrt(dx * dx + dy * dy))
        self.angular_vel = 0.0

    def detach(self):
        """Detach player, returning velocity from swing."""
        vx = self.angular_vel * self.cable_length * math.cos(self.swing_angle)
        vy = self.angular_vel * self.cable_length * -math.sin(self.swing_angle)
        self.attached_player = None
        self.angular_vel = 0.0
        return (vx * 0.15, vy * 0.15 - 3)

    def update(self):
        if self.attached_player is not None:
            gravity_torque = GRAVITY * math.sin(self.swing_angle) / max(self.cable_length, 1)
            self.angular_vel += gravity_torque * 0.5
            self.angular_vel *= 0.995
            self.swing_angle += self.angular_vel
            px = self.mid_x + math.sin(self.swing_angle) * self.cable_length
            py = self.mid_y + math.cos(self.swing_angle) * self.cable_length
            self.attached_player.x = px
            self.attached_player.y = py
        self.glow_phase += 0.05

    def draw(self, surface, camera):
        sx1, sy1 = camera.world_to_screen(self.x1, self.y1)
        sx2, sy2 = camera.world_to_screen(self.x2, self.y2)
        if max(sx1, sx2) < -50 or min(sx1, sx2) > WIDTH + 50:
            return
        glow_val = int(128 + 80 * math.sin(self.glow_phase))
        glow_color = (glow_val, int(glow_val * 0.6), 0)
        pygame.draw.line(surface, glow_color, (sx1, sy1), (sx2, sy2), 5)
        pygame.draw.line(surface, FIBER_CABLE, (sx1, sy1), (sx2, sy2), 3)
        bright = (255, 220, 100)
        pygame.draw.line(surface, bright, (sx1, sy1), (sx2, sy2), 1)
        pygame.draw.circle(surface, (200, 130, 0), (sx1, sy1), 5)
        pygame.draw.circle(surface, (200, 130, 0), (sx2, sy2), 5)
        if self.attached_player is not None:
            smx, smy = camera.world_to_screen(self.mid_x, self.mid_y)
            spx, spy = camera.world_to_screen(self.attached_player.x, self.attached_player.y)
            pygame.draw.line(surface, (200, 200, 50), (smx, smy), (spx, spy), 2)


class TelecomPole:
    """Climbable telecom pole with crossbars and insulators."""

    def __init__(self, x, y, height=200):
        self.x = x
        self.y = y
        self.height = height
        self.width = 16
        self.rect = pygame.Rect(x - self.width // 2, y - height, self.width, height)
        self.surface_type = SurfaceType.METAL
        self.crossbar_positions = []
        num_bars = max(1, height // 60)
        for i in range(num_bars):
            bar_y = y - height + 40 + i * (height - 50) // max(num_bars, 1)
            self.crossbar_positions.append(bar_y)

    def get_climb_rect(self):
        return pygame.Rect(self.rect.x - 8, self.rect.y, self.rect.width + 16, self.rect.height)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        if sx > WIDTH + 50 or sx + self.rect.width < -50:
            return
        pole_color = (120, 115, 105)
        pole_highlight = (150, 145, 135)
        pole_shadow = (90, 85, 75)
        pygame.draw.rect(surface, pole_color, (sx, sy, self.rect.width, self.rect.height))
        pygame.draw.rect(surface, pole_highlight, (sx, sy, self.rect.width // 3, self.rect.height))
        pygame.draw.rect(surface, pole_shadow,
                         (sx + self.rect.width * 2 // 3, sy, self.rect.width // 3, self.rect.height))
        pygame.draw.rect(surface, (80, 75, 65), (sx, sy, self.rect.width, self.rect.height), 2)
        bar_width = 60
        for bar_y in self.crossbar_positions:
            bsx, bsy = camera.world_to_screen(self.x - bar_width // 2, bar_y)
            pygame.draw.rect(surface, (100, 95, 85), (bsx, bsy, bar_width, 6))
            pygame.draw.rect(surface, (70, 65, 55), (bsx, bsy, bar_width, 6), 2)
            for ins_x_off in [-bar_width // 2 + 5, bar_width // 2 - 5]:
                ix = bsx + bar_width // 2 + ins_x_off
                pygame.draw.circle(surface, (60, 120, 60), (ix, bsy - 2), 4)
                pygame.draw.circle(surface, (40, 80, 40), (ix, bsy - 2), 4, 1)
                pygame.draw.line(surface, (80, 80, 80), (ix, bsy + 4), (ix, bsy - 6), 1)
        cap_sx, cap_sy = camera.world_to_screen(self.x - 4, self.rect.y - 8)
        pygame.draw.polygon(surface, (90, 85, 75),
                            [(cap_sx, cap_sy + 8), (cap_sx + 4, cap_sy), (cap_sx + 8, cap_sy + 8)])


class TowerStrut(Platform):
    """Angled metal beam with criss-cross pattern."""

    def __init__(self, x1, y1, x2, y2, thickness=16):
        min_x = min(x1, x2)
        min_y = min(y1, y2)
        w = abs(x2 - x1) + thickness
        h = abs(y2 - y1) + thickness
        super().__init__(min_x, min_y, w, h, SurfaceType.METAL)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.angle = math.atan2(y2 - y1, x2 - x1)
        self.length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def draw(self, surface, camera):
        sx1, sy1 = camera.world_to_screen(self.x1, self.y1)
        sx2, sy2 = camera.world_to_screen(self.x2, self.y2)
        if max(sx1, sx2) < -100 or min(sx1, sx2) > WIDTH + 100:
            return
        perp_x = -math.sin(self.angle) * self.thickness / 2
        perp_y = math.cos(self.angle) * self.thickness / 2
        points = [
            (sx1 + perp_x, sy1 + perp_y),
            (sx1 - perp_x, sy1 - perp_y),
            (sx2 - perp_x, sy2 - perp_y),
            (sx2 + perp_x, sy2 + perp_y),
        ]
        beam_color = (110, 105, 95)
        pygame.draw.polygon(surface, beam_color, [(int(px), int(py)) for px, py in points])
        pygame.draw.polygon(surface, (80, 75, 65), [(int(px), int(py)) for px, py in points], 3)
        num_crosses = max(2, int(self.length / 30))
        for i in range(num_crosses):
            frac = (i + 0.5) / num_crosses
            cx = sx1 + (sx2 - sx1) * frac
            cy = sy1 + (sy2 - sy1) * frac
            cross_size = self.thickness * 0.4
            c1 = (int(cx - cross_size * math.cos(self.angle) + perp_x * 0.6),
                  int(cy - cross_size * math.sin(self.angle) + perp_y * 0.6))
            c2 = (int(cx + cross_size * math.cos(self.angle) - perp_x * 0.6),
                  int(cy + cross_size * math.sin(self.angle) - perp_y * 0.6))
            c3 = (int(cx - cross_size * math.cos(self.angle) - perp_x * 0.6),
                  int(cy - cross_size * math.sin(self.angle) - perp_y * 0.6))
            c4 = (int(cx + cross_size * math.cos(self.angle) + perp_x * 0.6),
                  int(cy + cross_size * math.sin(self.angle) + perp_y * 0.6))
            cross_color = (70, 65, 55)
            pygame.draw.line(surface, cross_color, c1, c2, 2)
            pygame.draw.line(surface, cross_color, c3, c4, 2)


class WetConcrete(Platform):
    """Rooftop with rain puddles and reduced friction."""

    def __init__(self, x, y, w, h=24):
        super().__init__(x, y, w, h, SurfaceType.WET)
        self.friction = WET_FRICTION
        self.puddles = []
        num_puddles = max(1, w // 80)
        for _ in range(num_puddles):
            px = random.randint(10, max(11, w - 30))
            pw = random.randint(15, 40)
            self.puddles.append((px, pw))

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        if sx > WIDTH + 100 or sx + self.rect.width < -100:
            return
        w, h = self.rect.width, self.rect.height
        # Wet concrete base (darker than dry)
        wet_color = (130, 138, 155)
        pygame.draw.rect(surface, wet_color, (sx, sy, w, h))
        # Wet stain patches
        rng = random.Random(self.rect.x * 3 + self.rect.y)
        for _ in range(w // 30):
            sx2 = sx + rng.randint(5, w - 5)
            sy2 = sy + rng.randint(2, h - 2)
            sr = rng.randint(4, 10)
            stain = pygame.Surface((sr * 2, sr), pygame.SRCALPHA)
            pygame.draw.ellipse(stain, (115, 125, 145, 60), (0, 0, sr * 2, sr))
            surface.blit(stain, (sx2 - sr, sy2 - sr // 2))
        # Wet sheen highlight along top
        sheen = pygame.Surface((w, 3), pygame.SRCALPHA)
        sheen.fill((200, 210, 230, 70))
        surface.blit(sheen, (sx, sy))
        # Edge
        pygame.draw.rect(surface, (100, 108, 125), (sx, sy, w, h), 3)
        # Puddles with ripples
        for px, pw in self.puddles:
            puddle_x = sx + px
            puddle_y = sy + 2
            # Puddle base
            puddle_surf = pygame.Surface((pw, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(puddle_surf, (90, 125, 175, 110), (0, 0, pw, 8))
            surface.blit(puddle_surf, (puddle_x, puddle_y))
            # Reflection highlight
            pygame.draw.ellipse(surface, (160, 190, 230), (puddle_x + 4, puddle_y + 1, pw // 3, 4), 1)
            # Rain ripple circles
            ripple_phase = (pygame.time.get_ticks() / 500.0 + px) % 1.0
            ripple_r = int(3 + ripple_phase * 6)
            ripple_alpha = int(120 * (1.0 - ripple_phase))
            ripple_surf = pygame.Surface((ripple_r * 2 + 2, ripple_r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(ripple_surf, (180, 200, 240, ripple_alpha),
                              (ripple_r + 1, ripple_r + 1), ripple_r, 1)
            surface.blit(ripple_surf, (puddle_x + pw // 3 - ripple_r, puddle_y + 2 - ripple_r))


class AntennaMount(Platform):
    """Small platform at top of pole/tower for antenna installation."""

    def __init__(self, x, y, w=40, h=10):
        super().__init__(x, y, w, h, SurfaceType.ANTENNA)
        self.active = True
        self.installed = False
        self.glow_phase = random.uniform(0, math.pi * 2)

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.rect.x, self.rect.y)
        if sx > WIDTH + 50 or sx + self.rect.width < -50:
            return
        w, h = self.rect.width, self.rect.height
        # Mount platform
        mount_color = (75, 85, 95)
        pygame.draw.rect(surface, mount_color, (sx, sy, w, h))
        # Metal texture lines
        for tx in range(3, w - 3, 6):
            pygame.draw.line(surface, (85, 95, 105), (sx + tx, sy + 2), (sx + tx, sy + h - 2), 1)
        # Warning stripe
        stripe_w = 4
        for si in range(0, w, stripe_w * 2):
            pygame.draw.rect(surface, (200, 180, 0), (sx + si, sy, stripe_w, 3))
        # Bolts
        bolt_positions = [(5, h // 2), (w - 5, h // 2), (w // 2, 4), (w // 2, h - 4)]
        for bx, by in bolt_positions:
            pygame.draw.circle(surface, (140, 145, 155), (sx + bx, sy + by), 3)
            pygame.draw.circle(surface, (90, 95, 105), (sx + bx, sy + by), 3, 1)
            pygame.draw.circle(surface, (170, 175, 185), (sx + bx - 1, sy + by - 1), 1)
        # Cable stubs on sides
        pygame.draw.line(surface, (60, 60, 60), (sx - 3, sy + h // 2), (sx + 2, sy + h // 2), 2)
        pygame.draw.line(surface, (60, 60, 60), (sx + w - 2, sy + h // 2), (sx + w + 3, sy + h // 2), 2)
        # Frame
        pygame.draw.rect(surface, (55, 65, 75), (sx, sy, w, h), 2)

        if self.active and not self.installed:
            self.glow_phase += 0.08
            glow_intensity = int(128 + 127 * math.sin(self.glow_phase))
            indicator_color = (0, glow_intensity, int(glow_intensity * 0.6))
            cx = sx + w // 2
            cy = sy - 8
            # Pulsing indicator
            pygame.draw.circle(surface, indicator_color, (cx, cy), 6)
            pygame.draw.circle(surface, (0, 255, 150), (cx, cy), 6, 1)
            # Expanding rings
            for ring in range(3):
                ring_phase = (self.glow_phase + ring * 2.1) % 6.28
                ring_size = int(10 + 6 * math.sin(ring_phase * 0.5))
                ring_alpha = int(80 * max(0, math.sin(ring_phase * 0.5)))
                if ring_alpha > 5:
                    ring_surf = pygame.Surface((ring_size * 2 + 2, ring_size * 2 + 2), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surf, (0, 200, 100, ring_alpha),
                                      (ring_size + 1, ring_size + 1), ring_size, 1)
                    surface.blit(ring_surf, (cx - ring_size - 1, cy - ring_size - 1))
            # "INSTALL" text hint
            if int(self.glow_phase * 2) % 3 != 0:
                hint_font = pygame.font.Font(None, 16)
                hint = hint_font.render("E", True, (0, 255, 150))
                surface.blit(hint, (cx - hint.get_width() // 2, cy - 20))
        elif self.installed:
            cx = sx + w // 2
            cy = sy - 14
            # Sector antenna panel
            pygame.draw.rect(surface, (185, 185, 195), (cx - 5, sy - 28, 10, 28))
            pygame.draw.rect(surface, (160, 160, 170), (cx - 5, sy - 28, 10, 28), 2)
            # Panel face with slots
            for slot_y in range(sy - 26, sy - 4, 5):
                pygame.draw.line(surface, (140, 140, 150), (cx - 3, slot_y), (cx + 3, slot_y), 1)
            # Top cap
            pygame.draw.rect(surface, (170, 170, 180), (cx - 6, sy - 30, 12, 4))
            # Signal indicator light
            pygame.draw.circle(surface, SIGNAL_GOOD, (cx, sy - 32), 3)
            pygame.draw.circle(surface, (0, 200, 80), (cx, sy - 32), 3, 1)
            # Mounting bracket
            pygame.draw.line(surface, (120, 120, 130), (cx - 5, sy - 10), (cx - 8, sy), 2)
            pygame.draw.line(surface, (120, 120, 130), (cx + 5, sy - 10), (cx + 8, sy), 2)


# ============================================================
# SECTION 7: CHARACTERS
# ============================================================
class CharacterBase:
    """Base class for all playable characters."""

    def __init__(self):
        self.speed = 7
        self.jump_power = 12
        self.grip = 7
        self.install_skill = 6
        self.special_name = "NONE"
        self.special_cooldown_max = 5.0
        self.special_cooldown = 0.0
        self.special_duration_max = 1.0
        self.special_duration = 0.0
        self.special_active = False
        self.anim_state = AnimState.IDLE
        self.anim_frame = 0
        self.anim_timer = 0
        self.facing_right = True
        self.name = "Base"
        self.colors = {}

    def activate_special(self):
        if self.special_cooldown <= 0:
            self.special_active = True
            self.special_duration = self.special_duration_max
            self.special_cooldown = self.special_cooldown_max
            return True
        return False

    def update_special(self, dt, **kwargs):
        if self.special_active:
            self.special_duration -= dt
            if self.special_duration <= 0:
                self.special_active = False
                self.special_duration = 0
        if self.special_cooldown > 0:
            self.special_cooldown -= dt

    def update_animation(self, dt):
        self.anim_timer += dt
        if self.anim_timer > 0.1:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 8

    def draw(self, surface, x, y, camera):
        pass


class Rico(CharacterBase):
    """Rico - The starter character. Sarcastic cable tech with fiber lasso."""

    def __init__(self):
        super().__init__()
        self.name = "Rico"
        self.speed = 7
        self.jump_power = 12
        self.grip = 7
        self.install_skill = 6
        self.special_name = "CABLE_WHIP"
        self.special_cooldown_max = 5.0
        self.special_duration_max = 0.5
        self.lasso_x = 0.0
        self.lasso_y = 0.0
        self.lasso_active = False
        self.lasso_target = None
        self.colors = {
            "hat": (230, 210, 40),
            "hat_band": (200, 180, 30),
            "skin": (210, 180, 140),
            "vest": (50, 80, 160),
            "vest_pocket": (40, 65, 130),
            "pants": (120, 90, 60),
            "boots": (80, 60, 40),
            "goggles": (200, 200, 220),
            "goggle_rim": (100, 100, 100),
            "belt": (90, 70, 50),
            "outline": (30, 30, 30),
        }

    def activate_special(self):
        if self.special_cooldown <= 0:
            self.special_active = True
            self.special_duration = self.special_duration_max
            self.special_cooldown = self.special_cooldown_max
            self.lasso_active = True
            return True
        return False

    def update_special(self, dt, **kwargs):
        super().update_special(dt)
        if self.lasso_active and not self.special_active:
            self.lasso_active = False
            self.lasso_target = None

    def draw(self, surface, x, y, camera):
        sx, sy = camera.world_to_screen(x, y)
        f = 1 if self.facing_right else -1
        c = self.colors
        outline = c["outline"]
        bob = 0
        leg_phase = 0
        if self.anim_state == AnimState.RUN:
            bob = int(math.sin(self.anim_frame * 0.8) * 2)
            leg_phase = self.anim_frame * 0.8
        elif self.anim_state == AnimState.JUMP:
            bob = -2
        elif self.anim_state == AnimState.FALL:
            bob = 2
        head_x = sx
        head_y = sy - 32 + bob
        pygame.draw.circle(surface, c["skin"], (head_x, head_y), 10)
        pygame.draw.circle(surface, outline, (head_x, head_y), 10, 2)
        hat_rect = pygame.Rect(head_x - 13, head_y - 14, 26, 10)
        pygame.draw.ellipse(surface, c["hat"], hat_rect)
        pygame.draw.arc(surface, c["hat"], (head_x - 12, head_y - 18, 24, 16), 0, math.pi, 0)
        pygame.draw.ellipse(surface, c["hat"], (head_x - 10, head_y - 20, 20, 14))
        pygame.draw.rect(surface, c["hat_band"], (head_x - 10, head_y - 10, 20, 3))
        pygame.draw.ellipse(surface, outline, hat_rect, 2)
        gx = head_x + f * 4
        gy = head_y - 1
        pygame.draw.circle(surface, c["goggles"], (gx, gy), 5)
        pygame.draw.circle(surface, c["goggle_rim"], (gx, gy), 5, 2)
        pygame.draw.circle(surface, (50, 50, 60), (gx + f, gy), 2)
        eye_x = head_x + f * 5
        eye_y = head_y - 1
        mouth_y = head_y + 4
        if self.anim_state == AnimState.DEATH:
            pygame.draw.line(surface, outline, (eye_x - 2, head_y - 2), (eye_x + 2, head_y + 2), 2)
            pygame.draw.line(surface, outline, (eye_x - 2, head_y + 2), (eye_x + 2, head_y - 2), 2)
        if self.anim_state != AnimState.DEATH:
            pygame.draw.line(surface, outline, (head_x + f * 2, mouth_y), (head_x + f * 6, mouth_y), 2)
        body_top = sy - 20 + bob
        body_bottom = sy - 4 + bob
        body_x = sx
        pygame.draw.rect(surface, c["vest"], (body_x - 8, body_top, 16, body_bottom - body_top))
        pygame.draw.rect(surface, outline, (body_x - 8, body_top, 16, body_bottom - body_top), 2)
        pocket_y = body_top + 8
        pygame.draw.rect(surface, c["vest_pocket"], (body_x - 6 + (0 if f > 0 else 4), pocket_y, 5, 5))
        pygame.draw.rect(surface, outline, (body_x - 6 + (0 if f > 0 else 4), pocket_y, 5, 5), 1)
        belt_y = body_bottom - 3
        pygame.draw.rect(surface, c["belt"], (body_x - 9, belt_y, 18, 4))
        pygame.draw.rect(surface, (200, 180, 50), (body_x - 1, belt_y, 3, 4))
        tool_x = body_x + f * 9
        pygame.draw.rect(surface, (100, 100, 110), (tool_x - 2, belt_y - 2, 4, 8))
        arm_y = body_top + 3
        if self.anim_state == AnimState.INSTALL:
            arm_end_x = body_x + f * 18
            arm_end_y = arm_y - 5
            pygame.draw.line(surface, c["skin"], (body_x + f * 8, arm_y), (arm_end_x, arm_end_y), 5)
            pygame.draw.line(surface, outline, (body_x + f * 8, arm_y), (arm_end_x, arm_end_y), 2)
            pygame.draw.circle(surface, c["skin"], (arm_end_x, arm_end_y), 3)
        elif self.anim_state == AnimState.CABLE_SWING:
            arm_end_x = body_x + f * 14
            arm_end_y = arm_y - 10
            pygame.draw.line(surface, c["skin"], (body_x + f * 8, arm_y), (arm_end_x, arm_end_y), 5)
            pygame.draw.line(surface, outline, (body_x + f * 8, arm_y), (arm_end_x, arm_end_y), 2)
        else:
            arm_swing = math.sin(leg_phase) * 6 if self.anim_state == AnimState.RUN else 0
            arm_end_y_val = arm_y + 14 + int(arm_swing)
            pygame.draw.line(surface, c["skin"], (body_x + f * 8, arm_y),
                             (body_x + f * 10, arm_end_y_val), 5)
            pygame.draw.line(surface, outline, (body_x + f * 8, arm_y),
                             (body_x + f * 10, arm_end_y_val), 2)
            back_arm_x = body_x - f * 8
            back_swing = -arm_swing
            pygame.draw.line(surface, c["skin"], (back_arm_x, arm_y),
                             (back_arm_x - f * 2, arm_y + 14 + int(back_swing)), 4)
            pygame.draw.line(surface, outline, (back_arm_x, arm_y),
                             (back_arm_x - f * 2, arm_y + 14 + int(back_swing)), 2)
        hip_y = body_bottom + bob
        if self.anim_state == AnimState.RUN:
            l1_swing = math.sin(leg_phase) * 8
            l2_swing = math.sin(leg_phase + math.pi) * 8
            foot1_x = body_x + int(l1_swing)
            foot2_x = body_x + int(l2_swing)
            pygame.draw.line(surface, c["pants"], (body_x - 3, hip_y), (foot1_x - 3, hip_y + 14), 5)
            pygame.draw.line(surface, c["pants"], (body_x + 3, hip_y), (foot2_x + 3, hip_y + 14), 5)
            pygame.draw.line(surface, outline, (body_x - 3, hip_y), (foot1_x - 3, hip_y + 14), 2)
            pygame.draw.line(surface, outline, (body_x + 3, hip_y), (foot2_x + 3, hip_y + 14), 2)
            pygame.draw.rect(surface, c["boots"], (foot1_x - 6, hip_y + 12, 8, 5))
            pygame.draw.rect(surface, c["boots"], (foot2_x, hip_y + 12, 8, 5))
        elif self.anim_state == AnimState.JUMP:
            pygame.draw.line(surface, c["pants"], (body_x - 4, hip_y), (body_x - 8, hip_y + 10), 5)
            pygame.draw.line(surface, c["pants"], (body_x + 4, hip_y), (body_x + 8, hip_y + 10), 5)
            pygame.draw.line(surface, outline, (body_x - 4, hip_y), (body_x - 8, hip_y + 10), 2)
            pygame.draw.line(surface, outline, (body_x + 4, hip_y), (body_x + 8, hip_y + 10), 2)
            pygame.draw.rect(surface, c["boots"], (body_x - 11, hip_y + 8, 8, 5))
            pygame.draw.rect(surface, c["boots"], (body_x + 5, hip_y + 8, 8, 5))
        else:
            pygame.draw.line(surface, c["pants"], (body_x - 3, hip_y), (body_x - 4, hip_y + 14), 5)
            pygame.draw.line(surface, c["pants"], (body_x + 3, hip_y), (body_x + 4, hip_y + 14), 5)
            pygame.draw.line(surface, outline, (body_x - 3, hip_y), (body_x - 4, hip_y + 14), 2)
            pygame.draw.line(surface, outline, (body_x + 3, hip_y), (body_x + 4, hip_y + 14), 2)
            pygame.draw.rect(surface, c["boots"], (body_x - 7, hip_y + 12, 8, 5))
            pygame.draw.rect(surface, c["boots"], (body_x + 1, hip_y + 12, 8, 5))
        if self.lasso_active:
            lasso_range = 200 * (1.0 - self.special_duration / self.special_duration_max)
            lx = sx + f * lasso_range
            ly = sy - 20
            pygame.draw.line(surface, FIBER_CABLE, (sx + f * 10, sy - 18), (int(lx), int(ly)), 3)
            pygame.draw.circle(surface, (255, 200, 50), (int(lx), int(ly)), 6, 2)

    def draw_special_effect(self, surface, x, y, camera):
        if self.lasso_active:
            sx, sy = camera.world_to_screen(x, y)
            f = 1 if self.facing_right else -1
            progress = 1.0 - self.special_duration / self.special_duration_max
            reach = 200 * progress
            lx = sx + f * reach
            ly = sy - 20
            pygame.draw.line(surface, FIBER_CABLE, (sx + f * 10, sy - 18), (int(lx), int(ly)), 3)
            pygame.draw.circle(surface, (255, 200, 50), (int(lx), int(ly)), 8, 2)


class Vero(CharacterBase):
    """Ing. Vero - RF engineer. Precise, exasperated. Spectrum scan ability."""

    def __init__(self):
        super().__init__()
        self.name = "Ing. Vero"
        self.speed = 6
        self.jump_power = 11
        self.grip = 6
        self.install_skill = 10
        self.special_name = "SPECTRUM_SCAN"
        self.special_cooldown_max = 8.0
        self.special_duration_max = 3.0
        self.scan_radius = 0.0
        self.scan_max_radius = 250.0
        self.colors = {
            "hat": (240, 240, 245),
            "hat_visor": (180, 180, 190),
            "skin": (230, 210, 190),
            "glasses": (180, 180, 220),
            "glasses_rim": (80, 80, 100),
            "hair": (50, 30, 20),
            "vest": (140, 60, 180),
            "vest_detail": (120, 40, 160),
            "pants": (30, 30, 35),
            "boots": (60, 60, 65),
            "outline": (30, 30, 30),
        }

    def activate_special(self):
        if self.special_cooldown <= 0:
            self.special_active = True
            self.special_duration = self.special_duration_max
            self.special_cooldown = self.special_cooldown_max
            self.scan_radius = 0.0
            return True
        return False

    def update_special(self, dt, **kwargs):
        super().update_special(dt)
        if self.special_active:
            self.scan_radius = min(self.scan_max_radius,
                                   self.scan_radius + self.scan_max_radius * dt * 2)

    def draw(self, surface, x, y, camera):
        sx, sy = camera.world_to_screen(x, y)
        f = 1 if self.facing_right else -1
        c = self.colors
        outline = c["outline"]
        bob = 0
        leg_phase = 0
        if self.anim_state == AnimState.RUN:
            bob = int(math.sin(self.anim_frame * 0.8) * 2)
            leg_phase = self.anim_frame * 0.8
        head_x = sx
        head_y = sy - 32 + bob
        pygame.draw.circle(surface, c["skin"], (head_x, head_y), 10)
        pygame.draw.circle(surface, outline, (head_x, head_y), 10, 2)
        tail_x = head_x - f * 8
        pygame.draw.line(surface, c["hair"], (tail_x, head_y - 2), (tail_x - f * 6, head_y + 12), 4)
        pygame.draw.line(surface, outline, (tail_x, head_y - 2), (tail_x - f * 6, head_y + 12), 2)
        pygame.draw.arc(surface, c["hair"], (head_x - 10, head_y - 12, 20, 10), 0, math.pi, 3)
        hat_w = 24
        hat_h = 12
        pygame.draw.ellipse(surface, c["hat"], (head_x - hat_w // 2, head_y - 16, hat_w, hat_h))
        pygame.draw.ellipse(surface, c["hat"], (head_x - 10, head_y - 20, 20, 14))
        pygame.draw.ellipse(surface, outline, (head_x - hat_w // 2, head_y - 16, hat_w, hat_h), 2)
        visor_pts = [(head_x + f * 8, head_y - 8), (head_x + f * 14, head_y - 6),
                     (head_x + f * 12, head_y - 4)]
        pygame.draw.polygon(surface, c["hat_visor"], visor_pts)
        gx = head_x + f * 3
        gy = head_y - 1
        pygame.draw.rect(surface, c["glasses"], (gx - 6, gy - 3, 6, 6))
        pygame.draw.rect(surface, c["glasses"], (gx + 1, gy - 3, 6, 6))
        pygame.draw.rect(surface, c["glasses_rim"], (gx - 6, gy - 3, 6, 6), 1)
        pygame.draw.rect(surface, c["glasses_rim"], (gx + 1, gy - 3, 6, 6), 1)
        pygame.draw.line(surface, c["glasses_rim"], (gx, gy - 1), (gx + 1, gy - 1), 1)
        pygame.draw.circle(surface, (40, 40, 50), (gx - 3, gy), 2)
        pygame.draw.circle(surface, (40, 40, 50), (gx + 4, gy), 2)
        mouth_y = head_y + 4
        if self.anim_state == AnimState.IDLE:
            pygame.draw.line(surface, outline, (head_x + f * 1, mouth_y),
                             (head_x + f * 5, mouth_y + 1), 2)
        else:
            pygame.draw.line(surface, outline, (head_x + f * 1, mouth_y),
                             (head_x + f * 5, mouth_y), 2)
        body_top = sy - 20 + bob
        body_bottom = sy - 4 + bob
        pygame.draw.rect(surface, c["vest"], (sx - 8, body_top, 16, body_bottom - body_top))
        pygame.draw.rect(surface, outline, (sx - 8, body_top, 16, body_bottom - body_top), 2)
        pygame.draw.line(surface, c["vest_detail"], (sx, body_top), (sx, body_bottom), 1)
        id_x = sx - f * 5
        pygame.draw.rect(surface, (220, 220, 230), (id_x - 3, body_top + 3, 6, 8))
        pygame.draw.rect(surface, outline, (id_x - 3, body_top + 3, 6, 8), 1)
        arm_y = body_top + 3
        if self.anim_state == AnimState.IDLE:
            clip_x = sx + f * 14
            clip_y = arm_y + 2
            pygame.draw.line(surface, c["skin"], (sx + f * 8, arm_y), (clip_x, clip_y), 5)
            pygame.draw.line(surface, outline, (sx + f * 8, arm_y), (clip_x, clip_y), 2)
            pygame.draw.rect(surface, (180, 160, 140), (clip_x - 2, clip_y - 6, 8, 10))
            pygame.draw.rect(surface, outline, (clip_x - 2, clip_y - 6, 8, 10), 1)
            for ln in range(3):
                pygame.draw.line(surface, (100, 100, 110), (clip_x, clip_y - 4 + ln * 3),
                                 (clip_x + 4, clip_y - 4 + ln * 3), 1)
        else:
            arm_swing = math.sin(leg_phase) * 6 if self.anim_state == AnimState.RUN else 0
            pygame.draw.line(surface, c["skin"], (sx + f * 8, arm_y),
                             (sx + f * 10, arm_y + 14 + int(arm_swing)), 5)
            pygame.draw.line(surface, outline, (sx + f * 8, arm_y),
                             (sx + f * 10, arm_y + 14 + int(arm_swing)), 2)
        back_arm_y = arm_y
        back_swing = -math.sin(leg_phase) * 6 if self.anim_state == AnimState.RUN else 0
        pygame.draw.line(surface, c["skin"], (sx - f * 8, back_arm_y),
                         (sx - f * 10, back_arm_y + 14 + int(back_swing)), 4)
        pygame.draw.line(surface, outline, (sx - f * 8, back_arm_y),
                         (sx - f * 10, back_arm_y + 14 + int(back_swing)), 2)
        hip_y = body_bottom + bob
        if self.anim_state == AnimState.RUN:
            l1 = math.sin(leg_phase) * 8
            l2 = math.sin(leg_phase + math.pi) * 8
            pygame.draw.line(surface, c["pants"], (sx - 3, hip_y), (sx - 3 + int(l1), hip_y + 14), 5)
            pygame.draw.line(surface, c["pants"], (sx + 3, hip_y), (sx + 3 + int(l2), hip_y + 14), 5)
            pygame.draw.line(surface, outline, (sx - 3, hip_y), (sx - 3 + int(l1), hip_y + 14), 2)
            pygame.draw.line(surface, outline, (sx + 3, hip_y), (sx + 3 + int(l2), hip_y + 14), 2)
            pygame.draw.rect(surface, c["boots"], (sx - 6 + int(l1), hip_y + 12, 8, 5))
            pygame.draw.rect(surface, c["boots"], (sx + int(l2), hip_y + 12, 8, 5))
        else:
            pygame.draw.line(surface, c["pants"], (sx - 3, hip_y), (sx - 4, hip_y + 14), 5)
            pygame.draw.line(surface, c["pants"], (sx + 3, hip_y), (sx + 4, hip_y + 14), 5)
            pygame.draw.line(surface, outline, (sx - 3, hip_y), (sx - 4, hip_y + 14), 2)
            pygame.draw.line(surface, outline, (sx + 3, hip_y), (sx + 4, hip_y + 14), 2)
            pygame.draw.rect(surface, c["boots"], (sx - 7, hip_y + 12, 8, 5))
            pygame.draw.rect(surface, c["boots"], (sx + 1, hip_y + 12, 8, 5))

    def draw_special_effect(self, surface, x, y, camera):
        if self.special_active and self.scan_radius > 5:
            sx, sy = camera.world_to_screen(x, y)
            rad = int(self.scan_radius)
            alpha = max(30, int(150 * (self.special_duration / self.special_duration_max)))
            ring_surf = pygame.Surface((rad * 2 + 4, rad * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (0, 200, 255, alpha), (rad + 2, rad + 2), rad, 3)
            pygame.draw.circle(ring_surf, (0, 255, 200, alpha // 2), (rad + 2, rad + 2), rad - 5, 2)
            surface.blit(ring_surf, (sx - rad - 2, sy - rad - 2))


class DonAurelio(CharacterBase):
    """Don Aurelio - Old-school veteran. Ghost relay ability. Rick Sanchez energy."""

    def __init__(self):
        super().__init__()
        self.name = "Don Aurelio"
        self.speed = 5
        self.jump_power = 10
        self.grip = 10
        self.install_skill = 10
        self.special_name = "SENAL_FANTASMA"
        self.special_cooldown_max = 10.0
        self.special_duration_max = 5.0
        self.ghost_x = 0.0
        self.ghost_y = 0.0
        self.ghost_placed = False
        self.colors = {
            "hair": (180, 180, 190),
            "skin": (170, 140, 110),
            "eyebrows": (140, 140, 150),
            "shirt": (60, 130, 70),
            "shirt_button": (220, 200, 150),
            "pants": (180, 170, 130),
            "belt": (100, 80, 50),
            "shoes": (90, 70, 50),
            "outline": (30, 30, 30),
        }

    def activate_special(self):
        if self.special_cooldown <= 0:
            self.special_active = True
            self.special_duration = self.special_duration_max
            self.special_cooldown = self.special_cooldown_max
            self.ghost_placed = True
            return True
        return False

    def place_ghost(self, x, y):
        self.ghost_x = x
        self.ghost_y = y

    def update_special(self, dt, **kwargs):
        super().update_special(dt)
        if not self.special_active:
            self.ghost_placed = False

    def draw(self, surface, x, y, camera):
        sx, sy = camera.world_to_screen(x, y)
        f = 1 if self.facing_right else -1
        c = self.colors
        outline = c["outline"]
        bob = 0
        leg_phase = 0
        if self.anim_state == AnimState.RUN:
            bob = int(math.sin(self.anim_frame * 0.8) * 2)
            leg_phase = self.anim_frame * 0.8
        head_x = sx
        head_y = sy - 32 + bob
        pygame.draw.circle(surface, c["skin"], (head_x, head_y), 11)
        pygame.draw.circle(surface, outline, (head_x, head_y), 11, 2)
        hair_pts = []
        for spike in range(7):
            angle = math.pi + spike * math.pi / 7
            bx = head_x + int(math.cos(angle) * 10)
            by = head_y + int(math.sin(angle) * 10)
            tx = head_x + int(math.cos(angle + 0.15) * (16 + random.randint(-1, 1)))
            ty = head_y + int(math.sin(angle + 0.15) * (16 + random.randint(-1, 1)))
            pygame.draw.line(surface, c["hair"], (bx, by), (tx, ty), 3)
        eb_y = head_y - 5
        pygame.draw.line(surface, c["eyebrows"], (head_x - 6, eb_y), (head_x - 1, eb_y - 3), 3)
        pygame.draw.line(surface, c["eyebrows"], (head_x + 1, eb_y - 3), (head_x + 6, eb_y), 3)
        eye_y = head_y - 1
        pygame.draw.circle(surface, (240, 240, 240), (head_x - 4, eye_y), 3)
        pygame.draw.circle(surface, (240, 240, 240), (head_x + 4, eye_y), 3)
        pygame.draw.circle(surface, (30, 30, 30), (head_x - 4 + f, eye_y), 2)
        pygame.draw.circle(surface, (30, 30, 30), (head_x + 4 + f, eye_y), 2)
        mouth_y = head_y + 5
        if self.anim_state == AnimState.IDLE:
            pygame.draw.arc(surface, outline, (head_x - 4, mouth_y - 2, 8, 6), math.pi, 2 * math.pi, 2)
        else:
            pygame.draw.line(surface, outline, (head_x - 3, mouth_y), (head_x + 3, mouth_y), 2)
        body_top = sy - 20 + bob
        body_bottom = sy - 2 + bob
        bh = body_bottom - body_top
        pygame.draw.rect(surface, c["shirt"], (sx - 10, body_top, 20, bh))
        pygame.draw.rect(surface, outline, (sx - 10, body_top, 20, bh), 2)
        for btn_i in range(3):
            btn_y = body_top + 4 + btn_i * 5
            pygame.draw.circle(surface, c["shirt_button"], (sx, btn_y), 2)
        pygame.draw.rect(surface, c["belt"], (sx - 11, body_bottom - 4, 22, 5))
        pygame.draw.rect(surface, outline, (sx - 11, body_bottom - 4, 22, 5), 1)
        for gadget in range(3):
            gx_off = -8 + gadget * 7
            pygame.draw.rect(surface, (100, 100, 110), (sx + gx_off, body_bottom - 8, 5, 6))
            pygame.draw.rect(surface, (80, 80, 90), (sx + gx_off, body_bottom - 8, 5, 6), 1)
        arm_y = body_top + 3
        arm_swing = math.sin(leg_phase) * 6 if self.anim_state == AnimState.RUN else 0
        pygame.draw.line(surface, c["skin"], (sx + f * 10, arm_y),
                         (sx + f * 12, arm_y + 16 + int(arm_swing)), 5)
        pygame.draw.line(surface, outline, (sx + f * 10, arm_y),
                         (sx + f * 12, arm_y + 16 + int(arm_swing)), 2)
        pygame.draw.line(surface, c["skin"], (sx - f * 10, arm_y),
                         (sx - f * 12, arm_y + 16 - int(arm_swing)), 4)
        pygame.draw.line(surface, outline, (sx - f * 10, arm_y),
                         (sx - f * 12, arm_y + 16 - int(arm_swing)), 2)
        hip_y = body_bottom + bob
        if self.anim_state == AnimState.RUN:
            l1 = math.sin(leg_phase) * 7
            l2 = math.sin(leg_phase + math.pi) * 7
            pygame.draw.line(surface, c["pants"], (sx - 4, hip_y), (sx - 4 + int(l1), hip_y + 14), 6)
            pygame.draw.line(surface, c["pants"], (sx + 4, hip_y), (sx + 4 + int(l2), hip_y + 14), 6)
            pygame.draw.line(surface, outline, (sx - 4, hip_y), (sx - 4 + int(l1), hip_y + 14), 2)
            pygame.draw.line(surface, outline, (sx + 4, hip_y), (sx + 4 + int(l2), hip_y + 14), 2)
            pygame.draw.rect(surface, c["shoes"], (sx - 7 + int(l1), hip_y + 12, 9, 5))
            pygame.draw.rect(surface, c["shoes"], (sx + 1 + int(l2), hip_y + 12, 9, 5))
        else:
            pygame.draw.line(surface, c["pants"], (sx - 4, hip_y), (sx - 5, hip_y + 14), 6)
            pygame.draw.line(surface, c["pants"], (sx + 4, hip_y), (sx + 5, hip_y + 14), 6)
            pygame.draw.line(surface, outline, (sx - 4, hip_y), (sx - 5, hip_y + 14), 2)
            pygame.draw.line(surface, outline, (sx + 4, hip_y), (sx + 5, hip_y + 14), 2)
            pygame.draw.rect(surface, c["shoes"], (sx - 8, hip_y + 12, 9, 5))
            pygame.draw.rect(surface, c["shoes"], (sx + 2, hip_y + 12, 9, 5))

    def draw_special_effect(self, surface, x, y, camera):
        if self.ghost_placed and self.special_active:
            gsx, gsy = camera.world_to_screen(self.ghost_x, self.ghost_y)
            ghost_surf = pygame.Surface((60, 80), pygame.SRCALPHA)
            alpha = max(40, int(180 * (self.special_duration / self.special_duration_max)))
            pygame.draw.rect(ghost_surf, (0, 255, 150, alpha), (25, 20, 10, 50))
            pygame.draw.polygon(ghost_surf, (0, 255, 150, alpha),
                                [(20, 20), (30, 5), (40, 20)])
            for ring_i in range(3):
                r = 15 + ring_i * 10
                ring_alpha = max(20, alpha // (ring_i + 1))
                pygame.draw.circle(ghost_surf, (0, 255, 120, ring_alpha), (30, 25), r, 2)
            surface.blit(ghost_surf, (gsx - 30, gsy - 70))
            plat_alpha = max(60, int(200 * (self.special_duration / self.special_duration_max)))
            plat_surf = pygame.Surface((80, 10), pygame.SRCALPHA)
            pygame.draw.rect(plat_surf, (0, 255, 150, plat_alpha), (0, 0, 80, 10))
            pygame.draw.rect(plat_surf, (0, 200, 100, plat_alpha), (0, 0, 80, 10), 2)
            surface.blit(plat_surf, (gsx - 40, gsy))


class MorXel(CharacterBase):
    """MorXel - Glitchy digital entity. Reality reboot ability."""

    def __init__(self):
        super().__init__()
        self.name = "MorXel"
        self.speed = 9
        self.jump_power = 15
        self.grip = 8
        self.install_skill = 8
        self.special_name = "REBOOT_REALITY"
        self.special_cooldown_max = 15.0
        self.special_duration_max = 4.0
        self.glitch_offset = 0
        self.frame_count = 0
        self.colors = {
            "primary_r": (255, 50, 50),
            "primary_g": (50, 255, 50),
            "primary_b": (50, 50, 255),
            "wireframe": (0, 255, 200),
            "pixel": (255, 255, 255),
            "outline": (0, 200, 180),
        }

    def activate_special(self):
        if self.special_cooldown <= 0:
            self.special_active = True
            self.special_duration = self.special_duration_max
            self.special_cooldown = self.special_cooldown_max
            return True
        return False

    def draw(self, surface, x, y, camera):
        sx, sy = camera.world_to_screen(x, y)
        self.frame_count += 1
        f = 1 if self.facing_right else -1
        glitch_r = random.randint(-2, 2) if self.frame_count % 3 == 0 else 0
        glitch_g = random.randint(-2, 2) if self.frame_count % 5 == 0 else 0
        bob = 0
        leg_phase = 0
        if self.anim_state == AnimState.RUN:
            bob = int(math.sin(self.anim_frame * 0.8) * 2)
            leg_phase = self.anim_frame * 0.8
        head_x = sx
        head_y = sy - 32 + bob
        c = self.colors
        pygame.draw.circle(surface, c["primary_r"], (head_x + glitch_r, head_y), 10)
        pygame.draw.circle(surface, c["primary_g"], (head_x + glitch_g, head_y + 1), 9)
        pygame.draw.circle(surface, c["primary_b"], (head_x, head_y - 1), 9)
        pygame.draw.circle(surface, c["wireframe"], (head_x, head_y), 10, 2)
        for wire_a in range(0, 360, 45):
            rad = math.radians(wire_a)
            wx1 = head_x + int(math.cos(rad) * 8)
            wy1 = head_y + int(math.sin(rad) * 8)
            wx2 = head_x + int(math.cos(rad + 0.5) * 10)
            wy2 = head_y + int(math.sin(rad + 0.5) * 10)
            pygame.draw.line(surface, c["wireframe"], (wx1, wy1), (wx2, wy2), 1)
        hat_color = c["wireframe"]
        pygame.draw.lines(surface, hat_color, False, [
            (head_x - 12, head_y - 8),
            (head_x - 8, head_y - 16),
            (head_x, head_y - 18),
            (head_x + 8, head_y - 16),
            (head_x + 12, head_y - 8),
        ], 2)
        pygame.draw.line(surface, hat_color, (head_x - 8, head_y - 16), (head_x + 8, head_y - 16), 1)
        pygame.draw.line(surface, hat_color, (head_x - 4, head_y - 17), (head_x + 4, head_y - 17), 1)
        eye_color_1 = (255, 0, 0) if self.frame_count % 10 < 5 else (0, 255, 0)
        eye_color_2 = (0, 0, 255) if self.frame_count % 8 < 4 else (255, 255, 0)
        pygame.draw.rect(surface, eye_color_1, (head_x - 6, head_y - 3, 4, 4))
        pygame.draw.rect(surface, eye_color_2, (head_x + 2, head_y - 3, 4, 4))
        if self.frame_count % 15 < 3:
            pygame.draw.line(surface, c["pixel"], (head_x - 3, head_y + 4), (head_x + 3, head_y + 4), 2)
        body_top = sy - 20 + bob
        body_bottom = sy - 2 + bob
        bh = body_bottom - body_top
        body_color = random.choice([c["primary_r"], c["primary_g"], c["primary_b"]])
        pygame.draw.rect(surface, body_color, (sx - 8, body_top, 16, bh))
        pygame.draw.rect(surface, c["wireframe"], (sx - 8, body_top, 16, bh), 2)
        for gy_off in range(0, bh, 4):
            if random.random() < 0.3:
                seg_x = sx - 8 + random.randint(0, 12)
                seg_w = random.randint(2, 4)
                pygame.draw.rect(surface, c["pixel"], (seg_x, body_top + gy_off, seg_w, 2))
        arm_y = body_top + 3
        arm_color = c["wireframe"]
        arm_swing = math.sin(leg_phase) * 6 if self.anim_state == AnimState.RUN else 0
        pygame.draw.line(surface, arm_color, (sx + f * 8, arm_y),
                         (sx + f * 12, arm_y + 14 + int(arm_swing)), 3)
        pygame.draw.line(surface, arm_color, (sx - f * 8, arm_y),
                         (sx - f * 12, arm_y + 14 - int(arm_swing)), 3)
        if random.random() < 0.2:
            px = sx + random.randint(-10, 10)
            py = sy + random.randint(-35, 15)
            psize = random.randint(2, 4)
            pygame.draw.rect(surface, random.choice([c["primary_r"], c["primary_g"], c["primary_b"]]),
                             (px, py, psize, psize))
        hip_y = body_bottom + bob
        leg_color = c["wireframe"]
        if self.anim_state == AnimState.RUN:
            l1 = math.sin(leg_phase) * 8
            l2 = math.sin(leg_phase + math.pi) * 8
            pygame.draw.line(surface, leg_color, (sx - 3, hip_y), (sx - 3 + int(l1), hip_y + 14), 3)
            pygame.draw.line(surface, leg_color, (sx + 3, hip_y), (sx + 3 + int(l2), hip_y + 14), 3)
            foot_col = random.choice([c["primary_r"], c["primary_g"], c["primary_b"]])
            pygame.draw.rect(surface, foot_col, (sx - 6 + int(l1), hip_y + 12, 8, 5))
            pygame.draw.rect(surface, foot_col, (sx + int(l2), hip_y + 12, 8, 5))
        else:
            pygame.draw.line(surface, leg_color, (sx - 3, hip_y), (sx - 4, hip_y + 14), 3)
            pygame.draw.line(surface, leg_color, (sx + 3, hip_y), (sx + 4, hip_y + 14), 3)
            pygame.draw.rect(surface, c["wireframe"], (sx - 7, hip_y + 12, 8, 5))
            pygame.draw.rect(surface, c["wireframe"], (sx + 1, hip_y + 12, 8, 5))

    def draw_special_effect(self, surface, x, y, camera):
        if self.special_active:
            glitch_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            num_glitches = random.randint(3, 8)
            for _ in range(num_glitches):
                gy = random.randint(0, HEIGHT)
                gh = random.randint(2, 20)
                gx_shift = random.randint(-30, 30)
                color = random.choice([(255, 0, 0, 40), (0, 255, 0, 40), (0, 0, 255, 40)])
                pygame.draw.rect(glitch_surf, color, (gx_shift, gy, WIDTH, gh))
            for _ in range(random.randint(5, 15)):
                px = random.randint(0, WIDTH)
                py = random.randint(0, HEIGHT)
                ps = random.randint(2, 8)
                pygame.draw.rect(glitch_surf, (255, 255, 255, 60), (px, py, ps, ps))
            surface.blit(glitch_surf, (0, 0))


CHARACTER_CLASSES = {
    "Rico": Rico,
    "Ing. Vero": Vero,
    "Don Aurelio": DonAurelio,
    "MorXel": MorXel,
}

CHARACTER_UNLOCK = {
    "Rico": True,
    "Ing. Vero": False,
    "Don Aurelio": False,
    "MorXel": False,
}


# ============================================================
# SECTION 8: PLAYER CLASS
# ============================================================
class Player:
    """Full player class wrapping a character with physics and input."""

    def __init__(self, character_class, x=100, y=400):
        self.character = character_class()
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = 20
        self.height = 48
        self.on_ground = False
        self.on_wall = False
        self.wall_dir = 0
        self.can_double_jump = True
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.facing_right = True
        self.sprinting = False
        self.climbing = False
        self.swinging = False
        self.current_cable = None
        self.current_pole = None
        self.lives = 3
        self.max_lives = 3
        self.health = 100
        self.score = 0
        self.invincible_timer = 0
        self.invincible_duration = 90
        self.alive = True
        self.respawn_x = x
        self.respawn_y = y
        self.anim_state = AnimState.IDLE
        self.footstep_timer = 0
        self.combo_count = 0
        self.combo_timer = 0

    def get_rect(self):
        return pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height),
                           self.width, self.height)

    def get_feet_rect(self):
        return pygame.Rect(int(self.x - self.width // 2), int(self.y - 4),
                           self.width, 8)

    def set_checkpoint(self, x, y):
        self.respawn_x = x
        self.respawn_y = y

    def take_damage(self, amount=25):
        if self.invincible_timer > 0 or not self.alive:
            return
        self.health -= amount
        self.invincible_timer = self.invincible_duration
        if self.health <= 0:
            self.die()

    def die(self):
        self.alive = False
        self.lives -= 1
        self.character.anim_state = AnimState.DEATH
        self.anim_state = AnimState.DEATH
        self.vy = JUMP_FORCE * 0.5
        self.vx = 0

    def respawn(self):
        if self.lives > 0:
            self.alive = True
            self.health = 100
            self.x = self.respawn_x
            self.y = self.respawn_y
            self.vx = 0
            self.vy = 0
            self.invincible_timer = self.invincible_duration
            self.on_ground = False
            self.climbing = False
            self.swinging = False
            self.current_cable = None
            self.current_pole = None
            self.character.anim_state = AnimState.IDLE
            self.anim_state = AnimState.IDLE

    def handle_input(self, keys):
        if not self.alive:
            return
        if self.climbing:
            self._handle_climb_input(keys)
            return
        if self.swinging:
            self._handle_swing_input(keys)
            return
        move_speed = self.character.speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.sprinting = True
            move_speed = SPRINT_SPEED
        else:
            self.sprinting = False
        accel = move_speed if self.on_ground else move_speed * AIR_CONTROL
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= accel * 0.6
            self.facing_right = False
            self.character.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += accel * 0.6
            self.facing_right = True
            self.character.facing_right = True
        else:
            if self.on_ground:
                self.vx *= 0.7  # snappier ground stop
            else:
                self.vx *= 0.92  # less air drag
        max_speed = SPRINT_SPEED if self.sprinting else move_speed
        self.vx = max(-max_speed, min(max_speed, self.vx))
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.jump_buffer_timer = JUMP_BUFFER

    def handle_key_down(self, key, platforms, cables, poles):
        if not self.alive:
            return
        if key == pygame.K_SPACE or key == pygame.K_UP or key == pygame.K_w:
            self._try_jump()
        if key == pygame.K_e:
            self._try_grab(cables, poles)
        if key == pygame.K_q:
            self.character.activate_special()
            if self.character.special_name == "SENAL_FANTASMA" and self.character.ghost_placed:
                self.character.place_ghost(self.x, self.y)

    def _try_jump(self):
        if self.climbing:
            self.climbing = False
            self.current_pole = None
            self.vy = JUMP_FORCE * 0.8
            self.vx = (-1 if self.facing_right else 1) * 5
            self.coyote_timer = 0
            return
        if self.swinging and self.current_cable:
            vx_add, vy_add = self.current_cable.detach()
            self.vx += vx_add
            self.vy += vy_add
            self.swinging = False
            self.current_cable = None
            self.can_double_jump = True
            return
        if self.on_ground or self.coyote_timer > 0:
            self.vy = JUMP_FORCE
            self.jump_buffer_timer = 0
            self.on_ground = False
            self.coyote_timer = 0
            self.can_double_jump = True
            return
        if self.on_wall:
            wall_jump_vx = -self.wall_dir * 8
            self.vx = wall_jump_vx
            self.vy = JUMP_FORCE * 0.9
            self.on_wall = False
            self.can_double_jump = True
            self.facing_right = self.wall_dir < 0
            self.character.facing_right = self.facing_right
            return
        if self.can_double_jump:
            self.vy = DOUBLE_JUMP_FORCE
            self.jump_buffer_timer = 0
            self.can_double_jump = False
            return

    def _try_grab(self, cables, poles):
        player_rect = self.get_rect()
        for cable in cables:
            grab_rect = cable.get_grab_rect()
            if player_rect.colliderect(grab_rect):
                cable.attach(self)
                self.current_cable = cable
                self.swinging = True
                self.on_ground = False
                return
        for pole in poles:
            climb_rect = pole.get_climb_rect()
            if player_rect.colliderect(climb_rect):
                self.climbing = True
                self.current_pole = pole
                self.x = pole.x
                self.vy = 0
                self.vx = 0
                return

    def _handle_climb_input(self, keys):
        climb_speed = 3.0 * (self.character.grip / 10.0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= climb_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += climb_speed
        if self.current_pole:
            pole_top = self.current_pole.rect.y
            pole_bottom = self.current_pole.rect.y + self.current_pole.rect.height
            self.y = max(pole_top + self.height, min(pole_bottom, self.y))

    def _handle_swing_input(self, keys):
        if self.current_cable:
            swing_force = 0.02
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.current_cable.angular_vel -= swing_force
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.current_cable.angular_vel += swing_force

    def update(self, platforms, cables, poles, dt=1.0):
        if not self.alive:
            self.vy += GRAVITY
            self.y += self.vy
            return
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_count = 0
        self.character.update_special(dt / FPS)
        self.character.update_animation(dt / FPS)
        if self.climbing:
            self._update_climb_state()
            return
        if self.swinging:
            if self.current_cable:
                self.current_cable.update()
            self.character.anim_state = AnimState.CABLE_SWING
            self.anim_state = AnimState.CABLE_SWING
            return
        was_on_ground = self.on_ground
        self.vy += GRAVITY
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL
        self.x += self.vx
        self.y += self.vy
        self.on_ground = False
        self.on_wall = False
        self._resolve_collisions(platforms)
        if was_on_ground and not self.on_ground:
            self.coyote_timer = COYOTE_TIME
        if self.coyote_timer > 0:
            self.coyote_timer -= 1
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
            if self.on_ground:
                self._try_jump()
                self.jump_buffer_timer = 0
        if self.on_ground:
            self.can_double_jump = True
        self._update_anim_state()
        self.footstep_triggered = self._update_footsteps()

    def _update_climb_state(self):
        self.character.anim_state = AnimState.CLIMB
        self.anim_state = AnimState.CLIMB
        if self.current_pole:
            if not self.get_rect().colliderect(self.current_pole.get_climb_rect()):
                self.climbing = False
                self.current_pole = None

    def _resolve_collisions(self, platforms):
        player_rect = self.get_rect()
        for plat in platforms:
            if isinstance(plat, FiberCable) or isinstance(plat, TelecomPole):
                continue
            prect = plat.rect if hasattr(plat, 'rect') else plat
            if not player_rect.colliderect(prect):
                continue
            overlap_x_right = player_rect.right - prect.left
            overlap_x_left = prect.right - player_rect.left
            overlap_y_bottom = player_rect.bottom - prect.top
            overlap_y_top = prect.bottom - player_rect.top
            min_overlap = min(overlap_x_right, overlap_x_left, overlap_y_bottom, overlap_y_top)
            if min_overlap == overlap_y_bottom and self.vy >= 0:
                self.y = prect.top
                self.vy = 0
                self.on_ground = True
                friction = plat.friction if hasattr(plat, 'friction') else 1.0
                self.vx *= friction
            elif min_overlap == overlap_y_top and self.vy < 0:
                self.y = prect.bottom + self.height // 2
                self.vy = 0
            elif min_overlap == overlap_x_right:
                self.x = prect.left - self.width // 2
                if self.vx > 0:
                    self.vx = 0
                if not self.on_ground and self.vy > 0:
                    self.on_wall = True
                    self.wall_dir = 1
                    self.vy = min(self.vy, WALL_SLIDE_SPEED)
            elif min_overlap == overlap_x_left:
                self.x = prect.right + self.width // 2
                if self.vx < 0:
                    self.vx = 0
                if not self.on_ground and self.vy > 0:
                    self.on_wall = True
                    self.wall_dir = -1
                    self.vy = min(self.vy, WALL_SLIDE_SPEED)
            player_rect = self.get_rect()

    def _update_anim_state(self):
        if self.on_wall:
            self.anim_state = AnimState.WALL_SLIDE
            self.character.anim_state = AnimState.WALL_SLIDE
        elif not self.on_ground:
            if self.vy < 0:
                self.anim_state = AnimState.JUMP
                self.character.anim_state = AnimState.JUMP
            else:
                self.anim_state = AnimState.FALL
                self.character.anim_state = AnimState.FALL
        elif abs(self.vx) > 0.5:
            self.anim_state = AnimState.RUN
            self.character.anim_state = AnimState.RUN
        else:
            self.anim_state = AnimState.IDLE
            self.character.anim_state = AnimState.IDLE

    def _update_footsteps(self):
        if self.on_ground and abs(self.vx) > 1.0:
            self.footstep_timer += abs(self.vx)
            if self.footstep_timer > 30:
                self.footstep_timer = 0
                return True  # signal to play footstep
        else:
            self.footstep_timer = 0
        return False

    def draw(self, surface, camera):
        if not self.alive:
            return
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        shadow_w = 16
        shadow_h = 6
        shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), (0, 0, shadow_w * 2, shadow_h * 2))
        surface.blit(shadow_surf, (sx - shadow_w, sy - shadow_h // 2))
        self.character.draw(surface, self.x, self.y, camera)
        if hasattr(self.character, 'draw_special_effect'):
            self.character.draw_special_effect(surface, self.x, self.y, camera)


# ============================================================
# SECTION 9: DIALOG SYSTEM
# ============================================================
DIALOG_LIBRARY = {
    "Rico": {
        "cable_swing": [
            "Otro dia, otro poste...",
            "Si me caigo, culpo a la gravedad!",
            "Tarzan no tenia que lidiar con fibra optica",
        ],
        "rain": [
            "Lluvia y postes... combinacion ganadora",
            "Al menos no hay rayos... todavia",
            "Mi contrato no dice nada de trabajar mojado",
        ],
        "competitor_seen": [
            "Mira, Telmex. Que andan haciendo aqui?",
            "ATT otra vez? No tienen sus propios postes?",
            "Competencia... como si sus cables no se cayeran solos",
        ],
        "bad_signal": [
            "Esta senal esta mas perdida que yo los lunes",
            "Ni con antena de 3 metros levanto esto",
            "Houston, tenemos un problema de dBm",
        ],
        "excellent_signal": [
            "Eso! Senal perfecta, como yo",
            "Excelente! Hasta se me quito el hambre",
            "Senal full barras, vamos a celebrar!",
        ],
        "death": [
            "Ayyy... eso dolio",
            "Nota mental: no hacer eso otra vez",
            "Mi seguro de vida no cubre esto...",
        ],
        "random_quip": [
            "Me pregunto si pagan horas extra...",
            "Deberia haber sido programador",
            "Un taco no estaria mal ahorita",
            "Alguien vio mi desarmador?",
        ],
        "install_start": [
            "A darle, que la antena no se instala sola",
            "Veamos que tal la senal aqui arriba",
        ],
        "install_complete": [
            "Listo! Otro cliente feliz... o al menos conectado",
            "Instalacion completa, siguiente!",
        ],
        "npc_interact": [
            "Si senor, ya le llega el WiFi",
            "No, el router no va en el bano",
        ],
        "boss_encounter": [
            "Esto se puso serio...",
            "Ora si, a darle con todo!",
        ],
    },
    "Ing. Vero": {
        "cable_swing": [
            "Los parametros de tension estan dentro del rango",
            "Esto no es lo que estudie en la universidad...",
            "La fisica del pendulo aplica aqui, interesante",
        ],
        "rain": [
            "Humedad relativa alta, riesgo de interferencia",
            "Los parametros estan fuera de rango... otra vez",
            "Necesito recalibrar despues de esta lluvia",
        ],
        "competitor_seen": [
            "Su infraestructura es obsoleta, no me preocupa",
            "Datos muestran que su latencia es inaceptable",
            "Interesante estrategia... ineficiente, pero interesante",
        ],
        "bad_signal": [
            "SNR inaceptable. Hay interferencia co-canal",
            "Necesitamos un analisis espectral completo",
            "Los numeros no mienten: esta senal es basura",
        ],
        "excellent_signal": [
            "-55 dBm! Esto es lo que llamo ingenieria",
            "Parametros optimos confirmados",
            "Perfecto. Documentando para el reporte",
        ],
        "death": [
            "Error de calculo...",
            "Estadisticamente esto no debia pasar",
            "Necesito revisar mis procedimientos",
        ],
        "random_quip": [
            "Segun mis calculos, falta el 63% del recorrido",
            "La eficiencia de este proceso es cuestionable",
            "Me falta mi cafe para funcionar al 100%",
        ],
        "install_start": [
            "Iniciando protocolo de instalacion",
            "Verificando parametros de la antena...",
        ],
        "install_complete": [
            "Instalacion verificada y documentada",
            "QoS confirmado dentro de parametros",
        ],
        "npc_interact": [
            "La velocidad depende de multiples factores, senor",
            "Le explico: el ancho de banda no es lo mismo que velocidad",
        ],
        "boss_encounter": [
            "Analizando debilidades del objetivo...",
            "Los datos dicen que puedo ganar. Probablemente.",
        ],
    },
    "Don Aurelio": {
        "cable_swing": [
            "En mis tiempos esto se hacia con puro alambre, *burp*",
            "Yo hacia esto antes de que inventaran el Internet",
            "Bah, fibra optica... el cobre era mejor",
        ],
        "rain": [
            "He trabajado en peores condiciones, *burp*",
            "La lluvia no me asusta. Los impuestos si",
            "Antes subiamos los postes bajo tormenta y sin quejarnos",
        ],
        "competitor_seen": [
            "Esos payasos otra vez? Les gano con los ojos cerrados",
            "Telmex? Yo les ensenaba a ellos cuando empezaron",
            "Mira nomas, *burp*, amateurs",
        ],
        "bad_signal": [
            "He visto senales peores en el 95, esto no es nada",
            "Con un walkie y huevos se arregla todo, *burp*",
            "La senal esta mal? Dame un alambre y ya veras",
        ],
        "excellent_signal": [
            "Asi se hace! La vieja escuela no falla",
            "Perfecto, como mis instalaciones del 97",
            "Ven? La experiencia vale mas que el titulo, *burp*",
        ],
        "death": [
            "Ya no estoy para estos trotes...",
            "En mis tiempos... ay, me dolio",
            "Necesito un descanso... y un tequila",
        ],
        "random_quip": [
            "Estos chamacos no saben ni agarrar un desarmador",
            "*burp* ...donde deje mi herramienta?",
            "Llevo 30 anos en esto y cada dia es mas raro",
            "Antes no habia GPS, nos guiabamos con las estrellas y los postes",
        ],
        "install_start": [
            "Dejame ensenarte como se hace de verdad",
            "Una antena mas, ya perdi la cuenta",
        ],
        "install_complete": [
            "Listo, asi se hacia antes y asi se sigue haciendo",
            "Otro trabajo bien hecho, *burp*, como siempre",
        ],
        "npc_interact": [
            "Mire senora, en mis tiempos ni habia WiFi",
            "4K? Antes veiamos en blanco y negro y eramos felices",
        ],
        "boss_encounter": [
            "No me importa quien seas, he visto cosas peores *burp*",
            "Alla voy... esto me recuerda al 92",
        ],
    },
    "MorXel": {
        "cable_swing": [
            "SENAL//DETECTADA... o era un taco? BUFFER OVERFLOW de hambre",
            "SIMULANDO FISICA... resultados: divertido",
            "PENDULUM.EXE ejecutado con exito... mas o menos",
        ],
        "rain": [
            "AGUA DETECTADA... iniciando protocolo paraguas.dll NOT FOUND",
            "PRECAUCION: liquido no compatible con hardware",
            "RAIN.SYS: error 404, sol no encontrado",
        ],
        "competitor_seen": [
            "ENTIDAD HOSTIL... o amigable? CLASIFICACION: confuso",
            "ESCANEANDO... su firmware esta desactualizado jajaja",
            "COMPETITOR.EXE tiene un virus... de mediocridad",
        ],
        "bad_signal": [
            "SENAL: -85dBm... eso es peor que mi autoestima.log",
            "ERROR: senal tan baja que me da tristeza artificial",
            "DIAGNOSTICO: esto necesita un milagro.exe",
        ],
        "excellent_signal": [
            "SENAL OPTIMA! mi felicidad.bat se ejecuta correctamente",
            "EXCELENTE! compilando alegria... sin errores!",
            "PERFECTA CONEXION... como yo con los tacos",
        ],
        "death": [
            "FATAL EXCEPTION: existencia interrumpida",
            "BLUE SCREEN OF DEATH... literalmente",
            "REINICIANDO... porfavor espere 3... 2... ERROR",
        ],
        "random_quip": [
            "PENSAMIENTOS RANDOM: las nubes son el backup del oceano?",
            "EJECUTANDO existencialismo.py... resultado: indefinido",
            "SOY REAL O SOY UN NPC? pregunta sin respuesta.txt",
            "HAMBRE DETECTADA... pero no tengo estomago. PARADOJA",
        ],
        "install_start": [
            "INICIANDO install_antena.sh con sudo",
            "ACCEDIENDO hardware fisico... esto es raro",
        ],
        "install_complete": [
            "INSTALACION COMPLETA! commit y push exitoso",
            "DEPLOY exitoso! cero bugs... probablemente",
        ],
        "npc_interact": [
            "HUMANO DETECTADO... interaccion social.dll cargando...",
            "SI//NO//QUIZAS... respuesta optima calculada: asiente y sonrie",
        ],
        "boss_encounter": [
            "AMENAZA NIVEL: alto. MIEDO NIVEL: tambien alto",
            "CARGANDO valentía.exe... archivo corrupto. Igual le entro.",
        ],
    },
}


class SpeechBubble:
    """A floating speech bubble with text."""

    def __init__(self, text, speaker_x, speaker_y, bubble_type=BubbleType.SPEECH, duration=3.0):
        self.text = text
        self.speaker_x = speaker_x
        self.speaker_y = speaker_y
        self.bubble_type = bubble_type
        self.duration = duration
        self.timer = duration
        self.font = None
        self.visible = True

    def update(self, dt, speaker_x=None, speaker_y=None):
        if speaker_x is not None:
            self.speaker_x = speaker_x
        if speaker_y is not None:
            self.speaker_y = speaker_y
        self.timer -= dt
        if self.timer <= 0:
            self.visible = False

    def draw(self, surface, camera):
        if not self.visible:
            return
        if self.font is None:
            self.font = pygame.font.Font(None, 20)
        sx, sy = camera.world_to_screen(self.speaker_x, self.speaker_y)
        text_surface = self.font.render(self.text, True, WHITE)
        tw = text_surface.get_width()
        th = text_surface.get_height()
        pad = 8
        bw = tw + pad * 2
        bh = th + pad * 2
        bx = sx - bw // 2
        by = sy - 70
        if bx < 5:
            bx = 5
        if bx + bw > WIDTH - 5:
            bx = WIDTH - bw - 5
        if by < 5:
            by = 5
        bubble_surf = pygame.Surface((bw + 4, bh + 4), pygame.SRCALPHA)
        alpha = min(255, int(255 * min(1.0, self.timer / 0.5)))
        if self.bubble_type == BubbleType.SPEECH:
            pygame.draw.rect(bubble_surf, (*DIALOG_BG, alpha), (2, 2, bw, bh), border_radius=6)
            pygame.draw.rect(bubble_surf, (*DIALOG_BORDER, alpha), (2, 2, bw, bh), 2, border_radius=6)
            tail_pts = [(bw // 2 - 4 + 2, bh + 2), (bw // 2 + 2, bh + 12), (bw // 2 + 4 + 2, bh + 2)]
            pygame.draw.polygon(bubble_surf, (*DIALOG_BG, alpha), tail_pts)
            pygame.draw.lines(bubble_surf, (*DIALOG_BORDER, alpha), False, tail_pts, 2)
        elif self.bubble_type == BubbleType.THOUGHT:
            pygame.draw.ellipse(bubble_surf, (*DIALOG_BG, alpha), (2, 2, bw, bh))
            pygame.draw.ellipse(bubble_surf, (*DIALOG_BORDER, alpha), (2, 2, bw, bh), 2)
            cx = bw // 2 + 2
            pygame.draw.circle(bubble_surf, (*DIALOG_BG, alpha), (cx, bh + 6), 4)
            pygame.draw.circle(bubble_surf, (*DIALOG_BORDER, alpha), (cx, bh + 6), 4, 1)
            pygame.draw.circle(bubble_surf, (*DIALOG_BG, alpha), (cx + 3, bh + 12), 3)
            pygame.draw.circle(bubble_surf, (*DIALOG_BORDER, alpha), (cx + 3, bh + 12), 3, 1)
        elif self.bubble_type == BubbleType.SHOUT:
            spike_points = []
            num_spikes = 12
            for i in range(num_spikes):
                angle = 2 * math.pi * i / num_spikes
                r_inner = min(bw, bh) // 2
                r_outer = r_inner + 8
                r = r_outer if i % 2 == 0 else r_inner
                px = bw // 2 + 2 + int(math.cos(angle) * r * bw / max(bw, bh))
                py = bh // 2 + 2 + int(math.sin(angle) * r * bh / max(bw, bh))
                spike_points.append((px, py))
            if len(spike_points) >= 3:
                pygame.draw.polygon(bubble_surf, (*DIALOG_BG, alpha), spike_points)
                pygame.draw.polygon(bubble_surf, (*DIALOG_BORDER, alpha), spike_points, 2)
        elif self.bubble_type == BubbleType.RADIO:
            pygame.draw.rect(bubble_surf, (*DIALOG_BG, alpha), (2, 2, bw, bh), border_radius=4)
            dash_len = 6
            gap_len = 4
            perimeter_points = []
            for edge_x in range(0, bw, dash_len + gap_len):
                pygame.draw.line(bubble_surf, (*DIALOG_BORDER, alpha),
                                 (edge_x + 2, 2), (min(edge_x + dash_len + 2, bw + 2), 2), 2)
                pygame.draw.line(bubble_surf, (*DIALOG_BORDER, alpha),
                                 (edge_x + 2, bh + 2), (min(edge_x + dash_len + 2, bw + 2), bh + 2), 2)
            for edge_y in range(0, bh, dash_len + gap_len):
                pygame.draw.line(bubble_surf, (*DIALOG_BORDER, alpha),
                                 (2, edge_y + 2), (2, min(edge_y + dash_len + 2, bh + 2)), 2)
                pygame.draw.line(bubble_surf, (*DIALOG_BORDER, alpha),
                                 (bw + 2, edge_y + 2), (bw + 2, min(edge_y + dash_len + 2, bh + 2)), 2)
        text_alpha_surf = text_surface.copy()
        text_alpha_surf.set_alpha(alpha)
        bubble_surf.blit(text_alpha_surf, (pad + 2, pad + 2))
        surface.blit(bubble_surf, (bx - 2, by - 2))


class DialogManager:
    """Manages dialog queue and triggers."""

    def __init__(self):
        self.active_bubble = None
        self.queue = []
        self.random_timer = random.uniform(8.0, 20.0)
        self.last_situation = ""

    def trigger(self, character_name, situation, x, y, bubble_type=BubbleType.SPEECH):
        if self.active_bubble and self.active_bubble.visible:
            if situation == self.last_situation:
                return
        lines = DIALOG_LIBRARY.get(character_name, {}).get(situation, [])
        if lines:
            text = random.choice(lines)
            duration = max(2.0, len(text) * 0.06)
            self.active_bubble = SpeechBubble(text, x, y, bubble_type, duration)
            self.last_situation = situation

    def queue_dialog(self, character_name, situation, x, y, bubble_type=BubbleType.SPEECH):
        lines = DIALOG_LIBRARY.get(character_name, {}).get(situation, [])
        if lines:
            self.queue.append((random.choice(lines), x, y, bubble_type))

    def update(self, dt, player=None):
        if self.active_bubble:
            if player:
                self.active_bubble.update(dt, player.x, player.y - 20)
            else:
                self.active_bubble.update(dt)
            if not self.active_bubble.visible:
                self.active_bubble = None
                if self.queue:
                    text, qx, qy, bt = self.queue.pop(0)
                    duration = max(2.0, len(text) * 0.06)
                    self.active_bubble = SpeechBubble(text, qx, qy, bt, duration)
        if player and player.alive:
            self.random_timer -= dt
            if self.random_timer <= 0:
                self.random_timer = random.uniform(10.0, 25.0)
                if not self.active_bubble:
                    self.trigger(player.character.name, "random_quip", player.x, player.y)

    def draw(self, surface, camera):
        if self.active_bubble and self.active_bubble.visible:
            self.active_bubble.draw(surface, camera)


# ============================================================
# SECTION 10: OBSTACLES
# ============================================================
class WeatherSystem:
    """Dynamic weather with rain, lightning, heat shimmer, and wind."""

    def __init__(self):
        self.raining = False
        self.rain_intensity = 0.0
        self.target_rain = 0.0
        self.lightning_timer = 0.0
        self.lightning_flash = 0
        self.thunder_delay = 0.0
        self.thunder_pending = False
        self.wind_speed = 0.0
        self.wind_target = 0.0
        self.heat_shimmer = False
        self.shimmer_phase = 0.0
        self.particles = ParticleSystem()
        self.dark_overlay_alpha = 0

    def set_rain(self, intensity):
        self.target_rain = max(0.0, min(1.0, intensity))
        self.raining = intensity > 0

    def set_heat(self, active):
        self.heat_shimmer = active

    def set_wind(self, speed):
        self.wind_target = speed

    def update(self, dt, camera):
        if self.rain_intensity < self.target_rain:
            self.rain_intensity = min(self.target_rain, self.rain_intensity + 0.01)
        elif self.rain_intensity > self.target_rain:
            self.rain_intensity = max(self.target_rain, self.rain_intensity - 0.01)
        if self.rain_intensity > 0.1:
            count = int(self.rain_intensity * 15)
            self.particles.emit_rain(camera.x + WIDTH // 2, camera.y, count)
        if self.rain_intensity > 0.5:
            self.lightning_timer -= dt
            if self.lightning_timer <= 0:
                self.lightning_flash = 8
                self.thunder_delay = random.uniform(0.3, 1.5)
                self.thunder_pending = True
                self.lightning_timer = random.uniform(5.0, 15.0)
        if self.lightning_flash > 0:
            self.lightning_flash -= 1
        if self.thunder_pending:
            self.thunder_delay -= dt
            if self.thunder_delay <= 0:
                self.thunder_pending = False
        self.wind_speed += (self.wind_target - self.wind_speed) * 0.02
        if self.heat_shimmer:
            self.shimmer_phase += 0.03
        self.dark_overlay_alpha = int(self.rain_intensity * 60)
        self.particles.update(dt)

    def apply_to_player(self, player):
        if abs(self.wind_speed) > 0.1:
            player.vx += self.wind_speed * 0.1
        if self.lightning_flash == 7:
            if random.random() < 0.1:
                player.vx *= 0.3
                player.vy = 0

    def draw(self, surface, camera):
        self.particles.draw(surface, camera)
        if self.dark_overlay_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 30, self.dark_overlay_alpha), (0, 0, WIDTH, HEIGHT))
            surface.blit(overlay, (0, 0))
        if self.lightning_flash > 0:
            flash_alpha = self.lightning_flash * 30
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(flash, (255, 255, 255, min(255, flash_alpha)), (0, 0, WIDTH, HEIGHT))
            surface.blit(flash, (0, 0))
        if self.heat_shimmer:
            for hy in range(0, HEIGHT, 40):
                offset = int(math.sin(self.shimmer_phase + hy * 0.05) * 2)
                if 0 < hy < HEIGHT - 2:
                    strip = surface.subsurface((0, hy, WIDTH, min(2, HEIGHT - hy))).copy()
                    surface.blit(strip, (offset, hy))

    def draw_wind_particles(self, surface, camera):
        if abs(self.wind_speed) > 1.0:
            for _ in range(int(abs(self.wind_speed))):
                px = random.randint(0, WIDTH)
                py = random.randint(0, HEIGHT)
                wind_len = int(abs(self.wind_speed) * 8)
                wind_dir = 1 if self.wind_speed > 0 else -1
                color = (200, 200, 200, 80)
                end_x = px + wind_dir * wind_len
                pygame.draw.line(surface, (200, 200, 200), (px, py), (end_x, py), 1)


class Competitor:
    """Competitor truck entity (Telmex/ATT/Claro)."""

    def __init__(self, x, y, brand="Telmex"):
        self.x = float(x)
        self.y = float(y)
        self.brand = brand
        self.width = 80
        self.height = 50
        self.speed = 2.0
        self.direction = 1
        self.patrol_left = x - 200
        self.patrol_right = x + 200
        self.flash_timer = 0
        self.blocking = False
        if brand == "Telmex":
            self.color = (0, 80, 180)
            self.accent = (0, 120, 220)
        elif brand == "ATT":
            self.color = (0, 160, 220)
            self.accent = (0, 200, 255)
        else:
            self.color = (200, 30, 30)
            self.accent = (255, 50, 50)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y - self.height), self.width, self.height)

    def update(self, dt):
        self.x += self.speed * self.direction
        if self.x <= self.patrol_left:
            self.direction = 1
        elif self.x >= self.patrol_right:
            self.direction = -1
        self.flash_timer += dt * 5
        if self.flash_timer > 2 * math.pi:
            self.flash_timer -= 2 * math.pi

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(int(self.x), int(self.y))
        if sx > WIDTH + 100 or sx + self.width < -100:
            return
        truck_y = sy - self.height
        body_rect = (sx + 5, truck_y + 10, self.width - 10, self.height - 20)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=4)
        pygame.draw.rect(surface, (30, 30, 30), body_rect, 2, border_radius=4)
        cab_w = 25
        cab_x = sx + (self.width - cab_w - 5 if self.direction > 0 else 5)
        cab_rect = (cab_x, truck_y + 5, cab_w, self.height - 15)
        pygame.draw.rect(surface, self.accent, cab_rect, border_radius=3)
        pygame.draw.rect(surface, (30, 30, 30), cab_rect, 2, border_radius=3)
        win_x = cab_x + 3
        win_y = truck_y + 8
        pygame.draw.rect(surface, (180, 220, 240), (win_x, win_y, cab_w - 6, 12), border_radius=2)
        pygame.draw.rect(surface, (30, 30, 30), (win_x, win_y, cab_w - 6, 12), 1, border_radius=2)
        font = pygame.font.Font(None, 16)
        brand_text = font.render(self.brand, True, WHITE)
        text_x = sx + self.width // 2 - brand_text.get_width() // 2
        text_y = truck_y + self.height // 2 - brand_text.get_height() // 2 + 2
        surface.blit(brand_text, (text_x, text_y))
        wheel_y = sy - 5
        wheel_r = 7
        pygame.draw.circle(surface, (40, 40, 40), (sx + 15, wheel_y), wheel_r)
        pygame.draw.circle(surface, (80, 80, 80), (sx + 15, wheel_y), wheel_r - 2)
        pygame.draw.circle(surface, (40, 40, 40), (sx + self.width - 15, wheel_y), wheel_r)
        pygame.draw.circle(surface, (80, 80, 80), (sx + self.width - 15, wheel_y), wheel_r - 2)
        flash_on = math.sin(self.flash_timer) > 0
        if flash_on:
            light_color = (255, 180, 0)
        else:
            light_color = (255, 80, 0)
        light_x = cab_x + cab_w // 2
        pygame.draw.circle(surface, light_color, (light_x, truck_y + 3), 4)
        pygame.draw.circle(surface, (255, 255, 200), (light_x, truck_y + 3), 2)
        worker_x = cab_x + cab_w // 2
        worker_y = truck_y + 12
        pygame.draw.circle(surface, (210, 180, 140), (worker_x, worker_y), 4)
        pygame.draw.rect(surface, (200, 200, 50), (worker_x - 4, worker_y - 6, 8, 4))


class RFJammer:
    """Stationary RF jammer obstacle with pulsing aura."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.health = 3
        self.alive = True
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.effect_radius = 150
        self.frozen = False
        self.freeze_timer = 0.0

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height,
                           self.width, self.height)

    def get_stomp_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height - 5,
                           self.width, 10)

    def hit(self):
        if self.frozen:
            self.health -= 2
        else:
            self.health -= 1
        if self.health <= 0:
            self.alive = False

    def freeze(self, duration=3.0):
        self.frozen = True
        self.freeze_timer = duration

    def is_in_range(self, px, py):
        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < self.effect_radius

    def get_signal_penalty(self, px, py):
        dx = px - self.x
        dy = py - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist >= self.effect_radius:
            return 0.0
        return (1.0 - dist / self.effect_radius) * 20.0

    def update(self, dt):
        if not self.alive:
            return
        self.pulse_phase += 0.06
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sx < -100 or sx > WIDTH + 100:
            return
        box_x = sx - self.width // 2
        box_y = sy - self.height
        box_color = (80, 80, 90) if not self.frozen else (100, 150, 200)
        pygame.draw.rect(surface, box_color, (box_x, box_y, self.width, self.height), border_radius=3)
        pygame.draw.rect(surface, (50, 50, 60), (box_x, box_y, self.width, self.height), 2, border_radius=3)
        for vent_i in range(3):
            vy_line = box_y + 8 + vent_i * 8
            pygame.draw.line(surface, (40, 40, 50), (box_x + 4, vy_line), (box_x + self.width - 4, vy_line), 1)
        antenna_x = sx
        antenna_y = box_y - 15
        pygame.draw.line(surface, (120, 120, 130), (antenna_x, box_y), (antenna_x, antenna_y), 3)
        pygame.draw.circle(surface, SIGNAL_BAD, (antenna_x, antenna_y), 4)
        pygame.draw.circle(surface, (200, 30, 30), (antenna_x, antenna_y), 4, 1)
        if not self.frozen:
            num_rings = 3
            for ring_i in range(num_rings):
                ring_phase = self.pulse_phase + ring_i * (2 * math.pi / num_rings)
                ring_r = 20 + int(math.sin(ring_phase) * 10 + ring_i * 15)
                ring_alpha = max(30, int(150 - ring_i * 40 - abs(math.sin(ring_phase)) * 50))
                ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (255, 50, 50, ring_alpha), (ring_r + 2, ring_r + 2), ring_r, 2)
                surface.blit(ring_surf, (antenna_x - ring_r - 2, antenna_y - ring_r - 2))
        else:
            ice_color = (150, 200, 255)
            for ic in range(4):
                ix = box_x + random.randint(0, self.width)
                iy = box_y + random.randint(0, self.height)
                pygame.draw.polygon(surface, ice_color,
                                    [(ix, iy - 4), (ix + 3, iy), (ix, iy + 4), (ix - 3, iy)])
        for hi in range(self.health):
            hx = box_x + 5 + hi * 10
            hy = box_y + self.height - 8
            pygame.draw.rect(surface, (200, 50, 50), (hx, hy, 6, 4))


# ============================================================
# SECTION 11: ANTENNA INSTALLATION MINIGAME
# ============================================================
class InstallationMinigame:
    """Antenna installation minigame with signal meter."""

    def __init__(self, install_skill=6):
        self.active = False
        self.signal_dbm = -70.0
        self.signal_phase = random.uniform(0, math.pi * 2)
        self.signal_speed = 0.05
        self.noise_amount = 5.0
        self.locked = False
        self.locked_dbm = 0.0
        self.result = None
        self.result_timer = 0.0
        self.install_skill = install_skill
        self.bar_fill = 0.0
        self.oscillation_amp = 20.0 - install_skill * 0.8
        self.oscillation_speed = 0.03 + (10 - install_skill) * 0.005
        self.font_large = None
        self.font_small = None

    def start(self, install_skill=6, jammer_penalty=0.0):
        self.active = True
        self.locked = False
        self.result = None
        self.result_timer = 0.0
        self.install_skill = install_skill
        self.oscillation_amp = 20.0 - install_skill * 0.8 + jammer_penalty
        self.oscillation_speed = 0.03 + (10 - install_skill) * 0.005
        self.signal_phase = random.uniform(0, math.pi * 2)
        self.bar_fill = 0.0
        self.noise_amount = 5.0 + jammer_penalty * 0.5

    def lock_signal(self):
        if not self.locked and self.active:
            self.locked = True
            self.locked_dbm = self.signal_dbm
            if self.locked_dbm >= -65:
                self.result = "EXCELLENT"
            elif self.locked_dbm >= -75:
                self.result = "GOOD"
            else:
                self.result = "WEAK"
            self.result_timer = 2.0
            return self.result
        return None

    def update(self, dt):
        if not self.active:
            return
        if not self.locked:
            self.signal_phase += self.oscillation_speed
            base = -70.0
            oscillation = math.sin(self.signal_phase) * self.oscillation_amp
            noise = random.uniform(-self.noise_amount, self.noise_amount)
            self.signal_dbm = base + oscillation + noise
            self.signal_dbm = max(-90.0, min(-50.0, self.signal_dbm))
            norm = (self.signal_dbm - (-90)) / ((-50) - (-90))
            self.bar_fill = max(0.0, min(1.0, norm))
        else:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.active = False

    def get_score(self):
        if self.result == "EXCELLENT":
            return INSTALL_EXCELLENT
        elif self.result == "GOOD":
            return INSTALL_GOOD
        return 50

    def draw(self, surface):
        if not self.active:
            return
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 160), (0, 0, WIDTH, HEIGHT))
        surface.blit(overlay, (0, 0))
        panel_w = 500
        panel_h = 300
        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = HEIGHT // 2 - panel_h // 2
        pygame.draw.rect(surface, DIALOG_BG, (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(surface, DIALOG_BORDER, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=10)
        title_text = self.font_large.render(t("signal_strength"), True, WHITE)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, panel_y + 15))
        meter_x = panel_x + 50
        meter_y = panel_y + 60
        meter_w = panel_w - 100
        meter_h = 40
        pygame.draw.rect(surface, (30, 30, 40), (meter_x, meter_y, meter_w, meter_h), border_radius=5)
        pygame.draw.rect(surface, (60, 60, 70), (meter_x, meter_y, meter_w, meter_h), 2, border_radius=5)
        fill_w = int(meter_w * self.bar_fill)
        if self.bar_fill > 0.625:
            bar_color = SIGNAL_GOOD
        elif self.bar_fill > 0.375:
            bar_color = YELLOW
        else:
            bar_color = SIGNAL_BAD
        if fill_w > 0:
            pygame.draw.rect(surface, bar_color, (meter_x + 2, meter_y + 2, fill_w - 4, meter_h - 4),
                             border_radius=4)
        excellent_x = meter_x + int(meter_w * 0.625)
        good_x = meter_x + int(meter_w * 0.375)
        pygame.draw.line(surface, (100, 255, 100), (excellent_x, meter_y - 5),
                         (excellent_x, meter_y + meter_h + 5), 2)
        pygame.draw.line(surface, (255, 255, 100), (good_x, meter_y - 5),
                         (good_x, meter_y + meter_h + 5), 2)
        dbm_text = self.font_small.render(f"{self.signal_dbm:.1f} dBm", True, WHITE)
        surface.blit(dbm_text, (WIDTH // 2 - dbm_text.get_width() // 2, meter_y + meter_h + 10))
        label_font = pygame.font.Font(None, 18)
        labels = [("-90", 0.0), ("-75", 0.375), ("-65", 0.625), ("-50", 1.0)]
        for label_text, frac in labels:
            lx = meter_x + int(meter_w * frac)
            lt = label_font.render(label_text, True, GRAY)
            surface.blit(lt, (lx - lt.get_width() // 2, meter_y + meter_h + 30))
        needle_x = meter_x + int(meter_w * self.bar_fill)
        pygame.draw.polygon(surface, WHITE,
                            [(needle_x, meter_y - 8), (needle_x - 4, meter_y - 14),
                             (needle_x + 4, meter_y - 14)])
        bars_y = panel_y + 160
        bars_x = panel_x + 80
        num_bars = 5
        bar_w_each = 30
        bar_gap = 15
        for i in range(num_bars):
            bx = bars_x + i * (bar_w_each + bar_gap)
            bh_max = 20 + i * 15
            threshold = (i + 1) / num_bars
            if self.bar_fill >= threshold:
                bc = SIGNAL_GOOD
            elif self.bar_fill >= threshold - 0.15:
                bc = YELLOW
            else:
                bc = (60, 60, 70)
            by = bars_y + (80 - bh_max)
            pygame.draw.rect(surface, bc, (bx, by, bar_w_each, bh_max), border_radius=3)
            pygame.draw.rect(surface, (100, 100, 110), (bx, by, bar_w_each, bh_max), 2, border_radius=3)
        if not self.locked:
            prompt = self.font_small.render(t("press_space_lock"), True, DIALOG_BORDER)
            surface.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, panel_y + panel_h - 40))
        else:
            if self.result == "EXCELLENT":
                result_color = SIGNAL_GOOD
                result_text = t("excellent")
            elif self.result == "GOOD":
                result_color = YELLOW
                result_text = t("good")
            else:
                result_color = SIGNAL_BAD
                result_text = t("weak")
            result_surf = self.font_large.render(result_text, True, result_color)
            rx = WIDTH // 2 - result_surf.get_width() // 2
            ry = panel_y + panel_h - 60
            surface.blit(result_surf, (rx, ry))
            score_text = self.font_small.render(f"+{self.get_score()}", True, result_color)
            surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, ry + 35))


# ============================================================
# SECTION 12: NPC CLIENTS
# ============================================================
NPC_LINES = [
    "YouTube no carga en 4K!",
    "Puede venir ahorita? Son las 11:47pm",
    "Mi vecino tiene mejor senal, lo vi en Facebook",
    "El WiFi llega al bano? Es importante",
    "Antes pagaba menos y tenia... bueno, lo mismo, pero me quejo igual",
    "Cuando van a poner fibra? Llevo 3 anos preguntando",
    "Mi hijo dice que necesita 1 Gbps para Fortnite",
    "La antena esa no da cancer, verdad?",
    "Se me cae el Zoom cada 5 minutos!",
    "Quiero velocidad de 100 megas pero pagar plan de 10",
    "Mi router se reinicia solo a las 3am",
    "El Internet se pone lento cuando llueve, por que?",
    "Pueden poner la antena donde no se vea? Es que es fea",
    "Mi cunado dice que las antenas espantan a las palomas",
    "Netflix dice que mi conexion es lenta, sera?",
    "El vecino se roba mi WiFi, pueden ponerle seguridad?",
    "Por que no me llegan los 100 megas por WiFi si mi plan es de 100?",
    "Oiga, y si pongo papel aluminio en el router?",
    "Mi nieto dice que necesitamos mesh, que es eso?",
    "Se puede conectar la lavadora al WiFi?",
    "A que hora es mas rapido el Internet?",
    "Pueden venir el domingo a las 7am?",
    "La senal no llega al cuarto del fondo, el de 50 metros",
    "Mi perro le ladra al router, sera la radiacion?",
    "Quiero Internet sin cables, sin antena y sin pagar",
]


class NPCClient:
    """NPC client that appears near install points with dialog."""

    def __init__(self, x, y, in_window=False):
        self.x = x
        self.y = y
        self.in_window = in_window
        self.line = random.choice(NPC_LINES)
        self.skin_color = random.choice([
            (210, 180, 140), (180, 140, 100), (230, 200, 170),
            (160, 120, 80), (200, 170, 130), (240, 220, 200),
        ])
        self.shirt_color = random.choice([
            (200, 50, 50), (50, 50, 200), (50, 180, 50),
            (200, 200, 50), (200, 100, 50), (150, 50, 200),
            (50, 200, 200), (200, 100, 150),
        ])
        self.pants_color = random.choice([
            (40, 40, 80), (80, 80, 40), (60, 60, 60), (100, 70, 40),
        ])
        self.hair_color = random.choice([
            (30, 20, 10), (80, 50, 20), (150, 100, 50),
            (20, 20, 20), (60, 60, 60),
        ])
        self.has_spoken = False
        self.speak_distance = 80
        self.bubble = None
        self.wave_phase = random.uniform(0, math.pi * 2)
        self.hair_style = random.choice(["short", "long", "bald", "spiky"])

    def check_proximity(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < self.speak_distance and not self.has_spoken:
            self.has_spoken = True
            self.bubble = SpeechBubble(self.line, self.x, self.y - 30, BubbleType.SPEECH, 4.0)
            return True
        return False

    def reset_dialog(self):
        self.has_spoken = False
        self.line = random.choice(NPC_LINES)

    def update(self, dt):
        self.wave_phase += 0.03
        if self.bubble:
            self.bubble.update(dt, self.x, self.y - 30)
            if not self.bubble.visible:
                self.bubble = None

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sx < -60 or sx > WIDTH + 60:
            return
        if self.in_window:
            self._draw_in_window(surface, sx, sy)
        else:
            self._draw_on_roof(surface, sx, sy)
        if self.bubble:
            self.bubble.draw(surface, camera)

    def _draw_on_roof(self, surface, sx, sy):
        outline = (30, 30, 30)
        head_y = sy - 36
        arm_wave = math.sin(self.wave_phase) * 4
        pygame.draw.circle(surface, self.skin_color, (sx, head_y), 8)
        pygame.draw.circle(surface, outline, (sx, head_y), 8, 2)
        if self.hair_style == "short":
            pygame.draw.arc(surface, self.hair_color, (sx - 8, head_y - 10, 16, 12), 0, math.pi, 4)
        elif self.hair_style == "long":
            pygame.draw.arc(surface, self.hair_color, (sx - 8, head_y - 10, 16, 12), 0, math.pi, 4)
            pygame.draw.line(surface, self.hair_color, (sx - 7, head_y), (sx - 9, head_y + 10), 3)
            pygame.draw.line(surface, self.hair_color, (sx + 7, head_y), (sx + 9, head_y + 10), 3)
        elif self.hair_style == "spiky":
            for spike in range(5):
                sa = math.pi * 0.3 + spike * math.pi * 0.1
                pygame.draw.line(surface, self.hair_color,
                                 (sx + int(math.cos(sa) * 6), head_y + int(math.sin(sa) * 6)),
                                 (sx + int(math.cos(sa) * 12), head_y + int(math.sin(sa) * 12) - 4), 2)
        pygame.draw.circle(surface, outline, (sx - 3, head_y - 1), 2)
        pygame.draw.circle(surface, outline, (sx + 3, head_y - 1), 2)
        pygame.draw.line(surface, outline, (sx - 2, head_y + 3), (sx + 2, head_y + 3), 1)
        body_top = sy - 26
        body_bot = sy - 10
        pygame.draw.rect(surface, self.shirt_color, (sx - 7, body_top, 14, body_bot - body_top))
        pygame.draw.rect(surface, outline, (sx - 7, body_top, 14, body_bot - body_top), 2)
        pygame.draw.line(surface, self.skin_color, (sx - 7, body_top + 3),
                         (sx - 12, body_top + 10 + int(arm_wave)), 4)
        pygame.draw.line(surface, outline, (sx - 7, body_top + 3),
                         (sx - 12, body_top + 10 + int(arm_wave)), 2)
        pygame.draw.line(surface, self.skin_color, (sx + 7, body_top + 3),
                         (sx + 12, body_top + 10 - int(arm_wave)), 4)
        pygame.draw.line(surface, outline, (sx + 7, body_top + 3),
                         (sx + 12, body_top + 10 - int(arm_wave)), 2)
        pygame.draw.line(surface, self.pants_color, (sx - 3, body_bot), (sx - 4, sy - 2), 5)
        pygame.draw.line(surface, self.pants_color, (sx + 3, body_bot), (sx + 4, sy - 2), 5)
        pygame.draw.line(surface, outline, (sx - 3, body_bot), (sx - 4, sy - 2), 2)
        pygame.draw.line(surface, outline, (sx + 3, body_bot), (sx + 4, sy - 2), 2)
        pygame.draw.rect(surface, (60, 50, 40), (sx - 6, sy - 4, 5, 4))
        pygame.draw.rect(surface, (60, 50, 40), (sx + 1, sy - 4, 5, 4))

    def _draw_in_window(self, surface, sx, sy):
        outline = (30, 30, 30)
        win_w = 36
        win_h = 40
        pygame.draw.rect(surface, (60, 70, 90), (sx - win_w // 2, sy - win_h, win_w, win_h))
        pygame.draw.rect(surface, (180, 160, 120), (sx - win_w // 2 - 3, sy - win_h - 3,
                                                     win_w + 6, win_h + 6), 3)
        pygame.draw.line(surface, (180, 160, 120), (sx, sy - win_h), (sx, sy), 2)
        head_y = sy - win_h // 2 - 4
        pygame.draw.circle(surface, self.skin_color, (sx, head_y), 7)
        pygame.draw.circle(surface, outline, (sx, head_y), 7, 2)
        if self.hair_style != "bald":
            pygame.draw.arc(surface, self.hair_color, (sx - 7, head_y - 9, 14, 10), 0, math.pi, 3)
        pygame.draw.circle(surface, outline, (sx - 2, head_y - 1), 1)
        pygame.draw.circle(surface, outline, (sx + 2, head_y - 1), 1)
        body_y = head_y + 8
        pygame.draw.rect(surface, self.shirt_color, (sx - 6, body_y, 12, 12))
        arm_wave = math.sin(self.wave_phase) * 3
        pygame.draw.line(surface, self.skin_color, (sx + 6, body_y + 2),
                         (sx + 12, body_y - 2 + int(arm_wave)), 3)
        pygame.draw.line(surface, outline, (sx + 6, body_y + 2),
                         (sx + 12, body_y - 2 + int(arm_wave)), 1)


# ============================================================
# SECTION 13: CITY & LEVEL DATA
# ============================================================
CITY_DATA = {
    0: {
        "name": "Monterrey",
        "name_key": "city_monterrey",
        "levels": (1, 3),
        "sky_top": (200, 220, 255),
        "sky_bot": (255, 200, 150),
        "building_colors": [(180, 170, 160), (160, 155, 145), (140, 135, 128)],
        "weather": {"heat": True, "rain": 0.0, "wind": 0.5},
        "competitor": "Telmex",
        "special": "heat",
        "level_width": 3200,
        "time_limit": 180,
        "landmark": "cerro_silla",
    },
    1: {
        "name": "CDMX",
        "name_key": "city_cdmx",
        "levels": (4, 6),
        "sky_top": (160, 170, 180),
        "sky_bot": (200, 195, 185),
        "building_colors": [(170, 165, 155), (150, 148, 140), (130, 125, 120)],
        "weather": {"heat": False, "rain": 0.4, "wind": 0.3},
        "competitor": "Megacable",
        "special": "smog",
        "level_width": 3600,
        "time_limit": 180,
        "landmark": "cdmx_skyline",
    },
    2: {
        "name": "Guadalajara",
        "name_key": "city_guadalajara",
        "levels": (7, 9),
        "sky_top": (120, 180, 240),
        "sky_bot": (200, 220, 240),
        "building_colors": [(190, 180, 160), (175, 165, 145), (160, 150, 135)],
        "weather": {"heat": True, "rain": 0.2, "wind": 0.4},
        "competitor": "Telmex",
        "special": "drones",
        "level_width": 3600,
        "time_limit": 170,
        "landmark": "gdl_cathedral",
    },
    3: {
        "name": "Rio de Janeiro",
        "name_key": "city_rio",
        "levels": (10, 12),
        "sky_top": (80, 200, 255),
        "sky_bot": (140, 230, 200),
        "building_colors": [(200, 190, 170), (180, 175, 155), (220, 210, 190)],
        "weather": {"heat": True, "rain": 0.6, "wind": 0.6},
        "competitor": "Claro",
        "special": "vertical",
        "level_width": 3800,
        "time_limit": 170,
        "landmark": "cristo",
    },
    4: {
        "name": "Sao Paulo",
        "name_key": "city_sao_paulo",
        "levels": (13, 15),
        "sky_top": (150, 160, 180),
        "sky_bot": (190, 185, 175),
        "building_colors": [(160, 160, 165), (140, 140, 148), (120, 120, 130)],
        "weather": {"heat": False, "rain": 0.3, "wind": 0.3},
        "competitor": "Claro",
        "special": "skyscrapers",
        "level_width": 4000,
        "time_limit": 160,
        "landmark": "sp_skyline",
    },
    5: {
        "name": "Dallas",
        "name_key": "city_dallas",
        "levels": (16, 18),
        "sky_top": (200, 210, 240),
        "sky_bot": (240, 200, 160),
        "building_colors": [(190, 185, 175), (170, 168, 160), (210, 200, 185)],
        "weather": {"heat": True, "rain": 0.1, "wind": 0.8},
        "competitor": "ATT",
        "special": "heat",
        "level_width": 4000,
        "time_limit": 160,
        "landmark": "dallas_skyline",
    },
    6: {
        "name": "Bogota",
        "name_key": "city_bogota",
        "levels": (19, 21),
        "sky_top": (100, 140, 180),
        "sky_bot": (160, 180, 200),
        "building_colors": [(175, 170, 160), (155, 150, 140), (195, 185, 170)],
        "weather": {"heat": False, "rain": 0.5, "wind": 0.4},
        "competitor": "Claro",
        "special": "altitude",
        "level_width": 4200,
        "time_limit": 150,
        "landmark": "bogota_skyline",
    },
    7: {
        "name": "Buenos Aires",
        "name_key": "city_buenos_aires",
        "levels": (22, 24),
        "sky_top": (130, 170, 220),
        "sky_bot": (200, 210, 230),
        "building_colors": [(185, 180, 170), (165, 160, 152), (200, 195, 185)],
        "weather": {"heat": False, "rain": 0.2, "wind": 1.2},
        "competitor": "Claro",
        "special": "wind",
        "level_width": 4200,
        "time_limit": 150,
        "landmark": "obelisco",
    },
    8: {
        "name": "Miami",
        "name_key": "city_miami",
        "levels": (25, 27),
        "sky_top": (60, 180, 255),
        "sky_bot": (180, 240, 255),
        "building_colors": [(220, 215, 205), (200, 200, 195), (240, 235, 225)],
        "weather": {"heat": True, "rain": 0.3, "wind": 0.6},
        "competitor": "ATT",
        "special": "hurricane",
        "level_width": 4500,
        "time_limit": 140,
        "landmark": "miami_skyline",
    },
    9: {
        "name": "Final",
        "name_key": "city_final",
        "levels": (28, 30),
        "sky_top": (30, 20, 50),
        "sky_bot": (80, 40, 100),
        "building_colors": [(100, 95, 110), (80, 75, 90), (60, 55, 70)],
        "weather": {"heat": True, "rain": 0.7, "wind": 1.5},
        "competitor": "Telmex",
        "special": "all",
        "level_width": 5000,
        "time_limit": 120,
        "landmark": "final_tower",
    },
}


def get_city_for_level(level_num):
    """Return city index for a given level number (1-30)."""
    for cidx, cdata in CITY_DATA.items():
        if cdata["levels"][0] <= level_num <= cdata["levels"][1]:
            return cidx
    return 0


# ============================================================
# SECTION 14: LEVEL GENERATOR
# ============================================================
class Level:
    """Container for all entities in a level."""

    def __init__(self):
        self.platforms = []
        self.cables = []
        self.poles = []
        self.competitors = []
        self.jammers = []
        self.npcs = []
        self.install_points = []
        self.width = 3200
        self.height = 1200
        self.spawn_x = 100
        self.spawn_y = 400
        self.exit_x = 3100
        self.exit_y = 400
        self.city_idx = 0
        self.level_num = 1
        self.time_limit = 180
        self.bg_color_top = SKY_DAY
        self.bg_color_bot = (200, 220, 240)


class InstallPoint:
    """An antenna installation point in the level."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.completed = False
        self.result = None
        self.pulse_phase = random.uniform(0, math.pi * 2)

    def get_rect(self):
        return pygame.Rect(self.x - 20, self.y - 60, 40, 60)

    def update(self, dt):
        self.pulse_phase += 0.05

    def draw(self, surface, camera):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sx < -60 or sx > WIDTH + 60:
            return
        if self.completed:
            pole_color = (100, 200, 100)
            glow_color = SIGNAL_GOOD
        else:
            pole_color = (180, 180, 180)
            glow_color = UI_ACCENT
        pygame.draw.line(surface, pole_color, (sx, sy), (sx, sy - 50), 4)
        pygame.draw.line(surface, pole_color, (sx - 12, sy - 45), (sx + 12, sy - 45), 3)
        pygame.draw.line(surface, pole_color, (sx - 8, sy - 50), (sx + 8, sy - 50), 3)
        pygame.draw.line(surface, pole_color, (sx - 4, sy - 55), (sx + 4, sy - 55), 3)
        if not self.completed:
            pulse = abs(math.sin(self.pulse_phase)) * 0.5 + 0.5
            ring_r = int(15 + pulse * 10)
            ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
            alpha = int(100 * pulse)
            pygame.draw.circle(ring_surf, (*glow_color, alpha), (ring_r + 2, ring_r + 2), ring_r, 2)
            surface.blit(ring_surf, (sx - ring_r - 2, sy - 52 - ring_r - 2))
            font = pygame.font.Font(None, 20)
            prompt = font.render("E", True, glow_color)
            surface.blit(prompt, (sx - prompt.get_width() // 2, sy - 70))
        else:
            for arc_i in range(3):
                arc_r = 8 + arc_i * 6
                arc_alpha = max(40, 120 - arc_i * 30)
                arc_surf = pygame.Surface((arc_r * 2 + 4, arc_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.arc(arc_surf, (*glow_color, arc_alpha),
                                (2, 2, arc_r * 2, arc_r * 2),
                                math.pi * 0.25, math.pi * 0.75, 2)
                surface.blit(arc_surf, (sx - arc_r - 2, sy - 55 - arc_r - 2))


class LevelGenerator:
    """Procedurally generates levels from city data."""

    def __init__(self):
        self.rng = random.Random()

    def generate(self, city_idx, level_num):
        self.rng.seed(level_num * 1000 + city_idx * 77)
        city = CITY_DATA.get(city_idx, CITY_DATA[0])
        level = Level()
        level.city_idx = city_idx
        level.level_num = level_num
        level.width = city["level_width"] + (level_num % 3) * 400
        level.height = 1200
        level.time_limit = city["time_limit"] - (level_num % 3) * 10
        level.bg_color_top = city["sky_top"]
        level.bg_color_bot = city["sky_bot"]
        level.spawn_x = 100
        level.spawn_y = 400
        level.exit_x = level.width - 100
        level.exit_y = 400
        difficulty = min(1.0, level_num / 30.0)
        ground_y = 650
        level.platforms.append(Rooftop(0, ground_y, 300, 40))
        cursor_x = 300
        platform_idx = 0
        while cursor_x < level.width - 300:
            gap = self.rng.randint(40, int(80 + difficulty * 100))
            cursor_x += gap
            plat_w = self.rng.randint(80, 250 - int(difficulty * 80))
            plat_w = max(60, plat_w)
            height_var = self.rng.randint(-120, 80)
            plat_y = ground_y + height_var
            plat_y = max(200, min(800, plat_y))
            plat_type = self.rng.choice(["rooftop", "metal", "wet", "tower", "antenna"])
            if city["weather"]["rain"] > 0.3 and self.rng.random() < 0.3:
                plat_type = "wet"
            if plat_type == "rooftop":
                p = Rooftop(cursor_x, plat_y, plat_w, 30 + self.rng.randint(0, 20))
            elif plat_type == "metal":
                p = MetalGrate(cursor_x, plat_y, plat_w, 20)
            elif plat_type == "wet":
                p = WetConcrete(cursor_x, plat_y, plat_w, 30)
            elif plat_type == "tower":
                p = TowerStrut(cursor_x, plat_y, plat_w, 16)
            else:
                p = AntennaMount(cursor_x, plat_y, plat_w, 24)
            level.platforms.append(p)
            if self.rng.random() < 0.25 and platform_idx > 0:
                cable_start_x = cursor_x - gap // 2 - 30
                cable_end_x = cursor_x + 30
                cable_y = plat_y - self.rng.randint(30, 80)
                cable = FiberCable(cable_start_x, cable_y, cable_end_x, cable_y + self.rng.randint(-20, 20))
                level.cables.append(cable)
            if self.rng.random() < 0.2:
                pole_x = cursor_x + plat_w // 2
                pole_y = plat_y
                pole = TelecomPole(pole_x, pole_y, height=self.rng.randint(100, 180))
                level.poles.append(pole)
            cursor_x += plat_w
            platform_idx += 1
        level.platforms.append(Rooftop(level.width - 300, ground_y, 300, 40))
        num_install = 1 + (level_num - 1) % 3
        install_spacing = (level.width - 400) / (num_install + 1)
        for ii in range(num_install):
            ix = int(200 + install_spacing * (ii + 1))
            best_plat = None
            best_dist = 99999
            for p in level.platforms:
                px_center = p.rect.centerx
                d = abs(px_center - ix)
                if d < best_dist:
                    best_dist = d
                    best_plat = p
            if best_plat:
                ip = InstallPoint(best_plat.rect.centerx, best_plat.rect.y)
                level.install_points.append(ip)
        num_competitors = int(1 + difficulty * 2)
        comp_spacing = level.width / (num_competitors + 1)
        for ci in range(num_competitors):
            cx = int(comp_spacing * (ci + 1))
            cy = ground_y
            for p in level.platforms:
                if p.rect.left <= cx <= p.rect.right:
                    cy = p.rect.y
                    break
            comp = Competitor(cx, cy, city["competitor"])
            comp.speed = 1.5 + difficulty * 2.0
            level.competitors.append(comp)
        num_jammers = int(difficulty * 3)
        jammer_spacing = level.width / (num_jammers + 2)
        for ji in range(num_jammers):
            jx = int(jammer_spacing * (ji + 1) + 300)
            jy = ground_y - 20
            for p in level.platforms:
                if p.rect.left <= jx <= p.rect.right:
                    jy = p.rect.y
                    break
            level.jammers.append(RFJammer(jx, jy))
        num_npcs = self.rng.randint(2, 4)
        npc_spacing = level.width / (num_npcs + 1)
        for ni in range(num_npcs):
            nx = int(npc_spacing * (ni + 1))
            ny = ground_y
            for p in level.platforms:
                if p.rect.left <= nx <= p.rect.right:
                    ny = p.rect.y
                    break
            in_win = self.rng.random() < 0.3
            npc = NPCClient(nx, ny, in_window=in_win)
            level.npcs.append(npc)
        return level


# ============================================================
# SECTION 15: PARALLAX BACKGROUND SYSTEM
# ============================================================
class ParallaxBackground:
    """Three-layer parallax scrolling background with city-specific landmarks."""

    def __init__(self, city_idx=0):
        self.city_idx = city_idx
        city = CITY_DATA.get(city_idx, CITY_DATA[0])
        self.sky_top = city["sky_top"]
        self.sky_bot = city["sky_bot"]
        self.building_colors = city["building_colors"]
        self.landmark = city["landmark"]
        self.far_buildings = self._generate_far_layer()
        self.mid_buildings = self._generate_mid_layer()
        self.near_details = self._generate_near_layer()

    def _generate_far_layer(self):
        buildings = []
        rng = random.Random(self.city_idx * 111 + 7)
        x = 0
        while x < 3000:
            w = rng.randint(40, 120)
            h = rng.randint(60, 200)
            has_tank = rng.random() < 0.3
            has_antenna = rng.random() < 0.25
            has_crane = rng.random() < 0.1 and h > 140
            facade_shade = rng.randint(-20, 20)
            buildings.append((x, w, h, has_tank, has_antenna, has_crane, facade_shade))
            x += w + rng.randint(5, 30)
        return buildings

    def _generate_mid_layer(self):
        buildings = []
        rng = random.Random(self.city_idx * 222 + 13)
        x = 0
        while x < 4000:
            w = rng.randint(30, 90)
            h = rng.randint(80, 260)
            has_antenna = rng.random() < 0.3
            has_balconies = rng.random() < 0.4
            has_storefront = rng.random() < 0.5
            facade_shade = rng.randint(-15, 15)
            buildings.append((x, w, h, has_antenna, has_balconies, has_storefront, facade_shade))
            x += w + rng.randint(8, 25)
        return buildings

    def _generate_near_layer(self):
        details = []
        rng = random.Random(self.city_idx * 333 + 19)
        x = 0
        while x < 5000:
            kind = rng.choice(["pole", "sign", "bush", "wire"])
            details.append((x, kind))
            x += rng.randint(80, 250)
        return details

    def _draw_sky(self, surface):
        for row in range(0, HEIGHT, 4):
            frac = row / HEIGHT
            r = int(self.sky_top[0] + (self.sky_bot[0] - self.sky_top[0]) * frac)
            g = int(self.sky_top[1] + (self.sky_bot[1] - self.sky_top[1]) * frac)
            b = int(self.sky_top[2] + (self.sky_bot[2] - self.sky_top[2]) * frac)
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            pygame.draw.rect(surface, (r, g, b), (0, row, WIDTH, 4))

    def _draw_landmark(self, surface, cam_x):
        lx = WIDTH // 2 - int(cam_x * 0.05)
        if self.landmark == "cerro_silla":
            base_y = 250
            pts = [(lx - 180, base_y + 100), (lx - 80, base_y - 40), (lx - 20, base_y + 20),
                   (lx + 40, base_y - 60), (lx + 120, base_y + 10), (lx + 180, base_y + 100)]
            pygame.draw.polygon(surface, (80, 100, 70), pts)
            pygame.draw.polygon(surface, (60, 80, 55), pts, 2)
        elif self.landmark == "cdmx_skyline":
            base_y = 280
            towers = [(-100, 120), (-50, 90), (0, 150), (50, 100), (100, 130), (150, 80)]
            for tx_off, th in towers:
                tx = lx + tx_off
                pygame.draw.rect(surface, (120, 115, 110), (tx - 12, base_y - th, 24, th))
                pygame.draw.rect(surface, (100, 95, 90), (tx - 12, base_y - th, 24, th), 1)
            pygame.draw.circle(surface, (140, 135, 125), (lx, base_y - 160), 20)
            pygame.draw.circle(surface, (120, 115, 105), (lx, base_y - 160), 20, 2)
        elif self.landmark == "cristo":
            base_y = 220
            pygame.draw.polygon(surface, (60, 120, 60),
                                [(lx - 60, base_y + 80), (lx, base_y - 20), (lx + 60, base_y + 80)])
            body_x = lx
            body_y = base_y - 10
            pygame.draw.rect(surface, (210, 210, 200), (body_x - 4, body_y - 40, 8, 35))
            pygame.draw.line(surface, (210, 210, 200), (body_x - 30, body_y - 30),
                             (body_x + 30, body_y - 30), 6)
            pygame.draw.circle(surface, (210, 210, 200), (body_x, body_y - 44), 7)
        elif self.landmark == "obelisco":
            base_y = 300
            ob_x = lx
            pygame.draw.polygon(surface, (200, 195, 185),
                                [(ob_x - 12, base_y), (ob_x - 6, base_y - 140),
                                 (ob_x + 6, base_y - 140), (ob_x + 12, base_y)])
            pygame.draw.polygon(surface, (170, 165, 155),
                                [(ob_x - 6, base_y - 140), (ob_x, base_y - 155),
                                 (ob_x + 6, base_y - 140)])
            pygame.draw.polygon(surface, (150, 145, 135),
                                [(ob_x - 12, base_y), (ob_x - 6, base_y - 140),
                                 (ob_x + 6, base_y - 140), (ob_x + 12, base_y)], 2)
        elif self.landmark == "gdl_cathedral":
            base_y = 280
            pygame.draw.rect(surface, (180, 160, 120), (lx - 50, base_y - 80, 100, 80))
            pygame.draw.polygon(surface, (190, 170, 130),
                                [(lx - 20, base_y - 80), (lx - 15, base_y - 130), (lx - 10, base_y - 80)])
            pygame.draw.polygon(surface, (190, 170, 130),
                                [(lx + 10, base_y - 80), (lx + 15, base_y - 130), (lx + 20, base_y - 80)])
            pygame.draw.rect(surface, (100, 80, 50), (lx - 10, base_y - 40, 20, 40))
        elif self.landmark == "sp_skyline":
            base_y = 260
            towers = [(-120, 180), (-70, 140), (-20, 200), (30, 160), (80, 190), (130, 150)]
            for tx_off, th in towers:
                tx = lx + tx_off
                c = 110 + (tx_off % 30)
                pygame.draw.rect(surface, (c, c - 5, c - 10), (tx - 15, base_y - th, 30, th))
                for wy in range(base_y - th + 10, base_y, 15):
                    pygame.draw.rect(surface, (160, 180, 200), (tx - 10, wy, 6, 8))
                    pygame.draw.rect(surface, (160, 180, 200), (tx + 4, wy, 6, 8))
        elif self.landmark == "dallas_skyline":
            base_y = 270
            pygame.draw.rect(surface, (130, 140, 155), (lx - 20, base_y - 180, 40, 180))
            pygame.draw.polygon(surface, (150, 160, 175),
                                [(lx - 25, base_y - 180), (lx, base_y - 210), (lx + 25, base_y - 180)])
            for off in [-80, -50, 40, 70]:
                h = 80 + abs(off) % 50
                pygame.draw.rect(surface, (120, 125, 135), (lx + off - 12, base_y - h, 24, h))
        elif self.landmark == "bogota_skyline":
            base_y = 260
            for mi in range(5):
                mx = lx - 100 + mi * 50
                mh = 60 + (mi * 23) % 40
                pygame.draw.polygon(surface, (70, 100, 60),
                                    [(mx - 30, base_y), (mx, base_y - mh), (mx + 30, base_y)])
            pygame.draw.rect(surface, (150, 145, 135), (lx - 10, base_y - 120, 20, 120))
        elif self.landmark == "miami_skyline":
            base_y = 280
            colors = [(200, 220, 240), (180, 210, 230), (220, 200, 210)]
            for ti, (tx_off, th) in enumerate([(-90, 140), (-30, 170), (30, 130), (90, 150)]):
                c = colors[ti % len(colors)]
                pygame.draw.rect(surface, c, (lx + tx_off - 15, base_y - th, 30, th), border_radius=3)
            pygame.draw.rect(surface, (0, 120, 200), (0, base_y + 20, WIDTH, 40))
        elif self.landmark == "final_tower":
            base_y = 240
            pygame.draw.rect(surface, (60, 20, 80), (lx - 25, base_y - 200, 50, 200))
            pygame.draw.rect(surface, (80, 30, 100), (lx - 35, base_y - 220, 70, 30))
            for ring in range(5):
                ry = base_y - 220 - ring * 8
                rr = 8 + ring * 3
                pygame.draw.circle(surface, (180, 0, 255), (lx, ry), rr, 2)
            pygame.draw.line(surface, (200, 50, 50), (lx, base_y - 220), (lx, base_y - 260), 3)
            pygame.draw.circle(surface, (255, 50, 50), (lx, base_y - 264), 5)

    def _draw_far_layer(self, surface, cam_x):
        offset = int(cam_x * 0.2) % 3000
        col = self.building_colors[0] if self.building_colors else (120, 115, 110)
        base_y = HEIGHT - 100
        for bx, bw, bh, has_tank, has_antenna, has_crane, facade_shade in self.far_buildings:
            sx = bx - offset
            if sx > WIDTH + bw:
                sx -= 3000
            if sx < -bw:
                sx += 3000
            if -bw <= sx <= WIDTH + bw:
                # Building body with varied facade color
                bc = tuple(max(0, min(255, c - 30 + facade_shade)) for c in col)
                pygame.draw.rect(surface, bc, (sx, base_y - bh, bw, bh))
                # Darker right edge for depth
                edge_dark = tuple(max(0, c - 15) for c in bc)
                pygame.draw.rect(surface, edge_dark, (sx + bw - 4, base_y - bh, 4, bh))
                # Top edge highlight
                edge_light = tuple(min(255, c + 10) for c in bc)
                pygame.draw.line(surface, edge_light, (sx, base_y - bh), (sx + bw, base_y - bh), 1)
                # Window lights (small yellow dots)
                win_rng = random.Random(int(bx * 7 + bh))
                for wy in range(base_y - bh + 8, base_y - 4, 12):
                    for wx in range(sx + 4, sx + bw - 4, 10):
                        if win_rng.random() > 0.5:
                            wc = (200, 195, 140) if win_rng.random() > 0.3 else (100, 100, 110)
                            pygame.draw.rect(surface, wc, (wx, wy, 4, 5))
                # Rooftop water tank
                if has_tank:
                    tank_x = sx + bw // 3
                    pygame.draw.rect(surface, (90, 85, 80), (tank_x, base_y - bh - 10, 10, 10))
                    pygame.draw.rect(surface, (70, 65, 60), (tank_x, base_y - bh - 10, 10, 10), 1)
                # Antenna mast
                if has_antenna:
                    ant_x = sx + bw // 2
                    pygame.draw.line(surface, (140, 140, 140), (ant_x, base_y - bh), (ant_x, base_y - bh - 18), 1)
                    pygame.draw.line(surface, (140, 140, 140), (ant_x - 4, base_y - bh - 14), (ant_x + 4, base_y - bh - 14), 1)
                # Crane silhouette on tall buildings
                if has_crane:
                    cr_x = sx + bw - 8
                    cr_top = base_y - bh - 25
                    pygame.draw.line(surface, (100, 95, 90), (cr_x, base_y - bh), (cr_x, cr_top), 2)
                    pygame.draw.line(surface, (100, 95, 90), (cr_x - 20, cr_top), (cr_x + 15, cr_top), 2)
                    pygame.draw.line(surface, (100, 95, 90), (cr_x + 15, cr_top), (cr_x + 15, cr_top + 8), 1)

    def _draw_mid_layer(self, surface, cam_x):
        offset = int(cam_x * 0.5) % 4000
        col = self.building_colors[1] if len(self.building_colors) > 1 else (100, 95, 90)
        base_y = HEIGHT - 60
        for bx, bw, bh, has_ant, has_balconies, has_storefront, facade_shade in self.mid_buildings:
            sx = bx - offset
            if sx > WIDTH + bw:
                sx -= 4000
            if sx < -bw:
                sx += 4000
            if -bw <= sx <= WIDTH + bw:
                # Building body with varied color
                bc = tuple(max(0, min(255, c + facade_shade)) for c in col)
                pygame.draw.rect(surface, bc, (sx, base_y - bh, bw, bh))
                # Right side shadow for depth
                side_dark = tuple(max(0, c - 20) for c in bc)
                pygame.draw.rect(surface, side_dark, (sx + bw - 5, base_y - bh, 5, bh))
                # Outline
                outline_c = tuple(max(0, c - 15) for c in bc)
                pygame.draw.rect(surface, outline_c, (sx, base_y - bh, bw, bh), 1)
                # Roof ledge
                ledge_c = tuple(min(255, c + 10) for c in bc)
                pygame.draw.rect(surface, ledge_c, (sx - 1, base_y - bh - 2, bw + 2, 3))
                # Windows with deterministic randomness
                win_rng = random.Random(int(bx * 13 + bh * 3))
                for wy in range(base_y - bh + 8, base_y - 5, 14):
                    for wx in range(sx + 4, sx + bw - 4, 10):
                        is_lit = win_rng.random() > 0.4
                        if is_lit:
                            win_c = (220, 215, 170) if win_rng.random() > 0.3 else (180, 200, 230)
                        else:
                            win_c = (60, 65, 75)
                        pygame.draw.rect(surface, win_c, (wx, wy, 5, 7))
                        pygame.draw.rect(surface, (50, 55, 60), (wx, wy, 5, 7), 1)
                # Balconies
                if has_balconies:
                    for by_off in range(base_y - bh + 20, base_y - 20, 28):
                        for bx_off in range(sx + 3, sx + bw - 10, 18):
                            pygame.draw.rect(surface, (80, 80, 85), (bx_off, by_off, 12, 2))
                            pygame.draw.line(surface, (90, 90, 95), (bx_off, by_off), (bx_off, by_off + 6), 1)
                            pygame.draw.line(surface, (90, 90, 95), (bx_off + 12, by_off), (bx_off + 12, by_off + 6), 1)
                            pygame.draw.line(surface, (90, 90, 95), (bx_off, by_off + 6), (bx_off + 12, by_off + 6), 1)
                # Storefront at ground level
                if has_storefront and bh > 60:
                    store_y = base_y - 18
                    store_w = min(bw - 6, 30)
                    store_x = sx + 3
                    # Awning
                    pygame.draw.rect(surface, (160, 60, 60), (store_x, store_y - 4, store_w, 4))
                    # Store window
                    pygame.draw.rect(surface, (180, 210, 240), (store_x + 2, store_y, store_w - 4, 14))
                    pygame.draw.rect(surface, (60, 60, 60), (store_x + 2, store_y, store_w - 4, 14), 1)
                    # Door
                    pygame.draw.rect(surface, (80, 60, 40), (store_x + store_w + 2, store_y + 2, 8, 14))
                # Antenna
                if has_ant:
                    ant_x = sx + bw // 2
                    pygame.draw.line(surface, (160, 160, 160), (ant_x, base_y - bh),
                                     (ant_x, base_y - bh - 20), 2)
                    pygame.draw.line(surface, (160, 160, 160), (ant_x - 5, base_y - bh - 16),
                                     (ant_x + 5, base_y - bh - 16), 1)
                    pygame.draw.line(surface, (160, 160, 160), (ant_x - 3, base_y - bh - 12),
                                     (ant_x + 3, base_y - bh - 12), 1)

    def _draw_near_layer(self, surface, cam_x):
        offset = int(cam_x * 0.8) % 5000
        base_y = HEIGHT - 30
        for dx, kind in self.near_details:
            sx = dx - offset
            if sx > WIDTH + 40:
                sx -= 5000
            if sx < -40:
                sx += 5000
            if -40 <= sx <= WIDTH + 40:
                if kind == "pole":
                    # Utility pole with crossarm and insulators
                    pygame.draw.line(surface, (90, 75, 60), (sx, base_y), (sx, base_y - 60), 4)
                    pygame.draw.line(surface, (100, 85, 70), (sx - 1, base_y), (sx - 1, base_y - 60), 1)
                    pygame.draw.line(surface, (85, 75, 60), (sx - 18, base_y - 55),
                                     (sx + 18, base_y - 55), 3)
                    # Insulators
                    for ix in [-14, -6, 6, 14]:
                        pygame.draw.circle(surface, (120, 140, 130), (sx + ix, base_y - 55), 2)
                    # Ground base
                    pygame.draw.rect(surface, (70, 60, 50), (sx - 4, base_y - 2, 8, 4))
                elif kind == "sign":
                    # Street sign on post
                    pygame.draw.line(surface, (80, 80, 80), (sx, base_y), (sx, base_y - 35), 3)
                    pygame.draw.rect(surface, (50, 100, 50), (sx - 12, base_y - 35, 24, 16))
                    pygame.draw.rect(surface, (40, 80, 40), (sx - 12, base_y - 35, 24, 16), 1)
                    # Text line on sign
                    pygame.draw.line(surface, (200, 200, 200), (sx - 8, base_y - 28), (sx + 8, base_y - 28), 1)
                    pygame.draw.line(surface, (200, 200, 200), (sx - 6, base_y - 25), (sx + 6, base_y - 25), 1)
                elif kind == "bush":
                    # Multi-layered bush
                    pygame.draw.ellipse(surface, (35, 70, 35), (sx - 14, base_y - 12, 28, 16))
                    pygame.draw.ellipse(surface, (45, 85, 40), (sx - 10, base_y - 14, 20, 14))
                    pygame.draw.ellipse(surface, (50, 95, 45), (sx - 6, base_y - 16, 14, 10))
                    # Shadow beneath
                    shadow = pygame.Surface((24, 4), pygame.SRCALPHA)
                    shadow.fill((0, 0, 0, 30))
                    surface.blit(shadow, (sx - 12, base_y - 2))
                elif kind == "wire":
                    # Catenary wire with slight sag
                    for wi in range(60):
                        t = wi / 60.0
                        wx = sx - 30 + wi
                        sag = 4 * math.sin(t * math.pi)
                        wy = base_y - 50 + sag + (t * 5)
                        surface.set_at((int(wx), int(wy)), (55, 55, 55))
                    # Second wire slightly below
                    for wi in range(60):
                        t = wi / 60.0
                        wx = sx - 30 + wi
                        sag = 3 * math.sin(t * math.pi)
                        wy = base_y - 46 + sag + (t * 5)
                        surface.set_at((int(wx), int(wy)), (50, 50, 50))

    def draw(self, surface, camera):
        self._draw_sky(surface)
        cam_x = camera.x
        self._draw_landmark(surface, cam_x)
        self._draw_far_layer(surface, cam_x)
        self._draw_mid_layer(surface, cam_x)
        self._draw_near_layer(surface, cam_x)


# ============================================================
# SECTION 16: HUD
# ============================================================
class HUD:
    """Heads-up display showing signal, score, time, lives, etc."""

    def __init__(self):
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.displayed_score = 0
        self.score_lerp_speed = 5.0
        self.low_time_flash = 0.0

    def _init_fonts(self):
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 22)

    def update(self, dt, actual_score):
        self.low_time_flash += dt * 4
        diff = actual_score - self.displayed_score
        if abs(diff) < 2:
            self.displayed_score = actual_score
        else:
            self.displayed_score += int(diff * min(1.0, self.score_lerp_speed * dt))

    def _draw_signal_bars(self, surface, signal_level):
        sx, sy = 20, 20
        num_bars = 4
        bar_w = 10
        bar_gap = 4
        for i in range(num_bars):
            bh = 8 + i * 6
            bx = sx + i * (bar_w + bar_gap)
            by = sy + 30 - bh
            threshold = (i + 1) / num_bars
            if signal_level >= threshold:
                if signal_level > 0.7:
                    bc = SIGNAL_GOOD
                elif signal_level > 0.4:
                    bc = YELLOW
                else:
                    bc = SIGNAL_BAD
            else:
                bc = (60, 60, 70)
            pygame.draw.rect(surface, bc, (bx, by, bar_w, bh), border_radius=2)
            pygame.draw.rect(surface, (40, 40, 50), (bx, by, bar_w, bh), 1, border_radius=2)

    def _draw_score(self, surface):
        self._init_fonts()
        txt = self.font_medium.render(f"{t('score')}: {self.displayed_score}", True, WHITE)
        surface.blit(txt, (WIDTH - txt.get_width() - 20, 20))

    def _draw_time(self, surface, time_remaining):
        self._init_fonts()
        mins = int(time_remaining) // 60
        secs = int(time_remaining) % 60
        time_str = f"{mins:02d}:{secs:02d}"
        if time_remaining < 30:
            flash = abs(math.sin(self.low_time_flash))
            color = (255, int(50 + 100 * flash), int(50 * flash))
        else:
            color = WHITE
        txt = self.font_medium.render(f"{t('time_label')}: {time_str}", True, color)
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 20))

    def _draw_lives(self, surface, lives):
        for i in range(lives):
            hx = 20 + i * 30
            hy = 60
            pts = []
            for ang_step in range(20):
                a = ang_step / 20.0 * math.pi * 2
                r_heart = 8
                rx = r_heart * (16 * math.sin(a) ** 3) / 16.0
                ry = -r_heart * (13 * math.cos(a) - 5 * math.cos(2 * a) -
                                 2 * math.cos(3 * a) - math.cos(4 * a)) / 16.0
                pts.append((hx + int(rx), hy + int(ry)))
            if len(pts) >= 3:
                pygame.draw.polygon(surface, (220, 40, 60), pts)
                pygame.draw.polygon(surface, (180, 30, 50), pts, 2)

    def _draw_portrait(self, surface, character):
        px, py = 20, 90
        pw, ph = 40, 40
        pygame.draw.rect(surface, DIALOG_BG, (px, py, pw, ph), border_radius=5)
        pygame.draw.rect(surface, DIALOG_BORDER, (px, py, pw, ph), 2, border_radius=5)
        cx, cy = px + pw // 2, py + ph // 2 + 5
        skin = character.colors.get("skin", (210, 180, 140))
        pygame.draw.circle(surface, skin, (cx, cy - 5), 10)
        helmet = character.colors.get("helmet", UI_PRIMARY)
        pygame.draw.arc(surface, helmet, (cx - 10, cy - 17, 20, 14), 0, math.pi, 4)
        pygame.draw.circle(surface, (30, 30, 30), (cx - 3, cy - 6), 2)
        pygame.draw.circle(surface, (30, 30, 30), (cx + 3, cy - 6), 2)

    def _draw_city_level(self, surface, city_name, level_num):
        self._init_fonts()
        txt = self.font_small.render(f"{city_name} - {level_num}", True, CYAN)
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 50))

    def _draw_special_cooldown(self, surface, cooldown, max_cooldown):
        cx, cy = WIDTH - 50, 70
        radius = 18
        pygame.draw.circle(surface, (40, 40, 50), (cx, cy), radius)
        if max_cooldown > 0 and cooldown > 0:
            frac = cooldown / max_cooldown
            end_angle = math.pi * 2 * (1.0 - frac)
            if end_angle > 0.01:
                pts = [(cx, cy)]
                for step in range(int(end_angle * 10) + 1):
                    a = -math.pi / 2 + step / (end_angle * 10) * end_angle
                    pts.append((cx + int(math.cos(a) * radius), cy + int(math.sin(a) * radius)))
                if len(pts) >= 3:
                    pygame.draw.polygon(surface, UI_ACCENT, pts)
        else:
            pygame.draw.circle(surface, UI_ACCENT, (cx, cy), radius)
        pygame.draw.circle(surface, WHITE, (cx, cy), radius, 2)
        self._init_fonts()
        q_txt = self.font_small.render("Q", True, WHITE)
        surface.blit(q_txt, (cx - q_txt.get_width() // 2, cy - q_txt.get_height() // 2))

    def draw(self, surface, player, time_remaining, city_name, level_num, signal_level=0.8):
        self._draw_signal_bars(surface, signal_level)
        self._draw_score(surface)
        self._draw_time(surface, time_remaining)
        self._draw_lives(surface, player.lives)
        self._draw_portrait(surface, player.character)
        self._draw_city_level(surface, city_name, level_num)
        self._draw_special_cooldown(surface, player.character.special_cooldown,
                                     player.character.special_cooldown_max)


# ============================================================
# SECTION 17: CUTSCENE MANAGER
# ============================================================
CUTSCENE_DIALOGS = {
    0: [
        ("Rico", "Monterrey... 40 grados y subiendo. Hora de instalar antenas."),
        ("Rico", "Los de Telmex ya andan por aqui. Hay que ser rapido."),
    ],
    1: [
        ("Rico", "Ciudad de Mexico. Smog, trafico y clientes impacientes."),
        ("Vero", "Segun mis datos, Megacable domina esta zona. Hora de cambiar eso."),
    ],
    2: [
        ("Rico", "Guadalajara! Tierra del tequila y... drones de vigilancia?"),
        ("Rico", "Esto se pone interesante cada dia."),
    ],
    3: [
        ("Rico", "Rio de Janeiro! Instalaciones verticales en las favelas."),
        ("Rico", "La lluvia tropical no nos detiene."),
        ("Vero", "Cuidado con Claro, son fuertes aqui."),
    ],
    4: [
        ("Rico", "Sao Paulo, la ciudad que nunca duerme. Rascacielos hasta donde alcanza la vista."),
        ("Vero", "Intel dice que Claro tiene un jefe regional en el nivel 15."),
        ("Rico", "Pues va, a darle."),
    ],
    5: [
        ("Rico", "Dallas, Texas. El calor y AT&T, doble amenaza."),
        ("Aurelio", "Bah, he trabajado en peores condiciones. *burp*"),
    ],
    6: [
        ("Rico", "Bogota, 2600 metros de altitud. El aire esta delgado aqui."),
        ("Vero", "La altitud afecta la propagacion de senal. Cuidado."),
    ],
    7: [
        ("Rico", "Buenos Aires! Viento, tango y el Obelisco."),
        ("Rico", "El viento va a complicar las instalaciones."),
    ],
    8: [
        ("Rico", "Miami! Sol, playa y... huracanes?"),
        ("Vero", "El nivel 27 tiene alerta de huracan. Preparen todo."),
        ("Rico", "Genial, justo lo que necesitaba."),
    ],
    9: [
        ("Rico", "Esto es. La batalla final por el espectro."),
        ("Vero", "El Senor del Espectro controla todo desde aqui."),
        ("Rico", "Vamos a darle con todo. Por los WISPs!"),
    ],
}


class CutsceneManager:
    """Plays story cutscenes between cities with typewriter text."""

    def __init__(self):
        self.active = False
        self.panels = []
        self.current_panel = 0
        self.char_index = 0
        self.char_timer = 0.0
        self.char_speed = 0.03
        self.panel_timer = 0.0
        self.panel_duration = 3.0
        self.text_complete = False
        self.city_idx = 0
        self.font_large = None
        self.font_medium = None

    def start(self, city_idx):
        self.active = True
        self.city_idx = city_idx
        self.panels = CUTSCENE_DIALOGS.get(city_idx, [("Rico", "...")])
        self.current_panel = 0
        self.char_index = 0
        self.char_timer = 0.0
        self.panel_timer = 0.0
        self.text_complete = False

    def skip(self):
        if not self.text_complete:
            self.text_complete = True
            speaker, text = self.panels[self.current_panel]
            self.char_index = len(text)
        else:
            self.current_panel += 1
            if self.current_panel >= len(self.panels):
                self.active = False
                return True
            self.char_index = 0
            self.char_timer = 0.0
            self.panel_timer = 0.0
            self.text_complete = False
        return False

    def update(self, dt):
        if not self.active or self.current_panel >= len(self.panels):
            self.active = False
            return
        speaker, text = self.panels[self.current_panel]
        if not self.text_complete:
            self.char_timer += dt
            if self.char_timer >= self.char_speed:
                self.char_timer = 0.0
                self.char_index += 1
                if self.char_index >= len(text):
                    self.char_index = len(text)
                    self.text_complete = True
        else:
            self.panel_timer += dt
            if self.panel_timer >= self.panel_duration:
                self.current_panel += 1
                if self.current_panel >= len(self.panels):
                    self.active = False
                    return
                self.char_index = 0
                self.char_timer = 0.0
                self.panel_timer = 0.0
                self.text_complete = False

    def draw(self, surface):
        if not self.active or self.current_panel >= len(self.panels):
            return
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 40)
            self.font_medium = pygame.font.Font(None, 28)
        city = CITY_DATA.get(self.city_idx, CITY_DATA[0])
        top_c = city["sky_top"]
        bot_c = city["sky_bot"]
        for row in range(0, HEIGHT, 4):
            frac = row / HEIGHT
            r = int(top_c[0] + (bot_c[0] - top_c[0]) * frac)
            g = int(top_c[1] + (bot_c[1] - top_c[1]) * frac)
            b = int(top_c[2] + (bot_c[2] - top_c[2]) * frac)
            pygame.draw.rect(surface, (max(0, min(255, r)), max(0, min(255, g)),
                                        max(0, min(255, b))), (0, row, WIDTH, 4))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 120), (0, 0, WIDTH, HEIGHT))
        surface.blit(overlay, (0, 0))
        speaker, text = self.panels[self.current_panel]
        panel_w = 800
        panel_h = 200
        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = HEIGHT - panel_h - 60
        pygame.draw.rect(surface, DIALOG_BG, (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(surface, DIALOG_BORDER, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=10)
        portrait_x = panel_x + 20
        portrait_y = panel_y + 20
        portrait_size = 60
        pygame.draw.rect(surface, (40, 40, 60), (portrait_x, portrait_y, portrait_size, portrait_size),
                         border_radius=8)
        pygame.draw.rect(surface, DIALOG_BORDER, (portrait_x, portrait_y, portrait_size, portrait_size),
                         2, border_radius=8)
        pcx = portrait_x + portrait_size // 2
        pcy = portrait_y + portrait_size // 2
        pygame.draw.circle(surface, (210, 180, 140), (pcx, pcy - 5), 14)
        pygame.draw.circle(surface, (30, 30, 30), (pcx - 4, pcy - 7), 2)
        pygame.draw.circle(surface, (30, 30, 30), (pcx + 4, pcy - 7), 2)
        pygame.draw.line(surface, (30, 30, 30), (pcx - 3, pcy), (pcx + 3, pcy), 1)
        if speaker == "Vero":
            pygame.draw.arc(surface, (100, 0, 200), (pcx - 14, pcy - 22, 28, 16), 0, math.pi, 4)
        elif speaker == "Aurelio":
            pygame.draw.arc(surface, (150, 100, 50), (pcx - 14, pcy - 22, 28, 16), 0, math.pi, 4)
        else:
            pygame.draw.arc(surface, UI_PRIMARY, (pcx - 14, pcy - 22, 28, 16), 0, math.pi, 4)
        name_text = self.font_medium.render(speaker, True, DIALOG_BORDER)
        surface.blit(name_text, (portrait_x + portrait_size + 15, panel_y + 20))
        visible_text = text[:self.char_index]
        words = visible_text.split(' ')
        line = ""
        lines = []
        max_line_w = panel_w - portrait_size - 60
        for word in words:
            test = line + (" " if line else "") + word
            test_surf = self.font_medium.render(test, True, WHITE)
            if test_surf.get_width() > max_line_w and line:
                lines.append(line)
                line = word
            else:
                line = test
        if line:
            lines.append(line)
        text_x = portrait_x + portrait_size + 15
        text_y = panel_y + 55
        for li, ln in enumerate(lines):
            ln_surf = self.font_medium.render(ln, True, WHITE)
            surface.blit(ln_surf, (text_x, text_y + li * 28))
        if not self.text_complete:
            cursor_x = text_x
            if lines:
                last_line_surf = self.font_medium.render(lines[-1], True, WHITE)
                cursor_x = text_x + last_line_surf.get_width() + 2
            cursor_y = text_y + (len(lines) - 1) * 28 if lines else text_y
            if int(time.time() * 3) % 2 == 0:
                pygame.draw.rect(surface, WHITE, (cursor_x, cursor_y, 2, 22))
        skip_text = self.font_medium.render(t("skip"), True, GRAY)
        surface.blit(skip_text, (WIDTH // 2 - skip_text.get_width() // 2, HEIGHT - 40))
        city_name_text = self.font_large.render(city["name"], True, WHITE)
        surface.blit(city_name_text, (WIDTH // 2 - city_name_text.get_width() // 2, 40))


# ============================================================
# SECTION 18: PROGRESSION SYSTEM
# ============================================================
ACHIEVEMENTS = {
    "rf_wizard": {"name": "RF Wizard", "desc": "10 EXCELLENT installs in a row", "count": 10},
    "speed_runner": {"name": "Speed Runner", "desc": "Complete a level under time bonus", "count": 1},
    "no_damage": {"name": "No Damage", "desc": "Complete a level without taking damage", "count": 1},
    "jammer_hunter": {"name": "Jammer Hunter", "desc": "Destroy 50 jammers", "count": 50},
    "cable_master": {"name": "Cable Master", "desc": "Swing on 100 cables", "count": 100},
    "all_cities": {"name": "World Tour", "desc": "Complete all 10 cities", "count": 10},
}


class ProgressionManager:
    """Tracks character unlocks, completed levels, scores, achievements."""

    def __init__(self):
        self.unlocked_characters = ["Rico"]
        self.completed_levels = {}
        self.hi_scores = {}
        self.achievements = {k: 0 for k in ACHIEVEMENTS}
        self.achieved = set()
        self.excellent_streak = 0
        self.total_jammers = 0
        self.total_cables = 0

    def is_unlocked(self, char_name):
        return char_name in self.unlocked_characters

    def unlock_character(self, char_name):
        if char_name not in self.unlocked_characters:
            self.unlocked_characters.append(char_name)
            return True
        return False

    def complete_level(self, level_num, score, no_damage=False, under_time=False):
        self.completed_levels[level_num] = max(self.completed_levels.get(level_num, 0), score)
        self.hi_scores[level_num] = max(self.hi_scores.get(level_num, 0), score)
        if level_num >= 6 and "Ing. Vero" not in self.unlocked_characters:
            self.unlock_character("Ing. Vero")
        if level_num >= 15 and "Don Aurelio" not in self.unlocked_characters:
            self.unlock_character("Don Aurelio")
        if level_num >= 30 and "MorXel" not in self.unlocked_characters:
            self.unlock_character("MorXel")
        if no_damage:
            self.achievements["no_damage"] = max(self.achievements["no_damage"], 1)
            if self.achievements["no_damage"] >= ACHIEVEMENTS["no_damage"]["count"]:
                self.achieved.add("no_damage")
        if under_time:
            self.achievements["speed_runner"] = max(self.achievements["speed_runner"], 1)
            if self.achievements["speed_runner"] >= ACHIEVEMENTS["speed_runner"]["count"]:
                self.achieved.add("speed_runner")
        cities_done = set()
        for lv in self.completed_levels:
            cities_done.add(get_city_for_level(lv))
        self.achievements["all_cities"] = len(cities_done)
        if len(cities_done) >= 10:
            self.achieved.add("all_cities")
        stars = 1
        if score >= INSTALL_EXCELLENT * 2:
            stars = 3
        elif score >= INSTALL_EXCELLENT:
            stars = 2
        return stars

    def record_excellent(self):
        self.excellent_streak += 1
        self.achievements["rf_wizard"] = max(self.achievements["rf_wizard"], self.excellent_streak)
        if self.excellent_streak >= ACHIEVEMENTS["rf_wizard"]["count"]:
            self.achieved.add("rf_wizard")

    def record_not_excellent(self):
        self.excellent_streak = 0

    def record_jammer_kill(self):
        self.total_jammers += 1
        self.achievements["jammer_hunter"] = self.total_jammers
        if self.total_jammers >= ACHIEVEMENTS["jammer_hunter"]["count"]:
            self.achieved.add("jammer_hunter")

    def record_cable_swing(self):
        self.total_cables += 1
        self.achievements["cable_master"] = self.total_cables
        if self.total_cables >= ACHIEVEMENTS["cable_master"]["count"]:
            self.achieved.add("cable_master")

    def get_hi_score(self, level_num):
        return self.hi_scores.get(level_num, 0)

    def get_max_level(self):
        if not self.completed_levels:
            return 1
        return max(self.completed_levels.keys()) + 1

    def to_dict(self):
        return {
            "unlocked_characters": self.unlocked_characters,
            "completed_levels": {str(k): v for k, v in self.completed_levels.items()},
            "hi_scores": {str(k): v for k, v in self.hi_scores.items()},
            "achievements": self.achievements,
            "achieved": list(self.achieved),
            "total_jammers": self.total_jammers,
            "total_cables": self.total_cables,
            "excellent_streak": self.excellent_streak,
        }

    def from_dict(self, data):
        self.unlocked_characters = data.get("unlocked_characters", ["Rico"])
        self.completed_levels = {int(k): v for k, v in data.get("completed_levels", {}).items()}
        self.hi_scores = {int(k): v for k, v in data.get("hi_scores", {}).items()}
        self.achievements = data.get("achievements", {k: 0 for k in ACHIEVEMENTS})
        self.achieved = set(data.get("achieved", []))
        self.total_jammers = data.get("total_jammers", 0)
        self.total_cables = data.get("total_cables", 0)
        self.excellent_streak = data.get("excellent_streak", 0)


# ============================================================
# SECTION 19: SCREENS
# ============================================================
class BootScreen:
    """Green monospace boot text on black background."""

    BOOT_LINES = [
        "========================================",
        "  BAND//WIDTH  v2.6.0",
        "  A WISP Telecom Platformer Runner",
        "========================================",
        "  (c) 2026 BAND//WIDTH",
        "  Para WISPA, WISPMX & ABRINT",
        "  Inspired by every WISP tech who",
        "  climbs towers to connect the world.",
        "========================================",
        "",
        "INITIALIZING SPECTRUM ANALYZER...",
        "LOADING FREQUENCY TABLES...",
        "CALIBRATING RF MODULE...",
        "CHECKING ANTENNA ARRAY... OK",
        "LOADING CITY DATABASE... 10 CITIES FOUND",
        "CONNECTING TO WISP NETWORK... LINKED",
        "BAND//WIDTH ENGINE READY",
        "PRESS ENTER TO START",
    ]

    def __init__(self):
        self.current_line = 0
        self.char_index = 0
        self.line_timer = 0.0
        self.char_speed = 0.02
        self.line_delay = 0.4
        self.line_pause = 0.0
        self.done = False
        self.cursor_blink = 0.0
        self.font = None
        self.lines_shown = []

    def update(self, dt):
        if self.done:
            return
        if self.font is None:
            self.font = pygame.font.Font(None, 28)
        if self.line_pause > 0:
            self.line_pause -= dt
            return
        if self.current_line >= len(self.BOOT_LINES):
            self.line_timer += dt
            if self.line_timer > 1.5:
                self.done = True
            return
        self.line_timer += dt
        self.cursor_blink += dt
        current_text = self.BOOT_LINES[self.current_line]
        if self.line_timer >= self.char_speed:
            self.line_timer = 0.0
            self.char_index += 1
            if self.char_index >= len(current_text):
                if self.current_line < len(self.lines_shown):
                    self.lines_shown[self.current_line] = current_text
                else:
                    self.lines_shown.append(current_text)
                self.current_line += 1
                self.char_index = 0
                self.line_pause = self.line_delay

    def draw(self, surface):
        surface.fill(BLACK)
        if self.font is None:
            self.font = pygame.font.Font(None, 28)
        y = 80
        green = (0, 220, 80)
        for i, line_text in enumerate(self.lines_shown):
            txt_surf = self.font.render(f"> {line_text}", True, green)
            surface.blit(txt_surf, (60, y + i * 32))
        if self.current_line < len(self.BOOT_LINES):
            partial = self.BOOT_LINES[self.current_line][:self.char_index]
            txt_surf = self.font.render(f"> {partial}", True, green)
            line_y = y + len(self.lines_shown) * 32
            surface.blit(txt_surf, (60, line_y))
            if int(self.cursor_blink * 3) % 2 == 0:
                cx = 60 + txt_surf.get_width() + 2
                pygame.draw.rect(surface, green, (cx, line_y, 10, 22))


class LanguageSelectScreen:
    """Language selection: English, Espanol, Portugues."""

    LANGS = [
        ("EN", "English", (0, 40, 104), (220, 20, 60), (255, 255, 255)),
        ("ES", "Espanol", (0, 100, 60), (206, 17, 38), (255, 255, 255)),
        ("PT", "Portugues", (0, 155, 58), (255, 223, 0), (0, 39, 118)),
    ]

    def __init__(self):
        self.selected = 0
        self.font_large = None
        self.font_medium = None

    def handle_input(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % 3
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % 3
        elif key == pygame.K_RETURN:
            return self.LANGS[self.selected][0]
        return None

    def handle_mouse(self, mx, my, clicked):
        for i in range(3):
            rx = WIDTH // 2 - 150
            ry = 250 + i * 100
            if rx <= mx <= rx + 300 and ry <= my <= ry + 70:
                self.selected = i
                if clicked:
                    return self.LANGS[i][0]
        return None

    def draw(self, surface):
        surface.fill((20, 20, 30))
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
        title = self.font_large.render(t("language_select"), True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        for i, (code, name, c1, c2, c3) in enumerate(self.LANGS):
            rx = WIDTH // 2 - 150
            ry = 250 + i * 100
            rw, rh = 300, 70
            if i == self.selected:
                pygame.draw.rect(surface, WHITE, (rx - 3, ry - 3, rw + 6, rh + 6), border_radius=10)
            stripe_h = rh // 3
            pygame.draw.rect(surface, c1, (rx, ry, rw, stripe_h), border_radius=0)
            pygame.draw.rect(surface, c2, (rx, ry + stripe_h, rw, stripe_h))
            pygame.draw.rect(surface, c3, (rx, ry + stripe_h * 2, rw, rh - stripe_h * 2))
            pygame.draw.rect(surface, (60, 60, 80), (rx, ry, rw, rh), 2, border_radius=8)
            name_surf = self.font_medium.render(name, True, WHITE)
            surface.blit(name_surf, (rx + rw // 2 - name_surf.get_width() // 2,
                                     ry + rh // 2 - name_surf.get_height() // 2))


class MainMenuScreen:
    """Main menu with animated background and easter egg input."""

    def __init__(self):
        self.selected = 0
        self.options = ["start", "select_char", "options", "quit"]
        self.scroll_offset = 0.0
        self.title_pulse = 0.0
        self.font_title = None
        self.font_option = None
        self.easter_buffer = ""
        self.easter_found = set()
        self.flash_timer = 0.0
        self.flash_msg = ""
        self.has_save = False

    def set_has_save(self, val):
        self.has_save = val
        if val and "continue_game" not in self.options:
            self.options = ["continue_game", "start", "select_char", "options", "quit"]

    def handle_input(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif key == pygame.K_RETURN:
            return self.options[self.selected]
        else:
            char = pygame.key.name(key).upper()
            if len(char) == 1 and char.isalpha():
                self.easter_buffer += char
                if len(self.easter_buffer) > 10:
                    self.easter_buffer = self.easter_buffer[-10:]
                if "WISPA" in self.easter_buffer:
                    self.easter_found.add("WISPA")
                    self.flash_msg = "WISPA MODE ACTIVATED!"
                    self.flash_timer = 3.0
                    self.easter_buffer = ""
                elif "MIMOSA" in self.easter_buffer:
                    self.easter_found.add("MIMOSA")
                    self.flash_msg = "MIMOSA NETWORKS TRIBUTE!"
                    self.flash_timer = 3.0
                    self.easter_buffer = ""
                elif "CAMBIUM" in self.easter_buffer:
                    self.easter_found.add("CAMBIUM")
                    self.flash_msg = "CAMBIUM POWER UNLOCKED!"
                    self.flash_timer = 3.0
                    self.easter_buffer = ""
        return None

    def update(self, dt):
        self.scroll_offset += dt * 30
        if self.scroll_offset > 3000:
            self.scroll_offset -= 3000
        self.title_pulse += dt * 2
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def _draw_scrolling_bg(self, surface):
        surface.fill((15, 15, 25))
        offset = int(self.scroll_offset) % 3000
        rng = random.Random(42)
        base_y = HEIGHT - 80
        for i in range(40):
            bx = i * 80 - offset
            if bx < -80:
                bx += 3200
            if bx > WIDTH + 80:
                continue
            bw = 30 + (i * 17) % 40
            bh = 40 + (i * 31) % 120
            shade = 25 + (i * 7) % 20
            pygame.draw.rect(surface, (shade, shade, shade + 10), (bx, base_y - bh, bw, bh))
            for wy in range(base_y - bh + 5, base_y, 12):
                for wx in range(int(bx) + 3, int(bx) + bw - 3, 8):
                    wc = (60, 60, 40) if rng.random() > 0.6 else (20, 20, 25)
                    pygame.draw.rect(surface, wc, (wx, wy, 3, 5))

    def draw(self, surface):
        self._draw_scrolling_bg(surface)
        if self.font_title is None:
            self.font_title = pygame.font.Font(None, 72)
            self.font_option = pygame.font.Font(None, 40)
        pulse = abs(math.sin(self.title_pulse)) * 0.3 + 0.7
        title_color = (int(0 * pulse), int(200 * pulse), int(255 * pulse))
        title_surf = self.font_title.render("BAND//WIDTH", True, title_color)
        tx = WIDTH // 2 - title_surf.get_width() // 2
        ty = 100
        glow_surf = pygame.Surface((title_surf.get_width() + 20, title_surf.get_height() + 20), pygame.SRCALPHA)
        glow_alpha = int(60 * pulse)
        pygame.draw.rect(glow_surf, (*title_color, glow_alpha),
                         (0, 0, glow_surf.get_width(), glow_surf.get_height()), border_radius=10)
        surface.blit(glow_surf, (tx - 10, ty - 10))
        surface.blit(title_surf, (tx, ty))
        subtitle_font = pygame.font.Font(None, 24)
        sub = subtitle_font.render("A WISP Telecom Platformer", True, GRAY)
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, ty + 65))
        for i, opt_key in enumerate(self.options):
            oy = 260 + i * 60
            opt_text = t(opt_key)
            if i == self.selected:
                glow_w = 320
                glow_h = 46
                glow_x = WIDTH // 2 - glow_w // 2
                glow_y = oy - 6
                g_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
                pygame.draw.rect(g_surf, (0, 150, 220, 40), (0, 0, glow_w, glow_h), border_radius=8)
                surface.blit(g_surf, (glow_x, glow_y))
                opt_surf = self.font_option.render(opt_text, True, CYAN)
                arrow_x = WIDTH // 2 - 160
                pygame.draw.polygon(surface, CYAN, [(arrow_x, oy + 10),
                                                     (arrow_x + 12, oy + 4),
                                                     (arrow_x + 12, oy + 16)])
            else:
                opt_surf = self.font_option.render(opt_text, True, GRAY)
            surface.blit(opt_surf, (WIDTH // 2 - opt_surf.get_width() // 2, oy))
        if self.flash_timer > 0:
            flash_surf = self.font_option.render(self.flash_msg, True, YELLOW)
            surface.blit(flash_surf, (WIDTH // 2 - flash_surf.get_width() // 2, HEIGHT - 80))


class CharacterSelectScreen:
    """Character selection with panels, stats, and locked silhouettes."""

    CHARACTER_INFO = [
        {"class": Rico, "name": "Rico", "desc": "Cable Whip: stun+swing",
         "stats": {"speed": 7, "jump": 7, "grip": 7, "install": 6},
         "unlock": "Available from start"},
        {"class": Vero, "name": "Ing. Vero", "desc": "Spectrum Freeze: slow obstacles",
         "stats": {"speed": 6, "jump": 6, "grip": 5, "install": 10},
         "unlock": "Complete CDMX (Level 6)"},
        {"class": DonAurelio, "name": "Don Aurelio", "desc": "Old School Fix: instant repair",
         "stats": {"speed": 4, "jump": 5, "grip": 10, "install": 8},
         "unlock": "Complete Sao Paulo (Level 15)"},
        {"class": MorXel, "name": "MorXel", "desc": "Signal Ghost: teleport marker",
         "stats": {"speed": 9, "jump": 8, "grip": 4, "install": 5},
         "unlock": "Complete all 30 levels"},
    ]

    def __init__(self, progression):
        self.selected = 0
        self.progression = progression
        self.font_large = None
        self.font_medium = None
        self.font_small = None

    def handle_input(self, key):
        if key == pygame.K_LEFT:
            self.selected = (self.selected - 1) % 4
        elif key == pygame.K_RIGHT:
            self.selected = (self.selected + 1) % 4
        elif key == pygame.K_RETURN:
            info = self.CHARACTER_INFO[self.selected]
            if self.progression.is_unlocked(info["name"]):
                return info["class"]
        return None

    def draw(self, surface):
        surface.fill((15, 15, 25))
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 42)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 22)
        title = self.font_large.render(t("select_char"), True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        panel_w = 260
        panel_h = 500
        total_w = panel_w * 4 + 30 * 3
        start_x = WIDTH // 2 - total_w // 2
        for i, info in enumerate(self.CHARACTER_INFO):
            px = start_x + i * (panel_w + 30)
            py = 100
            unlocked = self.progression.is_unlocked(info["name"])
            bg_color = (30, 30, 50) if unlocked else (20, 20, 25)
            border_color = CYAN if i == self.selected else (60, 60, 80)
            pygame.draw.rect(surface, bg_color, (px, py, panel_w, panel_h), border_radius=10)
            pygame.draw.rect(surface, border_color, (px, py, panel_w, panel_h), 3, border_radius=10)
            char_cx = px + panel_w // 2
            char_cy = py + 140
            if unlocked:
                char_inst = info["class"]()
                dummy_cam = Camera(WIDTH, HEIGHT)
                dummy_cam.x = char_cx - WIDTH // 2
                dummy_cam.y = char_cy - HEIGHT // 2
                char_inst.anim_state = AnimState.IDLE
                char_inst.facing_right = True
                char_inst.draw(surface, char_cx, char_cy + 24, dummy_cam)
                name_surf = self.font_large.render(info["name"], True, WHITE)
                surface.blit(name_surf, (char_cx - name_surf.get_width() // 2, py + 220))
                desc_surf = self.font_small.render(info["desc"], True, DIALOG_BORDER)
                surface.blit(desc_surf, (char_cx - desc_surf.get_width() // 2, py + 260))
                stat_y = py + 300
                stat_names = [("speed", t("speed")), ("jump", t("jump_stat")),
                              ("grip", t("grip")), ("install", t("install_skill"))]
                for si, (skey, sname) in enumerate(stat_names):
                    sy_bar = stat_y + si * 35
                    label = self.font_small.render(sname, True, GRAY)
                    surface.blit(label, (px + 15, sy_bar))
                    bar_x = px + 100
                    bar_w = panel_w - 120
                    bar_h = 12
                    pygame.draw.rect(surface, (40, 40, 50), (bar_x, sy_bar + 3, bar_w, bar_h),
                                     border_radius=3)
                    fill_w = int(bar_w * info["stats"][skey] / 10.0)
                    bar_color = SIGNAL_GOOD if info["stats"][skey] >= 7 else (
                        YELLOW if info["stats"][skey] >= 5 else SIGNAL_BAD)
                    pygame.draw.rect(surface, bar_color, (bar_x, sy_bar + 3, fill_w, bar_h),
                                     border_radius=3)
            else:
                pygame.draw.circle(surface, (40, 40, 50), (char_cx, char_cy), 40)
                pygame.draw.circle(surface, (60, 60, 70), (char_cx, char_cy), 40, 3)
                q_surf = self.font_large.render("?", True, (80, 80, 100))
                surface.blit(q_surf, (char_cx - q_surf.get_width() // 2,
                                      char_cy - q_surf.get_height() // 2))
                lock_surf = self.font_medium.render(t("locked"), True, SIGNAL_BAD)
                surface.blit(lock_surf, (char_cx - lock_surf.get_width() // 2, py + 220))
                unlock_surf = self.font_small.render(info["unlock"], True, GRAY)
                surface.blit(unlock_surf, (char_cx - unlock_surf.get_width() // 2, py + 260))


class CityMapScreen:
    """World map with connected city nodes."""

    CITY_POSITIONS = [
        (200, 350), (320, 280), (280, 380),
        (480, 500), (520, 450), (700, 250),
        (600, 400), (750, 500), (900, 300),
        (1050, 350),
    ]

    def __init__(self, progression):
        self.progression = progression
        self.selected = 0
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.pulse = 0.0

    def handle_input(self, key):
        max_level = self.progression.get_max_level()
        if key == pygame.K_LEFT:
            self.selected = max(0, self.selected - 1)
        elif key == pygame.K_RIGHT:
            max_city = get_city_for_level(min(30, max_level))
            self.selected = min(max_city, self.selected + 1)
        elif key == pygame.K_RETURN:
            city = CITY_DATA[self.selected]
            first_level = city["levels"][0]
            if first_level <= max_level:
                return self.selected
        return None

    def update(self, dt):
        self.pulse += dt * 3

    def draw(self, surface):
        surface.fill((20, 25, 40))
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 22)
        max_level = self.progression.get_max_level()
        for i in range(len(self.CITY_POSITIONS) - 1):
            p1 = self.CITY_POSITIONS[i]
            p2 = self.CITY_POSITIONS[i + 1]
            line_color = (60, 80, 60) if CITY_DATA[i + 1]["levels"][0] <= max_level else (40, 40, 50)
            pygame.draw.line(surface, line_color, p1, p2, 2)
        for i, pos in enumerate(self.CITY_POSITIONS):
            city = CITY_DATA[i]
            first_level = city["levels"][0]
            last_level = city["levels"][1]
            all_done = all(lv in self.progression.completed_levels for lv in range(first_level, last_level + 1))
            unlocked = first_level <= max_level
            if all_done:
                node_color = SIGNAL_GOOD
                node_r = 14
            elif unlocked:
                node_color = YELLOW
                node_r = 14
            else:
                node_color = (60, 60, 70)
                node_r = 10
            if i == self.selected and unlocked:
                pulse_r = node_r + int(abs(math.sin(self.pulse)) * 6)
                ring_surf = pygame.Surface((pulse_r * 2 + 4, pulse_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(ring_surf, (*CYAN, 100), (pulse_r + 2, pulse_r + 2), pulse_r, 3)
                surface.blit(ring_surf, (pos[0] - pulse_r - 2, pos[1] - pulse_r - 2))
            pygame.draw.circle(surface, node_color, pos, node_r)
            pygame.draw.circle(surface, WHITE, pos, node_r, 2)
            name_surf = self.font_small.render(city["name"], True, WHITE if unlocked else GRAY)
            surface.blit(name_surf, (pos[0] - name_surf.get_width() // 2, pos[1] + node_r + 8))
        sel_city = CITY_DATA[self.selected]
        info_x = WIDTH - 300
        info_y = 80
        pygame.draw.rect(surface, (30, 30, 50), (info_x, info_y, 260, 200), border_radius=10)
        pygame.draw.rect(surface, DIALOG_BORDER, (info_x, info_y, 260, 200), 2, border_radius=10)
        cn = self.font_large.render(sel_city["name"], True, WHITE)
        surface.blit(cn, (info_x + 130 - cn.get_width() // 2, info_y + 15))
        lv_range = f"Levels {sel_city['levels'][0]}-{sel_city['levels'][1]}"
        lv_surf = self.font_medium.render(lv_range, True, GRAY)
        surface.blit(lv_surf, (info_x + 130 - lv_surf.get_width() // 2, info_y + 55))
        comp_surf = self.font_small.render(f"Rival: {sel_city['competitor']}", True, SIGNAL_BAD)
        surface.blit(comp_surf, (info_x + 20, info_y + 100))
        spec_surf = self.font_small.render(f"Special: {sel_city['special']}", True, YELLOW)
        surface.blit(spec_surf, (info_x + 20, info_y + 130))
        for li in range(sel_city["levels"][0], sel_city["levels"][1] + 1):
            idx = li - sel_city["levels"][0]
            lx = info_x + 20 + idx * 60
            ly = info_y + 160
            done = li in self.progression.completed_levels
            hi = self.progression.get_hi_score(li)
            dot_color = SIGNAL_GOOD if done else (60, 60, 70)
            pygame.draw.circle(surface, dot_color, (lx + 20, ly + 10), 8)
            pygame.draw.circle(surface, WHITE, (lx + 20, ly + 10), 8, 1)
            lbl = self.font_small.render(str(li), True, WHITE)
            surface.blit(lbl, (lx + 20 - lbl.get_width() // 2, ly + 10 - lbl.get_height() // 2))


class LevelCompleteScreen:
    """Score breakdown with animated counters and star rating."""

    def __init__(self):
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.display_timer = 0.0
        self.install_score = 0
        self.time_bonus = 0
        self.damage_bonus = 0
        self.total_score = 0
        self.stars = 1
        self.shown_install = 0
        self.shown_time = 0
        self.shown_damage = 0
        self.shown_total = 0
        self.counter_speed = 800.0

    def setup(self, install_score, time_bonus, damage_bonus, stars):
        self.install_score = install_score
        self.time_bonus = time_bonus
        self.damage_bonus = damage_bonus
        self.total_score = install_score + time_bonus + damage_bonus
        self.stars = stars
        self.shown_install = 0
        self.shown_time = 0
        self.shown_damage = 0
        self.shown_total = 0
        self.display_timer = 0.0

    def update(self, dt):
        self.display_timer += dt
        rate = self.counter_speed * dt
        if self.display_timer > 0.5:
            self.shown_install = min(self.install_score, self.shown_install + rate)
        if self.display_timer > 1.2:
            self.shown_time = min(self.time_bonus, self.shown_time + rate)
        if self.display_timer > 1.9:
            self.shown_damage = min(self.damage_bonus, self.shown_damage + rate)
        if self.display_timer > 2.6:
            self.shown_total = min(self.total_score, self.shown_total + rate * 1.5)

    def handle_input(self, key):
        if key == pygame.K_RETURN and self.display_timer > 3.0:
            return True
        return False

    def draw(self, surface):
        surface.fill((10, 10, 20))
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 52)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 28)
        title = self.font_large.render(t("level_complete"), True, SIGNAL_GOOD)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        panel_x = WIDTH // 2 - 250
        panel_y = 160
        panel_w = 500
        pygame.draw.rect(surface, (20, 20, 35), (panel_x, panel_y, panel_w, 320), border_radius=10)
        pygame.draw.rect(surface, DIALOG_BORDER, (panel_x, panel_y, panel_w, 320), 2, border_radius=10)
        rows = [
            (t("installing"), int(self.shown_install), self.install_score),
            (t("time_label") + " Bonus", int(self.shown_time), self.time_bonus),
            ("No Damage Bonus", int(self.shown_damage), self.damage_bonus),
        ]
        for ri, (label, shown, target) in enumerate(rows):
            ry = panel_y + 30 + ri * 55
            lbl = self.font_medium.render(label, True, GRAY)
            surface.blit(lbl, (panel_x + 30, ry))
            val_color = SIGNAL_GOOD if shown >= target and target > 0 else WHITE
            val = self.font_medium.render(f"+{shown}", True, val_color)
            surface.blit(val, (panel_x + panel_w - 30 - val.get_width(), ry))
        pygame.draw.line(surface, DIALOG_BORDER, (panel_x + 20, panel_y + 210),
                         (panel_x + panel_w - 20, panel_y + 210), 2)
        total_lbl = self.font_large.render("TOTAL", True, WHITE)
        surface.blit(total_lbl, (panel_x + 30, panel_y + 230))
        total_val = self.font_large.render(f"{int(self.shown_total)}", True, CYAN)
        surface.blit(total_val, (panel_x + panel_w - 30 - total_val.get_width(), panel_y + 230))
        star_y = panel_y + 290
        star_cx = WIDTH // 2
        for si in range(3):
            sx_star = star_cx - 60 + si * 60
            if si < self.stars and self.display_timer > 3.0:
                star_color = YELLOW
            else:
                star_color = (60, 60, 70)
            pts = []
            for pi in range(10):
                angle = -math.pi / 2 + pi * math.pi * 2 / 10
                r = 18 if pi % 2 == 0 else 8
                pts.append((sx_star + int(math.cos(angle) * r), star_y + int(math.sin(angle) * r)))
            pygame.draw.polygon(surface, star_color, pts)
            pygame.draw.polygon(surface, (200, 200, 100) if si < self.stars else (80, 80, 90), pts, 2)
        if self.display_timer > 3.5:
            next_txt = self.font_medium.render("Press ENTER for next level", True, DIALOG_BORDER)
            alpha = int(abs(math.sin(self.display_timer * 2)) * 255)
            next_txt.set_alpha(alpha)
            surface.blit(next_txt, (WIDTH // 2 - next_txt.get_width() // 2, HEIGHT - 80))


class GameOverScreen:
    """Game over with static/noise effect."""

    def __init__(self):
        self.font_large = None
        self.font_medium = None
        self.timer = 0.0
        self.selected = 0
        self.noise_surface = None

    def reset(self):
        self.timer = 0.0
        self.selected = 0

    def handle_input(self, key):
        if key == pygame.K_UP or key == pygame.K_DOWN:
            self.selected = 1 - self.selected
        elif key == pygame.K_RETURN:
            return "retry" if self.selected == 0 else "quit"
        return None

    def update(self, dt):
        self.timer += dt

    def draw(self, surface):
        surface.fill((5, 5, 10))
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 64)
            self.font_medium = pygame.font.Font(None, 36)
        if self.noise_surface is None or random.random() < 0.3:
            self.noise_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for _ in range(800):
                nx = random.randint(0, WIDTH - 1)
                ny = random.randint(0, HEIGHT - 1)
                nw = random.randint(1, 8)
                nc = random.randint(10, 50)
                pygame.draw.rect(self.noise_surface, (nc, nc, nc, 60), (nx, ny, nw, 2))
        surface.blit(self.noise_surface, (0, 0))
        for scan_i in range(3):
            scan_y = int((self.timer * 100 + scan_i * 250) % HEIGHT)
            pygame.draw.line(surface, (40, 40, 50), (0, scan_y), (WIDTH, scan_y), 1)
        title_text = t("connection_lost")
        shake_x = int(math.sin(self.timer * 15) * 3) if self.timer < 1.0 else 0
        title_surf = self.font_large.render(title_text, True, SIGNAL_BAD)
        surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2 + shake_x, 200))
        if self.timer > 1.0:
            options = [t("retry"), t("main_menu")]
            for i, opt in enumerate(options):
                oy = 380 + i * 60
                color = WHITE if i == self.selected else GRAY
                opt_surf = self.font_medium.render(opt, True, color)
                surface.blit(opt_surf, (WIDTH // 2 - opt_surf.get_width() // 2, oy))
                if i == self.selected:
                    pygame.draw.rect(surface, SIGNAL_BAD,
                                     (WIDTH // 2 - 120, oy - 5, 240, 40), 2, border_radius=5)


class CreditsScreen:
    """Scrolling credits with character sprites."""

    CREDITS_LINES = [
        "",
        "BAND//WIDTH",
        "A WISP Telecom Platformer",
        "",
        "--- DESIGN & PROGRAMMING ---",
        "Procedurally Generated with Love",
        "",
        "--- CHARACTERS ---",
        "Rico - The Cable Tech",
        "Ing. Vero - The RF Engineer",
        "Don Aurelio - The Old School Tech",
        "MorXel - The Digital Entity",
        "",
        "--- INSPIRED BY ---",
        "Every WISP technician who climbs towers",
        "in rain, heat, and wind to keep",
        "communities connected.",
        "",
        "--- SPECIAL THANKS ---",
        "WISPA - Wireless Internet Service",
        "        Providers Association",
        "WISPMX - WISPs de Mexico",
        "ABRINT - Associacao Brasileira de",
        "         Provedores de Internet",
        "",
        "--- INDUSTRY PARTNERS ---",
        "Cambium Networks",
        "Mimosa by Airspan",
        "Ubiquiti",
        "MikroTik",
        "",
        "--- MUSIC & SOUND ---",
        "All audio procedurally generated",
        "using numpy waveforms",
        "",
        "--- ART ---",
        "All graphics rendered with",
        "pygame.draw primitives",
        "Zero external assets!",
        "",
        "",
        "Para todos los que conectan",
        "al mundo, un poste a la vez.",
        "",
        "© 2026 BAND//WIDTH",
        "Para WISPA, WISPMX & ABRINT",
        "",
        "",
    ]

    def __init__(self):
        self.scroll_y = 0.0
        self.scroll_speed = 40.0
        self.font_large = None
        self.font_medium = None
        self.done = False
        self.char_dance_phase = 0.0

    def reset(self):
        self.scroll_y = 0.0
        self.done = False
        self.char_dance_phase = 0.0

    def update(self, dt):
        self.scroll_y += self.scroll_speed * dt
        self.char_dance_phase += dt * 3
        total_h = len(self.CREDITS_LINES) * 40 + 200
        if self.scroll_y > total_h:
            self.done = True

    def handle_input(self, key):
        if key == pygame.K_ESCAPE or key == pygame.K_RETURN:
            self.done = True
            return True
        return False

    def draw(self, surface):
        surface.fill((5, 5, 15))
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 40)
            self.font_medium = pygame.font.Font(None, 30)
        for i, line in enumerate(self.CREDITS_LINES):
            ly = HEIGHT + i * 40 - int(self.scroll_y)
            if ly < -40 or ly > HEIGHT + 40:
                continue
            if line.startswith("---"):
                color = DIALOG_BORDER
                font = self.font_medium
            elif line == "BAND//WIDTH":
                color = CYAN
                font = self.font_large
            elif line.startswith("©") or line.startswith("Para"):
                color = YELLOW
                font = self.font_medium
            else:
                color = WHITE
                font = self.font_medium
            txt = font.render(line, True, color)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, ly))
        dance_y = HEIGHT - 60
        char_classes = [Rico, Vero, DonAurelio, MorXel]
        spacing = 120
        start_x = WIDTH // 2 - (len(char_classes) - 1) * spacing // 2
        for ci, cls in enumerate(char_classes):
            cx = start_x + ci * spacing
            bounce = abs(math.sin(self.char_dance_phase + ci * 0.8)) * 10
            cy = dance_y - int(bounce)
            char_inst = cls()
            char_inst.facing_right = True
            char_inst.anim_state = AnimState.RUN
            char_inst.anim_frame = int(self.char_dance_phase * 5 + ci * 2) % 8
            dummy_cam = Camera(WIDTH, HEIGHT)
            dummy_cam.x = cx - WIDTH // 2
            dummy_cam.y = cy - HEIGHT // 2
            char_inst.draw(surface, cx, cy, dummy_cam)


# ============================================================
# HELP SCREEN (H key overlay)
# ============================================================

class HelpScreen:
    """Full-screen help overlay showing controls and instructions."""

    def __init__(self):
        self.font_title = None
        self.font_heading = None
        self.font_body = None
        self.scroll_y = 0
        self.previous_state = None

    def handle_input(self, key):
        if key == pygame.K_h or key == pygame.K_ESCAPE:
            return True  # close help
        elif key == pygame.K_UP:
            self.scroll_y = max(0, self.scroll_y - 30)
        elif key == pygame.K_DOWN:
            self.scroll_y = min(300, self.scroll_y + 30)
        return False

    def draw(self, surface):
        if self.font_title is None:
            self.font_title = pygame.font.Font(None, 52)
            self.font_heading = pygame.font.Font(None, 36)
            self.font_body = pygame.font.Font(None, 28)

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, (0, 0))

        # Panel background
        panel_x, panel_y = 80, 30
        panel_w, panel_h = WIDTH - 160, HEIGHT - 60
        pygame.draw.rect(surface, (15, 15, 30), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(surface, DIALOG_BORDER, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=12)

        # Title
        title_surf = self.font_title.render(t("help_title"), True, CYAN)
        surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, panel_y + 15))

        # Decorative line under title
        line_y = panel_y + 60
        pygame.draw.line(surface, DIALOG_BORDER, (panel_x + 30, line_y), (panel_x + panel_w - 30, line_y), 2)

        # Controls section
        y = line_y + 15 - self.scroll_y
        controls_label = self.font_heading.render(t("controls"), True, YELLOW)
        surface.blit(controls_label, (panel_x + 40, y))
        y += 40

        control_keys = [
            "help_move", "help_jump", "help_sprint", "help_interact",
            "help_special", "help_pause", "help_fullscreen", "help_skip", "help_info"
        ]
        for ck in control_keys:
            txt = t(ck)
            parts = txt.split(" - ", 1)
            if len(parts) == 2:
                key_surf = self.font_body.render(parts[0], True, (0, 220, 180))
                desc_surf = self.font_body.render(f" - {parts[1]}", True, WHITE)
                if panel_y + 50 < y < panel_y + panel_h - 30:
                    surface.blit(key_surf, (panel_x + 60, y))
                    surface.blit(desc_surf, (panel_x + 60 + key_surf.get_width(), y))
            else:
                txt_surf = self.font_body.render(txt, True, WHITE)
                if panel_y + 50 < y < panel_y + panel_h - 30:
                    surface.blit(txt_surf, (panel_x + 60, y))
            y += 28

        # How to Play section
        y += 15
        howto_label = self.font_heading.render(t("help_howto_title"), True, YELLOW)
        if panel_y + 50 < y < panel_y + panel_h - 30:
            surface.blit(howto_label, (panel_x + 40, y))
        y += 40

        howto_keys = ["help_howto_1", "help_howto_2", "help_howto_3", "help_howto_4", "help_howto_5"]
        for i, hk in enumerate(howto_keys):
            txt = t(hk)
            bullet = self.font_body.render(f"  {i+1}. {txt}", True, (200, 200, 220))
            if panel_y + 50 < y < panel_y + panel_h - 30:
                surface.blit(bullet, (panel_x + 50, y))
            y += 30

        # Scoring section
        y += 15
        score_label = self.font_heading.render("SCORING", True, YELLOW)
        if panel_y + 50 < y < panel_y + panel_h - 30:
            surface.blit(score_label, (panel_x + 40, y))
        y += 35

        scoring_info = [
            ("Excellent Install", "+500"),
            ("Good Install", "+200"),
            ("Cable Swing", "+25"),
            ("Perfect Landing", "+100"),
            ("No Damage Bonus", "+300"),
            ("Beat Competitor", "+400"),
            ("Jammer Destroyed", "+250"),
        ]
        for label, pts in scoring_info:
            if panel_y + 50 < y < panel_y + panel_h - 30:
                lbl_surf = self.font_body.render(f"  {label}", True, (180, 180, 200))
                pts_surf = self.font_body.render(pts, True, SIGNAL_GOOD)
                surface.blit(lbl_surf, (panel_x + 60, y))
                surface.blit(pts_surf, (panel_x + panel_w - 120, y))
            y += 26

        # Close hint at bottom
        close_surf = self.font_body.render(t("help_press_close"), True, GRAY)
        surface.blit(close_surf, (WIDTH // 2 - close_surf.get_width() // 2, panel_y + panel_h - 28))


# ============================================================
# OPTIONS SCREEN
# ============================================================

class OptionsScreen:
    """Options menu with volume, language, fullscreen, screen shake settings."""

    def __init__(self, audio_engine):
        self.audio = audio_engine
        self.font_title = None
        self.font_option = None
        self.font_value = None
        self.selected = 0
        self.items = ["music_vol", "sfx_vol", "language", "fullscreen", "screenshake", "credits", "back"]
        self.fullscreen_on = False
        self.screenshake_on = True
        self.lang_options = ["EN", "ES", "PT"]
        self.lang_index = 1  # default ES

    def handle_input(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.items)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.items)
        elif key == pygame.K_LEFT:
            self._adjust(-1)
        elif key == pygame.K_RIGHT:
            self._adjust(1)
        elif key == pygame.K_RETURN:
            item = self.items[self.selected]
            if item == "back":
                return "back"
            elif item == "credits":
                return "credits"
            elif item == "fullscreen":
                self.fullscreen_on = not self.fullscreen_on
                return "toggle_fullscreen"
            elif item == "screenshake":
                self.screenshake_on = not self.screenshake_on
                return "toggle_screenshake"
            elif item == "language":
                self._adjust(1)
        elif key == pygame.K_ESCAPE:
            return "back"
        return None

    def _adjust(self, direction):
        item = self.items[self.selected]
        if item == "music_vol":
            new_vol = self.audio.music_volume + direction * 0.1
            self.audio.set_music_volume(new_vol)
        elif item == "sfx_vol":
            new_vol = self.audio.sfx_volume + direction * 0.1
            self.audio.set_sfx_volume(new_vol)
        elif item == "language":
            self.lang_index = (self.lang_index + direction) % len(self.lang_options)
            global current_language
            current_language = self.lang_options[self.lang_index]

    def draw(self, surface):
        if self.font_title is None:
            self.font_title = pygame.font.Font(None, 52)
            self.font_option = pygame.font.Font(None, 36)
            self.font_value = pygame.font.Font(None, 32)

        surface.fill((10, 10, 25))

        # Title
        title = self.font_title.render(t("options_title"), True, CYAN)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        # Decorative line
        pygame.draw.line(surface, DIALOG_BORDER, (200, 110), (WIDTH - 200, 110), 2)

        y_start = 150
        spacing = 65

        for i, item in enumerate(self.items):
            y = y_start + i * spacing
            is_sel = (i == self.selected)
            base_color = CYAN if is_sel else GRAY

            if is_sel:
                # Selection highlight
                hl = pygame.Surface((500, 50), pygame.SRCALPHA)
                pygame.draw.rect(hl, (0, 150, 220, 30), (0, 0, 500, 50), border_radius=8)
                surface.blit(hl, (WIDTH // 2 - 250, y - 8))
                # Arrow
                pygame.draw.polygon(surface, CYAN, [
                    (WIDTH // 2 - 240, y + 12),
                    (WIDTH // 2 - 228, y + 6),
                    (WIDTH // 2 - 228, y + 18)])

            if item == "music_vol":
                label = t("opt_music_vol")
                self._draw_slider(surface, label, self.audio.music_volume, y, base_color)
            elif item == "sfx_vol":
                label = t("opt_sfx_vol")
                self._draw_slider(surface, label, self.audio.sfx_volume, y, base_color)
            elif item == "language":
                label = t("opt_language")
                lang_name = {"EN": "English", "ES": "Espanol", "PT": "Portugues"}
                val_text = lang_name.get(self.lang_options[self.lang_index], "??")
                lbl_surf = self.font_option.render(label, True, base_color)
                val_surf = self.font_value.render(f"< {val_text} >", True, YELLOW)
                surface.blit(lbl_surf, (WIDTH // 2 - 200, y))
                surface.blit(val_surf, (WIDTH // 2 + 80, y + 3))
            elif item == "fullscreen":
                label = t("opt_fullscreen")
                val = t("opt_on") if self.fullscreen_on else t("opt_off")
                lbl_surf = self.font_option.render(label, True, base_color)
                val_color = SIGNAL_GOOD if self.fullscreen_on else SIGNAL_BAD
                val_surf = self.font_value.render(val, True, val_color)
                surface.blit(lbl_surf, (WIDTH // 2 - 200, y))
                surface.blit(val_surf, (WIDTH // 2 + 120, y + 3))
            elif item == "screenshake":
                label = t("opt_screenshake")
                val = t("opt_on") if self.screenshake_on else t("opt_off")
                lbl_surf = self.font_option.render(label, True, base_color)
                val_color = SIGNAL_GOOD if self.screenshake_on else SIGNAL_BAD
                val_surf = self.font_value.render(val, True, val_color)
                surface.blit(lbl_surf, (WIDTH // 2 - 200, y))
                surface.blit(val_surf, (WIDTH // 2 + 120, y + 3))
            elif item == "credits":
                lbl_surf = self.font_option.render(t("opt_credits"), True, base_color)
                surface.blit(lbl_surf, (WIDTH // 2 - lbl_surf.get_width() // 2, y))
            elif item == "back":
                lbl_surf = self.font_option.render(t("opt_back"), True, base_color)
                surface.blit(lbl_surf, (WIDTH // 2 - lbl_surf.get_width() // 2, y))

        # Footer hint
        hint = self.font_value.render("LEFT/RIGHT to adjust  |  ENTER to select", True, (80, 80, 100))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

    def _draw_slider(self, surface, label, value, y, color):
        lbl_surf = self.font_option.render(label, True, color)
        surface.blit(lbl_surf, (WIDTH // 2 - 200, y))
        # Slider bar
        bar_x = WIDTH // 2 + 80
        bar_y = y + 10
        bar_w = 160
        bar_h = 12
        pygame.draw.rect(surface, (40, 40, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        fill_w = int(bar_w * value)
        if fill_w > 0:
            fill_color = SIGNAL_GOOD if value > 0.3 else SIGNAL_BAD
            pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_w, bar_h), border_radius=6)
        pygame.draw.rect(surface, color, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=6)
        # Knob
        knob_x = bar_x + fill_w
        pygame.draw.circle(surface, WHITE, (knob_x, bar_y + bar_h // 2), 8)
        pygame.draw.circle(surface, color, (knob_x, bar_y + bar_h // 2), 8, 2)
        # Percentage
        pct = self.font_value.render(f"{int(value * 100)}%", True, color)
        surface.blit(pct, (bar_x + bar_w + 15, y + 3))


# ============================================================
# SECTION 20: SAVE SYSTEM
# ============================================================
SAVE_FILE = os.path.join(os.path.expanduser("~"), "bandwidth_save.json")


class SaveManager:
    """Saves and loads game progress to JSON file."""

    def __init__(self):
        self.data = {
            "selected_language": "ES",
            "easter_eggs_found": [],
        }

    def save(self, progression, language, easter_eggs=None):
        try:
            self.data["selected_language"] = language
            self.data["progression"] = progression.to_dict()
            if easter_eggs:
                self.data["easter_eggs_found"] = list(easter_eggs)
            with open(SAVE_FILE, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception:
            return False

    def load(self):
        try:
            if not os.path.exists(SAVE_FILE):
                return None
            with open(SAVE_FILE, 'r') as f:
                self.data = json.load(f)
            return self.data
        except Exception:
            return None

    def has_save(self):
        return os.path.exists(SAVE_FILE)

    def get_language(self):
        return self.data.get("selected_language", "ES")

    def get_easter_eggs(self):
        return set(self.data.get("easter_eggs_found", []))

    def load_progression(self, progression):
        data = self.data.get("progression", None)
        if data:
            progression.from_dict(data)
            return True
        return False


# ============================================================
# SECTION 21: BOSS FIGHT (Level 30)
# ============================================================
class BossFight:
    """Final boss: El Senor del Espectro - 4-phase corporate exec fight."""

    def __init__(self):
        self.active = False
        self.phase = 1
        self.max_phase = 4
        self.health = 100.0
        self.max_health = 100.0
        self.phase_health = [25.0, 25.0, 25.0, 25.0]
        self.boss_x = WIDTH - 200.0
        self.boss_y = 400.0
        self.boss_vx = 0.0
        self.boss_vy = 0.0
        self.attack_timer = 0.0
        self.attack_cooldown = 2.0
        self.projectiles = []
        self.trucks = []
        self.glitch_timer = 0.0
        self.glitch_active = False
        self.controls_swapped = False
        self.antennas_to_install = []
        self.antenna_countdown = 0.0
        self.phase_transition = False
        self.transition_timer = 0.0
        self.defeated = False
        self.briefcase_glow = 0.0
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.flash_effect = 0
        self.move_phase = 0.0

    def start(self):
        self.active = True
        self.phase = 1
        self.health = self.max_health
        self.defeated = False
        self.projectiles = []
        self.trucks = []
        self.glitch_active = False
        self.controls_swapped = False
        self.phase_transition = False
        self.boss_x = float(WIDTH - 200)
        self.boss_y = 400.0
        self.attack_timer = 2.0

    def _spawn_fine_projectile(self):
        px = self.boss_x - 20
        py = self.boss_y - 60
        pvx = random.uniform(-5, -2)
        pvy = random.uniform(-3, 1)
        self.projectiles.append({"x": px, "y": py, "vx": pvx, "vy": pvy, "type": "fine", "life": 4.0})

    def _spawn_truck(self):
        ty = random.choice([350, 450, 550])
        self.trucks.append({"x": float(WIDTH + 50), "y": ty, "speed": random.uniform(4, 8), "life": 8.0})

    def _start_glitch(self):
        self.glitch_active = True
        self.glitch_timer = 3.0
        self.controls_swapped = True

    def _start_antenna_phase(self):
        self.antennas_to_install = []
        for ai in range(5):
            ax = 200 + ai * 180
            ay = 400
            self.antennas_to_install.append({"x": ax, "y": ay, "installed": False, "pulse": random.uniform(0, 6.28)})
        self.antenna_countdown = 20.0

    def update(self, dt, player):
        if not self.active or self.defeated:
            return
        self.briefcase_glow += dt * 3
        self.move_phase += dt * 2
        self.boss_y = 400 + math.sin(self.move_phase) * 40
        self.boss_x = WIDTH - 200 + math.sin(self.move_phase * 0.7) * 60
        if self.phase_transition:
            self.transition_timer -= dt
            if self.transition_timer <= 0:
                self.phase_transition = False
                self.phase += 1
                if self.phase > self.max_phase:
                    self.defeated = True
                    return
                self.attack_timer = 2.0
                if self.phase == 4:
                    self._start_antenna_phase()
            return
        current_phase_health = sum(self.phase_health[self.phase - 1:])
        if self.health <= self.max_health - sum(self.phase_health[:self.phase]):
            self.phase_transition = True
            self.transition_timer = 1.5
            self.flash_effect = 15
            self.projectiles.clear()
            self.trucks.clear()
            self.glitch_active = False
            self.controls_swapped = False
            return
        self.attack_timer -= dt
        if self.phase == 1:
            if self.attack_timer <= 0:
                for _ in range(3):
                    self._spawn_fine_projectile()
                self.attack_timer = self.attack_cooldown * 0.8
        elif self.phase == 2:
            if self.attack_timer <= 0:
                self._spawn_truck()
                self._spawn_fine_projectile()
                self.attack_timer = self.attack_cooldown
        elif self.phase == 3:
            if self.attack_timer <= 0:
                self._start_glitch()
                self._spawn_fine_projectile()
                self._spawn_fine_projectile()
                self.attack_timer = self.attack_cooldown * 1.5
            if self.glitch_active:
                self.glitch_timer -= dt
                if self.glitch_timer <= 0:
                    self.glitch_active = False
                    self.controls_swapped = False
        elif self.phase == 4:
            self.antenna_countdown -= dt
            if self.antenna_countdown <= 0:
                player.take_damage(100)
            if self.attack_timer <= 0:
                self._spawn_fine_projectile()
                self.attack_timer = self.attack_cooldown * 0.6
            all_installed = all(a["installed"] for a in self.antennas_to_install)
            if all_installed:
                self.health = 0
                self.defeated = True
                return
        to_remove = []
        for i, proj in enumerate(self.projectiles):
            proj["x"] += proj["vx"]
            proj["y"] += proj["vy"]
            proj["vy"] += 0.1
            proj["life"] -= dt
            if proj["life"] <= 0 or proj["x"] < -50 or proj["y"] > HEIGHT + 50:
                to_remove.append(i)
            else:
                pr = pygame.Rect(int(proj["x"]) - 10, int(proj["y"]) - 10, 20, 20)
                pl_rect = player.get_rect()
                if pr.colliderect(pl_rect):
                    player.take_damage(15)
                    to_remove.append(i)
        for i in reversed(to_remove):
            if i < len(self.projectiles):
                self.projectiles.pop(i)
        truck_remove = []
        for i, truck in enumerate(self.trucks):
            truck["x"] -= truck["speed"]
            truck["life"] -= dt
            if truck["x"] < -100 or truck["life"] <= 0:
                truck_remove.append(i)
            else:
                tr = pygame.Rect(int(truck["x"]) - 40, int(truck["y"]) - 25, 80, 50)
                if tr.colliderect(player.get_rect()):
                    player.take_damage(25)
                    truck_remove.append(i)
        for i in reversed(truck_remove):
            if i < len(self.trucks):
                self.trucks.pop(i)
        if self.flash_effect > 0:
            self.flash_effect -= 1
        boss_rect = pygame.Rect(int(self.boss_x) - 25, int(self.boss_y) - 70, 50, 70)
        pl_rect = player.get_rect()
        if boss_rect.colliderect(pl_rect) and player.vy > 0 and player.y < self.boss_y - 50:
            self.health -= 10
            player.vy = JUMP_FORCE
            self.flash_effect = 8

    def try_install_antenna(self, player_x, player_y):
        for ant in self.antennas_to_install:
            if not ant["installed"]:
                dx = player_x - ant["x"]
                dy = player_y - ant["y"]
                if abs(dx) < 40 and abs(dy) < 40:
                    ant["installed"] = True
                    return True
        return False

    def draw(self, surface, camera):
        if not self.active:
            return
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 42)
            self.font_medium = pygame.font.Font(None, 30)
            self.font_small = pygame.font.Font(None, 22)
        if self.glitch_active and random.random() < 0.3:
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-5, 5)
            strip_h = random.randint(20, 80)
            strip_y = random.randint(0, HEIGHT - strip_h)
            strip = surface.subsurface((0, strip_y, WIDTH, strip_h)).copy()
            surface.blit(strip, (offset_x, strip_y + offset_y))
        if self.flash_effect > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(flash_surf, (255, 255, 255, self.flash_effect * 15), (0, 0, WIDTH, HEIGHT))
            surface.blit(flash_surf, (0, 0))
        bsx = int(self.boss_x)
        bsy = int(self.boss_y)
        suit_color = (40, 40, 60)
        shirt_color = (220, 220, 230)
        skin_color = (210, 180, 140)
        pygame.draw.rect(surface, suit_color, (bsx - 18, bsy - 55, 36, 40), border_radius=3)
        pygame.draw.rect(surface, shirt_color, (bsx - 6, bsy - 52, 12, 35))
        pygame.draw.polygon(surface, (150, 30, 30),
                            [(bsx, bsy - 52), (bsx - 4, bsy - 42), (bsx + 4, bsy - 42)])
        pygame.draw.circle(surface, skin_color, (bsx, bsy - 65), 12)
        pygame.draw.circle(surface, (30, 30, 30), (bsx, bsy - 65), 12, 2)
        pygame.draw.circle(surface, (30, 30, 30), (bsx - 4, bsy - 67), 2)
        pygame.draw.circle(surface, (30, 30, 30), (bsx + 4, bsy - 67), 2)
        pygame.draw.line(surface, (30, 30, 30), (bsx - 3, bsy - 60), (bsx + 3, bsy - 60), 2)
        pygame.draw.rect(surface, (20, 20, 30), (bsx - 14, bsy - 73, 28, 8), border_radius=2)
        pygame.draw.line(surface, skin_color, (bsx - 18, bsy - 50), (bsx - 30, bsy - 35), 4)
        pygame.draw.line(surface, skin_color, (bsx + 18, bsy - 50), (bsx + 30, bsy - 35), 4)
        pygame.draw.line(surface, suit_color, (bsx - 5, bsy - 15), (bsx - 8, bsy), 6)
        pygame.draw.line(surface, suit_color, (bsx + 5, bsy - 15), (bsx + 8, bsy), 6)
        bc_glow = abs(math.sin(self.briefcase_glow))
        bc_color = (int(180 + 75 * bc_glow), int(50 * bc_glow), int(200 + 55 * bc_glow))
        pygame.draw.rect(surface, bc_color, (bsx + 25, bsy - 40, 18, 14), border_radius=2)
        pygame.draw.rect(surface, (255, 255, 200), (bsx + 25, bsy - 40, 18, 14), 2, border_radius=2)
        for proj in self.projectiles:
            px, py = int(proj["x"]), int(proj["y"])
            pygame.draw.rect(surface, (255, 255, 220), (px - 8, py - 10, 16, 20))
            pygame.draw.rect(surface, (200, 180, 140), (px - 8, py - 10, 16, 20), 1)
            pygame.draw.line(surface, (150, 140, 120), (px - 5, py - 4), (px + 5, py - 4), 1)
            pygame.draw.line(surface, (150, 140, 120), (px - 5, py), (px + 5, py), 1)
            pygame.draw.line(surface, (150, 140, 120), (px - 5, py + 4), (px + 3, py + 4), 1)
        for truck in self.trucks:
            tx, ty = int(truck["x"]), int(truck["y"])
            pygame.draw.rect(surface, (200, 30, 30), (tx - 40, ty - 25, 80, 50), border_radius=5)
            pygame.draw.rect(surface, (30, 30, 30), (tx - 40, ty - 25, 80, 50), 2, border_radius=5)
            pygame.draw.circle(surface, (40, 40, 40), (tx - 25, ty + 25), 8)
            pygame.draw.circle(surface, (40, 40, 40), (tx + 25, ty + 25), 8)
        for ant in self.antennas_to_install:
            ax, ay = int(ant["x"]), int(ant["y"])
            if ant["installed"]:
                pygame.draw.line(surface, SIGNAL_GOOD, (ax, ay), (ax, ay - 40), 3)
                pygame.draw.line(surface, SIGNAL_GOOD, (ax - 8, ay - 35), (ax + 8, ay - 35), 2)
                for arc_i in range(3):
                    ar = 6 + arc_i * 5
                    arc_s = pygame.Surface((ar * 2 + 4, ar * 2 + 4), pygame.SRCALPHA)
                    pygame.draw.arc(arc_s, (*SIGNAL_GOOD, 120 - arc_i * 30),
                                    (2, 2, ar * 2, ar * 2), math.pi * 0.25, math.pi * 0.75, 2)
                    surface.blit(arc_s, (ax - ar - 2, ay - 40 - ar - 2))
            else:
                ant["pulse"] += 0.05
                pygame.draw.line(surface, (150, 150, 150), (ax, ay), (ax, ay - 40), 3)
                pygame.draw.line(surface, (150, 150, 150), (ax - 8, ay - 35), (ax + 8, ay - 35), 2)
                pulse = abs(math.sin(ant["pulse"]))
                ring_r = int(10 + pulse * 8)
                rs = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(rs, (255, 100, 100, int(100 * pulse)), (ring_r + 2, ring_r + 2), ring_r, 2)
                surface.blit(rs, (ax - ring_r - 2, ay - 40 - ring_r - 2))
                e_txt = self.font_small.render("E", True, SIGNAL_BAD)
                surface.blit(e_txt, (ax - e_txt.get_width() // 2, ay - 55))
        bar_w = 400
        bar_h = 20
        bar_x = WIDTH // 2 - bar_w // 2
        bar_y = 30
        pygame.draw.rect(surface, (30, 30, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        fill_frac = max(0, self.health / self.max_health)
        fill_w = int(bar_w * fill_frac)
        if fill_frac > 0.5:
            bar_color = SIGNAL_BAD
        elif fill_frac > 0.25:
            bar_color = ORANGE
        else:
            bar_color = SIGNAL_GOOD
        if fill_w > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=5)
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=5)
        boss_name = self.font_medium.render("EL SENOR DEL ESPECTRO", True, WHITE)
        surface.blit(boss_name, (WIDTH // 2 - boss_name.get_width() // 2, bar_y - 25))
        phase_txt = self.font_small.render(f"Phase {self.phase}/{self.max_phase}", True, GRAY)
        surface.blit(phase_txt, (bar_x + bar_w + 10, bar_y + 2))
        if self.phase == 4 and self.antenna_countdown > 0:
            countdown_color = SIGNAL_BAD if self.antenna_countdown < 5 else YELLOW
            cd_txt = self.font_large.render(f"{self.antenna_countdown:.1f}s", True, countdown_color)
            surface.blit(cd_txt, (WIDTH // 2 - cd_txt.get_width() // 2, bar_y + bar_h + 10))
            installed = sum(1 for a in self.antennas_to_install if a["installed"])
            total = len(self.antennas_to_install)
            ant_txt = self.font_medium.render(f"Antennas: {installed}/{total}", True, WHITE)
            surface.blit(ant_txt, (WIDTH // 2 - ant_txt.get_width() // 2, bar_y + bar_h + 50))
        if self.phase_transition:
            trans_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(150 * (1.0 - self.transition_timer / 1.5))
            pygame.draw.rect(trans_surf, (255, 255, 255, min(255, alpha)), (0, 0, WIDTH, HEIGHT))
            surface.blit(trans_surf, (0, 0))
            phase_text = self.font_large.render(f"PHASE {self.phase + 1}", True, (30, 30, 30))
            surface.blit(phase_text, (WIDTH // 2 - phase_text.get_width() // 2,
                                      HEIGHT // 2 - phase_text.get_height() // 2))


# ============================================================
# SECTION 22: GAME CLASS & MAIN LOOP
# ============================================================
class Game:
    """Main game class tying all systems together."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("BAND//WIDTH - A WISP Telecom Platformer")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False
        self.state = GameState.BOOT
        self.audio = AudioEngine()
        self.camera = Camera(WIDTH, HEIGHT)
        self.particles = ParticleSystem()
        self.weather = WeatherSystem()
        self.hud = HUD()
        self.cutscene = CutsceneManager()
        self.progression = ProgressionManager()
        self.save_manager = SaveManager()
        self.level_generator = LevelGenerator()
        self.install_minigame = InstallationMinigame()
        self.dialog_manager = DialogManager()
        self.boss_fight = BossFight()
        self.boot_screen = BootScreen()
        self.lang_screen = LanguageSelectScreen()
        self.menu_screen = MainMenuScreen()
        self.char_select = CharacterSelectScreen(self.progression)
        self.city_map = CityMapScreen(self.progression)
        self.level_complete_screen = LevelCompleteScreen()
        self.game_over_screen = GameOverScreen()
        self.credits_screen = CreditsScreen()
        self.help_screen = HelpScreen()
        self.options_screen = OptionsScreen(self.audio)
        self.parallax = ParallaxBackground(0)
        self.player = None
        self.selected_char_class = Rico
        self.current_level = None
        self.current_level_num = 1
        self.current_city_idx = 0
        self.time_remaining = 180.0
        self.level_damage_taken = False
        self.level_install_score = 0
        self.signal_level = 0.8
        self.pause_selected = 0
        self.death_timer = 0.0
        self.exit_zone_rect = None
        saved = self.save_manager.load()
        if saved:
            global current_language
            current_language = self.save_manager.get_language()
            self.save_manager.load_progression(self.progression)
            self.menu_screen.set_has_save(True)
            self.menu_screen.easter_found = self.save_manager.get_easter_eggs()
        self._current_music_track = None

    def _ensure_music(self, track):
        """Start music track if not already playing."""
        if self._current_music_track != track:
            self.audio.play_music(track)
            self._current_music_track = track

    def _start_level(self, level_num):
        self.current_level_num = level_num
        self.current_city_idx = get_city_for_level(level_num)
        city = CITY_DATA[self.current_city_idx]
        self.current_level = self.level_generator.generate(self.current_city_idx, level_num)
        self.parallax = ParallaxBackground(self.current_city_idx)
        self.camera.set_bounds(0, 0, self.current_level.width, self.current_level.height)
        self.player = Player(self.selected_char_class,
                             self.current_level.spawn_x, self.current_level.spawn_y)
        self.player.set_checkpoint(self.current_level.spawn_x, self.current_level.spawn_y)
        self.time_remaining = float(self.current_level.time_limit)
        self.level_damage_taken = False
        self.level_install_score = 0
        self.signal_level = 0.8
        self.death_timer = 0.0
        weather_cfg = city["weather"]
        self.weather.set_rain(weather_cfg.get("rain", 0.0))
        self.weather.set_heat(weather_cfg.get("heat", False))
        self.weather.set_wind(weather_cfg.get("wind", 0.0))
        self.exit_zone_rect = pygame.Rect(self.current_level.exit_x - 30,
                                           self.current_level.spawn_y - 80, 60, 80)
        self.install_minigame.active = False
        if level_num == 30:
            self.state = GameState.BOSS_FIGHT
            self.boss_fight.start()
        else:
            self.state = GameState.PLAYING

    def _complete_level(self):
        time_bonus = int(max(0, self.time_remaining) * TIME_BONUS_PER_SEC // 10)
        damage_bonus = NO_DAMAGE if not self.level_damage_taken else 0
        install_score = self.level_install_score
        total = install_score + time_bonus + damage_bonus
        under_time = self.time_remaining > self.current_level.time_limit * 0.5
        stars = self.progression.complete_level(
            self.current_level_num, total,
            no_damage=not self.level_damage_taken,
            under_time=under_time
        )
        self.level_complete_screen.setup(install_score, time_bonus, damage_bonus, stars)
        self.save_manager.save(self.progression, current_language, self.menu_screen.easter_found)
        self.state = GameState.LEVEL_COMPLETE

    def _compute_signal_level(self):
        if not self.player or not self.current_level:
            return 0.8
        base = 0.8
        for jammer in self.current_level.jammers:
            if jammer.alive:
                penalty = jammer.get_signal_penalty(self.player.x, self.player.y) / 100.0
                base -= penalty
        if self.weather.raining:
            base -= self.weather.rain_intensity * 0.1
        return max(0.05, min(1.0, base))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11 or (event.key == pygame.K_f):
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    continue
                self._handle_key_down(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)

    def _handle_key_down(self, key):
        global current_language
        if self.state == GameState.BOOT:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.boot_screen.done = True

        elif self.state == GameState.LANG_SELECT:
            result = self.lang_screen.handle_input(key)
            if result:
                current_language = result
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.MAIN_MENU:
            if key == pygame.K_h:
                self.help_screen.previous_state = GameState.MAIN_MENU
                self.help_screen.scroll_y = 0
                self.state = GameState.HELP
                return
            result = self.menu_screen.handle_input(key)
            if result == "start":
                self.progression = ProgressionManager()
                self.char_select = CharacterSelectScreen(self.progression)
                self.city_map = CityMapScreen(self.progression)
                self.state = GameState.CHAR_SELECT
            elif result == "continue_game":
                self.state = GameState.CITY_MAP
            elif result == "select_char":
                self.state = GameState.CHAR_SELECT
            elif result == "options":
                self.options_screen.fullscreen_on = self.fullscreen
                lang_map = {"EN": 0, "ES": 1, "PT": 2}
                self.options_screen.lang_index = lang_map.get(current_language, 1)
                self.state = GameState.OPTIONS
            elif result == "quit":
                self.running = False

        elif self.state == GameState.OPTIONS:
            result = self.options_screen.handle_input(key)
            if result == "back":
                self.state = GameState.MAIN_MENU
            elif result == "credits":
                self.credits_screen.reset()
                self.state = GameState.CREDITS
            elif result == "toggle_fullscreen":
                self.fullscreen = self.options_screen.fullscreen_on
                if self.fullscreen:
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                else:
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            elif result == "toggle_screenshake":
                self.camera.shake_enabled = self.options_screen.screenshake_on

        elif self.state == GameState.HELP:
            if self.help_screen.handle_input(key):
                self.state = self.help_screen.previous_state or GameState.MAIN_MENU

        elif self.state == GameState.CHAR_SELECT:
            result = self.char_select.handle_input(key)
            if result:
                self.selected_char_class = result
                self.state = GameState.CITY_MAP
            elif key == pygame.K_ESCAPE:
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.CITY_MAP:
            result = self.city_map.handle_input(key)
            if result is not None:
                city = CITY_DATA[result]
                first_level = city["levels"][0]
                target_level = first_level
                for lv in range(first_level, city["levels"][1] + 1):
                    if lv not in self.progression.completed_levels:
                        target_level = lv
                        break
                else:
                    target_level = first_level
                self.cutscene.start(result)
                self.current_city_idx = result
                self.current_level_num = target_level
                self.state = GameState.CUTSCENE
            elif key == pygame.K_ESCAPE:
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.CUTSCENE:
            done = self.cutscene.skip()
            if done:
                self._start_level(self.current_level_num)

        elif self.state == GameState.PLAYING:
            if key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
                self.pause_selected = 0
            elif key == pygame.K_h:
                self.help_screen.previous_state = GameState.PLAYING
                self.help_screen.scroll_y = 0
                self.state = GameState.HELP
            elif key == pygame.K_e and self.current_level:
                near_install = False
                for ip in self.current_level.install_points:
                    if not ip.completed:
                        dx = self.player.x - ip.x
                        dy = self.player.y - ip.y
                        if abs(dx) < 50 and abs(dy) < 60:
                            near_install = True
                            jammer_pen = 0.0
                            for j in self.current_level.jammers:
                                if j.alive:
                                    jammer_pen += j.get_signal_penalty(ip.x, ip.y)
                            self.install_minigame.start(
                                self.player.character.install_skill, jammer_pen)
                            self.state = GameState.INSTALLING
                            break
                if not near_install and self.current_level:
                    self.player.handle_key_down(key, self.current_level.platforms,
                                                 self.current_level.cables,
                                                 self.current_level.poles)
            else:
                if self.current_level:
                    self.player.handle_key_down(key, self.current_level.platforms,
                                                 self.current_level.cables,
                                                 self.current_level.poles)

        elif self.state == GameState.INSTALLING:
            if key == pygame.K_SPACE:
                result = self.install_minigame.lock_signal()
                if result:
                    score = self.install_minigame.get_score()
                    self.player.score += score
                    self.level_install_score += score
                    for ip in self.current_level.install_points:
                        if not ip.completed:
                            dx = self.player.x - ip.x
                            dy = self.player.y - ip.y
                            if abs(dx) < 50 and abs(dy) < 60:
                                ip.completed = True
                                ip.result = result
                                break
                    if result == "EXCELLENT":
                        self.progression.record_excellent()
                    else:
                        self.progression.record_not_excellent()
                    self.particles.emit_signal(self.player.x, self.player.y - 30,
                                               SIGNAL_GOOD if result == "EXCELLENT" else YELLOW)

        elif self.state == GameState.PAUSED:
            if key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
            elif key == pygame.K_UP or key == pygame.K_DOWN:
                self.pause_selected = 1 - self.pause_selected
            elif key == pygame.K_RETURN:
                if self.pause_selected == 0:
                    self.state = GameState.PLAYING
                else:
                    self.state = GameState.MAIN_MENU

        elif self.state == GameState.LEVEL_COMPLETE:
            if self.level_complete_screen.handle_input(key):
                next_level = self.current_level_num + 1
                if next_level > 30:
                    self.credits_screen.reset()
                    self.state = GameState.CREDITS
                else:
                    next_city = get_city_for_level(next_level)
                    if next_city != self.current_city_idx:
                        self.cutscene.start(next_city)
                        self.current_city_idx = next_city
                        self.current_level_num = next_level
                        self.state = GameState.CUTSCENE
                    else:
                        self._start_level(next_level)

        elif self.state == GameState.GAME_OVER:
            result = self.game_over_screen.handle_input(key)
            if result == "retry":
                self._start_level(self.current_level_num)
            elif result == "quit":
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.CREDITS:
            if self.credits_screen.handle_input(key):
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.BOSS_FIGHT:
            if key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
                self.pause_selected = 0
            elif key == pygame.K_e:
                if self.boss_fight.try_install_antenna(self.player.x, self.player.y):
                    self.particles.emit_signal(self.player.x, self.player.y - 30, SIGNAL_GOOD)
            elif self.current_level:
                self.player.handle_key_down(key, self.current_level.platforms,
                                             self.current_level.cables,
                                             self.current_level.poles)

    def _handle_mouse_click(self, pos):
        if self.state == GameState.LANG_SELECT:
            result = self.lang_screen.handle_mouse(pos[0], pos[1], True)
            if result:
                global current_language
                current_language = result
                self.state = GameState.MAIN_MENU

    def update(self):
        dt = self.clock.get_time() / 1000.0
        dt = min(dt, 0.05)

        # Music management based on state
        if self.state in (GameState.MAIN_MENU, GameState.CHAR_SELECT, GameState.CITY_MAP,
                          GameState.LANG_SELECT, GameState.BOOT, GameState.OPTIONS,
                          GameState.HELP, GameState.CUTSCENE):
            self._ensure_music("menu")
        elif self.state in (GameState.PLAYING, GameState.INSTALLING, GameState.PAUSED):
            self._ensure_music("gameplay")
        elif self.state == GameState.BOSS_FIGHT:
            self._ensure_music("boss")
        elif self.state in (GameState.CREDITS, GameState.GAME_OVER, GameState.LEVEL_COMPLETE):
            self._ensure_music("menu")

        if self.state == GameState.BOOT:
            self.boot_screen.update(dt)
            if self.boot_screen.done:
                self.state = GameState.LANG_SELECT

        elif self.state == GameState.LANG_SELECT:
            pass

        elif self.state == GameState.MAIN_MENU:
            self.menu_screen.update(dt)

        elif self.state == GameState.OPTIONS:
            pass

        elif self.state == GameState.HELP:
            pass

        elif self.state == GameState.CHAR_SELECT:
            pass

        elif self.state == GameState.CITY_MAP:
            self.city_map.update(dt)

        elif self.state == GameState.CUTSCENE:
            self.cutscene.update(dt)
            if not self.cutscene.active:
                self._start_level(self.current_level_num)

        elif self.state == GameState.PLAYING:
            if not self.player or not self.current_level:
                return
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.update(self.current_level.platforms,
                               self.current_level.cables,
                               self.current_level.poles, dt)
            if getattr(self.player, 'footstep_triggered', False):
                self.audio.play_sound("footstep")
            self.camera.set_target(self.player.x, self.player.y)
            self.camera.update()
            self.weather.update(dt, self.camera)
            self.weather.apply_to_player(self.player)
            self.particles.update(dt)
            self.signal_level = self._compute_signal_level()
            self.hud.update(dt, self.player.score)
            for comp in self.current_level.competitors:
                comp.update(dt)
                comp_rect = comp.get_rect()
                pl_rect = self.player.get_rect()
                if comp_rect.colliderect(pl_rect):
                    if self.player.vy > 0 and self.player.y < comp.y - comp.height + 10:
                        self.player.vy = JUMP_FORCE * 0.7
                        self.player.score += BEAT_COMPETITOR
                        self.particles.emit_spark(comp.x + comp.width // 2, comp.y - comp.height)
                        comp.x = -999
                    else:
                        self.player.take_damage(20)
                        self.level_damage_taken = True
            for jammer in self.current_level.jammers:
                jammer.update(dt)
                if jammer.alive:
                    stomp_rect = jammer.get_stomp_rect()
                    if self.player.get_feet_rect().colliderect(stomp_rect) and self.player.vy > 0:
                        jammer.hit()
                        self.player.vy = JUMP_FORCE * 0.6
                        self.particles.emit_spark(jammer.x, jammer.y - jammer.height)
                        if not jammer.alive:
                            self.player.score += JAMMER_DESTROYED
                            self.progression.record_jammer_kill()
            for npc in self.current_level.npcs:
                npc.update(dt)
                npc.check_proximity(self.player.x, self.player.y)
            for ip in self.current_level.install_points:
                ip.update(dt)
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.player.die()
            if not self.player.alive:
                self.death_timer += dt
                if self.death_timer > 2.0:
                    if self.player.lives > 0:
                        self.player.respawn()
                        self.death_timer = 0.0
                    else:
                        self.game_over_screen.reset()
                        self.state = GameState.GAME_OVER
            if self.player.y > self.current_level.height + 100:
                self.player.take_damage(100)
                self.level_damage_taken = True
            all_installed = all(ip.completed for ip in self.current_level.install_points)
            if all_installed and self.exit_zone_rect:
                if self.player.get_rect().colliderect(self.exit_zone_rect):
                    self._complete_level()
            if self.player.on_ground and abs(self.player.vx) < 0.1:
                if self.player.anim_state != AnimState.IDLE:
                    self.player.anim_state = AnimState.IDLE
                    self.player.character.anim_state = AnimState.IDLE

        elif self.state == GameState.INSTALLING:
            self.install_minigame.update(1.0 / FPS)
            if not self.install_minigame.active:
                self.state = GameState.PLAYING

        elif self.state == GameState.PAUSED:
            pass

        elif self.state == GameState.LEVEL_COMPLETE:
            self.level_complete_screen.update(dt)

        elif self.state == GameState.GAME_OVER:
            self.game_over_screen.update(dt)

        elif self.state == GameState.CREDITS:
            self.credits_screen.update(dt)
            if self.credits_screen.done:
                self.state = GameState.MAIN_MENU

        elif self.state == GameState.BOSS_FIGHT:
            if not self.player or not self.current_level:
                return
            keys = pygame.key.get_pressed()
            if self.boss_fight.controls_swapped:
                swapped_keys = {
                    pygame.K_LEFT: pygame.K_RIGHT,
                    pygame.K_RIGHT: pygame.K_LEFT,
                    pygame.K_a: pygame.K_d,
                    pygame.K_d: pygame.K_a,
                }
                class SwappedKeys:
                    def __init__(self, original, swap_map):
                        self._original = original
                        self._swap = swap_map
                    def __getitem__(self, key):
                        return self._original[self._swap.get(key, key)]
                self.player.handle_input(SwappedKeys(keys, swapped_keys))
            else:
                self.player.handle_input(keys)
            self.player.update(self.current_level.platforms,
                               self.current_level.cables,
                               self.current_level.poles, dt)
            if getattr(self.player, 'footstep_triggered', False):
                self.audio.play_sound("footstep")
            self.camera.set_target(self.player.x, self.player.y)
            self.camera.update()
            self.boss_fight.update(dt, self.player)
            self.particles.update(dt)
            self.hud.update(dt, self.player.score)
            if self.boss_fight.defeated:
                self.progression.complete_level(30, self.player.score + 5000)
                self.save_manager.save(self.progression, current_language, self.menu_screen.easter_found)
                self.credits_screen.reset()
                self.state = GameState.CREDITS
            if not self.player.alive:
                self.death_timer += dt
                if self.death_timer > 2.0:
                    if self.player.lives > 0:
                        self.player.respawn()
                        self.death_timer = 0.0
                        self.boss_fight.start()
                    else:
                        self.game_over_screen.reset()
                        self.state = GameState.GAME_OVER

    def render(self):
        surface = self.screen

        if self.state == GameState.BOOT:
            self.boot_screen.draw(surface)

        elif self.state == GameState.LANG_SELECT:
            self.lang_screen.draw(surface)

        elif self.state == GameState.MAIN_MENU:
            self.menu_screen.draw(surface)

        elif self.state == GameState.CHAR_SELECT:
            self.char_select.draw(surface)

        elif self.state == GameState.CITY_MAP:
            self.city_map.draw(surface)

        elif self.state == GameState.CUTSCENE:
            self.cutscene.draw(surface)

        elif self.state == GameState.PLAYING:
            self._render_gameplay(surface)

        elif self.state == GameState.INSTALLING:
            self._render_gameplay(surface)
            self.install_minigame.draw(surface)

        elif self.state == GameState.PAUSED:
            self._render_gameplay(surface)
            self._render_pause_overlay(surface)

        elif self.state == GameState.LEVEL_COMPLETE:
            self.level_complete_screen.draw(surface)

        elif self.state == GameState.GAME_OVER:
            self.game_over_screen.draw(surface)

        elif self.state == GameState.CREDITS:
            self.credits_screen.draw(surface)

        elif self.state == GameState.BOSS_FIGHT:
            self._render_boss_gameplay(surface)

        elif self.state == GameState.OPTIONS:
            self.options_screen.draw(surface)

        elif self.state == GameState.HELP:
            # Draw the underlying screen first, then overlay help
            prev = self.help_screen.previous_state
            if prev == GameState.PLAYING:
                self._render_gameplay(surface)
            elif prev == GameState.MAIN_MENU:
                self.menu_screen.draw(surface)
            else:
                surface.fill(BLACK)
            self.help_screen.draw(surface)

        pygame.display.flip()

    def _render_gameplay(self, surface):
        if not self.current_level:
            surface.fill(SKY_DAY)
            return
        self.parallax.draw(surface, self.camera)
        for plat in self.current_level.platforms:
            plat.draw(surface, self.camera)
        for cable in self.current_level.cables:
            cable.draw(surface, self.camera)
        for pole in self.current_level.poles:
            pole.draw(surface, self.camera)
        for ip in self.current_level.install_points:
            ip.draw(surface, self.camera)
        for comp in self.current_level.competitors:
            comp.draw(surface, self.camera)
        for jammer in self.current_level.jammers:
            jammer.draw(surface, self.camera)
        for npc in self.current_level.npcs:
            npc.draw(surface, self.camera)
        if self.player:
            self.player.draw(surface, self.camera)
        self.weather.draw(surface, self.camera)
        self.weather.draw_wind_particles(surface, self.camera)
        self.particles.draw(surface, self.camera)
        if self.exit_zone_rect and self.current_level:
            all_installed = all(ip.completed for ip in self.current_level.install_points)
            if all_installed:
                ex, ey = self.camera.world_to_screen(self.exit_zone_rect.x, self.exit_zone_rect.y)
                exit_surf = pygame.Surface((60, 80), pygame.SRCALPHA)
                pulse = abs(math.sin(time.time() * 3)) * 0.4 + 0.3
                pygame.draw.rect(exit_surf, (0, 255, 120, int(100 * pulse)), (0, 0, 60, 80), border_radius=5)
                pygame.draw.rect(exit_surf, (0, 255, 120, 180), (0, 0, 60, 80), 3, border_radius=5)
                surface.blit(exit_surf, (ex, ey))
                arrow_font = pygame.font.Font(None, 30)
                arrow_txt = arrow_font.render(">>>", True, SIGNAL_GOOD)
                surface.blit(arrow_txt, (ex + 10, ey + 30))
        city_name = CITY_DATA.get(self.current_city_idx, CITY_DATA[0])["name"]
        self.hud.draw(surface, self.player, self.time_remaining,
                      city_name, self.current_level_num, self.signal_level)

    def _render_boss_gameplay(self, surface):
        if not self.current_level:
            surface.fill((30, 20, 50))
            return
        self.parallax.draw(surface, self.camera)
        for plat in self.current_level.platforms:
            plat.draw(surface, self.camera)
        if self.player:
            self.player.draw(surface, self.camera)
        self.boss_fight.draw(surface, self.camera)
        self.particles.draw(surface, self.camera)
        if self.player:
            city_name = CITY_DATA.get(self.current_city_idx, CITY_DATA[0])["name"]
            self.hud.draw(surface, self.player, self.time_remaining,
                          city_name, self.current_level_num, self.signal_level)

    def _render_pause_overlay(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
        surface.blit(overlay, (0, 0))
        font_large = pygame.font.Font(None, 64)
        font_option = pygame.font.Font(None, 40)
        pause_text = font_large.render(t("paused"), True, WHITE)
        surface.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 200))
        options = [t("resume"), t("main_menu")]
        for i, opt in enumerate(options):
            oy = 340 + i * 60
            color = CYAN if i == self.pause_selected else GRAY
            opt_surf = font_option.render(opt, True, color)
            surface.blit(opt_surf, (WIDTH // 2 - opt_surf.get_width() // 2, oy))
            if i == self.pause_selected:
                pygame.draw.rect(surface, CYAN,
                                 (WIDTH // 2 - 120, oy - 5, 240, 40), 2, border_radius=5)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
