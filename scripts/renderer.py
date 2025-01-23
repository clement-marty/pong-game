import time
import pygame
import configparser

from scripts.game import Ball, Bonuses


class Renderer:

    def __init__(self, screen: pygame.Surface, config: configparser.ConfigParser) -> None:
        self.screen = screen
        self.config = config
    

    def render_game(self, balls: list[Ball], left_paddle_pos: tuple[int, int], right_paddle_pos: tuple[int, int]) -> None:
        self.screen.fill('#000000')

        for ball in balls:
            pygame.draw.circle(self.screen, '#ffffff', ball.position, ball.radius)
        
        pw = self.config.getint('paddle', 'width')
        ph = self.config.getint('paddle', 'height')

        for x, y in [left_paddle_pos, right_paddle_pos]:
            pygame.draw.rect(self.screen, '#ffffff', pygame.Rect(x - pw//2, y - ph//2, pw, ph))


    def render_bonuses(self, bonuses: Bonuses) -> None:
        for bonus, x, y in bonuses.list:
            color = ''
            if bonus == 'yellow': color = '#ffff80'
            if bonus == 'blue': color = '#8080ff'
            if bonus == 'red': color = '#ff8080'
            pygame.draw.circle(self.screen, color, (x, y), bonuses.radius)


    
    def render_score(self, font: pygame.font.Font, left_score: int, right_score: int) -> None:
        delimiter = font.render(':', 1, '#ffffff')
        left_text = font.render(str(left_score), 1, '#ffffff')
        right_text = font.render(str(right_score), 1, '#ffffff')

        w, h = self.screen.get_size()
        dw, dh = delimiter.get_size()
        lw, lh = left_text.get_size()
        rw, rh = right_text.get_size()

        self.screen.blit(delimiter, (w//2 - dw//2, dh//2))
        self.screen.blit(left_text, (w//2 - lw - dw, lh//2))
        self.screen.blit(right_text, (w//2 + rw - dw, rh//2))


    def render_menu(self, title_font: pygame.font.Font, text_font: pygame.font.Font, little_font: pygame.font.Font, play_with_bot: bool, winner: str = None) -> None:
        title = title_font.render('PONG', 1, '#ffffff')
        t1 = text_font.render('press [enter] to start', 1, '#ffffff')
        t2 = little_font.render(f'<player vs {'bot' if play_with_bot else 'player'} mode> press [space] to change mode', 1, '#ffffff')
        t3 = little_font.render('<player 1> press [z] and [s] to move the left paddle', 1, '#ffffff')
        t4 = little_font.render('<player 2> press [o] and [l] to move the right paddle', 1, '#ffffff')
        t5 = little_font.render('press [esc] to quit', 1, '#ffffff')
        

        w, h = self.screen.get_size()
        wt, ht = title.get_size()
        w1, h1 = t1.get_size()
        w2, h2 = t2.get_size()
        _, h3 = t3.get_size()
        _, h4 = t4.get_size()
        _, h5 = t5.get_size()

        self.screen.fill('#000000')
        self.screen.blit(title, (w//2 - wt//2, h//4 - ht//2))
        if time.time() % 1 < .5:
            self.screen.blit(t1, (w//2 - w1//2, h//2 - h1//2))
        self.screen.blit(t2, (w//2 - w2//2, h//2 + h1 - h2//2))
        self.screen.blit(t3, (h3//2, h - h3 - h4))
        if not play_with_bot:
            self.screen.blit(t4, (h4//2, h - h4))
        self.screen.blit(t5, (h5//2, h5//2))

        if winner and time.time() % 1 < .5:
            player = 'player 1' if winner == 'left' else 'player 2' if not play_with_bot else 'bot'
            color = '#ff8080' if winner == 'right' and play_with_bot else '#80ff80'
            t6 = text_font.render(f'<{player}> won', 1, color)
            w6, h6 = t6.get_size()
            self.screen.blit(t6, (w//2 - w6//2, 3*h//4 - ht//2))