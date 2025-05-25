# config.py

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "resources/sounds")
MAPPINGS_DIR = os.path.join(BASE_DIR, "resources/mappings")

# 默认的 GM 音色编号到音源组名映射
DEFAULT_PROGRAM_TO_GROUP = {
    0: "piano",
    24: "guitar",
    32: "bass",
    40: "violin",
    48: "string",
    56: "trumpet",
    60: "french_horn",
    64: "sax",
    73: "flute",
    75: "panpipe",
    80: "square_lead",
    118: "synth_drum",
    128: "drum_kit"  # 特例：channel 9 为打击乐器，可特殊处理
}



def get_available_sound_groups():
    groups = []
    if os.path.exists(SOUNDS_DIR):
        for name in os.listdir(SOUNDS_DIR):
            full_path = os.path.join(SOUNDS_DIR, name)
            if os.path.isdir(full_path):
                groups.append(name)
    return groups

AVAILABLE_SOUND_GROUPS = get_available_sound_groups()

DEFAULT_SOUND_GROUP = AVAILABLE_SOUND_GROUPS[0] if AVAILABLE_SOUND_GROUPS else "default"
