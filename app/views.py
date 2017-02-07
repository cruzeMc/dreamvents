from app import app
from flask import render_template, request, redirect, \
    url_for, g, jsonify, flash, session, json, current_app
import os
from app import login_manager, login_required, logout_user, current_user, login_user, ALLOWED_EXTENSIONS
from werkzeug.utils import secure_filename
from recommender_engine import *
from .form import *
from app.sentiment_analysis import sentiment
import datetime
from db_insert import *
from functools import wraps
from dicts.sorteddict import ValueSortedDict
from sqlalchemy import func
from sqlalchemy.sql import text
import paypalrestsdk
import calendar
import uuid
from sklearn import linear_model
from random import randint
from mail_handler import *

import pdb
from htmlmin.minify import html_minify
import ast
from config import EVENTS_PER_PAGE


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.get_urole() not in roles:
                return redirect(url_for('home'))
            return f(*args, **kwargs)

        return wrapped

    return wrapper



@app.route("/")
@app.route("/landing")
def landing():
    category_list = db.session.query(Category).all()
    rendered_html = render_template('landing.html', lst=category_list)
    return html_minify(rendered_html)

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    user_id = g.user
    recommend_list = {}
    recommend = []
    recommends = []
    recommending = []
    recommendings = []
    users = Users.query.filter_by(id=user_id).first()
    category = users.users_category
    for cat in users.users_category:
        events = Event.query.filter_by(category=cat.id).all()
        for event in events:
            recommend_list.update(top_recommend(event.id))
    recommend_list = ValueSortedDict(recommend_list, reverse=True)
    for key in recommend_list:
        recommends.append(Event.query.filter_by(id=key).first())
    for evnt in recommends:
        due = time_remainding(evnt.date, evnt.start_time)
        recommend.append({"id": evnt.id, "creator": evnt.creator, "category": evnt.category, "poster": evnt.poster,
                          "eventname": evnt.eventname, "date": evnt.date, "start_time": evnt.start_time,
                          "end_time": evnt.end_time, "venue": evnt.venue, "lat": evnt.lat, "lng": evnt.lng,
                          "capacity": evnt.capacity, "addmission": evnt.admission, "description": evnt.description,
                          "contact": evnt.contact, "days": due[0], "hours": due[1]})

    recommend.sort(key=lambda x: (x["days"]))
    cat_list = []
    for i in category:
        for v in recommend:
            if v.get('category') == i.id and v.get('days') > 0:
                if i.id not in cat_list:
                    cat_list.append(i.id)
    filtered_recommendations = filtered_recommendation()
    if filtered_recommendations:
        first_list = filtered_recommendations[1]
        second_list = filtered_recommendations[0]

        in_first = set(first_list)
        in_second = set(second_list)

        in_second_but_not_in_first = in_second - in_first

        recommender = first_list + list(in_second_but_not_in_first)
        for evnt_id in recommender:
            recommending.append(Event.query.filter_by(id=evnt_id).first())
        for evnts in recommending:
            due = time_remainding(evnts.date, evnts.start_time)
            recommendings.append(
                {"id": evnts.id, "creator": evnts.creator, "category": evnts.category, "poster": evnts.poster,
                 "eventname": evnts.eventname, "date": evnts.date, "start_time": evnts.start_time,
                 "end_time": evnts.end_time, "venue": evnts.venue, "lat": evnts.lat, "lng": evnts.lng,
                 "capacity": evnts.capacity, "admission": evnts.admission, "description": evnts.description,
                 "contact": evnts.contact, "days": due[0], "hours": due[1]})

    if recommend:
        rendered_html = render_template('home.html', recommend=recommend, recommendings=recommendings, recommends=recommends,
                               category=category, cat_list=cat_list)
        return html_minify(rendered_html)

    else:
        return redirect(url_for('welcome'))


##############################################################
# Friend and Images
##############################################################

