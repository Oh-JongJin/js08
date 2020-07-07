#!/usr/bin/python3
# TODO(Oh Jong jin): Need to change the data to insert.
# required packages: python3-influxdb
#

import random
import time
import threading
from influxdb import InfluxDBClient


def main():
        """
        Select function to call (create, delete, insert)
        """

        print("\n\n-----------Select InfluxDB menu-----------")
        print("1. Create DB\n2. Delete DB\n3. Show DB \n"
              "4. Access 'test' DB, insert value randomly\n"
              "ESC when entering 'q'\n"
              "------------------------------------------")
        while True:
                a = input("> ")
                if a == "1":
                        db_name = input("> Input Database name to create: ")
                        create_db(db_name)
                if a == "2":
                        del_db = input("> Input Database name to delete : ")
                        drop_db(del_db)
                if a == "3":
                        insert_measure()
                if a == "q":
                        exit()
                main()


def create_db(database_name: str, host: str = "192.168.85.129", port: int = 8086):
        """
        Create a database with the name you entered.
        :param database_name: Database name to access internal data.
        :param host: IP address to access 'Grafana'.
        :param port: The port address to access 'Grafana'.
        :return:
        """
        client = InfluxDBClient(host, port)
        try:
                client.create_database(database_name)
                print("create " + database_name)
        except Exception as e:
                print("create except")
                print(e)
                pass
        try:
                client.switch_database(database_name)
                print("switch " + database_name)
        except Exception as e:
                print("switch except")
                print(e)
                return None
        return client


def drop_db(database_name: str, host: str = "192.168.85.129", port: int = 8086):
        """
        Delete a database with the entered name.
        :param database_name: Database name to access internal data.
        :param host: IP address to access 'Grafana'.
        :param port: The port address to access 'Grafana'.
        :return:
        """
        client = InfluxDBClient(host, port)
        try:
                client.drop_database(database_name)
                print("delete " + database_name)
        except Exception as e:
                print("delete except")
                print(e)
                pass
        return client


def insert_measure(host: str = "192.168.85.129", port: int = 8086):
        """
        Check DB, measurement
        :param host: IP address to access 'Grafana'.
        :param port: The port address to access 'Grafana'.
        :return:
        """
        client = InfluxDBClient(host, port)
        # Query statements that print a list of databases.
        rs = client.query("SHOW databases")
        for point in rs.get_points():
                print("Database: " + str(point))
        # Enter one of the printed databases.
        dbname = input("> Select Database: ")
        client.switch_database(dbname)
        rs1 = client.query("SHOW measurements")
        for point in rs1.get_points():
                print("Measurement: " + str(point))
        # Enter one of the printed measurements.
        # tag has '', field hasn't ''.
        measurement_name = input("> Select measurement: ")
        rs2 = client.query(f"SELECT * from {measurement_name}")
        for point in rs2.get_points():
                print(point)
        time.sleep(2)


def auto_run(host="192.168.85.129", port=8086):
        """
        Set the field values in the 'test' DB at random.
        :param host: IP address to access 'Grafana'.
        :param port: The port address to access 'Grafana'.
        :return:
        """
        client = InfluxDBClient(host, port)
        client.switch_database("test")
        value = random.randrange(0, 300)
        point = random.randrange(0, 10)
        ozone = random.uniform(0.001, 0.01)
        points = [
                {"measurement": "access",
                 "tags": {"server_id": "server1"},
                 "fields": {"value": float(value), "point": float(point), "ozone": float(ozone)},
                 "time": time.time_ns()}
        ]
        client.write_points(points=points, protocol="json")
        # Execute 'auto_run' funcion every 10 seconds.
        threading.Timer(10, auto_run).start()
        print("running...")


if __name__ == "__main__":
        # run main() function.
        main()
        # auto_run()
