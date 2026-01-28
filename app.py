from flask import *
from flask_login import *
from passlib.hash import sha256_crypt
from utils import *
from dash import *
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
app.secret_key = "secretKey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email, role, subj):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.subj = subj

@login_manager.user_loader
def load_user(id):
    cursor.execute("SELECT * FROM Users WHERE id = %s", (id,))
    user = cursor.fetchone()

    if user:
        return User(id=user['id'], username=user['username'], email=user['email'], role=user['urole'], subj=user['subjectID'])
    return None

@app.route('/')
def login():            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    cursor.execute("SELECT streamID, streamName, streamLevel FROM Streams")
    Streams = cursor.fetchall()
    return render_template('signup.html', Streams=Streams)

@app.route('/handleSignup', methods=['POST'])
def handleSignup():
    if request.method == 'POST':
        username = request.form['user']
        email = request.form['mail']
        role = request.form['userR']
        subj = request.form['subject']
        password = sha256_crypt.encrypt(request.form['pass'])
                
        # Check if email already exists
        cursor.execute("SELECT * FROM Users WHERE email = %s", [email])
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Email already exists', 'danger')
            return redirect('/signup')
        
        # Insert new user
        cursor.execute("INSERT INTO Users (username, email, upassword, urole, subjectID) VALUES (%s, %s, %s, %s, %s)", 
                   (username, email, password, role, subj))
        conn.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect('/')
    return redirect('/signup')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        mail = request.form['email']
        password_candidate = request.form['password']
                
        # Get user by email
        result = cursor.execute("SELECT * FROM Users WHERE email = %s", (mail,))
        data = cursor.fetchone()
        print(data)
        
        if data:
            password = data['upassword']
            
            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                user = User(id=data['id'], username=data['username'], role=data['urole'], email=data['email'], subj=data['subjectID'])
                login_user(user)
                flash('You are now logged in', 'success')

                if current_user.role == 'hod':
                    return redirect('hodDashboard')
                if current_user.role == 'examiner':
                    return redirect('examinerDashboard')
                if current_user.role == 'teacher':
                    return redirect('teacherDashboard')
                else:
                    flash('Invalid user role', 'danger')
                    print('Invalid user role')
                    return render_template('/editor.html')
            else:
                flash('Invalid password', 'danger')
                return redirect('/')
        else:
            flash('User not found', 'danger')
            return redirect('/')
    return redirect('/')

@app.route('/main')
@login_required
def main():
    return render_template('home.html', username=current_user.username, user_role=current_user.role, subject=current_user.subj)

@app.route('/teacherDashboard')
@login_required
def teacherDashboard():     
    return render_template('teacher/dashboard.html', username=current_user.username)

@app.route('/examinerDashboard')
@login_required
def examinerDashboard():
    return render_template('examiner/dashboard.html', username=current_user.username)

@app.route('/hodDashboard')
@login_required
def hodDashboard():
    return render_template('hod/dashboard.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect('/')

@app.route('/addQuestionBank')
@login_required
def addQuestionBank():
    cursor.execute("SELECT streamID, streamName, streamLevel FROM Streams")
    Streams = cursor.fetchall()

    return render_template("questions/addQuestionBank.html", Streams=Streams)

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

@app.route('/editQuestions')
def editQuestions():
    cursor.execute("select * from questionBanks;")
    QuestionBanks = cursor.fetchall()

    return render_template('questions/editQuestions.html', QuestionBanks=QuestionBanks)
    
@app.route('/search')
def search():
    # simple server-side search across name, type and courseID
    q = request.args.get('search', '').strip()
    if q:
        like = f"%{q}%"
        cursor.execute(
            "SELECT * FROM questionBanks WHERE questionBankName LIKE %s OR questionBankType LIKE %s OR courseID LIKE %s;",
            (like, like, like)
        )
        QuestionBanks = cursor.fetchall()
    else:
        cursor.execute("select * from questionBanks;")
        QuestionBanks = cursor.fetchall()

    return render_template('questions/editQuestions.html', QuestionBanks=QuestionBanks)
    
@app.route('/viewQuestions/<int:questionBankID>')
def viewQuestions(questionBankID):
    # Get the question bank details
    cursor.execute("SELECT * FROM questionBanks WHERE questionBankID=%s", (questionBankID,))
    bank = cursor.fetchone()
    
    if not bank:
        flash("Question bank not found")
        return redirect('/editQuestions')
    
    # Get all questions in this bank
    cursor.execute("SELECT * FROM questions WHERE questionBankID=%s", (questionBankID,))
    questions = cursor.fetchall()
    
    return render_template('questions/viewQuestions.html', bank=bank, questions=questions)

@app.route('/addMcqQuestions')
def addMcqQuestions():
    cursor.execute("SELECT * FROM questionBanks WHERE questionBankType=%s;",("mcq",))
    QuestionBanks = cursor.fetchall()
    return render_template('questions/addMcqQuestions.html', QuestionBanks=QuestionBanks)

@app.route('/addQuestions')
def addQuestions():
    cursor.execute("SELECT * FROM questionBanks WHERE questionBankType !=  %s;",("mcq",))
    QuestionBanks = cursor.fetchall()
    return render_template('questions/addQuestions.html', QuestionBanks=QuestionBanks)


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
            option1 = request.form.get("option1")
            option2 = request.form.get("option2")
            option3 = request.form.get("option3")
            option4 = request.form.get("option4")
            cursor.execute("INSERT INTO questions (questionBankID, questionBody, questionOption1, questionOption2, questionOption3, questionOption4, questionMarks) VALUES (%s, %s, %s, %s, %s, %s, %s);", 
                           (questionBankID, questionBody, option1, option2, option3, option4, questionMarks))
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

    return render_template('questions/viewQuestionBanks.html', QuestionBanks=QuestionBanks)


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
    paperCode = paper["courseID"]
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

    if paperSemester == "I" or paperSemester == "II":
        paperYear = "I"
    elif paperSemester == "1II" or paperSemester == "IV":
        paperYear = "II"
    elif paperSemester == "V" or paperSemester == "VI":
        paperYear = "III"
    else:
        paperYear = "IV"

    paperDetails = [
        paperStream, paperSubject, paperSemester, paperCourse, 
        paperStructure, totalMarks, paperYear, paperCode
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


#dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('hod/dashboard.html')

@app.route('/editCourses')
def editCourses():
    return render_template('hod/editCourses.html')

@app.route('/handleCourses', methods=['POST'])
def handle():
    x = handleCourses()
    return render_template('index.html')

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('pageNotFound.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
