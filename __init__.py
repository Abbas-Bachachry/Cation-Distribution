import os.path
import numpy as np
from cation_distribution import CD as _CD

_used_var = False


def init(e_num, u, r, *, var: list[bool] | None = None, delta=0.01, prec=None):
    """
    Initialize data files for cation distribution calculation.

    This function processes input states based on specified conditions and writes relevant
    information to temporary files.

    Parameters:
    e_num (int): The number of elements.
    u (list): List of cations magnetic moments.
    r (list): List of cations radii.
    var (list[bool]): Boolean list indicating which variables to consider in the states.
    delta (float): The uncertainty in the result (default is 0.01).
    prec (int): The overall precision of the result (calculated if not provided).

    Returns:
    None
    """
    global _used_var
    if var is None:
        var = [True] * len(u)
    else:
        _used_var = True
    # Calculate the precision if not provided
    if prec is None:
        prec = precision(delta, u, r)

    # Convert u and r to NumPy arrays
    u = np.array(u)
    r = np.array(r)

    # Remove existing files in the temporary folder
    remove_files_from_temp()

    # Write the value of delta to a file
    with open('Data/Temp/delta', 'w') as delta_file:
        delta_file.write(f'delta={delta}')
    with open('Data/Temp/precision', 'w') as precision_file:
        precision_file.write(f'precision={prec}')

    # Process states and write relevant information to temporary files
    with open(f'Data/States/{e_num}.dat', 'r') as states:
        exchange_u = open('Data/Temp/exchange_u.dat', 'a')
        zero_exchange_u = open('Data/Temp/zero_exchange_u.dat', 'a')
        exchange_r = open('Data/Temp/exchange_r.dat', 'a')
        zero_exchange_r = open('Data/Temp/zero_exchange_r.dat', 'a')
        exchange_ru = open('Data/Temp/exchange_ru.dat', 'a')
        zero_exchange_ru = open('Data/Temp/zero_exchange_ru.dat', 'a')

        state = states.readline()
        while state:
            state = eval(state)
            valid = True

            # Check if the state satisfies the specified conditions
            for i, status in enumerate(var):
                if status is False and state[i] != 0:
                    valid = False
                    break

            if valid:
                arr = delta * np.array(state)

                # Calculate delta_u and delta_r
                delta_u = np.sum((arr * u)[2 * e_num:]) - np.sum((arr * u)[:2 * e_num])
                delta_u = np.round(delta_u, prec)
                delta_r = 8 / (3 * np.sqrt(3)) * (
                        np.sum((arr * r)[:2 * e_num]) + np.sqrt(3) / 2 * np.sum((arr * r)[2 * e_num:]))
                delta_r = np.round(delta_r, prec)

                # Write to relevant files based on conditions
                if delta_u == 0:
                    zero_exchange_u.write(f'{list(arr)}\n')
                else:
                    exchange_u.write(f'{list(arr)}; {delta_u}\n')

                if delta_r == 0:
                    zero_exchange_r.write(f'{list(arr)}\n')
                else:
                    exchange_r.write(f'{list(arr)}; {delta_r}\n')
                if delta_r == 0 and delta_u == 0:
                    zero_exchange_ru.write(f'{list(arr)}\n')
                else:
                    exchange_ru.write(f'{list(arr)}; {delta_r}; {delta_u}\n')

            state = states.readline()

        # Close all temporary files
        exchange_u.close()
        zero_exchange_u.close()
        exchange_r.close()
        zero_exchange_r.close()
        exchange_ru.close()
        zero_exchange_ru.close()


def precision(delta, u, r):
    """
    Calculates the precision of a result given the uncertainties and inputs.

    This function takes the uncertainty (delta), inputs (u), and results (r),
    and calculates the overall precision of the result by considering the
    precision of each component.

    Parameters:
    delta (float): The uncertainty in the result.
    u (list): List of uncertainties for input values.
    r (list): List of input values and the result.

    Returns:
    int: The overall precision of the result.
    """
    # Calculate the precision of the uncertainty in the result
    delta_prec = decimal_length(delta)

    # Initialize the maximum precision
    max_prec = 0

    # Iterate through each input value and result to find the maximum precision
    for c in r:
        r_prec = decimal_length(c)
        if max_prec < r_prec:
            max_prec = r_prec

    for c in u:
        u_prec = decimal_length(c)
        if max_prec < u_prec:
            max_prec = u_prec

    # Calculate the overall precision by summing up the individual precisions
    prec = max_prec + delta_prec

    return prec


def decimal_length(f):
    """
    Calculates the length of the decimal part of a number.

    This function takes a number as input and calculates the length
    of its decimal part. If the input is in scientific notation, it
    considers both the significant digits and the exponent.

    Parameters:
    f (float): The input number.

    Returns:
    int: The length of the decimal part of the number.
    """
    f = str(f)

    # Check if the number is in scientific notation
    if 'e' in f:
        # Extract significant digits and exponent
        significant_digits, exponent = f.split('e')

        # Split significant digits into integer and decimal parts
        str_list = str(significant_digits).split('.')
        prec = 0

        # Calculate the precision of the decimal part
        if len(str_list) > 1:
            decimal = str_list[1]
            prec = len(decimal)

        # Return the total precision considering both decimal and exponent
        return prec + abs(int(exponent))

    # Check if the number has a decimal part
    elif '.' in f:
        str_list = str(f).split('.')
        decimal = str_list[1]

        # Calculate the precision of the decimal part
        prec = len(decimal)
        return prec

    # If the number has no decimal part, return 0
    else:
        return 0


def remove_files_from_temp():
    """
    Removes all files from the 'Data/Temp' folder.

    This function iterates through the files in the 'Data/Temp' folder
    and removes each file.
    """
    folder_path = 'Data/Temp'

    # List all files in the specified folder
    files = os.listdir(folder_path)

    # Iterate through the files and remove each one
    for file in files:
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)


def cation_distribution(n, names, mue, radii, *, var=None):
    global _used_var
    if _used_var and var is None:
        raise TypeError("cation_distribution() missing 1 required keyword-only argument: 'var'")
    if var is None:
        var = [True] * 4 * len(n)
    assert sum(n) == 3, f"total element content should be 3 not {sum(n)}"
    assert len(n) == len(names), \
        "the length of n list should be the same as name list. " \
        f"the length n, {len(n)} is not equal to length of name, {len(names)}"
    assert len(mue) == 4 * len(n), f"total element content should be 3 not {sum(n)}"
    assert len(mue) == len(var), \
        "the length of mue list should be the same as var list. " \
        f"the length mue, {len(mue)} is not equal to length of var, {len(var)}"
    return _CD(n, names, mue, radii, var)
