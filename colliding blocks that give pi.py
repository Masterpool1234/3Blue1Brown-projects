import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLOCK_COLOR = (0, 0, 255)
WALL_COLOR = (255, 0, 0)
FLOOR_COLOR = (0, 255, 0)
FPS = 60
FLOOR_HEIGHT = 20
INITIAL_SPEED = 1.0

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Block Collision Simulation')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

class Block:
    def __init__(self, mass, velocity, position, width):
        self.mass = mass
        self.velocity = velocity
        self.position = position
        self.width = width

    def update_position(self, speed):
        self.position += self.velocity * speed

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.grabbed = False

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)
        handle_x = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 5, 10, self.rect.height + 10)
        pygame.draw.rect(surface, BLOCK_COLOR, handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.grabbed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False
        elif event.type == pygame.MOUSEMOTION and self.grabbed:
            self.val = self.min_val + (event.pos[0] - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
            self.val = max(self.min_val, min(self.val, self.max_val))

    def get_value(self):
        return self.val

class TextBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return 0

class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('dodgerblue2')
        self.text = text
        self.txt_surface = font.render(text, True, BLACK)
        self.action = action

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.action()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + (self.rect.w - self.txt_surface.get_width()) / 2,
                                       self.rect.y + (self.rect.h - self.txt_surface.get_height()) / 2))

def handle_collision(block1, block2):
    u1, u2 = block1.velocity, block2.velocity
    m1, m2 = block1.mass, block2.mass

    block1.velocity = (u1 * (m1 - m2) + 2 * m2 * u2) / (m1 + m2)
    block2.velocity = (u2 * (m2 - m1) + 2 * m1 * u1) / (m1 + m2)

def draw_static_elements(slider, text_box1, text_box2, button):
    screen.fill(WHITE)
    pygame.draw.rect(screen, FLOOR_COLOR, (0, SCREEN_HEIGHT - FLOOR_HEIGHT, SCREEN_WIDTH, FLOOR_HEIGHT))
    pygame.draw.rect(screen, WALL_COLOR, (SCREEN_WIDTH - 50, 0, 10, SCREEN_HEIGHT - FLOOR_HEIGHT))
    slider.draw(screen)
    text_box1.draw(screen)
    text_box2.draw(screen)
    button.draw(screen)

def draw_dynamic_elements(block1, block2, collision_count):
    pygame.draw.rect(screen, BLOCK_COLOR, (block1.position, SCREEN_HEIGHT - FLOOR_HEIGHT - block1.width, block1.width, block1.width))
    pygame.draw.rect(screen, BLOCK_COLOR, (block2.position, SCREEN_HEIGHT - FLOOR_HEIGHT - block2.width, block2.width, block2.width))
    block1_label = font.render(f'{block1.mass}kg', True, BLACK)
    block2_label = font.render(f'{block2.mass}kg', True, BLACK)
    screen.blit(block1_label, (block1.position, SCREEN_HEIGHT - FLOOR_HEIGHT - block1.width - 20))
    screen.blit(block2_label, (block2.position, SCREEN_HEIGHT - FLOOR_HEIGHT - block2.width - 20))
    collision_label = font.render(f'Collisions: {collision_count}', True, BLACK)
    screen.blit(collision_label, (50, 50))

def restart_simulation(block1, block2, slider, text_box1, text_box2, collision_count):
    block1.mass = text_box1.get_value()
    block1.velocity = 0
    block1.position = 500

    block2.mass = text_box2.get_value()
    block2.velocity = 2
    block2.position = 100

    slider.val = INITIAL_SPEED
    collision_count[0] = 0  # Reset collision count

def main():
    # Initialize blocks and slider
    block1 = Block(10, 0, 500, 50)
    block2 = Block(100, 2, 100, 50)
    slider = Slider(300, 50, 200, 20, 0.1, 5.0, INITIAL_SPEED)
    text_box1 = TextBox(300, 100, 50, 32, '10')
    text_box2 = TextBox(360, 100, 50, 32, '100')
    collision_count = [0]  # Use a list to allow modification within restart_simulation
    button = Button(420, 100, 100, 32, 'Restart', lambda: restart_simulation(block1, block2, slider, text_box1, text_box2, collision_count))

    # Main simulation loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            slider.handle_event(event)
            text_box1.handle_event(event)
            text_box2.handle_event(event)
            button.handle_event(event)

        # Update block masses from text boxes
        block1.mass = text_box1.get_value()
        block2.mass = text_box2.get_value()

        # Get current speed from slider
        speed = slider.get_value()

        # Update positions
        block1.update_position(speed)
        block2.update_position(speed)

        # Check for collisions
        if block1.position <= block2.position + block2.width:
            handle_collision(block1, block2)
            collision_count[0] += 1
            block1.position = block2.position + block2.width

        if block1.position + block1.width >= SCREEN_WIDTH - 50:
            block1.velocity = -abs(block1.velocity)
            collision_count[0] += 1
            block1.position = SCREEN_WIDTH - 50 - block1.width

        draw_static_elements(slider, text_box1, text_box2, button)
        draw_dynamic_elements(block1, block2, collision_count[0])

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
