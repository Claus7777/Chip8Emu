import pygame
import numpy as np
from pygame.locals import QUIT

opcode = ""
memory = [0]*4096
register = [0] * 15

index = 0
program_counter = 0x200

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32
screen = [[0 for y in range (SCREEN_WIDTH)] for x in range (SCREEN_HEIGHT)]


delay_timer = 0 #Se maior que 0, diminuir por um a cada clock cycle até chegar a 0
sound_timer = 0 #Mesmo comportamento do outro timer, mas toca um beep quando é igual a 1

stack = [None] * 16
stack_pointer = 0

key = [None] * 16

font_set = { 
  "0" : [0xF0, 0x90, 0x90, 0x90, 0xF0],
  "1" : [0x20, 0x60, 0x20, 0x20, 0x70],
  "2" : [0xF0, 0x10, 0xF0, 0x80, 0xF0],
  "3" : [0xF0, 0x10, 0xF0, 0x10, 0xF0],
  "4" : [0x90, 0x90, 0xF0, 0x10, 0x10],
  "5" : [0xF0, 0x80, 0xF0, 0x10, 0xF0],
  "6" : [0xF0, 0x80, 0xF0, 0x90, 0xF0],
  "7" : [0xF0, 0x10, 0x20, 0x40, 0x40],
  "8" : [0xF0, 0x90, 0xF0, 0x90, 0xF0],
  "9" : [0xF0, 0x90, 0xF0, 0x10, 0xF0],
  "A" : [0xF0, 0x90, 0xF0, 0x90, 0x90],
  "B" : [0xE0, 0x90, 0xE0, 0x90, 0xE0],
  "C" : [0xF0, 0x80, 0x80, 0x80, 0xF0],
  "D" : [0xE0, 0x90, 0x90, 0x90, 0xE0],
  "E" : [0xF0, 0x80, 0xF0, 0x80, 0xF0],
  "F" : [0xF0, 0x80, 0xF0, 0x80, 0x80]
}

#region RNG
MODULUS = 256
MULTIPLIER = 1664525
INCREMENT = 1013904223
seed = (MULTIPLIER * 0 + INCREMENT) % MODULUS
#endregion

# Memory Map
# 0x000-0x1FF - Chip 8 interpreter (contains font set in emu)
# 0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F)
# 0x200-0xFFF - Program ROM and work RAM



def draw_to_screen_matrix():

    pass

def display_screen():
    pygame.surfarray.blit_array(matrix_surface, screen)
    scaled_surface = pygame.transform.scale(matrix_surface, window_size)
    screen.blit(scaled_surface, (0 , 0))
    pygame.display.flip()

def initialize_memory():
    program_counter = 0x200
    opcode = 0
    index = 0
    stack_pointer = 0
    #Fill memory 0x000 to 0x1FF with interpreter
    #Fill memory 0x050 to 0X0A0 with the built in font set
    for i in range(0x50, 0xA0):
        memory[i]
    #Fill 0x200 to 0xFFF with program


def emulate_cycle():
    #Fetch opcode from memory
    #Decode opcode
    opcode = str(hex(memory[program_counter] + memory[program_counter + 1]))
    opcode = opcode[2:]
    #Execute opcode
    execute_opcode(opcode)


    #Update timers
    if sound_timer > 0:
        if sound_timer == 1:
            print("BEEP! Sound should play here")
        sound_timer = sound_timer -1
    
    if delay_timer > 0:
        delay_timer = delay_timer - 1

def randomize_seed():
    seed = (MULTIPLIER * seed + INCREMENT) % MODULUS

