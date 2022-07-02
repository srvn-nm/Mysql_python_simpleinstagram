import random
import textwrap
import mysql.connector as mysql
from datetime import datetime
import smtplib
import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase

db = mysql.connect(
    host = "localhost",
    user = "root",
 
    db = "datacamp"
)
cursor = db.cursor()
# cursor.execute("CREATE DATABASE datacamp")
cursor.execute("use datacamp")
cursor.execute("DROP TABLE IF EXISTS limited_users")
cursor.execute("DROP TABLE IF EXISTS log_wrongPassword")
cursor.execute("DROP TABLE IF EXISTS log_login")
cursor.execute("DROP TABLE IF EXISTS messages")
cursor.execute("DROP TABLE IF EXISTS request")
cursor.execute("DROP TABLE IF EXISTS blocked")
cursor.execute("DROP TABLE IF EXISTS friends")
cursor.execute("DROP TABLE IF EXISTS users")


# try:
cursor.execute("CREATE TABLE users (uname VARCHAR(255) not null, ulname  VARCHAR(255) not null, userID VARCHAR(255) NOT NULL UNIQUE, phone VARCHAR(255) not null unique, email VARCHAR(255) not null unique, upassword VARCHAR(255) not null, useccheck VARCHAR(255) UNIQUE NOT NULL, timing VARCHAR(255) not null, log_in INT DEFAULT 0, PRIMARY KEY(userID, useccheck))")
cursor.execute("CREATE TABLE friends (u1ID VARCHAR(255), u2ID VARCHAR(255), fID INT AUTO_INCREMENT PRIMARY KEY, FOREIGN KEY(u1ID) REFERENCES users(userID), FOREIGN KEY(u2ID) REFERENCES users(userID))")
cursor.execute("CREATE TABLE blocked (blockerID VARCHAR(255), blockedID VARCHAR(255), bID INT AUTO_INCREMENT PRIMARY KEY, timing VARCHAR(255), FOREIGN KEY(blockerID) REFERENCES users(userID), FOREIGN KEY(blockedID) REFERENCES users(userID))")
cursor.execute("CREATE TABLE request (u1ID VARCHAR(255), u2ID VARCHAR(255), fID INT, bID INT, friendship SMALLINT, message SMALLINT, block SMALLINT, iID INT AUTO_INCREMENT PRIMARY KEY, FOREIGN KEY(u1ID) REFERENCES users(userID), FOREIGN KEY(fID) REFERENCES friends(fID), FOREIGN KEY(bID) REFERENCES blocked(bID), FOREIGN KEY(u2ID) REFERENCES users(userID))")
cursor.execute("CREATE TABLE messages (senderID VARCHAR(255), rID VARCHAR(255), timing VARCHAR(255), textmsg VARCHAR(255), seen SMALLINT DEFAULT 0, liked SMALLINT DEFAULT 0, mID INT NOT NULL AUTO_INCREMENT PRIMARY KEY, FOREIGN KEY(senderID) REFERENCES users(userID), FOREIGN KEY(rID) REFERENCES users(userID))")
cursor.execute("CREATE TABLE log_login (userID VARCHAR(255), useccheck VARCHAR(255), loginAttempts INT DEFAULT 0, timing VARCHAR(255), newPass VARCHAR(255), FOREIGN KEY(userID) REFERENCES users(userID), FOREIGN KEY(useccheck) REFERENCES users(useccheck))")
cursor.execute("CREATE TABLE log_wrongPassword (userID VARCHAR(255), useccheck VARCHAR(255), timing VARCHAR(255), attempts INT DEFAULT 0, FOREIGN KEY(userID) REFERENCES users(userID), FOREIGN KEY(useccheck) REFERENCES users(useccheck))")
cursor.execute("CREATE TABLE limited_users (userID VARCHAR(255), timing VARCHAR(255), FOREIGN KEY(userID) REFERENCES users(userID))")

