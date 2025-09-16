from flask import *
import pandas as pd

import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="Lingaombe@2001", database="VCKTsAssist") 
cursor = conn.cursor()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)