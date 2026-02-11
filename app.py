from flask import *
from flask_login import *
from passlib.hash import sha256_crypt
from utils import *
import pandas as pd
from dotenv import load_dotenv
import os
import time
from werkzeug.utils import secure_filename
from openpyxl import load_workbook
import secrets
import smtplib
from datetime import datetime, timedelta

load_dotenv() 

import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="Lingaombe@2001", database="VCKTsAssist") 
cursor = conn.cursor(dictionary=True)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if conn.is_connected():
    print("Successfully connected to the database")

app = Flask(__name__)
app.secret_key = "secretKey"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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

# ============= ZA ALIYENSE =============

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

                return redirect('/main')
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
    subj = current_user.subj
    cursor.execute("SELECT subjectName FROM Subjects WHERE subjectID = %s", (subj,))
    subject = cursor.fetchone()
    return render_template('home.html', username=current_user.username, user_role=current_user.role, subject=subject['subjectName'])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect('/')

@app.route('/profile')
@login_required
def profile():
    # Get user info from database
    cursor.execute("SELECT id, username, email, urole, subjectID FROM Users WHERE id = %s", (current_user.id,))
    user_data = cursor.fetchone()
    
    # Get subject/department name
    subject_name = "N/A"
    if user_data['subjectID']:
        cursor.execute("SELECT subjectName FROM Subjects WHERE subjectID = %s", (user_data['subjectID'],))
        subject_result = cursor.fetchone()
        if subject_result:
            subject_name = subject_result['subjectName']
    
    # Format member since date (using current date as placeholder)
    from datetime import datetime
    member_since = datetime.now().strftime("%B %d, %Y")
    
    user_info = {
        'username': user_data['username'],
        'email': user_data['email'],
        'role': user_data['urole'],
        'subject_id': user_data['subjectID'],
        'department': subject_name
    }
    
    return render_template('profile.html', user=user_info, member_since=member_since, user_role=current_user.role, username=current_user.username)

# ============ ZA MAFUNSO =============

@app.route('/addQuestionBank')
@login_required
def addQuestionBank():
    cursor.execute("SELECT streamID, streamName, streamLevel FROM Streams")
    Streams = cursor.fetchall()

    return render_template("questions/addQuestionBank.html", Streams=Streams, user_role=current_user.role, username=current_user.username)

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
@login_required
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
@login_required
def editQuestions():
    cursor.execute("select * from questionBanks;")
    QuestionBanks = cursor.fetchall()

    return render_template('questions/editQuestions.html', QuestionBanks=QuestionBanks, user_role=current_user.role, username=current_user.username)
    
@app.route('/search')
def search():
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
@login_required
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
    
    return render_template('questions/viewQuestions.html', bank=bank, questions=questions, user_role=current_user.role, username=current_user.username)

@app.route('/viewQuestionBanks')
@login_required
def viewQuestionBanks():
    cursor.execute("select * from questionBanks;")
    QuestionBanks = cursor.fetchall()

    return render_template('questions/viewQuestionBanks.html', QuestionBanks=QuestionBanks, user_role=current_user.role, username=current_user.username)

@app.route('/addMcqQuestions')
@login_required
def addMcqQuestions():
    cursor.execute("SELECT * FROM questionBanks WHERE questionBankType=%s;",("mcq",))
    QuestionBanks = cursor.fetchall()
    return render_template('questions/addMcqQuestions.html', QuestionBanks=QuestionBanks, user_role=current_user.role, username=current_user.username)

@app.route('/addQuestions')
@login_required
def addQuestions():
    cursor.execute("SELECT * FROM questionBanks WHERE questionBankType !=  %s;",("mcq",))
    QuestionBanks = cursor.fetchall()
    return render_template('questions/addQuestions.html', QuestionBanks=QuestionBanks, user_role=current_user.role, username=current_user.username)


