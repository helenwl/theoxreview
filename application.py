import os

import requests
from flask import Flask, render_template, session, request, redirect, url_for, abort, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import datetime
from jinja2 import Template
from jinja2 import Environment


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Home route
@app.route('/')
def index():
    return render_template('Login.html', user_id=session.get('user_id'))

# Registration route
@app.route('/register/', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        # If method is GET, show user the registration form
        return render_template('register.html', user_id=session.get('user_id'))
    elif request.method == 'POST':
        # If method is POST, check the data
        email = request.form.get('email')
        subject = request.form.get('subject')
        college = request.form.get('college')
        matriculation_year = request.form.get('matriculation_year')
        registered_on=datetime.datetime.now()
        user_db = db.execute('SELECT * FROM users WHERE email=:email', {'email': email}).fetchone()
        if user_db:
            # If user with specified name or email exists, return to registration page and show alert
            flash('User already exists', 'danger')
            return render_template('register.html', user_id=session.get('user_id'))
            print(registered_on)
        else:
            # If not, save new user credentials in database and show the login page

            db.execute('INSERT INTO users (email, subject, college, matriculation_year, password, registered_on) VALUES ( :email, :subject, :college, :matriculation_year, :password, :registered_on)',
                       {'email': email, 'subject': subject, 'college': college, 'matriculation_year': matriculation_year, 'registered_on':registered_on, 'password': generate_password_hash(request.form.get('pass1'))})
            db.commit()
            print(registered_on)
            flash('You have successfully registered! Now you may log in', 'success')
            return render_template('register.html', user_id=session.get('user_id'))


# Login route
@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        # If method is GET, just show the page
        return render_template('login1.html', show_alert=False, user_id=session.get('user_id'))
    elif request.method == 'POST':
        # If method is POST, check whether the user exists
        email = request.form.get('email')
        user_db = db.execute('SELECT * FROM users WHERE email=:email', {'email': email}).fetchone()
        if not user_db:
            # If the user doesn't exist, return to the login page and show alert
            flash('Wrong credentials', 'danger')
            return render_template('login1.html', user_id=session.get('user_id'))
        else:
            if check_password_hash(user_db.password, request.form.get('password')):
                # If the user exists and hashed password is ok, redirect to the search page
                session['user_id'] = user_db.id
                return redirect(url_for('landingpage'))
            else:
                # If not, return back and show alert
                flash('Wrong credentials', 'danger')
                return render_template('login1.html', user_id=session.get('user_id'))
#bringing the logged in user to the landing page
@app.route('/landingpage/')
def landingpage():
    if session.get('user_id') is None:
        return('Please log in to access this webpage')
    else:
        logged_in = session.get('user_id') is not None
        return render_template('landingpage.html', user_id=session.get('user_id'), logged_in=logged_in)

# Log out user and return to home page
@app.route('/logout/')
def logout():
    session['user_id'] = None
    return redirect(url_for('login'))

# Search route for subject courses
@app.route('/subject/', methods=['POST', 'GET'])
def subject():
        if session.get('user_id') is None:
            return('Please log in to access this webpage')
        else:
            if 'query' in request.args:
        # If 'query' is in request arguments, do the search and show results
                query = request.args['query']

                result = db.execute('SELECT * FROM subjects WHERE subject ILIKE :pattern OR course_name ILIKE :pattern OR lecturer ILIKE :pattern ORDER BY subject',
                            {'pattern': f'%{query}%'}).fetchall()

                return render_template('subject.html', has_query=True, result=result, user_id=session.get('user_id'))
            else:
        # If not, just show the search form
                allsubjects = db.execute('SELECT * FROM subjects ORDER BY subject').fetchall()
                return render_template('subject.html', has_query=False, allsubjects=allsubjects, user_id=session.get('user_id'))

@app.route('/addsubject/', methods=['POST', 'GET'])
def addsubject():
    if session.get('user_id') is None:
            return('Please log in to access this webpage')
    else:
        if request.method == 'POST':

            logged_in = session.get('user_id') is not None

            subject= request.form.get('subject')
            course_name= request.form.get('course_name')
            lecturer= request.form.get('lecturer')
            year_of_study= request.form.get('year_of_study')
            addedsubject_on=datetime.datetime.now().strftime("%d-%b-%Y at %H:%M")

            db.execute('INSERT INTO subjects (subject, course_name, lecturer, year_of_study, addedsubject_on) VALUES (:subject, :course_name, :lecturer, :year_of_study, addedsubject_on)',
                            {'subject': subject, 'course_name': course_name, 'lecturer': lecturer, 'year_of_study': year_of_study, 'addedsubject_on':addedsubject_on})
            db.commit()
            result2 = db.execute('SELECT * FROM subjects WHERE subjects.course_name= :course_name', {'course_name': course_name}
                            ).fetchall()

            return render_template('subject.html', result2=result2, user_id=session.get('user_id'))
#post a question and add it to the question table
@app.route('/postquestion/', methods=['POST', 'GET'])
def postquestion():
    if session.get('user_id') is None:
            return('Please log in to access this webpage')
    else:
        if request.method == 'POST':

            logged_in = session.get('user_id') is not None

            category= request.form.get('category')
            user_details= request.form.get('user_details')
            question= request.form.get('question')
            asked_on=datetime.datetime.now().strftime("%d-%b-%Y at %H:%M")


            db.execute('INSERT INTO questions (category, user_details, question, asked_on) VALUES (:category, :user_details, :question, :asked_on)',
                            {'category': category, 'user_details': user_details, 'question': question, 'asked_on':asked_on})
            db.commit()
            result3 = db.execute('SELECT * FROM questions WHERE questions.question= :question', {'question': question}
                            ).fetchall()

            return render_template('questions.html', result3=result3, user_id=session.get('user_id'))
# search for a question/
@app.route('/question/', methods=['POST', 'GET'])
def question():
    if session.get('user_id') is None:
            return('Please log in to access this webpage')
    else:
        if 'query' in request.args:
        # If 'query' is in request arguments, do the search and show results
            query = request.args['query']
            result = db.execute('SELECT * FROM questions WHERE question ILIKE :pattern ORDER BY id DESC',
                            {'pattern': f'%{query}%'}).fetchall()


            return render_template('questions.html', has_query=True, result=result, user_id=session.get('user_id'))
        else:
        # If not, just show all the questions that exist

            allresults = db.execute('SELECT * FROM questions ORDER BY id DESC').fetchall()


    #    all_results= questions.query.all

            return render_template('questions.html', has_query=False, allresults=allresults, user_id=session.get('user_id'))
#    def viewquestion():
#        return 'questions'

# Book route

@app.route('/course/<int:course_id>/', methods=['POST', 'GET'])
def course(course_id):
    if session.get('user_id') is None:
            return('Please log in to access this webpage')
    else:
        if request.method == 'GET':
        # If method is GET, get all reviews for this book from database
            logged_in = session.get('user_id') is not None

            reviews = db.execute('SELECT rating, review, users.id, email, reviewdate, review_on FROM reviews JOIN users ON (users.id = reviews.user_id) WHERE reviews.course_id = :course_id;', {'course_id': course_id}).fetchall()
            already_submit = session.get('user_id') in [review.id for review in reviews]

            course_name = db.execute('SELECT * FROM subjects WHERE id = :course_id', {'course_id': course_id}).fetchone()
        #gr_data = get_gr_data(book.isbn)

            return render_template('review.html', course_name=course_name, user_id=session.get('user_id'), logged_in=logged_in, reviews=reviews, already_submit=already_submit)
        #gr_data=gr_data)
        elif request.method == 'POST':
        # If method is POST, save new review in database
            if session.get('user_id') is None:
                return('Please log in to access this webpage')
                rating = request.form.get('rating')
                review_text = request.form.get('review')
                reviewdate = request.form.get('reviewdate')
                review_on=datetime.datetime.now().strftime("%d-%b-%Y at %H:%M")
                db.execute('INSERT INTO reviews (rating, review, reviewdate, user_id, course_id, review_on) VALUES (:rating, :review, :reviewdate, :user_id, :course_id, :review_on)',
                   {'rating': rating, 'review': review_text, 'reviewdate': reviewdate, 'user_id': session.get('user_id'), 'course_id': course_id, 'review_on':review_on})
                db.commit()
                return redirect(url_for('course', course_id=course_id))
@app.route('/questions/')
def questions():
  return 'Questions'

@app.route('/answers/<int:question_id>/', methods=['POST', 'GET'])
def answers(question_id):
    if session.get('user_id') is None:
            return('Please log in to access this webpage')
    else:
        if request.method == 'GET':
        # If method is GET, get all reviews for this book from database
            logged_in = session.get('user_id') is not None

            answers = db.execute('SELECT answer, users.id, question_id, college, matriculation_year, subject, answered_on FROM answers JOIN users ON (users.id = answers.user_id) WHERE answers.question_id = :question_id;', {'question_id': question_id}).fetchall()
            already_submit = session.get('user_id') in [answer.id for answer in answers]

            question_name = db.execute('SELECT * FROM questions WHERE id = :question_id', {'question_id': question_id}).fetchone()

        #gr_data = get_gr_data(book.isbn)

            return render_template('answers.html', question_name=question_name, user_id=session.get('user_id'), logged_in=logged_in, answers=answers, already_submit=already_submit)
        #gr_data=gr_data)
        elif request.method == 'POST':
        # If method is POST, save new review in database

                answer = request.form.get('answer')
                answered_on=datetime.datetime.now().strftime("%d-%b-%Y at %H:%M")
        #SELECT answered_on, TO_CHAR(NOW() :: TIMESTAMP, 'hh:mm dd-mm-yy'); come back to this!! this code should
        #convert the date format to something more aesthetic ofificall on the databse.

                db.execute('INSERT INTO answers (answer, user_id, question_id, answered_on) VALUES (:answer, :user_id, :question_id, :answered_on)',
                   {'answer': answer,'user_id': session.get('user_id'), 'question_id': question_id, 'answered_on': answered_on})
                db.commit()
                return redirect(url_for('answers', question_id=question_id))

@app.route('/departments/', methods=['POST', 'GET'])
def departments():
    if session.get('user_id') is None:
            return('Please log in to access this webpage')
    else:
        if 'query' in request.args:
        # If 'query' is in request arguments, do the search and show results
            query = request.args['query']
            result = db.execute('SELECT * FROM departments WHERE department ILIKE :pattern',
                            {'pattern': f'%{query}%'}).fetchall()

            return render_template('departments.html', has_query=True, result=result, user_id=session.get('user_id'))
        else:
        # If not, just show all the questions that exist

            allresults = db.execute('SELECT * FROM departments ORDER BY department').fetchall()


    #    all_results= questions.query.all

            return render_template('departments.html', has_query=False, allresults=allresults, user_id=session.get('user_id'))
#    def viewquestion():
#        return 'questions'

@app.route('/departmentreviews/<int:department_id>/', methods=['POST', 'GET'])
def departmentreviews(department_id):
    if session.get('user_id') is None:
            return('Please log in to access this webpage')
    else:
        if request.method == 'GET':
        # If method is GET, get all reviews for this book from database
            logged_in = session.get('user_id') is not None

            departmentreviews = db.execute('SELECT departmentreview, rating, users.id, department_id, college, matriculation_year, subject FROM departmentreviews JOIN users ON (users.id =departmentreviews.user_id) WHERE departmentreviews.department_id = :department_id;', {'department_id': department_id}).fetchall()
            already_submit = session.get('user_id') in [departmentreview.id for departmentreview in departmentreviews]

            department_name = db.execute('SELECT * FROM departments WHERE id = :department_id', {'department_id': department_id}).fetchone()

        #gr_data = get_gr_data(book.isbn)

            return render_template('departmentreviews.html', department_name=department_name, user_id=session.get('user_id'), logged_in=logged_in, departmentreviews=departmentreviews, already_submit=already_submit)
        #gr_data=gr_data)
        elif request.method == 'POST':
        # If method is POST, save new review in database
            if session.get('user_id') is None:
                return('Please log in to access this webpage')
                departmentreview = request.form.get('departmentreview')
                departmentreviewdate = request.form.get('departmentreviewdate')
                rating= request.form.get('rating')
                departmentreview_on=datetime.datetime.now().strftime("%d-%b-%Y at %H:%M")

                db.execute('INSERT INTO departmentreviews (departmentreview, departmentreviewdate, rating, user_id, department_id, departmentreview_on) VALUES (:departmentreview, :departmentreviewdate, :rating, :user_id, :department_id, :departmentreview_on)',
                   {'departmentreview': departmentreview, 'departmentreviewdate': departmentreviewdate, 'rating': rating, 'user_id': session.get('user_id'), 'department_id': department_id, 'departmentreview_on': departmentreview_on})
                db.commit()

                return redirect(url_for('departmentreviews', department_id=department_id))








# API route
@app.route('/api/<isbn>/')
def get_book_by_isbn(isbn):
    books = db.execute('SELECT title, author, year, isbn, rating FROM books LEFT JOIN reviews ON (reviews.book_id = books.id) WHERE isbn = :isbn', {'isbn': isbn}).fetchall()
    if not books:
        abort(404)

    ratings = [book[4] for book in books if book[4] is not None]
    review_count = len(ratings)
    average_score = sum(ratings) / review_count if ratings else 0

    return jsonify({'title': books[0][0],
                    'author': books[0][1],
                    'year': books[0][2],
                    'isbn': books[0][3],
                    'review_count': review_count,
                    'average_score': average_score})

def get_gr_data(isbn):
    """Get GoodRead data."""
    try:
        gr_data_raw = requests.get('https://www.goodreads.com/book/review_counts.json', params={"key": os.getenv("GR_API_KEY"), "isbns": isbn})
    except:
        return None

    try:
        gr_data = gr_data_raw.json()['books'][0]
    except:
        return None

    return gr_data
