import pickle
import sqlite3
from sqlite3 import Error
from datetime import datetime

print(str(datetime.now()))


def create_connection(db_file):
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

"""
A column declared INTEGER PRIMARY KEY will autoincrement.
"""

def main():
    database = "pythonsqlite.db"

    sql_drop_kyc = """
        DROP TABLE IF EXISTS kyc_classification;
    """
    sql_create_kyc_document_table = '''
    CREATE TABLE kyc_classification(
    id integer PRIMARY KEY,
    doc_name TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    extract_text TEXT NOT NULL,
    created_date DATETIME default CURRENT_TIMESTAMP,
    is_adhaar_type TEXT,
    adhaar_num TEXT,
    is_adhaar_name TEXT,
    is_adhaar_dob TEXT,
    is_adhaar_gender TEXT,
    is_adhaar_address TEXT
    );
    '''
    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_drop_kyc)
        create_table(conn, sql_create_kyc_document_table)
    else:
        print("Error! cannot create the database connection.")

    return conn

# db = pickle.load(open('examplePickle.pkl', 'rb'))
# print(db)


def create_project(conn, project):
    sql = "INSERT INTO projects (name, begin_date, end_date) VALUES(?,?,?)"

    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid


def create_kyc_doc(conn, task):
    sql = """INSERT INTO kyc_classification(
    doc_name, doc_type,extract_text,
    is_adhaar_type, adhaar_num, is_adhaar_name,
    is_adhaar_dob, is_adhaar_gender, is_adhaar_address
    ) 
     VALUES (?,?,?,?,?,?,?,?,?)"""

    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

    return cur.lastrowid


# if __name__ == '__main__':
#     main()
#     database = "pythonsqlite.db"
#
#     conn = create_connection(database)
#     with conn:
#         db = pickle.load(open('examplePickle.pkl', 'rb'))
#
#         for md in db:
#             task = (md.doc_name, md.doc_type, '\n'.join(md.extract_text),
#                      str(md.is_adhaar_type), md.adhaar_num, md.is_adhaar_name,
# md.is_adhaar_dob, md.is_adhaar_gender, md.is_adhaar_address)
#             create_kyc_doc(conn, task)
#         # project = ('coll app with sqlite & python', '2015-01-01', '2015-01-30')
#         # project_id = create_project(conn, project)
#         #
#         # task1 = ('Analyze the requirements of the app', 1, 1, project_id, '2015-01-01', '2015-01-02')
#         # task2 = ('Confirm with user about the top requirement', 1, 1, project_id, '2015-01-03', '2015-01-05')
#         #
#         # create_task(conn, task1)
#         # create_task(conn, task2)


