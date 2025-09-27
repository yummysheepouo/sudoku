import pygame
import random
from constants import *

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

    def __init__(self, x, y):
        ...

    def update(self):
        ...

    def draw(self, screen):
        ...