# except Exception as e:
#     print(e)

def register(name, lname, ID, phoneNo, gmail, password):
    checking = False
    for i in password:
        if i.isalpha():
            checking = True
            break
    while not checking:
        print("Password should have alphabets, too!\ntry again:\n")
        password = input()
        for i in password:
            if i.isalpha():
                checking = True
                break
    checking2 = False
    for i in phoneNo:
        if i.isalpha():
            checking2 = True
            break
    while checking2:
        print("phone should not have alphabets!\ntry again:\n")
        phoneNo = input()
        for i in phoneNo:
            if i.isalpha():
                checking2 = True
                break
    checking3 = False
    for i in name:
        if i.isnumeric():
            checking3 = True
            break
    while checking3:
        print("Name should have alphabets!\ntry again:\n")
        name = input()
        for i in name:
            if i.isnumeric():
                checking3 = True
                break
    checking4 = False
    for i in lname:
        if i.isnumeric():
            checking4 = True
            break
    while checking4:
        print("Last name should have alphabets!\ntry again:\n")
        lname = input()
        for i in lname:
            if i.isnumeric():
                checking4 = True
                break
    while gmail.isnumeric() or not gmail.endswith("@gmail.com"):
        print("Email should be a valid gmail address!\ntry again:\n")
        gmail = input()
    current_time = datetime.now().strftime("%H:%M:%S")
    temp = 1
    seccheck = input("what is your favorite color?")
    try:
        Q1 ="INSERT INTO users (uname, ulname, userID, phone, email, upassword, useccheck, timing , log_in) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (name, lname, ID, phoneNo, gmail, password, seccheck, current_time, temp)
        cursor.execute(Q1, values)
        db.commit()
    except Exception as e:
        print(e)
    sendMail(gmail,"succsessfully registered!^-^",f"Hi {name}.\nYou are a member of our family now!<3")
    print("succsessfully registered!^-^\n"+f"Hi {name}.\nYou are a member of our family now!<3")
    menu(ID)
    
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    if attachmentFile:
        message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    else: 
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"

def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_bytes())}

