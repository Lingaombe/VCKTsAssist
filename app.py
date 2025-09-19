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
    courseID = request.args.get("course")

    #name cleanup
    safeName = "".join(c for c in questionBankName if c.isalnum() or c == "_")
    questionBankName = safeName.lower()
    typeName = "".join(c for c in bankQuestionType if c.isalnum() or c == "_")
    bankQuestionType = typeName.lower()

    cursor.execute("SELECT questionBankName FROM questionBanks;")
    questionBanks = [row["questionBankName"] for row in cursor.fetchall()]

    if questionBankName in questionBanks:
        flash("Name already exists, please pick another name")
        return redirect('/addQuestionBank')
    
    try:
        cursor.execute(
            "INSERT INTO questionBanks (courseID, questionBankType, questionBankName) VALUES (%s, %s, %s);",
            (courseID, bankQuestionType, questionBankName)
        )
        conn.commit()
        flash(f"Question Bank '{safeName}' created successfully!")

        if bankQuestionType == "mcq":
            return redirect('/addMcqQuestions')
        else:
            return redirect('/addQuestions')

    except Exception as e:
        flash(f"Error creating question bank: {str(e)}")
        return redirect('/addQuestionBank')

    
@app.route('/addMcqQuestions')
def addMcqQuestions():
    cursor.execute("SELECT * FROM questionBanks WHERE questionBankType=%s;",("mcq",))
    QuestionBanks = cursor.fetchall()
    return render_template('addMcqQuestions.html', QuestionBanks=QuestionBanks)

@app.route('/addQuestions')
def addQuestions():
    cursor.execute("SELECT * FROM questionBanks WHERE questionBankType !=  %s;",("mcq",))
    QuestionBanks = cursor.fetchall()
    return render_template('addQuestions.html', QuestionBanks=QuestionBanks)


@app.route('/submitQuestion', methods=['POST'])
def submitQuestion():
    questionBankID = request.form.get("questionBank")
    questionBody = request.form.get("questionText")
    questionMarks = int(request.form.get("marks"))
    print(questionBankID, questionBody, questionMarks)

    cursor.execute("SELECT questionBankType FROM questionBanks WHERE questionBankID=%s", (questionBankID,))
    questionBankType = cursor.fetchone()["questionBankType"]
    
    try:
        if questionBankType == "mcq":
            options = request.form.getlist("option")
            cursor.execute("INSERT INTO questions (questionBankID, questionBody, questionOption1, questionOption2, questionOption3, questionOption4, questionMarks) VALUES (%s, %s, %s, %s, %s, %s, %s);", 
                           (questionBankID, questionBody, *options, questionMarks))
            conn.commit()
            flash("MCQ question added!")
            return redirect("/addMcqQuestions")
        else:
            cursor.execute("INSERT INTO questions (questionBankID, questionBody, questionMarks) VALUES (%s, %s, %s);", 
                           (questionBankID, questionBody, questionMarks))
            conn.commit()
            flash("Question added!")
            return redirect("/addQuestions")
    except Exception as e:
        flash(f"Error adding question: {str(e)}")
        return redirect("/addQuestionBank")
    
    return "Question submitted"


@app.route('/viewQuestionBanks')
def viewQuestionBanks():
    cursor.execute("select * from questionBanks;")
    QuestionBanks = cursor.fetchall()
    print(QuestionBanks)

    return render_template('viewQuestionBanks.html', QuestionBanks=QuestionBanks)


#ngati yagwiritsidwa kale ntchito
# cursor.execute("""
#     UPDATE questions
#     SET questionUsed = TRUE
#     WHERE questionID = %s
# """, (questionID,))
# conn.commit()
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('pageNotFound.html'), 404


if __name__ == '__main__':
    app.run(debug=True)