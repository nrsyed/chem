import sys

def get_subshells(num_electrons):
    """
    Return a list of tuples corresponding to subshells of the element with
    the given number of electrons. Each tuple contains the principle quantum
    number, azimuthal quantum number, and number of electrons in the subshell.
    Subshells are filled per the Madelung rule.
    """
    subshells = []
    diag = -1
    j = 0
    while num_electrons > 0:
        if j >= (diag // 2) + 1:
            diag += 1
            j = 0
        pqn = (diag // 2) + (diag % 2) + j
        aqn = (diag // 2) - j
        subshells.append((pqn, aqn, min(4 * aqn + 2, num_electrons)))
        num_electrons -= 4 * aqn + 2
        j += 1
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
    Return the atomic number of the kth noble gas, where k=1 is He,
    k=2 is Ne, etc. See README for derivation.
    """
    prev_pairs = int((2 * (k // 2) * (k // 2 + 1) * (2 * (k // 2) + 1)) / 3) - 2
    return prev_pairs + (2 * (k % 2 + 1) * (k // 2 + 1)**2)

if __name__ == "__main__":
    default_electrons = 10
    if len(sys.argv) > 1:
        electrons = int(sys.argv[1])
    else:
        electrons = default_electrons

    subshells = get_subshells(electrons)
    config = format_config(subshells)
    print(config)
