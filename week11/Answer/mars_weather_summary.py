# 평가자분들께 알림 : 

# 1. 다음 패키지들을 반드시 설치해주세요.
# pip install mysql-connector-python matplotlib

# 2. 아래 SQL문을 꼭 MySQL 내에서 실행시켜주세요.
#CREATE DATABASE IF NOT EXISTS mars_db;
# USE mars_db;

# CREATE TABLE IF NOT EXISTS mars_weather (
#     weather_id INT AUTO_INCREMENT PRIMARY KEY,
#     mars_date DATETIME NOT NULL,
#     temp INT,
#     storm INT
# );

import csv
import os
from datetime import datetime
import getpass


import mysql.connector
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, 'mars_weathers_data.csv')
PNG_DIR= os.path.join(BASE_DIR, 'mars_weather_summary.png')

class MySQLHelper:
    """
    Helper for MySQL connections and queries.
    """

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        Establish a connection to the MySQL database.
        """
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()

    def execute(self, query, params=None):
        """
        Execute a single query (INSERT, UPDATE, DELETE).
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        self.connection.commit()
        cursor.close()

    def fetchall(self, query, params=None):
        """
        Execute a SELECT query and fetch all results.
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        return results


def read_csv_file(file_path):
    """
    Read mars weather data from a CSV file.

    Returns:
        List of tuples (mars_date, temp_int, storm_int).
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            mars_date = datetime.strptime(row[1], '%Y-%m-%d')
            temp_int = int(float(row[2]))
            storm_int = int(row[3])
            data.append((mars_date, temp_int, storm_int))
    return data


def insert_data(helper, data_list):
    """
    Insert data into mars_weather table.
    """
    insert_sql = (
        'INSERT INTO mars_weather (mars_date, temp, storm) '
        'VALUES (%s, %s, %s)'
    )
    check_sql = 'SELECT weather_id FROM mars_weather WHERE mars_date = %s'

    for mars_date, temp_int, storm_int in data_list:
        # 중복 체크: 동일한 mars_date가 이미 있으면 건너뜁니다.
        exists = helper.fetchall(check_sql, (mars_date,))
        if exists:
            continue
        helper.execute(insert_sql, (mars_date, temp_int, storm_int))


def generate_summary_image(helper, image_path):
    """
    Query the table and generate a line plot of temperature over time,
    then save as a PNG image.

    Note: The "결과는 png 이미지로 저장" 요구사항은 이 시각화 결과를 가리킵니다.
    """
    query = (
        'SELECT mars_date, temp '
        'FROM mars_weather '
        'ORDER BY mars_date'
    )
    rows = helper.fetchall(query)

    dates = [row[0] for row in rows]
    temps = [row[1] for row in rows]

    plt.figure()
    plt.plot(dates, temps)
    plt.title('Mars Surface Temperature Over Time')
    plt.xlabel('Mars Date')
    plt.ylabel('Temperature (°C)')
    plt.tight_layout()
    plt.savefig(image_path)


def main():
    # --- 사용자 입력으로 MySQL 접속 정보 및 파일 경로 받기 ---
    host = input('MySQL host [localhost]: ') or 'localhost'
    user = input('MySQL user: ')
    password = getpass.getpass('MySQL password: ')
    database = input('Database name [mars_db]: ') or 'mars_db'
    csv_file = CSV_DIR
    output_image = PNG_DIR

    helper = MySQLHelper(host, user, password, database)
    helper.connect()

    # CSV 읽어서 데이터 삽입
    data_list = read_csv_file(csv_file)
    insert_data(helper, data_list)

    # 요약 그래프 생성 및 PNG로 저장
    generate_summary_image(helper, output_image)
    print(f'Data inserted and summary image saved to {output_image}')

    helper.close()


if __name__ == '__main__':
    main()
