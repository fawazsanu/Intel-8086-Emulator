import sys

class Microprocessor8086:
    """
    A software emulator for the Intel 8086 microprocessor.

    Supports:
    - General-purpose registers: AX, BX, CX, DX
    - Segment/pointer registers: SP, BP, SI, DI
    - Flag Register: Zero Flag (ZF), Carry Flag (CF), Sign Flag (SF), Overflow Flag (OF)
    - Instructions: MOV, ADD, SUB, MUL, DIV, AND, OR, XOR, NOT, PUSH, POP, NOP
    """

    REGISTERS = {'AX', 'BX', 'CX', 'DX', 'SP', 'BP', 'SI', 'DI'}
    MAX_VAL = 0xFFFF
    SIGN_BIT = 0x8000

    def __init__(self):
        self.registers = {r: 0 for r in self.REGISTERS}
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

    def _get_value(self, token):
        upper = token.upper()
        if upper in self.registers:
            return self.registers[upper]
        return int(token, 0)

    def _set_destination(self, dest, value):
        dest = dest.upper()
        value = value & self.MAX_VAL
        if dest in self.registers:
            self.registers[dest] = value
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

            # --- Logic instructions ---
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


HELP_TEXT = """
  AVAILABLE COMMANDS
  ------------------
  MOV  dest, src  — Move value into register
  ADD  dest, src  — Add src to dest, update flags
  SUB  dest, src  — Subtract src from dest, update flags
  MUL  src        — Multiply AX by src
  DIV  src        — Divide AX by src
  AND  dest, src  — Bitwise AND
  OR   dest, src  — Bitwise OR
  XOR  dest, src  — Bitwise XOR
  NOT  dest       — Bitwise NOT
  PUSH src        — Push value onto stack
  POP  dest       — Pop value from stack
  NOP             — No operation

  SHELL COMMANDS
  --------------
  FLAGS  — Show flag register state
  RESET  — Reset CPU to initial state
  HELP   — Show this message
  EXIT   — Quit emulator
"""

def run_shell():
    cpu = Microprocessor8086()
    print("\n" + "=" * 50)
    print("   INTEL 8086 EMULATOR  v1.2")
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
                print("\n  [!] CPU Reset.\n")
                cpu.dump_registers()
            elif upper == 'FLAGS':
                cpu.dump_flags()
            elif upper == 'HELP':
                print(HELP_TEXT)
            else:
                cpu.execute_instruction(cmd)
                cpu.dump_registers()
                cpu.dump_flags()
        except KeyboardInterrupt:
            print("\n  Powering down CPU. Goodbye.")
            break

if __name__ == "__main__":
    run_shell()
