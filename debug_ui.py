
import streamlit as st
import requests

API_URL = "http://localhost:8000"  # 根据实际服务地址修改

st.set_page_config(page_title="MIDI 调试界面", layout="centered")
st.title("🎹 MIDI 键盘调试工具")

st.markdown("## ▶️ 测试功能")

# --- 播放音符 ---
st.subheader("播放音符")
note_to_play = st.number_input("MIDI 音符编号 (0~127)", min_value=0, max_value=127, value=60, step=1)
if st.button("播放"):
    try:
        r = requests.post(f"{API_URL}/play_note", json={"note": note_to_play})
        st.success("播放成功" if r.ok else r.text)
    except Exception as e:
        st.error(f"请求失败：{e}")

# --- 设置音源组 ---
st.subheader("设置音源组")

# 用于保存音源组选项
if "sound_groups" not in st.session_state:
    try:
        r = requests.get(f"{API_URL}/refresh_sound_groups/")
        st.session_state.sound_groups = r.json().get("available_sound_groups", [])
    except Exception as e:
        st.session_state.sound_groups = []
        st.warning(f"加载音源组失败：{e}")

# 刷新按钮
if st.button("🔄 刷新音源组列表"):
    try:
        r = requests.get(f"{API_URL}/refresh_sound_groups/")
        st.session_state.sound_groups = r.json().get("available_sound_groups", [])
        st.success("音源组已刷新")
    except Exception as e:
        st.error(f"刷新失败：{e}")

# 下拉选择音源组
note_to_set = st.number_input("设置音符编号", min_value=0, max_value=127, value=60, step=1, key="set_note")
group_to_set = st.selectbox("选择音源组", st.session_state.sound_groups if st.session_state.sound_groups else ["default"])

if st.button("设置组"):
    try:
        r = requests.post(f"{API_URL}/set_note_group", json={"note": note_to_set, "group": group_to_set})
        st.success("设置成功" if r.ok else r.text)
    except Exception as e:
        st.error(f"请求失败：{e}")

# --- 获取音源组 ---
st.subheader("获取音符音源组")
note_to_get = st.number_input("查询音符编号", min_value=0, max_value=127, value=60, step=1, key="get_note")
if st.button("查询组"):
    try:
        r = requests.get(f"{API_URL}/get_note_group", params={"note": note_to_get})
        data = r.json()
        st.write(f"音符 {data['note']} 当前音源组: **{data['group']}**" if r.ok else r.text)
    except Exception as e:
        st.error(f"请求失败：{e}")

# --- 重置映射 ---
st.subheader("重置映射")
if st.button("重置所有音符映射"):
    try:
        r = requests.post(f"{API_URL}/reset_mapping")
        st.success("映射重置成功" if r.ok else r.text)
    except Exception as e:
        st.error(f"请求失败：{e}")

# --- 保存映射 ---
st.subheader("保存映射")
save_name = st.text_input("保存为映射组名", value="my_mapping")
if st.button("保存映射组"):
    try:
        r = requests.post(f"{API_URL}/save_mapping/", params={"name": save_name})
        st.success(r.json().get("message", "保存成功") if r.ok else r.text)
    except Exception as e:
        st.error(f"请求失败：{e}")

# --- 加载映射 ---
st.subheader("加载映射")
load_name = st.text_input("加载映射组名", value="my_mapping")
if st.button("加载映射组"):
    try:
        r = requests.post(f"{API_URL}/load_mapping/", params={"name": load_name})
        st.success(r.json().get("message", "加载成功") if r.ok else r.text)
    except Exception as e:
        st.error(f"请求失败：{e}")

# --- 映射列表 ---
st.subheader("映射列表")
if st.button("列出所有映射组"):
    try:
        r = requests.get(f"{API_URL}/list_mappings/")
        if r.ok:
            mappings = r.json().get("mappings", [])
            st.write("可用映射组：", mappings)
        else:
            st.error(r.text)
    except Exception as e:
        st.error(f"请求失败：{e}")

# --- 解析 MIDI 文件 ---
st.subheader("解析 MIDI 文件")
uploaded_file = st.file_uploader("上传 .mid 文件进行解析", type=["mid", "midi"])

if uploaded_file is not None:
    if st.button("开始解析"):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            r = requests.post(f"{API_URL}/parse_midi/", files=files)
            if r.ok:
                result = r.json()
                st.success(f"解析成功！文件名: {result['filename']}")
                st.markdown("### 通道乐器映射")
                st.json(result["channel_programs"])
                st.markdown("### 音符事件（前20条）")
                st.json(result["events"][:20])
            else:
                st.error(f"解析失败：{r.text}")
        except Exception as e:
            st.error(f"请求失败：{e}")