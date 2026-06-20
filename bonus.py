import pygame
from pygame.sprite import Sprite
import random


class Bonus(Sprite):
    LIFE = 'life'
    SHIELD = 'shield'
    POWER = 'power'
    
    def __init__(self, ai_game, x, y, bonus_type=None):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        
        if bonus_type is None:
            self.bonus_type = random.choice([self.LIFE, self.SHIELD, self.POWER])
        else:
            self.bonus_type = bonus_type
        
        self.size = 24
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.centerx = x
        self.rect.centery = y
        
        self.y = float(self.rect.y)
        
        self.colors = {
            self.LIFE: (255, 80, 80),
            self.SHIELD: (80, 180, 255),
            self.POWER: (255, 220, 80),
        }
        self.color = self.colors[self.bonus_type]
    
    def update(self):
        self.y += self.settings.bonus_speed
        self.rect.y = self.y
    
    def draw_bonus(self):
        pygame.draw.rect(self.screen, self.color, self.rect, border_radius=6)
        font = pygame.font.Font(None, 22)
        symbols = {self.LIFE: '+', self.SHIELD: 'S', self.POWER: 'P'}
        text = font.render(symbols[self.bonus_type], True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        self.screen.blit(text, text_rect)