import pygame
from constants import *
import time
from sounds import sound_click

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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
                self.is_pressed = True
                # Play click sound on mouse down for animated buttons
                if hasattr(self, "sound_click") and self.sound_click:
                    self.sound_click.play()
                elif "sound_click" in globals() and sound_click:
                    sound_click.play()
                return False
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_pressed:
                    self.is_pressed = False
                    if self.is_hovered:
                        if hasattr(self, "sound_click") and self.sound_click:
                            self.sound_click.play()
                        elif "sound_click" in globals() and sound_click:
                            sound_click.play()
                        if self.action:
                            return self.action()
                return False
            return False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
                # Always play click sound on button down
                if hasattr(self, "sound_click") and self.sound_click:
                    self.sound_click.play()
                elif "sound_click" in globals() and sound_click:
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
        self.value = value  # Ensure value is always set
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
