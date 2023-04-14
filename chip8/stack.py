from chip8.config import (
    CHIP8_TOTAL_STACK_DEPTH
)

def _is_stack_inbound(chip8):
    assert (chip8.register.SP >= 0 and chip8.register.SP < CHIP8_TOTAL_STACK_DEPTH)

class Stack:
    stack: list = [0]*CHIP8_TOTAL_STACK_DEPTH
    
    def __init__(self, chip8) -> None:
        self.chip8 = chip8

    def push(self, val):
        _is_stack_inbound(self.chip8)
        self.stack[self.chip8.register.SP] = val
        self.chip8.register.SP += 1

    def pop(self):
        self.chip8.register.SP -= 1
        _is_stack_inbound(self.chip8)
        val = self.stack[self.chip8.register.SP]
        return val