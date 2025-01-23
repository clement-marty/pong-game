import pygame
import configparser


class Sounds:

    def __init__(self, config: configparser.ConfigParser) -> None:

        self.menu_interaction = pygame.mixer.Sound(config.get('assets', 'menu_interaction_sound'))
        self.wall_collision = pygame.mixer.Sound(config.get('assets', 'wall_collision_sound'))
        self.paddle_collision = pygame.mixer.Sound(config.get('assets', 'paddle_collision_sound'))
        self.goal = pygame.mixer.Sound(config.get('assets', 'goal_sound'))
        self.yellow_bonus = pygame.mixer.Sound(config.get('assets', 'yellow_bonus_sound'))
        self.blue_bonus = pygame.mixer.Sound(config.get('assets', 'blue_bonus_sound'))
        self.red_bonus = pygame.mixer.Sound(config.get('assets', 'red_bonus_sound'))

        volume = config.getfloat('screen', 'sound_volume')
        for sound in self.__dict__.values():
            sound.set_volume(volume)