@app.route('/wore_what', methods=['GET'])
@login_required
def wore_what():
    photos = []
    list_of_friends = db.session.query(followers).filter_by(follower_id=g.user)

    for friend in list_of_friends:
        grab_photos = db.session.query(Userphoto).filter_by(users_id=friend[1])
        for photo in grab_photos:
            photos.append(photo.image)

    # friend_photos = db.session.query(Userphoto).filter_by()
    # photo_comment = db.session.query(UserPhotoComment).filter_by(g.user)
    # videos = db.session.query(UserVideo).filter_by(g.user)
    # video_comment = db.session.query(UserVideoComment).filter_by(g.user)
    rendered_html = render_template('wore_what.html', photos=photos)#, photo_comment=photo_comment, videos=videos, video_comment=video_comment)
    return html_minify(rendered_html)


@app.route('/upload_photo', methods=['GET','POST'])
@login_required
def upload_photo():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print ('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print ('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['WORE_WHAT'], filename))
            insert_photo(g.user, filename)

            flash('Successfully uploaded Photo')
            return redirect(url_for('wore_what', num=1))



def follow(fol_id):
    user_fol = db.session.query(Users).filter_by(id=fol_id).first()
    if user_fol is None:
        return "Not exist"
    elif user_fol == g.user:
        return "Can't follow yourself"

    u_fol = current_user.follow(user_fol)
    if u_fol is None:
        return "Can't follow user"
    db.session.add(u_fol)
    db.session.commit()
    return "Successfully following user"


def unfollow(fol_id):
    user_fol = db.session.query(Users).filter_by(id=fol_id).first()
    if user_fol is None:
        return "Not exist"
    elif user_fol == g.user:
        return "Can't unfollow yourself"

    u = current_user.unfollow(user_fol)
    if u is None:
        return "Can't unfollow user"

    db.session.add(u)
    db.session.commit()
    return "Successfully unfollowed user"


@app.route('/find_friend', methods=['GET', 'POST'])
@login_required
def find_friend():
    friend = Users.query.filter(Users.id != current_user.id).all()
    rendered_html = render_template('test_find_friend.html', friend=friend)
    return html_minify(rendered_html)


@app.route('/friend_handler', methods=['GET', 'POST'])
@login_required
def friend_handler():
    try:
        click = request.args.get('a', None, type=str)
        fol_already = db.session.query(followers).filter_by(follower_id=g.user, followed_id=int(click)).first()

        if fol_already is None:
            return jsonify(result=follow(int(click)))

        else:
            return jsonify(result=unfollow(int(click)))

    except:
        return "An fatal error occurred"


########################################################################################
# PAYPAL PAYPAL PAYPAL PAYPAL PAYPAL PAYPAL PAYPAL PAYPAL PAYPAL PAYPAL PAYPAL PAYPAL
########################################################################################
@app.route('/events/<int:cat>', methods=['GET', 'POST'])
@app.route('/events/<int:cat>/<int:page>', methods=['GET', 'POST'])
def events_listing(cat, page):
    form = GetEventForm()
    event_lst = []
    event_lsts = Event.query.filter_by(category=cat).paginate(page, EVENTS_PER_PAGE, True).items
    event_lst_size = len(Event.query.filter_by(category=cat).all())/EVENTS_PER_PAGE

    for evnt in event_lsts:
        due = time_remainding(evnt.date, evnt.start_time)
        event_lst.append({"id": evnt.id, "creator": evnt.creator, "category": evnt.category, "poster": evnt.poster,
                          "eventname": evnt.eventname, "date": evnt.date, "start_time": evnt.start_time,
                          "end_time": evnt.end_time, "admission": evnt.admission, "venue": evnt.venue, "lat": evnt.lat, "lng": evnt.lng,
                          "capacity": evnt.capacity, "addmission": evnt.admission, "description": evnt.description,
                          "contact": evnt.contact, "days": due[0], "format": evnt.poster_format, "hours": due[1]})

    event_lst.sort(key=lambda x: (x["days"]))

    if request.method == "POST":
        session['event_number'] = form.event_number.data
        return redirect(url_for('payment'))
    rendered_html = render_template('events.html', event_lst=event_lst, event_lst_size=event_lst_size, category=cat, page=page, form=form)
    return html_minify(rendered_html)


@app.route('/watching', methods=['POST', 'GET'])
def watching():
    if current_user.is_anonymous is False:
        event_id = request.args.get('a', None, type=str)

        watching_already = db.session.query(Watching).filter_by(users_id=g.user, event_id=int(event_id)).first()

        if watching_already is None:
            insert_watching(int(event_id), g.user, 'active')
        else:
            if str(watching_already.status) == 'active':
                watch = Watching.query.get(watching_already.id)
                watch.status = 'inactive'
                db.session.commit()
            else:
                watch = Watching.query.get(watching_already.id)
                watch.status = 'active'
                db.session.commit()
    return ""


