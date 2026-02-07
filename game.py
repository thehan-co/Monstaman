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

# Cat movement speed (move every N frames)
cat_move_counter = 0
CAT_MOVE_INTERVAL = 8  # Cats move every 8 frames (much slower)

MAX_CATS = 5  # Maximum cats on screen

# Last direction pressed (for shooting)
last_direction = 'up'  # default shoot upward

def init_cats():
    global cats
    cats = []
    for _ in range(3):
        spawn_cat()

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
                laser = next(l for l in lasers if l['x'] == x and l['y'] == y)
                row += laser['symbol']
            # Check for cats
            elif any(cat['x'] == x and cat['y'] == y for cat in cats):
                cat = next(c for c in cats if c['x'] == x and c['y'] == y)
                if cat['sleeping']:
                    row += 'z'  # Sleeping cat
                elif cat['hunter']:
                    row += '*'  # Hunter cat
                else:
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
    global dog_x, dog_y
    if direction == 'left' and dog_x > 0:
        dog_x -= 1
    elif direction == 'right' and dog_x < WIDTH - 1:
        dog_x += 1
    elif direction == 'up' and dog_y > 0:
        dog_y -= 1
    elif direction == 'down' and dog_y < HEIGHT - 1:
        dog_y += 1

def shoot_laser():
    if last_direction == 'up':
        lasers.append({'x': dog_x, 'y': dog_y - 1, 'dx': 0, 'dy': -1, 'symbol': '|'})
    elif last_direction == 'down':
        lasers.append({'x': dog_x, 'y': dog_y + 1, 'dx': 0, 'dy': 1, 'symbol': '|'})
    elif last_direction == 'left':
        lasers.append({'x': dog_x - 1, 'y': dog_y, 'dx': -1, 'dy': 0, 'symbol': '-'})
    elif last_direction == 'right':
        lasers.append({'x': dog_x + 1, 'y': dog_y, 'dx': 1, 'dy': 0, 'symbol': '-'})

def move_lasers():
    global lasers
    for laser in lasers:
        laser['x'] += laser['dx']
        laser['y'] += laser['dy']
    # Remove lasers that went off screen
    lasers = [laser for laser in lasers if 0 <= laser['x'] < WIDTH and 0 <= laser['y'] < HEIGHT]

def move_cats():
    global cats
    for cat in cats:
        # Sleeping cats might wake up (10% chance each move)
        if cat['sleeping']:
            if random.random() < 0.1:
                cat['sleeping'] = False
            continue  # Skip movement if sleeping

        # Awake cats might fall asleep (5% chance)
        if random.random() < 0.05:
            cat['sleeping'] = True
            continue

        # Hunter cats move toward dog
        if cat['hunter']:
            if dog_x > cat['x']:
                cat['dx'] = 1
            elif dog_x < cat['x']:
                cat['dx'] = -1
            else:
                cat['dx'] = 0

            if dog_y > cat['y']:
                cat['dy'] = 1
            elif dog_y < cat['y']:
                cat['dy'] = -1
            else:
                cat['dy'] = 0

        cat['x'] += cat['dx']
        cat['y'] += cat['dy']

    # Remove cats that went off screen (only non-hunters)
    cats = [cat for cat in cats if cat['hunter'] or (0 <= cat['x'] < WIDTH and 0 <= cat['y'] < HEIGHT)]
    # Keep hunters in bounds
    for cat in cats:
        if cat['hunter']:
            cat['x'] = max(0, min(WIDTH - 1, cat['x']))
            cat['y'] = max(0, min(HEIGHT - 1, cat['y']))

def spawn_cat():
    if len(cats) >= MAX_CATS:
        return  # Don't spawn if at max

    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, WIDTH - 1)
        y = 0
        dx, dy = 0, 1
        symbol = 'v'
    elif side == 'bottom':
        x = random.randint(0, WIDTH - 1)
        y = HEIGHT - 1
        dx, dy = 0, -1
        symbol = '^'
    elif side == 'left':
        x = 0
        y = random.randint(0, HEIGHT - 1)
        dx, dy = 1, 0
        symbol = '>'
    else:  # right
        x = WIDTH - 1
        y = random.randint(0, HEIGHT - 1)
        dx, dy = -1, 0
        symbol = '<'

    # 30% chance to be a hunter (attracted to dog)
    is_hunter = random.random() < 0.3
    # 20% chance to be sleeping
    is_sleeping = random.random() < 0.2

    cats.append({
        'x': x, 'y': y, 'dx': dx, 'dy': dy, 'symbol': symbol,
        'hunter': is_hunter, 'sleeping': is_sleeping
    })

def check_cat_reached_dog():
    global cats, lives
    cats_to_remove = []
    for cat in cats:
        if cat['x'] == dog_x and cat['y'] == dog_y:
            cats_to_remove.append(cat)
            lives -= 1
    for cat in cats_to_remove:
        if cat in cats:
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
    global frame_count, cat_move_counter, lives, last_direction

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
            last_direction = 'left'
        elif key == curses.KEY_RIGHT:
            move_dog('right')
            last_direction = 'right'
        elif key == curses.KEY_UP:
            move_dog('up')
            last_direction = 'up'
        elif key == curses.KEY_DOWN:
            move_dog('down')
            last_direction = 'down'
        elif key == ord(' '):
            shoot_laser()

        move_lasers()

        # Move cats slower
        cat_move_counter += 1
        if cat_move_counter >= CAT_MOVE_INTERVAL:
            move_cats()
            cat_move_counter = 0

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
