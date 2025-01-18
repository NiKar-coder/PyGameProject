import sqlite3


class Db:
    def __init__(self, db_name="achievements.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                                login TEXT UNIQUE NOT NULL,
                                password TEXT UNIQUE NOT NULL,
                                level INTEGER,
                                scores INTEGER);''')

        self.connection.commit()

    def login(self, login, password):
        self.cursor.execute(
            "INSERT OR IGNORE INTO Users (login, password) VALUES (?, ?);",
            (login, password))
        self.connection.commit()
        if self.cursor.execute(
                "SELECT * FROM Users WHERE login = ? AND password = ?",
                (login, password)).fetchone() != None:
            print("Login successful")
            return True

    def add_result(self, level, scores):
        try:
            self.cursor.execute(
                "UPDATE Users SET scores = ?, level = ?",
                (scores, level))
            self.connection.commit()
        except sqlite3.IntegrityError as message:
            print("Error!")
            raise SystemExit(message)

    def get_result(self):
        self.cursor.execute(
            "SELECT level FROM Achievements WHERE isPassed = ?", (1,))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()
