# sound/sound_mapping.py

import os
import json
import config

class SoundMapping:
    """
    管理 MIDI 音符（0-127）到音源组名称的映射关系
    """

    def __init__(self):
        # 初始化时全部默认映射到 config.DEFAULT_SOUND_GROUP
        self.mapping = {i: config.DEFAULT_SOUND_GROUP for i in range(128)}

    def get_group(self, note: int) -> str:
        """
        获取某个MIDI音符对应的音源组
        """
        if note < 0 or note > 127:
            raise ValueError("Note 必须在0-127之间")
        return self.mapping.get(note, config.DEFAULT_SOUND_GROUP)

    def set_group(self, note: int, group: str):
        """
        设置某个MIDI音符对应的音源组
        """
        if note < 0 or note > 127:
            raise ValueError("Note 必须在0-127之间")
        if group not in config.AVAILABLE_SOUND_GROUPS:
            raise ValueError(f"无效的音源组: {group}")
        self.mapping[note] = group

    def reset_all(self):
        """
        重置所有MIDI音符映射为默认组
        """
        self.mapping = {i: config.DEFAULT_SOUND_GROUP for i in range(128)}

    def get_note_sound_path(self, note: int) -> str:
        """
        根据MIDI音符编号返回对应的声音文件路径
        文件名统一为 0.wav ~ 127.wav，和 MIDI 音符编号对应
        """
        group = self.get_group(note)
        filename = f"{note}.wav"  # 直接用note编号，不加1
        return f"{config.SOUNDS_DIR}/{group}/{filename}"

    def load_mapping_from_dict(self, mapping_dict: dict):
        """
        用户当前手动设置的映射组默认保存在mapping_dict
        用一个字典批量设置映射，key是note，value是group
        """
        for note, group in mapping_dict.items():
            self.set_group(note, group)

    def to_dict(self) -> dict:
        """
        返回当前映射的字典形式
        """
        return self.mapping.copy()

    def save_mapping_to_file(self, name: str):
        """
        将当前的映射保存为一个 JSON 文件
        """
        os.makedirs(config.MAPPINGS_DIR, exist_ok=True)
        path = os.path.join(config.MAPPINGS_DIR, f"{name}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f, indent=2)
        print(f"[映射保存] 保存至: {path}")

    def load_mapping_from_file(self, name: str):
        """
        从 JSON 文件加载映射
        """
        path = os.path.join(config.MAPPINGS_DIR, f"{name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"映射文件不存在: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            raw_dict = json.load(f)
        # 转换键为 int 类型
        mapping_dict = {int(k): v for k, v in raw_dict.items()}
        self.load_mapping_from_dict(mapping_dict)
        print(f"[映射加载] 加载自: {path}")

    def list_saved_mappings(self):
        """
        返回所有保存的映射名（不带扩展名）
        """
        if not os.path.exists(config.MAPPINGS_DIR):
            return []
        return [
            f[:-5] for f in os.listdir(config.MAPPINGS_DIR)
            if f.endswith('.json')
        ]