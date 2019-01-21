import sys
from noble import noble

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

def format_config(subshells, order="energy", noble_gas=False, separator=""):
    orbitals = ("s", "p", "d", "f", "g", "h", "i", "k", "l", "m", "n")
    noble_gases = {2: "He", 10: "Ne", 18: "Ar", 36: "Kr",
            54: "Xe", 86: "Rn", 118: "Og"}
    utf8_superscripts = {0: "\u2070", 1: "\u00b9", 2: "\u00b2", 3: "\u00b3",
            4: "\u2074", 5: "\u2075", 6: "\u2076", 7: "\u2077",
            8: "\u2078", 9: "\u2079"}
    config = []

    if noble_gas:
        # Determine noble gas with nearest atomic number.
        num_electrons = sum([subshell[2] for subshell in subshells])
        noble_atomic_num = 0
        next_noble_atomic_num = 0
        k = 0
        while next_noble_atomic_num <= num_electrons:
            noble_atomic_num = next_noble_atomic_num
            k += 1
            next_noble_atomic_num = noble(k)
        if noble_atomic_num > 0:
            # Get subshells for the noble gas; remove as many subshells
            # from source list. Add noble gas to config.
            noble_config = get_subshells(noble_atomic_num)
            subshells = subshells[len(noble_config):]
            noble_gas_abbrev = "[{}]".format(
                    noble_gases.get(noble_atomic_num, str(noble_atomic_num)))
            config.append(noble_gas_abbrev)

    if order == "numeric":
        subshells.sort(key=lambda elem: (elem[0], elem[1]))

    for pqn, aqn, electrons in subshells:
        formatted = "{}{}".format(pqn + 1, orbitals[aqn])
        for digit in str(electrons):
            formatted += utf8_superscripts[int(digit)]
        config.append(formatted)
    return separator.join(config)

if __name__ == "__main__":
    default_electrons = 10
    if len(sys.argv) > 1:
        electrons = int(sys.argv[1])
    else:
        electrons = default_electrons

    subshells = get_subshells(electrons)
    config = format_config(subshells, noble_gas=True, order="numeric", separator="")
    print(config)
