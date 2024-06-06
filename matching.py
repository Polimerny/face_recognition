import os
import face_recognition
import pickle
import cv2
import mysql.connector
from mysql.connector import Error
from datetime import datetime


def connect_to_db(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to mysql db successful")
    except Error as e:
        print(f"The Error '{e}' occurred")

    return connection


def create_db(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("DB successfully created")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def update_visit_time(connection, name, time):
    query = f"""
    UPDATE
      users
    SET 
      visit_time = '{time}'
    WHERE
      name = '{name}'
    """
    execute_query(connection, query)


def attendance(connection, name):
    query = f"""
    UPDATE
        users
    SET
        name = name + 1
    WHERE
        name = '{name}'    
    """
    execute_query(connection, query)


def attendance_time(connection, name):
    query = f"""
        INSERT INTO
          `attendance_time` (`name`, `visit_time`)
        VALUES
          ('{name}', '{datetime.now()}') 
    """
    execute_query(connection, query)


def detect_person_in_video(connection):

    video = cv2.VideoCapture(0)
    video.set(cv2.CAP_PROP_FPS, 60)
    while True:

        ret, image = video.read()

        cv2.imshow("detect_person_in_video is running", image)
        k = cv2.waitKey(20)

        locations = face_recognition.face_locations(image)
        encodings = face_recognition.face_encodings(image, locations)

        for filename in os.listdir('dataset'):
            for face_encoding, face_location in zip(encodings, locations):

                data = pickle.loads(open(f"dataset/{filename}", "rb").read())
                # print(data)

                result = face_recognition.compare_faces(data["encodings"], face_encoding)
                match = None

                if True in result:
                    match = data["name"]
                    print(f"Access permitted. {match}, welcome!")
                    update_visit_time(connection, match, datetime.now())
                    attendance(connection, match)
                    attendance_time(connection, match)
                    return
                else:
                    print("Access denied. Unknown person")
#Эт

        if k == ord("q"):
            print(f"Q pressed, closing the window")
            break


def main():

    connection = connect_to_db("localhost", "root", "", "db")
    detect_person_in_video(connection)
    # create_db_query = "CREATE DATABASE db"
    # create_db(connection, create_db_query)
    # create_users_table = """
    # CREATE TABLE IF NOT EXISTS attendance_time (
    #   id INT AUTO_INCREMENT,
    #   name TEXT NOT NULL,
    #   visit_time DATETIME,
    #   PRIMARY KEY (id)
    # ) ENGINE = InnoDB
    # """
    # execute_query(connection, create_users_table)

    # create_users = """
    # INSERT INTO
    #   `users` (`name`)
    # VALUESq
    #   ('Valentin'),qq
    #   ('Alina')
    # """
    #
    # execute_query(connection, create_users)


if __name__ == '__main__':
    main()
