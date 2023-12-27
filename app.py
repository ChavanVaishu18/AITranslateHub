import requests, os, uuid, json
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

from flask import Flask, redirect, url_for, request, render_template, session

app = Flask(__name__)

mydb = mysql.connector.connect(
  host="aayudb.mysql.database.azure.com",
  user="aayushi",
  password="dhanu@123",
  database="ai"
)

mycursor = mydb.cursor()


@app.route('/', methods=['GET'])
def index():
    mycursor.execute("SELECT * FROM histroy")

    myresult = mycursor.fetchall()

    return render_template('index.html', myresult=myresult)

@app.route('/', methods=['POST'])
def index_post():
    # Read the values from the form
    original_text = request.form['text']
    target_language = request.form['language']

    # Load the values from .env
    #key = os.environ['KEY']
    #endpoint = os.environ['ENDPOINT']
    #location = os.environ['LOCATION']

    key="ce9c5786e30b41948e4cf67f276b2e5e"
    endpoint="https://api.cognitive.microsofttranslator.com/"
    location="eastus"

    # Indicate that we want to translate and the API version (3.0) and the target language
    path = '/translate?api-version=3.0'
    # Add the target language parameter
    target_language_parameter = '&to=' + target_language
    # Create the full URL
    constructed_url = endpoint + path + target_language_parameter

    # Set up the header information, which includes our subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # Create the body of the request with the text to be translated
    body = [{ 'text': original_text }]

    # Make the call using post
    translator_request = requests.post(constructed_url, headers=headers, json=body)
    # Retrieve the JSON response
    translator_response = translator_request.json()
    # Retrieve the translation
    translated_text = translator_response[0]['translations'][0]['text']

    # store in the Database
    sql = "INSERT INTO histroy (transated_text, original_text, target_language) VALUES (%s, %s, %s)"
    val = (translated_text, original_text, target_language)
    mycursor.execute(sql, val)

    mydb.commit()

    # Call render template, passing the translated text,
    # original text, and target language to the template
    return render_template(
        'results.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language
    )
