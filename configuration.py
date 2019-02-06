import argparse
from collections import namedtuple
from noble import noble

class ElectronConfiguration:

    ELEMENTS = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg",
            "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr",
            "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br",
            "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag",
            "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr",
            "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
            "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb",
            "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu",
            "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db",
            "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv",
            "Ts", "Og"]

    ATOMIC_NUMBERS = {symbol: i + 1 for i, symbol in enumerate(ELEMENTS)}

    NOBLE_GASES = {2: "He", 10: "Ne", 18: "Ar", 36: "Kr",
            54: "Xe", 86: "Rn", 118: "Og"}

    extra_orbitals = [chr(i) for i in range(ord("g"), ord("z") + 1)
        if chr(i) not in ("s", "p", "d", "f", "j")]
    ORBITALS = ["s", "p", "d", "f"] + extra_orbitals

    Subshell = namedtuple("Subshell", ["position", "pqn", "aqn", "electrons"])

    def __init__(self):
        pass

    @classmethod
    def electron_config(cls, input_, charge=0):
        if isinstance(input_, int):
            atomic_num = input_
        elif isinstance(input_, str):
            atomic_num = cls.ATOMIC_NUMBERS[input_]
        #else:
            # throw exception

        if charge <= 0:
            subshells = cls.aufbau_config(atomic_num - charge)
        else:
            subshells = cls.aufbau_config(atomic_num)
            subshells = cls.cation_config(subshells, charge)
        return subshells

    @classmethod
    def aufbau_config(cls, num_electrons):
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

            # Fill the subshell with as many electrons as it can hold or as
            # many electrons remain, whichever is smaller.
            electrons_in_subshell = min(4 * aqn + 2, remaining_electrons)
            subshell = cls.Subshell(position=i, pqn=pqn, aqn=aqn,
                    electrons=electrons_in_subshell)
            subshells.append(subshell)

            remaining_electrons -= 4 * aqn + 2
            i += 1
            j += 1
        return subshells

    @classmethod
    def cation_config(cls, subshells, charge):
        """
        Given a list of subshells from aufbau_config() and a positive ion
        charge, return the electron configuration of the cation by removing
        electrons from the subshells with the highest principal quantum numbers.
        """

        # If charge exceeds total electrons, return blank list.
        if charge >= sum([subshell.electrons for subshell in subshells]):
            return []

        # Sort subshells by principal, then azimuthal, quantum number.
        subshells.sort(key=lambda subshell: (subshell.pqn, subshell.aqn))

        # Iterate in reverse over the sorted list of subshells, removing the
        # necessary electrons from each outermost subshell. Delete subshells
        # that end up without electrons.
        i = len(subshells) - 1
        while charge:
            subshell = subshells[i]
            electrons_to_remove = min(charge, subshell.electrons)
            if electrons_to_remove == subshell.electrons:
                del subshells[i]
            else:
                updated_electrons = subshell.electrons - electrons_to_remove
                updated_subshell = cls.Subshell(position=subshell.position,
                        pqn=subshell.pqn, aqn=subshell.aqn,
                        electrons=updated_electrons)
                subshells[i] = updated_subshell
            charge -= electrons_to_remove
            i -= 1

        # Return list of subshells sorted by Madelung rule energy
        # (i.e., by position in sequence).
        subshells.sort(key=lambda subshell: subshell.position)
        return subshells

    @classmethod
    def noble_config(cls, subshells):
        """
        Given a list of subshells, remove the first N subshells corresponding
        to the configuration of the nearest noble gas, replacing them with the
        atomic number of said noble gas.
        """

        # Correctly format when noble_gas=True and ion charge > 0 (e.g.,
        # eg, Z=93 and charge=2 vs Z=93 and charge=4.

        num_electrons = sum([subshell.electrons for subshell in subshells])

        k = 0
        while noble(k) <= num_electrons:
            k += 1
        k -= 1

        noble_atomic_num = 0
        while k > 0:
            noble_atomic_num = noble(k)
            noble_subshells = cls.aufbau_config(noble_atomic_num)
            if (len(noble_subshells) <= len(subshells) and 
                    subshells[:len(noble_subshells)] == noble_subshells):
                subshells = subshells[len(noble_subshells):]
                break
            k -= 1
        return subshells, noble_atomic_num

    @classmethod
    def format_config(cls, subshells, order="energy", noble_gas=False, delimiter=""):

        UTF8_SUPERSCRIPTS = {0: "\u2070", 1: "\u00b9", 2: "\u00b2",
                3: "\u00b3", 4: "\u2074", 5: "\u2075", 6: "\u2076",
                7: "\u2077", 8: "\u2078", 9: "\u2079"}

        config = []

        if noble_gas:
            subshells, noble_atomic_num = cls.noble_config(subshells)
            noble_gas_abbrev = "[{}]".format(
                    cls.NOBLE_GASES.get(noble_atomic_num, str(noble_atomic_num)))
            config.append(noble_gas_abbrev)

        if order == "numeric":
            subshells.sort(key=lambda subshell: (subshell.pqn, subshell.aqn))

        for subshell in subshells:
            formatted = "{}{}".format(subshell.pqn, cls.ORBITALS[subshell.aqn])
            for digit in str(subshell.electrons):
                formatted += UTF8_SUPERSCRIPTS[int(digit)]
            config.append(formatted)
        return delimiter.join(config)

    @classmethod
    def __call__(cls, input_, charge=0, order="energy", noble_gas=False, delimiter=""):
        subshells = cls.electron_config(input_, charge)
        formatted = cls.format_config(subshells, order, noble_gas, delimiter)
        return formatted

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

    if args["input"].isdigit():
        input_ = int(args["input"])
    else:
        input_ = args["input"]

    config = ElectronConfiguration()
    fmt = config(input_, charge=args["charge"], order=args["order"],
            noble_gas=args["noble"], delimiter=args["delimiter"])
    print(fmt)
