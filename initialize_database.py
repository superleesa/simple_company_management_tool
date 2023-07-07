import sqlite3

data = [
    ("user1")
]

data = [("user"+x, "pass"+x, "first"+x, "last"+x, "email"+x, False, False) for x in [str(x) for x in range(10)]]

conn = sqlite3.connect("company_database.db")
c = conn.cursor()

sql = "insert into user_table (username, password, first_name, last_name, email_address, is_admin, is_working) values (?, ?, ?, ?, ?, ?, ?)"
c.executemany(sql, data)
conn.commit()
conn.close()
