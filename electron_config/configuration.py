import sys

def get_subshells(num_electrons):
    subshells = []
    diag = -1
    k = 0
    while num_electrons > 0:
        if k >= (diag // 2) + 1:
            diag += 1
            k = 0
        pqn = (diag // 2) + (diag % 2) + k
        aqn = (diag // 2) - k
        subshells.append((pqn, aqn, min(4 * aqn + 2, num_electrons)))
        num_electrons -= 4 * aqn + 2
        k += 1
    return subshells

def format_config(subshells, order="energy"):
    orbitals = ("s", "p", "d", "f", "g", "h", "i", "k")
    utf8_superscripts = {0: "\u2070", 1: "\u00b9", 2: "\u00b2", 3: "\u00b3",
            4: "\u2074", 5: "\u2075", 6: "\u2076", 7: "\u2077",
            8: "\u2078", 9: "\u2079"}
    config = []
    
    if order == "number":
        subshells.sort(key=lambda elem: (elem[0], elem[1]))

    for pqn, aqn, electrons in subshells:
        formatted = "{}{}".format(pqn + 1, orbitals[aqn])
        for digit in str(electrons):
            formatted += utf8_superscripts[int(digit)]
        config.append(formatted)
    return "".join(config)

def noble(k):
    """
    Return the atomic number of the kth noble gas (He=1, Ne=2, Ar=3, ...).
    See README for derivation.
    """
    def f(x):
        return ((2 * x * (x + 1) * (2 * x + 1)) / 3) - 2
    return int(f(k // 2)) + (2 * (k % 2 + 1) * (k // 2 + 1)**2)

if __name__ == "__main__":
    default_electrons = 10
    if len(sys.argv) > 1:
        electrons = int(sys.argv[1])
    else:
        electrons = default_electrons

    subshells = get_subshells(electrons)
    config = format_config(subshells)
    print(config)
