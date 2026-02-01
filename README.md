# 📄 VCKTsAssist

`VCKTsAssist` is a role-based Flask web application to create, manage and generate question papers for educational institutions. It supports role-based access (Teacher, HoD, Examiner), bulk uploads, course/subject management, and automated paper assembly.

**Quick overview of current functionality (as implemented):**

- **Authentication & users:** Signup, login, logout; role-based sessions via `flask-login` (`teacher`, `examiner`, `hod`).
- **Profiles:** View user profile and department/subject info (`/profile`).
- **Streams / Subjects / Courses:** CRUD-like routes for HoD to add/edit/delete subjects and courses (`/editSubjects`, `/addSubject`, `/editSubject`, `/deleteSubject`, `/editCourses`, `/addCourse`, `/editCourse`, `/deleteCourse`).
- **Teachers management:** HoD can list and remove teachers (`/editTeachers`, `/removeTeacher/<id>`).
- **Question banks:** Create and manage question banks (`/addQuestionBank`, `/verifyAddQuestionBank`, `/viewQuestionBanks`, `/editBanks`, `/deleteBank/<id>`).
- **Questions:** Add MCQ and descriptive questions, edit and delete (`/addMcqQuestions`, `/addQuestions`, `/submitQuestion`, `/deleteQuestion/<id>`, `/editQuestions`, `/editMyQuestions`, `/viewQuestions/<bankID>`).
- **Bulk upload:** Upload Excel files to add many questions at once (`/uploadQuestions`) using `pandas` + `openpyxl`. Required columns validated for each bank type.
- **File uploads:** Support for image uploads attached to questions; files saved under `static/uploads` with allowed types: `png,jpg,jpeg,gif,pdf` and max size 16MB.
- **Paper generation:** Generate papers from selected banks and structure (`/generatePaper`, `/paperGenerated`) with support for paper types `INT`, `EXT`, `PR`. Assembling logic implemented in `utils.assemblePaper()` with MCQ/SAQ/LAQ selection and `questionUsed` marking.
- **AJAX endpoints:** `GET /getSubjects/<streamID>`, `GET /getCourses/<subjectID>/<semester>`, `GET /getBanks/<courseID>` return JSON used by the UI.
- **Search & filtering:** Server-side search for question banks (`/search`) and filtered views for banks/papers.
- **Examiner dashboards & analytics:** Examiner-specific pages for reviewing papers, printing papers, and analytics (`/examinerDashboard`, `/reviewPapers`, `/examinerAnalytics`, `/printPaper/<course_id>`).
- **Teacher analytics:** Teacher-specific analytics by subject (`/teacherAnalytics`).
- **HOD pages:** Manage banks, papers, subjects, courses and teachers (`/editBanks`, `/editPapers`, `/editSubjects`, etc.).
- **Error handling:** Custom 404 page (`pageNotFound.html`) and flash messaging across flows.

* 🧑‍🏫 **Teachers**

  * Upload questions manually or as document(excel/word)
  * Generate question papers based on course, pattern, and marks
  * Manage and edit own question bank

* 👩‍💼 **HoD (Head of Department)**

  * Manage courses and department-level teachers
  * Review and delete used or flagged questions
  * Receive alerts when questions are running low

* 🧑‍⚖️ **Examiner**

  * Cross-department access to all papers
  * Print and review generated question papers

* ⚙️ **Question Management**

  * Separate handling for different question types (MCQ, SA, LA, etc.)
  * Duplicate prevention via `used` status
  * Flagging and deletion workflows

## Tech stack & libraries

- Python 3.x
- Flask
- flask-login
- mysql-connector-python
- pandas
- openpyxl
- python-dotenv
- passlib

Check `requirements.txt` for exact pinned versions.

## 📂 Folder Structure

```
VCKTsAssist/
├── app.py                  # Flask entry point
├── templates/              # Jinja2 templates (HTML pages)
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
├── utils/                  # Helper functions, file parsers, etc.
├── requirements.txt        # Python dependencies pip freeze>requirements.txt
├── README.md
└── .env                    # Environment configuration (.gitignore this)
```
## Important files

- `app.py` — main Flask application with routes and business logic.
- `utils.py` — helper functions for assembling papers (`assemblePaper`, `getMCQs`, `getSAQs`, `getLAQs`, `banksToUse`).
- `dash.py` — small helper file (currently minimal).
- `templates/` — Jinja2 templates (pages for login, signup, dashboards, question forms, paper views).
- `static/uploads/` — uploaded files and images.
---

## 🛠️ Setup Instructions

## Running locally (Windows)

### 1. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Clone the Repo
```bash
git clone https://github.com/Lingaombe/VCKTsAssist.git
cd VCKTsAssist
```

### 3. Install Dependencies
* Backend (Flask + MySQL)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file with necessary variables. Remember to `.gitignore` it.


```env
FLASK_APP=app.py
FLASK_ENV=development
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DB=VCKTsAssist
SECRET_KEY=someSecret
```

Ensure the MySQL database schema exists and tables used in `app.py` are created (Users, Streams, Subjects, Courses, questionBanks, questions). The app expects a local MySQL instance by default.

### 5. Run the app:

```bash
python app.py
```

The app runs in debug mode by default when executed directly.


## 🤝 Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

---

## 📄 License

[MIT](LICENSE)

---

## ✨ Acknowledgements

Thanks to educators and curriculum designers who inspired this tool.
