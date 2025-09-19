from flask import *
import pandas as pd

import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="Lingaombe@2001", database="VCKTsAssist") 
cursor = conn.cursor(dictionary=True)


if conn.is_connected():
    print("Successfully connected to the database")

app = Flask(__name__)
app.secret_key = "744d5ca4b473aa1cda78ae760abd166d255e2e732d1fe5e7f8c88db00e507f1f"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/addQuestionBank')
def addQuestionBank():
    cursor.execute("SELECT streamID, streamName, streamLevel FROM Streams")
    Streams = cursor.fetchall()

    return render_template("addQuestionBank.html", Streams=Streams)

@app.route("/getSubjects/<streamID>")
def getSubjects(streamID):

    cursor.execute("SELECT subjectID, subjectName FROM Subjects WHERE streamID=%s", (streamID,))
    Subjects = cursor.fetchall()
    print(Subjects)

    return jsonify(Subjects)

@app.route("/getCourses/<subjectID>/<semester>")
def getCourses(subjectID, semester):
    
    cursor.execute("SELECT courseID, courseName FROM Courses WHERE subjectID=%s and courseSem=%s", (subjectID, semester))
    Courses = cursor.fetchall()

    return jsonify(Courses)

@app.route('/verifyAddQuestionBank')
def verifyAddQuestionBank():
    questionBankName = request.args.get("bankName")
    bankQuestionType = request.args.get("bankType")
    cursor.execute("use VCKTsAssist;")
    cursor.execute("show tables;")

    #name cleanup
    safeName = "".join(c for c in questionBankName if c.isalnum() or c == "_")
    questionBankName = safeName.lower()
    Name = "".join(c for c in bankQuestionType if c.isalnum() or c == "_")
    bankQuestionType = Name.lower()

    tables = cursor.fetchall()
    questionBanks = []
    for i in tables:
        for j in i:
            questionBanks.append(i[j])
    print(questionBanks)

    if questionBankName not in questionBanks:
        if bankQuestionType == "MCQ":
            cursor.execute("INSERT INTO questionBanks (questionBankName, questionBankType) VALUES (%s, %s);",(questionBankName,bankQuestionType))
            cursor.execute(f"""create table {questionBankName}(
                questionID int primary key auto_increment,
                questionBankType varchar(10) default '{bankQuestionType}',
                questionBody TEXT not null,
                questionOption1 varchar(100) not null,
                questionOption2 varchar(100) not null,
                questionOption3 varchar(100) not null,  
                questionOption4 varchar(100) not null,        
                questionMarks int not null,
                foreign key (questionBankType) references questionBanks(questionBankType)
            );""")
            conn.commit()
            flash(f"✅ Question Bank '{questionBankName}' created successfully!")
            return redirect('/addMcqQuestions')
        
        else:
            cursor.execute("INSERT INTO questionBanks (questionBankName, questionBankType) VALUES (%s, %s);",(questionBankName,bankQuestionType))
            cursor.execute(f"""create table {questionBankName}(
                questionID int primary key auto_increment,
                questionBankType varchar(10) default '{bankQuestionType}',
                questionBody TEXT not null,     
                questionMarks int not null,
                foreign key (questionBankType) references questionBanks(questionBankType)
            );""")
            conn.commit()
            flash(f"✅ Question Bank '{questionBankName}' created successfully!")
            return redirect('/addQuestions')
    else:
        flash("❌Name already exists, please pick another name")
        return redirect('/addQuestionBank')

    

@app.route('/addMcqQuestions')
def addMcqQuestions():
    cursor.execute("select * from questionBanks;")
    QuestionBanks = cursor.fetchall()
    return render_template('addMcqQuestions.html', QuestionBanks=QuestionBanks)

@app.route('/addQuestions')
def addQuestions():
    cursor.execute("select * from questionBanks;")
    QuestionBanks = cursor.fetchall()
    return render_template('addQuestions.html', QuestionBanks=QuestionBanks)


@app.route('/viewQuestionBanks')
def viewQuestionBanks():
    cursor.execute("select * from questionBanks;")
    QuestionBanks = cursor.fetchall()
    print(QuestionBanks)

    return render_template('viewQuestionBanks.html', QuestionBanks=QuestionBanks)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('pageNotFound.html'), 404


if __name__ == '__main__':
    app.run(debug=True)