# server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

from sound.sound_manager import SoundManager
from sound.sound_mapping import SoundMapping
import config

app = FastAPI(title="MIDI 键盘音源接口")

# 初始化映射与播放管理器
sound_mapping = SoundMapping()
sound_manager = SoundManager(sound_mapping)


# 请求模型
class NoteRequest(BaseModel):
    note: int


class NoteGroupRequest(BaseModel):
    note: int
    group: str


class MappingDictRequest(BaseModel):
    mapping_dict: Dict[int, str]


@app.post("/play_note")
def play_note(req: NoteRequest):
    """
    播放一个音符
    """
    try:
        sound_manager.play_note(req.note)
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