import sqlite3


class DB:
    def __init__(self, name='C:/Users/nam1k/PycharmProjects/ScheduleBot/DataBases/schedule.db', table='schedule', count=6):
        self.conn = sqlite3.connect(name)
        self.cur = self.conn.cursor()
        self.table = table
        self.count = count

    def create(self, data):
        with self.conn:
            self.cur.execute(f'CREATE TABLE if not exists {self.table} {data}')


    def add_data(self, data, queue=''):
        with self.conn:
            c = ("?," * self.count)[::-1].replace(',', '', 1)
            self.cur.execute(f'insert into {self.table} {queue} values({c})', data)


    def get_data(self, where, select='*', al=True):
        with self.conn:
            if type(where) == bool:
                data = self.cur.execute(f'select {select} from {self.table}').fetchall()
            elif al:
                data = self.cur.execute(f'select {select} from {self.table} where {where}').fetchall()
            else:
                data = self.cur.execute(f'select {select} from {self.table} where {where}').fetchone()
            return data


    def update_db(self, upd, where):
        with self.conn:
            self.cur.execute(f'Update {self.table} set {upd} where {where}')


    def delete(self, data):
        with self.conn:
            self.cur.execute(f'Delete from {self.table} where {data}')


    def commit(self):
        self.conn.commit()


    def close(self):
        self.conn.close()
