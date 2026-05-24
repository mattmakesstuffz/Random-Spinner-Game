import pygame
import math
import os

pygame.init()

# Window setup
WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RANDOM SPINNER GAME (R.S.G)")

# ✅ Add window icon (looks inside Downloads folder)
downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "icon.png")
icon = pygame.image.load(downloads_path)
pygame.display.set_icon(icon)

# Colors
WHITE = (255, 255, 255)
BLUE = (100, 149, 237)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)

# Shapes and slice counts
shapes = {"Circle": 6, "Triangle": 3, "Square": 4, "Hexagon": 6}
current_shape = "Circle"

rotation_angle = 0
dragging = False
last_angle = None
spin_speed = 0
result_text = ""

# Default font
font = pygame.font.SysFont(None, 28)

# Game states
MENU = "menu"
GAME = "game"
state = MENU

# Input box setup
input_boxes = []
options = []

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = font.render(text, True, WHITE)  # text is white
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, WHITE)

    def draw(self, screen):
        # Fill background black
        pygame.draw.rect(screen, BLACK, self.rect)
        # Draw black outline
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        # Draw text
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

def get_angle(pos):
    dx = pos[0] - WIDTH//2
    dy = HEIGHT//2 - pos[1]
    return math.degrees(math.atan2(dy, dx))

def draw_background():
    # Gradient background
    for y in range(HEIGHT):
        color = (100+y//10, 149, 237-y//20)
        pygame.draw.line(screen, color, (0,y), (WIDTH,y))

def draw_wheel(angle):
    draw_background()
    slices = shapes[current_shape]
    angle_per_slice = 360 / slices
    radius = 200
    center = (WIDTH//2, HEIGHT//2)

    for i in range(slices):
        start_angle = math.radians(i * angle_per_slice + angle)
        end_angle = math.radians((i + 1) * angle_per_slice + angle)
        color = GOLD if i % 2 == 0 else BLUE

        pygame.draw.polygon(screen, color, [
            center,
            (center[0] + radius * math.cos(start_angle), center[1] - radius * math.sin(start_angle)),
            (center[0] + radius * math.cos(end_angle), center[1] - radius * math.sin(end_angle))
        ])

        if i < len(options) and options[i].strip() != "":
            text_angle = math.radians(i * angle_per_slice + angle + angle_per_slice / 2)
            text_x = center[0] + (radius / 2) * math.cos(text_angle)
            text_y = center[1] - (radius / 2) * math.sin(text_angle)
            label = font.render(options[i], True, BLACK)
            screen.blit(label, (text_x - label.get_width()//2, text_y - label.get_height()//2))

    # Pointer
    pygame.draw.polygon(screen, (255,0,0), [
        (center[0], center[1] - radius - 20),
        (center[0] - 20, center[1] - radius - 60),
        (center[0] + 20, center[1] - radius - 60)
    ])

    # Show result text
    if result_text:
        result_label = font.render(f"Result: {result_text}", True, BLACK)
        screen.blit(result_label, (WIDTH//2 - result_label.get_width()//2, HEIGHT - 80))

    pygame.display.flip()

def detect_result(angle):
    slices = shapes[current_shape]
    angle_per_slice = 360 / slices
    normalized_angle = (-angle) % 360
    index = int(normalized_angle // angle_per_slice)
    if index < len(options):
        return options[index]
    return ""

# Create input boxes dynamically based on shape
def create_input_boxes(shape):
    global input_boxes, options
    input_boxes.clear()
    slices = shapes[shape]
    if len(options) < slices:
        options += [f"Option {i+1}" for i in range(len(options), slices)]
    elif len(options) > slices:
        options = options[:slices]
    for i in range(slices):
        input_boxes.append(InputBox(250, 150 + i*60, 200, 40, options[i]))

create_input_boxes(current_shape)

running = True
clock = pygame.time.Clock()

while running:
    # ✅ Update window bar caption dynamically
    pygame.display.set_caption(f"RANDOM SPINNER GAME (R.S.G) | Shape: {current_shape} | State: {state.upper()}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            for box in input_boxes:
                box.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    options = [box.text if box.text.strip() != "" else f"Option {i+1}" for i, box in enumerate(input_boxes)]
                    state = GAME
                elif event.key == pygame.K_TAB:
                    # Cycle shapes
                    shape_keys = list(shapes.keys())
                    current_shape = shape_keys[(shape_keys.index(current_shape)+1) % len(shape_keys)]
                    create_input_boxes(current_shape)

        elif state == GAME:
            if event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
                last_angle = get_angle(event.pos)
                spin_speed = 0

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                last_angle = None
                result_text = detect_result(rotation_angle)

            if event.type == pygame.MOUSEMOTION and dragging:
                current_angle = get_angle(event.pos)
                delta = current_angle - last_angle
                rotation_angle += delta
                spin_speed = delta
                last_angle = current_angle

    if state == MENU:
        draw_background()
        title = font.render("RANDOM SPINNER GAME (R.S.G)", True, BLACK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        subtitle = font.render("Enter option names, press Enter to start", True, BLACK)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 80))
        shape_label = font.render(f"Shape: {current_shape} (TAB to change)", True, BLACK)
        screen.blit(shape_label, (WIDTH//2 - shape_label.get_width()//2, 110))
        for box in input_boxes:
            box.draw(screen)
        pygame.display.flip()

    elif state == GAME:
        if not dragging and abs(spin_speed) > 0.01:
            rotation_angle += spin_speed
            spin_speed *= 0.97  # smoother friction
        draw_wheel(rotation_angle)

    clock.tick(60)

pygame.quit()