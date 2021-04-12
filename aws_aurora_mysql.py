import json
import boto3
import base64
import datetime
import mysql
import mysql.connector
class AuroraMySqlDataBase:

    def __init__(self, aws_secret, dbname=""):
        self.__endpoint_db = aws_secret.get("host")
        self.__port = aws_secret.get("port")
        self.__username = aws_secret.get("username")
        self.__password = aws_secret.get("password")
        if dbname == "": self.__database = aws_secret.get("dbname")
        else: self.__database = dbname
        self.__region_name = aws_secret.get("region")
        print("Try to connect to '" + str(self.__endpoint_db) + "':'" + str(self.__port) + "' with database '" + str(self.__database) + "'")

        self.conn =  mysql.connector.connect(host=self.__endpoint_db, user=self.__username, passwd=self.__password, port=self.__port, database=self.__database,
        ssl_ca="rds-ca-2019-root.pem")
        print("Successfully connected")

        self.cur = self.conn.cursor()


    def beginTransaction(self):
        self.conn.start_transaction()

    def executeSQL(self, sqlStatement):
        self.cur.execute(sqlStatement)

    def endTransaction(self):
        resp = self.conn.commit()

    def selectFromTable(self, cols, table, condition="", dictFormat=False):
        cols = cols.replace(" ", "")
        keys = cols.split(",")
        
        stmt = "select {cols} from {table}"
        stmt = stmt.format(cols=cols, table=table)
        if not(condition == ""): stmt = stmt + " where " + condition 

        self.cur.execute(stmt)
        data = self.cur.fetchall()
        if not dictFormat: return data
        result = []
        for line in data:
            tmp = {}
            for i in range(len(keys)): tmp[keys[i]] = line[i]
            result.append(tmp)
        return result

    def deleteCompleteTable(self, tbl_name):
        stmt = "delete from " + str(tbl_name) + ";"
        self.cur.execute(stmt)

    def insertDictToDB(self, tbl_name, rows):
        i, n = 1, len(rows)
        for row in rows:
            placeholder = ", ".join(["%s"] * len(row))
            stmt = "insert IGNORE into `{table}` ({columns}) values ({values});"
            stmt = stmt.format(table=tbl_name, columns=",".join(row.keys()), values=placeholder)       
            resp = self.cur.execute(stmt, list(row.values()))

    def updateTableWithDict(self, source_tbl, dest_tbl, rows):
        n = len(rows)
        for row in rows:
            reference_col = source_tbl + "_id"
            reference_val = row[reference_col]
            placeholder = ", ".join(["%s"] * len(row))
            stmt = "UPDATE `{table}` set "
            for key in row: stmt = stmt + key + "=%s,"
            stmt = stmt[:-1] + " where " + reference_col + "=" + str(reference_val)
            stmt = stmt.format(table=dest_tbl, columns=",".join(row.keys()), values=placeholder)           
            self.cur.execute(stmt, list(row.values()))