from flask import Flask, render_template, request, redirect, url_for, jsonify
# from celery import Celery
import threading

import init

app = Flask(__name__)
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

cd_list = []


def get_data(form):
    data = {
        'label': f'{len(cd_list)}',
        'names': [],
        'content': [],
        'mue': [],
        'radii': [],
        'sites_perf': []
    }
    i = 0
    while True:
        try:
            data['names'].append(form[f'elementName{i}'])
            data['content'].append(float(form[f'elementContent{i}']))
            data['sites_perf'].append(f'oxidationA{i}_1' in form)
            data['sites_perf'].append(f'oxidationA{i}_2' in form)
            data['sites_perf'].append(f'oxidationB{i}_1' in form)
            data['sites_perf'].append(f'oxidationB{i}_2' in form)
            data['mue'].append(form[f'A{i}1magneticMoment'])
            data['mue'].append(form[f'A{i}2magneticMoment'])
            data['mue'].append(form[f'B{i}1magneticMoment'])
            data['mue'].append(form[f'B{i}2magneticMoment'])
            data['radii'].append(form[f'A{i}1radii'])
            data['radii'].append(form[f'A{i}2radii'])
            data['radii'].append(form[f'B{i}1radii'])
            data['radii'].append(form[f'B{i}2radii'])
            i += 1
        except KeyError as e:
            print(e)
            break
    label = ''
    for name, content in zip(data['names'], data['content']):
        label += f'{name}<sub>{content}</sub>'
    data['label'] = label
    return data


# @celery.task
def calculate_cd(data):
    global cd_list
    init.init(len(data['names']), data['mue'], data['radii'], var=data['sites_perf'], delta=0.001)
    # cd = init.cation_distribution(data['content'], data['names'], data['mue'], data['radii'], var=data['sites_perf'])
    # cd.initiate_simulation()
    # cd_list.append(cd)
    print(data)
    return data


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


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        text_input = request.form['text_input']
        try:
            check_input(text_input)
            result = ','.join([item.strip().capitalize() for item in text_input.split(",")])
            return redirect(url_for('chem', results=result))
        except AssertionError as e:
            error = f'Invalid input. {e}'
    print(len(cd_list))
    return render_template("index.html", error=error, cd_list=cd_list)


@app.route('/Chem=<results>')
def chem(results):
    list_inp = results.split(',')
    n = len(list_inp) // 2
    element_data = [{"name": list_inp[i], "content": list_inp[i + 1]} for i in range(0, len(list_inp), 2)]
    return render_template("chem.html", n=n, element_data=element_data)


@app.route('/calculate', methods=['POST'])
def calculate():
    # Process the form data here
    form_data = request.form.to_dict()
    data = get_data(form_data)
    thread = threading.Thread(target=calculate_cd, args=[data])
    form_data['data'] = data
    thread.start()
    # Perform calculations or further processing
    return redirect(url_for('index')), 202


if __name__ == '__main__':
    app.run(debug=True)
