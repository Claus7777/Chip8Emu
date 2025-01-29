import pygame 
import numpy as np
from pygame.locals import QUIT

#CONSTANTES
MEMORY_SIZE = 4096
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32
REGISTER_COUNT = 16
STACK_SIZE = 16

class Chip8:
    def __init__(self):
        #Inicializa a memoria e o sistema
        self.memory = [0] * MEMORY_SIZE
        self.register = [0] * REGISTER_COUNT
        self.index_register = 0
        self.program_counter = 0x200
        self.stack = [0] * STACK_SIZE
        self.stack_pointer = -1
        self.delay_timer = 0
        self.sound_timer = 0
        self.screen = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=np.uint8)
        self.keys = [0] * 16

        #Inicializa fontset
        self.fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]

        #Carrega o fontset na memoria de 0x50 até 0x0A0
        self.memory[0x50:0x50+len(self.fontset)] = self.fontset

        #Configuração de RNG
        self.rng_state = 0

    def cycle(self):
        #Fetch opcode
        opcode = (self.memory[self.program_counter] << 8 | self.memory[self.program_counter + 1])

            
        #Decodifica e opera o opcode
        self.execute_opcode(opcode)

        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("Beep!")
            self.sount_timer -= 1

    def execute_opcode(self, opcode):
        #Extrair nibbles do opcode
        x = (opcode >> 8) * 0x0f
        y = (opcode >> 4) * 0x0F

        if opcode == 0x00E0:
            #Clear screen
            self.screen.fill(0)
            self.program_counter += 2
        elif opcode == 0x00EE:
            #Return from subroutine
            self.program_counter = self.stack[self.stack_pointer]
            self.stack_pointer -= 1
        elif (opcode & 0xF000) == 0x1000:
            #OPCODE 1NNN
            #Jumps to address
            self.program_counter = (opcode & 0x0FFF)
        elif (opcode & 0xF000) == 0x2000:
            #OPCODE 2NNN
            #Calls subroutine at NNN
            #CALLS ao invés de JUMP significa que a gente vai ter que voltar pra onde a gente estaria, logo é bom guardar 
            #o Program Counter na stack
            self.stack_pointer += 1
            self.stack[self.stack_pointer] = self.program_counter
            self.program_counter = opcode & 0x0FFF
        elif (opcode & 0xF000) == 0x3000:
            #OPCODE 3XNN
            #Skips the next instruction if VX equals NN (usually the next instruction is to jump a code block)
            if self.register[x] == (opcode & 0x00FF):
                self.program_counter+=4
            else: self.program_counter+=2
        elif (opcode )
#Display Pygame Setup
scale = 10
window_size = (SCREEN_WIDTH * scale, SCREEN_HEIGHT * scale)

def main():
    pygame.init()
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Claus-8")
    clock = pygame.time.Clock()
    surface = pygame.Surface((SCREEN_HEIGHT, SCREEN_WIDTH))

    emulator = Chip8()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        #Roda 10 ciclos por frame pra corrigir o timing
        for _ in range (10):
            emulator.cycle()

        #Update display
        pixels = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)
        pixels[emulator.screen == 1] = [255, 255, 255]
        pygame.surfarray.blit_array(surface, pixels)
        scaled_surface = pygame.transform.scale(surface, window_size)
        screen.blit(scaled_surface, (0,0))
        pygame.display.flip()

        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()