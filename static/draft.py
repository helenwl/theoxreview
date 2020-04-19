@app.route('/course/<int:course_id>/', methods=['POST', 'GET'])
def course(course_id):
    if session.get('user_id') is None:
        flash('theOXREVIEW is for students of Oxford only. Please log in to access this webpage.')
        return render_template('Login.html', user_id=session.get('user_id'))
    else:
        if request.method == 'GET':
        # If method is GET, get all reviews for this book from database
            logged_in = session.get('user_id') is not None

            reviews = db.execute('SELECT rating, review, users.id, email, reviewdate, review_on, college, matriculation_year FROM reviews JOIN users ON (users.id = reviews.user_id) WHERE reviews.course_id = :course_id;', {'course_id': course_id}).fetchall()
            already_submit = session.get('user_id') in [review.id for review in reviews]

            course_name = db.execute('SELECT * FROM subjects WHERE id = :course_id', {'course_id': course_id}).fetchone()
        #gr_data = get_gr_data(book.isbn)

            return render_template('review.html', course_name=course_name, user_id=session.get('user_id'), logged_in=logged_in, reviews=reviews, already_submit=already_submit)
