import numpy as np
from math import factorial
import itertools
import numba as nb

# Precompute factorial values up to 19 and store them in a NumPy array
FACTORIAL_TABLE = np.zeros(20)
for x in range(len(FACTORIAL_TABLE)):
    FACTORIAL_TABLE[x] = factorial(x)


@nb.njit()
def states(n):
    """
    Calculate the number of states with equal numbers of +1 and -1 elements.

    Parameters:
    n (int): number of elements.

    Returns:
    int: The number of states.
    """
    # Possible state on each place: -1, 0, +1.
    # Find the number of states that contain an equal number of -1 and +1,
    # excluding states that consist entirely of zeros

    # Calculate the total number of places
    l = n * 4
    states_number = 0

    # Iterate over possible values of 'm', the number of +1 or -1
    for m in range(1, 2 * n + 1):
        # Calculate the number of zeros
        z = l - 2 * m

        # Use the formula to calculate the microstates number
        mic_num = FACTORIAL_TABLE[l] / (FACTORIAL_TABLE[z] * FACTORIAL_TABLE[m] ** 2)

        # Accumulate microstates to obtain total states
        states_number += mic_num

    return int(states_number)


def micro_states(n):
    assert n <= 4
    l = 4 * n
    state = [0, 1, -1]
    q = np.zeros(4 * len(n))
    q[::2] = 2
    q[1::2] = 3
    c = np.zeros(4 * len(n))
    a = np.zeros(4 * len(n))
    a[:2 * len(n)] = 1
    b = np.zeros(4 * len(n))
    b[2 * len(n):] = 1
    for i in range(len(n)):
        c[[2 * i, 2 * i + 1, len(n) + 2 * i, len(n) + 2 * i + 1]] = n[i]
    valid_comb = []
    for comb in itertools.product(state, repeat=l):
        comb = np.array(comb)
        if check_conditions(comb, l, q, a, b):
            valid_comb.append(comb)
    return np.asarray(valid_comb)


def micro_states_v2(n: int):
    assert n <= 5
    state = np.asarray([0, 1, -1], int)
    tuples_count = np.prod(n * 4 * [3], dtype=np.float64)
    q = np.zeros(4 * n)
    q[::2] = 2
    q[1::2] = 3
    a = np.zeros(4 * n)
    a[:2 * n] = 1
    b = np.zeros(4 * n)
    b[2 * n:] = 1

    c = np.zeros((n, 4 * n))
    for i in range(n):
        c[i, [2 * i, 2 * i + 1, 2 * (i + n), 2 * (i + n) + 1]] = 1

    return micro_states_namba(n, state, tuples_count, q, a, b, c)


@nb.njit()
def micro_states_namba(n, state, tuples_count, q, a, b, c):
    size = 4 * n
    counter = 0
    # stores the current combination
    current_tuple = np.zeros(size, dtype=np.int32)
    while counter < tuples_count:
        current_tuple[0] += 1
        # using a condition here instead of including this in the inner loop
        # to gain a bit of speed: this is going to be tested each iteration,
        # and starting a loop to have it end right away is a bit silly
        if current_tuple[0] == len(state):
            # the reset to 0 and subsequent increment amount to carrying
            # the number to the higher "power"
            current_tuple[0] = 0
            current_tuple[1] += 1
            for i in range(1, size - 1):
                if current_tuple[i] == len(state):
                    # same as before, but in a loop, since this is going
                    # to get run less often
                    current_tuple[i + 1] += 1
                    current_tuple[i] = 0
                else:
                    break
        if check_conditions(state[current_tuple], size, q, a, b, c):
            yield state[current_tuple], counter
        counter += 1


@nb.njit()
def check_conditions(array, size, q, a, b, c):
    """
    Check conditions for a given microstate array.

    Parameters:
    array (numpy.ndarray): Microstate array.
    size (int): Total number of places.
    q (numpy.ndarray): Array 'q' for conditions.
    a (numpy.ndarray): Array 'a' for conditions.
    b (numpy.ndarray): Array 'b' for conditions.
    c (numpy.ndarray): Array 'c' for conditions.

    Returns:
    bool: True if conditions are satisfied, False otherwise.
    """
    ones = np.count_nonzero(array == 1)
    neg_ones = np.count_nonzero(array == -1)
    zeros = np.count_nonzero(array == 0)
    q_check = np.sum(array * q)
    a_check = np.sum(array * a)
    b_check = np.sum(array * b)
    c_check = np.sum(array * c, axis=1)
    if ones == neg_ones and zeros != size:
        return q_check == 0 and a_check == 0 and b_check == 0 and (c_check == 0).all()
    else:
        return False
