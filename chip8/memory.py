from chip8.config import (
    CHIP8_MEMORY_SIZE
)


def _is_valid_index(index: int):
    assert (index >= 0 and index < CHIP8_MEMORY_SIZE)


class Memory:
    memory: list = [0x0]*CHIP8_MEMORY_SIZE

    def set(self, index: int, val):
        _is_valid_index(index)
        self.memory[index] = val

    def get(self, index: int):
        _is_valid_index(index)
        return self.memory[index]

    def get_short(self, index: int):
        byte1 = self.get(index)
        byte2 = self.get(index+1)
        return byte1 << 8 | byte2
