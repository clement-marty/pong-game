# Pong Game

![Pong Menu Screenshot](/media/menu_screenshot.png)
![Pong Game Screenshot](/media/game_screenshot.png)

Welcome to the Pong Game! This is a classic arcade game where two players control paddles to hit a ball back and forth. The objective is to score points by getting the ball past the opponent's paddle.

## Modes

- **Player vs Player**: Play against your friends on the same keyboard
- **Player vs Bot**: Play against a bot

## Bonuses
Each bonus spawn at a random location and can be activated by the ball.

- **Speed Boost (yellow)**: Fires the ball at a high speed directly towards your opponent
- **Teleportation (blue)**: Teleports the ball at a random location, keeping the same orientation.
- **Multi-Ball (red)**: Duplicates the ball that touched the bonus.


## Installation

To install and run the Pong Game, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/clement-marty/pong-game.git
    cd pong-game
    ```

2. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the game**:
    ```bash
    python main.py
    ```