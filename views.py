from django.shortcuts import render
from datetime import datetime
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
import json
from web3 import Web3, HTTPProvider
import base64
from datetime import date
import ipfsApi

global username, questionList, examList, usersList
global contract, web3
api = ipfsApi.Client(host='http://127.0.0.1', port=5001)

#function to call contract
def getContract():
    global contract, web3
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Proctor.json' #Proctor contract file
    deployed_contract_address = '0xe21Be81A05354644e5c16Bd4C38345f07993090F' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
getContract()

def getUsersList():
    global usersList, contract
    usersList = []
    count = contract.functions.getUserCount().call()
    for i in range(0, count):
        user = contract.functions.getUsername(i).call()
        password = contract.functions.getPassword(i).call()
        phone = contract.functions.getPhone(i).call()
        email = contract.functions.getEmail(i).call()
        usertype = contract.functions.getUserType(i).call()
        usersList.append([user, password, phone, email, usertype])

def getQuestionList():
    global questionList, contract
    questionList = []
    count = contract.functions.getQuestionCount().call()
    for i in range(0, count):
        question_id = contract.functions.getQuestion(i).call()
        questionList.append([question_id])

def getExamList():
    global examList, contract
    examList = []
    count = contract.functions.getPerformanceCount().call()
    for i in range(0, count):
        sname = contract.functions.getStudentName(i).call()
        appear_question = contract.functions.getAppearQuestion(i).call()
        answer = contract.functions.getStudentAnswer(i).call()
        dd = contract.functions.getExamDate(i).call()
        examList.append([sname, appear_question, answer, dd])
getUsersList()
getQuestionList()    
getExamList()

def getMarks(sname):
    global examList
    total = 0
    count = 0
    for i in range(len(examList)):
        elist = examList[i]
        if elist[0] == sname:
            hashcode = elist[1]
            student_answer = elist[2]
            content = api.get_pyobj(hashcode)
            content = content.decode()
            question = content.split("@")            
            if question[5] == student_answer:
                total += 1
            count += 1
            print(str(total)+" "+str(count))
    if total > 0:
        total = total / count
    return round(total, 2) * 100

def ViewStudentMarks(request):
    if request.method == 'GET':
        global examList, username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Question</font></th>'
        output+='<th><font size=3 color=black>Correct Answer</font></th>'
        output+='<th><font size=3 color=black>Student Answer</font></th>'
        output+='<th><font size=3 color=black>Obtained Marks</font></th></tr>'
        for i in range(len(examList)):
            elist = examList[i]
            if elist[0] == username:
                hashcode = elist[1]
                content = api.get_pyobj(hashcode)
                content = content.decode()
                question = content.split("@")
                output+='<tr><td><font size=3 color=black>'+question[0]+'</font></td>'
            output+='<td><font size=3 color=black>'+question[5]+'</font></td>'
            output+='<td><font size=3 color=black>'+elist[2]+'</font></td>'
            if elist[2] == question[5]:
                output+='<td><font size=4 color=green>1</font></td></tr>'
            else:
                output+='<td><font size=4 color=red>0</font></td></tr>'            
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}        
        return render(request,'StudentScreen.html', context)
        

def ViewTeacherMarks(request):
    if request.method == 'GET':
        global usersList
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Student Name</font></th>'
        output+='<th><font size=3 color=black>Marks</font></th></tr>'
        for i in range(len(usersList)):
            ulist = usersList[i]
            if ulist[4] == "Student":
                marks = getMarks(ulist[0])
                output+='<tr><td><font size=3 color=black>'+ulist[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+str(marks)+'</font></td></tr>'
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}        
        return render(request,'TeacherScreen.html', context)

def ViewMarks(request):
    if request.method == 'GET':
        global usersList
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Student Name</font></th>'
        output+='<th><font size=3 color=black>Marks</font></th></tr>'
        for i in range(len(usersList)):            
            ulist = usersList[i]
            if ulist[4] == "Student":
                marks = getMarks(ulist[0])
                output+='<tr><td><font size=3 color=black>'+ulist[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+str(marks)+'</font></td></tr>'
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}        
        return render(request,'AdminScreen.html', context)

def ViewQuestions(request):
    if request.method == 'GET':
        global contentList
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Question</font></th>'
        output+='<th><font size=3 color=black>Option A</font></th>'
        output+='<th><font size=3 color=black>Option B</font></th>'
        output+='<th><font size=3 color=black>Option C</font></th>'
        output+='<th><font size=3 color=black>Option D</font></th>'
        output+='<th><font size=3 color=black>Correct Answer</font></th>'
        for i in range(len(questionList)):
            qlist = questionList[i]
            hashcode = qlist[0]
            content = api.get_pyobj(hashcode)
            content = content.decode()
            question = content.split("@")
            output+='<tr><td><font size=3 color=black>'+question[0]+'</font></td>'
            output+='<td><font size=3 color=black>'+question[1]+'</font></td>'
            output+='<td><font size=3 color=black>'+question[2]+'</font></td>'
            output+='<td><font size=3 color=black>'+question[3]+'</font></td>'
            output+='<td><font size=3 color=black>'+question[4]+'</font></td>'
            output+='<td><font size=3 color=black>'+question[5]+'</font></td></tr>'
        output += "</table><br/><br/><br/><br/>"
        context= {'data':output}        
        return render(request,'AdminScreen.html', context)

