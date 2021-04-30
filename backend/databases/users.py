import sqlite3


class Users:

    def __init__(self, path="users.db"):
        self.conn = sqlite3.connect(path)

        self.cursor = self.conn.cursor()

        # make table
        command = 'CREATE TABLE IF NOT EXISTS users (username text, password text, email text);'

        self.cursor.execute(command)

    def __contains__(self, username):
        self.cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")

        result = self.cursor.fetchall()

        return len(result)

    def add(self, username, password, email):
        # check username in database
        if username in self:
            print(f'{username} exists')
            return False

        command = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{password}', '{email}')"

        self.cursor.execute(command)

        self.conn.commit()

        return True

    def login(self, username, password):

        command = f"select username, password FROM users WHERE username = '{username}'"
        self.cursor.execute(command)

        result = self.cursor.fetchall()
        if len(result) == 0:
            return False, "User does not exist"

        user = result[0]
        # print(user)

        if user[1] != password:
            return False, "Wrong password"

        return True, ""

    def print_all(self):
        self.cursor.execute("SELECT * FROM users")
        # names = [description[0] for description in self.cursor.description]
        print(self.cursor.fetchall())


if __name__ == '__main__':
    users = Users()
    users.add("Yousef", "password", "ykh@bu.edu")
    users.add("Maxime", "password", "maxime@bu.edu")

    users.print_all()
