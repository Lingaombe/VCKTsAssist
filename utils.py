import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="Lingaombe@2001", database="VCKTsAssist") 
cursor = conn.cursor(dictionary=True)


def banksToUse(questionBanks):
    mcqBanksToUse = []
    saqBanksToUse = []
    laqBanksToUse = []
    for questionBankID in questionBanks:
        cursor.execute("SELECT * FROM questionBanks where questionBankID=%s;", (questionBankID,))
        bank = cursor.fetchall()
        if bank[0]["questionBankType"] == "mcq":
            mcqBanksToUse.append(bank[0]["questionBankID"])
        if bank[0]["questionBankType"] == "saq":
            saqBanksToUse.append(bank[0]["questionBankID"])
        if bank[0]["questionBankType"] == "laq":
            laqBanksToUse.append(bank[0]["questionBankID"])
    return mcqBanksToUse, saqBanksToUse, laqBanksToUse #imbwera ngati tuple ya questionBankID

def getMCQs(mcqBanksToUse, totalMarks):
    mcqquestions = [] 
    for questionBankID in mcqBanksToUse:
        cursor.execute("SELECT * FROM questions where questionBankID=%s;", (questionBankID,))
        question = cursor.fetchall()
        mcqquestions.append(question[0]["marksInternal"])
    return mcqquestions

def getSAQs(saqBanksToUse, totalMarks):
    saqquestions = [] 
    for questionBankID in saqBanksToUse:
        cursor.execute("SELECT * FROM questions where questionBankID=%s;", (questionBankID,))
        question = cursor.fetchall()
        saqquestions.append(question[0]["marksInternal"])
    return saqquestions

def getLAQs(laqBanksToUse, totalMarks):
    laqquestions = [] 
    for questionBankID in laqBanksToUse:
        cursor.execute("SELECT * FROM questions where questionBankID=%s;", (questionBankID,))
        question = cursor.fetchall()
        laqquestions.append(question[0]["marksInternal"])
    return laqquestions

def assemblePaper(totalMarks, questionBanks, paperStructure):
    mcqBanksToUse, saqBanksToUse, laqBanksToUse = banksToUse(questionBanks)

    if mcqBanksToUse:
        mcqs= getMCQs(mcqBanksToUse, totalMarks)
    if saqBanksToUse:
        saqs = getSAQs(saqBanksToUse, totalMarks)
    if laqBanksToUse:
        laqs = getLAQs(laqBanksToUse, totalMarks)