import pygame
import sys
import os
import time
import random
import json

# Initialize pygame and mixer for sounds
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 750
GRID_SIZE = 450
CELL_SIZE = GRID_SIZE // 9
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE) // 2
GRID_OFFSET_Y = 120
BUTTON_HEIGHT = 45
BUTTON_WIDTH = 160
BUTTON_MARGIN = 15
BUTTON_ROW_MARGIN = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)
BLUE = (65, 105, 225)
LIGHT_BLUE = (173, 216, 230)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
YELLOW = (255, 215, 0)
PURPLE = (147, 112, 219)
BACKGROUND = (240, 248, 255)
SHADOW = (150, 150, 150)
ALERT_BG = (255, 255, 255, 200)
OVERLAY_BG = (0, 0, 0, 150)
DISABLED_GRAY = (200, 200, 200)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUZZLE_DIR = os.path.join(BASE_DIR, "puzzle")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
SETTINGS_ICON_PATH = os.path.join("./img/settings.png")  

# Difficulty and hints
DIFFICULTY_LEVELS = {"beginner": 60, "normal": 40, "advanced": 20}
HINT_LIMITS = {"beginner": 7, "normal": 5, "advanced": 3}

# Required sound filenames
REQUIRED_SOUNDS = ["click.wav", "success.wav", "error.wav", "background.mp3", "win.wav"]

# Utility: load settings from file (if exists), otherwise defaults
def load_settings():
    defaults = {"bg_volume": 1.0, "sfx_volume": 1.0}
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
                bg = float(data.get("bg_volume", defaults["bg_volume"]))
                sfx = float(data.get("sfx_volume", defaults["sfx_volume"]))
                return {"bg_volume": max(0.0, min(1.0, bg)), "sfx_volume": max(0.0, min(1.0, sfx))}
    except Exception as e:
        print("Failed to load settings:", e)
    return defaults

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print("Failed to save settings:", e)

# Load sound helper
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

# Initialize sound directory if missing
def ensure_sounds_dir():
    if not os.path.exists(SOUNDS_DIR):
        os.makedirs(SOUNDS_DIR)

ensure_sounds_dir()

# Load settings (persisted)
persisted_settings = load_settings()

# Load sound assets (some may be missing — code handles that)
sound_click = load_sound("click.wav")
sound_success = load_sound("success.wav")
sound_error = load_sound("error.wav")
sound_win = load_sound("win.wav")
# For background music, we'll prefer using pygame.mixer.music if background.mp3 exists in sounds
background_music_path = os.path.join(SOUNDS_DIR, "background.mp3")
if os.path.exists(background_music_path):
    try:
        pygame.mixer.music.load(background_music_path)
        pygame.mixer.music.set_volume(persisted_settings["bg_volume"])
        pygame.mixer.music.play(-1)
        music_available = True
    except Exception as e:
        print("Failed to start background music:", e)
        music_available = False
else:
    music_available = False

# Apply sfx volume to loaded Sound objects
for s in (sound_click, sound_success, sound_error, sound_win):
    if s:
        s.set_volume(persisted_settings["sfx_volume"])

# Puzzle contents (same as before)
PUZZLE_CONTENTS = {
    "puzzle1.txt":[ "476598312","852961437","394287615","719854632","263693814","648125739","921346827","137782469","586473915"],
    "puzzle1S.txt":[ "476598312","852961437","394287615","719854632","263693814","648125739","921346827","137782469","586473915"],
    "puzzle2.txt":[ "381654729","729381564","564729318","693217845","857496213","412835697","248913675","175264938","936748251"],
    "puzzle2S.txt":[ "381654729","729381564","564729318","693217845","857496213","412835697","248913675","175264938","936748251"],
    "puzzle3.txt":[ "219348765","765219348","348765219","672984513","984513672","513672984","456723198","897146235","132895476"],
    "puzzle3S.txt":[ "219348765","765219348","348765219","672984513","984513672","513672984","456723198","897146235","132895476"],
    "puzzle4.txt":[ "123456789","456789123","789123456","234567891","567891234","891234567","345678912","678912345","912345678"],
    "puzzle4S.txt":[ "123456789","456789123","789123456","234567891","567891234","891234567","345678912","678912345","912345678"],
    "puzzle5.txt":[ "534678912","672195348","198342567","859761423","426853791","713924856","961537284","287419635","345286179"],
    "puzzle5S.txt":[ "534678912","672195348","198342567","859761423","426853791","713924856","961537284","287419635","345286179"],
    "puzzle6.txt":[ "795836421","431297856","286145397","814753962","659421738","372968145","928514673","163782594","547693281"],
    "puzzle6S.txt":[ "795836421","431297856","286145397","814753962","659421738","372968145","928514673","163782594","547693281"]
}

