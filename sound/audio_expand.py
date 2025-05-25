import os
import librosa
import soundfile as sf

INPUT_DIR = "resources/sounds/lalala"
OUTPUT_DIR = "resources/sounds/expanded_88"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载已有样本：假设命名为 60.wav, 61.wav...
existing_samples = {}
for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".wav"):
        midi = int(filename.replace(".wav", ""))
        path = os.path.join(INPUT_DIR, filename)
        y, sr = librosa.load(path, sr=None)
        existing_samples[midi] = (y, sr)

# 所有目标键：21 ~ 108
for target_midi in range(21, 109):
    out_path = os.path.join(OUTPUT_DIR, f"{target_midi}.wav")

    # 如果输出文件已存在，跳过
    if os.path.exists(out_path):
        continue

    # 找最近的已录制样本
    closest_midi = min(existing_samples.keys(), key=lambda x: abs(x - target_midi))
    y_base, sr = existing_samples[closest_midi]
    n_steps = target_midi - closest_midi  # 半音差

    # 使用 librosa 进行音高变换
    y_shifted = librosa.effects.pitch_shift(y_base, sr=sr, n_steps=n_steps)

    # 保存新音频
    sf.write(out_path, y_shifted, sr)
    print(f"生成 {target_midi}.wav，基于 {closest_midi}.wav，变调 {n_steps:+} 半音")
