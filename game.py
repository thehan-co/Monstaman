#!/usr/bin/env python3

# Game dimensions (internal playable area)
WIDTH = 30
HEIGHT = 30

# Game state
score = 0
lives = 5

# Dog position (center bottom of playable area)
dog_x = WIDTH // 2
dog_y = HEIGHT - 1

def draw_canvas():
    # Top wall
    print("+" + "-" * WIDTH + "+")

    # Playable area with side walls
    for y in range(HEIGHT):
        print("|", end="")
        for x in range(WIDTH):
            if x == dog_x and y == dog_y:
                print("@", end="")
            else:
                print(" ", end="")
        print("|")

    # Bottom wall
    print("+" + "-" * WIDTH + "+")

    # Status line
    print(f"Score: {score} | Lives: {lives}")

if __name__ == "__main__":
    draw_canvas()