@app.route('/like', methods=['POST', 'GET'])
def like():
    if current_user.is_anonymous is False:
        event_id = request.args.get('a', None, type=str)

        like_already = db.session.query(Like).filter_by(users_id=g.user, event_id=int(event_id)).first()

        if like_already is None:
            insert_like(int(event_id), g.user, 'active')
        else:
            if str(like_already.status) == 'active':
                watch = Like.query.get(like_already.id)
                watch.status = 'inactive'
                db.session.commit()
            else:
                watch = Like.query.get(like_already.id)
                watch.status = 'active'
                db.session.commit()
    return ""




# @security.context_processor
@app.route('/about', methods=['GET'])
def getsession():
    return redirect('https://goo.gl/VR68jM', code=302)


# @security.context_processor
@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    num = int(session['event_number'])
    form = PaymentForm()
    event = db.session.query(Event).filter_by(id=num).first()
    card_lst = db.session.query(Card).filter_by(user_id=g.user).all()
    if request.method == 'POST':
        user = db.session.query(Users).filter_by(id=g.user).first()
        card = db.session.query(Card).filter_by(id=form.card_num.data, user_id=g.user).first()
        pay = make_payment(str(g.user), str(user.first_name), str(user.last_name), str(card.payment_method),
                           str(card.card_type), int(card.id), str(card.expire_month), int(card.expire_year),
                           str(event.eventname), form.event_num.data, int(event.admission), form.qty.data)
        if pay == True:
            return redirect(url_for('success'))
        else:
            k = str(pay['details'][0]['field']) + ": " + str(pay['details'][0]['issue'])
            return render_template('failure.html', k=k)
    rendered_html = render_template('payment.html', form=form, event=event, card_lst=card_lst, number=num)
    return html_minify(rendered_html)


# @security.context_processor
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = SignupForm()
    lst, ev, event = [], 0, []
    user_id = g.user
    users = db.session.query(Users).filter_by(id=user_id).first()
    history = db.session.query(Payment).filter_by(users_id=user_id).all()
    for i in range(len(history)):
        lst.append(int(history[i].event_id))
    ev = db.session.query(Event).filter(Event.id.in_(lst)).all()
    for j in range(len(ev)):
        event.append({'id': ev[j].id, 'eventname': ev[j].eventname})
    rendered_html = render_template('account.html', users=users, form=form, history=history, event=event)
    return html_minify(rendered_html)


# @security.context_processor
@app.route('/switch', methods=['GET', 'POST'])
@login_required
def switch():
    idnum = request.args.get('u', type=int)
    user = Users.query.filter_by(id=idnum).first()
    if user.urole == "PROMOTER":
        user.urole = "USER"
    else:
        user.urole = "PROMOTER"
    db.session.commit()
    return user.urole


# @security.context_processor
@app.route('/add_payment', methods=['GET', 'POST'])
@login_required
def add_payment():
    form = CardForm()
    user_id = g.user
    user = db.session.query(Users).filter_by(id=user_id).first()
    if form.validate_on_submit():
        new_card = Card(form.card_num.data, None, form.card_type.data, form.expire_month.data, form.expire_year.data,
                        user_id, form.payment_method.data)
        new_card.users_card.append(user)
        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for('home'))
    rendered_html = render_template('add_payment.html', form=form)
    return html_minify(rendered_html)


@app.route('/success', methods=["GET"])
@login_required
def success():
    rendered_html = render_template('success.html')
    return html_minify(rendered_html)


@app.route('/failure', methods=['GET'])
@login_required
def failure():
    rendered_html = render_template('failure.html')
    return html_minify(rendered_html)


