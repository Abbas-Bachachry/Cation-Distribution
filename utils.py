import os
import pickle
import numpy as np
import main

cd_list = []
initial = True


def get_guess(form, n):
    guess = []
    for i in range(4 * n):
        try:
            guess.append(float(form[f'initialGuess{i}']))
        except ValueError:
            return

    return guess


def rearrange_data(data):
    n = len(data['names'])
    index_list = []
    for i in range(n):
        index_list.extend([4 * i, 4 * i + 1])
    for i in range(n):
        index_list.extend([4 * i + 2, 4 * i + 3])

    data['sites_perf'] = np.array(data['sites_perf'], dtype=bool)[index_list].tolist()
    data['mue'] = np.array(data['mue'])[index_list].tolist()
    data['radii'] = np.array(data['radii'])[index_list].tolist()

    return data


def get_data(form):
    data = {
        'label': f'{len(cd_list)}',
        'names': [],
        'content': [],
        'weight': [],
        'mue': [],
        'radii': [],
        'sites_perf': [],
        'guess': None,
        'a_exp': None,
        'm_exp': None,
        'Ro': 1.28
    }
    i = 0
    while True:
        try:
            data['names'].append(form[f'elementName{i}'])
            data['content'].append(float(form[f'elementContent{i}']))
            data['weight'].append(float(form[f'atomicWeight{i}']))
            data['sites_perf'].append(f'oxidationA{i}_1' in form)
            data['sites_perf'].append(f'oxidationA{i}_2' in form)
            data['sites_perf'].append(f'oxidationB{i}_1' in form)
            data['sites_perf'].append(f'oxidationB{i}_2' in form)
            data['mue'].append(float(form[f'A{i}1magneticMoment']))
            data['mue'].append(float(form[f'A{i}2magneticMoment']))
            data['mue'].append(float(form[f'B{i}1magneticMoment']))
            data['mue'].append(float(form[f'B{i}2magneticMoment']))
            data['radii'].append(float(form[f'A{i}1radii']))
            data['radii'].append(float(form[f'A{i}2radii']))
            data['radii'].append(float(form[f'B{i}1radii']))
            data['radii'].append(float(form[f'B{i}2radii']))
            if form['saturationMagnetization']:
                data['m_exp'] = float(form['saturationMagnetization'])
            if form['latticeConstant']:
                data['a_exp'] = float(form['latticeConstant'])
            if form['radiiOxygen']:
                data['Ro'] = float(form['radiiOxygen'])
            i += 1
        except KeyError as e:
            # print(e)
            break

    data['guess'] = get_guess(form, i)
    label = ''
    for name, content in zip(data['names'], data['content']):
        label += f'{name}<sub>{content}</sub>'
    data['name'] = label + 'O<sub>4</sub>'
    data['label'] = data['name']
    return rearrange_data(data)


def calculate_cd(socketio, data):
    try:
        main.init(len(data['names']), data['mue'], data['radii'], var=data['sites_perf'], delta=0.001)
        cd = main.cation_distribution(data['content'], data['names'], data['mue'], data['radii'],
                                      var=data['sites_perf'])
        cd.initiate_simulation(data['guess'])
        cd.Ro = data['Ro']
        cd.find_dist(moment=cd.calculate_magnetic_moment(data['m_exp'], data['weight']),
                     a_exp=data['a_exp'], tol=.001)
        cd_list.append({
            'site_a': cd.cations_content[np.where(cd.a)[0]].tolist(),
            'site_b': cd.cations_content[np.where(cd.b)[0]].tolist(),
            'e_name': cd.name.tolist(),
            'label': data['label'],
            'name': data['name'],
            'a_th': cd.calculate_a_th(),
            'a_exp': data['a_exp'],
            'mue_exp': cd.calculate_magnetic_moment(data['m_exp'], data['weight']),
            'mue_th': cd.calculate_mue(),
            'R_O': cd.Ro
        })
        cd_list[-1].update(data)
        save_cd_list()
        message = "The calculation is complete. Reload the page to see the results."
        print(f"Emitting event 'task_done' with message: {message}")
        socketio.emit("task_done", {"message": message})
        print("task_done event emitted")
    except Exception as err:
        error_message = f"An error occurred during calculation: {str(err)}"
        print(f"Emitting event 'task_error' with message: {error_message}")
        socketio.emit("task_error", {"message": error_message})
        print("task_error event emitted")


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def check_input(txt_inp):
    list_inp = txt_inp.split(',')
    assert all(item.strip() for item in list_inp), "Please enter a comma-separated list."
    assert all(
        len(item.strip()) < 3 for item in list_inp[::2]), "The symbol of an element should be less than three letters."
    assert all(is_number(item.strip()) or ("{" in item and "}" in item) for item in list_inp[1::2]), \
        "Each element should be followed by a valid number or content in braces."
    assert len(list_inp) % 2 == 0, "There should be an element name followed by its content."


def save_cd_list():
    with open('Data/Temp/cd_list.pkl', 'wb') as f:
        pickle.dump(cd_list, f)


def load_cd_list():
    global cd_list
    if os.path.exists('Data/Temp/cd_list.pkl'):
        try:
            with open('Data/Temp/cd_list.pkl', 'rb') as f:
                cd_list = pickle.load(f)
        except (FileNotFoundError, EOFError) as e:
            print(e)


def get_cd_list():
    global initial
    if initial:
        load_cd_list()
        initial = False
    return cd_list


def delete_cd_list_file():
    try:
        os.remove('Data/Temp/cd_list.pkl')
    except FileNotFoundError:
        pass
