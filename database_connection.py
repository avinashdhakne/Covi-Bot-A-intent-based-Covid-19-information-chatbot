from ast import If
import mysql.connector

def insert_record(Input_question, Tag, Probability):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='vit',
                                             user='root',
                                             password='root')
        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO Chatbot (Input_question, Tag, Probability)
                                VALUES (%s, %s, %s) """
        record = (Input_question, Tag, Probability)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        print("Record inserted successfully into student table")
    except mysql.connector.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


if __name__ == "__main__":
    insert_record("test","record","---")


