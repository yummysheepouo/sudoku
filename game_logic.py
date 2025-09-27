import pygame
import random
from puzzles import randomize_puzzle
from dialogs import SettingsDialog, SaveLoadDialog, Dialog
from particles import Particle
from sounds import load_sound, initialize_background_music
from constants import *
from ui_components import Button, ImageButton, sound_click
from settings import *
from sounds import sound_click, sound_success, sound_error, sound_win, background_music_path, music_available
from puzzles import initialize_puzzle_files
import os
import sys
import time
import json


class SudokuGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Ensure the mixer is initialized
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sudoku Game")
        self.clock = pygame.time.Clock()
        self.progress_dir = os.path.join(BASE_DIR, "progress")
        if not os.path.exists(self.progress_dir):
            os.makedirs(self.progress_dir)
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
        settings = load_settings()
        self.bg_volume = settings.get("bg_volume", 1.0)
        self.sfx_volume = settings.get("sfx_volume", 1.0)

        # apply volumes
        if music_available:
            try:
                pygame.mixer.music.set_volume(self.bg_volume)
            except:
                pass
        for s in (self.sound_click, self.sound_success, self.sound_error, self.sound_win):
            if s:
                s.set_volume(self.sfx_volume)

        # Start background music if available and not already playing
        if music_available:
            try:
                pygame.mixer.music.load(background_music_path)
                pygame.mixer.music.set_volume(self.bg_volume)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print("Failed to start background music:", e)

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
        load_progress_y = exit_button_y + BUTTON_HEIGHT + 10
        self.load_progress_button = Button(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, load_progress_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Load Progress", LIGHT_BLUE, BLUE, lambda: self.open_save_load_dialog("load"))
        self.menu_buttons.append(self.load_progress_button)

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
        self.new_game_button = Button(button_start_x + 2*(BUTTON_WIDTH + BUTTON_MARGIN), second_row_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Save Progress", LIGHT_BLUE, BLUE, lambda: self.open_save_load_dialog("save"))
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
            self.puzzle = randomize_puzzle(self.solution, self.current_difficulty, DIFFICULTY_LEVELS)
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
            self.puzzle = randomize_puzzle(self.solution, self.current_difficulty, DIFFICULTY_LEVELS)
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
        # File is read-only, no writing
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
        # File is read-only, no writing
        self.show_alert("[SUCCESS] Undo successful", GREEN)
        if self.sound_success: self.sound_success.play()
        return True

    def save_progress(self, slot=None):
        if not self.puzzle or not self.solution:
            self.show_alert("[ERROR] No puzzle to save", RED)
            if self.sound_error: self.sound_error.play()
            return False
        try:
            data = {
                "current_puzzle_name": self.current_puzzle_name,
                "current_difficulty": self.current_difficulty,
                "hints_remaining": self.hints_remaining,
                "puzzle": self.puzzle,
                "solution": self.solution,
                "original_puzzle": self.original_puzzle,
                "start_time": self.start_time,
                "paused_time": self.paused_time,
                "history": [list(h) for h in self.history],
                "selected_cell": self.selected_cell,
                "solution_check_mode": self.solution_check_mode,
                "cell_colors": {str(k): v for k, v in self.cell_colors.items()},
                "editable_cells": list(self.editable_cells),
                "puzzle_completed": self.puzzle_completed,
                "instructions": self.instructions,
                "save_time": time.time()
            }
            progress_file = os.path.join(self.progress_dir, f"slot{slot}.json" if slot else "progress.json")
            with open(progress_file, 'w') as f:
                json.dump(data, f)
            slot_msg = f" to slot {slot}" if slot else ""
            self.show_alert(f"[SUCCESS] Progress saved{slot_msg}!", GREEN)
            if self.sound_success: self.sound_success.play()
            return True
        except Exception as e:
            slot_msg = f" to slot {slot}" if slot else " progress"
            self.show_alert(f"[ERROR] Failed to save{slot_msg}: {e}", RED)
            if self.sound_error: self.sound_error.play()
            return False

    def load_progress(self, slot=None):
        progress_file = os.path.join(self.progress_dir, f"slot{slot}.json" if slot else "progress.json")
        if not os.path.exists(progress_file):
            slot_msg = f" in slot {slot}" if slot else ""
            self.show_alert(f"[ERROR] No saved progress found{slot_msg}", RED)
            if self.sound_error: self.sound_error.play()
            return False
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
            self.current_puzzle_name = data.get("current_puzzle_name")
            self.current_difficulty = data.get("current_difficulty")
            self.hints_remaining = data.get("hints_remaining")
            self.puzzle = data.get("puzzle")
            self.solution = data.get("solution")
            self.original_puzzle = data.get("original_puzzle")
            self.start_time = data.get("start_time")
            self.paused_time = data.get("paused_time", 0)
            self.history = [tuple(h) for h in data.get("history", [])]
            self.selected_cell = data.get("selected_cell")
            self.solution_check_mode = data.get("solution_check_mode", False)
            self.cell_colors = {eval(k): tuple(v) for k, v in data.get("cell_colors", {}).items()}
            self.editable_cells = set(data.get("editable_cells", []))
            self.puzzle_completed = data.get("puzzle_completed", False)
            self.instructions = data.get("instructions", "Click on a cell to select it, then press a number key to fill it")
            self.file_path = os.path.join(PUZZLE_DIR, self.current_puzzle_name + ".txt") if self.current_puzzle_name else None
            self.celebration_active = False
            self.particles = []
            for b in self.game_buttons:
                b.enabled = not self.puzzle_completed or b.text in ["Main Menu", "Save Progress"]
            self.update_hint_button_text()
            slot_msg = f" slot {slot}" if slot else ""
            self.show_alert(f"[SUCCESS] Progress loaded from{slot_msg}!", GREEN)
            if self.sound_success: self.sound_success.play()
            self.game_state = "GAME"
            return True
        except Exception as e:
            slot_msg = f" slot {slot}" if slot else " progress"
            self.show_alert(f"[ERROR] Failed to load{slot_msg}: {e}", RED)
            if self.sound_error: self.sound_error.play()
            return False

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


    def open_save_load_dialog(self, mode):
        self.dialog_parent_state = self.game_state
        self.current_dialog = SaveLoadDialog(self, mode)
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
                if event.type == pygame.KEYDOWN and self.puzzle:
                    if self.selected_cell:
                        r, c = self.selected_cell
                    else:
                        # If no cell selected, default to (0,0)
                        r, c = 0, 0
                        self.selected_cell = (0, 0)

                    # Handle arrow keys for navigation
                    if event.key == pygame.K_UP and r > 0:
                        self.selected_cell = (r - 1, c)
                        if self.sound_click:
                            self.sound_click.play()
                    elif event.key == pygame.K_DOWN and r < 8:
                        self.selected_cell = (r + 1, c)
                        if self.sound_click:
                            self.sound_click.play()
                    elif event.key == pygame.K_LEFT and c > 0:
                        self.selected_cell = (r, c - 1)
                        if self.sound_click:
                            self.sound_click.play()
                    elif event.key == pygame.K_RIGHT and c < 8:
                        self.selected_cell = (r, c + 1)
                        if self.sound_click:
                            self.sound_click.play()
                    # Only handle input if not an arrow key or if we want to allow input after navigation
                    elif self.selected_cell:
                        r, c = self.selected_cell
                        can_edit = (r,c) in self.editable_cells if self.solution_check_mode else (self.original_puzzle[r][c] == '.')
                        if can_edit:
                            if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE) or event.key == pygame.K_0:
                                self.history.append((r,c,self.puzzle[r][c])); self.puzzle[r][c] = '.'
                                if self.solution_check_mode: self.cell_colors[(r,c)] = None
                                if self.sound_click:
                                    self.sound_click.play()
                            elif event.unicode.isdigit() and event.unicode != '0':
                                self.history.append((r,c,self.puzzle[r][c])); self.puzzle[r][c] = event.unicode
                                if self.sound_click:
                                    self.sound_click.play()
                                if self.solution_check_mode:
                                    if event.unicode == self.solution[r][c]:
                                        self.cell_colors[(r,c)] = GREEN
                                        if (r,c) in self.editable_cells: self.editable_cells.remove((r,c))
                                    else:
                                        self.cell_colors[(r,c)] = RED
                        # File is read-only, no writing
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
                                    if b.text not in ["Main Menu", "Save Progress"]:
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
                    if b.text not in ["Main Menu", "Save Progress"]:
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
        print("Game is running...")
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
                elif isinstance(self.current_dialog, SaveLoadDialog):
                    for b in self.current_dialog.slot_buttons: b.check_hover(pos)
                    for b in self.current_dialog.delete_buttons:
                        if b:
                            b.check_hover(pos)
                    self.current_dialog.back_button.check_hover(pos)
                else:
                    self.current_dialog.yes_button.check_hover(pos)
                    self.current_dialog.no_button.check_hover(pos)

            self.draw()
            self.clock.tick(30)
        pygame.quit()
        print("Game has exited.")
        sys.exit()


