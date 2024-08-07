import os.path
from functions import *


class CDResults:
    def __init__(self, n: int, names, mue, radii, cc):
        self.__e_number = n
        self.__name = np.asarray(names)
        self.__mue = np.array(mue)
        self.__radii = np.array(radii)
        self.__cations_content = np.array(cc)
        self.__parameters = {
            "a_exp": None,
            "a_th": None,
            "nB_exp": None,
            "nB_th": None,
            "u": None,
            "Ra": None,
            "Rb": None,
            "Ro": None,
        }

        self._q = np.zeros_like(mue, dtype=np.int32)
        self._q[::2] = 2
        self._q[1::2] = 3
        self._a = np.zeros_like(mue, dtype=np.int32)
        self._a[:2 * self.__e_number] = 1
        self._b = np.zeros_like(mue, dtype=np.int32)
        self._b[2 * self.__e_number:] = 1


class CD:
    """
    cation distribution in spinel sub-latices
    """

    a_capacity = 1
    b_capacity = 2

    def __init__(self, n, names, mue, radii, var):
        self._Ro = 1.28
        self.e_content = np.array(n)
        self.e_number = len(n)
        self.name = np.asarray(names)
        self.mue = np.array(mue)
        self.radii = np.array(radii)
        self.var = var

        if os.path.exists('Data/Temp/precision'):
            with open('Data/Temp/precision', 'r') as prec_file:
                prec = prec_file.read().split('=')[1]
                self.precision = int(prec)
        else:
            self.precision = 0

        self.cations_content = np.zeros_like(mue)
        self.q = np.zeros_like(mue, dtype=np.int32)
        self.q[::2] = 2
        self.q[1::2] = 3
        self.a = np.zeros_like(mue, dtype=np.int32)
        self.a[:2 * self.e_number] = 1
        self.b = np.zeros_like(mue, dtype=np.int32)
        self.b[2 * self.e_number:] = 1

    def initiate_simulation(self, guss=None):
        if guss is None:
            massage = self.__initial_distribution__()
        else:
            massage = self.__initial_guss__(guss)

        return massage

    def __initial_guss__(self, guss):
        guss = np.array(guss)
        self.cations_content = guss
        assert self.check_conditions(), f"somthing went wrong!\ninitial cation distribution: {self.cations_content}"
        self.a_capacity = 0
        self.b_capacity = 0
        mue = self.calculate_mue()
        massage = f"the cation distribution initiated with moment of {mue} \u03BCB.\n" \
                  f"{self}"
        return massage

    def __initial_distribution__(self):  # fixme
        self.cations_content[:] = 0
        self.a_capacity = 1
        self.b_capacity = 2
        n = self.e_number

        e_content = self.e_content.copy()

        for i in range(self.e_number):
            for j in [2 * i, 2 * i + 1, 2 * (i + n), 2 * (i + n) + 1]:
                if self.var[j]:
                    if e_content[i] > 0:
                        if j < 2 * n and j % 2 == 0 and self.a_capacity > 0:
                            delta = e_content[i] if e_content[i] < self.a_capacity else self.a_capacity
                            self.a_capacity -= delta
                            e_content[i] -= delta
                            self.cations_content[j] += delta
                        elif j >= 2 * n and j % 2 == 1 and self.b_capacity > 0:
                            delta = e_content[i] if e_content[i] < self.b_capacity else self.b_capacity
                            self.b_capacity -= delta
                            e_content[i] -= delta
                            self.cations_content[j] += delta
                    else:
                        break
        self.a_capacity = round(self.a_capacity, self.precision + 1)
        self.b_capacity = round(self.b_capacity, self.precision + 1)
        assert self.a_capacity == 0, f"somthing went wrong!\ninitial cation distribution: {self.cations_content}"
        assert self.b_capacity == 0, f"somthing went wrong!\ninitial cation distribution: {self.cations_content}"
        assert self.check_conditions(), f"somthing went wrong!\ninitial cation distribution: {self.cations_content}"

        mue = self.calculate_mue()
        massage = f"the cation distribution initiated with moment of {mue} \u03BCB.\n" \
                  f"{self}"
        return massage

    def find_dist(self, *, moment=None, a_exp=None, maxitiration=10000, tol=0.01):
        assert self.check_conditions(), f"initial simulation before calling this method"
        if moment is None and a_exp is None:
            raise TypeError("CD.find_dist() missing 1 required keyword-only argument: 'moment' or 'a_exp")
        elif a_exp is None:
            self.cations_content = find_dist_moment(self.cations_content, self.mue, moment, maxitiration, tol)
        elif moment is None:
            self.cations_content = find_dist_a(self.cations_content, self.radii, self.Ro, a_exp, maxitiration, tol)
        else:
            self.cations_content = find_dist(self.cations_content, self.mue, moment, self.radii, a_exp, self.Ro,
                                             maxitiration=maxitiration, tol=tol)
        assert self.check_conditions(), f"somthing went wrong!\ncation distribution: {self.cations_content}"

    def calculate_mue(self):
        site_a = np.where(self.a)[0]
        site_b = np.where(self.b)[0]
        mue_a = np.sum((self.mue * self.cations_content)[site_a])
        mue_b = np.sum((self.mue * self.cations_content)[site_b])
        mue = mue_b - mue_a
        if self.precision:
            mue = np.round(mue, self.precision)
        return mue

    def calculate_a_th(self):
        a_th = 8 / (3 * np.sqrt(3)) * ((self.Ra + self.Ro) + np.sqrt(3) * (self.Rb + self.Ro))
        if self.precision:
            a_th = np.round(a_th, self.precision)
        return a_th

    @property
    def Ra(self):
        site_a = np.where(self.a)[0]
        ra = np.sum((self.radii * self.cations_content)[site_a])
        if self.precision:
            ra = np.round(ra, self.precision)
        return ra

    @property
    def Rb(self):
        site_b = np.where(self.b)[0]
        rb = np.sum((self.radii * self.cations_content)[site_b]) / 2
        if self.precision:
            rb = np.round(rb, self.precision)
        return rb

    @property
    def Ro(self):
        return self._Ro

    @Ro.setter
    def Ro(self, value):
        self._Ro = value

    def check_conditions(self):
        n = self.e_number
        c_check = True

        # check the mass conservation law
        # check if content of each element in calculated/guessed cations_content is the same as provided element content
        for i in range(self.e_number):
            element_indexes = [2 * i, 2 * i + 1, 2 * (i + n), 2 * (i + n) + 1]
            cation_content = self.cations_content[element_indexes]
            c_check = c_check and self.e_content[i] == np.round(np.sum(cation_content), 3)

        # check the charge conservation principle
        q_check = round(self.cations_content @ self.q, self.precision + 1) == 8
        # check the content in site A, it should be 1
        a_check = round(self.cations_content @ self.a, self.precision + 1) == 1
        # check the content in site B, it should be 2
        b_check = round(self.cations_content @ self.b, self.precision + 1) == 2
        return c_check and q_check and a_check and b_check

    def check_conditions_v2(self):  # todo: use this method
        n = self.e_number
        c_check = True
        error_messages = []

        # Check the mass conservation law
        for i in range(self.e_number):
            element_indexes = [2 * i, 2 * i + 1, 2 * (i + n), 2 * (i + n) + 1]
            cation_content = self.cations_content[element_indexes]
            if self.e_content[i] != np.round(np.sum(cation_content), 3):
                c_check = False
                error_messages.append(
                    f"Mass conservation law failed for element {i}. Expected {self.e_content[i]}, got {np.round(np.sum(cation_content), 3)}.")

        # Check the charge conservation principle
        q_check = round(self.cations_content @ self.q, self.precision + 1) == 8
        if not q_check:
            error_messages.append("Charge conservation principle failed. Expected total charge to be 8.")

        # Check the content in site A, it should be 1
        a_check = round(self.cations_content @ self.a, self.precision + 1) == 1
        if not a_check:
            error_messages.append("Content in site A failed. Expected content to be 1.")

        # Check the content in site B, it should be 2
        b_check = round(self.cations_content @ self.b, self.precision + 1) == 2
        if not b_check:
            error_messages.append("Content in site B failed. Expected content to be 2.")

        success = c_check and q_check and a_check and b_check
        error_message = "\n".join(error_messages) if error_messages else ""
        return success, error_message

    def calculate_magnetic_moment(self, m, w):
        return m * np.sum(self.e_content * w) / 5585

    def __str__(self):
        site_a = np.where(self.a)[0]
        site_b = np.where(self.b)[0]

        max_len = 5
        for c in self.cations_content:
            if max_len < len(str(c)):
                max_len = len(str(c))
        max_len -= 5
        if max_len < 0:
            max_len = 0

        space = ""
        for _ in range(max_len):
            space += " "
        cations_str = "["
        for i in range(len(site_a)):
            cations_str += f"{self.name[i // 2]}{self.q[i]}+{space} "
            if i % 2:
                cations_str += "| "
        cations_str = cations_str[:-3 - max_len] + ']'

        a_site_str = "["
        space_length = 1
        for i in range(len(site_a)):
            c = str(self.cations_content[i])
            space = ""
            if len(c) < max_len + 4:
                space_length = max_len + 4 - len(c)
            for _ in range(space_length):
                space += " "
            a_site_str += f"{c}{space} "
            if i % 2:
                a_site_str += "| "
        a_site_str = a_site_str[:-2 - space_length] + ']'

        b_site_str = "["
        space_length = 1
        for i in range(len(site_b), 2 * len(site_b)):
            c = str(self.cations_content[i])
            space = ""
            if len(c) < max_len + 4:
                space_length = max_len + 4 - len(c)
            for _ in range(space_length):
                space += " "
            b_site_str += f"{c}{space} "
            if i % 2:
                b_site_str += "| "
        b_site_str = b_site_str[:-2 - space_length] + ']'

        text = "cation distribution:{\n" \
               f"\tQ:{cations_str}\n" \
               f"\tA:{a_site_str}\n" \
               f"\tB:{b_site_str}\n" \
               "}"
        return text
