#!/usr/bin/env python3
import random
import curses

# Game dimensions (internal playable area)
WIDTH = 30
HEIGHT = 15

# Game state
score = 0
lives = 5

# Dog position (center bottom of playable area)
dog_x = WIDTH // 2
dog_y = HEIGHT - 1

# Cats at the top - list of (x, symbol)
cats = []

# Lasers - list of {x, y}
lasers = []

# Frame counter for spawning
frame_count = 0
SPAWN_INTERVAL = 20  # Spawn new cat every 20 frames (2 seconds)

def init_cats():
    global cats
    cats = []
    positions = random.sample(range(WIDTH), 3)  # 3 unique random positions
    for x in positions:
        symbol = random.choice(['^', 'v'])
        cats.append({'x': x, 'y': 0, 'symbol': symbol})

def draw_canvas(stdscr):
    stdscr.clear()

    # Top wall
    stdscr.addstr(0, 0, "+" + "-" * WIDTH + "+")

    # Playable area with side walls
    for y in range(HEIGHT):
        row = "|"
        for x in range(WIDTH):
            # Check for dog
            if x == dog_x and y == dog_y:
                row += "@"
            # Check for lasers
            elif any(laser['x'] == x and laser['y'] == y for laser in lasers):
                row += "|"
            # Check for cats
            elif any(cat['x'] == x and cat['y'] == y for cat in cats):
                cat = next(c for c in cats if c['x'] == x and c['y'] == y)
                row += cat['symbol']
            else:
                row += " "
        row += "|"
        stdscr.addstr(y + 1, 0, row)

    # Bottom wall
    stdscr.addstr(HEIGHT + 1, 0, "+" + "-" * WIDTH + "+")

    # Status line
    stdscr.addstr(HEIGHT + 2, 0, f"Score: {score} | Lives: {lives} | SPACE: shoot | 'q': quit")

    stdscr.refresh()

def move_dog(direction):
    global dog_x
    if direction == 'left' and dog_x > 0:
        dog_x -= 1
    elif direction == 'right' and dog_x < WIDTH - 1:
        dog_x += 1

def shoot_laser():
    lasers.append({'x': dog_x, 'y': dog_y - 1})

def move_lasers():
    global lasers
    for laser in lasers:
        laser['y'] -= 1
    # Remove lasers that went off screen
    lasers = [laser for laser in lasers if laser['y'] >= 0]

def move_cats():
    for cat in cats:
        cat['y'] += 1

def spawn_cat():
    x = random.randint(0, WIDTH - 1)
    symbol = random.choice(['^', 'v'])
    cats.append({'x': x, 'y': 0, 'symbol': symbol})

def check_cat_reached_dog():
    global cats, lives
    cats_to_remove = []
    for cat in cats:
        if cat['y'] >= dog_y:
            cats_to_remove.append(cat)
            lives -= 1
    for cat in cats_to_remove:
        cats.remove(cat)

def check_collisions():
    global lasers, cats, score
    lasers_to_remove = []
    cats_to_remove = []

    for laser in lasers:
        for cat in cats:
            if laser['x'] == cat['x'] and laser['y'] == cat['y']:
                lasers_to_remove.append(laser)
                cats_to_remove.append(cat)
                score += 10

    for laser in lasers_to_remove:
        if laser in lasers:
            lasers.remove(laser)
    for cat in cats_to_remove:
        if cat in cats:
            cats.remove(cat)

def game_loop(stdscr):
    global frame_count, lives

    # Setup curses
    curses.curs_set(0)  # Hide cursor
    stdscr.keypad(True)  # Enable arrow keys
    stdscr.nodelay(True)  # Non-blocking input

    init_cats()

    while True:
        draw_canvas(stdscr)

        # Check for game over
        if lives <= 0:
            stdscr.nodelay(False)
            stdscr.addstr(HEIGHT // 2 + 1, WIDTH // 2 - 4, "GAME OVER!")
            stdscr.addstr(HEIGHT // 2 + 2, WIDTH // 2 - 8, f"Final Score: {score}")
            stdscr.addstr(HEIGHT // 2 + 3, WIDTH // 2 - 8, "Press any key...")
            stdscr.refresh()
            stdscr.getch()
            break

        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_LEFT:
            move_dog('left')
        elif key == curses.KEY_RIGHT:
            move_dog('right')
        elif key == ord(' '):
            shoot_laser()

        move_lasers()
        move_cats()
        check_collisions()
        check_cat_reached_dog()

        # Spawn new cats periodically
        frame_count += 1
        if frame_count >= SPAWN_INTERVAL:
            spawn_cat()
            frame_count = 0

        curses.napms(100)  # 100ms delay for game speed

if __name__ == "__main__":
    curses.wrapper(game_loop)