@app.route('/uploadQuestions', methods=['GET', 'POST'])
@login_required
def uploadQuestions():
    upload_summary = None
    
    if request.method == 'POST':
        questionBankID = request.form.get('questionBank')
        
        if not questionBankID:
            flash('Please select a question bank', 'danger')
            return redirect('/uploadQuestions')
        
        if 'excelFile' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect('/uploadQuestions')
        
        file = request.files['excelFile']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect('/uploadQuestions')
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            flash('Please upload an Excel file (.xlsx or .xls)', 'danger')
            return redirect('/uploadQuestions')
        
        try:
            # Get question bank type
            cursor.execute("SELECT questionBankType FROM questionBanks WHERE questionBankID=%s", (questionBankID,))
            result = cursor.fetchone()
            if not result:
                flash('Question bank not found', 'danger')
                return redirect('/uploadQuestions')
            
            questionBankType = result['questionBankType']
            
            # Read Excel file
            df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = ['questionBody', 'difficulty', 'unit', 'marks']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                flash(f'Missing required columns: {", ".join(missing_columns)}', 'danger')
                return redirect('/uploadQuestions')
            
            success_count = 0
            failed_count = 0
            errors = []
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    questionBody = str(row['questionBody']).strip()
                    difficulty = str(row['difficulty']).strip().upper()
                    unit = str(int(row['unit'])) if pd.notna(row['unit']) else '1'
                    marks = int(row['marks']) if pd.notna(row['marks']) else 1
                    
                    # Validate difficulty
                    if difficulty not in ['A', 'B', 'C']:
                        errors.append(f"Row {idx+2}: Invalid difficulty '{difficulty}' (must be A, B, or C)")
                        failed_count += 1
                        continue
                    
                    if questionBankType == "mcq":
                        # Check for MCQ options
                        if 'option1' not in df.columns or 'option2' not in df.columns or 'option3' not in df.columns or 'option4' not in df.columns:
                            errors.append(f"Row {idx+2}: MCQ bank requires option1, option2, option3, option4 columns")
                            failed_count += 1
                            continue
                        
                        option1 = str(row['option1']).strip()
                        option2 = str(row['option2']).strip()
                        option3 = str(row['option3']).strip()
                        option4 = str(row['option4']).strip()
                        
                        cursor.execute(
                            "INSERT INTO questions (questionBankID, questionBody, questionGrade, questionUnit, questionOption1, questionOption2, questionOption3, questionOption4, questionMarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                            (questionBankID, questionBody, difficulty, unit, option1, option2, option3, option4, marks)
                        )
                    else:
                        # Descriptive question
                        cursor.execute(
                            "INSERT INTO questions (questionBankID, questionBody, questionGrade, questionUnit, questionMarks) VALUES (%s, %s, %s, %s, %s);",
                            (questionBankID, questionBody, difficulty, unit, marks)
                        )
                    
                    conn.commit()
                    success_count += 1
                
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Row {idx+2}: {str(e)}")
            
            upload_summary = {
                'total': len(df),
                'success': success_count,
                'failed': failed_count,
                'errors': errors[:10]  # Show first 10 errors
            }
            
            flash(f'Upload complete: {success_count} questions added, {failed_count} failed', 'info')
        
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'danger')
            return redirect('/uploadQuestions')
    
    cursor.execute("SELECT * FROM questionBanks")
    QuestionBanks = cursor.fetchall()
    
    return render_template('questions/uploadQuestionsDoc.html', QuestionBanks=QuestionBanks, upload_summary=upload_summary, user_role=current_user.role, username=current_user.username)

# ============= ENI MZINDA =============

@app.route('/submitQuestion', methods=['POST'])
@login_required
def submitQuestion():
    questionBankID = request.form.get("questionBank")
    questionBody = request.form.get("questionText")
    questionMarks = int(request.form.get("marks"))
    questionGrade = request.form.get("difficulty")
    questionUnit = request.form.get("unit")
    
    # Handle file upload
    photo_filename = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to make filename unique
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename
    
    print(questionBankID, questionBody, questionMarks)

    cursor.execute("SELECT questionBankType FROM questionBanks WHERE questionBankID=%s", (questionBankID,))
    questionBankType = cursor.fetchone()["questionBankType"]
    
    try:
        if questionBankType == "mcq":
            option1 = request.form.get("option1")
            option2 = request.form.get("option2")
            option3 = request.form.get("option3")
            option4 = request.form.get("option4")
            cursor.execute("INSERT INTO questions (questionBankID, questionBody, questionGrade, questionPhoto, questionUnit, questionOption1, questionOption2, questionOption3, questionOption4, questionMarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", 
                           (questionBankID, questionBody, questionGrade, photo_filename, questionUnit, option1, option2, option3, option4, questionMarks))
            conn.commit()
            flash("MCQ question added!")
            return redirect("/addMcqQuestions")
        else:
            cursor.execute("INSERT INTO questions (questionBankID, questionBody, questionGrade, questionPhoto, questionUnit, questionMarks) VALUES (%s, %s, %s, %s, %s, %s);", 
                           (questionBankID, questionBody, questionGrade, photo_filename, questionUnit, questionMarks))
            conn.commit()
            flash("Question added!")
            return redirect("/addQuestions")
    except Exception as e:
        flash(f"Error adding question: {str(e)}")
        return redirect("/addQuestionBank")

