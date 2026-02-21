from unittest import case
from flask import *
from assemble import *
from app import *
import pandas as pd
import os
import random
import mysql.connector

conn = mysql.connector.connect(host="localhost", user="root", password="Lingaombe@2001", database="VCKTsAssist") 
cursor = conn.cursor(dictionary=True)

def banksToUse(checkedQuestionBanks):
    mcqBanksToUse = []
    saqBanksToUse = []
    laqBanksToUse = []
    if checkedQuestionBanks:
        placeholders = ",".join(["%s"] * len(checkedQuestionBanks))
        cursor.execute(f"SELECT questionBankID, questionBankType FROM questionBanks WHERE questionBankID IN ({placeholders})", tuple(checkedQuestionBanks))
        
        banks = cursor.fetchall()
        print(f"banks fetched: {banks}")
        for bank in banks:
            if bank["questionBankType"] == "mcq":
                mcqBanksToUse.append(bank["questionBankID"])
            elif bank["questionBankType"] == "saq":
                saqBanksToUse.append(bank["questionBankID"])
            elif bank["questionBankType"] == "laq":
                laqBanksToUse.append(bank["questionBankID"])
    return mcqBanksToUse, saqBanksToUse, laqBanksToUse #imbwera ngati tuple ya questionBankID

def getMCQs(mcqBanksToUse, questionNum):
    # kutenga ma questionID onse mma Bank nkuaika mu IN clause
    placeholders = ",".join(["%s"] * len(mcqBanksToUse))
    qNum = questionNum

    cursor.execute(f"SELECT questionID, questionBankID, questionBody, questionGrade, questionUnit, questionOption1, questionOption2, questionOption3, questionOption4, questionMarks FROM questions WHERE questionBankID IN ({placeholders}) AND questionUsed = FALSE", tuple(mcqBanksToUse)) 

    availableQuestions = cursor.fetchall()
    print(f"Available qs: {availableQuestions}")

    mcqQuestions = []
    basic =[]
    medium = []
    complexQ = []

    # mafunso asakhale mu order yomwe ili mu table
    random.shuffle(availableQuestions)
    print(f"Available qs after shuffle: {availableQuestions}")

    while questionNum > 0 and availableQuestions:
        for question in availableQuestions:
            print(questionNum)
            if question["questionGrade"] == "A" or question["questionGrade"] == "a":
                basic.append({
                "questionBody" : question["questionBody"], 
                "option1" : question["questionOption1"], 
                "option2" : question["questionOption2"],
                "option3" : question["questionOption3"], 
                "option4" : question["questionOption4"]
            })
                questionNum -= 1
                cursor.execute("UPDATE questions SET questionUsed = TRUE WHERE questionID=%s", (question["questionID"],))
                conn.commit()
            elif question["questionGrade"] == "B" or question["questionGrade"] == "b":
                medium.append({
                "questionBody" : question["questionBody"], 
                "option1" : question["questionOption1"], 
                "option2" : question["questionOption2"],
                "option3" : question["questionOption3"], 
                "option4" : question["questionOption4"]
            })
                questionNum -= 1
                cursor.execute("UPDATE questions SET questionUsed = TRUE WHERE questionID=%s", (question["questionID"],))
                conn.commit()
            elif question["questionGrade"] == "C" or question["questionGrade"] == "c":
                complexQ.append({
                "questionBody" : question["questionBody"], 
                "option1" : question["questionOption1"], 
                "option2" : question["questionOption2"],
                "option3" : question["questionOption3"], 
                "option4" : question["questionOption4"]
            })
                questionNum -= 1
                cursor.execute("UPDATE questions SET questionUsed = TRUE WHERE questionID=%s", (question["questionID"],))
                conn.commit()
            if questionNum <= 0:
                break
            # mcqQuestions.append({
            #     "questionBody" : question["questionBody"],
            #     "option1" : question["questionOption1"],
            #     "option2" : question["questionOption2"],
            #     "option3" : question["questionOption3"],
            #     "option4" : question["questionOption4"]
            # })
            # questionNum -= 1
            # print(questionNum)

            # # funso yagwiritsidwa ntchito
            # cursor.execute(
            #     "UPDATE questions SET questionUsed = TRUE WHERE questionID=%s",
            #     (question["questionID"],)
            # )
            # conn.commit()
    print(f"basic: {basic}")
    print(f"medium: {medium}")
    print(f"complex: {complexQ}")
    mcqQuestions.extend(basic)
    mcqQuestions.extend(medium)
    mcqQuestions.extend(complexQ)

    print(f"final qs: {mcqQuestions}")

    return mcqQuestions

def getSAQs(saqBanksToUse, questionNum):

    # kutenga ma questionID onse mma Bank nkuaika mu IN clause
    placeholders = ",".join(["%s"] * len(saqBanksToUse))

    cursor.execute(f"SELECT questionID, questionBankID, questionBody, questionGrade, questionUnit, questionMarks FROM questions WHERE questionBankID IN ({placeholders}) AND questionUsed = FALSE", tuple(saqBanksToUse)) 

    availableQuestions = cursor.fetchall()

    saqQuestions = []

    # mafunso asakhale mu order yomwe ili mu table
    random.shuffle(availableQuestions)

    while questionNum > 0 and availableQuestions:
        for question in availableQuestions:
            print(questionNum)
            saqQuestions.append(question["questionBody"])
            questionNum -= 1

            # funso yagwiritsidwa ntchito
            cursor.execute(
                "UPDATE questions SET questionUsed = TRUE WHERE questionID=%s",
                (question["questionID"],)
            )
            conn.commit()

            if questionNum <= 0:
                break
        print(f"saqs at end of loop: {saqQuestions}")

    return saqQuestions


def getLAQs(laqBanksToUse, questionNum):
    placeholders = ",".join(["%s"] * len(laqBanksToUse))

    cursor.execute(f"SELECT questionID, questionBankID, questionBody, questionGrade, questionUnit, questionMarks FROM questions WHERE questionBankID IN ({placeholders}) AND questionUsed = FALSE", tuple(laqBanksToUse)) 

    availableQuestions = cursor.fetchall()

    laqquestions = []

    # mafunso asakhale mu order yomwe ili mu table
    random.shuffle(availableQuestions)


    for question in availableQuestions:
        if question["questionMarks"] <= questionNum:
            laqquestions.append(question["questionBody"])
            questionNum -= question["questionMarks"]

            # funso yagwiritsidwa ntchito
            cursor.execute(
                "UPDATE questions SET questionUsed = TRUE WHERE questionID=%s",
                (question["questionID"],)
            )
            conn.commit()

        if questionNum <= 0:
            break

    if questionNum <= 0:
        return laqquestions
    else:
        return []