def WriteExamAction(request):
    if request.method == 'POST':
        global questionList, username, examList
        dd = str(date.today())
        total = 0
        for i in range(len(questionList)):
            qlist = questionList[i]
            hashcode = qlist[0]
            content = api.get_pyobj(hashcode)
            content = content.decode()
            question = content.split("@")
            user_answer = request.POST.get("t"+str(i+1), False)
            print(user_answer)
            msg = contract.functions.savePerformance(username, hashcode, user_answer, dd).transact()
            tx_receipt = web3.eth.waitForTransactionReceipt(msg)
            examList.append([username, hashcode, user_answer, dd])
            if question[5] == user_answer:
                total += 1
        if total > 0:
            total = total / len(questionList)
        context= {'data':'<font size=3 color=blue>Your total marks = '+str(total)+'</font>'}
        return render(request, 'StudentScreen.html', context)               

def WriteExam(request):
    if request.method == 'GET':
        output = ""
        global questionList, api
        for i in range(len(questionList)):
            qlist = questionList[i]
            hashcode = qlist[0]
            content = api.get_pyobj(hashcode)
            content = content.decode()
            question = content.split("@")
            output += '<tr><td><font size="4" color="black">Question = '+question[0]+'</font></td></tr>'
            output += '<tr><td><font size="3" color="black">'+question[1]+'</font><input type="radio" name="t'+str(i+1)+'" value="'+question[1]+'"/></td></tr>'
            output += '<tr><td><font size="3" color="black">'+question[2]+'</font><input type="radio" name="t'+str(i+1)+'" value="'+question[2]+'"/></td></tr>'
            output += '<tr><td><font size="3" color="black">'+question[3]+'</font><input type="radio" name="t'+str(i+1)+'" value="'+question[3]+'"/></td></tr>'
            output += '<tr><td><font size="3" color="black">'+question[4]+'</font><input type="radio" name="t'+str(i+1)+'" value="'+question[4]+'"/></td></tr>'
            output += '<tr><td></td></tr><tr><td></td></tr>'
        context= {'data1':output}
        return render(request, 'WriteExam.html', context)              

def AddQuestionAction(request):
    if request.method == 'POST':
        global questionList
        question = request.POST.get('t1', False)
        optiona = request.POST.get('t2', False)
        optionb = request.POST.get('t3', False)
        optionc = request.POST.get('t4', False)
        optiond = request.POST.get('t5', False)
        correct = request.POST.get('t6', False)
        data = question+"@"+optiona+"@"+optionb+"@"+optionc+"@"+optiond+"@"+correct
        data = data.encode()
        hashcode = api.add_pyobj(data)
        msg = contract.functions.saveQuestion(hashcode).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
        questionList.append([hashcode])
        context= {'data':'<font size=3 color=blue>Question IPFS hashcode = '+hashcode+' saved in Blockchain with below transaction details</font><br/><br/>'+str(tx_receipt)}
        return render(request, 'AddQuestion.html', context)        

def AddQuestion(request):
    if request.method == 'GET':
        return render(request,'AddQuestion.html', {})

def TeacherLogin(request):
    if request.method == 'GET':
        return render(request,'TeacherLogin.html', {})

def index(request):
    if request.method == 'GET':
        return render(request,'index.html', {})

def AddUser(request):
    if request.method == 'GET':
       return render(request, 'AddUser.html', {})
    
def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})

def StudentLogin(request):
    if request.method == 'GET':
       return render(request, 'StudentLogin.html', {})

def AddUserAction(request):
    if request.method == 'POST':
        global usersList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        usertype = request.POST.get('t5', False)
        status = "none"
        for i in range(len(usersList)):
            users = usersList[i]
            if username == users[0]:
                status = "exists"
                break
        if status == "none":
            msg = contract.functions.saveUser(username, password, contact, email, usertype).transact()
            tx_receipt = web3.eth.waitForTransactionReceipt(msg)
            usersList.append([username, password, contact, email, usertype])
            context= {'data':'<font size=3 color=blue>New '+usertype+' details successfully added to Blockchain with below transaction details</font><br/><br/>'+str(tx_receipt)}
            return render(request, 'AddUser.html', context)
        else:
            context= {'data':'Given username already exists'}
            return render(request, 'AddUser.html', context)

def TeacherLoginAction(request):
    if request.method == 'POST':
        global username, contract, usersList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = 'none'
        for i in range(len(usersList)):
            ulist = usersList[i]
            user1 = ulist[0]
            pass1 = ulist[1]
            if user1 == username and pass1 == password and ulist[4] == "Teacher":
                status = "success"
                break
        if status == 'success':
            output = 'Welcome '+username
            context= {'data':output}
            return render(request, "TeacherScreen.html", context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'TeacherLogin.html', context)
        
def AdminLoginAction(request):
    if request.method == 'POST':
        global username, contract, usersList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = 'none'
        if username == 'admin' and password == 'admin':
            output = 'Welcome '+username
            context= {'data':output}
            return render(request, "AdminScreen.html", context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'AdminLogin.html', context)


def StudentLoginAction(request):
    if request.method == 'POST':
        global username, contract, usersList
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = 'none'
        for i in range(len(usersList)):
            ulist = usersList[i]
            user1 = ulist[0]
            pass1 = ulist[1]
            if user1 == username and pass1 == password and ulist[4] == "Student":
                status = "success"
                break
        if status == 'success':
            output = 'Welcome '+username
            context= {'data':output}
            return render(request, "StudentScreen.html", context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'StudentLogin.html', context)



        







        


        
