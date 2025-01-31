opcode = 0x5A29

test1 = (opcode & 0xF00) >> 8
test2 = (opcode >> 8) & 0x0F
print("Test1 = " + str(test1) + "\nTest2 = " + str(test2))