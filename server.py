# server.py

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import Dict
import uuid
import os

from sound.sound_manager import SoundManager
from sound.sound_mapping import SoundMapping
from midi.midi_player import MidiPlayer
import config

app = FastAPI(title="MIDI 键盘音源接口")

# 初始化映射与播放管理器
sound_mapping = SoundMapping()
sound_manager = SoundManager(sound_mapping)

# 全局缓存，用 session_id 关联 MidiPlayer 实例
midi_sessions = {}

UPLOAD_DIR = "resources/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 请求模型
class NoteRequest(BaseModel):
    note: int
    velocity: int = 100


class NoteGroupRequest(BaseModel):
    note: int
    group: str


class MappingDictRequest(BaseModel):
    mapping_dict: Dict[int, str]


@app.post("/play_note")
def play_note(req: NoteRequest):
    """
    播放一个音符（支持力度）
    """
    try:
        sound_manager.play_note(note=req.note, velocity=req.velocity)  # 传入力度
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"播放失败: {e}")

@app.get("/refresh_sound_groups/")
def refresh_sound_groups():
    """
    刷新并返回当前存在的音源组
    """
    try:
        groups = config.get_available_sound_groups()
        return {"available_sound_groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新失败: {e}")

@app.post("/set_note_group")
def set_note_group(req: NoteGroupRequest):
    """
    设置单个音符的音源组
    """
    try:
        sound_manager.set_note_group(req.note, req.group)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"设置失败: {e}")


@app.get("/get_note_group")
def get_note_group(note: int):
    """
    获取某个音符当前的音源组
    """
    try:
        group = sound_manager.get_note_group(note)
        return {"note": note, "group": group}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"获取失败: {e}")


@app.post("/reset_mapping")
def reset_mapping():
    """
    重置所有音符的映射为默认组
    """
    try:
        sound_mapping.reset_all()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置失败: {e}")

@app.post("/save_mapping/")
def save_mapping(name: str):
    """
    保存用户当前的映射组
    """
    try:
        sound_mapping.save_mapping_to_file(name)
        return {"message": f"映射已保存为 {name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load_mapping/")
def load_mapping(name: str):
    """
    加载指定映射组
    """
    try:
        sound_mapping.load_mapping_from_file(name)
        return {"message": f"已加载映射: {name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_mappings/")
def list_mappings():
    """
    获取映射组列表
    """
    try:
        mappings = sound_mapping.list_saved_mappings()
        return {"mappings": mappings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_midi/")
async def upload_midi(file: UploadFile = File(...)):
    """
    上传 MIDI 文件，保存，生成 MidiPlayer 并缓存，返回 session_id
    """
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())

        player = MidiPlayer(file_location)
        session_id = str(uuid.uuid4())
        midi_sessions[session_id] = player

        return {"session_id": session_id, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {e}")

@app.post("/parse_midi/")
async def parse_midi(session_id: str = Form(...)):
    """
    解析指定 session_id 对应的 MIDI 文件，返回事件和通道乐器信息
    """
    player = midi_sessions.get(session_id)
    if player is None:
        raise HTTPException(status_code=404, detail="无效的 session_id 或会话已过期")

    try:
        player.parse()

        events = [
            {
                "time": round(e.time, 3),
                "type": e.type,
                "channel": e.channel,
                "note": e.note,
                "velocity": e.velocity,
                "program": e.program,
                "group": player.get_group_name_by_program(e.program) if e.program is not None else None
            }
            for e in player.get_events()
        ]

        channel_programs = player.get_channel_programs()

        return {
            "filename": os.path.basename(player.file_path),
            "events": events,
            "channel_programs": channel_programs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {e}")

@app.post("/play_midi/")
def play_midi(session_id: str):
    """
    伪代码，待实现
    """
    player = midi_sessions.get(session_id)
    if not player:
        raise HTTPException(status_code=404, detail="Session不存在")
    player.play()
    return {"status": "playing"}

@app.get("/get_group_by_program/")
async def get_group_by_program(session_id: str = Query(...), program: int = Query(...)):
    """
    查询指定 session_id 会话中 MIDI 音色编号对应的音源组
    """
    player = midi_sessions.get(session_id)
    if player is None:
        raise HTTPException(status_code=404, detail="无效的 session_id 或会话已过期")

    group = player.get_group_name_by_program(program)
    if group is None:
        return {"program": program, "group": None, "message": "未找到对应音源组"}
    else:
        return {"program": program, "group": group}

@app.post("/set_instrument_mapping/")
def set_mapping(session_id: str, mapping: Dict[int, str]):
    player = midi_sessions.get(session_id)
    if not player:
        raise HTTPException(status_code=404, detail="Session不存在")
    player.set_instrument_mapping(mapping)
    return {"status": "ok"}

@app.post("/cleanup/")
def cleanup(session_id: str):
    if session_id in midi_sessions:
        del midi_sessions[session_id]
    return {"status": "cleaned"}