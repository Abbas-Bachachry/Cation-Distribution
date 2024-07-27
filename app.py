from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    # Process the form data here
    # You can add your calculation logic here
    return f'{data} submitted successfully!'


if __name__ == '__main__':
    app.run(debug=True)
