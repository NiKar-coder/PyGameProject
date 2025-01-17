import sqlite3


class Db:
    def __init__(self, db_name="achievements.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Achievements (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                level INTEGER NOT NULL,
                                isPassed INTEGER NOT NULL)''')
        self.connection.commit()

    def add_result(self, level, scores):
        try:
            self.cursor.execute(
                "UPDATE Achievements SET scores = ? WHERE level = ?",
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
