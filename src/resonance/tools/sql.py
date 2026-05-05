import sqlite3

#def EXEC(database, command):
#    conn = sqlite3.connect(database)
#    cur = conn.cursor()

#    cur.execute(command)
#    result = cur.fetchall()

#    conn.commit()
#    conn.close()
#    return result

def EXEC(database, query, params=None, fetch=True) -> list:
    print("PARAMS:", params)
    try:
        with sqlite3.connect(database) as conn:
            cur = conn.cursor()
            cur.execute(query, params or ())

            if fetch:
                return cur.fetchall()
            return []

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
