# config.py

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "resources/sounds")
MAPPINGS_DIR = os.path.join(BASE_DIR, "resources/mappings")

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
