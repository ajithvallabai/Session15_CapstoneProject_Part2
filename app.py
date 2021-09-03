import re
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import SigUpForm
import smtplib 
from datetime import datetime
import random
import uuid
import os 
app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
random.seed(0)

#init
db = SQLAlchemy(app)
# create db model
class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a function to return a string
    def __repr__(self):
        return '<Name %r>' % self.id 


subscribers = []


class AccountDetails:
    def __init__(self) -> None:
        self.account_details = {"tsai":"tsai99!"}
        self.current_user = ""

class QuizDataClass:
    def __init__(self) -> None:
        self.q_count = 0
        self.data_quiz_1 = ["What is your name ?", "How old are you ?",
                                "Where are you living ?","What is your pet name","What are u doing ?"]
        self.user_input = []
        self.database_user_input = {}
        self.created_questions = {}
        
        self.current_quiz_id = -1
    def counter():
        print("one")
quiz_data = QuizDataClass()
account_detail = AccountDetails()


@app.route('/delete/<int:id>')
def delete(id):
    friend_to_delete = Friends.query.get_or_404(id)
    try:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return redirect("/friends")
    except:
        return "There was a problem deleting that friend"

@app.route('/update/<int:id>', methods=['POST','GET'])
def update(id):
    friend_to_update = Friends.query.get_or_404(id)
    if request.method == "POST":
        friend_to_update.name = request.form['name']
        try:
            db.session.commit()
            return redirect('/friends')
        except:
            return "There was a problem updating that friend.."
    else:
        return render_template('update.html', friend_to_update=friend_to_update)

@app.route('/friends', methods=['POST', 'GET'])
def friends():
    title = "My Friend List"
    if request.method == "POST":
        friend_name = request.form['name']
        new_friend = Friends(name=friend_name)        
        try:
            db.session.add(new_friend)
            db.session.commit()
            return redirect('/friends')
        except:
            return "There was an error adding your friend..."
    else:
        friends = Friends.query.order_by(Friends.date_created)
        return render_template("friends.html", title=title, friends=friends)

@app.route('/', methods=['POST', 'GET'])
def index():
    form = SigUpForm()
    if form.is_submitted():
        result = request.form
        print(result)

        if result["username"] in account_detail.account_details:
            return  render_template('accountpage.html', username=result["username"])
        else:
            return render_template('signup.html', form=form, failure = "true")
        
        
    return render_template('signup.html', form=form, failure = "true")

@app.route('/about')
def about():
    title = "About Ajith Kumar"
    names = ["John", "Mary", "Wes", "Sally"]
    return render_template("about.html", names=names, title=title)


@app.route('/subscribe')
def subscribe():
    title = "Subscribe To My Email Newsletter"    
    return render_template("subscribe.html", title=title)


@app.route('/form', methods=["POST"])
def form():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")

    message = "You have been scubscribed to my email newsletter"
    sever = smtplib.SMTP("smtp.gmail.com", 587)
    sever.starttls()
    sever.login("ajithdschrozahan@gmail.com", "pass123thispass")
    sever.sendmail("ajithdschrozahan@gmail.com", email, message)

    if not first_name or not last_name or not email:
        error_statement = "All Form Fields Required..."
        return render_template("subscribe.html", error_statement=error_statement, first_name=first_name,
            last_name=last_name, email=email)

    subscribers.append(f"{first_name}{last_name} | {email}")
    title = "Thank you!"
    return render_template("form.html", title=title, subscribers=subscribers)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/quiz',methods=['POST','GET'])
def quiz():    
    if request.method == "POST":
        quiz_data.q_count += 1
        result = request.form        
        quiz_data.user_input.append([quiz_data.data_quiz_1[quiz_data.q_count-1],result.to_dict(flat=False)["answer"][0]])
        print(quiz_data.user_input)
    print(quiz_data.q_count)
    
    button_name = "Next"
    if quiz_data.q_count == len(quiz_data.data_quiz_1)-1:
        button_name = "submit"
    return render_template('quiz.html', data_quiz=quiz_data.data_quiz_1[quiz_data.q_count], button_name=button_name)


@app.route('/archives',methods=['POST','GET'])
def display_all_user_inputs():
    return render_template('displayall.html', user_datas = quiz_data.database_user_input)

@app.route('/thanks',methods=['POST','GET'])
def thanks():
    if request.method == "POST":
        result = request.form        
        quiz_data.user_input.append([quiz_data.data_quiz_1[quiz_data.q_count],result.to_dict(flat=False)["answer"][0]])
        print(quiz_data.user_input)
        quiz_data.database_user_input.update({int(random.random()*1e8):quiz_data.user_input})
        # empty data
        quiz_data.user_input = []
        # resetting 
        quiz_data.q_count = 0
    print(quiz_data.database_user_input)
    return render_template('thanksyou.html')

@app.route('/home',methods=['POST','GET'])
def home():
    return render_template('accountpage.html', username=account_detail.current_user)


@app.route('/signupback',methods=['POST','GET'])
def signup():
    form = SigUpForm()
    if form.is_submitted():
        result = request.form
        #print(result)
        if (result["username"] in account_detail.account_details) and (result["password"] == account_detail.account_details[result["username"]]):
            account_detail.current_user = result["username"]
            return  render_template('accountpage.html', username=result["username"])
        else:
            return render_template('signup.html', form=form, failure = "true")       
        
    return render_template('signup.html', form=form, failure = "true")

@app.route('/createquiz', methods=['POST','GET'])
def createquiz():
    question = 0
    if quiz_data.current_quiz_id == -1:
        quiz_data.current_quiz_id =int(random.random()*1e8)
        quiz_id = quiz_data.current_quiz_id
    else:
        quiz_id = quiz_data.current_quiz_id

    if request.method == "POST":
        result = request.form
        print(result)
        if quiz_id not in quiz_data.created_questions:
            quiz_data.created_questions.update({quiz_id: [result["answer"]] })
        else:
            quiz_data.created_questions[quiz_id].append(result["answer"])
        print(quiz_data.created_questions)
    
    return render_template('creatingquiz.html', quiz_id = quiz_id )

@app.route('/createdquizes/<int:id>', methods=['POST','GET'])
def createdquizes(id):
    quiz_id = id
    if request.method == "POST":
        result = request.form
        #quiz_id = request.args.get('id')
        if quiz_id not in quiz_data.created_questions:
            quiz_data.created_questions.update({quiz_id: [result["answer"]] })
        else:
            quiz_data.created_questions[quiz_id].append(result["answer"])
        quiz_data.current_quiz_id = -1
        print(quiz_data.created_questions)
    return render_template('thanksyou.html')

@app.route('/showallquiztypes', methods=['POST','GET'])
def showallquiztypes():

    return render_template("displayquiztypes.html", created_quesitons = quiz_data.created_questions)

if __name__ == '__main__':
    app.run(debug=True)