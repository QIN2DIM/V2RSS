__all__ = ['FlowTransferStation', 'FlowTransferStation1']

import sqlite3
from typing import Tuple, List

import pymysql

from src.BusinessCentralLayer.setting import SQLITE3_CONFIG, logger, MYSQL_CONFIG


@logger.catch()
class FlowTransferStation:
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
            return self.conn.cursor().execute('select * from %s;', (self.table,)).fetchall()


class FlowTransferStation1:
    def __init__(self, flower_config=None):
        if flower_config is None:
            flower_config = MYSQL_CONFIG
        self.table_name = ['v2raycs', ]

        self.conn, self.cursor = self.__prepare__(flower_config)

        self.__init_tables__()

    @staticmethod
    def __prepare__(flower_config: dict) -> Tuple[pymysql.connections.Connection, pymysql.cursors.Cursor]:
        _conn = pymysql.connect(
            host=flower_config['host'],
            user=flower_config['user'],
            passwd=flower_config['password'],
            db=flower_config['db'])
        _cursor = _conn.cursor()

        return _conn, _cursor

    def __init_tables__(self):
        for table_name in self.table_name:
            if table_name == 'v2raycs':
                sql = f'CREATE TABLE IF NOT EXISTS {table_name} (' \
                      'domain VARCHAR(255) NOT NULL ,' \
                      'subs VARCHAR(255) NOT NULL,' \
                      'class_ VARCHAR(20) NOT NULL,' \
                      'end_life VARCHAR(255) NOT NULL,' \
                      'res_time VARCHAR(255) NOT NULL,' \
                      'passable varchar(10) not null,' \
                      'username VARCHAR(255) NOT NULL,' \
                      'password VARCHAR(255) NOT NULL,' \
                      'email  VARCHAR(255) NOT NULL,' \
                      'uuid VARCHAR(255) NOT NULL PRIMARY KEY)'

                self.cursor.execute(sql)

    def push_info(self, user: dict or List[dict]):
        if isinstance(user, dict):
            user = [user, ]
        elif not isinstance(user, list):
            logger.warning('MySQL add_user 调用格式有误')

        try:
            for user_ in user:
                try:
                    sql = 'INSERT INTO v2raycs (' \
                          'domain, subs, class_,end_life,res_time,passable,username,password,email,uuid) VALUES (' \
                          '%s, %s, %s,%s, %s, %s,%s, %s, %s,%s)'
                    val = (user_["domain"], user_["subs"], user_['class_'], user_['end_life'], user_["res_time"],
                           user_['passable'], user_['username'], user_["password"], user_['email'], user_['uuid'])
                    self.cursor.execute(sql, val)
                except KeyError as e:
                    logger.warning(f"MySQL数据解析出错，user:dict必须同时包含username、password以及email的键值对{e}")
                    # return 702
                except pymysql.err.IntegrityError as e:
                    logger.warning(f'{user_["username"]} -- 用户已在库，若需修改用户信息，请使用更新指令{e}')
                    # return 701
                else:
                    logger.success(f'{user_["username"]} -- 用户添加成功')
                    # return 700
        finally:
            self.conn.commit()
            self.conn.close()

    def update_info(self):
        pass

    def beat_synchronization(self):
        """
        节拍同步
        @return:
        """
        pass


if __name__ == '__main__':
    FlowTransferStation1()
