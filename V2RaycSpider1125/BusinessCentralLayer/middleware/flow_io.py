import sqlite3
from config import SQLITE3_CONFIG, logger


@logger.catch()
class FlowTransferStation(object):
    def __init__(self, database_config: dict = None, docker=None):
        """
        @param docker: 接收一个写死的容器名 docker ，类型为List[Tuple(),...]
        @param database_config:
        @param docker:
        """

        self.database = database_config if database_config else SQLITE3_CONFIG
        self.db = self.database.get('db')
        self.table = self.database.get('table')
        self.header = self.database.get('header')

        self.docker = docker

        self.conn = self.__prepare__()

    def __prepare__(self, ) -> sqlite3.Connection:
        with sqlite3.connect(self.db) as conn:
            sql = f'create table if not exists {self.table}({self.header})'
            conn.execute(sql)
        return conn

    def add(self):
        if isinstance(self.docker, list) and self.docker:
            sep = ",".join(['?'] * (len(self.docker[0])))
            try:
                with self.conn:
                    self.conn.executemany(f"insert into {self.table} values ({sep})", self.docker)
            except sqlite3.IntegrityError:
                pass

    def __del__(self):
        ...

    def __update__(self):
        ...

    def fetch_all(self) -> list:
        """

        @return:
        """
        with self.conn:
            return self.conn.cursor().execute(f'select * from {self.table}').fetchall()
