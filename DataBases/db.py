import sqlite3


class DB:
    def __init__(self, name='DataBases/schedule.db', table='schedule', count=7):
        self.conn = sqlite3.connect(name)
        self.cur = self.conn.cursor()
        self.table = table
        self.count = count

    def create(self, data, count=1):
        with self.conn:
            resp = self.cur.execute(f'CREATE TABLE if not exists {self.table} {data}').rowcount
            return resp == count


    def add_data(self, data, queue='', count=0):
        with self.conn:
            c = ("?," * self.count)[::-1].replace(',', '', 1)
            resp = self.cur.execute(f'insert into {self.table} {queue} values({c})', data)
            return resp == count


    def get_data(self, where, select='*', al=True):
        with self.conn:
            if type(where) == bool:
                data = self.cur.execute(f'select {select} from {self.table}').fetchall()
            elif al:
                data = self.cur.execute(f'select {select} from {self.table} where {where}').fetchall()
            else:
                data = self.cur.execute(f'select {select} from {self.table} where {where}').fetchone()
            return data


    def update_db(self, upd, where, count=1):
        with self.conn:
            resp = self.cur.execute(f'Update {self.table} set {upd} where {where}').rowcount
            return resp == count

    def delete(self, data, count=1):
        with self.conn:
            resp = self.cur.execute(f'Delete from {self.table} where {data}')
            return resp == count


    def commit(self):
        self.conn.commit()


    def close(self):
        self.conn.close()
