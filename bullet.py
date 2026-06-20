import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    def __init__(self, ai_game, powered=False):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.powered = powered
        
        if powered:
            self.color = (255, 220, 80)
            self.width = 6
            self.height = 20
        else:
            self.color = self.settings.bullet_color
            self.width = self.settings.bullet_width
            self.height = self.settings.bullet_height
        
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.midtop = ai_game.ship.rect.midtop
        
        self.y = float(self.rect.y)
    
    def update(self):
        self.y -= self.settings.bullet_speed
        self.rect.y = self.y
    
    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)