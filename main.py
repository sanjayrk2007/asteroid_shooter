import pygame
import sys
import math
import random
from player import Player
from bullet import Bullet
from asteroid import AsteroidManager
from bullet_manager import BulletManager
from explosion import ExplosionManager
from leaderboard import Leaderboard
from sounds import SoundManager

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h

FPS = 60

# Professional Color Palette
COLOR_BG_DARK = (10, 12, 20)
COLOR_BG_MEDIUM = (20, 25, 35)
COLOR_ACCENT_PRIMARY = (0, 255, 255)
COLOR_ACCENT_SECONDARY = (138, 43, 226)
COLOR_SUCCESS = (0, 255, 127)
COLOR_WARNING = (255, 165, 0)
COLOR_DANGER = (255, 69, 58)
COLOR_GOLD = (255, 215, 0)
COLOR_SILVER = (192, 192, 192)
COLOR_BRONZE = (205, 127, 50)
COLOR_TEXT_PRIMARY = (255, 255, 255)
COLOR_TEXT_SECONDARY = (150, 160, 180)
COLOR_PANEL_BG = (25, 30, 45, 220)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("AIC Asteroid Shooter")
        self.clock = pygame.time.Clock()
        
        # Professional Font Setup
        self.font_xs = pygame.font.SysFont("Segoe UI", 16, bold=False)
        self.font_sm = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_md = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_lg = pygame.font.SysFont("Segoe UI", 40, bold=True)
        self.font_xl = pygame.font.SysFont("Segoe UI", 56, bold=True)
        self.font_xxl = pygame.font.SysFont("Segoe UI", 80, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 120, bold=True)
        self.bullet_font = pygame.font.SysFont("Arial", 32, bold=True)
        
        self.leaderboard = Leaderboard("leaderboard.json")
        self.sound_manager = SoundManager()

        self.player_name = ""
        self.players_queue = []
        self.current_player = None
        self.cursor_blink = 0
        self.animation_timer = 0
        self.particle_effects = []

        self.state = "START_SCREEN"
        self.asteroids = None
        self.bullets = None
        self.explosions = None
        self.player = None
        self.score = 0
        self.lives = 3
        self.time_left = 30.0
        
        # Background effects
        self.stars = self.generate_stars(200)

    def generate_stars(self, count):
        """Generate parallax star field"""
        stars = []
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 2)
            speed = random.uniform(0.05, 0.3)
            brightness = random.randint(120, 255)
            stars.append({
                'x': x, 'y': y, 'size': size, 
                'speed': speed, 'brightness': brightness
            })
        return stars

    def draw_starfield(self):
        """Draw animated starfield background - FIXED"""
        self.screen.fill(COLOR_BG_DARK)
        
        for star in self.stars:
            star['x'] = (star['x'] - star['speed']) % SCREEN_WIDTH
            alpha = star['brightness'] + int(30 * math.sin(self.animation_timer * 0.03 + star['x']))
            alpha = max(80, min(255, alpha))
            color = (alpha, alpha, alpha)  # Fixed: simple RGB tuple
            pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), star['size'])

    def draw_glass_panel(self, x, y, width, height, alpha=220):
        """Draw modern glassmorphism panel"""
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Background with gradient
        for i in range(height):
            gradient_factor = i / height
            bg_alpha = int(alpha * (0.8 + 0.2 * gradient_factor))
            color = (*COLOR_PANEL_BG[:3], bg_alpha)
            pygame.draw.line(panel, color, (0, i), (width, i))
        
        # Border glow
        border_color = (*COLOR_ACCENT_PRIMARY, 180)
        pygame.draw.rect(panel, border_color, (0, 0, width, height), 2, border_radius=12)
        
        # Inner highlight
        highlight = (*COLOR_TEXT_PRIMARY, 40)
        pygame.draw.line(panel, highlight, (12, 3), (width - 12, 3), 1)
        
        self.screen.blit(panel, (x, y))

    def draw_text_with_shadow(self, text, x, y, font, color, center=True, shadow_offset=2):
        """Draw text with drop shadow"""
        # Shadow
        shadow = font.render(text, True, (0, 0, 0, 180))
        shadow_rect = shadow.get_rect(center=(x + shadow_offset, y + shadow_offset)) if center else shadow.get_rect(topleft=(x + shadow_offset, y + shadow_offset))
        self.screen.blit(shadow, shadow_rect)
        
        # Main text
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(x, y)) if center else text_surf.get_rect(topleft=(x, y))
        self.screen.blit(text_surf, text_rect)
        return text_rect

    def draw_progress_bar(self, x, y, width, height, progress, color_start, color_end):
        """Draw modern progress bar with gradient"""
        # Background
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((30, 35, 50, 200))
        self.screen.blit(bg, (x, y))
        
        # Fill
        fill_width = int(width * progress)
        if fill_width > 0:
            fill = pygame.Surface((fill_width, height), pygame.SRCALPHA)
            for i in range(fill_width):
                ratio = i / width
                r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
                g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
                b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
                pygame.draw.line(fill, (r, g, b), (i, 0), (i, height))
            self.screen.blit(fill, (x, y))
        
        # Border
        pygame.draw.rect(self.screen, COLOR_ACCENT_PRIMARY, (x, y, width, height), 2, border_radius=6)

    def draw_particles(self):
        """Draw particle effects"""
        for particle in self.particle_effects[:]:
            particle['y'] -= particle['speed']
            particle['x'] += math.sin(particle['y'] * 0.02) * 0.3
            particle['alpha'] -= 3
            
            if particle['alpha'] <= 0:
                self.particle_effects.remove(particle)
            else:
                surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                color = (*particle['color'][:3], particle['alpha'])
                pygame.draw.circle(surf, color, (particle['size'], particle['size']), particle['size'])
                self.screen.blit(surf, (int(particle['x']) - particle['size'], int(particle['y']) - particle['size']))

    def spawn_particles(self, x, y, count=8, color=COLOR_ACCENT_PRIMARY):
        """Spawn particle burst"""
        for _ in range(count):
            self.particle_effects.append({
                'x': x + random.randint(-20, 20),
                'y': y + random.randint(-20, 20),
                'speed': random.uniform(1, 3),
                'size': random.randint(2, 4),
                'color': color,
                'alpha': 255
            })

    def start_screen(self):
        """Professional start screen UI"""
        self.draw_starfield()
        self.animation_timer += 1
        
        # Title area with accent
        title_y = SCREEN_HEIGHT // 5
        
        # Animated accent line
        line_width = 600 + int(50 * math.sin(self.animation_timer * 0.05))
        pygame.draw.line(self.screen, COLOR_ACCENT_SECONDARY, 
                        (SCREEN_WIDTH//2 - line_width//2, title_y - 30),
                        (SCREEN_WIDTH//2 + line_width//2, title_y - 30), 3)
        
        # Main title
        self.draw_text_with_shadow("ASTEROID SHOOTER", SCREEN_WIDTH//2, title_y, 
                                   self.font_title, COLOR_ACCENT_PRIMARY, shadow_offset=4)
        
        # Subtitle
        pulse = 0.7 + 0.3 * math.sin(self.animation_timer * 0.08)
        subtitle_color = tuple(int(c * pulse) for c in COLOR_ACCENT_SECONDARY)
        self.draw_text_with_shadow("AIC Club Expo", SCREEN_WIDTH//2, title_y + 100, 
                                   self.font_xl, subtitle_color, shadow_offset=2)
        
        # Input panel
        panel_width = 700
        panel_height = 200
        panel_x = SCREEN_WIDTH//2 - panel_width//2
        panel_y = SCREEN_HEIGHT//2 - 50
        
        self.draw_glass_panel(panel_x, panel_y, panel_width, panel_height)
        
        # Input label
        self.draw_text_with_shadow("ENTER YOUR NAME", SCREEN_WIDTH//2, panel_y + 50, 
                                   self.font_lg, COLOR_TEXT_PRIMARY)
        
        # Input field
        input_width = 600
        input_height = 60
        input_x = SCREEN_WIDTH//2 - input_width//2
        input_y = panel_y + 110
        
        # Input box with glow
        glow_alpha = int(80 + 40 * math.sin(self.animation_timer * 0.1))
        glow_surf = pygame.Surface((input_width + 10, input_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*COLOR_ACCENT_PRIMARY, glow_alpha), (0, 0, input_width + 10, input_height + 10), border_radius=8)
        self.screen.blit(glow_surf, (input_x - 5, input_y - 5), special_flags=pygame.BLEND_ADD)
        
        pygame.draw.rect(self.screen, (35, 40, 55), (input_x, input_y, input_width, input_height), border_radius=8)
        pygame.draw.rect(self.screen, COLOR_ACCENT_PRIMARY, (input_x, input_y, input_width, input_height), 2, border_radius=8)
        
        # Input text
        self.cursor_blink += 1
        cursor = "│" if (self.cursor_blink // 25) % 2 == 0 else ""
        display_text = self.player_name + cursor if self.player_name else "Type here..." + cursor
        text_color = COLOR_TEXT_PRIMARY if self.player_name else COLOR_TEXT_SECONDARY
        
        input_surf = self.font_lg.render(display_text, True, text_color)
        input_rect = input_surf.get_rect(center=(SCREEN_WIDTH//2, input_y + input_height//2))
        self.screen.blit(input_surf, input_rect)
        
        # Controls info
        controls_y = SCREEN_HEIGHT - 200
        control_panel_width = 1000
        self.draw_glass_panel(SCREEN_WIDTH//2 - control_panel_width//2, controls_y, control_panel_width, 150, alpha=180)
        
        controls = [
            ("◄►", "ROTATE"),
            ("▲", "THRUST"),
            ("SPACE", "SHOOT"),
            ("ESC", "EXIT")
        ]
        
        spacing = control_panel_width // len(controls)
        for i, (key, desc) in enumerate(controls):
            x = SCREEN_WIDTH//2 - control_panel_width//2 + spacing//2 + i * spacing
            
            # Key display
            key_surf = self.font_lg.render(key, True, COLOR_ACCENT_PRIMARY)
            key_rect = key_surf.get_rect(center=(x, controls_y + 50))
            self.screen.blit(key_surf, key_rect)
            
            # Description
            desc_surf = self.font_sm.render(desc, True, COLOR_TEXT_SECONDARY)
            desc_rect = desc_surf.get_rect(center=(x, controls_y + 100))
            self.screen.blit(desc_surf, desc_rect)
        
        # Start prompt
        prompt_alpha = int(200 + 55 * math.sin(self.animation_timer * 0.15))
        prompt_color = (*COLOR_SUCCESS, prompt_alpha)
        self.draw_text_with_shadow("PRESS ENTER TO START", SCREEN_WIDTH//2, SCREEN_HEIGHT - 80, 
                                   self.font_xl, prompt_color)
        
        self.draw_particles()
        pygame.display.flip()

    def game_over_screen(self):
        """Professional game over screen"""
        self.draw_starfield()
        self.animation_timer += 1
        
        # Red overlay pulse
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pulse_alpha = int(30 * abs(math.sin(self.animation_timer * 0.06)))
        overlay.fill((255, 0, 0, pulse_alpha))
        self.screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 900
        panel_height = 550
        panel_x = SCREEN_WIDTH//2 - panel_width//2
        panel_y = SCREEN_HEIGHT//2 - panel_height//2 - 50
        
        self.draw_glass_panel(panel_x, panel_y, panel_width, panel_height)
        
        # Game Over title
        self.draw_text_with_shadow("GAME OVER", SCREEN_WIDTH//2, panel_y + 80, 
                                   self.font_xxl, COLOR_DANGER, shadow_offset=4)
        
        # Stats section
        stats_y = panel_y + 200
        
        # Player
        self.draw_text_with_shadow("PLAYER", SCREEN_WIDTH//2, stats_y, 
                                   self.font_sm, COLOR_TEXT_SECONDARY)
        self.draw_text_with_shadow(self.current_player.upper(), SCREEN_WIDTH//2, stats_y + 40, 
                                   self.font_xl, COLOR_ACCENT_PRIMARY, shadow_offset=3)
        
        # Score
        self.draw_text_with_shadow("FINAL SCORE", SCREEN_WIDTH//2, stats_y + 120, 
                                   self.font_sm, COLOR_TEXT_SECONDARY)
        self.draw_text_with_shadow(str(self.score), SCREEN_WIDTH//2, stats_y + 170, 
                                   self.font_xxl, COLOR_GOLD, shadow_offset=3)
        
        # Rank
        rank = self.leaderboard.get_player_rank(self.current_player, self.score)
        self.draw_text_with_shadow(f"WORLD RANK: #{rank}", SCREEN_WIDTH//2, stats_y + 260, 
                                   self.font_lg, COLOR_SUCCESS)
        
        # Continue prompt
        prompt_pulse = 200 + int(55 * math.sin(self.animation_timer * 0.12))
        self.draw_text_with_shadow("PRESS ENTER TO CONTINUE", SCREEN_WIDTH//2, panel_y + panel_height - 50, 
                                   self.font_lg, (*COLOR_ACCENT_PRIMARY, prompt_pulse))
        
        # Side leaderboard
        self.draw_mini_leaderboard(SCREEN_WIDTH - 370, 50)
        
        self.draw_particles()
        pygame.display.flip()

    def leaderboard_screen(self):
        """Professional full leaderboard"""
        self.draw_starfield()
        self.animation_timer += 1
        
        # Title
        self.draw_text_with_shadow("🏆 HALL OF FAME", SCREEN_WIDTH//2, 100, 
                                   self.font_xxl, COLOR_GOLD, shadow_offset=4)
        
        # Main panel
        panel_width = 1100
        panel_height = SCREEN_HEIGHT - 400
        panel_x = SCREEN_WIDTH//2 - panel_width//2
        panel_y = 200
        
        self.draw_glass_panel(panel_x, panel_y, panel_width, panel_height)
        
        # Headers
        header_y = panel_y + 40
        headers = [
            ("RANK", panel_x + 80),
            ("PLAYER", panel_x + 350),
            ("SCORE", panel_x + 700),
            ("DATE", panel_x + 920)
        ]
        
        for header, x in headers:
            self.draw_text_with_shadow(header, x, header_y, self.font_md, COLOR_ACCENT_PRIMARY, center=True, shadow_offset=1)
        
        # Divider
        pygame.draw.line(self.screen, COLOR_ACCENT_SECONDARY, 
                        (panel_x + 40, header_y + 40), 
                        (panel_x + panel_width - 40, header_y + 40), 2)
        
        # Scores
        scores = self.leaderboard.get_top_scores()
        entry_y = header_y + 80
        
        for i, entry in enumerate(scores[:12]):
            # Rank color
            if i == 0:
                rank_color = COLOR_GOLD
            elif i == 1:
                rank_color = COLOR_SILVER
            elif i == 2:
                rank_color = COLOR_BRONZE
            else:
                rank_color = COLOR_TEXT_PRIMARY
            
            # Highlight top 3
            if i < 3:
                highlight = pygame.Surface((panel_width - 80, 50), pygame.SRCALPHA)
                highlight.fill((*rank_color, 20))
                self.screen.blit(highlight, (panel_x + 40, entry_y - 20))
            
            # Data
            rank_text = f"#{i+1}"
            name = entry['name'][:20]
            score = str(entry['score'])
            date = entry.get('timestamp', 'N/A')[:10]
            
            # Draw entry
            self.draw_text_with_shadow(rank_text, panel_x + 80, entry_y, self.font_lg, rank_color, shadow_offset=1)
            self.draw_text_with_shadow(name, panel_x + 350, entry_y, self.font_lg, COLOR_TEXT_PRIMARY, shadow_offset=1)
            self.draw_text_with_shadow(score, panel_x + 700, entry_y, self.font_lg, COLOR_ACCENT_PRIMARY if i < 3 else COLOR_TEXT_PRIMARY, shadow_offset=1)
            self.draw_text_with_shadow(date, panel_x + 920, entry_y, self.font_sm, COLOR_TEXT_SECONDARY, shadow_offset=1)
            
            entry_y += 55
        
        # No scores
        if not scores:
            self.draw_text_with_shadow("NO SCORES YET - BE THE FIRST!", 
                                      SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 
                                      self.font_xl, COLOR_ACCENT_PRIMARY)
        
        # Instructions
        inst_y = SCREEN_HEIGHT - 120
        self.draw_glass_panel(SCREEN_WIDTH//2 - 400, inst_y, 800, 80, alpha=200)
        self.draw_text_with_shadow("ENTER: Next Player  │  Q: Quit", 
                                  SCREEN_WIDTH//2, inst_y + 40, 
                                  self.font_lg, COLOR_TEXT_PRIMARY)
        
        self.draw_particles()
        pygame.display.flip()

    def draw_mini_leaderboard(self, x, y):
        """Draw compact leaderboard"""
        scores = self.leaderboard.get_top_scores(5)
        
        panel_width = 350
        panel_height = 80 + len(scores) * 60
        
        self.draw_glass_panel(x, y, panel_width, panel_height, alpha=230)
        
        # Title
        self.draw_text_with_shadow("TOP PLAYERS", x + panel_width//2, y + 40, 
                                   self.font_md, COLOR_ACCENT_PRIMARY, shadow_offset=1)
        
        # Entries
        entry_y = y + 80
        for i, entry in enumerate(scores):
            color = [COLOR_GOLD, COLOR_SILVER, COLOR_BRONZE][i] if i < 3 else COLOR_TEXT_PRIMARY
            
            name = entry['name'][:12]
            score = str(entry['score'])
            
            # Name
            name_surf = self.font_sm.render(f"{i+1}. {name}", True, color)
            self.screen.blit(name_surf, (x + 20, entry_y))
            
            # Score
            score_surf = self.font_md.render(score, True, COLOR_ACCENT_PRIMARY)
            score_rect = score_surf.get_rect(right=x + panel_width - 20, centery=entry_y + 10)
            self.screen.blit(score_surf, score_rect)
            
            entry_y += 60

    def draw_game(self):
        """Professional gameplay UI"""
        game_width = SCREEN_WIDTH - 400
        
        self.draw_starfield()
        
        # Game area border
        for i in range(5):
            alpha = 60 - i * 12
            pygame.draw.line(self.screen, (*COLOR_ACCENT_PRIMARY, alpha), 
                           (game_width + i, 0), (game_width + i, SCREEN_HEIGHT))
        
        # Draw entities
        self.player.draw(self.screen)
        self.bullets.draw(self.screen)
        self.asteroids.draw(self.screen)
        self.explosions.draw(self.screen)
        
        # HUD - Player & Score
        self.draw_glass_panel(20, 20, 300, 120)
        self.draw_text_with_shadow(f"👤 {self.current_player[:12]}", 30, 50, 
                                   self.font_md, COLOR_ACCENT_PRIMARY, center=False, shadow_offset=1)
        self.draw_text_with_shadow(f"SCORE: {self.score}", 30, 95, 
                                   self.font_lg, COLOR_GOLD, center=False, shadow_offset=2)
        
        # Lives
        self.draw_glass_panel(20, 160, 300, 100)
        self.draw_text_with_shadow("LIVES", 30, 185, self.font_sm, COLOR_TEXT_SECONDARY, center=False)
        
        for i in range(self.lives):
            ship_x = 40 + i * 70
            ship_y = 225
            points = [(ship_x+10, ship_y-8), (ship_x, ship_y+8), (ship_x+20, ship_y+8)]
            pygame.draw.polygon(self.screen, COLOR_ACCENT_PRIMARY, points)
            pygame.draw.polygon(self.screen, COLOR_TEXT_PRIMARY, points, 1)
        
        # Timer
        timer_width = 350
        timer_x = game_width//2 - timer_width//2
        self.draw_glass_panel(timer_x, 20, timer_width, 140)
        
        self.draw_text_with_shadow("TIME", game_width//2, 50, self.font_sm, COLOR_TEXT_SECONDARY)
        
        time_remaining = int(self.time_left)
        if time_remaining > 15:
            time_color = COLOR_SUCCESS
        elif time_remaining > 5:
            time_color = COLOR_WARNING
        else:
            time_color = COLOR_DANGER
        
        self.draw_text_with_shadow(f"{time_remaining}s", game_width//2, 100, 
                                   self.font_xxl, time_color, shadow_offset=3)
        
        # Progress bar
        bar_width = 300
        bar_x = game_width//2 - bar_width//2
        progress = max(0, self.time_left / 30.0)
        
        if progress > 0.6:
            bar_colors = (COLOR_SUCCESS, COLOR_SUCCESS)
        elif progress > 0.3:
            bar_colors = (COLOR_WARNING, COLOR_WARNING)
        else:
            bar_colors = (COLOR_DANGER, COLOR_DANGER)
        
        self.draw_progress_bar(bar_x, 135, bar_width, 12, progress, bar_colors[0], bar_colors[1])
        
        # Side leaderboard
        self.draw_mini_leaderboard(SCREEN_WIDTH - 380, 20)
        
        # Stats
        stats_y = SCREEN_HEIGHT - 200
        self.draw_glass_panel(SCREEN_WIDTH - 380, stats_y, 360, 180)
        
        self.draw_text_with_shadow("GAME STATS", SCREEN_WIDTH - 200, stats_y + 30, 
                                   self.font_md, COLOR_ACCENT_PRIMARY)
        
        stats = [
            (f"Asteroids: {len(self.asteroids.asteroids)}", stats_y + 75),
            (f"Bullets: {len(self.bullets.bullets)}", stats_y + 110),
            (f"High: {self.leaderboard.get_high_score()}", stats_y + 145)
        ]
        
        for text, y_pos in stats:
            self.draw_text_with_shadow(text, SCREEN_WIDTH - 360, y_pos, 
                                      self.font_sm, COLOR_TEXT_PRIMARY, center=False)
        
        self.draw_particles()
        pygame.display.flip()

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.time_left = 30.0
        self.player = Player(SCREEN_WIDTH//4, SCREEN_HEIGHT//2, sound_manager=self.sound_manager.play)
        self.asteroids = AsteroidManager(SCREEN_WIDTH - 400, SCREEN_HEIGHT)
        self.bullets = BulletManager(self.bullet_font, sound_manager=self.sound_manager.play)
        self.explosions = ExplosionManager()
        self.asteroids.spawn_initial()

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.state == "START_SCREEN":
                    self.handle_start_screen(event)
                elif self.state == "PLAYING":
                    self.handle_game_events(event)
                elif self.state == "GAME_OVER":
                    self.handle_game_over(event)
                elif self.state == "LEADERBOARD":
                    self.handle_leaderboard(event)

            if self.state == "START_SCREEN":
                self.start_screen()
            elif self.state == "PLAYING":
                self.update_game()
                self.draw_game()
            elif self.state == "GAME_OVER":
                self.game_over_screen()
            elif self.state == "LEADERBOARD":
                self.leaderboard_screen()

    def handle_start_screen(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.player_name.strip():
                self.players_queue.append(self.player_name.strip())
                self.player_name = ""
                self.next_player()
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            else:
                if len(event.unicode) == 1 and event.unicode.isprintable() and len(self.player_name) < 20:
                    self.player_name += event.unicode

    def handle_game_over(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.leaderboard.add_score(self.current_player, self.score)
            self.leaderboard.save()
            self.state = "LEADERBOARD"

    def handle_leaderboard(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = "START_SCREEN"
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    def next_player(self):
        self.current_player = self.players_queue.pop(0) if self.players_queue else "Player1"
        self.reset_game()
        self.state = "PLAYING"

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.player.rotating_left = True
            elif event.key == pygame.K_RIGHT:
                self.player.rotating_right = True
            elif event.key == pygame.K_UP:
                self.player.thrusting = True
            elif event.key == pygame.K_SPACE:
                self.player.shooting = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.player.rotating_left = False
            elif event.key == pygame.K_RIGHT:
                self.player.rotating_right = False
            elif event.key == pygame.K_UP:
                self.player.thrusting = False
            elif event.key == pygame.K_SPACE:
                self.player.shooting = False

    def update_game(self):
        if self.state != "PLAYING":
            return
        
        self.animation_timer += 1
        self.player.update()
        self.bullets.update()
        self.asteroids.update()
        self.explosions.update()
        
        if self.player.shooting:
            bullet_info = self.player.shoot()
            if bullet_info:
                bullet = Bullet(*bullet_info, font=self.bullet_font, sound_manager=self.sound_manager.play)
                self.bullets.add(bullet)
        
        self.handle_collisions()
        self.time_left -= 1.0 / FPS
        
        if self.lives <= 0 or self.time_left <= 0:
            self.time_left = max(0, self.time_left)
            self.state = "GAME_OVER"
            self.sound_manager.play('explosion')

    def handle_collisions(self):
        for bullet in self.bullets.bullets[:]:
            for asteroid in self.asteroids.asteroids[:]:
                if asteroid.rect.collidepoint(bullet.pos):
                    self.score += asteroid.point_value
                    self.explosions.create_explosion(asteroid.pos, asteroid.size * 10, 'asteroid')
                    self.asteroids.destroy(asteroid)
                    if bullet in self.bullets.bullets:
                        self.bullets.bullets.remove(bullet)
                    self.sound_manager.play('hit')
                    self.spawn_particles(asteroid.pos.x, asteroid.pos.y, 12, COLOR_WARNING)
                    break
        
        for asteroid in self.asteroids.asteroids:
            if asteroid.rect.colliderect(self.player.rect):
                self.lives -= 1
                self.explosions.create_explosion(self.player.pos, 30, 'normal')
                self.player.respawn()
                self.sound_manager.play('explosion')
                self.spawn_particles(self.player.pos.x, self.player.pos.y, 15, COLOR_DANGER)
                break


if __name__ == "__main__":
    game = Game()
    game.run()
