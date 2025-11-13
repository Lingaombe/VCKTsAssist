from flask import *
from utils import *
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv() 

import mysql.connector
conn = mysql.connector.connect(host="", user="", password="", database="") 
cursor = conn.cursor(dictionary=True)


if conn.is_connected():
    print("Successfully connected to the database")

app = Flask(__name__)
app.secret_key = os.getenv("secretKey")

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
    


@app.route('/viewQuestionBanks')
def viewQuestionBanks():
    cursor.execute("select * from questionBanks;")
    QuestionBanks = cursor.fetchall()
    print(QuestionBanks)

    return render_template('viewQuestionBanks.html', QuestionBanks=QuestionBanks)


@app.route("/generatePaper")
def generatePaper():

    cursor.execute("SELECT streamID, streamName, streamLevel FROM Streams")
    Streams = cursor.fetchall()
    
    return render_template("generatePaper.html", Streams=Streams)

@app.route("/getBanks/<courseID>")
def getBanks(courseID):

    cursor.execute("SELECT * FROM questionBanks WHERE courseID=%s", (courseID,))
    QuestionBanks = cursor.fetchall()

    return jsonify( QuestionBanks)

@app.post("/paperGenerated")
def paperGenerated():
    paperStream = request.form.get("stream")
    paperSubject = request.form.get("subject")
    paperSemester = request.form.get("semester")
    paperCourse = request.form.get("course")
    checkedQuestionBanks = [int(bank) for bank in request.form.getlist("bankNames")]
    if not checkedQuestionBanks:
        flash("Choose atleast one bank")
        return redirect("/generatePaper")

    paperStructure = request.form.get("marks")

    cursor.execute("SELECT * FROM courses where courseID=%s;", (paperCourse,))
    paper = cursor.fetchone()
    paperSemester = paper["courseSem"]
    paperCourse = paper["courseName"]

    try:
        if paperStructure == "INT":
            totalMarks = paper["marksInternal"]
        elif paperStructure == "EXT":
            totalMarks = paper["marksExternal"]
        elif paperStructure == "PR":
            totalMarks = paper["marksPractical"]
        else:
            flash("Invalid paper structure")
            return redirect("/generatePaper")
    except Exception as e:
        flash(f"Error retrieving marks: {str(e)}")
        return redirect("/generatePaper")
        
    mcqQuestions, saqQuestions, laqQuestions = assemblePaper(totalMarks, checkedQuestionBanks, paperStructure)

    errorCheck()
    cursor.execute("SELECT streamName FROM Streams WHERE streamID=%s;", (paperStream,))
    paperStream = cursor.fetchone()["streamName"]

    cursor.execute("SELECT subjectName FROM Subjects WHERE subjectID=%s;", (paperSubject,))
    paperSubject = cursor.fetchone()["subjectName"]

    paperDetails = [
        paperStream, paperSubject, paperSemester, 
        paperCourse, paperStructure, totalMarks
    ]
    if paperStructure == "INT":
        if not mcqQuestions or not saqQuestions:
            flash("not enough questions in database")
            return redirect("/addQuestionBank")
        else:
            return render_template("paperGenerated.html", paperDetails=paperDetails, mcqQuestions=mcqQuestions, saqQuestions=saqQuestions, laqQuestions=laqQuestions)


    elif paperStructure == "EXT":
        if not mcqQuestions or not saqQuestions or not laqQuestions:
            flash("not enough questions in database")
            return redirect("/addQuestionBank")
        else:
            return render_template("paperGenerated.html", paperDetails=paperDetails, mcqQuestions=mcqQuestions, saqQuestions=saqQuestions, laqQuestions=laqQuestions)
        
    elif paperStructure == "PR":
        if not saqQuestions or not laqQuestions:
            flash("not enough questions in database")
            return redirect("/addQuestionBank")
        else:
            return render_template("paperGenerated.html", paperDetails=paperDetails, mcqQuestions=mcqQuestions, saqQuestions=saqQuestions, laqQuestions=laqQuestions)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('pageNotFound.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
