from . import db
import datetime

ACTIVE_PATRON = 1
PROMOTER = 1
INACTIVE_USER = 0

selected_event = db.Table(
    'selected_event',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    )

selected_category = db.Table(
    'selected_category',
    db.Column('users_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('category', db.Integer, db.ForeignKey('category.id'))
    )

card_association = db.Table(
    'card_association',
    db.Column('users_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('card_id', db.BIGINT, db.ForeignKey('card.id'))
    )

roles_users = db.Table(
    'roles_users',
    db.Column('users_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    category_name = db.Column(db.String(80), nullable=False, index=True)
    image = db.Column(db.String(80), nullable=False)

    categories = db.relationship('Users', secondary=selected_category, backref=db.backref('users_category', lazy='dynamic'))
    events = db.relationship('Event', backref='category_event', lazy='dynamic')

    def __init__(self, category_name, image):
        self.category_name = category_name
        self.image = image

    def __repr__(self):
        return '<category %r>' % self.category_name


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    creator = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    poster = db.Column(db.String(120))
    poster_format = db.Column(db.String(7))
    eventname = db.Column(db.String(120))
    date = db.Column(db.String(120))
    start_time = db.Column(db.String(80))
    end_time = db.Column(db.String(80))
    venue = db.Column(db.String(80))
    lat = db.Column(db.String(80))
    lng = db.Column(db.String(80))
    capacity = db.Column(db.Integer)
    admission = db.Column(db.Numeric(10, 2))
    description = db.Column(db.String(120))
    contact = db.Column(db.BIGINT)

    comments = db.relationship('Comment', backref='event_comment', lazy='dynamic')
    ratings = db.relationship('Rating', backref='event_rating', lazy='dynamic')
    hit = db.relationship('Hit', backref='event_hit', lazy='dynamic')
    payments = db.relationship('Payment', backref='event_payment', lazy='dynamic')
    
    def __init__(self, creator, category, poster, eventname, date, start_time, end_time, venue, lat, lng, capacity,\
                 admission, description, contact, poster_format):
        self.creator = creator
        self.category = category
        self.poster = poster
        self.eventname = eventname
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.venue = venue
        self.lat = lat
        self.lng = lng
        self.capacity = capacity
        self.admission = admission
        self.description = description
        self.contact = contact
        self.poster_format = poster_format

    def __repr__(self):
        return '<Event %r>' % self.eventname


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    usersname = db.Column(db.String(120), index=True)
    pic = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(80))
    address = db.Column(db.String(120))
    sex = db.Column(db.String(8))
    age = db.Column(db.String(30))
    confirmed_at = db.Column(db.DateTime())
    active = db.Column(db.Boolean())
    last_seen = db.Column(db.DateTime)
    urole = db.Column(db.String(8))

    comments = db.relationship('Comment', backref='users_comment', lazy='dynamic')
    payments = db.relationship('Payment', backref='users_payment', lazy='dynamic')
    user_photo = db.relationship('Userphoto', backref='users_photo', lazy='dynamic')
    user_photo_comment = db.relationship('Userphotocomment', backref='users_photo_comment', lazy='dynamic')
    user_video = db.relationship('Uservideo', backref='users_video', lazy='dynamic')
    user_video_comment = db.relationship('Uservideocomment', backref='users_video', lazy='dynamic')

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users_roles', lazy='dynamic'))
    events = db.relationship('Event', secondary=selected_event, backref=db.backref('users_event', lazy='dynamic'))
    cards = db.relationship('Card', secondary=card_association, backref=db.backref('users_card', lazy='dynamic'))
    followed = db.relationship('Users',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    
    def __init__(self, first_name, last_name, usersname, pic, email, address, sex, age, password, urole):
        self.password = password
        self.pic = pic
        self.first_name = first_name
        self.last_name = last_name
        self.usersname = usersname
        self.email = email
        self.address = address
        self.sex = sex
        self.urole = urole
        self.age = age

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    def active_prom(self):
        return self

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 

    def get_urole(self):
        return self.urole

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    # def followed_posts(self):
    #     return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
    #         followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def __repr__(self):
        return '<users %r>' % self.usersname


class Connection(db.Model):
    # __tablename__ = 'connection'
    # def __init__(self, *args, **kwargs):
    #     self.user_id = kwargs['user_id']
    #     self.provider_id = kwargs['provider_id']
    #     self.provider_user_id = kwargs['provider_user_id']
    #     self.access_token = kwargs['access_token']
    #     self.secret = kwargs['secret']
    #     self.display_name = kwargs['display_name']
    #     self.profile_url = kwargs['profile_url']
    #     self.image_url = kwargs['image_url']
    #     self.rank = kwargs.get('rank')
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)


# class Tracking(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     last_login_at
#     current_login_at
#     last_login_ip
#     current_login_ip
#     login_count


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    post = db.Column(db.String(160))
    status = db.Column(db.String(8))
    percentage = db.Column(db.String(8))
    timestamp = db.Column(db.DateTime)

    def __init__(self, users_id, event_id, post, status, percentage):
        self.users_id = users_id
        self.event_id = event_id
        self.post = post
        self.status = status
        self.percentage = percentage
        self.timestamp = datetime.datetime.now()

    def __repr__(self):
        return '<Comment %r>' % self.users_id


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    rate = db.Column(db.Integer, nullable=False)
    
    def __init__(self, event_id, users_id, rate):
        self.event_id = event_id
        self.users_id = users_id
        self.rate = rate

    def __repr__(self):
        return '<Rating %r>' % self.rate


class Hit(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    number = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Date)

    def __init__(self, event_id, users_id, number):
        self.event_id = event_id
        self.users_id = users_id
        self.number = 1
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

    def __repr__(self):
        return '<Hit %r>' % (self.number)


class Card(db.Model):
    id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
    card_cvv = db.Column(db.Integer)
    card_type = db.Column(db.String(12))
    expire_month = db.Column(db.String(10))
    expire_year = db.Column(db.Integer)
    payment_method = db.Column(db.String(20))

    def __init__(self, id, card_cvv, card_type, expire_month, expire_year, user_id, payment_method):
        self.id = id
        self.card_cvv = card_cvv
        self.card_type = card_type
        self.expire_month = expire_month
        self.expire_year = expire_year
        self.user_id = user_id
        self.payment_method = payment_method

    def __repr__(self):
        return '<Card number %r>' % self.id


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    card_num = db.Column(db.BIGINT)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

    def __init__(self, users_id, event_id,  card_num, price, quantity):
        self.users_id = users_id
        self.event_id = event_id
        self.card_num = card_num
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return '<Transaction amount %r>' % (self.price * self.quantity)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    sender_id = db.Column('sender_id', db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column('receiver_id', db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime())


class ChatStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20))


class Userphoto(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    image = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime())

    user_photo_comment = db.relationship('Userphotocomment', backref='user_photo_user_comment', lazy='dynamic')

    def __init__(self, users_id, image, timestamp):
        self.users_id = users_id
        self.image = image
        self.timestamp = timestamp

class Userphotocomment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    image_id = db.Column('image_id', db.Integer, db.ForeignKey('userphoto.id'))
    comment = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime())


class Uservideo(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    video = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime())

    user_video_comment = db.relationship('Uservideocomment', backref='user_video_user_comment', lazy='dynamic')


class Uservideocomment(db.Model):
    commenter_id = db.Column('commenter_id', db.Integer, db.ForeignKey('users.id'))
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    video_id = db.Column('video_id', db.Integer, db.ForeignKey('uservideo.id'))
    comment = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime())


class Watching(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(10))

    def __init__(self, event_id, users_id, status):
        self.event_id = event_id
        self.users_id = users_id
        self.status = status

    def __repr__(self):
        return '<Watching %r>' % self.event_id

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_id = db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    users_id = db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(10))

    def __init__(self, event_id, users_id, status):
        self.event_id = event_id
        self.users_id = users_id
        self.status = status

    def __repr__(self):
        return '<Like %r>' % self.event_id