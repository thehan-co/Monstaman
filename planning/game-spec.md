# Monstaman Game Specification

## Concept
A dog with a laser gun defends his living room from invading colorful cats.

## Gameplay
- Dog is in the center of the living room
- Cats enter from top and sides, through windows and the door.
- Player moves dog left/right and up/down with arrow keys
- Player shoots with spacebar
- Each cat killed = 10 points
- Game ends when 5 cats escape (reach the dog/back wall)
- In time, the pace of entering cats grows steadily and subtly.

## Scoring
- Score location: upper left side
- Score: number of cats killed × 10
- Lives: 5 (you lose when cats reach you or wall)
- Display on screen: "Score: 120 | Lives: 3" 

## Stopwatch
- Stopwatch location: top right
- Stope watch counts minutes and seconds of play from game start
- Format is 00:00

## Win/Lose
- Win condition: Survive and kill 50 cats
- Lose condition: 5 cats reach you

##Game Over Status Board
- When game ends (win or lose), a status board pops up on top of the game with a winning/losing message and icon, socring and time. 

## ASCII Style
- Dog: @ (with gun below: ===>)
- Cats: ^ and v (different directions)
- Laser: | (moving up)
- Living room: | walls, - ceiling/floor