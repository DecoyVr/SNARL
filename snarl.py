#!/usr/bin/env python3
"""
SNARL interpreter (Self-Nullifying Anachronistic Rotational Language)

Usage:
    python3 snarl.py program.snarl [--trace] [--max-steps N]
"""
import sys

CHARSET = " 012#><^v?+-*/%~@.,:!X"  # index -> instruction, used by X (self-modify)
DECAY_LIMIT = 5
DECAYING = set(">^v<?+-*/%~@.,:!X")  # these erase themselves after DECAY_LIMIT executions
DEFAULT_MAX_STEPS = 2_000_000


def load_grid(path):
    with open(path) as f:
        text = f.read()
    lines = text.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    if not lines:
        lines = [" "]
    width = max(len(l) for l in lines)
    grid = [list(l.ljust(width)) for l in lines]
    return grid


def run(path, max_steps=DEFAULT_MAX_STEPS, trace=False):
    grid = load_grid(path)
    h = len(grid)
    w = len(grid[0])
    durability = [[DECAY_LIMIT] * w for _ in range(h)]

    x, y = 0, 0
    dx, dy = 1, 0
    phase = 0
    stacks = [[], [], []]
    acc = 0
    out = []

    steps = 0
    while steps < max_steps:
        steps += 1
        ch = grid[y][x]
        active = stacks[phase]

        def pop():
            return active.pop() if active else 0

        if ch in "012":
            acc = acc * 3 + int(ch)
        elif ch == '#':
            active.append(acc)
            acc = 0
        elif ch == '>':
            dx, dy = 1, 0
        elif ch == '<':
            dx, dy = -1, 0
        elif ch == '^':
            dx, dy = 0, -1
        elif ch == 'v':
            dx, dy = 0, 1
        elif ch == '?':
            v = pop()
            if v == 0:
                dx, dy = -dy, dx   # turn clockwise
            else:
                dx, dy = dy, -dx   # turn counter-clockwise
        elif ch in '+-*/%':
            b = pop(); a = pop()
            if ch == '+':
                r = a + b
            elif ch == '-':
                r = a - b
            elif ch == '*':
                r = a * b
            elif ch == '/':
                r = a // b if b != 0 else 0
            else:
                r = a % b if b != 0 else 0
            active.append(r)
        elif ch == '~':
            v = pop()
            stacks[(phase + 1) % 3].append(v)
        elif ch == ':':
            v = pop()
            active.append(v)
            active.append(v)
        elif ch == '!':
            pop()
        elif ch == '.':
            v = pop()
            out.append(str(v))
        elif ch == ',':
            v = pop()
            out.append(chr(v % 0x110000))
        elif ch == 'X':
            v = pop()
            tx, ty = (x + dx) % w, (y + dy) % h
            newch = CHARSET[v % len(CHARSET)]
            grid[ty][tx] = newch
            durability[ty][tx] = DECAY_LIMIT
        elif ch == '@':
            if trace:
                sys.stderr.write(f"step={steps} pos=({x},{y}) ch='@' HALT\n")
            break
        # space / unknown char -> no-op

        if ch in DECAYING:
            durability[y][x] -= 1
            if durability[y][x] <= 0:
                grid[y][x] = ' '

        if trace:
            sys.stderr.write(
                f"step={steps} pos=({x},{y}) ch={ch!r} phase={phase} "
                f"stacks={stacks} acc={acc} dir=({dx},{dy})\n"
            )

        x = (x + dx) % w
        y = (y + dy) % h
        phase = (phase + 1) % 3

    return ''.join(out)


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print("usage: snarl.py <file.snarl> [--trace] [--max-steps N]")
        sys.exit(1)
    trace = '--trace' in args
    max_steps = DEFAULT_MAX_STEPS
    if '--max-steps' in args:
        i = args.index('--max-steps')
        max_steps = int(args[i + 1])
    path = [a for a in args if not a.startswith('--') and a != str(max_steps)][0]
    result = run(path, max_steps=max_steps, trace=trace)
    sys.stdout.write(result)
