import sys

def orbitals(num_electrons):
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

def formatted_config(subshells, order="energy"):
    orbitals = ("s", "p", "d", "f", "g", "h", "i", "k")
    utf8_superscripts = ("\u2070", "\u00b9", "\u00b2", "\u00b3", "\u2074",
            "\u2075", "\u2076", "\u2077", "\u2078", "\u2079")
    config = []
    
    if order == "number":
        subshells.sort(key=lambda elem: (elem[0], elem[1]))

    for pqn, aqn, electrons in subshells:
        formatted = "{}{}".format(pqn + 1, orbitals[aqn])
        for digit in str(electrons):
            formatted += utf8_superscripts[int(digit)]
        config.append(formatted)
    return "".join(config)

if __name__ == "__main__":
    default_electrons = 10
    if len(sys.argv) > 1:
        electrons = int(sys.argv[1])
    else:
        electrons = default_electrons

    subshells = orbitals(electrons)
    config = formatted_config(subshells)
    #config = formatted_config(subshells, order="number")
    print(config)