def make_payment(user_id, first_name, last_name, payment_method, card_type, card_num, expire_month, expire_year,
                 event_name, event_id, price, qty):
    paypalrestsdk.configure({
        "mode": "sandbox",
        "client_id": "Aac-yXuzoHPnyOcpC3Yde0udhTag2AidoEs1odeGSWQwrmG6xGMtmdWNNNI2pt6uv9ATcyn7qy9Rv40-",
        "client_secret": "EDbX7m-BVsqpr6TkDzmxr4-GmSFVpdJ28Lb8hZA3KFXrkAFH2GzsNb-1z1Zd7bUjAFaM8ltj-wECz6XZ"
    })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": str(payment_method),
            "funding_instruments": [{
                "credit_card": {
                    "type": str(card_type),
                    "number": str(card_num),
                    "expire_month": str(expire_month),
                    "expire_year": str(expire_year),
                    # "cvv2": "874",
                    "first_name": str(first_name),
                    "last_name": str(last_name)}}]},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": str(event_name),
                    "sku": "Ticket",
                    "price": str(price),
                    "currency": "USD",
                    "quantity": int(qty)}]},
            "amount": {
                "total": str((int(qty) * int(price))),
                "currency": "USD"},
            "description": str(first_name) + " purchased " + str(qty) + " ticket(s) to attend " + str(event_name)}]})

    if payment.create():
        payment = Payment(user_id, event_id, card_num, price, qty)
        db.session.add(payment)
        db.session.commit()
        return True
    else:
        return payment.error


# @security.context_processor
@app.route('/what_if_analysis', methods=['GET'])
@login_required
@requires_roles('PROMOTER')
def what_if_analysis():
    ev_id = request.args.get('c', type=int)
    try:
        event = db.session.query(Event).filter_by(creator=g.user).all()
        views = db.session.query(Hit.users_id, func.sum(Hit.number).label('sum')).group_by(Hit.users_id).filter_by(
            event_id=ev_id).order_by('users_id desc').all()
        ratings = db.session.query(Rating).filter_by(event_id=ev_id).order_by('users_id desc').all()
        pay = db.session.query(Payment).filter_by(event_id=ev_id).order_by('users_id desc').all()

        if len(views) < 2 or len(ratings) < 2 or len(pay) < 2:
            rendered_html = render_template("failure.html", k="There is not enough data to do the processing")
            return html_minify(rendered_html)

        test = False
        for i in event:
            if i.id == ev_id:
                test = True

        if test == False:
            rendered_html = render_template("failure.html", k="You are not allowed to look at this event!")
            return html_minify(rendered_html)
        view_lst = []
        rating_lst = []
        for p in range(len(pay)):
            for v in range(len(views)):
                if views[v].users_id == pay[p].users_id:
                    number = int(views[v].sum)
                    view_lst.append({'users_id': views[v].users_id, 'number': number})

            for r in range(len(ratings)):
                if ratings[r].users_id == pay[p].users_id:
                    rating_lst.append({'users_id': ratings[r].users_id, 'rate': ratings[r].rate})

        if len(view_lst) > len(rating_lst):
            lst = len(view_lst)
        else:
            lst = len(rating_lst)

        betas = []
        y_vals = []
        for i in range(lst):
            betas.append([view_lst[i]['number'], rating_lst[i]['rate']])
            y_vals.append(int(pay[i].quantity))

        clf = linear_model.LinearRegression()
        clf.fit(betas, y_vals)
        rendered_html = render_template('what_if_analysis.html', coefficient=clf.coef_, intercept=clf.intercept_)
        return html_minify(rendered_html)

    except:
        if len(views) < 2 and len(ratings) < 2 and len(pay) < 2:
            rendered_html = render_template("failure.html", k="There is not enough data to do the processing")
            return html_minify(rendered_html)

        else:
            rendered_html = render_template("failure.html")
            return html_minify(rendered_html)


def filtered_recommendation():
    rating = db.session.query(Rating).order_by(Rating.users_id).all()
    rating2 = db.session.query(Rating).distinct(Rating.users_id).all()
    if rating:
        dic = {}
        dic2 = {}
        for j in range(len(rating2)):
            for r in range(len(rating)):
                if rating[r].users_id == rating2[j].users_id:
                    dic[str(rating[r].event_id)] = int(rating[r].rate)
            dic2[str(rating2[j].users_id)] = dic
            dic = {}

        dic3 = dic2
        for key2 in dic3:
            for key in dic2:
                if len(dic3[key2]) == len(dic2[key]):
                    algorithm = randint(1, 3)
                else:
                    algorithm = 4
                    break
        rec = ratings_recommender(str(g.user), dic2, algorithm)
        cln = k_nearest_neighbour(str(g.user), dic2, 2, algorithm)

        del dic2[str(g.user)]
        predicted_lst = []
        for key3 in dic2:
            for i in range(len(rec)):
                if rec[i][0] in dic2[key3]:
                    if event_judge([(cln[0][1], cln[0][0], rec[i][0], rec[i][1]),
                                    (cln[1][1], cln[1][0], rec[i][0], rec[i][1])]) > 2:
                        predicted_lst.append(rec[i][0])

        raw_lst = []
        for w in range(len(rec)):
            raw_lst.append(rec[w][0])

        return [raw_lst, predicted_lst]


