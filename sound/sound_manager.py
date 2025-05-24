# sound/sound_manager.py

import os
from threading import Lock
from pydub import AudioSegment
import simpleaudio as sa
from sound.sound_mapping import SoundMapping

class SoundManager:
    def __init__(self, sound_mapping: SoundMapping):
        self.lock = Lock()
        self.sound_cache = {}  # key: (note, group)
        self.play_objects = []
        self.sound_mapping = sound_mapping

    def load_sound(self, note: int):
        group = self.sound_mapping.get_group(note)
        if not group:
            raise ValueError(f"音源组未定义，note={note}")
        key = (note, group)
        if key in self.sound_cache:
            return self.sound_cache[key]

        path = self.sound_mapping.get_note_sound_path(note)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"未找到声音文件: {path}")

        audio = AudioSegment.from_wav(path)
        self.sound_cache[key] = audio
        return audio

    def play_note(self, note: int):
        try:
            with self.lock:
                audio = self.load_sound(note)
                play_obj = sa.play_buffer(
                    audio.raw_data,
                    num_channels=audio.channels,
                    bytes_per_sample=audio.sample_width,
                    sample_rate=audio.frame_rate
                )
                self.play_objects.append(play_obj)
                self.play_objects = [obj for obj in self.play_objects if obj.is_playing()]
        except Exception as e:
            print(f"播放音符失败: {e}")

    def set_note_group(self, note: int, group: str):
        self.sound_mapping.set_group(note, group)
        # 清理缓存，强制重新加载
        key = (note, group)
        if key in self.sound_cache:
            del self.sound_cache[key]

    def get_note_group(self, note: int) -> str:
        return self.sound_mapping.get_group(note)
