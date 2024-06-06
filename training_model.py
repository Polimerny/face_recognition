import os
import pickle
import sys
import face_recognition
import cv2
import mysql.connector
from mysql.connector import Error


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


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def create_users(connection, name):
    create_users_query = f"""
        INSERT INTO
          `users` (`name`) #dolzhnost
        VALUES
          ('{name}')
        """

    execute_query(connection, create_users_query)


def train_model_by_img(connection, name):

    if not os.path.exists("dataset_from_video"):
        print("[ERROR] there is no directory 'dataset'")
        sys.exit()

    known_encodings = []
    images = os.listdir("dataset_from_video")

    # print(images)

    for(i, image) in enumerate(images):
        print(f"[+] processing img {i + 1}/{len(images)}")
        print(image)

        face_img = face_recognition.load_image_file(f"dataset_from_video/{image}")
        face_enc = face_recognition.face_encodings(face_img)[0]

        # print(face_enc)

        if len(known_encodings) == 0:
            known_encodings.append(face_enc)
        else:
            for item in range(0, len(known_encodings)):
                result = face_recognition.compare_faces([face_enc], known_encodings[item])
                # print(result)

                if result[0]:
                    known_encodings.append(face_enc)
                    # print("Same person!")
                    break
                else:
                    # print("Another person!")
                    break

    # print(known_encodings)
    # print(f"Length {len(known_encodings)}")

    data = {
        "name": name,
        "encodings": known_encodings
    }

    with open(f"dataset/{name}_encodings.pickle", "wb") as file:
        file.write(pickle.dumps(data))

    for f in os.listdir('dataset_from_video'):
        os.remove(os.path.join('dataset_from_video', f))

    create_users(connection, name)

    return f"[INFO] File {name}_encodings.pickle successfully created"


def take_screenshot_from_video():
    cap = cv2.VideoCapture(0)
    count = 0

    if not os.path.exists("dataset_from_video"):
        os.mkdir("dataset_from_video")

    while True:
        ret, frame = cap.read()
        fps = cap.get(cv2.CAP_PROP_FPS)
        multiplier = fps * 200
        # print(fps)

        if ret:
            frame_id = int(round(cap.get(1)))
            # print(frame_id)
            cv2.imshow("frame", frame)
            k = cv2.waitKey(2000)

            # if frame_id % multiplier == 0:
            #     cv2.imwrite(f"dataset_from_video/{count}.jpg", frame)
            #     print(f"Take a screenshot {count}")
            #     count += 1

            if k == ord(" "):
                cv2.imwrite(f"dataset_from_video/{count}_extra_scr.jpg", frame)
                print(f"Take an extra screenshot {count}")
                count += 1
            elif k == ord("q"):
                print("Q pressed, closing the app")
                break

        else:
            print("[Error] Can't get the frame...")
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    connection = connect_to_db("localhost", "root", "", "db")
    take_screenshot_from_video()
    user_input = input("Введите имя: ")
    print(train_model_by_img(connection, user_input))


if __name__ == '__main__':
    main()
