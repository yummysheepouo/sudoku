import pygame
import os

pygame.mixer.init()
# 定义音效文件目录
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

# 定义音效文件的路径
sound_click_path = os.path.join(SOUNDS_DIR, "click.wav")
sound_success_path = os.path.join(SOUNDS_DIR, "success.wav")
sound_error_path = os.path.join(SOUNDS_DIR, "error.wav")
sound_win_path = os.path.join(SOUNDS_DIR, "win.wav")
background_music_path = os.path.join(SOUNDS_DIR, "background.mp3")

# 检查音效文件是否存在
music_available = os.path.exists(background_music_path)

# 加载音效
def load_sound(filename):

    path = os.path.join(SOUNDS_DIR, filename)
    if os.path.exists(path):
        try:
            sound = pygame.mixer.Sound(path)
            print(f"Loaded sound: {filename}")
            return sound
        except Exception as e:
            print(f"Error loading sound {filename}: {e}")
    else:
        print(f"Sound not found: {filename}")
    return None

def initialize_background_music(volume):

    if music_available:
        try:
            pygame.mixer.music.load(background_music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)  # 无限循环播放背景音乐
            return True
        except Exception as e:
            print("Failed to start background music:", e)
    return False

# 加载各类音效
sound_click = load_sound("click.wav")
sound_success = load_sound("success.wav")
sound_error = load_sound("error.wav")
sound_win = load_sound("win.wav")