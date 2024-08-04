import numpy as np
import main
from write.html import table, tables
from PTable import look_for

#      Fe2+  Fe3+  Co2+  Co3+   Cr2+  Cr3+
var = [True, True, True, False, False, False,  # a
       True, True, True, True, False, True]  # b
u = [4, 5, 3., 0., 0, 3,
     4, 5, 3., 0., 0, 3]

CoCr6_sat_mag = {
    225: 22.759824,
    200: 19.80,
    175: 13.69,
    150: 6.43
}
m = CoCr6_sat_mag[200] * (1.4 * 55.845 + 1 * 58.933 + 0.6 * 51.996 + 4 * 16) / 5585

r = [.63, .49, .58, .0, .0, .8,
     .78, .645, .745, .545, .0, .615]
a = 8.337828

guss = [
    0, 1, 0, 0, 0, 0,
    0, .4, 1, 0, 0, .6
]

main.init(3, u, r, var=var, delta=0.001)
c1 = main.cation_distribution([1.4, 1, 0.6], ['Fe', 'Co', 'Cr'], u, r, var=var)
c1.initiate_simulation(guss)
c1.Ro = 1.37
cd_tables = []
for T, ms in CoCr6_sat_mag.items():
    mue = ms * (1.4 * 55.845 + 1 * 58.933 + 0.6 * 51.996 + 4 * 16) / 5585
    c1.initiate_simulation(guss)
    c1.find_dist(moment=mue, tol=0.001)
    cd_tables.append({
        'site_a': c1.cations_content[np.where(c1.a)[0]],
        'site_b': c1.cations_content[np.where(c1.b)[0]],
        'e_name': c1.name,
        'label': f'{T}',
        'name': f'CoCr6&{T}',
        'a_th': c1.calculate_a_th(),
        'a_exp': a,
        'mue_exp': mue,
        'mue_th': c1.calculate_mue(),
    })
    print(c1)
    # print('exp a:', a)
    print('th a:', c1.calculate_a_th())
    print('exp mue:', mue)
    print('th mue:', c1.calculate_mue())
#
# r = table({
#     'site_a': c1.cations_content[np.where(c1.a)[0]],
#     'site_b': c1.cations_content[np.where(c1.b)[0]],
#     'e_name': c1.name,
#     'label': 'CoCr6',
#     'name': 'CoCr6'
# }, name='CoCr6', overwrite=True)

r = tables(cd_tables, filename='CoCr6', overwrite=True)

print(look_for('co'))
