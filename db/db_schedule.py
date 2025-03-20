import sqlite3


class DB:
    def __init__(self, name='schedule', create=None):
        self.conn = sqlite3.connect(f'db/{name}')
        self.cur = self.conn.cursor()
        if create:
            self.cur.execute(f'CREATE TABLE {name} {create}')
        self.name = name

    def add_data(self, data):
        self.cur.execute(f'insert into {self.name} values(?, ?, ?, ?)', data)

    def delete(self, data):
        self.cur.execute(f'Delete from {self.name} where {data}')

    def get_data(self, where, select='*'):
        if type(where) == bool:
            return self.cur.execute(f'select {select} from {self.name}').fetchall()
        return self.cur.execute(f'select {select} from {self.name} where {where}').fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