# @security.context_processor
@app.route("/welcome", methods=['GET', 'POST'])
@login_required
def welcome():
    category_list = db.session.query(Category).all()
    user_id = g.user
    user = db.session.query(Users).filter_by(id=user_id).first()
    if request.method == 'POST':
        for cat in category_list:
            if request.form.get(cat.category_name):
                cat1 = Category.query.filter_by(id=cat.id).first()
                user.users_category.append(cat1)
                db.session.commit()
        return redirect(url_for('home'))
    rendered_html = render_template('welcome.html', lst=category_list)
    return html_minify(rendered_html)


# @security.context_processor
@app.route('/newevent', methods=['GET', 'POST'])
@login_required
@requires_roles('PROMOTER')
def newevent():
    form = EventForm()
    user_id = g.user
    if form.validate_on_submit():
        poster = form.poster.data
        filename = secure_filename(poster.filename)

        # Get poster type: Image vs Video
        poster_list = poster.split('.')
        if poster_list[len(poster_list)-1] == "jpg" or poster_list[len(poster_list)-1] == "jpeg" or poster_list[len(poster_list)-1] == "png":
            poster_format = "image"
        else:
            poster_format = "video"

        form.poster.data.save(os.path.join('app/static/posters', filename))
        insert_event(user_id, form.category.data, filename, form.eventname.data, form.date.data, form.start_time.data,
                     form.end_time.data, form.venue.data, form.lat.data, form.lng.data, form.capacity.data,
                     form.admission.data, form.description.data, form.contact.data, poster_format)
        return redirect(url_for('home'))
    rendered_html = render_template('newevent.html', form=form, user_id=user_id)
    return html_minify(rendered_html)

# @security.context_processor
@app.route('/details/<idnum>', methods=['GET', 'POST'])
def details(idnum):
    form = GetEventForm()
    if request.method == "POST":
        session['event_number'] = form.event_number.data
        return redirect(url_for('payment'))
    event = Event.query.filter_by(id=idnum).first()
    category = Category.query.filter_by(id=event.category).first()
    user_id = g.user
    users = Users.query.filter_by(id=user_id).first()

    contact = Users.query.all()
    event_id = idnum
    hit = Hit.query.filter_by(event_id=idnum).first()
    rendered_html = render_template('details.html', form=form, hit=hit, event=event, category=category, user_id=user_id,
                           event_id=event_id, users=users, contact=contact)
    return html_minify(rendered_html)

def getUsername(user_id):
    user = Users.query.filter_by(id=user_id).first()
    return [user.username, user.pic]


app.jinja_env.globals.update(getEmail=getUsername)


# @security.context_processor
@app.route('/statistics', methods=['GET', 'POST'])
@login_required
@requires_roles('PROMOTER')
def stats():
    user_id = g.user
    creator = Users.query.filter_by(id=user_id).first()
    events = Event.query.filter_by(creator=creator.id).all()
    rendered_html = render_template('test.html', events=events, creator=creator)
    return html_minify(rendered_html)


