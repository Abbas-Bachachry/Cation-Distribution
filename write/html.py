import os.path
from pathlib import Path

__root__ = str(Path(__file__).parent.parent)


def _html(table_str, info):
    # load head
    with open(rf'{__root__}\write\head.html', 'r') as headf:
        head = headf.read()
    return f'<!DOCTYPE html>\n<html lang="">{head}\n' \
           f'<body>\n' \
           f'<div class="row">\n' \
           f'\t<div class="column">\n{table_str}</div>\n' \
           f'\t<div class="column">{info}</div>\n' \
           f'</div>\n' \
           f'</body>\n' \
           f'</html>'


def _creat_cd_table(caption):
    # load table
    with open(rf'{__root__}\write\cd_table.html', 'r') as cdtf:
        cdt = cdtf.read()
    cdt = cdt.replace('set_caption', caption)
    return cdt


def _get_site_ab(a, b, name):
    site_a = '['
    site_b = '('
    q = [2, 3]
    for i, c in enumerate(a):
        if c:
            site_a += f'{name[i // 2]}<sup>{q[i % 2]}+</sup><sub>{c}</sub>, '

    site_a = site_a[:-2] + ']'
    for i, c in enumerate(b):
        if c:
            site_b += f'{name[i // 2]}<sup>{q[i % 2]}+</sup><sub>{c}</sub>, '

    site_b = site_b[:-2] + ')'

    return site_a, site_b


def _add_row(table_str, site_a, site_b, label):
    # row table
    with open(rf'{__root__}\write\cd_row.html', 'r') as cdrf:
        cdr = cdrf.read()
    table_str = table_str.replace('<!--#set row-->', f"{cdr}")
    table_str = table_str.replace('set_label', f'{label}')
    table_str = table_str.replace('set_A', f'{site_a}')
    table_str = table_str.replace('set_B', f'{site_b}')
    return table_str


def _get_more(T):
    ath = T.get('a_th')
    aexp = T.get('a_exp')
    mueth = T.get('mue_exp')
    mueexp = T.get('mue_th')
    result = f'<div class="row">theoretical a: {ath}</div>\n' \
             f'<div class="row">experimental a: {aexp}</div>\n' \
             f'<div class="row">theoretical mue: {mueth}</div>\n' \
             f'<div class="row">experimental mue: {mueexp}</div>'
    return result


def table(T: dict = {}, name=None, overwrite=False):
    file = name
    if file is None:
        file = T.get('name', 'table')
    file = __root__ + fr'\OutPut\{file}'
    if not overwrite:
        i = 1
        new_file = file
        while os.path.exists(f'{new_file}.html'):
            new_file = f'{file}_{i}'
            i += 1
        file = new_file

    file += '.html'
    with open(file, 'w') as tfile:
        site_a, site_b = _get_site_ab(T.get('site_a'), T.get('site_b'), T.get('e_name'))
        table_str = _creat_cd_table(f'cation distribution of {T.get("name")}')
        table_str = _add_row(table_str, site_a, site_b, T.get("label"))
        tstr = _html(table_str, 'more')
        tfile.write(tstr)

    return tstr


def tables(T_L: list[dict], filename, overwrite=False):
    file = __root__ + fr'\OutPut\{filename}'
    if not overwrite:
        i = 1
        new_file = file
        while os.path.exists(f'{new_file}.html'):
            new_file = f'{file}_{i}'
            i += 1
        file = new_file

    file += '.html'
    with open(file, 'w') as tfile:
        table_str = _creat_cd_table(f'cation distribution of {filename}')
        for T in T_L:
            site_a, site_b = _get_site_ab(T.get('site_a'), T.get('site_b'), T.get('e_name'))
            table_str = _add_row(table_str, site_a, site_b, T.get("label"))
            tstr = _html(table_str, _get_more(T))
        tfile.write(tstr)

    return tstr
