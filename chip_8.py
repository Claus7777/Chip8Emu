import pygame 
import numpy as np
from pygame.locals import QUIT

#CONSTANTES
MEMORY_SIZE = 4096
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32
REGISTER_COUNT = 16
STACK_SIZE = 16

#RNG
MODULUS = 256
MULTIPLIER = 1664525
INCREMENT = 1013904223
seed = (MULTIPLIER * 0 + INCREMENT) % MODULUS

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

        #Valores que o program counter pode ser incrementado
        STOP = 0
        PROCEED = 2
        SKIP = 4

        #Tirando em casos especiais, incrementamos o PC em 2
        program_counter_instruction = PROCEED

        if opcode == 0x00E0:
            #Clear screen
            self.screen.fill(0)

        elif opcode == 0x00EE:
            #Return from subroutine
            self.program_counter = self.stack[self.stack_pointer]
            self.stack_pointer -= 1
            program_counter_instruction=STOP

        elif (opcode & 0xF000) == 0x1000:
            #OPCODE 1NNN
            #Jumps to address
            self.program_counter = (opcode & 0x0FFF)
            program_counter_instruction = STOP

        elif (opcode & 0xF000) == 0x2000:
            #OPCODE 2NNN
            #Calls subroutine at NNN
            #CALLS ao invés de JUMP significa que a gente vai ter que voltar pra onde a gente estaria, logo é bom guardar 
            #o Program Counter na stack
            self.stack_pointer += 1
            self.stack[self.stack_pointer] = self.program_counter
            self.program_counter = opcode & 0x0FFF
            program_counter_instruction = STOP

        elif (opcode & 0xF000) == 0x3000:
            #OPCODE 3XNN
            #Skips the next instruction if VX equals NN (usually the next instruction is to jump a code block)
            if self.register[x] == (opcode & 0x00FF):
                program_counter_instruction = SKIP
            else: program_counter_instruction = PROCEED

        elif (opcode & 0xF000) == 0x4000:
            #OPCODE 4XNN
            #Skips the next instruction if VX does not equal NN (usually the next instruction is a jump to skip a code block).
            if self.register[x] != (opcode & 0x00FF):
                program_counter_instruction = SKIP
            else: program_counter_instruction = PROCEED

        elif (opcode & 0xF000) == 0x5000:
            #OPCODE 5XY0
            #Skips the next instruction if VX equals VY (usually the next instruction is a jump to skip a code block).
            if self.register[x] == self.register[y]:
                program_counter_instruction = SKIP
            else: program_counter_instruction = PROCEED

        elif (opcode & 0xF000) == 0x6000:
            #OPCODE 6XNN
            #Sets VX to NN
            self.register[x] == (opcode & 0x00FF)


        elif (opcode & 0xF000) == 0x7000:
            #OPCODE 7XNN
            #Adds NN to Vx, Carry flag not changed
            self.register[x] += (opcode & 0x00FF)


        elif (opcode & 0xF000) == 0x8000:
            if (opcode & 0x000F) == 0x0000:
                #OPCODE 8XY0
                #Sets VX to the value of VY.
                self.register[x] = self.register[y]


            if (opcode & 0x000F) == 0x0001:
                #OPCODE 8XY1
                #Sets VX to VX or VY. (bitwise OR operation).
                self.register[x] = (self.register[x] | self.register[y])


            if (opcode & 0x000F) == 0x0002:
                #OPCODE 8XY2
                #Sets VX to VX and VY (bitwise AND)
                self.register[x] = (self.register[x] | self.register[y])


            if (opcode & 0x000F) == 0x0003:
                #OPCODE 8XY3
                #Sets VX to VX XOR VY
                self.register[x] = (self.register[x] | self.register[y])


            if (opcode & 0x000F) == 0x0004:
                #OPCODE 8XY4
                #Adds VY to VX. VF is set to 1 when there's an overflow, and to 0 when there is not.
                self.register[x] += self.register[y]
                if self.register[x] > 0xFF:
                    self.register[x] = self.register[x] % 0xFF
                    self.register[0xF] = 1
                else: self.register[0xF] = 0 

            if (opcode & 0x000F) == 0x0005:
                self.register[x] -= self.register[y]
                if self.register[x] < 0:
                    self.register[x] = 0xFF + self.register[x]
                    self.register[0xF] = 0
                else: self.register[0xF] = 1

            if (opcode & 0x000F) == 0x0006:
                self.register[0xF] = (self.register[x] & 0x0F)
                self.register[x] = (self.register[x >> 1])

            if (opcode & 0x000F) == 0x0007:
                self.register[x] = self.register[y] - self.register[x]
                if self.register[x] < 0:
                    self.register[x] = 0xFF + self.register[x]
                    self.register[0xF] = 0
                else: self.register[0xF] = 1

            if (opcode & 0x000F) == 0x000E:
                if self.register[x] >= 128:
                    self.register[0xF] = 1
                else: self.register[0xF] = 0
                self.register[x] = self.register[x] << 1

        elif (opcode & 0xF000) == 0x9000:
            if self.register[x] != self.register[y]:
                program_counter_instruction = SKIP
            else: program_counter_instruction = PROCEED

        elif (opcode & 0xF000) == 0xA000:
            self.index_register = (opcode & 0x0FFF)

        elif (opcode & 0xF000) == 0xB000:
            self.program_counter = self.register[0x0] + (opcode & 0x0FFF)

        elif (opcode & 0xF000) == 0xC000:
            self.register[x] = (seed & (opcode & 0x0FFF))

        elif (opcode & 0xF000) == 0xD000:
            #OPCODE DXYN
            #Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels.
            # Each row of 8 pixels is read as bit-coded starting from memory location I; 
            # I value does not change after the execution of this instruction. As described above, 
            # VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that does not happen.
            pass

        self.program_counter += program_counter_instruction





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
        
        #Ticks RNG seed
        seed = (MULTIPLIER * seed + INCREMENT) % MODULUS

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