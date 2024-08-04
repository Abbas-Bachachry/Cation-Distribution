from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'elements.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS elements (
            name TEXT PRIMARY KEY,
            molecular_weight REAL,
            oxidation_state_a1 BOOL,
            magnetic_moment_a1 REAL,
            radii_a1 REAL,
            oxidation_state_a2 BOOL,
            magnetic_moment_a2 REAL,
            radii_a2 REAL,
            oxidation_state_b1 BOOL,
            magnetic_moment_b1 REAL,
            radii_b1 REAL,
            oxidation_state_b2 BOOL,
            magnetic_moment_b2 REAL,
            radii_b2 REAL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('databaseForm.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name'].capitalize()
    molecular_weight = request.form['molecular_weight']
    oxidation_state_a1 = 'oxidation_state_a1' in request.form
    magnetic_moment_a1 = request.form['magnetic_moment_a1'] or 0
    radii_a1 = request.form['radii_a1'] or 0
    oxidation_state_a2 = 'oxidation_state_a2' in request.form
    magnetic_moment_a2 = request.form['magnetic_moment_a2'] or 0
    radii_a2 = request.form['radii_a2'] or 0
    oxidation_state_b1 = 'oxidation_state_b1' in request.form
    magnetic_moment_b1 = request.form['magnetic_moment_b1'] or 0
    radii_b1 = request.form['radii_b1'] or 0
    oxidation_state_b2 = 'oxidation_state_b2' in request.form
    magnetic_moment_b2 = request.form['magnetic_moment_b2'] or 0
    radii_b2 = request.form['radii_b2'] or 0

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO elements (name, molecular_weight, oxidation_state_a1, magnetic_moment_a1, radii_a1,
            oxidation_state_a2, magnetic_moment_a2, radii_a2, oxidation_state_b1, magnetic_moment_b1, radii_b1,
            oxidation_state_b2, magnetic_moment_b2, radii_b2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, molecular_weight, oxidation_state_a1, magnetic_moment_a1, radii_a1,
              oxidation_state_a2, magnetic_moment_a2, radii_a2, oxidation_state_b1, magnetic_moment_b1, radii_b1,
              oxidation_state_b2, magnetic_moment_b2, radii_b2))
        conn.commit()
        flash('Element added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Element already exists!', 'error')
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    #todo: update the table content.
    init_db()
    app.run(debug=True)
