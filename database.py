from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'elements.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM elements')
    elements = cursor.fetchall()
    conn.close()
    return render_template('list.html', elements=elements)


@app.route('/add')
def add():
    return render_template('add.html', element=None)


@app.route('/edit/<name>')
def edit(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM elements WHERE name = ?', (name,))
    element = cursor.fetchone()
    conn.close()
    return render_template('add.html', element=element)


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

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.form['edit_mode'] == 'true':
        cursor.execute('''
            UPDATE elements
            SET molecular_weight = ?, oxidation_state_a1 = ?, magnetic_moment_a1 = ?, radii_a1 = ?,
                oxidation_state_a2 = ?, magnetic_moment_a2 = ?, radii_a2 = ?,
                oxidation_state_b1 = ?, magnetic_moment_b1 = ?, radii_b1 = ?,
                oxidation_state_b2 = ?, magnetic_moment_b2 = ?, radii_b2 = ?
            WHERE name = ?
        ''', (molecular_weight, oxidation_state_a1, magnetic_moment_a1, radii_a1,
              oxidation_state_a2, magnetic_moment_a2, radii_a2,
              oxidation_state_b1, magnetic_moment_b1, radii_b1,
              oxidation_state_b2, magnetic_moment_b2, radii_b2, name))
        flash(f'Element {name} updated successfully!')
    else:
        try:
            cursor.execute('''
                INSERT INTO elements (name, molecular_weight, oxidation_state_a1, magnetic_moment_a1, radii_a1,
                                      oxidation_state_a2, magnetic_moment_a2, radii_a2,
                                      oxidation_state_b1, magnetic_moment_b1, radii_b1,
                                      oxidation_state_b2, magnetic_moment_b2, radii_b2)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, molecular_weight, oxidation_state_a1, magnetic_moment_a1, radii_a1,
                  oxidation_state_a2, magnetic_moment_a2, radii_a2,
                  oxidation_state_b1, magnetic_moment_b1, radii_b1,
                  oxidation_state_b2, magnetic_moment_b2, radii_b2))
            flash(f'Element {name} added successfully!')
        except sqlite3.IntegrityError:
            flash(f'Element {name} already exists in the database!')

    conn.commit()
    conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    # todo: update the table content.
    init_db()
    app.run(debug=True, port=4000)