# @security.context_processor
@app.route('/update_event', methods=['GET', 'POST'])
@login_required
def update_event():
    idnum = request.args.get('c', type=int)
    event = Event.query.filter_by(id=idnum).first()
    form = UpdateForm()
    if request.method == "POST":
        idnum = form.idnum.data
        event = Event.query.filter_by(id=idnum).first()
        if form.poster.data:
            event.poster = form.poster.data
        if form.eventname.data:
            event.eventname = form.eventname.data
        if form.category.data:
            event.category = form.category.data
        if form.date.data:
            event.date = form.date.data
        if form.start_time.data:
            event.start_time = form.start_time.data
        if form.end_time.data:
            event.end_time = form.end_time.data
        if form.venue.data:
            event.venue = form.venue.data
        if form.lat.data:
            event.lat = form.lat.data
        if form.lng.data:
            event.lng = form.lng.data
        if form.capacity.data:
            event.capacity = form.capacity.data
        if form.admission.data:
            event.admission = form.admission.data
        if form.description.data:
            event.description = form.description.data
        if form.contact.data:
            event.contact = form.contact.data
        db.session.commit()
        return redirect(url_for("details", idnum=idnum))
    rendered_html = render_template('event_update.html', event=event, form=form)
    return html_minify(rendered_html)

# @security.context_processor
@app.route('/stats', methods=['GET', 'POST'])
@login_required
@requires_roles('PROMOTER')
def getStats():
    idnum = request.args.get('c', type=int)
    event = Event.query.filter_by(id=idnum).first()
    ratings = []
    for i in range(5, 0, -1):
        ratings.append(Rating.query.filter_by(event_id=idnum, rate=i).count())
    comments = []
    sql = text(
        """SELECT count(Comment.id) AS counts,sum(CAST(Comment.percentage AS DECIMAL(9,2))) AS csum FROM Comment WHERE Comment.event_id =:idnums GROUP BY Comment.status""")
    comment_sum = db.engine.execute(sql, idnums=idnum)
    for comment in comment_sum:
        comments.append(str(json.dumps(round(float(comment['csum']) / comment['counts'] * 100, 1))))
    i = 1
    days = []
    visits = []
    hits = Hit.query.with_entities(func.sum(Hit.number).label('sum')).group_by(Hit.timestamp).filter(
        Hit.event_id == idnum).order_by("timestamp asc").all()
    for hit in hits:
        visits.append(hit.sum)
        days.append("day" + str(i))
        i += 1
    rendered_html = render_template('event_stats.html', event=event, ratings=json.dumps(ratings), visits=json.dumps(visits),
                           comments=json.dumps(comments), days=days)
    return html_minify(rendered_html)

# @security.context_processor
@app.route('/comment_sent', methods=['GET', 'POST'])
def add_comment():
    post = request.args.get('b', type=str)
    event_id = request.args.get('c', type=str)
    user_id = request.args.get('d', type=str)
    status = sentiment(post)[0]
    percentage = str(sentiment(post)[1] * 100)[:5]
    comment = Comment(user_id, event_id, post, status, percentage)
    db.session.add(comment)
    db.session.commit()
    return jsonify(result=post)


# @security.context_processor
@app.route('/comment_recieved')
def get_comments():
    event_id = request.args.get('c', type=str)
    comments = Comment.query.filter_by(event_id=event_id).order_by('id desc').all()
    rendered_html = render_template('comments.html', comments=comments)
    return html_minify(rendered_html)


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            e_mail = form.email.data
            password = form.password.data
            registered_user = Users.query.filter_by(email=e_mail, password=password).first()
            if registered_user is None:
                err = "Email or Password is invalid"
                rendered_html = render_template("login.html", err=err, form=form, title='Register')
                return html_minify(rendered_html)

            session['logged_in'] = True
            session['user'] = email
            login_user(registered_user, remember=form.remember.data)
            return redirect(request.args.get('next') or url_for('home'))
    rendered_html = render_template("login.html", form=form, title='Register')
    return html_minify(rendered_html)


@app.route('/recover_account', methods=['GET', 'POST'])
def recover_account():
    form = RecoverAccountForm()
    if request.method == "POST":
        if form.validate_on_submit():
            e_mail = form.email.data
            user_exist = Users.query.filter_by(email=e_mail).first()

            if user_exist is None:
                flash("Sorry, but you are not a user! Please sign up!")
                return redirect(url_for('signup'))

            else:
                unique_string = uuid.uuid4()
                message_sender("Click here: " + "http://localhost/verification/" + unique_string,
                               ["cruze.m.mcfarlane@gmail.com"])
                render_html = render_template("account_recovery_mail_sent.html")
                return html_minify(render_html)
    rendered_html = render_template("recover_account.html", form=form)
    return html_minify(rendered_html)


# @app.route('/verification/<str:link>', methods=['GET', 'POST'])
# def verification(link):
#     return link


