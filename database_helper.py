from contextlib import contextmanager
import sqlite3
import datetime


class DB_helper:
    '''
    Class to do database operations 
    '''
    def __init__(self, db_name=':memory:') -> None:
        self.db_name = db_name

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


    # Add a manager to open and close the connection everytime database method is called. 
    @contextmanager
    def cursor(self):
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = self.dict_factory
            cur = conn.cursor()
            yield cur
            conn.commit()
        finally:
            conn.close()


    def setup(self):
        '''
        Add table if is not allready initialized
        '''
        with self.cursor() as cur:
            stmt = """CREATE TABLE IF NOT EXISTS event (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        robotID text,
                        eventType text ,
                        time TIMESTAMP,
                        flagged INTEGER
                        );"""
            cur.execute(stmt)

            stmt2 = """CREATE TABLE IF NOT EXISTS alarm_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        robotID text,
                        eventType text ,
                        time TIMESTAMP
                        );"""
            cur.execute(stmt2)


    def insert_event(self, robotID, eventype):
        '''
        Insert new item to the event table
        '''
        with self.cursor() as cur:
            stmt = "INSERT INTO event VALUES (:id,:robotID, :eventType, :time, :flagged)"
            args = {'id':None,'robotID': robotID, 'eventType': eventype, 'time': datetime.datetime.now(), "flagged": 0}
            cur.execute(stmt, args)


    def insert_flaggedevent(self, robotID, eventype):
        '''
        Insert new item to the alarm table table
        '''
        with self.cursor() as cur:
            stmt = "INSERT INTO alarm_events VALUES (:id,:robotID, :eventType, :time)"
            args = {'id':None,'robotID': robotID, 'eventType': eventype, 'time': datetime.datetime.now()}
            cur.execute(stmt, args)
         

    def get_all_events(self):
        '''
        Return all added event.
        '''
        with self.cursor() as cur:
            sqlq = "SELECT * FROM event WHERE 1 ORDER BY time DESC;"
            cur.execute(sqlq)
            return cur.fetchall()


    def get_all_alarmevents(self):
        '''
        Return all added event.
        '''
        with self.cursor() as cur:
            sqlq = "SELECT * FROM alarm_events WHERE 1 ORDER BY time DESC;"
            cur.execute(sqlq)
            return cur.fetchall()


    def get_latest_events(self):
        '''
        Return the latest events 
        '''
        with self.cursor() as cur:
            sqlq = "SELECT id, robotID, eventType, MAX(time), flagged FROM event GROUP BY robotID;"
            cur.execute(sqlq)
            return cur.fetchall()


    def update_flagged(self, robID):
        '''
        Update the events table with flagged value
        '''
        with self.cursor() as cur:
            sqlq = f"UPDATE event SET flagged = 1 WHERE id = {robID}"
            cur.execute(sqlq)