from unittest import case
from flask import *
from getQuestions import *
from app import *
import pandas as pd
import os
import random
import mysql.connector
from dotenv import load_dotenv

load_dotenv() 

import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="Lingaombe@2001", database="VCKTsAssist") 
cursor = conn.cursor(dictionary=True)


if conn.is_connected():
    print("Successfully connected to the database")

app = Flask(__name__)
app.secret_key = os.getenv("secretKey")

def errorCheck():
    print("Connected")

def assemblePaper(mcqNum, saqNum, laqNum, checkedQuestionBanks, paperStructure):
    mcqBanksToUse, saqBanksToUse, laqBanksToUse = banksToUse(checkedQuestionBanks) 
    print(f"MCQ banks to use: {mcqBanksToUse}")
    print(f"SAQ banks to use: {saqBanksToUse}")
    print(f"LAQ banks to use: {laqBanksToUse}")
    mcqs = []
    saqs = []
    laqs = []
    if mcqBanksToUse: 
        print(mcqBanksToUse)
        mcqs = getMCQs(mcqBanksToUse, mcqNum) #tilandira list
    if saqBanksToUse:
        saqs = getSAQs(saqBanksToUse, saqNum)
    if laqBanksToUse and paperStructure in ["PR", "EXT"]:
        laqs = getLAQs(laqBanksToUse, laqNum)
    
    return mcqs, saqs, laqs

def assembleBSc(totalMarks, checkedQuestionBanks, paperStructure): #"INT", "EXT", "PR"
    match paperStructure:
        case "INT":
            mcqNum = 2
            saqNum = 4
            laqNum = 0
        case "EXT":
            mcqNum = 8
            saqNum = 6
            laqNum = 3

    mcqs, saqs, laqs = assemblePaper(mcqNum, saqNum, laqNum, checkedQuestionBanks, paperStructure)

    return mcqs, saqs, laqs

def assembleBCom(totalMarks, checkedQuestionBanks, paperStructure): #trueFalseQuestions extend mcqs
    match paperStructure:
        case "INT":
            mcqNum = 2
            saqNum = 4
            laqNum = 0
        case "EXT":
            mcqNum = 10
            tfNum = 6
            saqNum = 3
            laqNum = 4
    mcqBanksToUse, saqBanksToUse, laqBanksToUse = banksToUse(checkedQuestionBanks)

def assembleBCA(totalMarks, checkedQuestionBanks, paperStructure): 
    match paperStructure:
        case "INT":
            mcqNum = 2
            saqNum = 4
            laqNum = 0
        case "EXT":
            mcqNum = 5
            saqNum = 6
            laqNum = 3

def assembleBA(totalMarks, checkedQuestionBanks, paperStructure):
    match paperStructure:
        case "INT":
            mcqNum = 2
            saqNum = 4
            laqNum = 0
        case "EXT":
            mcqNum = 10
            saqNum = 7
            laqNum = 5

def assembleBBA(totalMarks, checkedQuestionBanks, paperStructure):
    match paperStructure:
        case "INT":
            mcqNum = 2
            saqNum = 4
            laqNum = 0
        case "EXT":
            mcqNum = 8
            saqNum = 6
            laqNum = 3

def assembleBVoc(totalMarks, checkedQuestionBanks, paperStructure): 
    match paperStructure:
        case "INT":
            mcqNum = 2
            saqNum = 4
            laqNum = 0
        case "EXT":
            mcqNum = 8
            saqNum = 6
            laqNum = 3
