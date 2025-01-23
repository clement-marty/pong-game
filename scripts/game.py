import math
import pygame
import random
import configparser

from scripts.sounds import Sounds



class Game:

    def __init__(self, config: configparser.ConfigParser, screen_size: tuple[int, int], sounds: Sounds) -> None:
        self.screen_width, self.screen_height = screen_size
        self.sounds = sounds
        self.ball_radius = config.getint('ball', 'radius')
        self.inital_ball_speed = config.getint('ball', 'initial_speed')
        self.ball_acceleration = config.getint('ball', 'acceleration')

        self.paddles = Paddles(
            speed=config.getint('paddle', 'speed'),
            padding=config.getint('paddle', 'padding'),
            paddle_size=(config.getint('paddle', 'width'), config.getint('paddle', 'height')),
            screen_size=screen_size,
            game=self
        )

        self.balls = [Ball(
            position=(self.screen_width // 2, self.screen_height // 2),
            radius=config.getint('ball', 'radius'),
            speed=config.getint('ball', 'initial_speed'),
            direction=self.random_ball_direction()
        )]

        self.bonuses = Bonuses(
            game=self,
            max_amount=config.getint('bonus', 'maximum_amount'),
            cooldown=config.getint('bonus', 'spawn_cooldown'),
            radius=config.getint('bonus', 'radius'),
            hitbox_radius=config.getint('bonus', 'hitbox_radius'),
            yellow_bonus_speed=config.getint('bonus', 'yellow_bonus_speed')
        )

        self.score = [0, 0]


    def random_ball_direction(self) -> tuple[int, int]:
        angle = random.random() * math.pi/2 - math.pi/4
        side = random.choice([-1, 1])
        return (side * math.cos(angle), math.sin(angle))
    
    def random_position(self) -> tuple[int, int]:
        x = random.random() * (self.screen_width - 8*self.paddles.padding) + 4*self.paddles.padding
        y = random.random() * (self.screen_height - 4*self.paddles.padding) + 2*self.paddles.padding
        return x, y

    
    def check_collision(self, ball: 'Ball') -> None:

        # Collision with the paddles
        for paddle in [self.paddles.left, self.paddles.right]:
            paddle.check_collision(ball)

        # Collision with the top and bottom walls
        if ball.y - ball.radius < 0 or ball.y + ball.radius > self.screen_height:
            ball.direction = [ball.direction[0], -ball.direction[1]]
            self.sounds.wall_collision.play()

        # Collision with the bonuses
        self.bonuses.check_collision(ball)


    def check_goal(self, ball: 'Ball') -> str:
        return 'left' if (ball.x) < 0 \
            else 'right' if (ball.x) > self.screen_width \
            else None
    
    
    def update(self, dt: float) -> None:
        for ball in self.balls:
            ball.move(dt)
            ball.speed += self.ball_acceleration * dt

            self.check_collision(ball)
            winner = self.check_goal(ball)
            if winner:
                self.score[1 if winner == 'left' else 0] += 1
                self.sounds.goal.play()

                if len(self.balls) == 1:
                    ball.position = [self.screen_width // 2, self.screen_height // 2]
                    ball.direction = self.random_ball_direction()
                    ball.speed = self.inital_ball_speed
                    ball.previous_speed = None
                    ball.radius = self.ball_radius
                else:
                    self.balls.remove(ball)

                if len(self.balls) == 1:
                    self.balls[0].radius = self.ball_radius     
        
        self.bonuses.update(dt)


  
class Bot:

    THRESHOLD = 20

    def __init__(self, game: Game, paddle: 'Paddles.Paddle') -> None:
        self.game = game
        self.paddle = paddle

    def update(self, dt: float) -> None:
        closest_ball = min(self.game.balls, key=lambda ball: abs(ball.x - self.paddle.x))
        dy = closest_ball.y - self.paddle.y
        if abs(dy) > self.THRESHOLD:
            self.paddle.move(1 if dy > 0 else -1, dt)



class Ball:

    def __init__(self, position: tuple[int, int], radius: int, speed: int, direction: tuple[int, int]) -> None:
        self.position = list(position)
        self.radius = radius
        self.speed = speed
        self.previous_speed: int = None
        self.direction = direction

    def move(self, dt: float) -> None:
        self.position[0] += self.speed * self.direction[0] * dt
        self.position[1] += self.speed * self.direction[1] * dt

    @property
    def x(self) -> int:
        return self.position[0]
    
    @property
    def y(self) -> int:
        return self.position[1]


class Paddles:

    def __init__(self, speed: int, padding: int, paddle_size: tuple[int, int], screen_size: tuple[int, int], game) -> None:
        self.speed = speed
        self.padding = padding
        self.w, self.h = paddle_size
        self.screen_width, self.screen_height = screen_size

        self.left = self.Paddle('left', self.padding, self.screen_height // 2, self.w, self.h, self.screen_height, self.speed, game)
        self.right = self.Paddle('right', self.screen_width - self.padding, self.screen_height // 2, self.w, self.h, self.screen_height, self.speed, game)

    class Paddle:
        def __init__(self, paddle, x, y, w, h, max_y, speed, game) -> None:
            self.paddle = paddle
            self.x, self.y = x, y
            self.w, self.h = w, h
            self.max_y = max_y
            self.speed = speed
            self.game = game

        @property
        def position(self) -> tuple[int, int]: return self.x, self.y
        
        def __eq__(self, value): return value == self.paddle

        def check_collision(self, ball: Ball) -> bool:
            if ball.x - ball.radius <= self.x + self.w//2 and ball.x + ball.radius >= self.x - self.w//2 \
                and ball.y + ball.radius > self.y - self.h//2 and ball.y - ball.radius < self.y + self.h//2:

                self.game.sounds.paddle_collision.play()
                direction_angle = (math.pi/4) * (ball.y - self.y) / (self.h//2)
                ball.direction = (math.cos(direction_angle) * (-1 if self == 'right' else 1), math.sin(direction_angle))

                if ball.previous_speed:
                    ball.speed = ball.previous_speed
                    ball.previous_speed = None
        
        def move(self, direction: int, dt: float) -> None:
            self.y += self.speed * direction * dt
            self.y = max(self.h//2, min(self.max_y - self.h//2, self.y))


class Bonuses:

    def __init__(self, game: Game, max_amount, cooldown, radius, hitbox_radius, yellow_bonus_speed) -> None:
        self.game = game
        self.max = max_amount
        self.cooldown = cooldown
        self.radius = radius
        self.hitbox_radius = hitbox_radius

        self.blue = self.BlueBonus()
        self.yellow = self.YellowBonus(yellow_bonus_speed)
        self.red = self.RedBonus()
        self.bonus_types = [self.yellow, self.blue, self.red]

        self.eta = self.cooldown
        self.list: list[tuple[str, int, int]] = []

    def update(self, dt: float) -> None:
        self.eta = max(0, self.eta - dt)
        if self.eta == 0:
            self.eta = self.cooldown

            if len(self.list) < self.max:

                weights = []
                for bonus in self.bonus_types:
                    weights.append(bonus.weight)

                n = random.random() * sum(weights)
                i = -1
                while n > 0:
                    n -= weights[i+1]
                    i += 1

                self.list.append((self.bonus_types[i].color, *self.game.random_position()))

    def check_collision(self, ball: Ball) -> None:
        for bonus, x, y in self.list:
            if (ball.x - x)**2 + (ball.y - y)**2 < (ball.radius + self.hitbox_radius)**2:
                self.list.remove((bonus, x, y))

                for bonus_type in self.bonus_types:
                    if bonus == bonus_type:
                        bonus_type.interact(ball, self.game)
                        break


    class BonusType:
        def __init__(self, color: str, weight): self.color,self.weight = color, weight
        def __eq__(self, value): return value == self.color
        def interact(self, ball: Ball, game: Game): raise NotImplementedError

    class YellowBonus(BonusType):

        def __init__(self, speed: int):
            super().__init__('yellow', 2)
            self.speed = speed

        def interact(self, ball: Ball, game: Game) -> None:
            ball.previous_speed = ball.speed
            ball.speed = self.speed
            ball.direction = (ball.direction[0]/abs(ball.direction[0]), 1e-4)
            game.sounds.yellow_bonus.play()


    class BlueBonus(BonusType):

        def __init__(self):
            super().__init__('blue', 1)
        
        def interact(self, ball: Ball, game: Game) -> None:
            ball.position = list(game.random_position())
            game.sounds.blue_bonus.play()


    class RedBonus(BonusType):

        def __init__(self):
            super().__init__('red', 1)

        def interact(self, ball: Ball, game: Game) -> None:
            game.balls.append(Ball(
                position=ball.position,
                radius=game.ball_radius*2//3,
                speed=ball.speed,
                direction=(-ball.direction[0], ball.direction[1])
            ))
            ball.radius = game.ball_radius*2//3
            game.sounds.red_bonus.play()