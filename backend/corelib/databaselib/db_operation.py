#!/usr/bin/python
# -*- coding: UTF-8 -*-

from loguru import logger
import pyodbc
import psycopg2 as pg2
import psycopg2.extras as pg2Ex
import time
import datetime
import calendar
import traceback
 
class DB():
    def __init__(self, server_name, dbName, username="",password=""):
        self.server_name = server_name
        self.db_name = dbName
        self.username = username
        self.password = password
        self.coxn = None
        self.connected = False
        self.cursor = None
    
    def connect(self):
        """ Connection String should be: 'DRIVER={ODBC Driver 13 for SQL Server};
        SERVER=SHAWNNB\SQLEXPRESS;DATABASE=HDA150;UID=BareissAdmin;PWD=BaAdmin'  """
        try:
            conn_str = r"DRIVER={ODBC Driver 11 for SQL Server};SERVER="+ self.server_name + ";DATABASE="+self.db_name+";UID="+ self.username+";PWD="+self.password+""
            self.coxn = pyodbc.connect(conn_str)
            self.coxn.autocommit = True
            self.cursor = self.coxn.cursor()
            self.connected = True
        except:
            self.connected = False
        return self.connected
    
    def create_table(self, table, fields, types, primary_field=""):
        '''CREATE TABLE TestTable(symbol varchar(15), leverage double, shares integer, price double)'''
        pairs = []
        for f, typ in zip(fields, types):
            if primary_field == f:
                pairs.append(r"{} {} IDENTITY(1,1) PRIMARY KEY".format(f,typ))
            else:
                pairs.append(r"{} {}".format(f,typ))
        data_str = ','.join(map(str, pairs))
        print(data_str)
        exe_str = r"CREATE TABLE {}({})".format(table, data_str)
        self.cursor.execute(exe_str) 
        self.coxn.commit()

    def drop_table(self, table):
        '''DROP TABLE table'''
        exe_str = r"DROP TABLE {};".format(table)
        self.cursor.execute(exe_str) 
        self.coxn.commit()

    def select(self, table, fields="*", condition=""):
        """Sample select query"""
        fileds_str = ','.join(map(str, fields))
        exe_str = r"SELECT {} FROM {} {};".format(fileds_str, table, condition)
        # get columns type in this query table
        col = dict()
        cols = self.cursor.columns(table=table)
        fds = []
        for c in cols:
            fds.append(c.column_name)
            if c.column_name in fields or fields == "*":
                col[c.column_name] = c.type_name

        self.cursor.execute(exe_str) 
        rows =self.cursor.fetchall()

        fmt_all_row = []
        for row in rows:
            fmt_single_row = {}
            for j, r in enumerate(row):
                col_name = fields[j]
                col_type = col[col_name]
                if col_type == 'datetime2':
                    fmt_single_row[col_name] = r.strftime(r"%Y/%m/%d %H:%M:%S.%f")
                else:
                    fmt_single_row[col_name] = r
            fmt_all_row.append(fmt_single_row)
            
        #final_result = [json.dumps(dict(zip(fields,row)), default=str) for row in rows]
        self.coxn.commit()
        return fmt_all_row

    def insert(self, table, fields, data):
        '''Sample insert query'''
        fileds_str = ','.join(map(str, fields))
        # values = ["'{}'".format(x) if type(x) is str else x for x in data]
        # data_str = ','.join(map(str, values))
        para_str = ','.join(map(str, '?'*len(data)))
        # print(data_str)
        exe_str = r"""INSERT INTO {} ({}) VALUES ({});""".format(table, fileds_str, para_str)
        # "insert into products(id, name) values (?, ?)", 'pyodbc', 'awesome library'
        self.cursor.execute(exe_str, data)
        self.coxn.commit()
    
    def update(self, table, fields, data, condition):
        '''UPDATE Table_Name SET Column1_Name = value1, Column2_Name = value2 WHERE condition'''
        values = ["'{}'".format(x) if type(x) is str else x for x in data]
        pairs = []
        for col in fields:
            pairs.append("{}=?".format(col))
        data_str = ','.join(map(str, pairs))
        exe_str = r"""UPDATE {} SET {} {};""".format(table, data_str, condition)
        self.cursor.execute(exe_str, data)
        self.coxn.commit()
    
    def delete(self, table, condition):
        '''DELETE FROM Table_Name WHERE condition'''
        exe_str = r"DELETE FROM {} {};".format(table, condition)
        self.cursor.execute(exe_str)
        self.coxn.commit()

    def execute(self, sql, data=None, to_dict=False, dict_field=[], autoDateToString=False):
        '''return empty list if no result'''
        exe_str = sql
        if exe_str[-1] != ';':
            exe_str = exe_str+';'

        if data:
            self.cursor.execute(exe_str,data)
        else:
            self.cursor.execute(exe_str)
        try:
            rows =self.cursor.fetchall()
        except:
            rows = None
        self.coxn.commit()
        fmt_all_row = []
        if rows:
            for row in rows:
                if to_dict:
                    single_row_dict = {}
                    for k,v in zip(dict_field,row):
                        if autoDateToString and type(v) is datetime.datetime:
                            v = v.strftime('%Y-%m-%d %H:%M:%S')
                        single_row_dict[k] = v
                    fmt_all_row.append(single_row_dict)
                else:
                    fmt_all_row.append([x for x in row])
        return fmt_all_row

    def close(self):
        self.cursor.close()
        self.coxn.close()
    
    def get_fields(self, table):
        exe_str = r"SELECT * FROM {} WHERE 1=0;".format(table)
        self.cursor.execute(exe_str)
        fields=[]
        for row in self.cursor.columns(table=table):
            fields.append(row.column_name)
        return fields

