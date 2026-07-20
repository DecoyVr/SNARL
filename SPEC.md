# SNARL Language Specification

**SNARL** — *Self-Nullifying Anachronistic Rotational Language*

SNARL is a genuinely Turing-complete esoteric programming language. It runs,
it's testable, and it will actively fight you the whole way. Two mechanics
make it brutal:

1. **Rotational phase.** There is a global "phase" counter (0, 1, 2) that
   advances by one on *every single instruction executed* — not tied to
   position, not tied to what the instruction does. Whichever of the
   language's three stacks you touch is decided by `phase`, not by anything
   you wrote. The same `+` character will silently operate on a different
   stack depending on when execution happens to reach it.

2. **Decay.** Most instruction cells wear out. Every time a decaying
   instruction executes, its durability drops by one. At zero, the cell
   erases itself into a no-op space. Loops rot from the inside unless you
   actively rewrite them at runtime with the self-modification instruction.

Nothing here is decorative — every mechanic below is required to write
anything beyond a trivial program, and every example in `examples/` has been
executed against the reference interpreter (`snarl.py`) to confirm it
actually produces the claimed output.

## The Grid

A SNARL program is a rectangular grid of characters (a text file). Shorter
lines are padded with spaces to the width of the longest line. The grid is
**toroidal**: moving off any edge wraps to the opposite edge, in both x and y.

## The Instruction Pointer (IP)

The IP has:
- a position `(x, y)`, starting at `(0, 0)`
- a direction `(dx, dy)`, starting as right `(1, 0)`
- a **phase** `p ∈ {0, 1, 2}`, starting at `0`

Execution is a loop:
1. Read the character at the IP's position.
2. Execute it (see Instruction Set).
3. If the instruction was a *decaying* instruction, reduce that cell's
   durability by 1; if it hits 0, the cell becomes a space permanently.
4. Move the IP by `(dx, dy)`, wrapping at the grid edges.
5. Advance phase: `p = (p + 1) mod 3`.
6. Repeat, until an `@` is executed or the step limit is hit.

## State

- **Three data stacks**: `stack[0]`, `stack[1]`, `stack[2]`, each holding
  signed integers. Popping an empty stack yields `0` rather than crashing.
- **One accumulator register** (`acc`), used only for building numeric
  literals in balanced base-3 digit form.
- The **active stack** for any instruction that reads/writes a stack is
  always `stack[phase]` — i.e. determined by the phase *at the moment that
  instruction executes*, not by anything written in the source.

## Numeric Literals

There are no multi-digit number tokens. Numbers are built digit-by-digit in
**base 3**:

- `0`, `1`, `2` — each shifts the accumulator: `acc = acc*3 + digit`
- `#` — pushes `acc` onto the active stack (`stack[phase]`) and resets
  `acc` to 0

Example: `2102#` pushes 65 (`'A'`), because `2*27 + 1*9 + 0*3 + 2 = 65`.
Digits and `#` never decay — they're the one part of SNARL that's actually
reliable, because you'll be using them constantly to rebuild everything else.

## Instruction Set

| Char | Decays? | Effect |
|------|---------|--------|
| `0` `1` `2` | no | shift into accumulator (base-3 digit) |
| `#` | no | push accumulator onto `stack[phase]`, reset accumulator to 0 |
| `>` `<` `^` `v` | yes | set direction to right / left / up / down |
| `?` | yes | pop `stack[phase]`; if 0, turn direction 90° clockwise, else 90° counter-clockwise |
| `+` `-` `*` `/` `%` | yes | pop b, pop a from `stack[phase]`; push `a OP b` back onto `stack[phase]` (division/modulo by 0 yields 0) |
| `~` | yes | pop `stack[phase]`, push it onto `stack[(phase+1) mod 3]` |
| `:` | yes | duplicate top of `stack[phase]` |
| `!` | yes | discard top of `stack[phase]` |
| `.` | yes | pop `stack[phase]`, output as a decimal integer |
| `,` | yes | pop `stack[phase]`, output as a character (by code point) |
| `X` | yes | pop `stack[phase]` as `v`; write `CHARSET[v mod 23]` into the cell one step ahead of the IP (in its current direction), and reset that cell's durability to 5 |
| ` ` (space) | no | no-op |
| anything else | no | no-op (undefined characters are inert) |
| `@` | — | halt immediately |

`CHARSET` (used only by `X`, index → character) is:
```
index:  0123456789...
chars:  " 012#><^v?+-*/%~@.,:!X"
```
So `X` can write literally any SNARL instruction, including another `X`,
into the grid at runtime. This is the only way to repair decayed cells or
to build code that didn't exist when the program started.

**Decay limit:** every decaying instruction starts with durability 5. It
survives 5 executions and erases on what would have been its 6th.

## Why This Is Hard

- You cannot reason about a `+`, `-`, `?`, or any stack-touching instruction
  in isolation — its target stack depends on the parity of *everything that
  ran before it*, including padding spaces.
- The reliable trick: if a "producer" (e.g. `#`) and a "consumer" (e.g. `,`)
  of the same stack value are separated by a number of executed cells that
  is a multiple of 3, they will always land on the same phase and therefore
  the same stack — regardless of where in the program they sit. Padding with
  spaces is not cosmetic in SNARL; it's how you route data.
- Loops rot. A naive loop body that outputs a character every pass will
  silently stop outputting after 5 iterations, with no error — the `,` cell
  just isn't there anymore. Long-running loops are only possible if the
  program uses `X` to rewrite its own decaying cells before they expire.
- There are no named variables, no functions, no labels — only stacks
  selected by a counter you don't control directly, and a grid you must
  edit while it's running.

## Files

- `snarl.py` — reference interpreter
- `gen_print.py` — a tiny compiler: turns an ASCII string into SNARL source
  that prints it (handles the phase-alignment bookkeeping for you)
- `examples/` — verified working programs, see `README.md`
