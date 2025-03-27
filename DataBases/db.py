import sqlite3


class DB:
    def __init__(self, name='C:/Users\Academy\PycharmProjects\ScheduleBot\DataBases\schedule.db', table='schedule', count=5):
        self.conn = sqlite3.connect(name)
        self.cur = self.conn.cursor()
        self.table = table
        self.count = count

    def create(self, data):
        with self.conn:
            self.cur.execute(f'CREATE TABLE if not exists {self.table} {data}')


    def add_data(self, data):
        with self.conn:
            c = ("?," * self.count).replace('')
            self.cur.execute(f'insert into {self.table} values()', data)


    def get_data(self, where, select='*'):
        with self.conn:
            if type(where) == bool:
                return self.cur.execute(f'select {select} from {self.table}').fetchall()
            data = self.cur.execute(f'select {select} from {self.table} where {where}').fetchall()
            return data


    def delete(self, data):
        with self.conn:
            self.cur.execute(f'Delete from {self.table} where {data}')


    def commit(self):
        self.conn.commit()


    def close(self):
        self.conn.close()
