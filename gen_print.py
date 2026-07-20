import sys

def base3_digits(n):
    if n == 0:
        return "0"
    digs = []
    while n > 0:
        digs.append(str(n % 3))
        n //= 3
    return "".join(reversed(digs))

def compile_string(s):
    parts = []
    for ch in s:
        parts.append(base3_digits(ord(ch)))
        parts.append("#")
        parts.append("  ")
        parts.append(",")
    parts.append("@")
    return "".join(parts)

if __name__ == "__main__":
    s = sys.argv[1] if len(sys.argv) > 1 else "Hi"
    print(compile_string(s))
