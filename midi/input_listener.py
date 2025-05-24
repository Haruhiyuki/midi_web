# midi/input_listener.py

import mido
import threading
import keyboard
from sound.sound_mapping import SoundMapping
from sound.sound_manager import SoundManager

# 默认的键盘键位映射：键盘按键 → MIDI音符编号
# 这一映射可用于在无MIDI设备的环境下通过键盘演奏音符
DEFAULT_KEYBOARD_MAPPING = {
    'z': 60,  # C4
    's': 61,  # C#4
    'x': 62,  # D4
    'd': 63,  # D#4
    'c': 64,  # E4
    'v': 65,  # F4
    'g': 66,  # F#4
    'b': 67,  # G4
    'h': 68,  # G#4
    'n': 69,  # A4
    'j': 70,  # A#4
    'm': 71,  # B4
    'q': 72   # C5
}


class MIDIInputListener:
    """
    支持同时监听 MIDI 输入设备与电脑键盘输入的监听器
    接收到音符后调用 SoundManager 播放对应音频
    """

    def __init__(self, keyboard_mapping=None):
        # 初始化音符映射和声音管理器
        self.mapping = SoundMapping()
        self.sound_manager = SoundManager(self.mapping)
        # 使用用户自定义或默认的键盘映射
        self.keyboard_mapping = keyboard_mapping or DEFAULT_KEYBOARD_MAPPING

        # 控制线程运行状态
        self.running = False
        self.midi_thread = None
        self.keyboard_thread = None

    def list_devices(self):
        """
        列出所有可用的MIDI输入设备
        """
        inputs = mido.get_input_names()
        print("可用 MIDI 输入设备:")
        for idx, name in enumerate(inputs):
            print(f"{idx}: {name}")
        return inputs

    def start_midi_listening(self, device_name=None):
        """
        启动 MIDI 输入监听线程，可选指定设备名称
        """

        def midi_loop():
            try:
                with mido.open_input(device_name) as inport:
                    print(f"[MIDI] 监听设备: {device_name or '默认'}")
                    for msg in inport:
                        if not self.running:
                            break
                        if msg.type == 'note_on' and msg.velocity > 0:
                            self.sound_manager.play_note(msg.note)
            except Exception as e:
                print(f"[MIDI] 监听失败: {e}")

        # 启动后台线程
        self.midi_thread = threading.Thread(target=midi_loop, daemon=True)
        self.midi_thread.start()

    def start_keyboard_listening(self):
        """
        启动键盘输入监听线程
        """

        def keyboard_loop():
            print("[键盘] 监听启动，可按 z/s/x/d/c... 进行测试")
            while self.running:
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN:
                    key = event.name.lower()
                    if key in self.keyboard_mapping:
                        note = self.keyboard_mapping[key]
                        self.sound_manager.play_note(note)

        # 启动后台线程
        self.keyboard_thread = threading.Thread(target=keyboard_loop, daemon=True)
        self.keyboard_thread.start()

    def start_listening(self, device_name=None):
        """
        启动 MIDI 和键盘监听
        """
        self.running = True
        self.start_midi_listening(device_name)
        self.start_keyboard_listening()

    def stop_listening(self):
        """
        停止监听线程
        """
        self.running = False
        if self.midi_thread and self.midi_thread.is_alive():
            self.midi_thread.join()
        if self.keyboard_thread and self.keyboard_thread.is_alive():
            self.keyboard_thread.join()
        print("监听已停止")
