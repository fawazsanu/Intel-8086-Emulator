import sys

class Microprocessor8086:
    """
    A software emulator for the Intel 8086 microprocessor.

    Supports:
    - General-purpose registers: AX, BX, CX, DX
    - Segment/pointer registers: SP, BP, SI, DI
    - Flag Register: Zero Flag (ZF), Carry Flag (CF), Sign Flag (SF), Overflow Flag (OF)
    - Memory: 64KB address space (dictionary-backed)
    - Instructions: MOV, ADD, SUB, MUL, DIV, AND, OR, XOR, NOT, CMP,
                    JMP, JZ, JNZ, JE, JNE, JG, JL, PUSH, POP, NOP
    - Program execution mode with labelled jump targets
    """

    REGISTERS = {'AX', 'BX', 'CX', 'DX', 'SP', 'BP', 'SI', 'DI'}
    MAX_VAL = 0xFFFF
    SIGN_BIT = 0x8000

    def __init__(self):
        self.registers = {r: 0 for r in self.REGISTERS}
        self.memory = {}
        self.stack = []
        self.flags = {
            'ZF': 0,
            'CF': 0,
            'SF': 0,
            'OF': 0,
        }

    def _update_flags(self, result, operand_a=None, operand_b=None, operation='add'):
        unsigned_result = result & self.MAX_VAL
        self.flags['ZF'] = 1 if unsigned_result == 0 else 0
        self.flags['SF'] = 1 if (unsigned_result & self.SIGN_BIT) else 0
        self.flags['CF'] = 1 if (result > self.MAX_VAL or result < 0) else 0
        if operand_a is not None and operand_b is not None:
            a_sign = (operand_a & self.SIGN_BIT)
            b_sign = (operand_b & self.SIGN_BIT) if operation == 'add' else (~operand_b & self.SIGN_BIT)
            r_sign = (unsigned_result & self.SIGN_BIT)
            self.flags['OF'] = 1 if (a_sign == b_sign and a_sign != r_sign) else 0
        else:
            self.flags['OF'] = 0

    def _resolve_address(self, token):
        token = token.strip().upper()
        if token in self.registers:
            return self.registers[token]
        return int(token, 0)

    def _get_value(self, token):
        upper = token.upper()
        if upper in self.registers:
            return self.registers[upper]
        if upper.startswith('[') and upper.endswith(']'):
            addr = self._resolve_address(token[1:-1])
            return self.memory.get(addr, 0)
        return int(token, 0)

    def _set_destination(self, dest, value):
        dest_upper = dest.upper()
        value = value & self.MAX_VAL
        if dest_upper in self.registers:
            self.registers[dest_upper] = value
        elif dest_upper.startswith('[') and dest_upper.endswith(']'):
            addr = self._resolve_address(dest[1:-1])
            self.memory[addr] = value
        else:
            raise ValueError(f"Invalid destination: '{dest}'")

    def execute_instruction(self, instruction):
        instruction = instruction.split(';')[0].strip()
        if not instruction:
            return None

        parts = instruction.replace(',', ' ').split()
        opcode = parts[0].upper()

        try:
            if opcode == 'MOV':
                self._set_destination(parts[1], self._get_value(parts[2]))

            elif opcode == 'ADD':
                a = self._get_value(parts[1])
                b = self._get_value(parts[2])
                result = a + b
                self._update_flags(result, a, b, 'add')
                self._set_destination(parts[1], result)

            elif opcode == 'SUB':
                a = self._get_value(parts[1])
                b = self._get_value(parts[2])
                result = a - b
                self._update_flags(result, a, b, 'sub')
                self._set_destination(parts[1], result)

            elif opcode == 'MUL':
                src = self._get_value(parts[1])
                result = self.registers['AX'] * src
                self.flags['CF'] = self.flags['OF'] = 1 if result > self.MAX_VAL else 0
                self._set_destination('AX', result)

            elif opcode == 'DIV':
                src = self._get_value(parts[1])
                if src == 0:
                    print("  [!] DIVIDE ERROR: Division by zero.")
                    return None
                self._set_destination('AX', self.registers['AX'] // src)
                self.flags['ZF'] = 1 if self.registers['AX'] == 0 else 0

            elif opcode == 'AND':
                a = self._get_value(parts[1])
                b = self._get_value(parts[2])
                result = a & b
                self._update_flags(result)
                self.flags['CF'] = self.flags['OF'] = 0
                self._set_destination(parts[1], result)

            elif opcode == 'OR':
                a = self._get_value(parts[1])
                b = self._get_value(parts[2])
                result = a | b
                self._update_flags(result)
                self.flags['CF'] = self.flags['OF'] = 0
                self._set_destination(parts[1], result)

            elif opcode == 'XOR':
                a = self._get_value(parts[1])
                b = self._get_value(parts[2])
                result = a ^ b
                self._update_flags(result)
                self.flags['CF'] = self.flags['OF'] = 0
                self._set_destination(parts[1], result)

            elif opcode == 'NOT':
                a = self._get_value(parts[1])
                self._set_destination(parts[1], (~a) & self.MAX_VAL)

            elif opcode == 'CMP':
                a = self._get_value(parts[1])
                b = self._get_value(parts[2])
                self._update_flags(a - b, a, b, 'sub')

            elif opcode == 'JMP':
                return parts[1]

            elif opcode in ('JZ', 'JE'):
                if self.flags['ZF'] == 1:
                    return parts[1]

            elif opcode in ('JNZ', 'JNE'):
                if self.flags['ZF'] == 0:
                    return parts[1]

            elif opcode == 'JG':
                if self.flags['ZF'] == 0 and self.flags['SF'] == self.flags['OF']:
                    return parts[1]

            elif opcode == 'JL':
                if self.flags['SF'] != self.flags['OF']:
                    return parts[1]

            elif opcode == 'PUSH':
                self.stack.append(self._get_value(parts[1]))

            elif opcode == 'POP':
                if not self.stack:
                    print("  [!] STACK ERROR: Stack is empty.")
                    return None
                self._set_destination(parts[1], self.stack.pop())

            elif opcode == 'NOP':
                pass

            else:
                print(f"  [!] ERROR: Unknown instruction '{opcode}'")

        except IndexError:
            print(f"  [!] SYNTAX ERROR: Too few operands in '{instruction}'")
        except ValueError as e:
            print(f"  [!] VALUE ERROR in '{instruction}': {e}")
        except Exception as e:
            print(f"  [!] ERROR in '{instruction}': {e}")

        return None

    # ------------------------------------------------------------------
    # Program execution mode
    # ------------------------------------------------------------------

    def run_program(self, source):
        """
        Execute a multi-line assembly program.
        Supports labels (e.g. 'LOOP:') as jump targets.
        Detects infinite loops (> 10,000 cycles).
        """
        lines = [l.strip() for l in source.strip().splitlines()]

        # First pass: index all labels
        labels = {}
        clean_lines = []
        for line in lines:
            stripped = line.split(';')[0].strip()
            if not stripped:
                continue
            if stripped.endswith(':'):
                labels[stripped[:-1].upper()] = len(clean_lines)
            else:
                clean_lines.append(stripped)

        # Second pass: execute
        ip = 0
        cycle_count = 0
        MAX_CYCLES = 10_000

        print(f"\n  Running program ({len(clean_lines)} instructions)...\n")

        while ip < len(clean_lines):
            if cycle_count >= MAX_CYCLES:
                print(f"  [!] HALTED: Exceeded {MAX_CYCLES} cycles. Possible infinite loop.")
                break

            instruction = clean_lines[ip]
            jump_target = self.execute_instruction(instruction)
            cycle_count += 1

            if jump_target:
                target = jump_target.upper()
                if target not in labels:
                    print(f"  [!] JUMP ERROR: Label '{target}' not defined.")
                    break
                ip = labels[target]
            else:
                ip += 1

        print(f"\n  Program completed in {cycle_count} cycle(s).")

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def dump_registers(self):
        print("+------------------------------------------+")
        print("|         8086 REGISTER STATE              |")
        print("+--------+---------+-----------------------+")
        print("| REG    |   HEX   |       DECIMAL         |")
        print("+--------+---------+-----------------------+")
        for reg, val in self.registers.items():
            val = val & self.MAX_VAL
            print(f"| {reg:<6} | {val:04X}h    | {val:<21} |")
        print("+------------------------------------------+")

    def dump_flags(self):
        print("+------------------------------------------+")
        print("|            FLAG REGISTER                 |")
        print("+--------+---------------------------------+")
        descriptions = {
            'ZF': 'Zero Flag    (result was zero)',
            'CF': 'Carry Flag   (unsigned overflow)',
            'SF': 'Sign Flag    (result negative)',
            'OF': 'Overflow Flag(signed overflow)',
        }
        for flag, val in self.flags.items():
            state = "SET  [1]" if val else "CLEAR[0]"
            print(f"| {flag} | {state}  {descriptions[flag]:<28} |")
        print("+------------------------------------------+\n")

    def dump_memory(self, start=0, end=16):
        print(f"\n  Memory [{start:04X}h — {end:04X}h]:")
        any_written = False
        for addr in range(start, end + 1):
            val = self.memory.get(addr, None)
            if val is not None:
                print(f"    [{addr:04X}h] = {val:04X}h  (Dec: {val})")
                any_written = True
        if not any_written:
            print("    (empty)")
        print()


# ----------------------------------------------------------------------
# CLI Shell
# ----------------------------------------------------------------------

HELP_TEXT = """
  AVAILABLE COMMANDS
  ------------------
  MOV  dest, src       — Move value into register or memory
  ADD  dest, src       — Add src to dest, update flags
  SUB  dest, src       — Subtract src from dest, update flags
  MUL  src             — Multiply AX by src
  DIV  src             — Divide AX by src
  AND  dest, src       — Bitwise AND
  OR   dest, src       — Bitwise OR
  XOR  dest, src       — Bitwise XOR
  NOT  dest            — Bitwise NOT
  CMP  a, b            — Compare (sets flags, no write)
  JMP  label           — Unconditional jump (use in RUN mode)
  JZ/JE   label        — Jump if Zero Flag set
  JNZ/JNE label        — Jump if Zero Flag clear
  JG   label           — Jump if greater
  JL   label           — Jump if less
  PUSH src             — Push value onto stack
  POP  dest            — Pop value from stack
  NOP                  — No operation

  Memory syntax:        MOV [1000], AX  |  MOV AX, [BX]  |  MOV [0xFF], 42
  Hex immediates:       MOV AX, 0xFF

  SHELL COMMANDS
  --------------
  FLAGS    — Show flag register state
  MEMORY   — Show non-zero memory contents
  RESET    — Reset CPU to initial state
  RUN      — Enter program mode (multi-line, type END to execute)
  HELP     — Show this message
  EXIT     — Quit emulator
"""

def run_shell():
    cpu = Microprocessor8086()

    print("\n" + "=" * 50)
    print("   INTEL 8086 EMULATOR  v2.0")
    print("   Type HELP for commands. EXIT to quit.")
    print("=" * 50 + "\n")
    cpu.dump_registers()

    while True:
        try:
            cmd = input("8086> ").strip()
            if not cmd or cmd.startswith(';'):
                continue

            upper = cmd.upper()

            if upper == 'EXIT':
                print("  Powering down CPU. Goodbye.")
                break

            elif upper == 'RESET':
                cpu = Microprocessor8086()
                print("\n  [!] CPU Reset to Initial State.\n")
                cpu.dump_registers()

            elif upper == 'FLAGS':
                cpu.dump_flags()

            elif upper == 'MEMORY':
                cpu.dump_memory()

            elif upper == 'HELP':
                print(HELP_TEXT)

            elif upper == 'RUN':
                print("  Program mode — enter instructions line by line.")
                print("  Use labels ending with ':' for jump targets (e.g. LOOP:).")
                print("  Type END on a new line to execute.\n")
                program_lines = []
                while True:
                    line = input("  ... ").strip()
                    if line.upper() == 'END':
                        break
                    program_lines.append(line)
                if program_lines:
                    cpu.run_program('\n'.join(program_lines))
                    cpu.dump_registers()
                    cpu.dump_flags()
                else:
                    print("  No instructions entered.")

            else:
                cpu.execute_instruction(cmd)
                cpu.dump_registers()
                cpu.dump_flags()

        except KeyboardInterrupt:
            print("\n  Powering down CPU. Goodbye.")
            break


if __name__ == "__main__":
    # Optional: pass a .asm file as argument to run directly
    # Usage: python cpu_simulator.py program.asm
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                source = f.read()
            cpu = Microprocessor8086()
            cpu.run_program(source)
            cpu.dump_registers()
            cpu.dump_flags()
        except FileNotFoundError:
            print(f"  [!] File not found: {sys.argv[1]}")
    else:
        run_shell()
