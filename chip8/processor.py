from pygame import key
from chip8.config import (
    CHIP8_MEMORY_SIZE,
    CHIP8_LOAD_ADDRESS,
    CHIP8_DEFAULT_SPRITE_HEIGHT
)
from chip8.memory import Memory
from chip8.register import Register
from chip8.screen import Screen
from chip8.stack import Stack
from chip8.keyboard import Keyboard
import pygame
import random

class Chip8:
    memory: Memory
    register: Register
    stack: Stack
    keyboard: Keyboard
    screen: Screen
    default_character_set: list = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
    ]

    def __init__(self) -> None:
        self.memory = Memory()
        self.register = Register()
        self.stack = Stack(self)
        self.keyboard = Keyboard()
        self.screen = Screen(self.memory)
        for i, v in enumerate(self.default_character_set):
            self.memory.memory[i] = v

    def _is_valid_index(self, index: int):
        assert (index >= 0 and index < self.memory.MEMORY_SIZE)

    def memory_set(self, index: int, value):
        self.memory.set(index, value)
    
    def memory_get(self, index:int):
        return self.memory.get(index)
    
    def stack_push(self, val):
        self.stack.push(val)

    def stack_pop(self):
        return self.stack.pop()
    
    def _exec_extended_eight(self, opcode: int, x: int, y: int):
        tmp = 0
        match opcode & 0x000f:
            # LD Vx, Vy - 8xy0: Vx = Vy
            case 0x00:
                self.register.V[x] = self.register.V[y]
            
            # OR Vx, Vy - 8xy1: Performs a bitwise OR on Vx and Vy, stores the result in Vx
            case 0x01:
                self.register.V[x] |= self.register.V[y]
            
            # AND Vx, Vy - 8xy2: Performs a bitwise AND on Vx and Vy, stores the result in Vx
            case 0x02:
                self.register.V[x] &= int(self.register.V[y])
            
            # XOR Vx, Vy - 8xy3: Performs a bitwise XOR on Vx and Vy, stores the result in Vx
            case 0x03:
                self.register.V[x] ^= int(self.register.V[y])
            
            # ADD Vx, Vy - 8xy4: Set Vx = Vx + Vy, set VF = carry
            case 0x04:
                tmp = self.register.V[x] + self.register.V[y]
                self.register.V[0x0F] = 1 if tmp > 0xFF else 0
                self.register.V[x] = tmp & 0xFF

            # SUB Vx, Vy -  8xy5: Set Vx = Vx - Vy, set VF = NOT borrow.
            case 0x05:
                self.register.V[0x0F] = 0
                if self.register.V[x] > self.register.V[y]:
                    self.register.V[0x0F] = 1
                self.register.V[x] -= self.register.V[y]
            
            # SHR Vx {, Vy} - 8xy6: Set Vx = Vx SHR 1.
            case 0x06:
                self.register.V[0x0F] = int(self.register.V[x]) & 0x01
                self.register.V[x] /= 2
            
            # SUBN Vx, Vy - 8xy7: Set Vx = Vy - Vx, set VF = NOT borrow.
            case 0x07:
                self.register.V[0x0F] = 1 if self.register.V[y] > self.register.V[x] else 0
                self.register.V[x] -= self.register.V[y]

            # SHL Vx {, Vy} - 8xyE: Set Vx = Vx SHL 1. 
            case 0x0E:
                self.register.V[0x0F] = self.register.V[x] & 0b1000000
                self.register.V[x] *= 2
    
    def wait_for_key_press(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                key = event.key
                virtual_key = self.keyboard.map(key)
                if virtual_key is not None:
                    return virtual_key

    def _exec_extended_f(self, opcode: int, x: int, y: int):
        match opcode & 0x00ff:
            # LD Vx, DT - Fx07: Set Vx = delay timer value.
            case 0x07:
                self.register.V[x] = self.register.delay_timer
            
            # LD Vx, K - Fx0A: Wait for a key press, store the value of the key in Vx.
            case 0x0A:
                key = self.wait_for_key_press()
                self.register.V[x] = key

            # LD DT, Vx - Fx15: Set delay timer = Vx.
            case 0x15:
                self.register.delay_timer = self.register.V[x]
            
            # LD ST, Vx - Fx18: Set sound timer = Vx.
            case 0x18:
                self.register.sound_timer = self.register.V[x]
            
            # ADD I, Vx - Fx1E: Set I = I + Vx.
            case 0x1E:
                self.register.I += self.register.V[x]
            
            # LD F, Vx - Fx29: Set I = location of sprite for digit Vx. 
            case 0x29:
                self.register.I = self.register.V[x] * CHIP8_DEFAULT_SPRITE_HEIGHT
            
            # LD B, Vx - Fx33: Store BCD representation of Vx in memory locations I, I+1, and I+2.
            case 0x33:
                hundreds = int(self.register.V[x]/100)
                tens = int(self.register.V[x] / 10 % 10)
                unit = self.register.V[x] % 10
                self.memory_set(self.register.I, hundreds)
                self.memory_set(self.register.I+1, tens)
                self.memory_set(self.register.I+2, unit)
            
            # LD [I], Vx - Fx55: Store registers V0 through Vx in memory starting at location I.
            case 0x55:
                for i in range(0, x):
                    self.memory_set(self.register.I+i, self.register.V[i])
                
            # LD Vx, [I] - Fx65: Read registers V0 through Vx from memory starting at location I.
            case 0x65:
                 for i in range(0, x):
                    self.register.V[i] = self.memory_get(self.register.I+i)
                
    def _exec_extended(self, opcode: int):
        nnn = opcode & 0x0fff
        x = (opcode >> 8) & 0x000f
        y = (opcode >> 4) & 0x000f
        kk = opcode &0x00ff
        n = opcode & 0x000f
        
        match opcode & 0xf000:
            # JP addr - 1nnn: Jump to address nnn
            case 0x1000:
                self.register.PC = nnn
            
            # CALL addr - 2nnn: Call subroutine at address nnn
            case 0x2000:
                self.stack_push(self.register.PC)
                self.register.PC = nnn
            
            # SE Vx, byte - 3xkk: Skip next instruction if Vx == kk
            case 0x3000:
                if self.register.V[x] == kk:
                    self.register.PC += 2
            
            # SNE Vx, byte - 4xkk: Skip next instruction if Vx != kk
            case 0x4000:
                if self.register.V[x] != kk:
                    self.register.PC += 2
            
            # SE Vx, Vy - 5xy0: Skip next instruction if Vx == Vy
            case 0x5000:
                if self.register.V[x] == self.register.V[y]:
                    self.register.PC += 2
            
            # LD Vx, byte - 6xkk: Vx = kk
            case 0x6000:
                self.register.V[x] = kk
            
            # ADD Vx, byte - 7xkk: Vx += kk
            case 0x7000:
                self.register.V[x] += kk
            
            case 0x8000:
                self._exec_extended_eight(opcode,x,y)
            
            # SNE Vx, Vy - 9xy0: Skip next instruction if Vx != Vy.
            case 0x9000:
                if self.register.V[x] != self.register.V[y]:
                    self.register.PC += 2

            # LD I, addr - Annn: The value of register I is set to nnn.
            case 0xA000:
                self.register.I = nnn
            
            # JP V0, addr - Bnnn: The program counter is set to nnn plus the value of V0.
            case 0xB000:
                self.register.PC = nnn + self.register.V[0]
            
            # RND Vx, byte - Cxkk: The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk. The results are stored in Vx.
            case 0xC000:
                self.register.V[x] = random.randint(0, 255) & kk
            
            # DRW Vx, Vy, nibble - Dxyn: Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
            case 0xD000:
                collision = self.screen.draw_sprite(self.register.V[x], self.register.V[y], self.register.I, n)
                self.register.V[0x0F] = 1 if collision else 0
            
            case 0xE000:
                match opcode & 0x00ff:
                    # SKP Vx - Ex9E: Skip next instruction if key with the value of Vx is pressed.
                    case 0x9E:
                        if self.keyboard._is_down(self.register.V[x]):
                            self.register.PC += 2

                    # SKNP Vx - ExA1: Skip next instruction if key with the value of Vx is not pressed.
                    case 0xA1:
                        if not self.keyboard._is_down(self.register.V[x]):
                            self.register.PC += 2

            case 0xF000:
                self._exec_extended_f(opcode,x,y)
            
    def exec(self, opcode: int):
        match opcode:
            # CLS: Clear the display
            case 0x00E0:
                self.screen.cls()
            
            # RET: Return from subroutine
            case 0x00EE:
                self.register.PC = self.stack_pop()
            case _ :
                self._exec_extended(opcode)
            
            

    def load(self, buffer, size: int):
        assert size+CHIP8_LOAD_ADDRESS < CHIP8_MEMORY_SIZE
        for i in range(size):
            self.memory.memory[CHIP8_LOAD_ADDRESS+i] = buffer[i]
        
        self.register.PC = CHIP8_LOAD_ADDRESS
