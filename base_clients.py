import psycopg2
from pprint import pprint

def create_db(conn, cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients(
                id SERIAL PRIMARY KEY,
                name VARCHAR(60),
                lastname VARCHAR(20),
                email VARCHAR(300) NOT NULL);
                """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS numbers(
                 id SERIAL PRIMARY KEY,
                 number VARCHAR(60) NOT NULL,
                 client_id INTEGER NOT NULL REFERENCES clients(id));
                """)
    conn.commit()

def delete_db(cur):
    cur.execute("""DROP TABLE numbers;
                DROP TABLE clients;
                """)
    
def add_clients(cur, first_name, last_name, email, phone = None):
    cur.execute("""INSERT INTO clients(name, lastname, email) VALUES(%s, %s, %s) RETURNING id, name, lastname;
                """, (first_name, last_name, email))
    new_client = cur.fetchone()
    if phone is not None:
        cur.execute("""INSERT INTO numbers(client_id, number) VALUES(%s, %s);
                    """, (new_client[0], phone))
        
def add_phone(conn, cur, client_id, phone):
    cur.execute("""INSERT INTO numbers(client_id, number) VALUES(%s, %s) RETURNING id, number;
                """, (client_id, phone))
    conn.commit()
    print(cur.fetchone())

def change_client(conn, cur, client_id, first_name=None, last_name=None, email=None, phones=None):
    if first_name is not None:
        cur.execute("""UPDATE clients SET name = %s WHERE id = %s
                    """, (first_name, client_id))
    if last_name is not None:
        cur.execute("""UPDATE clients SET lastname = %s WHERE id = %s
                    """, (last_name, client_id))
    if email is not None:
        cur.execute("""UPDATE clients SET email = %s WHERE id = %s
                    """, (email, client_id))
    if phones is not None:
        add_phone(conn, cur, client_id, phones)

    cur.execute("""SELECT * FROM clients;
                """)
    print(cur.fetchall())


def delete_phone(cur, client_id, phone):
    cur.execute("""DELETE FROM numbers WHERE client_id = %s and number = %s;
                """, (client_id, phone,))
    cur.execute("""SELECT * FROM numbers WHERE client_id = %s
                """, (client_id,))
    print (cur.fetchall())

def delete_client(cur, client_id):
    cur.execute("""DELETE FROM numbers WHERE client_id = %s;
                """, (client_id))
    cur.execute("""DELETE FROM clients WHERE id = %s;
                """, (client_id))
    cur.execute("""SELECT * FROM clients;
                """)
    print(cur.fetchall())

def find_client(conn, cur, first_name=None, last_name=None, email=None, phone=None):
    if phone is not None:
        cur.execute("""SELECT cl.id FROM clients cl
                    JOIN numbers nu ON nu.client_id = cl.id
                    WHERE nu.number = %s;
                    """, (phone,))
    else:
        cur.execute("""SELECT id FROM clients
                    WHERE name = %s OR lastname = %s OR email = %s;
                    """, (first_name, last_name, email))
        
    print(cur.fetchall())

if __name__ == '__main__':
    with psycopg2.connect(database='base_clients', user='postgres', password='password') as conn:
        with conn.cursor() as cur:
            delete_db(cur)
            create_db(conn, cur)
            add_clients(cur, 'Николай', 'Петров', 'mihail@mail.com', +7895203654)
            add_clients(cur, 'Василий', 'Алибабаевич', 'vasili@mail.com', +79805642358)
            add_clients(cur, 'Николай', 'Расторгуев', 'nikolai@mail.com')
            add_clients(cur, 'Джордж', 'Лукас', 'georg@mail.com', +785202563254)
            add_phone(conn, cur, '3', '+79201111111')
            change_client(conn, cur, '3', 'Петр')
            change_client(conn, cur, '1', 'Михаил', None, None, None)
            change_client(conn, cur, '4', None, None, None, 112)
            find_client(conn, cur, 'Петр')
            find_client(conn, cur, None, None, None, '112')
            find_client(conn, cur, None, None, 'vasili@mail.com')
            delete_phone(cur, '2', '79805642358')
            delete_client(cur, '2')

conn.close()