@app.route("/generatePaper")
@login_required
def generatePaper():

    cursor.execute("SELECT streamID, streamName, streamLevel FROM Streams")
    Streams = cursor.fetchall()
    
    return render_template("generatePaper.html", Streams=Streams, user_role=current_user.role, username=current_user.username)

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
    paperStructure = request.form.get("marks")
    checkedQuestionBanks = [int(bank) for bank in request.form.getlist("bankNames")]
    if not checkedQuestionBanks:
        flash("Choose atleast one bank")
        return redirect("/generatePaper")

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
            return render_template("BSc.html", paperDetails=paperDetails, mcqQuestions=mcqQuestions, saqQuestions=saqQuestions, laqQuestions=laqQuestions) 

    elif paperStructure == "EXT":
        if not mcqQuestions or not saqQuestions or not laqQuestions:
            flash("not enough questions in database")
            return redirect("/addQuestionBank")
        else:
            return render_template("BSc.html", paperDetails=paperDetails, mcqQuestions=mcqQuestions, saqQuestions=saqQuestions, laqQuestions=laqQuestions)
        
    elif paperStructure == "PR":
        if not saqQuestions or not laqQuestions:
            flash("not enough questions in database")
            return redirect("/addQuestionBank")
        else:
            return render_template("BSc.html", paperDetails=paperDetails, mcqQuestions=mcqQuestions, saqQuestions=saqQuestions, laqQuestions=laqQuestions)


# ============= HOD =============

@app.route('/editCourses', methods=['GET', 'POST'])
@login_required
def editCourses():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    # Get all courses with subject names
    cursor.execute("""
        SELECT c.*, s.subjectName 
        FROM Courses c 
        JOIN Subjects s ON c.subjectID = s.subjectID
        WHERE c.subjectID=%s
        ORDER BY c.courseName
    """, (current_user.subj,))
    courses = cursor.fetchall()
    
    cursor.execute("""
        SELECT u.username, u.id as teacherID
        FROM Teachers t
        JOIN Users u on t.TeacherID = u.id
        WHERE u.subjectID = %s
        """, (current_user.subj,))
    teachers = cursor.fetchall()
    print(teachers)

    for course in courses:
        cursor.execute("""
            SELECT u.username
            FROM Teachers t 
            JOIN Users u ON t.teacherID = u.id 
            WHERE t.courseID = %s
        """, (course['courseID'],))
        teacher = cursor.fetchone()
        courses[courses.index(course)]['teacher'] = teacher['username'] if teacher else "Unassigned"
    
    return render_template('hod/manageCourses.html', 
                         courses=courses,
                         teachers = teachers,
                         total_courses=len(courses),
                         department=current_user.subj,
                         username=current_user.username,
                         user_role=current_user.role)

