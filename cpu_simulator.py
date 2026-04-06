import time

class Microprocessor8086:
    def __init__(self):
        self.registers = {
            'AX': 0, 
            'BX': 0, 
            'CX': 0, 
            'DX': 0
        }

    def execute_instruction(self, instruction):
        """Parses and executes a single assembly instruction."""
        parts = instruction.replace(',', ' ').split()
        if not parts: 
            return

        opcode = parts[0].upper()
        
        try:
            if opcode == 'MOV':
                dest = parts[1].upper()
                src = parts[2].upper()
                if src in self.registers:
                    self.registers[dest] = self.registers[src]
                else:
                    self.registers[dest] = int(src)
                    
            elif opcode == 'ADD':
                dest = parts[1].upper()
                src = parts[2].upper()
                val = self.registers[src] if src in self.registers else int(src)
                self.registers[dest] += val
                
            elif opcode == 'SUB':
                dest = parts[1].upper()
                src = parts[2].upper()
                val = self.registers[src] if src in self.registers else int(src)
                self.registers[dest] -= val
                
            else:
                print(f"  [!] ERROR: Unknown Instruction '{opcode}'")
                
        except Exception as e:
            print(f"  [!] SYNTAX ERROR in '{instruction}': {e}")

    def dump_registers(self):
        """Prints the current state of all registers in Hex and Decimal."""
        print("+---------------------------------+")
        print("|    8086 INTERNAL REGISTERS      |")
        print("+---------------------------------+")
        for reg, val in self.registers.items():
            val = val & 0xFFFF 
            print(f"|  {reg}  |  {val:04X}h  |  (Dec: {val:<5})  |")
        print("+---------------------------------+\n")

if __name__ == "__main__":
    cpu = Microprocessor8086()
    
    print("\n" + "="*45)
    print("      INTEL 8086 EMULATOR SHELL v1.0")
    print("  Type 'EXIT' to quit, 'RESET' to clear.")
    print("="*45 + "\n")
    
    cpu.dump_registers()
    
    while True:
        try:
            cmd = input("8086> ").strip()
            
            if not cmd:
                continue
            if cmd.upper() == 'EXIT':
                print("Powering down CPU...")
                break
            if cmd.upper() == 'RESET':
                cpu = Microprocessor8086()
                print("\n[!] CPU Reset to Initial State [!]\n")
                cpu.dump_registers()
                continue
                
            cpu.execute_instruction(cmd)
            cpu.dump_registers()
            
        except KeyboardInterrupt:
            print("\nPowering down CPU...")
            break