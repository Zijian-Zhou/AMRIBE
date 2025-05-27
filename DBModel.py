import json

import pymysql

class Model:
    def __init__(self):
        self.Conf = self._Get_DBconf()
        self.Engine_name = self.Conf["engine"]
        if self.Engine_name != "mysql":
            raise Exception("Only MySQL is supported!")
        self.DBConf = {
            'host': self.Conf["host"],
            'port': self.Conf["port"],
            'user': self.Conf["user"],
            'password': self.Conf["pwd"],
            'database': self.Conf["dbname"],
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.Connection = self.Connect()

    def _GET_DBconf(self):
        pass

    def Destroy(self):
        self.Connection.close()

    def Connect(self):
        try:
            connect = pymysql.connect(**self.DBConf)
            return connect
        except Exception as e:
            raise Exception("Failed At Database connection. ", str(e))

    def ExecuteWithCommit(self, sql, op):
        try:
            with self.Connection.cursor() as cursor:
                cursor.execute(sql)
                self.Connection.commit()
        except Exception as e:
            raise Exception("Failed At %s \"%s\". " % (op, sql), str(e))

    def Execute(self, sql, op):
        try:
            with self.Connection.cursor() as cursor:
                cursor.execute(sql)
                if op == "SELECT":
                    result = cursor.fetchall()
                    return result
        except Exception as e:
            raise Exception("Failed At %s \"%s\". " % (op, sql), str(e))

    def Insert(self, table, pairs):
        keys = ""
        for idx in range(len(pairs[0])):
            keys += "%s, " % pairs[0][idx]

        sql = "INSERT INTO %s (%s) VALUES %s" % (table, keys[:-2], pairs[1])

        self.ExecuteWithCommit(sql, "INSERT")

    def Update(self, table, set_commands, conditions):
        sql = "UPDATE %s SET %s WHERE %s" % (table, str(set_commands), str(conditions))
        self.ExecuteWithCommit(sql, "UPDATE")

    def Delete(self, table, conditions):
        sql = "DELETE FROM %s WHERE %s" % (table, str(conditions))
        self.ExecuteWithCommit(sql, "DELETE")

    def Get(self, sql):
        return self.Execute(sql, "SELECT")

    def Counter(self, table):
        return self.Execute("SELECT COUNT(*) FROM %s" % table, "SELECT")[0]["COUNT(*)"]


class AC_Model(Model):
    def __init__(self):
        super().__init__()

    def _Get_DBconf(self):
        conf = None
        with open("conf.json", "r") as f:
            conf = json.load(f)
            conf = conf["AC"]["DB"]
        return conf


if __name__ == "__main__":
    print(AC_Model().Conf)