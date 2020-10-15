C = 2.99792458e8

def highest_power_of_two(val):
    '''
        Rounds a 32 bit value to the next power of two
        From: https://graphics.stanford.edu/~seander/bithacks.html#RoundUpPowerOf2
    '''
    val = int(val)
    val -= 1
    val |= val >> 1
    val |= val >> 2
    val |= val >> 4
    val |= val >> 8
    val |= val >> 16
    val += 1
    return val