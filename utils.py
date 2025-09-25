from flask import *
from utils import *
import pandas as pd

import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="", database="VCKTsAssist") 
cursor = conn.cursor(dictionary=True)


if conn.is_connected():
    print("Successfully connected to the database")

app = Flask(__name__)
app.secret_key = "744d5ca4b473aa1cda78ae760abd166d255e2e732d1fe5e7f8c88db00e507f1f"

import random

def errorCheck():
    print("Connected")

def assemblePaper(totalMarks, checkedQuestionBanks, paperStructure):
    mcqBanksToUse, saqBanksToUse, laqBanksToUse = banksToUse(checkedQuestionBanks)
    mcqs = []
    saqs = []
    laqs = []
    if mcqBanksToUse:
        mcqs = getMCQs(mcqBanksToUse, totalMarks) #tilandira list
    if saqBanksToUse:
        saqs = getSAQs(saqBanksToUse, paperStructure, totalMarks)
    if laqBanksToUse and paperStructure in ["PR", "EXT"]:
        laqs = getLAQs(laqBanksToUse, totalMarks)
    
    return mcqs, saqs, laqs

    
def banksToUse(checkedQuestionBanks):
    mcqBanksToUse = []
    saqBanksToUse = []
    laqBanksToUse = []
    if checkedQuestionBanks:
        placeholders = ",".join(["%s"] * len(checkedQuestionBanks))
        cursor.execute(f"SELECT questionBankID, questionBankType FROM questionBanks WHERE questionBankID IN ({placeholders})", tuple(checkedQuestionBanks))
        
        banks = cursor.fetchall()
        for bank in banks:
            if bank["questionBankType"] == "mcq":
                mcqBanksToUse.append(bank["questionBankID"])
            elif bank["questionBankType"] == "saq":
                saqBanksToUse.append(bank["questionBankID"])
            elif bank["questionBankType"] == "laq":
                laqBanksToUse.append(bank["questionBankID"])
    return mcqBanksToUse, saqBanksToUse, laqBanksToUse #imbwera ngati tuple ya questionBankID

def getMCQs(mcqBanksToUse, totalMarks):
    mcqMarks = totalMarks // 5 #ikakhala out of 10 marks 2MCQ, 20 4MCQ, 40 8MCQ
    # kutenga ma questionID onse mma Bank nkuaika mu IN clause
    placeholders = ",".join(["%s"] * len(mcqBanksToUse))

    cursor.execute(f"SELECT questionID, questionBankID, questionBody, questionOption1, questionOption2, questionOption3, questionOption4, questionMarks FROM questions WHERE questionBankID IN ({placeholders}) AND questionUsed = FALSE", tuple(mcqBanksToUse)) 

    availableQuestions = cursor.fetchall()

    mcqQuestions = []
    basic =[]
    medium = []
    complexQ = []

    # mafunso asakhale mu order yomwe ili mu table
    random.shuffle(availableQuestions)

    for question in availableQuestions:
        print(mcqMarks)
        if question["questionMarks"] <= mcqMarks:
            if question["questionGrade"] == "A":
                basic.append({
                "questionBody" : question["questionBody"], 
                "option1" : question["questionOption1"], 
                "option2" : question["questionOption2"],
                "option3" : question["questionOption3"], 
                "option4" : question["questionOption4"]
            })
            elif question["questionGrade"] == "B":
                medium.append({
                "questionBody" : question["questionBody"], 
                "option1" : question["questionOption1"], 
                "option2" : question["questionOption2"],
                "option3" : question["questionOption3"], 
                "option4" : question["questionOption4"]
            })
            elif question["questionGrade"] == "C":
                complexQ.append({
                "questionBody" : question["questionBody"], 
                "option1" : question["questionOption1"], 
                "option2" : question["questionOption2"],
                "option3" : question["questionOption3"], 
                "option4" : question["questionOption4"]
            })
            mcqMarks -= question["questionMarks"]
            print(mcqMarks)

            # funso yagwiritsidwa ntchito
            cursor.execute(
                "UPDATE questions SET questionUsed = TRUE WHERE questionID=%s",
                (question["questionID"],)
            )
            conn.commit()

        if mcqMarks <= 0:
            break

    mcqQuestions.extend(basic, medium, complexQ)
    
    if mcqMarks <= 0:
        return mcqQuestions
    else:
        return []

def getSAQs(saqBanksToUse, paperStructure, totalMarks):
    #ikakhale INT 4 kusankha 2, EXT 6 kusankha 4

    # kutenga ma questionID onse mma Bank nkuaika mu IN clause
    placeholders = ",".join(["%s"] * len(saqBanksToUse))

    cursor.execute(f"SELECT questionID, questionBankID, questionBody, questionMarks FROM questions WHERE questionBankID IN ({placeholders}) AND questionUsed = FALSE", tuple(saqBanksToUse)) 

    availableQuestions = cursor.fetchall()

    saqQuestions = []

    # mafunso asakhale mu order yomwe ili mu table
    random.shuffle(availableQuestions)

    if paperStructure == "INT":
        saqMarks = ((totalMarks*4)//5) + 8  #abwere mafunso 4 kusankha awiri, 6 kusankha 4
    elif paperStructure == "EXT":
        saqMarks = ((totalMarks*2)//5) + 8  #abwere mafunso 6 kusankha anayi

    for question in availableQuestions:
        if question["questionMarks"] <= saqMarks:
            saqQuestions.append(question["questionBody"])
            saqMarks -= question["questionMarks"]

            # funso yagwiritsidwa ntchito
            cursor.execute(
                "UPDATE questions SET questionUsed = TRUE WHERE questionID=%s",
                (question["questionID"],)
            )
            conn.commit()

        if saqMarks <= 0:
            break

    if saqMarks <= 0:
        return saqQuestions
    else:
        return []


def getLAQs(laqBanksToUse, totalMarks):
    placeholders = ",".join(["%s"] * len(laqBanksToUse))

    cursor.execute(f"SELECT questionID, questionBankID, questionBody, questionMarks FROM questions WHERE questionBankID IN ({placeholders}) AND questionUsed = FALSE", tuple(laqBanksToUse)) 

    availableQuestions = cursor.fetchall()

    laqquestions = []

    laqMarks = ((totalMarks*4)//5) + 8

    # mafunso asakhale mu order yomwe ili mu table
    random.shuffle(availableQuestions)


    for question in availableQuestions:
        if question["questionMarks"] <= laqMarks:
            laqquestions.append(question["questionBody"])
            laqMarks -= question["questionMarks"]

            # funso yagwiritsidwa ntchito
            cursor.execute(
                "UPDATE questions SET questionUsed = TRUE WHERE questionID=%s",
                (question["questionID"],)
            )
            conn.commit()

        if laqMarks <= 0:
            break

    if laqMarks <= 0:
        return laqquestions
    else:
        return []