@app.route('/social_login', methods=['GET', 'POST'])
def social_login():
    rendered_html = render_template("social_login.html", title='Social Login')
    return html_minify(rendered_html)


@app.route('/login3', methods=['GET', 'POST'])
def login3():
    try:
        user_data = request.args['a']
        js = json.loads(user_data)
        # pdb.set_trace()
        print js
        return redirect(url_for('home'))
    except IOError:
        return "Error: can't find file or read data"


@app.before_request
def before_request():
    g.user = current_user.get_id()


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('landing'))


@login_manager.unauthorized_handler
def unauthorized():
    rendered_html = render_template('unauthorized.html')
    return html_minify(rendered_html)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        pic = request.files['profile_pic']
        if pic and allowed_file(pic.filename):
            filename = secure_filename(pic.filename)
            first_name = form.first_name.data
            last_name = form.last_name.data
            username = form.username.data
            password = form.password.data
            email = form.email.data
            address = form.address.data
            age = form.age.data
            sex = form.sex.data
            utype = form.utype.data
            new_user = Users(first_name, last_name, username, filename, email, address, sex, age, password, utype)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.session.add(new_user)
            db.session.add(new_user.follow(new_user))
            db.session.commit()
            return redirect(url_for('login'))
    rendered_html = render_template('signup.html', form=form)
    return html_minify(rendered_html)


@app.route('/rating_sent', methods=['GET', 'POST'])
@login_required
def rating_sent():
    rating_num = request.args.get('a', None, type=str)
    user_id = g.user
    # Test for number
    try:
        val = int(rating_num)
        if val <= 10:
            return jsonify(result=rating_num)

        elif val >= 11:
            e_id = int(str(val)[1:])  # Event ID
            e_num = int(str(val)[0])  # Event Rating

            # Update if rating already exist
            if db.session.query(Rating).filter_by(event_id=e_id, users_id=user_id).first():
                id_no = db.session.query(Rating).filter_by(event_id=e_id, users_id=user_id).first()
                new_rating = Rating.query.get(id_no.id)
                new_rating.rate = e_num
                db.session.commit()
                return jsonify(result=rating_num)

            else:
                user_rating = Rating(event_id=e_id, users_id=user_id, rate=e_num)
                db.session.add(user_rating)
                db.session.commit()
                return jsonify(result=rating_num)

    except ValueError:
        return jsonify(result=rating_num)


@app.route('/feed_test', methods=['GET', 'POST'])
@login_required
def feed_test():
    rendered_html = render_template('feed_test.html')
    return html_minify(rendered_html)

@app.route('/recommendations', methods=['GET', 'POST'])
@login_required
def recommend():
    user_id = g.user
    recommend_list = {}
    recommend_ = []
    recommends = []
    users = Users.query.filter_by(id=user_id).first()
    category = users.users_category
    for cat in users.users_category:
        events = Event.query.filter_by(category=cat.id).all()
        for event in events:
            recommend_list.update(top_recommend(event.id))
    recommend_list = ValueSortedDict(recommend_list, reverse=True)
    for key in recommend_list:
        recommends.append(Event.query.filter_by(id=key).first())
    for evnt in recommends:
        due = time_remainding(evnt.date, evnt.start_time)
        recommend_.append(
            {"creator": evnt.creator, "category": evnt.category, "poster": evnt.poster, "eventname": evnt.eventname,
             "date": evnt.date, "star_time": evnt.start_time, "end_time": evnt.end_time, "venue": evnt.venue,
             "lat": evnt.lat, "lng": evnt.lng, "capacity": evnt.capacity, "addmission": evnt.admission,
             "description": evnt.description, "contact": evnt.contact, "days": due[0], "hours": due[1]})

    recommend_.sort(key=lambda x: (x["days"]))
    catlist = []
    for c in category:
        for v in recommend_:
            if v.get('category') == c.id and v.get('days') > 0:
                if i.category_name not in cat_list:
                    catlist.append(c.category_name)
    rendered_html = render_template('recommendations.html', recommend=recommend_, recommends=recommends, category=category,
                           cat_list=cat_list)
    return html_minify(rendered_html)


