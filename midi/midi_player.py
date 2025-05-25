# midi/midi_player.py

import mido
from typing import List, Dict, Any, Optional
from config import DEFAULT_PROGRAM_TO_GROUP


class MidiEvent:
    def __init__(self, time: float, type: str, channel: Optional[int] = None,
                 note: Optional[int] = None, velocity: Optional[int] = None,
                 program: Optional[int] = None):
        self.time = time
        self.type = type
        self.channel = channel
        self.note = note
        self.velocity = velocity
        self.program = program

    def __repr__(self):
        return f"<MidiEvent time={self.time:.3f} type={self.type} " \
               f"channel={self.channel} note={self.note} velocity={self.velocity} program={self.program}>"


class MidiPlayer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.midi = mido.MidiFile(file_path)
        self.ticks_per_beat = self.midi.ticks_per_beat
        self.tempo = 500000
        self.events: List[MidiEvent] = []
        self.channel_programs: Dict[int, int] = {}
        self.instrument_mapping: Dict[int, str] = DEFAULT_PROGRAM_TO_GROUP.copy()  # 映射音源组：type 0 为音符编号，type 1 为轨道编号

    def ticks_to_seconds(self, ticks: int) -> float:
        return ticks * (self.tempo / self.ticks_per_beat) / 1_000_000

    def parse(self):
        if self.midi.type == 0:
            self._parse_type0()
        elif self.midi.type == 1:
            self._parse_type1()
        else:
            raise ValueError(f"不支持的MIDI类型: {self.midi.type}")
        self.events.sort(key=lambda e: e.time)

    def _parse_type0(self):
        abs_time_ticks = 0
        for msg in self.midi.tracks[0]:
            abs_time_ticks += msg.time
            if msg.type == 'set_tempo':
                self.tempo = msg.tempo
            elif not msg.is_meta:
                time_sec = self.ticks_to_seconds(abs_time_ticks)
                self._handle_msg(msg, time_sec)

    def _parse_type1(self):
        temp_events: List[MidiEvent] = []
        for track_index, track in enumerate(self.midi.tracks):
            abs_time_ticks = 0
            for msg in track:
                abs_time_ticks += msg.time
                if msg.type == 'set_tempo':
                    self.tempo = msg.tempo
                elif not msg.is_meta:
                    time_sec = self.ticks_to_seconds(abs_time_ticks)
                    event = self._create_event(msg, time_sec)
                    if event:
                        temp_events.append(event)
        self.events = temp_events

    def _handle_msg(self, msg, time_sec):
        event = self._create_event(msg, time_sec)
        if event:
            self.events.append(event)

    def _create_event(self, msg, time_sec) -> Optional[MidiEvent]:
        if msg.type == 'note_on':
            program = self.channel_programs.get(msg.channel, 0)
            return MidiEvent(time_sec, 'note_on', msg.channel, msg.note, msg.velocity, program=program)
        elif msg.type == 'note_off':
            program = self.channel_programs.get(msg.channel, 0)
            return MidiEvent(time_sec, 'note_off', msg.channel, msg.note, msg.velocity, program=program)
        elif msg.type == 'program_change':
            self.channel_programs[msg.channel] = msg.program
            return MidiEvent(time_sec, 'program_change', msg.channel, program=msg.program)
        return None

    def get_events(self) -> List[MidiEvent]:
        return self.events

    def get_channel_programs(self) -> Dict[int, int]:
        return self.channel_programs

    def get_type(self) -> int:
        return self.midi.type

    def get_track_instruments(self) -> Dict[int, int]:
        if self.midi.type == 1:
            instruments = {}
            for i, track in enumerate(self.midi.tracks):
                for msg in track:
                    if msg.type == 'program_change':
                        instruments[i] = msg.program
                        break
            return instruments
        elif self.midi.type == 0:
            return {0: self.channel_programs.get(0, 0)}
        else:
            raise ValueError("不支持的MIDI类型")

    def get_mapping(self) -> Dict[int, str]:
        return self.instrument_mapping

    def get_group_name_by_program(self, program_id: int) -> Optional[str]:
        """
        根据 MIDI 的 program number 获取映射的音源组 group_name。
        """
        return self.instrument_mapping.get(program_id)

    def set_instrument_mapping(self, mapping: Dict[int, str]):
        """
        批量设置 instrument_mapping，允许外部动态更新。
        """
        self.instrument_mapping = mapping