def initialize_puzzle_files():
    if not os.path.exists(PUZZLE_DIR):
        os.makedirs(PUZZLE_DIR)
    for filename, content in PUZZLE_CONTENTS.items():
        file_path = os.path.join(PUZZLE_DIR, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                for line in content:
                    f.write(line + "\n")

def randomize_puzzle(puzzle, difficulty):
    puzzle_copy = [row[:] for row in puzzle]
    cells_to_hide = 81 - DIFFICULTY_LEVELS.get(difficulty, 40)
    all_positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(all_positions)
    for i in range(min(cells_to_hide, 81)):
        r, c = all_positions[i]
        puzzle_copy[r][c] = '.'
    return puzzle_copy

# UI building blocks
class Button:
    def __init__(self, x, y, w, h, text="", color=LIGHT_GRAY, hover_color=GRAY, action=None, font_size=22, enabled=True, animated=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.SysFont("Arial", font_size)
        self.is_hovered = False
        self.enabled = enabled
        # animation support for settings fallback button
        self.animated = animated
        self.is_pressed = False
        self.press_offset = 0

    def draw(self, screen):
        # apply press offset if animated
        draw_rect = self.rect.copy()
        if self.animated and self.is_pressed:
            draw_rect = draw_rect.move(0, 4)
        if not self.enabled:
            col = DISABLED_GRAY
            txt_col = GRAY
        else:
            col = self.hover_color if self.is_hovered else self.color
            txt_col = BLACK
        shadow = draw_rect.move(2,2)
        pygame.draw.rect(screen, SHADOW, shadow, border_radius=6)
        pygame.draw.rect(screen, col, draw_rect, border_radius=6)
        pygame.draw.rect(screen, DARK_GRAY, draw_rect, 2, border_radius=6)
        if self.text:
            surf = self.font.render(self.text, True, txt_col)
            screen.blit(surf, surf.get_rect(center=draw_rect.center))

    def check_hover(self, pos):
        if not self.enabled:
            self.is_hovered = False
            return False
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    # Note: for animated button we handle press on MOUSEBUTTONDOWN/UP in handle_event
    def handle_event(self, event):
        if not self.enabled:
            return False
        if self.animated:
            # press animation behavior: set is_pressed on down, call action on release if hovered
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
                self.is_pressed = True
                return False
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_pressed:
                    self.is_pressed = False
                    if self.is_hovered:
                        if sound_click:
                            sound_click.play()
                        if self.action:
                            return self.action()
                return False
            return False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
                if sound_click:
                    sound_click.play()
                if self.action:
                    return self.action()
        return False

class ImageButton:
    def __init__(self, x, y, image_surf, action=None, size=40, animated=False):
        self.x = x
        self.y = y
        self.size = size
        self.action = action
        self.image = None
        if image_surf:
            self.image = pygame.transform.smoothscale(image_surf, (size, size))
        self.rect = pygame.Rect(x, y, size, size)
        self.is_hovered = False
        self.animated = animated
        self.is_pressed = False
        self.pulse = 0.0  # optional small pulse
        self.last_pulse_time = time.time()

    def draw(self, screen):
        # compute press offset & scale when pressed
        draw_rect = self.rect.copy()
        scale = 1.0
        if self.animated and self.is_pressed:
            draw_rect = draw_rect.move(0, 4)
            scale = 0.95
        # shadow
        shadow_rect = draw_rect.move(2, 2)
        pygame.draw.rect(screen, SHADOW, shadow_rect, border_radius=6)
        if self.image:
            # optionally scale image a bit when pressed
            if scale != 1.0:
                w = int(self.size * scale)
                h = int(self.size * scale)
                img = pygame.transform.smoothscale(self.image, (w, h))
                img_pos = (draw_rect.centerx - w//2, draw_rect.centery - h//2)
                screen.blit(img, img_pos)
            else:
                screen.blit(self.image, draw_rect.topleft)
            pygame.draw.rect(screen, DARK_GRAY, draw_rect, 2, border_radius=6)
            if self.is_hovered:
                # darken overlay to indicate hover
                overlay = pygame.Surface((draw_rect.w, draw_rect.h), pygame.SRCALPHA)
                overlay.fill((0,0,0,40))
                screen.blit(overlay, draw_rect.topleft)
        else:
            pygame.draw.rect(screen, LIGHT_GRAY, draw_rect, border_radius=6)
            pygame.draw.rect(screen, DARK_GRAY, draw_rect, 2, border_radius=6)
            f = pygame.font.SysFont("Arial", 18)
            surf = f.render("Settings", True, BLACK)
            screen.blit(surf, surf.get_rect(center=draw_rect.center))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    # Animated press: set is_pressed on MOUSEBUTTONDOWN, on MOUSEBUTTONUP trigger action if released on button
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.is_pressed = True
            return False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed:
                self.is_pressed = False
                if self.is_hovered:
                    if sound_click:
                        sound_click.play()
                    if self.action:
                        return self.action()
        return False

class Slider:
    def __init__(self, x, y, w, value=1.0):
        self.rect = pygame.Rect(x, y, w, 8)
        self.knob_radius = 10
        self.value = max(0.0, min(1.0, value))
        self.dragging = False

    def draw(self, screen):
        # track
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=4)
        filled = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.w * self.value), self.rect.h)
        pygame.draw.rect(screen, LIGHT_BLUE, filled, border_radius=4)
        # knob
        kx = self.rect.x + int(self.rect.w * self.value)
        ky = self.rect.centery
        pygame.draw.circle(screen, WHITE, (kx, ky), self.knob_radius)
        pygame.draw.circle(screen, DARK_GRAY, (kx, ky), self.knob_radius, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # if clicking near knob or on track
            if pygame.Rect(self.rect.x - 5, self.rect.y - 10, self.rect.w + 10, self.rect.h + 20).collidepoint((mx, my)):
                self.dragging = True
                self.update_value(mx)
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        return False

    def update_value(self, mx):
        rel = (mx - self.rect.x) / self.rect.w
        self.value = max(0.0, min(1.0, rel))

# Dialogs
class SettingsDialog:
    def __init__(self, game, width=480, height=260):
        self.game = game
        self.width = width
        self.height = height
        self.rect = pygame.Rect((SCREEN_WIDTH - width)//2, (SCREEN_HEIGHT - height)//2, width, height)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.label_font = pygame.font.SysFont("Arial", 20)
        # sliders initial from game's persisted volumes
        self.bg_slider = Slider(self.rect.x + 40, self.rect.y + 80, self.width - 80, value=self.game.bg_volume)
        self.sfx_slider = Slider(self.rect.x + 40, self.rect.y + 150, self.width - 80, value=self.game.sfx_volume)
        self.close_btn = Button(self.rect.centerx - 60, self.rect.y + self.height - 56, 120, 40, "Close", LIGHT_BLUE, BLUE, self.close, 20)

    def draw(self, screen):
        # overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)
        screen.blit(overlay, (0,0))
        # dialog box
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=10)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 3, border_radius=10)
        # title
        title = self.title_font.render("Settings", True, BLACK)
        screen.blit(title, title.get_rect(midtop=(self.rect.centerx, self.rect.y + 12)))
        # BG label + slider
        bg_label = self.label_font.render(f"Background Volume: {int(self.bg_slider.value * 100)}%", True, BLACK)
        screen.blit(bg_label, (self.rect.x + 40, self.rect.y + 48))
        self.bg_slider.draw(screen)
        # SFX
        sfx_label = self.label_font.render(f"SFX Volume: {int(self.sfx_slider.value * 100)}%", True, BLACK)
        screen.blit(sfx_label, (self.rect.x + 40, self.rect.y + 118))
        self.sfx_slider.draw(screen)
        # close
        self.close_btn.draw(screen)

    def handle_event(self, event):
        changed = False
        if self.bg_slider.handle_event(event):
            changed = True
        if self.sfx_slider.handle_event(event):
            changed = True
        self.close_btn.check_hover(pygame.mouse.get_pos())
        if self.close_btn.handle_event(event):
            return True
        if changed:
            # apply live
            self.game.bg_volume = round(self.bg_slider.value, 2)
            self.game.sfx_volume = round(self.sfx_slider.value, 2)
            # apply volumes to sound channels
            if music_available:
                try:
                    pygame.mixer.music.set_volume(self.game.bg_volume)
                except:
                    pass
            for s in (self.game.sound_click, self.game.sound_success, self.game.sound_error, self.game.sound_win):
                if s:
                    s.set_volume(self.game.sfx_volume)
            # update persisted settings immediately
            save_settings({"bg_volume": self.game.bg_volume, "sfx_volume": self.game.sfx_volume})
        return False

    def close(self):
        # ensure persisted settings saved
        save_settings({"bg_volume": self.game.bg_volume, "sfx_volume": self.game.sfx_volume})
        self.game.current_dialog = None
        # restore previous state (if present), default to GAME
        prev = getattr(self.game, "dialog_parent_state", "GAME")
        self.game.game_state = prev
        # remove stored parent state
        if hasattr(self.game, "dialog_parent_state"):
            delattr(self.game, "dialog_parent_state")
        return True