def top_recommend(event_id):
    events = Event.query.filter_by(id=event_id).all()
    events_dict = {}
    for event in events:
        total_comment = 0.0
        total_rate = 0.0
        total_clicks = 0.0
        comments = Comment.query.filter_by(event_id=event.id).all()
        comments_count = Comment.query.filter_by(event_id=event.id).count()
        ratings = Rating.query.filter_by(event_id=event_id).all()
        ratings_count = Rating.query.filter_by(event_id=event_id).count()
        clicks = Hit.query.filter_by(event_id=event_id).all()
        clicks_count = Hit.query.filter_by(event_id=event_id).count()
        for comment in comments:
            total_comment += float(comment.percentage)
        for r in ratings:
            total_rate = total_rate + r.rate
        for click in clicks:
            total_clicks = total_clicks + click.number
        if comments_count != 0:
            total_comment = total_comment / comments_count
        if ratings_count != 0:
            total_rate = total_rate / ratings_count
        if clicks_count != 0:
            total_clicks = total_clicks / clicks_count
        events_dict[str(event.id)] = int(round(total_rate + total_comment + total_clicks))
    return events_dict


app.jinja_env.globals.update(top_recommend=top_recommend)


@app.route('/page_count', methods=['GET', 'POST'])
@login_required
def page_clicks():
    if request.method == 'GET':
        event_id = request.args.get('c', type=str)
        user_id = g.user
        event_hit = Hit.query.filter_by(event_id=event_id, users_id=user_id,
                                        timestamp=datetime.datetime.now().strftime("%Y-%m-%d")).first()
        if event_hit:
            hits = event_hit.number
            up_hits = int(hits) + 1
            event_hit.number = up_hits
            db.session.add(event_hit)
            db.session.commit()
        else:
            hits = 1
            new_hit = Hit(event_id, user_id, hits)
            db.session.add(new_hit)
            db.session.commit()
        return event_hit.number


def sum_page_count(event_id):
    event_hit = Hit.query.filter_by(event_id=event_id).all()
    total = 0
    for hits in event_hit:
        total = total + hits.number
    return total


app.jinja_env.globals.update(sum_page_count=sum_page_count)


def cat_list():
    category_list = db.session.query(Category).all()
    return category_list


app.jinja_env.globals.update(cat_list=cat_list)


def user():
    user_id = g.user
    if user_id:
        user = Users.query.filter_by(id=user_id).first()
        return user.usersname
    else:
        return "Guest"


app.jinja_env.globals.update(user=user)

def email():
    user_id = g.user
    if user_id:
        user = Users.query.filter_by(id=user_id).first()
        return user.email
    else:
        return "No email"


app.jinja_env.globals.update(email=email)


def categorys():
    category = Category.query.all()
    return category


app.jinja_env.globals.update(categorys=categorys)


def user_role():
    user_id = g.user
    if user_id:
        user = Users.query.filter_by(id=user_id).first()
        return user.urole


app.jinja_env.globals.update(user_role=user_role)


def picture():
    user_id = g.user
    if user_id:
        user = Users.query.filter_by(id=user_id).first()
        return user.pic
    else:
        return "Guest"


app.jinja_env.globals.update(picture=picture)


@app.route('/search', methods=["POST", "GET"])
def search():
    if request.method == 'POST':
        search_text = request.form['search_text']
        if search_text:
            events = Event.query.filter(Event.eventname.like('%' + search_text + '%')).order_by("id desc").all()
            rendered_html = render_template('search.html', events=events, search_text=search_text)
            return html_minify(rendered_html)


@app.route('/usersearch', methods=["POST", "GET"])
def usearch():
    if request.method == 'POST':
        search_text = request.form['search_text']
        if search_text:
            user = Users.query.filter_by(usersname=search_text).first()
            if user:
                return user.pic
            else:
                return "testing-mindfire-1.jpg"


def time_remainding(dates, time):
    if dates and time:
        dates = dates.replace(",", "").split()
        month = list(calendar.month_name).index(dates[1])
        time = time.replace("am", "")
        time = time.replace("pm", "")
        time = time.split(":")
        remaining = (datetime.datetime(int(dates[2]), int(month), int(dates[0]), int(time[0]), int(time[1]),
                                       0) - datetime.datetime.now())
        return [remaining.days, remaining.seconds / 3600]
    return [0, 0]


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404