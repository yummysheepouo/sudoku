from ui_components import Button, Slider
from constants import *
import pygame
from settings import load_settings, save_settings
import os
import json
import datetime

class SettingsDialog:
    def __init__(self, game, width=480, height=260):
        self.game = game
        self.width = width
        self.height = height
        self.rect = pygame.Rect((SCREEN_WIDTH - width)//2, (SCREEN_HEIGHT - height)//2, width, height)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.label_font = pygame.font.SysFont("Arial", 20)
        # sliders initial from game's persisted volumes
        self.bg_slider = Slider(self.rect.x + 40, self.rect.y + 80, self.width - 80, value=getattr(self.game, "bg_volume", 1.0))
        self.sfx_slider = Slider(self.rect.x + 40, self.rect.y + 150, self.width - 80, value=getattr(self.game, "sfx_volume", 1.0))
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
            for s in (self.game.sound_click, self.game.sound_success, self.game.sound_error, self.game.sound_win):
                if s:
                    s.set_volume(self.game.sfx_volume)
            # apply background music volume
            pygame.mixer.music.set_volume(self.game.bg_volume)
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

class SaveLoadDialog:
    def __init__(self, game, mode, width=600, height=400):
        self.game = game
        self.mode = mode  # "save" or "load"
        self.width = width
        self.height = height
        self.rect = pygame.Rect((SCREEN_WIDTH - width)//2, (SCREEN_HEIGHT - height)//2, width, height)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.label_font = pygame.font.SysFont("Arial", 20)
        self.slots = 5
        self.slot_buttons = []
        self.delete_buttons = []
        start_y = self.rect.y + 60
        slot_btn_width = self.width - 200  # Leave space for delete button
        del_btn_width = 80
        for i in range(1, self.slots + 1):
            info = self.get_slot_info(i)
            text = f"Slot {i}: {info}"
            slot_btn = Button(self.rect.x + 50, start_y + (i-1) * (BUTTON_HEIGHT + 10), slot_btn_width, BUTTON_HEIGHT, text, LIGHT_BLUE, BLUE, lambda i=i: self.select_slot(i), 18)
            self.slot_buttons.append(slot_btn)
            
            if self.mode == "load":
                del_x = self.rect.x + 50 + slot_btn_width + 20
                del_btn = Button(del_x, start_y + (i-1) * (BUTTON_HEIGHT + 10), del_btn_width, BUTTON_HEIGHT, "Delete", RED, (255, 100, 100), lambda i=i: self.delete_slot(i), 18)
                self.delete_buttons.append(del_btn)
            else:
                self.delete_buttons.append(None)
        self.back_button = Button(self.rect.centerx - 60, self.rect.y + self.height - 56, 120, 40, "Back", LIGHT_GRAY, GRAY, self.close, 20)

    def get_slot_info(self, slot):
        path = os.path.join(self.game.progress_dir, f"slot{slot}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                puzzle = data.get("current_puzzle_name", "Unknown")
                diff = data.get("current_difficulty", "Unknown")
                completed = data.get("puzzle_completed", False)
                save_time = data.get("save_time", 0)
                try:
                    if save_time and isinstance(save_time, (int, float)):
                        dt = datetime.datetime.fromtimestamp(float(save_time))
                        date_str = dt.strftime("%m/%d %H:%M")
                    else:
                        date_str = "Unknown"
                except (ValueError, TypeError, OSError):
                    date_str = "Unknown"
                info = f"{puzzle} {diff} {date_str}"
                if completed:
                    info += " (Completed)"
                return info
            except Exception as e:
                print(f"Error loading slot {slot}: {e}")
                return "Corrupted"
        else:
            return "Empty"

    def draw(self, screen):
        # overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_BG)
        screen.blit(overlay, (0,0))
        # dialog box
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=10)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 3, border_radius=10)
        # title
        title_text = "Save Progress" if self.mode == "save" else "Load Progress"
        title = self.title_font.render(title_text, True, BLACK)
        screen.blit(title, title.get_rect(midtop=(self.rect.centerx, self.rect.y + 12)))
        # slots
        for b in self.slot_buttons:
            b.draw(screen)
        # delete buttons if load mode
        for b in self.delete_buttons:
            if b:
                b.draw(screen)
        # back
        self.back_button.draw(screen)

    def handle_events(self, event, mouse_pos):
        for b in self.slot_buttons:
            b.check_hover(mouse_pos)
            if b.handle_event(event):
                return True
        # delete buttons if load mode
        for b in self.delete_buttons:
            if b:
                b.check_hover(mouse_pos)
                if b.handle_event(event):
                    return True
        self.back_button.check_hover(mouse_pos)
        if self.back_button.handle_event(event):
            return True
        return False

    def select_slot(self, slot):
        if self.mode == "save":
            success = self.game.save_progress(slot)
            if success:
                self.game.show_alert(f"[SUCCESS] Progress saved to slot {slot}!", GREEN)
                if self.game.sound_success:
                    self.game.sound_success.play()
                self.close()
            else:
                self.game.show_alert(f"[ERROR] Failed to save to slot {slot}", RED)
                if self.game.sound_error:
                    self.game.sound_error.play()
                return  # stay in dialog
        elif self.mode == "load":
            path = os.path.join(self.game.progress_dir, f"slot{slot}.json")
            if not os.path.exists(path):
                self.game.show_alert(f"[ERROR] No save in slot {slot}", RED)
                if self.game.sound_error:
                    self.game.sound_error.play()
                return
            success = self.game.load_progress(slot)
            if success:
                self.game.dialog_parent_state = "GAME"
                self.close()
            else:
                self.game.show_alert(f"[ERROR] Failed to load slot {slot}", RED)
                if self.game.sound_error:
                    self.game.sound_error.play()
                self.close()

    def delete_slot(self, slot):
        path = os.path.join(self.game.progress_dir, f"slot{slot}.json")
        if os.path.exists(path):
            try:
                os.remove(path)
                self.game.show_alert(f"[SUCCESS] Slot {slot} deleted!", GREEN)
                if self.game.sound_success:
                    self.game.sound_success.play()
                # Refresh the slot button text
                info = self.get_slot_info(slot)
                self.slot_buttons[slot-1].text = f"Slot {slot}: {info}"
            except Exception as e:
                self.game.show_alert(f"[ERROR] Failed to delete slot {slot}: {e}", RED)
                if self.game.sound_error:
                    self.game.sound_error.play()
        else:
            self.game.show_alert(f"[ERROR] No save in slot {slot}", RED)
            if self.game.sound_error:
                self.game.sound_error.play()

    def close(self):
        self.game.current_dialog = None
        self.game.game_state = self.game.dialog_parent_state

# Add this simple Dialog class at the end of the file:
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

    def __init__(self, title, message, yes_action, no_action, width=400, height=200):
        self.title = title
        self.message = message
        self.yes_action = yes_action
        self.no_action = no_action
        self.width = width
        self.height = height
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