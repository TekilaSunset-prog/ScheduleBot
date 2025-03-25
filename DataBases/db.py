import sqlite3


class DB:
    def __init__(self, name='schedule.sqlite'):
        self.conn = sqlite3.connect(f'{name}')
        self.cur = self.conn.cursor()
        self.name = name.replace('.sqlite', '')

    def create(self, name, data):
        self.cur.execute(f'CREATE TABLE if not exists {name} {data}')

    def add_data(self, data):
        self.cur.execute(f'insert into {self.name} values(?, ?, ?, ?, ?)', data)

    def get_data(self, where, select='*'):
        if type(where) == bool:
            return self.cur.execute(f'select {select} from {self.name}').fetchall()
        data = self.cur.execute(f'select {select} from {self.name} where {where}').fetchall()
        if data:
            return data
        return []


    def delete(self, data):
        self.cur.execute(f'Delete from {self.name} where {data}')

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


class ScheduleDB(DB):
    def count_rems(self, user_id):
        sp = super().get_data(f'user_id like {user_id}', select='user_id')
        if not sp:
            return 0
        last = sp[len(sp) - 1]
        return last[len(last) - 1]
