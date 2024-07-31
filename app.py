from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)


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
    return render_template("index.html", error=error)


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
    # Perform calculations or further processing
    return jsonify(form_data)


if __name__ == '__main__':
    app.run(debug=True)
