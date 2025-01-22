import math
import pygame
import random
import configparser


class Game:

    def __init__(self, config: configparser.ConfigParser, screen_size: tuple[int, int]) -> None:
        self.screen_width, self.screen_height = screen_size
        self.ball_radius = config.getint('ball', 'radius')
        self.inital_ball_speed = config.getint('ball', 'initial_speed')
        self.paddle_speed = config.getint('paddle', 'speed')
        self.paddle_padding = config.getint('paddle', 'padding')
        self.paddle_height = config.getint('paddle', 'height')
        self.paddle_width = config.getint('paddle', 'width')

        self.ball_acceleration = config.getint('ball', 'acceleration')
        self.left_paddle_pos = [self.paddle_padding, self.screen_height // 2]
        self.right_paddle_pos = [self.screen_width - self.paddle_padding, self.screen_height // 2]

        self.balls = [Ball(
            position=(self.screen_width // 2, self.screen_height // 2),
            radius=config.getint('ball', 'radius'),
            speed=config.getint('ball', 'initial_speed'),
            direction=self.random_ball_direction()
        )]

        self.score = [0, 0]

        self.max_bonuses = config.getint('bonus', 'maximum_amount')
        self.bonus_cooldown = config.getint('bonus', 'spawn_cooldown')
        self.bonus_hitbox_radius = config.getint('bonus', 'hitbox_radius')
        self.bonus_eta = self.bonus_cooldown
        self.bonus_types = ['yellow', 'blue', 'red']
        self.bonus_weights = [.5, .25, .25]
        self.bonuses: list[tuple[str, int, int]] = []

        self.yellow_bonus_speed = config.getint('bonus', 'yellow_bonus_speed')
        self.yellow_bonus_previous_speed: int = None

        self.wall_collision_sound = pygame.mixer.Sound(config.get('assets', 'wall_collision_sound'))
        self.paddle_collision_sound = pygame.mixer.Sound(config.get('assets', 'paddle_collision_sound'))
        self.goal_sound = pygame.mixer.Sound(config.get('assets', 'goal_sound'))
        self.yellow_bonus_sound = pygame.mixer.Sound(config.get('assets', 'yellow_bonus_sound'))
        self.blue_bonus_sound = pygame.mixer.Sound(config.get('assets', 'blue_bonus_sound'))
        self.red_bonus_sound = pygame.mixer.Sound(config.get('assets', 'red_bonus_sound'))
        for sound in [self.wall_collision_sound, self.paddle_collision_sound, self.goal_sound, self.yellow_bonus_sound, self.blue_bonus_sound]:
            sound.set_volume(config.getfloat('screen', 'sound_volume'))


    def random_ball_direction(self) -> tuple[int, int]:
        angle = random.random() * math.pi/2 - math.pi/4
        side = random.choice([-1, 1])
        return (side * math.cos(angle), math.sin(angle))
    
    def random_position(self) -> tuple[int, int]:
        x = random.random() * (self.screen_width - 8*self.paddle_padding) + 4*self.paddle_padding
        y = random.random() * (self.screen_height - 4*self.paddle_padding) + 2*self.paddle_padding
        return x, y

    
    def check_collision(self, ball: 'Ball') -> None:
        # Collision with the paddles
        if ball.x - ball.radius <= self.paddle_padding + self.paddle_width//2:
            self.check_collision_with_paddle('left', ball)
        elif ball.x + ball.radius >= self.screen_width - self.paddle_padding - self.paddle_width//2:
            self.check_collision_with_paddle('right', ball)

        # Collision with the top and bottom walls
        if ball.y - ball.radius < 0 or ball.y + ball.radius > self.screen_height:
            ball.direction = [ball.direction[0], -ball.direction[1]]
            self.wall_collision_sound.play()

        # Collision with the bonuses
        for bonus, x, y in self.bonuses:
            if (ball.x - x)**2 + (ball.y - y)**2 < (ball.radius + self.bonus_hitbox_radius)**2:
                self.bonuses.remove((bonus, x, y))

                if bonus == 'yellow':
                    ball.previous_speed = ball.speed
                    ball.speed = self.yellow_bonus_speed
                    ball.direction = (ball.direction[0]/abs(ball.direction[0]), 1e-4)
                    self.yellow_bonus_sound.play()

                if bonus == 'blue':
                    ball.position = list(self.random_position())
                    self.blue_bonus_sound.play()

                if bonus == 'red':
                    self.balls.append(Ball(
                        position=ball.position,
                        radius=self.ball_radius*2//3,
                        speed=ball.speed,
                        direction=(-ball.direction[0], ball.direction[1])
                    ))
                    ball.radius = self.ball_radius*2//3
                    self.red_bonus_sound.play()


    def check_collision_with_paddle(self, paddle: str, ball: 'Ball') -> None:
        _, y = self.left_paddle_pos if paddle == 'left' else self.right_paddle_pos
        if ball.y + ball.radius > y - self.paddle_height//2 and ball.y - ball.radius < y + self.paddle_height//2:

            direction_angle = (math.pi/4) * (ball.y - y) / (self.paddle_height//2)
            ball.direction = (math.cos(direction_angle) * (-1 if paddle == 'right' else 1), math.sin(direction_angle))

            self.paddle_collision_sound.play()
            
            if ball.previous_speed:
                ball.speed = ball.previous_speed
                ball.previous_speed = None


    def check_goal(self, ball: 'Ball') -> str:
        return 'left' if (ball.x) < 0 \
            else 'right' if (ball.x) > self.screen_width \
            else None


    def move_paddle(self, paddle: str, direction: int, dt: float) -> None:
        if paddle == 'left':
            self.left_paddle_pos[1] += self.paddle_speed * direction * dt
            self.left_paddle_pos[1] = max(self.paddle_height//2, min(self.screen_height - self.paddle_height//2, self.left_paddle_pos[1]))
        else:
            self.right_paddle_pos[1] += self.paddle_speed * direction * dt
            self.right_paddle_pos[1] = max(self.paddle_height//2, min(self.screen_height - self.paddle_height//2, self.right_paddle_pos[1]))

    
    def update(self, dt: float) -> None:
        for ball in self.balls:
            ball.move(dt)
            ball.speed += self.ball_acceleration * dt

            self.check_collision(ball)
            winner = self.check_goal(ball)
            if winner:
                self.score[1 if winner == 'left' else 0] += 1
                self.goal_sound.play()

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
                
        
        self.update_bonuses(dt)


    def update_bonuses(self, dt: float) -> None:
        self.bonus_eta = max(0, self.bonus_eta - dt)
        if self.bonus_eta == 0:
            self.bonus_eta = self.bonus_cooldown

            if len(self.bonuses) < self.max_bonuses:

                n = random.random() * sum(self.bonus_weights)
                i = -1
                while n > 0:
                    n -= self.bonus_weights[i+1]
                    i += 1

                self.bonuses.append((self.bonus_types[i], *self.random_position()))


  
class Bot:

    THRESHOLD = 20

    def __init__(self, game: Game, paddle: str) -> None:
        self.game = game
        self.paddle = paddle
        self.paddle_pos = game.left_paddle_pos if self.paddle == 'left' else game.right_paddle_pos

    def update(self, dt: float) -> None:
        closest_ball = min(self.game.balls, key=lambda ball: abs(ball.x - self.paddle_pos[0]))
        dy = closest_ball.y - self.paddle_pos[1]
        if abs(dy) > self.THRESHOLD:
            self.game.move_paddle(self.paddle, 1 if dy > 0 else -1, dt)



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