@app.route('/addCourse', methods=['POST'])
@login_required
def addCourse():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        subject_id = current_user.subj
        course_name = request.form.get('courseName')
        semester = request.form.get('semester')
        marks_internal = request.form.get('marksInternal')
        marks_external = request.form.get('marksExternal')
        marks_practical = request.form.get('marksPractical')
        course = request.form.get('courseCode')
        
        cursor.execute("""
            INSERT INTO Courses (subjectID, courseID, courseName, courseSem, marksInternal, marksExternal, marksPractical)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (subject_id, course, course_name, semester, marks_internal, marks_external, marks_practical))
        conn.commit()
        flash(f'Course "{course_name}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding course: {str(e)}', 'danger')
    
    return redirect('/editCourses')

@app.route('/editCourse', methods=['POST'])
@login_required
def editCourseRoute():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        course_id = request.form.get('courseID')
        course_name = request.form.get('courseName')
        subject_id = current_user.subj
        semester = request.form.get('semester')
        marks_internal = request.form.get('marksInternal')
        marks_external = request.form.get('marksExternal')
        marks_practical = request.form.get('marksPractical')
        teacherID = request.form.get('teacher')
        
        cursor.execute("""
            UPDATE Courses 
            SET subjectID=%s, courseName=%s, courseSem=%s, marksInternal=%s, marksExternal=%s, marksPractical=%s
            WHERE courseID=%s
        """, (subject_id, course_name, semester, marks_internal, marks_external, marks_practical, course_id))
        conn.commit()

        cursor.execute("""
            UPDATE Teachers
            SET teacherID = %s
            WHERE courseID = %s
        """, (teacherID, course_id))
        conn.commit()
        flash(f'Course updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating course: {str(e)}', 'danger')
    
    return redirect('/editCourses')

@app.route('/deleteCourse/<course_id>', methods=['GET'])
@login_required
def deleteCourse(course_id):
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        cursor.execute("DELETE FROM Courses WHERE courseID=%s", (course_id,))
        conn.commit()
        flash('Course deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting course: {str(e)}', 'danger')
    
    return redirect('/editCourses')

# ===== TEACHERS =====

@app.route('/assign', methods=['GET'])
@login_required
def assign():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    cursor.execute("SELECT * FROM Users WHERE urole='teacher' ORDER BY username")
    teachers = cursor.fetchall()
    print(teachers)

    cursor.execute("""
        SELECT c.*, s.subjectName 
        FROM Courses c 
        JOIN Subjects s ON c.subjectID = s.subjectID
        ORDER BY c.courseName
    """)
    courses = cursor.fetchall()
    
    return render_template('hod/assignTeacher.html',
                         teachers=teachers,
                         courses=courses,
                         username=current_user.username,
                         user_role=current_user.role)

@app.route('/assignTeacher', methods=['POST'])
@login_required
def assignTeacher():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        teacher_id = request.form.get('teacher')
        course_id = request.form.get('course')
        
        cursor.execute("""
            INSERT INTO Teachers (courseID, teacherID)
            VALUES (%s, %s)
        """, (course_id, teacher_id))  
        conn.commit()
        flash('Teacher assigned to course successfully!', 'success')
    except Exception as e:
        flash(f'Error assigning teacher: {str(e)}', 'danger')
    
    return redirect('/editTeachers')

@app.route('/editTeachers', methods=['GET'])
@login_required
def editTeachers():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    selected_subject = request.args.get('subject', '')
    
    # Get all subjects
    cursor.execute("SELECT * FROM Subjects ORDER BY subjectName")
    subjects = cursor.fetchall()
    
    # Get teachers based on filter
    if selected_subject:
        cursor.execute("""
            SELECT u.*, s.subjectName 
            FROM Users u 
            LEFT JOIN Subjects s ON u.subjectID = s.subjectID
            WHERE u.urole='teacher' AND u.subjectID=%s
            ORDER BY u.username
        """, (selected_subject,))
    else:
        cursor.execute("""
            SELECT u.*, s.subjectName 
            FROM Users u 
            LEFT JOIN Subjects s ON u.subjectID = s.subjectID
            WHERE u.urole='teacher'
            ORDER BY u.username
        """)
    
    teachers = cursor.fetchall()
    
    return render_template('hod/manageTeachers.html',
                         teachers=teachers,
                         subjects=subjects,
                         selected_subject=selected_subject,
                         total_teachers=len(teachers),
                         total_subjects=len(subjects),
                         active_count=len(teachers),
                         username=current_user.username,
                         user_role=current_user.role)

@app.route('/removeTeacher/<int:user_id>', methods=['GET'])
@login_required
def removeTeacher(user_id):
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        cursor.execute("DELETE FROM Users WHERE id=%s AND urole='teacher'", (user_id,))
        conn.commit()
        flash('Teacher removed from department!', 'success')
    except Exception as e:
        flash(f'Error removing teacher: {str(e)}', 'danger')
    
    return redirect('/editTeachers')

# ===== SUBJECTS =====

@app.route('/editSubjects', methods=['GET', 'POST'])
@login_required
def editSubjects():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    # Get all streams
    cursor.execute("SELECT * FROM Streams ORDER BY streamName")
    streams = cursor.fetchall()
    
    # Get all subjects with course counts
    cursor.execute("""
        SELECT s.*, st.streamName, COUNT(c.courseID) as course_count
        FROM Subjects s
        JOIN Streams st ON s.streamID = st.streamID
        LEFT JOIN Courses c ON s.subjectID = c.subjectID
        GROUP BY s.subjectID
        ORDER BY s.subjectName
    """)
    subjects = cursor.fetchall()
    
    return render_template('hod/manageSubjects.html',
                         subjects=subjects,
                         streams=streams,
                         total_subjects=len(subjects),
                         total_streams=len(streams),
                         total_courses=sum([s['course_count'] for s in subjects]),
                         username=current_user.username,
                         user_role=current_user.role)

@app.route('/addSubject', methods=['POST'])
@login_required
def addSubject():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        subject_name = request.form.get('subjectName')
        stream_id = request.form.get('stream')
        
        cursor.execute("""
            INSERT INTO Subjects (subjectName, streamID)
            VALUES (%s, %s)
        """, (subject_name, stream_id))
        conn.commit()
        flash(f'Subject "{subject_name}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding subject: {str(e)}', 'danger')
    
    return redirect('/editSubjects')

@app.route('/editSubject', methods=['POST'])
@login_required
def editSubjectRoute():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        subject_id = request.form.get('subjectID')
        subject_name = request.form.get('subjectName')
        stream_id = request.form.get('stream')
        
        cursor.execute("""
            UPDATE Subjects
            SET subjectName=%s, streamID=%s
            WHERE subjectID=%s
        """, (subject_name, stream_id, subject_id))
        conn.commit()
        flash('Subject updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating subject: {str(e)}', 'danger')
    
    return redirect('/editSubjects')

@app.route('/deleteSubject/<int:subject_id>', methods=['GET'])
@login_required
def deleteSubject(subject_id):
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        cursor.execute("DELETE FROM Subjects WHERE subjectID=%s", (subject_id,))
        conn.commit()
        flash('Subject deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting subject: {str(e)}', 'danger')
    
    return redirect('/editSubjects')

# ===== QUESTION BANKS MANAGEMENT =====

@app.route('/editBanks', methods=['GET'])
@login_required
def editBanks():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    selected_course = request.args.get('course', '')
    selected_type = request.args.get('type', '')
    
    # Get all courses
    cursor.execute("SELECT * FROM Courses ORDER BY courseName")
    courses = cursor.fetchall()
    
    # Get question banks with course names and question counts
    query = """
        SELECT qb.*, c.courseName, COUNT(q.questionID) as question_count
        FROM questionBanks qb
        JOIN Courses c ON qb.courseID = c.courseID
        LEFT JOIN questions q ON qb.questionBankID = q.questionBankID
    """
    params = []
    
    if selected_course or selected_type:
        query += " WHERE "
        conditions = []
        if selected_course:
            conditions.append("qb.courseID=%s")
            params.append(selected_course)
        if selected_type:
            conditions.append("qb.questionBankType=%s")
            params.append(selected_type)
        query += " AND ".join(conditions)
    
    query += " GROUP BY qb.questionBankID ORDER BY c.courseName"
    
    cursor.execute(query, params)
    banks = cursor.fetchall()
    
    return render_template('hod/manageBanks.html',
                         banks=banks,
                         courses=courses,
                         selected_course=selected_course,
                         selected_type=selected_type,
                         username=current_user.username,
                         user_role=current_user.role)

@app.route('/deleteUsedQuestions')
@login_required
def deleteUsedQuestions():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        cursor.execute("DELETE FROM questions WHERE questionUsed = 1 LIMIT 1000;")
        conn.commit()
        flash('Used questions deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting used questions: {str(e)}', 'danger')
    
    return redirect('/editBanks')

@app.route('/deleteBank/<int:bank_id>', methods=['GET'])
@login_required
def deleteBank(bank_id):
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    try:
        # Delete all questions in the bank first
        cursor.execute("DELETE FROM questions WHERE questionBankID=%s", (bank_id,))
        # Delete the bank
        cursor.execute("DELETE FROM questionBanks WHERE questionBankID=%s", (bank_id,))
        conn.commit()
        flash('Question bank deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting bank: {str(e)}', 'danger')
    
    return redirect('/editBanks')

@app.route('/deleteQuestion/<int:question_id>', methods=['GET'])
@login_required
def deleteQuestion(question_id):
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    # Get the question bank ID first
    cursor.execute("SELECT questionBankID FROM questions WHERE questionID=%s", (question_id,))
    result = cursor.fetchone()
    bank_id = result['questionBankID'] if result else None
    
    try:
        cursor.execute("DELETE FROM questions WHERE questionID=%s", (question_id,))
        conn.commit()
        flash('Question deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting question: {str(e)}', 'danger')
    
    return redirect(f'/viewQuestions/{bank_id}') if bank_id else redirect('/editQuestions')

# ===== PAPERS MANAGEMENT =====

@app.route('/editPapers', methods=['GET'])
@login_required
def editPapers():
    if current_user.role != 'hod':
        flash('Unauthorized access', 'danger')
        return redirect('/main')
    
    # Get streams
    cursor.execute("SELECT * FROM Streams ORDER BY streamName")
    streams = cursor.fetchall()
    
    # Placeholder stats (you can implement actual paper tracking later)
    total_papers = 0
    total_courses = 0
    avg_marks = 0
    question_types = 3
    papers = []
    
    return render_template('hod/managePapers.html',
                         streams=streams,
                         papers=papers,
                         total_papers=total_papers,
                         total_courses=total_courses,
                         avg_marks=avg_marks,
                         question_types=question_types,
                         username=current_user.username,
                         user_role=current_user.role)

# ============= EXAMINER ROUTES =============

@app.route('/examinerDashboard')
@login_required
def examinerDashboardRoute():
    if current_user.role != 'examiner':
        flash('Access denied. Examiner only.', 'danger')
        return redirect('/main')
    
    # Get statistics for dashboard
    cursor.execute("SELECT COUNT(*) as count FROM questions")
    total_questions = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM questionBanks")
    total_banks = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM Courses")
    total_courses = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM Subjects")
    total_subjects = cursor.fetchone()['count']
    
    return render_template('examiner/dashboard.html',
                         total_papers=total_courses,
                         total_banks=total_banks,
                         total_questions=total_questions,
                         total_subjects=total_subjects,
                         user_role=current_user.role,
                         username=current_user.username)

@app.route('/reviewPapers', methods=['GET'])
@login_required
def reviewPapers():
    if current_user.role != 'examiner':
        flash('Access denied. Examiner only.', 'danger')
        return redirect('/main')
    
    selected_stream = request.args.get('stream', '')
    selected_subject = request.args.get('subject', '')
    
    # Get all streams
    cursor.execute("SELECT * FROM Streams ORDER BY streamName")
    streams = cursor.fetchall()
    
    # Build query for papers
    query = """
        SELECT DISTINCT 
            c.courseID, c.courseName, c.courseSem, c.marksInternal, c.marksExternal, c.marksPractical,
            s.subjectID, s.subjectName,
            st.streamID, st.streamName,
            COUNT(q.questionID) as questionCount,
            'INT' as paperType
        FROM Courses c
        JOIN Subjects s ON c.subjectID = s.subjectID
        JOIN Streams st ON s.streamID = st.streamID
        LEFT JOIN questionBanks qb ON c.courseID = qb.courseID
        LEFT JOIN questions q ON qb.questionBankID = q.questionBankID
    """
    
    params = []
    where_clauses = []
    
    if selected_stream:
        where_clauses.append("st.streamID = %s")
        params.append(selected_stream)
    
    if selected_subject:
        where_clauses.append("s.subjectID = %s")
        params.append(selected_subject)
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " GROUP BY c.courseID ORDER BY st.streamName, s.subjectName, c.courseName"
    
    cursor.execute(query, params)
    papers = cursor.fetchall()
    
    # Get statistics
    total_papers = len(papers)
    total_subjects = len(set([p['subjectID'] for p in papers]))
    total_courses = len(papers)
    avg_marks = sum([p['marksExternal'] for p in papers]) / len(papers) if papers else 0
    
    return render_template('examiner/reviewPapers.html',
                         papers=papers,
                         streams=streams,
                         selected_stream=selected_stream,
                         selected_subject=selected_subject,
                         total_papers=total_papers,
                         total_subjects=total_subjects,
                         total_courses=total_courses,
                         avg_marks=int(avg_marks),
                         user_role=current_user.role,
                         username=current_user.username)

@app.route('/examinerAnalytics', methods=['GET'])
@login_required
def examinerAnalytics():
    if current_user.role != 'examiner':
        flash('Access denied. Examiner only.', 'danger')
        return redirect('/main')
    
    # Total questions
    cursor.execute("SELECT COUNT(*) as count FROM questions")
    total_questions = cursor.fetchone()['count']
    
    # Total banks
    cursor.execute("SELECT COUNT(*) as count FROM questionBanks")
    total_banks = cursor.fetchone()['count']
    
    # Total courses
    cursor.execute("SELECT COUNT(*) as count FROM Courses")
    total_courses = cursor.fetchone()['count']
    
    # Total subjects
    cursor.execute("SELECT COUNT(*) as count FROM Subjects")
    total_subjects = cursor.fetchone()['count']
    
    
    # Question difficulty distribution
    cursor.execute("""
        SELECT questionGrade as difficulty, COUNT(*) as count
        FROM questions
        GROUP BY questionGrade
    """)
    diff_results = cursor.fetchall()
    total_for_diff = sum([r['count'] for r in diff_results]) if diff_results else 1
    difficulty_dist = [
        {'difficulty': r['difficulty'], 'count': r['count'], 'percentage': (r['count'] / total_for_diff * 100)}
        for r in diff_results
    ]
    
    # Top banks
    cursor.execute("""
        SELECT qb.*, c.courseName, COUNT(q.questionID) as question_count, AVG(q.questionMarks) as avg_marks
        FROM questionBanks qb
        JOIN Courses c ON qb.courseID = c.courseID
        LEFT JOIN questions q ON qb.questionBankID = q.questionBankID
        GROUP BY qb.questionBankID
        ORDER BY question_count DESC
        LIMIT 10
    """)
    top_banks = cursor.fetchall()
    
    # Subject coverage
    cursor.execute("""
        SELECT s.subjectID, s.subjectName, st.streamName, st.streamID,
               COUNT(DISTINCT qb.questionBankID) as bank_count,
               COUNT(q.questionID) as question_count,
               ROUND(AVG(CASE WHEN q.questionMarks IS NOT NULL THEN 1 ELSE 0 END) * 100) as quality_score
        FROM Subjects s
        JOIN Streams st ON s.streamID = st.streamID
        LEFT JOIN Courses c ON s.subjectID = c.subjectID
        LEFT JOIN questionBanks qb ON c.courseID = qb.courseID
        LEFT JOIN questions q ON qb.questionBankID = q.questionBankID
        GROUP BY s.subjectID
        ORDER BY question_count DESC
    """)
    subject_coverage = cursor.fetchall()
    
    return render_template('examiner/analytics.html',
                         total_questions=total_questions,
                         total_banks=total_banks,
                         total_courses=total_courses,
                         total_subjects=total_subjects,
                         difficulty_dist=difficulty_dist,
                         top_banks=top_banks,
                         subject_coverage=subject_coverage,
                         user_role=current_user.role,
                         username=current_user.username)

@app.route('/printPaper/<int:course_id>')
@login_required
def printPaper(course_id):
    if current_user.role != 'examiner':
        flash('Access denied. Examiner only.', 'danger')
        return redirect('/main')
    
    # Get course details
    cursor.execute("""
        SELECT c.*, s.subjectName, st.streamName
        FROM Courses c
        JOIN Subjects s ON c.subjectID = s.subjectID
        JOIN Streams st ON s.streamID = st.streamID
        WHERE c.courseID = %s
    """, (course_id,))
    course = cursor.fetchone()
    
    if not course:
        flash('Course not found', 'danger')
        return redirect('/reviewPapers')
    
    # Get banks for this course
    cursor.execute("SELECT * FROM questionBanks WHERE courseID = %s", (course_id,))
    banks = cursor.fetchall()
    
    # Get all questions from all banks
    questions = []
    for bank in banks:
        cursor.execute("SELECT * FROM questions WHERE questionBankID = %s", (bank['questionBankID'],))
        bank_questions = cursor.fetchall()
        questions.extend(bank_questions)
    
    return render_template('paperGenerated.html',
                         course=course,
                         banks=banks,
                         questions=questions,
                         user_role=current_user.role,
                         username=current_user.username)

# ============= TEACHER ROUTES =============

@app.route('/teacherAnalytics', methods=['GET'])
@login_required
def teacherAnalytics():
    if current_user.role != 'teacher':
        flash('Access denied. Teacher only.', 'danger')
        return redirect('/main')
    
    # Get teacher's questions
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM questions q
        JOIN questionBanks qb ON q.questionBankID = qb.questionBankID
        JOIN Courses c ON qb.courseID = c.courseID
        JOIN Teachers t ON c.courseID = t.courseID
        WHERE t.teacherID = %s
    """, (current_user.id,))
    total_questions = cursor.fetchone()['count']


    # Get teacher's banks
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM questionBanks qb
        JOIN Courses c ON qb.courseID = c.courseID
        JOIN Teachers t ON c.courseID = t.courseID
        WHERE t.teacherID = %s
    """, (current_user.id,))
    total_banks = cursor.fetchone()['count']


    # Question type distribution
    cursor.execute("""
        SELECT q.questionBankType AS type, COUNT(*) AS count
        FROM questionBanks q
        JOIN questions qb ON q.questionBankID = qb.questionBankID
        JOIN Courses c ON q.courseID = c.courseID
        JOIN Teachers t ON c.courseID = t.courseID
        WHERE t.teacherID = %s
        GROUP BY q.questionBankType
    """, (current_user.id,))
    type_results = cursor.fetchall()

    total_for_type = sum([r['count'] for r in type_results]) if type_results else 1
    question_types = [
        {'type': r['type'], 'count': r['count'], 'percentage': (r['count'] / total_for_type * 100)}
        for r in type_results
    ]


    # Difficulty distribution
    cursor.execute("""
        SELECT q.questionGrade AS difficulty, COUNT(*) AS count
        FROM questions q
        JOIN questionBanks qb ON q.questionBankID = qb.questionBankID
        JOIN Courses c ON qb.courseID = c.courseID
        JOIN Teachers t ON c.courseID = t.courseID
        WHERE t.teacherID = %s
        GROUP BY q.questionGrade
    """, (current_user.id,))
    diff_results = cursor.fetchall()

    total_for_diff = sum([r['count'] for r in diff_results]) if diff_results else 1
    difficulty_dist = [
        {'difficulty': r['difficulty'], 'count': r['count'], 'percentage': (r['count'] / total_for_diff * 100)}
        for r in diff_results
    ]


    # Marks distribution
    cursor.execute("""
        SELECT SUM(q.questionMarks) AS total_marks, COUNT(*) AS question_count
        FROM questions q
        JOIN questionBanks qb ON q.questionBankID = qb.questionBankID
        JOIN Courses c ON qb.courseID = c.courseID
        JOIN Teachers t ON c.courseID = t.courseID
        WHERE t.teacherID = %s
    """, (current_user.id,))
    marks_result = cursor.fetchone()

    avg_marks = (
        (marks_result['total_marks'] / marks_result['question_count'])
        if marks_result and marks_result['question_count']
        else 0
    )


    # Top banks
    cursor.execute("""
        SELECT qb.*, c.courseName, COUNT(q.questionID) AS question_count, AVG(q.questionMarks) AS avg_marks
        FROM questionBanks qb
        JOIN Courses c ON qb.courseID = c.courseID
        JOIN Teachers t ON c.courseID = t.courseID
        LEFT JOIN questions q ON qb.questionBankID = q.questionBankID
        WHERE t.teacherID = %s
        GROUP BY qb.questionBankID
        ORDER BY question_count DESC
        LIMIT 10
    """, (current_user.id,))
    top_banks = cursor.fetchall()
    
    # Courses info
    cursor.execute("""
        SELECT c.*, COUNT(DISTINCT qb.questionBankID) AS bank_count, COUNT(q.questionID) AS question_count
        FROM Courses c
        JOIN Teachers t ON c.courseID = t.courseID
        LEFT JOIN questionBanks qb ON c.courseID = qb.courseID
        LEFT JOIN questions q ON qb.questionBankID = q.questionBankID
        WHERE t.teacherID = %s
        GROUP BY c.courseID
        ORDER BY c.courseName
    """, (current_user.id,))
    courses_info = cursor.fetchall()
    
    return render_template('teacher/analytics.html',
                         total_questions=total_questions,
                         total_banks=total_banks,
                         avg_marks=round(avg_marks, 1),
                         question_types=question_types,
                         difficulty_dist=difficulty_dist,
                         top_banks=top_banks,
                         courses_info=courses_info,
                         user_role=current_user.role,
                         username=current_user.username)

@app.route('/myCourses', methods=['GET'])
@login_required           
def myCourses():
    if current_user.role != 'teacher':
        flash('Access denied. Teacher only.', 'danger')
        return redirect('/main')
    
    cursor.execute("""
        SELECT c.*, u.username AS teacherName
        FROM Courses c
        JOIN Teachers t ON c.courseID = t.courseID
        JOIN Users u ON t.teacherID = u.id
        WHERE t.teacherID = %s
        ORDER BY c.courseName;
        """, (current_user.id,))
    courses = cursor.fetchall()
    print(courses)

    return render_template('teacher/myCourses.html', 
                        courses=courses, 
                        user_role=current_user.role, 
                        username=current_user.username)

@app.route('/editMyQuestions', methods=['GET'])
@login_required
def editMyQuestions():
    if current_user.role != 'teacher':
        flash('Access denied. Teacher only.', 'danger')
        return redirect('/main')
    
    # Get only teacher's question banks (from their subject)
    cursor.execute("""
        SELECT qb.*, c.courseName
        FROM questionBanks qb
        JOIN Courses c ON qb.courseID = c.courseID
        JOIN Teachers t ON c.courseID = t.courseID
        WHERE t.TeacherID = %s
        ORDER BY qb.questionBankName
    """, (current_user.id,))
    QuestionBanks = cursor.fetchall()
    
    return render_template('questions/editQuestions.html', 
                         QuestionBanks=QuestionBanks, 
                         user_role=current_user.role, 
                         username=current_user.username)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('pageNotFound.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
