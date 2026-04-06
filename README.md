# Intel 8086 Microprocessor Emulator

## Project Overview
This project is a lightweight, interactive software simulator for the Intel 8086 microprocessor. It bridges low-level hardware architecture with high-level software by parsing and executing Assembly language instructions in a virtualized CPU environment.

Built entirely in pure Python, it mimics bare-metal execution without relying on external dependencies, showcasing a deep understanding of memory states, instruction cycles, and hardware registers.

## Key Features
- **Interactive CLI Shell:** Type Assembly commands live and watch the CPU process them instantly.
- **Register State Visualization:** Dynamically tracks and displays general-purpose 16-bit registers (AX, BX, CX, DX) in both Hexadecimal and Decimal formats.
- **Instruction Set Architecture (ISA):** Currently supports core arithmetic and data movement operations (`MOV`, `ADD`, `SUB`) with built-in syntax error handling.
- **Zero Dependencies:** Runs on standard Python with no external libraries required.

## How to Run
Since this project uses pure standard Python, there is no need to install any external packages (no `pip install` required).

1. Clone the repository or download the `cpu_simulator.py` file.
2. Run the script in your terminal:
   ```
   python cpu_simulator.py
3. Once the 8086 shell boots up, try entering some Assembly commands:
      ```
      8086> MOV AX, 500
      8086> MOV BX, 250
      8086> ADD AX, BX
      8086> SUB AX, 100
4. Type RESET to clear the registers or EXIT to power down the virtual CPU.

## Future Roadmap
- Implement memory addressing modes (e.g., MOV AX, [1000]).
- Add the Flag Register (Zero Flag, Carry Flag) to support jump commands (JMP, JZ).
- Expand the instruction set to include logic gates (AND, OR, XOR).