class DB_PG2(DB):
    def __init__(self, server_name, dbName, username="",password="") -> None:
        super().__init__(server_name, dbName, username, password)
    def connect(self):
        try:
            self.coxn = pg2.connect(database=self.db_name, user=self.username,password=self.password,
                                  host = "127.0.0.1",
                                  port = "5432",)
            self.cursor = self.coxn.cursor()
            self.connected = True
        except:
            err = traceback.format_exc()
            print(err)
            self.connected = False
        return self.connected

    def get_columns_format(self, table):
        conn = pg2.connect(database=self.db_name, user=self.username,password=self.password,
                                  host = "127.0.0.1",
                                  port = "5432",)
        cur = conn.cursor(cursor_factory=pg2.extras.DictCursor)
        col={}
        try:
            cur.execute("""select *
                        from information_schema.columns
                        where table_schema NOT IN ('information_schema', 'pg_catalog')
                        order by table_schema, table_name""")
            for row in cur:
                # print("schema: {schema}, table: {table}, column: {col}, type: {type}".format(
                # schema = row['table_schema'], table = row['table_name'],
                # col = row['column_name'], type = row['data_type']))
                if row['table_name'] == table.lower():
                    col[row['column_name']] = row['data_type']
            
            conn.commit()
            cur.close()
            conn.close()
        except:
            err = traceback.format_exc()
            print(err)
            conn.rollback()
        return col
        # print("schema: {schema}, table: {table}, column: {col}, type: {type}".format(
        #     schema = row['table_schema'], table = row['table_name'],
        #     col = row['column_name'], type = row['data_type']))

    def select(self, table, fields="*", condition=""):
        """Sample select query"""
        col = self.get_columns_format(table)
        fileds_str = ','.join(map(str, fields))
        exe_str = r"SELECT {} FROM {} {};".format(fileds_str, table, condition)
        
        fmt_all_row = []
        try:
            self.cursor.execute(exe_str)
            rows =self.cursor.fetchall()
            for row in rows:
                fmt_single_row = {}
                for j, r in enumerate(row):
                    col_name = fields[j]
                    col_type = col[col_name]
                    if col_type == 'datetime2':
                        fmt_single_row[col_name] = r.strftime(r"%Y/%m/%d %H:%M:%S.%f")
                    else:
                        fmt_single_row[col_name] = r
                fmt_all_row.append(fmt_single_row)
            self.coxn.commit()
        except:
            err = traceback.format_exc()
            print(err)
            self.coxn.rollback()
        return fmt_all_row
    
    def insert(self, table, fields, data):
        '''Sample insert query'''
        fileds_str = ','.join(map(str, fields))
        para_arr = []
        for d in data:
            para_arr.append('%s')
        para_str = ','.join(map(str, para_arr))
        exe_str = r"""INSERT INTO {} ({}) VALUES ({});""".format(table, fileds_str, para_str)
        try:
            self.cursor.execute(exe_str, data)
            self.coxn.commit()
        except:
            err = traceback.format_exc()
            print(err)
            self.coxn.rollback()
    
    def update(self, table, fields, data, condition):
        '''UPDATE Table_Name SET Column1_Name = value1, Column2_Name = value2 WHERE condition'''
        pairs = []
        for col in fields:
            pairs.append("{}=%s".format(col))
        data_str = ','.join(map(str, pairs))
        exe_str = r"""UPDATE {} SET {} {};""".format(table, data_str, condition)
        try:
            self.cursor.execute(exe_str, data)
            self.coxn.commit()    
        except:
            err = traceback.format_exc()
            print(err)
            self.coxn.rollback()

    def execute(self, sql, data=None, to_dict=False, dict_field=[], autoDateToString=False, fetch=False):
        '''return empty list if no result'''
        exe_str = sql
        fmt_all_row = []
        rows = None
        if exe_str[-1] != ';':
            exe_str = exe_str+';'
        try:
            if data:
                self.cursor.execute(exe_str,data)
            else:
                self.cursor.execute(exe_str)
            try:
                rows =self.cursor.fetchall()
                for row in rows:
                    if to_dict:
                        single_row_dict = {}
                        for k,v in zip(dict_field,row):
                            if autoDateToString and type(v) is datetime.datetime:
                                v = v.strftime('%Y-%m-%d %H:%M:%S')
                            single_row_dict[k] = v
                        fmt_all_row.append(single_row_dict)
                    else:
                        fmt_all_row.append([x for x in row])
            except pg2.ProgrammingError:
                pass
            self.coxn.commit()
        except:
            err = traceback.format_exc()
            logger.error(err)
            self.coxn.rollback()
        return fmt_all_row

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    hour = sourcedate.hour
    minutes = sourcedate.minute
    seconds = sourcedate.second
    return datetime.datetime(year, month, day, hour,minutes, seconds)


if __name__=="__main__":
    db = DB_PG2(r"bareiss", r"BareissAdmin", r"BaAdmin")
    db.connect("BaOne")
    db.close()