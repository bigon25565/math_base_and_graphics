import sys
import pygame
import pickle
import random
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from bonus import Bonus
from utils import resource_path

def save_game(data, filename="savefile.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def load_game(filename="savefile.pkl"):
    with open(filename, "rb") as f:
        return pickle.load(f)


class AlienInvasion:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.settings = Settings()
        
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        
        self.clock = pygame.time.Clock()
        
        self._load_sounds()
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        self.game_active = False
        
        self.power_bullet_active = False
        self.power_bullet_end_time = 0
        
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 74)
        
        self._create_fleet()
    
    def _load_sounds(self):
        try:
            self.laser_sound = pygame.mixer.Sound(resource_path("sounds/laser.wav"))
            self.explosion_sound = pygame.mixer.Sound(resource_path("sounds/explosion.wav"))
            self.ship_hit_sound = pygame.mixer.Sound(resource_path("sounds/ship_hit.wav"))
            self.game_over_sound = pygame.mixer.Sound(resource_path("sounds/game_over.wav"))
            self.bonus_sound = pygame.mixer.Sound(resource_path("sounds/bonus.wav"))
        except pygame.error:
            self.laser_sound = None
            self.explosion_sound = None
            self.ship_hit_sound = None
            self.game_over_sound = None
            self.bonus_sound = None
    
    def _play_sound(self, sound):
        if sound:
            sound.play()
    
    def run_game(self):
        while True:
            self._check_events()
            
            if self.game_active:
                current_time = pygame.time.get_ticks()
                self.ship.update_shield(current_time)
                self._update_power_bullet(current_time)
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_bonuses()
            
            self._update_screen()
            self.clock.tick(100)
    
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
    
    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            if self.game_active:
                self._fire_bullet()
        elif event.key == pygame.K_p:
            if not self.game_active:
                self._start_new_game()
        elif event.key == pygame.K_s:
            self._save_game()
        elif event.key == pygame.K_l:
            self._load_game()
    
    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
    
    def _save_game(self):
        data = {
            "level": self.level,
            "score": self.score,
            "lives": self.ships_left,
        }
        save_game(data)
    
    def _load_game(self):
        try:
            data = load_game()
            self.level = data.get("level", 1)
            self.score = data.get("score", 0)
            self.ships_left = data.get("lives", self.settings.ship_limit)
            
            self.bullets.empty()
            self.aliens.empty()
            self.bonuses.empty()
            
            self.settings.initialize_dynamic_settings()
            for _ in range(self.level - 1):
                self.settings.increase_speed()
            
            self._create_fleet()
            self.ship.center_ship()
            self.game_active = True
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            pass
    
    def _start_new_game(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
        
        self.bullets.empty()
        self.aliens.empty()
        self.bonuses.empty()
        
        self.settings.initialize_dynamic_settings()
        
        self._create_fleet()
        self.ship.center_ship()
        
        self.power_bullet_active = False
        self.game_active = True
    
    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self, powered=self.power_bullet_active)
            self.bullets.add(new_bullet)
            self._play_sound(self.laser_sound)
    
    def _update_power_bullet(self, current_time):
        if self.power_bullet_active and current_time >= self.power_bullet_end_time:
            self.power_bullet_active = False
    
    def _update_bullets(self):
        self.bullets.update()
        
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()
    
    def _check_bullet_alien_collisions(self):
        if self.power_bullet_active:
            collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, False, True)
            for bullet, hit_aliens in collisions.items():
                self.score += self.settings.alien_points * len(hit_aliens)
                for alien in hit_aliens:
                    self._try_spawn_bonus(alien.rect.centerx, alien.rect.centery)
            self._play_sound(self.explosion_sound)
        else:
            collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)
            if collisions:
                for hit_aliens in collisions.values():
                    self.score += self.settings.alien_points * len(hit_aliens)
                    for alien in hit_aliens:
                        self._try_spawn_bonus(alien.rect.centerx, alien.rect.centery)
                self._play_sound(self.explosion_sound)
        
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.level += 1
    
    def _try_spawn_bonus(self, x, y):
        if random.random() < self.settings.bonus_drop_chance:
            bonus = Bonus(self, x, y)
            self.bonuses.add(bonus)
    
    def _update_bonuses(self):
        self.bonuses.update()
        
        for bonus in self.bonuses.copy():
            if bonus.rect.top > self.settings.screen_height:
                self.bonuses.remove(bonus)
        
        collected = pygame.sprite.spritecollide(self.ship, self.bonuses, True)
        for bonus in collected:
            self._apply_bonus(bonus)
    
    def _apply_bonus(self, bonus):
        self._play_sound(self.bonus_sound)
        current_time = pygame.time.get_ticks()
        
        if bonus.bonus_type == Bonus.LIFE:
            self.ships_left += 1
        elif bonus.bonus_type == Bonus.SHIELD:
            self.ship.activate_shield(current_time)
        elif bonus.bonus_type == Bonus.POWER:
            self.power_bullet_active = True
            self.power_bullet_end_time = current_time + self.settings.power_bullet_duration
    
    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        
        if not self.ship.shield_active:
            if pygame.sprite.spritecollideany(self.ship, self.aliens):
                self._ship_hit()
        
        self._check_aliens_bottom()
    
    def _ship_hit(self):
        if self.ships_left > 0:
            self.ships_left -= 1
            self._play_sound(self.ship_hit_sound)
            
            self.bullets.empty()
            self.aliens.empty()
            self.bonuses.empty()
            
            self._create_fleet()
            self.ship.center_ship()
            
            pygame.time.delay(500)
        else:
            self.game_active = False
            self._play_sound(self.game_over_sound)
    
    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                if not self.ship.shield_active:
                    self._ship_hit()
                break
    
    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - 
                            (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
    
    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
    
    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    
    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        
        self.ship.bltime()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        for bonus in self.bonuses.sprites():
            bonus.draw_bonus()
        
        self._draw_hud()
        
        if not self.game_active:
            self._show_game_over()
        
        pygame.display.flip()
    
    def _draw_hud(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        lives_text = self.font.render(f"Lives: {self.ships_left}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 45))
        self.screen.blit(lives_text, (10, 80))
        
        if self.ship.shield_active:
            shield_text = self.font.render("SHIELD", True, (80, 180, 255))
            self.screen.blit(shield_text, (self.settings.screen_width - 120, 10))
        
        if self.power_bullet_active:
            power_text = self.font.render("POWER", True, (255, 220, 80))
            self.screen.blit(power_text, (self.settings.screen_width - 120, 45))
    
    def _show_game_over(self):
        overlay = pygame.Surface((self.settings.screen_width, 
                                  self.settings.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("GAME OVER", True, (255, 255, 255))
        text_rect = game_over_text.get_rect(
            center=(self.settings.screen_width // 2, 
                   self.settings.screen_height // 2 - 80))
        self.screen.blit(game_over_text, text_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(
            center=(self.settings.screen_width // 2, 
                   self.settings.screen_height // 2 - 20))
        self.screen.blit(score_text, score_rect)
        
        level_text = self.font.render(f"Level Reached: {self.level}", True, (255, 255, 255))
        level_rect = level_text.get_rect(
            center=(self.settings.screen_width // 2, 
                   self.settings.screen_height // 2 + 15))
        self.screen.blit(level_text, level_rect)
        
        font_small = pygame.font.Font(None, 30)
        restart_text = font_small.render(
            "Press P to play again", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(
            center=(self.settings.screen_width // 2, 
                   self.settings.screen_height // 2 + 70))
        self.screen.blit(restart_text, restart_rect)
        
        save_hint = font_small.render(
            "S - save | L - load", True, (150, 150, 150))
        save_rect = save_hint.get_rect(
            center=(self.settings.screen_width // 2, 
                   self.settings.screen_height // 2 + 105))
        self.screen.blit(save_hint, save_rect)


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()