from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, FileField, PasswordField, SubmitField, RadioField, IntegerField, SelectField, validators
from wtforms.validators import DataRequired, InputRequired, Email
from flask_wtf.file import FileField, FileRequired
from app.models import *

c_type = [('','Card Type'), ('visa','Visa'), ('mastercard', 'MasterCard'), ('amex', 'Amex'), ('jcb', 'JCB'), ('discover', 'Discover')]
e_month = [('','Expire Month'), ('01','Jan'), ('02','Feb'), ('03','Mar'), ('04','Apr'), ('05','May'), ('06','June'), ('07','July'), ('08','Aug'), ('09','Sept'), ('10','Oct'), ('11','Nov'), ('12','Dec')]
p_method = [('', 'Payment Method'), ('credit_card','Credit Card'), ('debit_card','Debit Card')]
e_year=[('','Expire year')]
for i in range(2016, 2031):
  e_year.append((str(i), str(i)))

def getCategory():
    category_names = [("", "Select Category")]
    try:
        cat = Category.query.all()
        for z in cat:
            category_names.append((str(z.id), z.category_name))
        return category_names
    except Exception:
        return category_names

class Login2(FlaskForm):
    username = StringField('Username', validators=[DataRequired])
    password = PasswordField('Password', validators=[DataRequired])
    remember = BooleanField('Remember me')
    confirm = SubmitField('Login')

class EventForm(FlaskForm):
    poster = FileField('Poster')
    eventname = StringField('Event Name', validators=[DataRequired()])
    category = SelectField('Category', choices=getCategory(), validators=[DataRequired()])
    date = StringField('date')
    start_time = StringField('start_time')
    end_time = StringField('end_time')
    venue = StringField('venue')
    lat = StringField('lat')
    lng = StringField('lng')
    capacity = StringField('capacity')
    admission = StringField('admission')
    description = StringField('description')
    contact = StringField('contact')


class UpdateForm(FlaskForm):
    idnum = StringField('id')
    poster = FileField('Poster')
    eventname = StringField('Event Name')
    category = SelectField('Category', choices=getCategory())
    date = StringField('date')
    start_time = StringField('start_time')
    end_time = StringField('end_time')
    venue = StringField('venue')
    lat = StringField('lat')
    lng = StringField('lng')
    capacity = StringField('capacity')
    admission = StringField('admission')
    description = StringField('desription')
    contact = StringField('contact')


class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = Users.query.filter_by(email=self.email.data).first()
        if user is None:
            self.email.errors.append('Invalid email')
            return False

        if user.password != self.password.data:
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True


class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('User Name', validators=[DataRequired(), validators.DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), validators.DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    confirm = PasswordField('Re-type Password', validators=[DataRequired(), validators.EqualTo('password', message='Passwords doesn\'t match')])
    address = StringField('Address', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    profile_pic = FileField('Profile Picture', validators=[FileRequired()])
    sex = RadioField('Sex', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    utype = SelectField('Account Type', choices=[("", "Select Account Type"), ("USER", "User"), ("PROMOTER", "Promoter")], validators=[validators.DataRequired(message='Please Select an account Type')])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = Users.query.filter_by(usersname=self.username.data).first()
        if user:
            self.email.errors.append('Email already taken')
            return False

        email = Users.query.filter_by(email=self.email.data).first()
        if email:
            self.email.errors.append('Account already created with this email')
            return False

        self.user = user
        return True


class CommentForm(FlaskForm):
    post = StringField('Post', [DataRequired()])
    submit = SubmitField('Post')


class CategoryForm(FlaskForm):
    parties = BooleanField('PARTIES')
    cultures = BooleanField('CULTURES')
    foods = BooleanField('FOODS')
    religious = BooleanField('RELIGIOUS')
    sports = BooleanField('SPORTS')
    education = BooleanField('EDUCATION')
    social = BooleanField('SOCIAL')
    charity = BooleanField('CHARITY')
    corporate = BooleanField('CORPORATE')


class CardForm(FlaskForm):
    card_num = IntegerField('Card Number', validators=[DataRequired()])
    card_type = SelectField('Card Type', choices=c_type, validators=[validators.DataRequired(message='Please Select a card Type')])
    expire_month = SelectField('Expire Month', choices=e_month, validators=[validators.DataRequired(message='Please select a valid Expiration Month')])
    expire_year = SelectField('Expire Year', choices=e_year, validators=[validators.DataRequired(message='Please select a valid Expiration Year')])
    payment_method = SelectField('Payment Method', choices=p_method, validators=[validators.DataRequired(message='Please select your payment method')])

class PaymentForm(FlaskForm):
    card_num = RadioField('Card Number', validators=[InputRequired()])
    event_num = IntegerField('Price', validators=[InputRequired()])
    qty = IntegerField('Quantity', validators=[InputRequired()])

class GetEventForm(FlaskForm):
    event_number = IntegerField('Event Number')