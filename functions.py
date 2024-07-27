import numpy as np


## find cation distribution based on magnetic moment
def calculate_mue(cations_content, mue):
    with open('Data/Temp/precision', 'r') as precision_file:
        prec = precision_file.read().split('=')[1]
        prec = int(prec)
    site_a = np.arange(0, cations_content.size // 2)
    site_b = np.arange(cations_content.size // 2, cations_content.size)
    mue_a = np.sum((mue * cations_content)[site_a])
    mue_b = np.sum((mue * cations_content)[site_b])
    return np.round(mue_b - mue_a, prec)


def find_dist_moment(cation_dist, mue, moment, maxitiration=10000, tol=0.01):
    with open('Data/Temp/precision', 'r') as precision_file:
        prec = precision_file.read().split('=')[1]
        prec = int(prec)
    current_value = calculate_mue(cation_dist, mue)
    diff_save = None
    for _ in np.arange(maxitiration):
        diff = moment - current_value
        if diff_save is not None and np.abs(diff - diff_save) < 1e-10:
            for zstate in zero_exchange('u'):
                if (np.round(cation_dist + zstate, prec) >= 0).all():
                    cation_dist = np.round(cation_dist + zstate, prec)
                    break
        if diff != 0:
            for state in exchange(diff, 'u'):
                if (np.round(cation_dist + state, prec) >= 0).all():
                    cation_dist = np.round(cation_dist + state, prec)
                    break
        current_value = calculate_mue(cation_dist, mue)
        diff_save = diff
        if np.abs(current_value - moment) <= tol:
            break
    return cation_dist


## find cation distribution based on lattice parameter
def calculate_a(cations_content, r, Ro):
    with open('Data/Temp/precision', 'r') as precision_file:
        prec = precision_file.read().split('=')[1]
        prec = int(prec)
    site_a = np.arange(0, cations_content.size // 2)
    site_b = np.arange(cations_content.size // 2, cations_content.size)

    ra = np.sum((r * cations_content)[site_a])
    rb = np.sum((r * cations_content)[site_b]) / 2
    return np.round(8 / (3 * np.sqrt(3)) * ((ra + Ro) + np.sqrt(3) * (rb + Ro)), prec)


def find_dist_a(cation_dist, r, Ro, a, maxitiration=10000, tol=0.01):
    with open('Data/Temp/precision', 'r') as precision_file:
        prec = precision_file.read().split('=')[1]
        prec = int(prec)
    current_value = calculate_a(cation_dist, r, Ro)
    diff_save = None
    for _ in np.arange(maxitiration):
        diff = a - current_value
        if diff_save is not None and np.abs(diff - diff_save) < 1e-10:
            zero_counter = 0
            for zstate in zero_exchange('r'):
                zero_counter += 1
                if (np.round(cation_dist + zstate, prec) >= 0).all():
                    cation_dist = np.round(cation_dist + zstate, prec)
                    break
            if zero_counter == 0:
                for state in exchange(diff, 'r', counter):
                    if (np.round(cation_dist + state, prec) >= 0).all():
                        cation_dist = np.round(cation_dist + state, prec)
                        break
        if np.abs(diff) > tol:
            counter = 0
            for state in exchange(diff, 'r'):
                counter += 1
                if (np.round(cation_dist + state, prec) >= 0).all():
                    cation_dist = np.round(cation_dist + state, prec)
                    break
        current_value = calculate_a(cation_dist, r, Ro)
        diff_save = diff
        if np.abs(current_value - a) <= tol:
            break
    return cation_dist


def find_dist(cation_dist, mue, momemt, r, Ro, a, maxitiration=10000, tol=0.01):
    with open('Data/Temp/precision', 'r') as precision_file:
        prec = precision_file.read().split('=')[1]
        prec = int(prec)
    current_a = calculate_a(cation_dist, r, Ro)
    current_u = calculate_mue(cation_dist, mue)
    for _ in np.arange(maxitiration):
        diff_a = a - current_a
        diff_u = momemt - current_u
        if np.abs(diff_a) * np.abs(diff_u) > tol ** 2:
            counter = 0
            for state in exchange([diff_a, diff_u], 'ru'):
                counter += 1
                if (np.round(cation_dist + state, prec) >= 0).all():
                    cation_dist = np.round(cation_dist + state, prec)
                    break
        current_a = calculate_a(cation_dist, r, Ro)
        current_u = calculate_mue(cation_dist, mue)
        if np.abs(current_a - a) * np.abs(current_u - momemt) <= tol**2:
            break
    return cation_dist


def exchange(diff, type, skip=0):
    with open(f'Data/Temp/exchange_{type}.dat', 'r') as exch:
        content = exch.readline()
        while skip > 0:
            content = exch.readline()
            skip -= 1
        while content:
            try:
                state, value = content.split(';')
                value = float(value)
                if np.abs(value) <= np.abs(diff) and value * diff >= 0:
                    state = eval(state)
                    state = np.array(state)
                    yield state
            except ValueError:
                state, value_a, value_u = content.split(';')
                value_a, value_u = float(value_a), float(value_u)
                if np.abs(value_a) <= np.abs(diff[0]) and np.abs(value_u) <= np.abs(diff[1]) \
                        and value_a * diff[0] >= 0 and value_u * diff[1] >= 0:
                    state = eval(state)
                    state = np.array(state)
                    yield state

            content = exch.readline()


def zero_exchange(type):
    with open(f'Data/Temp/zero_exchange_{type}.dat', 'r') as zex:
        state = zex.readline()
        while state:
            state = eval(state)
            state = np.array(state)
            yield state
            state = zex.readline()
