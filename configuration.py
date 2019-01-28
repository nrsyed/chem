import argparse
from collections import namedtuple
from noble import noble

Subshell = namedtuple("Subshell", ["position", "pqn", "aqn", "electrons"])

def aufbau_config(num_electrons):
    """
    Return a list of tuples corresponding to subshells of the element with
    the given number of electrons. Each tuple contains the principle quantum
    number, azimuthal quantum number, and number of electrons in the subshell.
    Subshells are filled per the Madelung rule.
    """

    remaining_electrons = num_electrons
    subshells = []
    diag = -1
    i = 0   # Loop counter to track position of each subshell in sequence.
    j = 0   # Counter to track progress through diagonals.
    while remaining_electrons > 0:
        if j > (diag // 2):
            diag += 1
            j = 0

        # Compute principal (pqn) and azimuthal (aqn) quantum numbers.
        pqn = (diag // 2) + (diag % 2) + 1 + j
        aqn = (diag // 2) - j

        # Fill the subshell with as many electrons as it can hold or as many
        # electrons remain, whichever is smaller.
        electrons_in_subshell = min(4 * aqn + 2, remaining_electrons)
        subshell = Subshell(position=i, pqn=pqn, aqn=aqn,
                electrons=electrons_in_subshell)
        subshells.append(subshell)

        remaining_electrons -= 4 * aqn + 2
        i += 1
        j += 1
    return subshells

def cation_config(subshells, charge):
    """
    Given a list of subshells from aufbau_config() and a positive ion charge,
    return the electron configuration of the cation by removing electrons
    from the subshells with the highest principal quantum numbers.
    """

    # If charge exceeds total electrons, return blank list.
    if charge >= sum([subshell.electrons for subshell in subshells]):
        return []

    # Sort subshells by principal quantum number, then azimuthal quantum number.
    subshells.sort(key=lambda subshell: (subshell.pqn, subshell.aqn))

    # Iterate in reverse over the sorted list of subshells, removing the
    # necessary electrons from each outermost subshell.
    # Delete subshells that end up without electrons.
    i = len(subshells) - 1
    while charge:
        subshell = subshells[i]
        electrons_to_remove = min(charge, subshell.electrons)
        if electrons_to_remove == subshell.electrons:
            del subshells[i]
        else:
            updated_electrons = subshell.electrons - electrons_to_remove
            updated_subshell = Subshell(position=subshell.position,
                    pqn=subshell.pqn, aqn=subshell.aqn,
                    electrons=updated_electrons)
            subshells[i] = updated_subshell
        charge -= electrons_to_remove
        i -= 1

    # Return list of subshells sorted by Madelung rule energy
    # (i.e., by position in sequence).
    subshells.sort(key=lambda subshell: subshell.position)
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
        num_electrons = sum([subshell.electrons for subshell in subshells])
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
        subshells.sort(key=lambda subshell: (subshell.pqn, subshell.aqn))

    for subshell in subshells:
        formatted = "{}{}".format(subshell.pqn, ORBITALS[subshell.aqn])
        for digit in str(subshell.electrons):
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

    num_electrons = int(args["input"])
    subshells = ground_state(num_electrons)

    if args["charge"] > 0:
        subshells = cation(subshells, args["charge"])

    config = format_config(subshells, order=args["order"],
            noble_gas=args["noble"], delimiter=args["delimiter"])
    print(config)
