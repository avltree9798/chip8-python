from chip8.config import (
    CHIP8_COLOUR_BLACK,
    CHIP8_COLOUR_WHITE,
    CHIP8_HEIGHT,
    CHIP8_WIDTH,
    CHIP8_WINDOW_MULTIPLIER,
    EMULATOR_WINDOW_TITLE
)
from chip8.processor import Chip8
import os
import pygame
import time


def beep(duration):
    # brew install sox
    os.system('play --no-show-progress --null\
               --channels 1 synth %s triangle %f' % (duration, 440))


class Emulator:
    def __init__(self, buffer, filename):
        self.buffer = buffer
        pygame.init()
        self.screen = pygame.display.set_mode(
            [
                CHIP8_WIDTH * CHIP8_WINDOW_MULTIPLIER,
                CHIP8_HEIGHT * CHIP8_WINDOW_MULTIPLIER
            ]
        )
        self.running = True
        self.chip8 = Chip8()
        pygame.display.set_caption(f'{EMULATOR_WINDOW_TITLE}: {filename}')

    def render(self):
        self.screen.fill(CHIP8_COLOUR_BLACK)
        for y in range(CHIP8_HEIGHT):
            for x in range(CHIP8_WIDTH):
                if self.chip8.screen.is_set(x, y):
                    white_surface = pygame.Surface((
                        CHIP8_WINDOW_MULTIPLIER,
                        CHIP8_WINDOW_MULTIPLIER
                    ))
                    white_surface.fill(CHIP8_COLOUR_WHITE)
                    self.screen.blit(white_surface, (
                        x * CHIP8_WINDOW_MULTIPLIER,
                        y * CHIP8_WINDOW_MULTIPLIER
                    ))
        pygame.display.flip()

    def handle_event(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    key = event.key
                    virtual_key = self.chip8.keyboard.map(key)
                    if virtual_key:
                        self.chip8.keyboard.down(virtual_key)
                case pygame.KEYUP:
                    key = event.key
                    virtual_key = self.chip8.keyboard.map(key)
                    if virtual_key:
                        self.chip8.keyboard.up(virtual_key)

    def handle_timer(self):
        if self.chip8.register.delay_timer > 0:
            time.sleep(1/1000)
            self.chip8.register.delay_timer -= 1
        if self.chip8.register.sound_timer > 0:
            duration = (self.chip8.register.sound_timer)/60
            beep(duration)
            self.chip8.register.sound_timer = 0

    def execution(self):
        opcode = self.chip8.memory.get_short(self.chip8.register.PC)
        self.chip8.register.PC += 2
        self.chip8.exec(opcode)

    def run(self):
        assert self.buffer

        self.chip8.load(self.buffer, len(self.buffer))
        while self.running:
            self.handle_event()
            self.handle_timer()
            self.render()
            self.execution()

        pygame.quit()
        return 0
