import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_socketio import SocketIO
import threading
from utils import get_cd_list, check_input, get_data, calculate_cd, delete_cd_list_file
from output import save

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET'
socketio = SocketIO(app, async_mode='threading')

DATABASE = 'elements.db'

cd_list = []


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
    global cd_list
    cd_list = get_cd_list()
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
    return render_template("index.html", error=error, enumerate=enumerate, enumerated_cd_list=enumerated_cd_list)


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
    form_data = request.form.to_dict()
    data = get_data(form_data)
    thread = threading.Thread(target=calculate_cd, args=[socketio, data])
    thread.start()
    return redirect(url_for('index'))


@app.route('/output/<i>')
def output(i):
    try:
        cd = cd_list[int(i)]
    except Exception as err:
        return f'<h1>Error: {err}</h1>'
    return jsonify(cd)


@app.route('/results')
def result_table():
    return render_template('output.html', enumerate=enumerate, output=cd_list)


@app.route('/save_table', methods=['POST'])
def save_table():
    data = request.json
    file_type = data.get('type', 'html')  # Default to HTML if type is not provided

    try:
        save(cd_list, type_=file_type)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
    delete_cd_list_file()