def execute_opcode(e_opcode):
    if opcode[0] == "0":
        if opcode[1] == "0":
            if opcode[3] == "0":
                #OPCODE 00E0
                #Screen clear"
                for y in range (SCREEN_WIDTH):
                    for x in range (SCREEN_HEIGHT):
                        screen[y][x] = 0
                program_counter += 2
                return
            
            elif opcode[3] == "E":
                #OPCODE 00EE
                #Returns from subroutine"
                stack_pointer = stack_pointer -1
                program_counter = stack[stack_pointer]
                return

    elif opcode[0] == "1":
        #OPCODE 1NNN
        #Jumps to subroutine at memory[NNN]
        program_counter = int(opcode[1:], 16)
        return
    
    elif opcode[0] == "2":
        #OPCODE 2NNN

        # print("Calls subroutine at memory[NNN]")
        #CALLS ao invés de JUMP significa que a gente vai ter que voltar pra onde a gente estaria, logo é bom guardar 
        #o Program Counter na stack

        stack[stack_pointer] = program_counter
        stack_pointer += 1
        program_counter = int(opcode[1:], 16)
        return
    
    elif opcode[0] == "3":
        #OPCODE 3XNN
        #Skips the next instruction if register[int(opcode[1], 16)] equals int(opcode[2:],16)
        # (usually the next instruction is a jump to skip a code block).")
        if register[int(opcode[1], 16)] == int(opcode[2:], 16):
            program_counter+=4
            return
        program_counter+=2
        return
           
        
    elif opcode[0] == "4":
        #OPCODE 4XNN
        # Skips the next instruction if register[X] does not equals NN)
        # (usually the next instruction is a jump to skip a code block).")
        if register[int(opcode[1], 16)] != int(opcode[2:], 16):
            program_counter+=4 
            return
        program_counter += 2
        return
    
    elif opcode[0] == "5":
        #OPCODE 5XY0
        # print("Skips the next instruction if register[int(opcode[1], 16)] equals register[int(opcode[2])] (usually the next instruction is a jump to skip a code block).")
        if register[int(opcode[1], 16)] == register[int(opcode[2],16)]:
            program_counter+=4
            return
        program_counter += 2
        return
    
    elif opcode[0] == "6":
        #OPCODE 6XNN
        # print("Sets register[int(opcode[1], 16)] to int(opcode[2:],16)")
        register[int(opcode[1], 16)] == int(opcode[2:],16)
        return
    
    elif opcode[0] == "7":
        #OPCODE 7XNN
        # print("Adds int(opcode[2:],16) to register[int(opcode[1], 16)]")
        register[int(opcode[1], 16)] += int(opcode[2:], 16)
        if register[int(opcode[1])] > 256:
            register[int(opcode[1])] -= 256
        return
    
    elif opcode[0] == "8":
        if opcode[3] == "0":
            #OPCODE 8XY0
            # print("Sets register[opcode[1]] to the value of register[opcode[2]].")
            register[int(opcode[1], 16)] = register[int(opcode[2], 16)]
            return
            
        if opcode[3] == "1":
            #OPCODE 8XY1
            # print("Sets VX to (VX OR VY).")
            register[int(opcode[1], 16)] = register[int(opcode[1], 16)] | register[int(opcode[2], 16)]
            return
            
        if opcode[3] == "2":
            #OPCODE 8XY2
            # print("Sets VX to VX AND VY.")
            register[int(opcode[1], 16)] = register[int(opcode[1], 16)] & register[int(opcode[2], 16)]
            return
        
        if opcode[3] == "3":
            #OPCODE 8XY3
            # print("Sets VX to VX xor VY")
            register[int(opcode[1], 16)] = register[int(opcode[1], 16)] ^ register[int(opcode[2], 16)] 
            return
        
        if opcode[3] == "4":
            #OPCODE 8XY4
            # print("Adds VY to VX. VF is set to 1 when there's an overflow, and to 0 when there is not.")
            register[int(opcode[1])] += register[int(opcode[2], 16)]
            if register[int(opcode[1], 16)] > 255:
                register[int(opcode[1], 16)] -= 255
                register[15] = 1
            else: register[15] = 0
            return
        
        if opcode[3] == "5":
            #OPCODE 8XY5
            # print("VY is subtracted from VX. VF is set to 0 when there's an underflow, and 1 when there is not. (i.e. VF set to 1 if VX >= VY and 0 if not)")
            register[int(opcode[1], 16)] -= register[int(opcode[2], 16)]
            if register[int(opcode[1], 16)] < 0:
                register[int(opcode[1], 16)] += 255
                register[15] = 0
            else: register[15] = 1
            return

        if opcode[3] == "6":
            #OPCODE 8XY6
            # print("Shifts VX to the right by 1, then stores the least significant bit of VX prior to the shift into VF.")
            least_sig = bin(register[int(opcode[1], 16)])
            register[15] = int(least_sig[-1])

            register[int(opcode[1], 16)]  = register[int(opcode[1], 16)] >> 1
            return
        
        if opcode[3] == "7":
            #OPCODE 8XY7
            # Sets VX to VY minus VX. VF is set to 0 when there's an underflow, and 1 when there is not. (i.e. VF set to 1 if VY >= VX).
            register[int(opcode[1], 16)] = register[int(opcode[2], 16)] - register[int(opcode[1], 16)]
            if register[int(opcode[1], 16)] < 0:
                register[int(opcode[1], 16)] += 255
                register[15] = 0
            else: register[15] = 1
            return
            
        if opcode[3] == "e":
            #OPCODE 8XYE
            # Shifts VX to the left by 1, then sets VF to 1 if the most significant bit of VX prior to that shift was set, or to 0 if it was unset.
            most_sig = bin(register[int(opcode[1], 16)])
            if most_sig[2:] == "1":
                register[15] = 1
            else: register[15] = 0
            register[int(opcode[1], 16)] = register[int(opcode[1], 16)] << 1
            return 
        return
    
    elif opcode[0] == "9":
        #OPCODE 9XY0
        #Skips the next instruction if VX does not equal VY. (Usually the next instruction is a jump to skip a code block)
        if register[int(opcode[1], 16)] != register[int(opcode[2], 16)]:
            program_counter+=4
        else: program_counter += 2
        return
    
    elif opcode[0] == "a":
        #OPCODE ANNN
        #Sets I to the address NNN
        index = int(opcode[1:], 16)
        return
    
    elif opcode[0] == "b":
        #OPCODE BNNN
        #Jumps to the address NNN + 0
        program_counter = register[0] + int(opcode[1:], 16)
        return
    
    elif opcode[0] == "c":
        #OPCODE CXNN
        #Sets VX to the result of a bitwise and operation on a random number from 0 to FF and NN.
        register[int(opcode[1], 16)] = seed & int(opcode[2:], 16)
        randomize_seed()
        return
    
    elif opcode[0] == "d":
        #OPCODE DXYN
        #Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels. Each row of 8 pixels is read as bit-coded
        #starting from memory location I; I value does not change after the execution of this instruction. As described above,
        #VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that does not happen.

        register[15] = 0
        for height in range (opcode[3]):
            for width in range(8):
                pass
        return
    
    elif opcode[0] == "e":
        print(opcode)
        return
    elif opcode[0] == "f":
        print(opcode)
        return

#Inicializando Pygame
pygame.init()
scale = 10
window_size = (SCREEN_WIDTH * scale, SCREEN_HEIGHT * scale)
screen = pygame.display.set_mode(window_size)
clock = pygame.time.Clock()

matrix_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), depth=screen.get_bitsize)
running = True
initialize_memory()
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
    emulate_cycle()
    display_screen()
pygame.quit()
