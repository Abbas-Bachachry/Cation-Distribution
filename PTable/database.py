import json
import sqlite3

ROOT_PATH = __file__.replace("database.py", '')


def adapt_elementp(element: dict):
    return json.dumps(element)


def convert_elementp(s: str | bytes):
    return json.loads(s)


# Register the adapter and converter
sqlite3.register_adapter(dict, adapt_elementp)
sqlite3.register_converter("ELEMENTP", convert_elementp)


# Create a table, add, delete, and edit it ***************************************
def create_table():
    try:
        conn = sqlite3.connect(ROOT_PATH + 'Ptable.db', detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()
        c.execute("""CREATE TABLE Ptable(
        symbol text primary key,
        z int,
        mass numeric,
        name text,
        properties ELEMENTP
        )""")
        # Commit our command
        conn.commit()
        # Close our connection
        conn.close()
    except sqlite3.OperationalError as e:
        print(e)


def delete_table():
    conn = sqlite3.connect(ROOT_PATH + 'Ptable.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("DROP TABLE Ptable")
    # Commit our command
    conn.commit()
    # Close our connection
    conn.close()


def add_one(symbol, z, mass, name, properties):
    conn = sqlite3.connect(ROOT_PATH + 'Ptable.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("INSERT INTO Ptable VALUES (?,?,?,?,?)", (symbol, z, mass, name, properties))
    # Commit our command
    conn.commit()
    # Close our connection
    conn.close()


def add_list(elemnet_list):
    for e in elemnet_list:
        try:
            add_one(e['symbol'], e['z'], e['w'], e['name'], e['prop'])
        except sqlite3.IntegrityError as err:
            print(f"::{err} {e['symbol']}")


def get(symbol: str, asrow=False):
    print(ROOT_PATH)
    # Create or connect to a database
    conn = sqlite3.connect(ROOT_PATH + 'Ptable.db', detect_types=sqlite3.PARSE_DECLTYPES)
    # Set row_factory to fetch data as dictionaries
    if asrow:
        conn.row_factory = sqlite3.Row
    # create cursor
    c = conn.cursor()
    # Query The Database
    c.execute(f'SELECT * FROM Ptable WHERE symbol="{symbol}"')
    items = c.fetchone()
    # Commit our command
    conn.commit()
    # Close our connection
    conn.close()
    return items


def get_all():
    # Create or connect to a database
    conn = sqlite3.connect(ROOT_PATH + 'Ptable.db', detect_types=sqlite3.PARSE_DECLTYPES)
    # create cursor
    c = conn.cursor()
    # Query The Database
    c.execute(f"SELECT * FROM Ptable")
    items = c.fetchall()
    # Commit our command
    conn.commit()
    # Close our connection
    conn.close()
    return items


def update_one(element):
    conn = sqlite3.connect(ROOT_PATH + 'Ptable.db', detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("""UPDATE Ptable SET
        z = :z,
        mass = :w,
        name = :name,
        properties = :prop
        
        WHERE symbol = :symbol""", element)
    # Commit our command
    conn.commit()
    # Close our connection
    conn.close()


def update_list(elemnet_list):
    for e in elemnet_list:
        try:
            update_one(e)
        except sqlite3.IntegrityError as err:
            print(f"::{err} {e['symbol']}")


def fetch_as_dict():
    # Connect to the database
    conn = sqlite3.connect(ROOT_PATH + 'Ptable.db', detect_types=sqlite3.PARSE_DECLTYPES)
    # Set row_factory to fetch data as dictionaries
    conn.row_factory = sqlite3.Row
    # Create a cursor
    c = conn.cursor()
    # Execute a query
    c.execute('SELECT * FROM Ptable')
    # Fetch data
    rows = c.fetchall()

    # Convert each row to a dictionary
    results = {}
    for row in rows:
        row_dict = {}
        symbol = row['symbol']
        for key in row.keys():
            row_dict[key] = row[key]
        results[symbol] = row_dict

    # Close the connection
    conn.close()
    return results


if __name__ == '__main__':
    # delete_table()
    create_table()

    elist = [
        {
            'symbol': 'Fe',
            'z': 26,
            'w': 55.845,
            'name': 'Iron',
            'prop':
                {
                    2: {
                        'a': {'u': [4, None], 'r': [0.63, None]},
                        'b': {'u': [4, None], 'r': [0.78, None]}
                    },
                    3: {
                        'a': {'u': [5, None], 'r': [0.49, None]},
                        'b': {'u': [5, None], 'r': [0.645, None]}
                    }

                }
        },
        {
            'symbol': 'Co',
            'z': 27,
            'w': 58.933195,
            'name': 'Cobalt',
            'prop':
                {
                    2: {
                        'a': {'u': [3, None], 'r': [0.58, None]},
                        'b': {'u': [3, None], 'r': [0.745, None]}
                    },
                    3: {
                        'a': {'u': [None, None], 'r': [None, None]},
                        'b': {'u': [0, None], 'r': [0.545, None]}
                    }
                }
        },
        {
            'symbol': 'Cr',
            'z': 24,
            'w': 51.9961,
            'name': 'Chromium',
            'prop':
                {
                    2: {
                        'a': {'u': [None, None], 'r': [None, None]},
                        'b': {'u': [None, None], 'r': [None, None]}
                    },
                    3: {
                        'a': {'u': [None, None], 'r': [None, None]},
                        'b': {'u': [3, None], 'r': [0.615, None]}
                    }

                }
        }
    ]

    add_list(elist)
    update_list(elist)
