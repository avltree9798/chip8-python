from chip8.config import (
    CHIP8_TOTAL_DATA_REGISTER
)

class Register:
    V: list = [0]*CHIP8_TOTAL_DATA_REGISTER
    I: int = 0
    delay_timer: int = 0
    sound_timer: int = 0
    PC: int = 0
    SP = 0