# Particle and main game class (keeps most of original features)
class Particle:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.vx = random.uniform(-2,2); self.vy = random.uniform(-5,-1)
        self.size = random.randint(5,15)
        self.color = random.choice([RED,GREEN,BLUE,YELLOW,PURPLE])
        self.life = random.uniform(30,60)
    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += 0.1; self.life -= 1
    def draw(self, screen):
        alpha = min(255, max(0, int(self.life * 4)))
        if alpha > 0:
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color[:3], alpha), (self.size//2, self.size//2), self.size//2)
            screen.blit(surf, (int(self.x), int(self.y)))

class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sudoku Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 28)
        self.title_font = pygame.font.SysFont("Arial", 60)
        self.cell_font = pygame.font.SysFont("Arial", 40)

        # game/puzzle state
        self.puzzle = None; self.original_puzzle = None; self.solution = None; self.file_path = None
        self.selected_cell = None; self.history = []
        self.message = ""; self.message_time = 0; self.message_color = BLACK
        self.game_state = "MAIN_MENU"
        self.current_puzzle_name = None

        # alerts
        self.alert_message = ""; self.alert_color = RED; self.alert_time = 0

        # timer
        self.start_time = None; self.timer_paused = False; self.paused_time = 0

        # dialog
        self.current_dialog = None

        # difficulty and hints
        self.current_difficulty = "normal"; self.hints_remaining = 0

        # sounds & volumes
        self.sound_click = sound_click; self.sound_success = sound_success
        self.sound_error = sound_error; self.sound_win = sound_win
        self.sound_background_path = background_music_path if music_available else None
        # load persisted volumes into game
        self.bg_volume = persisted_settings["bg_volume"]
        self.sfx_volume = persisted_settings["sfx_volume"]

        # apply volumes
        if music_available:
            try:
                pygame.mixer.music.set_volume(self.bg_volume)
            except:
                pass
        for s in (self.sound_click, self.sound_success, self.sound_error, self.sound_win):
            if s:
                s.set_volume(self.sfx_volume)

        # celebration / check mode
        self.solution_check_mode = False
        self.cell_colors = {}
        self.puzzle_completed = False
        self.particles = []; self.celebration_active = False; self.celebration_start_time = 0
        self.editable_cells = set()
        self.instructions = "Click on a cell to select it, then press a number key to fill it"

        # load resources and UI
        initialize_puzzle_files()
        self.load_settings_icon()
        self.setup_ui()

        if not any((self.sound_click, self.sound_success, self.sound_error, self.sound_win, music_available)):
            self.show_alert("[WARNING] Sound files missing - game will run without sound", YELLOW)

    def load_settings_icon(self):
        self.settings_icon = None
        if os.path.exists(SETTINGS_ICON_PATH):
            try:
                img = pygame.image.load(SETTINGS_ICON_PATH).convert_alpha()
                self.settings_icon = img
            except Exception as e:
                print("Failed to load settings icon:", e)
                self.settings_icon = None

    def setup_ui(self):
        # main menu buttons 2x3
        button_grid_width = 2 * BUTTON_WIDTH + BUTTON_MARGIN
        button_grid_height = 3 * BUTTON_HEIGHT + 2 * BUTTON_MARGIN
        start_x = (SCREEN_WIDTH - button_grid_width) // 2
        start_y = (SCREEN_HEIGHT - button_grid_height) // 2 - 30
        self.menu_buttons = [
            Button(start_x, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Puzzle 1", LIGHT_BLUE, BLUE, lambda: self.select_difficulty("puzzle1")),
            Button(start_x, start_y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Puzzle 3", LIGHT_BLUE, BLUE, lambda: self.select_difficulty("puzzle3")),
            Button(start_x, start_y + 2*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "Puzzle 5", LIGHT_BLUE, BLUE, lambda: self.select_difficulty("puzzle5")),
            Button(start_x + BUTTON_WIDTH + BUTTON_MARGIN, start_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Puzzle 2", LIGHT_BLUE, BLUE, lambda: self.select_difficulty("puzzle2")),
            Button(start_x + BUTTON_WIDTH + BUTTON_MARGIN, start_y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Puzzle 4", LIGHT_BLUE, BLUE, lambda: self.select_difficulty("puzzle4")),
            Button(start_x + BUTTON_WIDTH + BUTTON_MARGIN, start_y + 2*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "Puzzle 6", LIGHT_BLUE, BLUE, lambda: self.select_difficulty("puzzle6")),
        ]
        exit_button_y = start_y + button_grid_height + 20
        self.menu_buttons.append(Button(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, exit_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Exit", (255,150,150), RED, self.exit_game))

        # difficulty buttons
        difficulty_button_y = (SCREEN_HEIGHT - 3 * (BUTTON_HEIGHT + BUTTON_MARGIN) + BUTTON_MARGIN) // 2
        self.difficulty_buttons = [
            Button(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, difficulty_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Beginner", (200,255,200), GREEN, lambda: self.load_puzzle_with_difficulty("beginner")),
            Button(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, difficulty_button_y + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Normal", YELLOW, (255,200,0), lambda: self.load_puzzle_with_difficulty("normal")),
            Button(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, difficulty_button_y + 2*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "Advanced", (255,150,150), RED, lambda: self.load_puzzle_with_difficulty("advanced")),
            Button(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, difficulty_button_y + 3*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "Back", LIGHT_GRAY, GRAY, self.show_main_menu),
        ]

        # game buttons
        first_row_y = SCREEN_HEIGHT - 2*(BUTTON_HEIGHT + BUTTON_ROW_MARGIN)
        second_row_y = SCREEN_HEIGHT - BUTTON_HEIGHT - 10
        total_button_width = 3 * BUTTON_WIDTH + 2 * BUTTON_MARGIN
        button_start_x = (SCREEN_WIDTH - total_button_width) // 2
        self.game_buttons = [
            Button(button_start_x, first_row_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Main Menu", LIGHT_BLUE, BLUE, self.show_main_menu),
            Button(button_start_x + BUTTON_WIDTH + BUTTON_MARGIN, first_row_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Check Solution", YELLOW, (255,200,0), self.check_solution_button),
            Button(button_start_x + 2*(BUTTON_WIDTH + BUTTON_MARGIN), first_row_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Reset Puzzle", (255,150,150), RED, self.show_reset_confirmation),
        ]
        self.hint_button = Button(button_start_x, second_row_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Hint (0)", (200,255,150), GREEN, self.provide_hint)
        self.undo_button = Button(button_start_x + BUTTON_WIDTH + BUTTON_MARGIN, second_row_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Undo", (200,150,255), PURPLE, self.undo_move)
        self.new_game_button = Button(button_start_x + 2*(BUTTON_WIDTH + BUTTON_MARGIN), second_row_y, BUTTON_WIDTH, BUTTON_HEIGHT, "New Game", LIGHT_BLUE, BLUE, self.show_main_menu)
        self.game_buttons.extend([self.hint_button, self.undo_button, self.new_game_button])

        # unified settings button top-left under timer (both MAIN_MENU and GAME)
        settings_x = 20
        settings_y = 60  # under timer area
        if self.settings_icon:
            # animated image button when icon exists
            self.settings_button = ImageButton(settings_x, settings_y, self.settings_icon, action=self.open_settings, size=44, animated=True)
        else:
            # fallback text button with animation enabled
            self.settings_button = Button(settings_x, settings_y, 120, 36, "Settings", LIGHT_GRAY, GRAY, self.open_settings, font_size=20, animated=True)

    # helper: update hint button text
    def update_hint_button_text(self):
        self.hint_button.text = f"Hint ({self.hints_remaining})"
        self.hint_button.enabled = self.hints_remaining > 0

    # flow control
    def select_difficulty(self, puzzle_name):
        self.current_puzzle_name = puzzle_name
        self.game_state = "DIFFICULTY_SELECT"
        return True

    def load_puzzle_with_difficulty(self, difficulty):
        self.current_difficulty = difficulty
        self.hints_remaining = HINT_LIMITS.get(difficulty, 5)
        return self.load_puzzle_action(self.current_puzzle_name)

    def load_puzzle_action(self, puzzle_name):
        try:
            solution_path = os.path.join(PUZZLE_DIR, puzzle_name + "S.txt")
            if not os.path.exists(solution_path):
                self.show_alert("[ERROR] No solution file found", RED)
                if self.sound_error:
                    self.sound_error.play()
                return True
            with open(solution_path, 'r') as f:
                self.solution = [list(line.strip()) for line in f.readlines()]
            self.puzzle = randomize_puzzle(self.solution, self.current_difficulty)
            self.original_puzzle = [row[:] for row in self.puzzle]
            self.file_path = os.path.join(PUZZLE_DIR, puzzle_name + ".txt")
            self.selected_cell = None; self.history = []; self.solution_check_mode = False
            self.cell_colors = {}; self.puzzle_completed = False; self.celebration_active = False
            self.editable_cells = set(); self.instructions = "Click on a cell to select it, then press a number key to fill it"
            for b in self.game_buttons:
                b.enabled = True
            self.update_hint_button_text()
            self.show_alert(f"[SUCCESS] Loaded {puzzle_name} ({self.current_difficulty}) successfully!", GREEN)
            if self.sound_success:
                self.sound_success.play()
            self.game_state = "GAME"
            self.start_time = time.time()
        except Exception as e:
            print("Error loading puzzle:", e)
            self.show_alert("[ERROR] Failed to load puzzle", RED)
            if self.sound_error:
                self.sound_error.play()
        return True

    def show_main_menu(self):
        self.game_state = "MAIN_MENU"
        return True

    def exit_game(self):
        # ensure settings saved before exit
        save_settings({"bg_volume": self.bg_volume, "sfx_volume": self.sfx_volume})
        pygame.quit()
        sys.exit()

    def show_reset_confirmation(self):
        self.current_dialog = Dialog("Reset Puzzle", "Are you sure you want to reset the puzzle?", self.reset_puzzle, self.cancel_dialog)
        # record parent state for correct background when dialog opens
        self.dialog_parent_state = self.game_state
        self.game_state = "DIALOG"
        return True

    def check_solution_button(self):
        # ensure puzzle complete
        has_empty = any(self.puzzle[r][c] == '.' for r in range(9) for c in range(9))
        if has_empty:
            self.show_alert("[ERROR] Please complete the puzzle before checking", RED)
            if self.sound_error: self.sound_error.play()
        else:
            self.check_solution()
        return True

    def cancel_dialog(self):
        self.current_dialog = None
        # restore parent state if present
        prev = getattr(self, "dialog_parent_state", "GAME")
        self.game_state = prev
        if hasattr(self, "dialog_parent_state"):
            delattr(self, "dialog_parent_state")
        return True

    def reset_puzzle(self):
        if not self.solution:
            self.show_alert("[ERROR] No solution available", RED)
            if self.sound_error: self.sound_error.play()
            return False
        try:
            self.puzzle = randomize_puzzle(self.solution, self.current_difficulty)
            self.original_puzzle = [row[:] for row in self.puzzle]
            self.hints_remaining = HINT_LIMITS.get(self.current_difficulty, 5)
            self.history = []; self.selected_cell = None; self.solution_check_mode = False
            self.cell_colors = {}; self.puzzle_completed = False; self.celebration_active = False; self.editable_cells = set()
            self.instructions = "Click on a cell to select it, then press a number key to fill it"
            for b in self.game_buttons: b.enabled = True
            self.update_hint_button_text()
            self.show_alert(f"[SUCCESS] Puzzle reset ({self.current_difficulty} mode)", GREEN)
            if self.sound_success: self.sound_success.play()
            self.current_dialog = None
            prev = getattr(self, "dialog_parent_state", "GAME")
            self.game_state = prev
            if hasattr(self, "dialog_parent_state"):
                delattr(self, "dialog_parent_state")
            return True
        except Exception as e:
            self.show_alert(f"[ERROR] Error resetting: {e}", RED)
            if self.sound_error: self.sound_error.play()
            self.current_dialog = None
            self.game_state = "GAME"
            return False

    def provide_hint(self):
        if not self.puzzle or not self.solution:
            self.show_alert("[ERROR] No puzzle or solution loaded", RED)
            if self.sound_error: self.sound_error.play()
            return False
        if self.hints_remaining <= 0:
            self.show_alert("[ERROR] No hints remaining!", RED)
            if self.sound_error: self.sound_error.play()
            return False
        empty_cells = [(r,c) for r in range(9) for c in range(9) if self.puzzle[r][c] == '.']
        if not empty_cells:
            self.show_alert("[SUCCESS] Puzzle is already complete!", GREEN)
            if self.sound_success: self.sound_success.play()
            return False
        r,c = random.choice(empty_cells)
        self.history.append((r,c,self.puzzle[r][c]))
        self.puzzle[r][c] = self.solution[r][c]
        self.selected_cell = (r,c)
        self.hints_remaining -= 1
        self.update_hint_button_text()
        if self.solution_check_mode:
            self.cell_colors[(r,c)] = GREEN
        if self.file_path:
            try:
                with open(self.file_path, 'w') as f:
                    for row in self.puzzle: f.write("".join(row) + "\n")
            except: pass
        self.show_alert(f"[WARNING] Hint: Row {r+1}, Column {c+1} is {self.solution[r][c]}", BLUE)
        return True

    def undo_move(self):
        if not self.history:
            self.show_alert("[ERROR] Unable to undo - no moves to undo", RED)
            if self.sound_error: self.sound_error.play()
            return False
        r,c,val = self.history.pop()
        self.puzzle[r][c] = val
        self.selected_cell = (r,c)
        if self.solution_check_mode:
            if val == '.': self.cell_colors[(r,c)] = None
            elif val == self.solution[r][c]: self.cell_colors[(r,c)] = GREEN
            else:
                self.cell_colors[(r,c)] = RED
                self.editable_cells.add((r,c))
        if self.file_path:
            try:
                with open(self.file_path, 'w') as f:
                    for row in self.puzzle: f.write("".join(row) + "\n")
            except: pass
        self.show_alert("[SUCCESS] Undo successful", GREEN)
        if self.sound_success: self.sound_success.play()
        return True

    def update_celebration(self):
        if not self.celebration_active: return
        if random.random() < 0.1:
            for _ in range(5):
                self.particles.append(Particle(random.randint(0, SCREEN_WIDTH), random.randint(SCREEN_HEIGHT-50, SCREEN_HEIGHT)))
        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)
        if time.time() - self.celebration_start_time > 10:
            self.celebration_active = False

    def show_alert(self, message, color=RED):
        self.alert_message = message; self.alert_color = color; self.alert_time = time.time()

    def draw_alert(self):
        if self.alert_message and time.time() - self.alert_time < 3:
            t = self.small_font.render(self.alert_message, True, self.alert_color)
            rect = t.get_rect(topright=(SCREEN_WIDTH-20, 20))
            bg = pygame.Rect(rect.left - 15, rect.top - 10, rect.width + 30, rect.height + 20)
            surf = pygame.Surface((bg.width, bg.height), pygame.SRCALPHA)
            surf.fill(ALERT_BG); self.screen.blit(surf, bg)
            pygame.draw.rect(self.screen, BLACK, bg, 2, border_radius=5)
            self.screen.blit(t, rect)

    def draw_timer(self):
        if self.start_time and not self.timer_paused:
            elapsed = int(time.time() - self.start_time - self.paused_time)
            timer_text = self.small_font.render(f"Time: {elapsed//60}:{elapsed%60:02}", True, BLACK)
            timer_rect = timer_text.get_rect(topleft=(20,20))
            bg = pygame.Rect(timer_rect.left - 10, timer_rect.top - 5, timer_rect.width + 20, timer_rect.height + 10)
            pygame.draw.rect(self.screen, WHITE, bg, border_radius=5)
            pygame.draw.rect(self.screen, GRAY, bg, 2, border_radius=5)
            self.screen.blit(timer_text, timer_rect)

    def draw_difficulty_indicator(self):
        if self.game_state == "GAME":
            txt = self.small_font.render(f"Difficulty: {self.current_difficulty.title()}", True, BLACK)
            rect = txt.get_rect(topright=(SCREEN_WIDTH-20,60))
            bg = pygame.Rect(rect.left - 10, rect.top - 5, rect.width + 20, rect.height + 10)
            pygame.draw.rect(self.screen, WHITE, bg, border_radius=5)
            pygame.draw.rect(self.screen, GRAY, bg, 2, border_radius=5)
            self.screen.blit(txt, rect)

    def draw_grid(self):
        pygame.draw.rect(self.screen, WHITE, (GRID_OFFSET_X, GRID_OFFSET_Y, GRID_SIZE, GRID_SIZE))
        for i in range(10):
            lw = 3 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (GRID_OFFSET_X + i*CELL_SIZE, GRID_OFFSET_Y), (GRID_OFFSET_X + i*CELL_SIZE, GRID_OFFSET_Y + GRID_SIZE), lw)
            pygame.draw.line(self.screen, BLACK, (GRID_OFFSET_X, GRID_OFFSET_Y + i*CELL_SIZE), (GRID_OFFSET_X + GRID_SIZE, GRID_OFFSET_Y + i*CELL_SIZE), lw)
        if self.selected_cell:
            r,c = self.selected_cell
            pygame.draw.rect(self.screen, LIGHT_BLUE, (GRID_OFFSET_X + c*CELL_SIZE, GRID_OFFSET_Y + r*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        # numbers
        if self.puzzle:
            for r in range(9):
                for c in range(9):
                    if self.puzzle[r][c] == '.': continue
                    if self.solution_check_mode and (r,c) in self.cell_colors:
                        color = self.cell_colors.get((r,c), BLACK)
                    else:
                        color = BLUE if (self.original_puzzle and self.original_puzzle[r][c] == '.') else BLACK
                    txt = self.cell_font.render(self.puzzle[r][c], True, color)
                    rect = txt.get_rect(center=(GRID_OFFSET_X + c*CELL_SIZE + CELL_SIZE//2, GRID_OFFSET_Y + r*CELL_SIZE + CELL_SIZE//2))
                    self.screen.blit(txt, rect)

    def draw_main_menu(self):
        title = self.title_font.render("Sudoku Game", True, PURPLE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2,100)))
        subtitle = self.font.render("Select a puzzle to begin", True, DARK_GRAY)
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH//2,170)))
        for b in self.menu_buttons: b.draw(self.screen)
        # settings on main menu (top-left)
        self.settings_button.draw(self.screen)

    def draw_difficulty_select(self):
        title = self.title_font.render("Select Difficulty", True, PURPLE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2,100)))
        subtitle = self.font.render(f"For Puzzle {self.current_puzzle_name[-1]}" if self.current_puzzle_name else "Select Difficulty", True, DARK_GRAY)
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH//2,170)))
        for b in self.difficulty_buttons: b.draw(self.screen)
        beginner = self.small_font.render("Easiest version", True, DARK_GRAY)
        normal = self.small_font.render("Common version", True, DARK_GRAY)
        advanced = self.small_font.render("Hardest version", True, DARK_GRAY)
        self.screen.blit(beginner, beginner.get_rect(left=SCREEN_WIDTH//2 + BUTTON_WIDTH//2 + 20, centery=self.difficulty_buttons[0].rect.centery))
        self.screen.blit(normal, normal.get_rect(left=SCREEN_WIDTH//2 + BUTTON_WIDTH//2 + 20, centery=self.difficulty_buttons[1].rect.centery))
        self.screen.blit(advanced, advanced.get_rect(left=SCREEN_WIDTH//2 + BUTTON_WIDTH//2 + 20, centery=self.difficulty_buttons[2].rect.centery))

    def draw_celebration(self):
        if not self.celebration_active: return
        for p in self.particles: p.draw(self.screen)

    def draw_game(self):
        title = self.title_font.render("Sudoku", True, PURPLE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2,80)))
        self.draw_grid()
        for b in self.game_buttons: b.draw(self.screen)
        if self.message and time.time() - self.message_time < 3:
            t = self.small_font.render(self.message, True, self.message_color)
            self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 2*(BUTTON_HEIGHT + BUTTON_ROW_MARGIN) - 25)))
        instr = self.small_font.render(self.instructions, True, DARK_GRAY)
        self.screen.blit(instr, instr.get_rect(center=(SCREEN_WIDTH//2, GRID_OFFSET_Y + GRID_SIZE + 40)))
        # unified settings button
        self.settings_button.draw(self.screen)
        self.draw_celebration()

    def draw_dialog(self):
        # Draw underlying screen according to the state that opened the dialog
        parent = getattr(self, "dialog_parent_state", None)
        if parent == "MAIN_MENU":
            self.draw_main_menu()
        elif parent == "DIFFICULTY_SELECT":
            self.draw_difficulty_select()
        else:
            # default to game screen if unknown
            self.draw_game()

        # Then draw the dialog on top
        if self.current_dialog:
            self.current_dialog.draw(self.screen)


    def draw(self):
        self.screen.fill(BACKGROUND)
        if self.game_state == "MAIN_MENU":
            self.draw_main_menu()
        elif self.game_state == "DIFFICULTY_SELECT":
            self.draw_difficulty_select()
        elif self.game_state == "GAME":
            self.draw_game(); self.draw_timer(); self.draw_difficulty_indicator()
        elif self.game_state == "DIALOG":
            self.draw_dialog()
        self.draw_alert()
        pygame.display.flip()

    def open_settings(self):
        # record which state opened the dialog so we draw correct background
        self.dialog_parent_state = self.game_state
        self.current_dialog = SettingsDialog(self)
        self.game_state = "DIALOG"
        return True


    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False

            if self.game_state == "MAIN_MENU":
                for b in self.menu_buttons:
                    b.check_hover(mouse_pos)
                    if b.handle_event(event): break
                # settings button
                self.settings_button.check_hover(mouse_pos)
                # for animated settings_button the handle_event uses press semantics
                if self.settings_button.handle_event(event): pass

            elif self.game_state == "DIFFICULTY_SELECT":
                for b in self.difficulty_buttons:
                    b.check_hover(mouse_pos)
                    if b.handle_event(event): break
            elif self.game_state == "GAME":
                for b in self.game_buttons:
                    b.check_hover(mouse_pos)
                    if b.enabled and b.handle_event(event): break
                # settings
                self.settings_button.check_hover(mouse_pos)
                if self.settings_button.handle_event(event): pass
                # grid clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if (GRID_OFFSET_X <= mouse_pos[0] <= GRID_OFFSET_X + GRID_SIZE and
                        GRID_OFFSET_Y <= mouse_pos[1] <= GRID_OFFSET_Y + GRID_SIZE and self.puzzle):
                        col = (mouse_pos[0] - GRID_OFFSET_X) // CELL_SIZE
                        row = (mouse_pos[1] - GRID_OFFSET_Y) // CELL_SIZE
                        if self.solution_check_mode:
                            if (row,col) in self.editable_cells: self.selected_cell = (row,col)
                            else:
                                if self.sound_error: self.sound_error.play()
                                self.show_alert("[WARNING] Only incorrect cells can be modified", YELLOW)
                        else:
                            if self.puzzle[row][col] == '.': self.selected_cell = (row,col)
                            else:
                                if self.original_puzzle[row][col] != '.':
                                    if self.sound_error: self.sound_error.play()
                                    self.show_alert("[WARNING] Original cells cannot be modified", YELLOW)
                                else:
                                    self.selected_cell = (row,col)
                # key input
                if event.type == pygame.KEYDOWN and self.selected_cell and self.puzzle:
                    r,c = self.selected_cell
                    can_edit = (r,c) in self.editable_cells if self.solution_check_mode else (self.original_puzzle[r][c] == '.')
                    if can_edit:
                        if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE) or event.key == pygame.K_0:
                            self.history.append((r,c,self.puzzle[r][c])); self.puzzle[r][c] = '.'
                            if self.solution_check_mode: self.cell_colors[(r,c)] = None
                        elif event.unicode.isdigit() and event.unicode != '0':
                            self.history.append((r,c,self.puzzle[r][c])); self.puzzle[r][c] = event.unicode
                            if self.solution_check_mode:
                                if event.unicode == self.solution[r][c]:
                                    self.cell_colors[(r,c)] = GREEN
                                    if (r,c) in self.editable_cells: self.editable_cells.remove((r,c))
                                else:
                                    self.cell_colors[(r,c)] = RED
                        if self.file_path:
                            try:
                                with open(self.file_path, 'w') as f:
                                    for row in self.puzzle: f.write("".join(row) + "\n")
                            except: pass
                        # check completion in solution_check_mode
                        if self.solution_check_mode:
                            all_filled = all(self.puzzle[r][c] != '.' for r in range(9) for c in range(9))
                            all_correct = all(self.puzzle[r][c] == self.solution[r][c] for r in range(9) for c in range(9))
                            if all_filled and all_correct and not self.puzzle_completed:
                                self.puzzle_completed = True; self.celebration_active = True; self.celebration_start_time = time.time()
                                self.particles = [Particle(random.randint(0,SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT//2)) for _ in range(100)]
                                if self.sound_win: self.sound_win.play()
                                self.show_alert("[SUCCESS] Congratulations! Puzzle solved correctly!", GREEN)
                                for b in self.game_buttons:
                                    if b.text not in ["Main Menu", "New Game"]:
                                        b.enabled = False

            elif self.game_state == "DIALOG":
                if self.current_dialog:
                    # if settings dialog
                    if isinstance(self.current_dialog, SettingsDialog):
                        self.current_dialog.handle_event(event)
                    else:
                        self.current_dialog.handle_events(event, mouse_pos)

        return True

    def check_solution(self):
        if not self.solution:
            self.show_alert("[ERROR] No solution available", RED)
            if self.sound_error: self.sound_error.play()
            return False
        try:
            self.solution_check_mode = True
            self.editable_cells.clear()
            # remove colors for empty cells
            keys_to_remove = [k for k in list(self.cell_colors.keys()) if self.puzzle[k[0]][k[1]] == '.']
            for k in keys_to_remove: self.cell_colors.pop(k, None)
            checked = {}
            all_correct = True
            for r in range(9):
                for c in range(9):
                    if self.original_puzzle[r][c] == '.' and self.puzzle[r][c] != '.':
                        if self.puzzle[r][c] == self.solution[r][c]:
                            checked[(r,c)] = GREEN
                        else:
                            checked[(r,c)] = RED
                            self.editable_cells.add((r,c))
                            all_correct = False
            self.cell_colors.update(checked)
            if all_correct:
                self.puzzle_completed = True; self.celebration_active = True; self.celebration_start_time = time.time()
                self.particles = [Particle(random.randint(0,SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT//2)) for _ in range(100)]
                if self.sound_win: self.sound_win.play()
                self.show_alert("[SUCCESS] Congratulations! All answers are correct!", GREEN)
                for b in self.game_buttons:
                    if b.text not in ["Main Menu", "New Game"]:
                        b.enabled = False
            else:
                self.show_alert("[WARNING] Some cells are incorrect - only incorrect cells can be modified", YELLOW)
                if self.sound_error: self.sound_error.play()
                self.instructions = "Only incorrect (red) cells can be modified"
            self.current_dialog = None; self.game_state = "GAME"
            return True
        except Exception as e:
            self.show_alert(f"[ERROR] Error checking solution: {e}", RED)
            if self.sound_error: self.sound_error.play()
            self.current_dialog = None; self.game_state = "GAME"
            return False

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if self.celebration_active: self.update_celebration()

            # update hover states
            pos = pygame.mouse.get_pos()
            if self.game_state == "MAIN_MENU":
                for b in self.menu_buttons: b.check_hover(pos)
            elif self.game_state == "DIFFICULTY_SELECT":
                for b in self.difficulty_buttons: b.check_hover(pos)
            elif self.game_state == "GAME":
                for b in self.game_buttons: b.check_hover(pos)
                self.settings_button.check_hover(pos)
            elif self.game_state == "DIALOG" and self.current_dialog:
                if isinstance(self.current_dialog, SettingsDialog):
                    self.current_dialog.close_btn.check_hover(pos)
                else:
                    self.current_dialog.yes_button.check_hover(pos)
                    self.current_dialog.no_button.check_hover(pos)

            self.draw()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()

# Simple confirmation dialog reused
class Dialog:
    def __init__(self, title, message, yes_action, no_action, width=400, height=200):
        self.title = title; self.message = message; self.yes_action = yes_action; self.no_action = no_action
        self.width = width; self.height = height
        self.rect = pygame.Rect((SCREEN_WIDTH-width)//2, (SCREEN_HEIGHT-height)//2, width, height)
        btn_w = 120; btn_h = 40; btn_margin = 20
        button_y = self.rect.y + self.height - btn_h - 20
        self.yes_button = Button(self.rect.x + (self.width//2) - btn_w - btn_margin//2, button_y, btn_w, btn_h, "Yes", GREEN, (100,255,100), self.yes_action, 22)
        self.no_button = Button(self.rect.x + (self.width//2) + btn_margin//2, button_y, btn_w, btn_h, "No", RED, (255,100,100), self.no_action, 22)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.message_font = pygame.font.SysFont("Arial", 20)

    def draw(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG); screen.blit(overlay, (0,0))
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=10)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 3, border_radius=10)
        title = self.title_font.render(self.title, True, BLACK)
        screen.blit(title, title.get_rect(midtop=(self.rect.centerx, self.rect.y+12)))
        msg = self.message_font.render(self.message, True, DARK_GRAY)
        screen.blit(msg, msg.get_rect(center=(self.rect.centerx, self.rect.centery-20)))
        self.yes_button.draw(screen); self.no_button.draw(screen)

    def handle_events(self, event, mouse_pos):
        self.yes_button.check_hover(mouse_pos); self.no_button.check_hover(mouse_pos)
        if self.yes_button.handle_event(event): return True
        if self.no_button.handle_event(event): return True
        return False

# Start the game
if __name__ == "__main__":
    game = SudokuGame()
    game.run()
