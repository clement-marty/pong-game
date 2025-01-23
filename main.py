import pygame
import configparser

from scripts.game import Game, Bot
from scripts.renderer import Renderer


def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def main() -> None:

    config = load_config()
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((config.getint('screen', 'width'), config.getint('screen', 'height')), pygame.FULLSCREEN if config.getboolean('screen', 'fullscreen') else 0)
    pygame.display.set_caption('PONG')
    title_font = pygame.font.Font(config.get('assets', 'font'), 100)
    font = pygame.font.Font(config.get('assets', 'font'), 50)
    little_font = pygame.font.Font(config.get('assets', 'font'), 30)
    menu_interaction_sound = pygame.mixer.Sound(config.get('assets', 'menu_interaction_sound'))
    points_to_win = config.getint('game', 'points_to_win')

    game: Game = None
    bot: Bot = None
    renderer = Renderer(screen, config)

    clock = pygame.time.Clock()
    fps = config.getint('screen', 'framerate')
    running = True
    game_running = False
    play_with_bot = False
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    menu_interaction_sound.play()
                    if game_running:
                        game_running = False
                    else:
                        running = False

                if event.key == pygame.K_RETURN and not game_running:
                    game = Game(config, screen.get_size())
                    if play_with_bot:
                        bot = Bot(game, game.paddles.right)
                    game_running = True

                if event.key == pygame.K_SPACE and not game_running:
                    play_with_bot = not play_with_bot
                    menu_interaction_sound.play()
              

        if game_running:

            # Process player inputs
            keys = pygame.key.get_pressed()
            if keys[pygame.K_z]:
                game.paddles.left.move(-1, dt=1/fps)
            if keys[pygame.K_s]:
                game.paddles.left.move(1, dt=1/fps)
            if keys[pygame.K_o]:
                game.paddles.right.move(-1, dt=1/fps)
            if keys[pygame.K_l]:
                game.paddles.right.move(1, dt=1/fps)

            if play_with_bot:
                bot.update(dt=1/fps)
            game.update(dt=1/fps)

            renderer.render_game(game.balls, game.paddles.left.position, game.paddles.right.position)
            renderer.render_bonuses(game.bonuses)
            renderer.render_score(font, *game.score)

            if game.score[0] == points_to_win or game.score[1] == points_to_win:
                game_running = False
        
        else:
            if game:
                renderer.render_menu(
                    title_font, font, little_font, play_with_bot,
                    winner='left' if game.score[0] == points_to_win else 'right' if game.score[1] == points_to_win else None
                )
            else:
                renderer.render_menu(title_font, font, little_font, play_with_bot)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()



if __name__ == '__main__':
    main()