base, hard, soft_from = 0.066, 10, 7
def p_at(n: int) -> float:
    if n <= soft_from:
        return base
    return base + (1 - base) * (n - soft_from) / (hard - soft_from)
survive = 1.0
f = []
for n in range(1, hard + 1):
    p = p_at(n)
    f.append(survive * p)
    survive *= 1 - p
expected = sum(n * fk for n, fk in enumerate(f, start=1))
consolidated = 1 / expected
print(consolidated)