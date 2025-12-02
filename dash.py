from flask import *
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv() 

import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="Lingaombe@2001", database="VCKTsAssist") 
cursor = conn.cursor(dictionary=True)


if conn.is_connected():
    print("Successfully connected to the database")

app = Flask(__name__)
app.secret_key = os.getenv("secretKey")

def handleCourses():
    intMarks = request.form.get('int')
    extMarks = request.form.get('ext')
    subName = request.form.get('subName')
    subName = request.form.get('subName')

    print("howdy")
    b = ["hellloe","e"]
    return b