def createMessageWithAttachment(
    sender, to, subject, msgHtml, msgPlain, attachmentFile):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msgHtml: Html message to be sent
      msgPlain: Alternative plain text message for older email clients          
      attachmentFile: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    messageA = MIMEMultipart('alternative')
    messageR = MIMEMultipart('related')

    messageR.attach(MIMEText(msgHtml, 'html'))
    messageA.attach(MIMEText(msgPlain, 'plain'))
    messageA.attach(messageR)

    message.attach(messageA)

    print("create_message_with_attachment: file: %s" % attachmentFile)
    content_type, encoding = mimetypes.guess_type(attachmentFile)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(attachmentFile, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(attachmentFile, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(attachmentFile, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(attachmentFile, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}

    
def sendMail(TO,SUBJECT,TEXT):
    try:
        sender = "srvn0nm@gmail.com"
        msgHtml = "Hi<br/>Html Email"
        SendMessage(sender, TO, SUBJECT, msgHtml, TEXT)
    # Send message with attachment: 
    # SendMessage(sender, TO, SUBJECT, msgHtml, TEXT, '/path/to/file.pdf')
    # try:
    #     message = textwrap.dedent("""\
    #         From: %s\
    #         To: %s\
    #         Subject: %s\
    #         %s\
    #         """ % ("snnn99554@gmail.com", ", ".join(TO), SUBJECT, TEXT))
    #     server = smtplib.SMTP("127.0.0.1")
    #     server.sendmail("snnn99554@gmail.com", TO, message)
    #     server.quit()
    except Exception as e:
        print(e)

def passwordRecovery(username):
    questionCount = 0
    seccheck = input("what was your answer to security question? ")
    try:
        cursor.execute("SELECT * from users WHERE userID = %s and useccheck = %s", (username, seccheck))
        checking = cursor.fetchall()
        db.commit()
    except Exception as e:
        print(e)
    while checking == None and questionCount < 5 :
        seccheck = input("what was your answer to security question?")
        print(f"login attempts = {questionCount}")
        questionCount += 1
    randomCode = random.randint(10000,100000)
    code_check = True
    try:
        cursor.execute('SELECT email FROM users WHERE userID = %s',(username,))
        reciever = str(cursor.fetchone())
        db.commit()
        cursor.execute("SELECT * from users WHERE userID = %s and useccheck = %s", (username, seccheck))
        checking = cursor.fetchall()
        db.commit()
    except Exception as e:
        print(e)
    while code_check and checking == None and questionCount == 5 :
        print("login code: "+randomCode)
        sendMail(reciever, "login code", randomCode)
        entered_code = input("type the code we have sended to you here: ")
        if entered_code == randomCode:
            code_check = False
    try:
        user = cursor.fetchone()
        print(user)
        db.commit()
        current_time = datetime.now().strftime("%H:%M:%S")
        Q2 = "INSERT INTO log_login (userID, useccheck, loginAttempts, timing) VALUES(%s, %s, %s, %s)"
        cursor.execute(Q2,(username, seccheck, questionCount, current_time))
        db.commit()
    except Exception as e:
        print(e)
    changePassword(username)
    try:
        cursor.execute('SELECT upassword FROM users WHERE userID = %s',(username,))
        new_password = str(cursor.fetchone())
        db.commit()
        update_query2 = "UPDATE log_login SET newPass = %s WHERE userID = %s"
        cursor.execute(update_query2,(new_password, username))
        db.commit()    
    except Exception as e:
        print(e)

def wrongPassword(username):
    try:
        print("invalid inputs for login attempt!")
        cursor.execute('SELECT attempts FROM log_wrongPassword WHERE userID = %s',(username,))
        number = cursor.fetchone()
        db.commit()
        if (int(number) + 1) < 3 :
            temp = int(number) + 1
            update_query = "UPDATE log_wrongPassword SET attempts = %s WHERE userID = %s"
            cursor.execute(update_query,(temp, username))
            db.commit()
        else: 
            current_time = datetime.now().strftime("%H:%M:%S")
            Q4 = "INSERT INTO limited_users (userID, timing) VALUES(%s, %s)"
            cursor.execute(Q4,(username, current_time))
            db.commit()
    except Exception as e:
        print(e)
        
def login():
    try:
        username = input("type your username here: ")
        limited_query = "SELECT userID From limited_users WHERE userID = %s"
        cursor.execute(limited_query,(username,))
        limited_username = cursor.fetchone()
        db.commit()
        login_query ="SELECT userID FROM users WHERE log_in = '1' and userID = %s"
        cursor.execute(login_query,(username,))
        loggedin_username = cursor.fetchone()
        db.commit()
        if (not (username == limited_username)) and (not(username == loggedin_username)):
            password = input("type your password here or if you don't remember it just type 0:  ")
            if password == '0':
                passwordRecovery(username)
            else:
                cursor.execute('SELECT upassword FROM users WHERE userID = %s',(username,))
                oldpass = cursor.fetchone()
                db.commit()
                if oldpass[0] == password:
                    cursor.execute("SELECT * from users WHERE userID = %s and upassword = %s", (username, password))
                    user = cursor.fetchone()
                    print("Hello!\nWelcome Back!\n" + str(user))
                    db.commit()
                    print("Congratulations!\nYou successfully logged in!\n")
                    update_query = "UPDATE users SET log_in = '1' WHERE userID = %s"
                    cursor.execute(update_query,(username,))
                    db.commit()
                    menu(username)
                else:
                    wrongPassword(username)
        else:
            print("Sorry!\nYou can't login.>-<\n")
    except Exception as e:
        print(e)

def changePassword(username):
    try:
        questionCount = 0
        seccheck = input("what was your answer to security question? ")
        cursor.execute("SELECT * from users WHERE userID = %s and useccheck = %s", (username, seccheck))
        checking = cursor.fetchone()
        db.commit()
        while checking == None and questionCount < 5 :
            seccheck = input("what was your answer to security question?")
            print(f"login attempts = {questionCount}")
            questionCount += 1
        randomCode = random.randint(10000,100000)
        code_check = True
        cursor.execute('SELECT email FROM users WHERE userID = %s',(username,))
        checking_email = cursor.fetchone()
        reciever = str(checking_email)
        db.commit()
        cursor.execute("SELECT * from users WHERE userID = %s and useccheck = %s", (username, seccheck))
        checking2 = cursor.fetchone()
        db.commit()
        while code_check and checking2 == None and questionCount == 5 :
            sendMail(reciever, "login code", randomCode)
            print("login code: "+randomCode)
            entered_code = input("type the code we have sended to you here: ")
            if entered_code == randomCode:
                code_check = False
        new_password = input("Enter your new password here: ")
        checking2 = False
        for i in new_password:
            if i.isalpha():
                checking2 = True
                break
        while not checking2:
            print("Password should have alphabets, too!\ntry again:\n")
            new_password = input()
            for i in new_password:
                if i.isalpha():
                    checking2 = True
                    break
        update_query = "UPDATE users SET upassword = %s WHERE userID = %s"
        cursor.execute(update_query,(new_password, username))
        db.commit()
    except Exception as e:
        print(e)

def firstMenu():
    print("Hello.Welcome here.Please enter the number of one of the choices below: ")
    choice = input("1)register for a new account\n2)login to an existing account")
    if choice == "1":
        name = input("Enter your name here: ")
        lname = input("Enter your lname here: ")
        ID = input("Enter your ID here: ")
        phoneNo = input("Enter your phone number here: ")
        gmail = input("Enter your gmail here: ")
        password = input("Enter your password here: ")
        register(name, lname, ID, phoneNo, gmail, password)
    if choice == "2":
        login()

def searchMenu(ids,username):
    try:
        choice = input("Please select one of the options below:\n1)friendship\n2)unfriend\n3)block\n4)unblock\n5)send messsages\n6)exit\n")
        if choice == "1":
            no = 1
            for id in ids:
                print(str(no) + ") " + str(id))
                no += 1
            i = int(input("Enter the number of one person")) - 1
            cursor.execute('SELECT blockerID, blockedID, u1ID, u2ID FROM friends JOIN blocked ON ((blockerID = %s and blockedID = %s) or (u1ID = %s and u2ID = %s) or (u2ID = %s and u1ID = %s))',(ids[i][0], username, ids[i][0], username, ids[i][0], username))
            checking = cursor.fetchall()
            db.commit()
            limited_query = "SELECT uname From users WHERE userID = %s"
            cursor.execute(limited_query,(ids[i][0],))
            limited_name = cursor.fetchone()
            db.commit()
            if (not len(checking)) and (not limited_name[0] == None):
                Q6 = "INSERT INTO friends (u1ID, u2ID) VALUES (%s, %s)"
                cursor.execute(Q6,(username, ids[i][0]))
                db.commit()
                Q7 = "DELETE FROM blocked WHERE blockerID = %s and blockedID = %s"
                cursor.execute(Q7,(username, ids[i][0]))
                db.commit()
            searchMenu(ids,username)
        elif choice == "2":
            no = 1
            for id in ids:
                print(str(no) + ") " + str(id))
                no += 1
            i = int(input("Enter the number of one person")) - 1
            Q6 = "DELETE FROM friends WHERE (u1ID = %s and u2ID = %s) or (u2ID = %s and u1ID = %s)"
            cursor.execute(Q6,(ids[i][0], username, ids[i][0], username))
            db.commit()
            searchMenu(ids,username)
        elif choice == "3":
            no = 1
            for id in ids:
                print(str(no) + ") " + str(id))
                no += 1
            i = int(input("Enter the number of one person")) - 1
            current_time = datetime.now().strftime("%H:%M:%S")
            cursor.execute("SELECT bID FROM blocked WHERE blockerID = %s and blockedID = %s",(username,ids[i][0]))
            checking4 = cursor.fetchone()
            limited_query = "SELECT uname From users WHERE userID = %s"
            cursor.execute(limited_query,(ids[i][0],))
            limited_name = cursor.fetchone()
            db.commit()
            if len(checking4) == 0 and (not limited_name[0] == None):
                cursor.execute('INSERT INTO blocked (blockerID, blockedID, timing) VALUES (%s, %s, %s)',(username, ids[i][0], current_time))
                cursor.execute('SELECT fID FROM friends WHERE (u1ID = %s and u2ID = %s) or (u2ID = %sand u1ID = %s)',(ids[i][0], username, ids[i][0], username))
                checking3 = cursor.fetchall()
                db.commit()
                if len(checking3) == 2:
                    Q6 = "DELETE FROM friends WHERE fID = %s"
                    cursor.execute(Q6,(checking3[0]))
                    Q7 = "DELETE FROM friends WHERE fID = %s"
                    cursor.execute(Q7,(checking3[1]))
                    db.commit()
                elif len(checking3) == 1:
                    Q6 = "DELETE FROM friends WHERE fID = %s"
                    cursor.execute(Q6,(checking3[0]))
                    Q7 = "DELETE FROM friends WHERE fID = %s"
                    cursor.execute(Q7,(checking3[0]))
                else:
                    print("you have already blocked this user!")
            searchMenu(ids,username)
        elif choice == "4":
            no = 1
            for id in ids:
                print(str(no) + ") " + str(id))
                no += 1
            i = int(input("Enter the number of one person")) - 1
            cursor.execute('DELETE FROM blocked WHERE blockerID = %s and blockedID= %s',(username, ids[i][0]))
            db.commit()
            searchMenu(ids,username)
        elif choice == "5":
            no = 1
            for id in ids:
                print(str(no) + ") " + str(id))
                no += 1
            i = int(input("Enter the number of one person")) - 1
            # limited_query = "SELECT uname From users WHERE userID = %s"
            # cursor.execute(limited_query,(ids[i],))
            # limited_name = cursor.fetchone()
            # db.commit()
            # if (not limited_name[0] == None):
            sendmessage(username , id[i])
            searchMenu(ids,username)
        elif choice == "6":
            menu(username)
    except Exception as e:
        print(e)

def sendmessage(sender,reciever):
    try:
        msg = input("Please type your message here: ")
        current_time = datetime.now().strftime("%H:%M:%S")
        cursor.execute('INSERT INTO messages (senderID, rID, timing, textmsg) VALUES (%s, %s, %s, %s)',(sender, reciever, current_time, msg))
        db.commit()
    except Exception as e:
        print(e)
   
def menu(username):
    try:
        choice = input("Hi.Type the number of the action you want to perform here:\n1)change password\n2)log out\n3)delete account\n4)search\n5)messages\n6)friends\n7)shutdown\n8)show profile\n9)show all accounts\n10)show all tables")
        if choice == "1":
            changePassword(username)
            menu(username)
        elif choice == "2":
            update_query = "UPDATE users SET log_in = '0' WHERE userID = %s"
            cursor.execute(update_query,(username,))
            db.commit()
            firstMenu()
        elif choice == "3":
            update_query = "UPDATE users SET upassword = None, SET uname = None, SET ulname = None, SET phone = None, SET email = None, SET useccheck = None, SET timing = None, SET log_in = '0' WHERE userID = %s"
            cursor.execute(update_query,(username,))
            db.commit()
            cursor.execute('DELETE FROM friends WHERE (u1ID = %sor u2ID = %s)',(username, username))
            db.commit()
            cursor.execute('DELETE FROM blocked WHERE (blockerID = %sor blockedID = %s)',(username, username))
            db.commit()
        elif choice == "4":
            searched_username = input("Please enter the username you want to search for: ")
            searching_number = int(len(searched_username)*0.5)
            searching_name = searched_username[0:searching_number]
            search_query = "SELECT userID FROM users WHERE userID LIKE CONCAT(%s, '%')"
            cursor.execute(search_query,(searching_name,))
            searched_IDs = []
            for row in cursor:
                searched_IDs.append(row)
            db.commit()
            for id in searched_IDs:
                if id[0] == username:
                    searched_IDs.remove(id)
                    break
            no = 1
            for id in searched_IDs:
                print(str(no) + ") " + str(id))
                no += 1
            searchMenu(searched_IDs,username)  
        elif choice == "5":
            search_query = "SELECT * FROM messages WHERE rID = %s"
            cursor.execute(search_query,(username,))
            messages = cursor.fetchall()
            db.commit()
            no = 1
            for msg in messages:
                print(str(no) + ") " + str(msg))
                no += 1
            cursor.execute("UPDATE messages SET seen = '1' WHERE seen = '0'")
            db.commit()
            choice2 = input("If you want to like a message type its number or type 0")
            if choice2 == "0": 
                menu(username)
            else:
                cursor.execute("UPDATE messages SET liked = '1' WHERE mID = %s",(messages[int(choice2)-1][6],))
                db.commit()
                menu(username)
        elif choice == "6":
            search_query = "SELECT * FROM friends WHERE (u1ID = %s or u2ID = %s)"
            cursor.execute(search_query,(username, username))
            friends = cursor.fetchall()
            db.commit()
            no = 1
            for fr in friends:
                print(str(no) + ") " + str(fr))
                no += 1
            choice2 = input("If you want to unfriend a friend type their number or type 0")
            if choice2 == "0": 
                menu(username)
            else:
                i = int(choice2) - 1
                Q6 = "DELETE FROM friends WHERE ((u1ID = %s and u2ID = %s) or (u2ID = %s and u1ID = %s))"
                cursor.execute(Q6,(friends[i][0], username, friends[i][0], username))
                db.commit()
                menu(username)
        elif choice == "7":
            print(f"Goodbye {username}!\nHope to see you again soon.^-^\n")
        elif choice == '8':
            cursor.execute("SELECT * FROM users WHERE username = %s",(username,))
            acc = cursor.fetchone()
            for i in acc:
                print(i + '\n')
            db.commit()
            menu(username)
        elif choice == '9':
            cursor.execute("SELECT * FROM users")
            acc = cursor.fetchall()
            for i in acc:
                print(i + '\n')
            db.commit()
            menu(username)
        elif choice == '10':
            cursor.execute("SELECT * FROM users")
            print("users: ")
            for j in cursor:
                print(j)
            cursor.execute("SELECT * FROM friends")
            print("friends: ")
            for j in cursor:
                print(j)
            cursor.execute("SELECT * FROM blocked")
            print("blocked: ")
            for j in cursor:
                print(j)
            cursor.execute("SELECT * FROM request")
            print("request: ")
            for j in cursor:
                print(j)
            cursor.execute("SELECT * FROM messages")
            print("messages: ")
            for j in cursor:
                print(j)
            cursor.execute("SELECT * FROM log_login")
            print("log_login: ")
            for j in cursor:
                print(j)
            cursor.execute("SELECT * FROM log_wrongPassword")
            print("log_wrongPassword: ")
            for j in cursor:
                print(j)
            cursor.execute("SELECT * FROM limited_users")
            print("limited_users: ")
            for j in cursor:
                print(j)
            db.commit()
            menu(username)
    except Exception as e:
        print(e)
firstMenu()
db.close()