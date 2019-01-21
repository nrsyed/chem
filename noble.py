def noble(k):
    """
    Return the atomic number of the kth noble gas, where k=1 is He,
    k=2 is Ne, etc. See README for derivation.
    """
    prev_pairs = int((2 * (k // 2) * (k // 2 + 1) * (2 * (k // 2) + 1)) / 3) - 2
    return prev_pairs + (2 * (k % 2 + 1) * (k // 2 + 1)**2)
