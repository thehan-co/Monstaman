#!/usr/bin/env python3
import random
import curses
import time

# Game dimensions (internal playable area)
WIDTH = 50
HEIGHT = 20

# Game state
score = 0
lives = 5
cats_killed = 0
CATS_TO_WIN = 50
game_start_time = 0

# Dog position (center of playable area)
dog_x = WIDTH // 2
dog_y = HEIGHT // 2

# Cats list
cats = []

# Lasers list
lasers = []

# Frame counter for spawning
frame_count = 0
SPAWN_INTERVAL = 15  # Spawn new cat every 15 frames

# Cat movement speed
cat_move_counter = 0
CAT_MOVE_INTERVAL = 6

MAX_CATS = 7

# Last direction pressed (for shooting)
last_direction = 'up'

# Room decorations (fixed positions) - furniture the player can't walk through
FURNITURE = []

# ASCII Art for the dog (multi-char representation stored as offsets)
DOG_CHARS = {
    'up':    ['▲', '╬'],
    'down':  ['╬', '▼'],
    'left':  ['◄═', '╬ '],
    'right': ['═►', ' ╬'],
}

def get_elapsed_time():
    elapsed = int(time.time() - game_start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    return f"{minutes:02d}:{seconds:02d}"

def init_cats():
    global cats
    cats = []
    for _ in range(2):
        spawn_cat()

def init_furniture():
    global FURNITURE
    FURNITURE = [
        # Couch at bottom
        {'x': 5, 'y': HEIGHT - 3, 'char': '[▀▀▀▀▀▀▀]'},
        # Lamp in corner
        {'x': WIDTH - 6, 'y': HEIGHT - 4, 'char': ' () '},
        {'x': WIDTH - 6, 'y': HEIGHT - 3, 'char': ' || '},
        {'x': WIDTH - 6, 'y': HEIGHT - 2, 'char': '===='},
        # Table
        {'x': 3, 'y': 5, 'char': '┌───┐'},
        {'x': 3, 'y': 6, 'char': '│   │'},
        {'x': 3, 'y': 7, 'char': '└───┘'},
    ]

def draw_canvas(stdscr):
    stdscr.clear()

    # Create the game buffer
    buffer = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Draw furniture into buffer (background)
    for furn in FURNITURE:
        fx, fy = furn['x'], furn['y']
        for i, ch in enumerate(furn['char']):
            if 0 <= fx + i < WIDTH and 0 <= fy < HEIGHT:
                buffer[fy][fx + i] = ch

    # Draw lasers
    for laser in lasers:
        lx, ly = laser['x'], laser['y']
        if 0 <= lx < WIDTH and 0 <= ly < HEIGHT:
            buffer[ly][lx] = laser['symbol']

    # Draw cats
    for cat in cats:
        cx, cy = cat['x'], cat['y']
        if 0 <= cx < WIDTH and 0 <= cy < HEIGHT:
            if cat['sleeping']:
                buffer[cy][cx] = 'ᵶ'
            elif cat['hunter']:
                buffer[cy][cx] = '☠'
            else:
                buffer[cy][cx] = cat['symbol']

    # Draw dog
    if 0 <= dog_x < WIDTH and 0 <= dog_y < HEIGHT:
        buffer[dog_y][dog_x] = '@'

    # === DRAW THE FRAME ===

    # Title bar
    title = "══════════════════╡ M O N S T A M A N ╞══════════════════"
    stdscr.addstr(0, 0, "╔" + title[:WIDTH] + "╗")

    # Score and timer line
    score_str = f" Score: {score:04d} "
    lives_str = f" Lives: {'♥' * lives}{'♡' * (5 - lives)} "
    timer_str = f" Time: {get_elapsed_time()} "
    kills_str = f" Kills: {cats_killed}/{CATS_TO_WIN} "

    header = f"║{score_str}{lives_str}"
    padding = WIDTH - len(score_str) - len(lives_str) - len(timer_str) - len(kills_str)
    header += " " * padding + kills_str + timer_str + "║"
    stdscr.addstr(1, 0, header[:WIDTH + 2])

    # Top wall with windows
    window = "┌──╔══╗──┐"
    top_wall = "╠" + "═" * 5 + window + "═" * (WIDTH - 20) + window + "═" * 5 + "╣"
    stdscr.addstr(2, 0, top_wall[:WIDTH + 2])

    # Window details row
    window_detail = "│▒▒║  ║▒▒│"
    detail_row = "║" + "░" * 5 + window_detail + "░" * (WIDTH - 20) + window_detail + "░" * 5 + "║"
    stdscr.addstr(3, 0, detail_row[:WIDTH + 2])

    # Window bottom
    window_bottom = "└──╚══╝──┘"
    bottom_row = "║" + " " * 5 + window_bottom + " " * (WIDTH - 20) + window_bottom + " " * 5 + "║"
    stdscr.addstr(4, 0, bottom_row[:WIDTH + 2])

    # Main play area
    for y in range(HEIGHT):
        row_content = "".join(buffer[y])

        # Add door on right side at certain rows
        if 8 <= y <= 12:
            if y == 8:
                right_wall = "╔═╗"
            elif y == 12:
                right_wall = "╚═╝"
            elif y == 10:
                right_wall = "║●║"  # Door knob
            else:
                right_wall = "║ ║"
            stdscr.addstr(y + 5, 0, "║" + row_content + right_wall)
        else:
            stdscr.addstr(y + 5, 0, "║" + row_content + "║")

    # Floor with rug pattern
    rug_pattern = "░▓" * (WIDTH // 2)
    stdscr.addstr(HEIGHT + 5, 0, "╠" + rug_pattern[:WIDTH] + "╣")

    # Bottom decorative border
    stdscr.addstr(HEIGHT + 6, 0, "╚" + "═" * WIDTH + "╝")

    # Control hints
    hint = "  [←↑↓→] Move   [SPACE] Shoot   [Q] Quit  "
    stdscr.addstr(HEIGHT + 7, 0, hint)

    # Legend
    legend = "  @ = You   ☠ = Hunter   ᵶ = Sleeping   ^v<> = Cats"
    stdscr.addstr(HEIGHT + 8, 0, legend)

    stdscr.refresh()

def draw_game_over(stdscr, won):
    # Draw status board overlay
    box_width = 36
    box_height = 12
    start_x = (WIDTH - box_width) // 2
    start_y = (HEIGHT - box_height) // 2 + 3

    # Box border
    stdscr.addstr(start_y, start_x, "╔" + "═" * (box_width - 2) + "╗")
    for i in range(1, box_height - 1):
        stdscr.addstr(start_y + i, start_x, "║" + " " * (box_width - 2) + "║")
    stdscr.addstr(start_y + box_height - 1, start_x, "╚" + "═" * (box_width - 2) + "╝")

    if won:
        # Win message
        stdscr.addstr(start_y + 1, start_x + 2, "    ★ ★ ★  YOU WIN!  ★ ★ ★    ")
        stdscr.addstr(start_y + 2, start_x + 2, "                                ")
        stdscr.addstr(start_y + 3, start_x + 2, "      \\(^◡^)/  WOOF WOOF!       ")
        stdscr.addstr(start_y + 4, start_x + 2, "       /|  |\\                   ")
    else:
        # Lose message
        stdscr.addstr(start_y + 1, start_x + 2, "      ✗ ✗  GAME OVER  ✗ ✗      ")
        stdscr.addstr(start_y + 2, start_x + 2, "                                ")
        stdscr.addstr(start_y + 3, start_x + 2, "        (×_×)  *meow*           ")
        stdscr.addstr(start_y + 4, start_x + 2, "       The cats got you!        ")

    stdscr.addstr(start_y + 5, start_x + 2, "────────────────────────────────")
    stdscr.addstr(start_y + 6, start_x + 2, f"  Final Score:  {score:04d}            ")
    stdscr.addstr(start_y + 7, start_x + 2, f"  Cats Killed:  {cats_killed}               ")
    stdscr.addstr(start_y + 8, start_x + 2, f"  Time:         {get_elapsed_time()}             ")
    stdscr.addstr(start_y + 9, start_x + 2, "────────────────────────────────")
    stdscr.addstr(start_y + 10, start_x + 2, "     Press any key to exit      ")

    stdscr.refresh()

def move_dog(direction):
    global dog_x, dog_y
    new_x, new_y = dog_x, dog_y

    if direction == 'left' and dog_x > 1:
        new_x -= 1
    elif direction == 'right' and dog_x < WIDTH - 2:
        new_x += 1
    elif direction == 'up' and dog_y > 1:
        new_y -= 1
    elif direction == 'down' and dog_y < HEIGHT - 2:
        new_y += 1

    # Check furniture collision (simplified - just don't walk into first char of furniture)
    can_move = True
    for furn in FURNITURE:
        fx, fy = furn['x'], furn['y']
        flen = len(furn['char'])
        if fy == new_y and fx <= new_x < fx + flen:
            can_move = False
            break

    if can_move:
        dog_x, dog_y = new_x, new_y

def shoot_laser():
    if last_direction == 'up':
        lasers.append({'x': dog_x, 'y': dog_y - 1, 'dx': 0, 'dy': -1, 'symbol': '║'})
    elif last_direction == 'down':
        lasers.append({'x': dog_x, 'y': dog_y + 1, 'dx': 0, 'dy': 1, 'symbol': '║'})
    elif last_direction == 'left':
        lasers.append({'x': dog_x - 1, 'y': dog_y, 'dx': -1, 'dy': 0, 'symbol': '═'})
    elif last_direction == 'right':
        lasers.append({'x': dog_x + 1, 'y': dog_y, 'dx': 1, 'dy': 0, 'symbol': '═'})

def move_lasers():
    global lasers
    for laser in lasers:
        laser['x'] += laser['dx']
        laser['y'] += laser['dy']
    lasers = [laser for laser in lasers if 0 <= laser['x'] < WIDTH and 0 <= laser['y'] < HEIGHT]

def move_cats():
    global cats
    for cat in cats:
        if cat['sleeping']:
            if random.random() < 0.1:
                cat['sleeping'] = False
            continue

        if random.random() < 0.05:
            cat['sleeping'] = True
            continue

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

    cats = [cat for cat in cats if cat['hunter'] or (0 <= cat['x'] < WIDTH and 0 <= cat['y'] < HEIGHT)]
    for cat in cats:
        if cat['hunter']:
            cat['x'] = max(0, min(WIDTH - 1, cat['x']))
            cat['y'] = max(0, min(HEIGHT - 1, cat['y']))

def spawn_cat():
    if len(cats) >= MAX_CATS:
        return

    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(1, WIDTH - 2)
        y = 0
        dx, dy = 0, 1
        symbol = '▼'
    elif side == 'bottom':
        x = random.randint(1, WIDTH - 2)
        y = HEIGHT - 1
        dx, dy = 0, -1
        symbol = '▲'
    elif side == 'left':
        x = 0
        y = random.randint(1, HEIGHT - 2)
        dx, dy = 1, 0
        symbol = '►'
    else:
        x = WIDTH - 1
        y = random.randint(1, HEIGHT - 2)
        dx, dy = -1, 0
        symbol = '◄'

    is_hunter = random.random() < 0.3
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
    global lasers, cats, score, cats_killed
    lasers_to_remove = []
    cats_to_remove = []

    for laser in lasers:
        for cat in cats:
            if laser['x'] == cat['x'] and laser['y'] == cat['y']:
                lasers_to_remove.append(laser)
                cats_to_remove.append(cat)
                score += 10
                cats_killed += 1

    for laser in lasers_to_remove:
        if laser in lasers:
            lasers.remove(laser)
    for cat in cats_to_remove:
        if cat in cats:
            cats.remove(cat)

def game_loop(stdscr):
    global frame_count, cat_move_counter, lives, last_direction, game_start_time

    curses.curs_set(0)
    stdscr.keypad(True)
    stdscr.nodelay(True)

    game_start_time = time.time()
    init_furniture()
    init_cats()

    while True:
        draw_canvas(stdscr)

        # Check win condition
        if cats_killed >= CATS_TO_WIN:
            stdscr.nodelay(False)
            draw_game_over(stdscr, won=True)
            stdscr.getch()
            break

        # Check lose condition
        if lives <= 0:
            stdscr.nodelay(False)
            draw_game_over(stdscr, won=False)
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

        cat_move_counter += 1
        if cat_move_counter >= CAT_MOVE_INTERVAL:
            move_cats()
            cat_move_counter = 0

        check_collisions()
        check_cat_reached_dog()

        frame_count += 1
        if frame_count >= SPAWN_INTERVAL:
            spawn_cat()
            frame_count = 0

        curses.napms(80)

if __name__ == "__main__":
    curses.wrapper(game_loop)
