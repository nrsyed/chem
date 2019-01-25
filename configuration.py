import argparse
import sys
from noble import noble

def ground_state(atomic_num):
    """
    Return a list of tuples corresponding to subshells of the element with
    the given number of electrons. Each tuple contains the principle quantum
    number, azimuthal quantum number, and number of electrons in the subshell.
    Subshells are filled per the Madelung rule.
    """

    remaining_electrons = atomic_num
    subshells = []
    diag = -1
    j = 0
    while remaining_electrons > 0:
        if j > (diag // 2):
            diag += 1
            j = 0
        pqn = (diag // 2) + (diag % 2) + 1 + j
        aqn = (diag // 2) - j
        subshells.append((pqn, aqn, min(4 * aqn + 2, remaining_electrons)))
        remaining_electrons -= 4 * aqn + 2
        j += 1
    return subshells

def format_config(subshells, order="energy", noble_gas=False, delimiter=""):
    ORBITALS = ("s", "p", "d", "f", "g", "h", "i", "k", "l", "m", "n")
    NOBLE_GASES = {2: "He", 10: "Ne", 18: "Ar", 36: "Kr",
            54: "Xe", 86: "Rn", 118: "Og"}
    UTF8_SUPERSCRIPTS = {0: "\u2070", 1: "\u00b9", 2: "\u00b2", 3: "\u00b3",
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
            noble_config = ground_state(noble_atomic_num)
            subshells = subshells[len(noble_config):]
            noble_gas_abbrev = "[{}]".format(
                    NOBLE_GASES.get(noble_atomic_num, str(noble_atomic_num)))
            config.append(noble_gas_abbrev)

    if order == "numeric":
        subshells.sort(key=lambda elem: (elem[0], elem[1]))

    for pqn, aqn, electrons in subshells:
        formatted = "{}{}".format(pqn, ORBITALS[aqn])
        for digit in str(electrons):
            formatted += UTF8_SUPERSCRIPTS[int(digit)]
        config.append(formatted)
    return delimiter.join(config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Element or number of electrons")
    parser.add_argument("-o", "--order", default="energy",
            help="Order in which to print subshells: 'energy' (default; in\
                    order of increasing energy) or 'numeric' (in order of\
                    increasing quantum number)")
    parser.add_argument("-n", "--noble", action="store_true",
            help="Use noble gas notation")
    parser.add_argument("-c", "--charge", type=int, default=0,
            help="Atom charge (default 0)")
    parser.add_argument("-d", "--delimiter", default="",
            help="Character separating printed subshells (default none)")

    args = vars(parser.parse_args())
