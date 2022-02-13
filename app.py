import tensorflow as tf
import json
import mysql.connector

model = tf.keras.models.load_model('Ch_model.h5')
with open('final_data.json') as file:
    intents = json.load(file)

import pickle
vect = pickle.load(open("vectoriser.pkl","rb"))

tags = pickle.load(open("tags.pkl","rb"))
x_final = pickle.load(open("x_final.pkl","rb"))

import re
import nltk
# nltk.download('punkt')
from nltk.corpus import stopwords
# nltk.download('stopwords')
stopwords = stopwords.words('english')

from nltk.stem import PorterStemmer
stemmer = PorterStemmer()

import random
from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer().fit(x_final)

def insert_question(Input_question, Tag, Probability):
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

def input_sentence(msg):
  clean_sentece = re.sub('[^a-zA-Z\s\w]','',msg)
  sentence_words = nltk.word_tokenize(clean_sentece)
  processed_sentence = []
  for w in sentence_words:
    if w not in stopwords:
      word = stemmer.stem(w.lower())
      processed_sentence.append(word)

  processed_sentence = ' '.join(processed_sentence)
  return processed_sentence


def identify_intent(msg):
  result = model.predict(vect.transform([input_sentence(msg)]).toarray())
  max_score = max(result[0])
  index = 0
  for score in result:
    for prob in score:
      index +=1
      if prob == max_score:
        break
  return index,prob

def responce(msg):
  output_tag, prob = identify_intent(msg)
  result = tags[output_tag-1]
  for intent in intents['Intents']:
    if intent['tag'] == result:
      insert_question(msg, intent['tag'],str(prob))
      print(msg, intent['tag'],str(prob))
      responce = random.choice(intent['responses'])
      break
  return responce

from flask import Flask, render_template, request

app = Flask(__name__)
app.static_folder = 'static'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return responce(str(userText))

if __name__ == "__main__":
    app.run(debug=True,port=8000)
   