from chip8.config import (
    CHIP8_TOTAL_KEY
)
import pygame

def _is_keyboard_inbound(key: int):
    assert (key >= 0 and key < CHIP8_TOTAL_KEY)

class Keyboard:
    keyboard: list = [False]*CHIP8_TOTAL_KEY
    mapping = {
        0: pygame.K_0,
        1: pygame.K_1,
        2: pygame.K_2,
        3: pygame.K_3,
        4: pygame.K_4,
        5: pygame.K_5,
        6: pygame.K_6,
        7: pygame.K_7,
        8: pygame.K_8,
        9: pygame.K_9,
        0xA: pygame.K_a,
        0xB: pygame.K_b,
        0xC: pygame.K_c,
        0xD: pygame.K_d,
        0xE: pygame.K_e,
        0xF: pygame.K_f
    }

    def map(self, key):
        for k,v in self.mapping.items():
            if v == key:
                return k
        
        return None

    def _is_down(self, key: int):
        _is_keyboard_inbound(key)
        return self.keyboard[key]

    def down(self, key: int):
        _is_keyboard_inbound(key)
        self.keyboard[key] = True

    def up(self, key: int):
        _is_keyboard_inbound(key)
        self.keyboard[key] = False

