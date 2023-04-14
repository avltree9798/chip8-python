from chip8.config import (
    CHIP8_WIDTH,
    CHIP8_HEIGHT
)
from chip8.memory import Memory


def _check_bounds(x: int, y: int):
    assert (x >= 0 and x < CHIP8_WIDTH and y >= 0 and y < CHIP8_HEIGHT)


class Screen:
    memory: Memory

    def __init__(self, memory: Memory) -> None:
        self.pixels = []
        self.cls()
        self.memory = memory

    def set(self, x: int, y: int):
        _check_bounds(x, y)
        self.pixels[y][x] = True

    def unset(self, x: int, y: int):
        _check_bounds(x, y)
        self.pixels[y][x] = False

    def is_set(self, x: int, y: int):
        _check_bounds(x, y)
        return self.pixels[y][x]

    def cls(self):
        W = CHIP8_WIDTH
        H = CHIP8_HEIGHT
        self.pixels = [[False for _ in range(W)] for _ in range(H)]

    def draw_sprite(self, x: int, y: int, base_addr: int, num: int = 5):
        pixel_changed = False
        for ly in range(num):
            c = self.memory.memory[ly+base_addr]
            for lx in range(8):
                if (c & (0b10000000 >> lx)) == 0:
                    continue
                current_y = (ly+y) % CHIP8_HEIGHT
                current_x = (lx+x) % CHIP8_WIDTH
                if self.pixels[current_y][current_x]:
                    pixel_changed = True
                self.pixels[current_y][current_x] ^= True
        return pixel_changed
