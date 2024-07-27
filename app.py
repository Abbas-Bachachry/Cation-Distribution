from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

form_data_list = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    form_data_list.append(data)
    return jsonify({"status": "success", "message": "Data added successfully"})


@app.route('/recalculate', methods=['POST'])
def recalculate():
    index = int(request.json.get('index'))
    data = request.json.get('data')
    if 0 <= index < len(form_data_list):
        form_data_list[index] = data
        return jsonify({"status": "success", "message": "Data recalculated successfully"})
    else:
        return jsonify({"status": "error", "message": "Invalid index"})


@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(form_data_list)


def create_output_object(data_list):
    output_list = []
    for data in data_list:
        output = {
            'r_A': [],  # Collect r_A values
            'r_B': [],  # Collect r_B values
            'a_th': None,  # Placeholder for a_th value
            'n_B_th': None,  # Placeholder for n_B^th value
            'n_B_exp': None,  # Placeholder for n_B^exp value
            'SiteA': [],  # Collect SiteA values
            'SiteB': [],  # Collect SiteB values
            'R_O': data.get('radiiOxygen', 1.28),  # Use default if not provided
            'the_names': [],  # Collect element names
            'label': data.get('label', 'default_label')  # Placeholder for label
        }

        for key, value in data.items():
            if key.startswith('radiiA'):
                output['r_A'].append(value)
            elif key.startswith('radiiB'):
                output['r_B'].append(value)
            elif key.startswith('oxidationA'):
                output['SiteA'].append(value)
            elif key.startswith('oxidationB'):
                output['SiteB'].append(value)
            elif key.startswith('elementName'):
                output['the_names'].append(value)

        output_list.append(output)

    return output_list


@app.route('/get_output', methods=['GET'])
def get_output():
    output = create_output_object(form_data_list)
    return render_template('output.html', output=output)


if __name__ == '__main__':
    app.run(debug=True)
