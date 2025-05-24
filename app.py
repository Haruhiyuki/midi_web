# app.py

import time

from midi.input_listener import MIDIInputListener


def run_listener():
    """
    运行MIDI和键盘监听模式，阻塞主线程
    """
    listener = MIDIInputListener()

    print("启动监听器，按 Ctrl+C 退出...")
    listener.start_listening()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("收到退出信号，停止监听...")
        listener.stop_listening()


if __name__ == "__main__":
    run_listener()
