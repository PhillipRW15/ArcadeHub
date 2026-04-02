import pygame
import random
import sys
import os
import math

# --- Configuration ---
GRID_SIZE = 20
TILE_SIZE = 30
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
FPS = 8
HIGHSCORE_FILE = "highscore.txt"

# Colors (Ultra-Premium Palette)
COLOR_BACKGROUND = (13, 17, 23)      # GitHub Dark
COLOR_GRID = (28, 33, 40)            # Slate
COLOR_SNAKE_HEAD = (0, 255, 127)    # Spring Green
COLOR_SNAKE_BODY = (46, 204, 113)    # Emerald
COLOR_FOOD = (255, 46, 99)           # Radical Red
COLOR_TEXT_PRIMARY = (236, 240, 241) # Clouds White
COLOR_TEXT_SECONDARY = (149, 165, 166)# Asbestos Gray
COLOR_ACCENT = (155, 89, 182)        # Amethyst

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 1.0  # Life from 1.0 to 0.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.05
        return self.life > 0

    def draw(self, screen):
        alpha = int(self.life * 255)
        color = (*self.color, alpha)
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        s.fill(color)
        screen.blit(s, (int(self.x), int(self.y)))

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Premium Snake v2.0")
        self.clock = pygame.time.Clock()
        self.fonts = {
            'main': pygame.font.SysFont("Inter, Roboto, Arial", 48, bold=True),
            'small': pygame.font.SysFont("Inter, Roboto, Arial", 24),
            'huge': pygame.font.SysFont("Inter, Roboto, Arial", 72, bold=True)
        }
        self.high_score = self.load_high_score()
        self.state = "START"  # START, PLAY, GAMEOVER
        self.particles = []
        self.shake_time = 0
        self.reset_game()

    def load_high_score(self):
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    return int(f.read())
            except:
                return 0
        return 0

    def save_high_score(self):
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(self.high_score))

    def reset_game(self):
        start_x = GRID_SIZE // 2
        start_y = GRID_SIZE // 2
        self.snake = [(start_x, start_y), (start_x, start_y+1), (start_x, start_y+2)]
        self.direction = (0, -1)
        self.next_direction = (0, -1)
        self.food = self.spawn_food()
        self.score = 0
        self.speed = FPS
        self.particles = []
        self.shake_time = 0

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if pos not in self.snake:
                return pos

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_high_score()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.state == "START":
                    if event.key == pygame.K_SPACE:
                        self.state = "PLAY"
                elif self.state == "PLAY":
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.next_direction = (1, 0)
                elif self.state == "GAMEOVER":
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = "PLAY"
                    elif event.key == pygame.K_m:
                        self.reset_game()
                        self.state = "START"

    def update(self):
        if self.state != "PLAY":
            # Just update particles in menu?
            self.particles = [p for p in self.particles if p.update()]
            return

        # Particle Update
        self.particles = [p for p in self.particles if p.update()]

        # Shake Update
        if self.shake_time > 0:
            self.shake_time -= 1

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Collision Check: Walls & Self
        if not (0 <= new_head[0] < GRID_SIZE and 0 <= new_head[1] < GRID_SIZE) or new_head in self.snake:
            self.state = "GAMEOVER"
            self.shake_time = 10
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
            self.speed += 0.2
            # Explode particles!
            for _ in range(15):
                self.particles.append(Particle(new_head[0]*TILE_SIZE + 15, new_head[1]*TILE_SIZE + 15, COLOR_SNAKE_HEAD))
        else:
            self.snake.pop()

    def draw_grid(self, surf):
        t = pygame.time.get_ticks() / 1000
        pulse = 20 + math.sin(t * 3) * 5
        grid_color = (int(pulse), int(pulse), int(pulse + 10))
        for x in range(0, WINDOW_SIZE, TILE_SIZE):
            pygame.draw.line(surf, grid_color, (x, 0), (x, WINDOW_SIZE))
        for y in range(0, WINDOW_SIZE, TILE_SIZE):
            pygame.draw.line(surf, grid_color, (0, y), (WINDOW_SIZE, y))

    def draw(self):
        draw_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        draw_surf.fill(COLOR_BACKGROUND)
        self.draw_grid(draw_surf)

        # Draw Food
        t = pygame.time.get_ticks() / 1000
        pulse = math.sin(t * 10) * 4
        food_rect = pygame.Rect(self.food[0]*TILE_SIZE+4-pulse/2, self.food[1]*TILE_SIZE+4-pulse/2, TILE_SIZE-8+pulse, TILE_SIZE-8+pulse)
        pygame.draw.ellipse(draw_surf, COLOR_FOOD, food_rect)
        # Glow
        glow_surf = pygame.Surface((TILE_SIZE + 20, TILE_SIZE + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLOR_FOOD, 50), (TILE_SIZE//2 + 10, TILE_SIZE//2 + 10), TILE_SIZE//2 + 5)
        draw_surf.blit(glow_surf, (self.food[0]*TILE_SIZE-10, self.food[1]*TILE_SIZE-10))

        # Draw Snake
        for i, (x, y) in enumerate(self.snake):
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            # Gradient effect for body
            if i > 0:
                fact = 1 - (i / len(self.snake))
                color = (int(color[0]*fact + 20), int(color[1]*fact + 35), int(color[2]*fact + 25))
            
            rect = pygame.Rect(x*TILE_SIZE+2, y*TILE_SIZE+2, TILE_SIZE-4, TILE_SIZE-4)
            pygame.draw.rect(draw_surf, color, rect, border_radius=8 if i == 0 else 4)

        # Particles
        for p in self.particles:
            p.draw(draw_surf)

        # UI
        if self.state == "PLAY":
            score_text = self.fonts['small'].render(f"SCORE: {self.score}", True, COLOR_TEXT_PRIMARY)
            hi_text = self.fonts['small'].render(f"HI-SCORE: {self.high_score}", True, COLOR_TEXT_SECONDARY)
            draw_surf.blit(score_text, (20, 20))
            draw_surf.blit(hi_text, (20, 50))
        elif self.state == "START":
            overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            draw_surf.blit(overlay, (0, 0))
            title = self.fonts['huge'].render("NEON SNAKE", True, COLOR_SNAKE_HEAD)
            prompt = self.fonts['main'].render("PRESS SPACE TO START", True, COLOR_TEXT_PRIMARY)
            hi_text = self.fonts['small'].render(f"ALL-TIME HI-SCORE: {self.high_score}", True, COLOR_ACCENT)
            
            draw_surf.blit(title, title.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 100)))
            draw_surf.blit(prompt, prompt.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2)))
            draw_surf.blit(hi_text, hi_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 150)))
        elif self.state == "GAMEOVER":
            overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
            overlay.fill((20, 0, 0, 200))
            draw_surf.blit(overlay, (0, 0))
            msg = self.fonts['huge'].render("GAME OVER", True, COLOR_FOOD)
            restart = self.fonts['main'].render("PRESS 'R' TO RESTART", True, COLOR_TEXT_PRIMARY)
            menu = self.fonts['small'].render("PRESS 'M' FOR MENU", True, COLOR_TEXT_SECONDARY)
            
            draw_surf.blit(msg, msg.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 50)))
            draw_surf.blit(restart, restart.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 50)))
            draw_surf.blit(menu, menu.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 120)))

        # Screen Shake
        offset = (0, 0)
        if self.shake_time > 0:
            offset = (random.randint(-10, 10), random.randint(-10, 10))
        
        self.screen.blit(draw_surf, offset)
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            # Dynamic FPS handling
            current_fps = self.speed if self.state == "PLAY" else 30
            self.clock.tick(current_fps)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
