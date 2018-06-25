import pygame
from pygame.constants import *


class InputProcessor:
    @staticmethod
    def get_new_direction(event_list):
        for event in reversed(event_list):
            if event.type == pygame.KEYDOWN:
                if event.key == K_w:
                    return "up"
                elif event.key == K_a:
                    return "left"
                elif event.key == K_s:
                    return "down"
                elif event.key == K_d:
                    return "right"
                else:
                    return None

    @staticmethod
    def get_piece_shift(event_list):
        # may have to edit logic, currently returns the most recent shift input for the active piece
        for event in reversed(event_list):
            if event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    return "up"
                elif event.key == K_LEFT:
                    return "left"
                elif event.key == K_DOWN:
                    return "down"
                elif event.key == K_RIGHT:
                    return "right"
                elif event.key == K_SPACE:
                    return "drop"
                elif event.key == K_SLASH:
                    return "rotate"
                else:
                    return None
