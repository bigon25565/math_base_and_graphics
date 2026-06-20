import pygame
from utils import resource_path

class Ship:
    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()
        
        self.image = pygame.image.load(resource_path('images/ship.bmp'))
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom
        
        self.x = float(self.rect.x)
        
        self.moving_right = False
        self.moving_left = False
        
        self.shield_active = False
        self.shield_end_time = 0
    
    def activate_shield(self, current_time):
        self.shield_active = True
        self.shield_end_time = current_time + self.settings.shield_duration
    
    def update_shield(self, current_time):
        if self.shield_active and current_time >= self.shield_end_time:
            self.shield_active = False
    
    def center_ship(self):
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
    
    def update(self):
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        self.rect.x = self.x
    
    def bltime(self):
        self.screen.blit(self.image, self.rect)
        if self.shield_active:
            shield_rect = self.rect.inflate(20, 20)
            pygame.draw.ellipse(self.screen, (80, 180, 255), shield_rect, 2)