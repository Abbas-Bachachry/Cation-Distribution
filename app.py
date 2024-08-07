import time
import sqlite3
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_socketio import SocketIO, emit
# from celery import Celery
import threading
import main

# import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET'
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

socketio = SocketIO(app, async_mode='threading')

cd_list = []


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
                data['m_exp'] = float(form['latticeConstant'])
            i += 1
        except KeyError as e:
            # print(e)
            break

    data['guess'] = get_guess(form, i)
    label = ''
    for name, content in zip(data['names'], data['content']):
        label += f'{name}<sub>{content}</sub>'
    data['label'] = label + 'O<sub>4</sub>'
    return rearrange_data(data)


# @celery.task
def calculate_cd(data):
    global cd_list
    time.sleep(10)  # pause for 10 seconds
    main.init(len(data['names']), data['mue'], data['radii'], var=data['sites_perf'], delta=0.001)
    cd = main.cation_distribution(data['content'], data['names'], data['mue'], data['radii'], var=data['sites_perf'])
    cd.initiate_simulation(data['guess'])
    cd_list.append({
        'site_a': cd.cations_content[np.where(cd.a)[0]].tolist(),
        'site_b': cd.cations_content[np.where(cd.b)[0]].tolist(),
        'e_name': cd.name.tolist(),
        'label': data['label'],
        'name': data['label'],
        'a_th': cd.calculate_a_th(),
        'a_exp': data['a_exp'],
        'mue_exp': cd.calculate_magnetic_moment(data['m_exp'], data['weight']),
        'mue_th': cd.calculate_mue(),
        'R_O': cd.Ro
    })
    message = "The calculation is complete. Reload the page to see the results."
    print(f"Emitting event 'task_done' with message: {message}")  # Debugging line
    socketio.emit("task_done", {"message": message})
    print("task_done event emitted")  # Debugging line
    return cd


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


DATABASE = 'elements.db'


def get_element_data(name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM elements WHERE name=?", (name,))
    row = cursor.fetchone()
    if row:
        element_data = {
            'name': row[0],
            'molecular_weight': row[1],
            'oxidation_state_a1': row[2],
            'magnetic_moment_a1': row[3],
            'radii_a1': row[4],
            'oxidation_state_a2': row[5],
            'magnetic_moment_a2': row[6],
            'radii_a2': row[7],
            'oxidation_state_b1': row[8],
            'magnetic_moment_b1': row[9],
            'radii_b1': row[10],
            'oxidation_state_b2': row[11],
            'magnetic_moment_b2': row[12],
            'radii_b2': row[13]
        }
    else:
        flash(f"No data found for element {name}", "error")
        element_data = {'name': name}
    conn.close()
    return element_data


@app.route('/', methods=['GET', 'POST'])
def index():
    error = ''
    if request.method == 'POST':
        text_input = request.form['text_input']
        try:
            check_input(text_input)
            result = ','.join([item.strip().capitalize() for item in text_input.split(",")])
            return redirect(url_for('chem', results=result))
        except AssertionError as e:
            error = f'Invalid input. {e}'
    enumerated_cd_list = list(enumerate(cd_list))
    return render_template("index.html", error=error, enumerated_cd_list=enumerated_cd_list)


@app.route('/Chem=<results>')
def chem(results):
    list_inp = results.split(',')
    n = len(list_inp) // 2
    element_data = []
    for i in range(0, len(list_inp), 2):
        element_data.append({"content": list_inp[i + 1]})
        element_data[-1].update(get_element_data(list_inp[i]))

    return render_template("chem.html", n=n, element_data=element_data)


@app.route('/calculate', methods=['POST'])
def calculate():
    print('start')
    # Process the form data here
    form_data = request.form.to_dict()
    data = get_data(form_data)
    thread = threading.Thread(target=calculate_cd, args=[data])
    form_data['data'] = data
    thread.start()
    # Perform calculations or further processing
    return redirect(url_for('index'))


@app.route('/output/<i>')
def output(i):
    try:
        cd = cd_list[int(i)]
    except Exception as err:
        return f'<h1>Error: {err}</h1>'
    return jsonify(cd)


if __name__ == '__main__':
    # todo:do cd calculation
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
