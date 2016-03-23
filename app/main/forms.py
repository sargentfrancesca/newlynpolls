from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, IntegerField, DateField, SelectMultipleField, HiddenField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User, Prompt, Event, PromptEvent, Location
from random import randint

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Your Institution/Organisation/Collective/Individual name', validators=[Length(0, 64)])
    location = StringField('Your Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About you')
    user_type = SelectField('Your Profile Type', choices=[("institution", "Institution"), ("organisation", "Organisation"), ("collective", "Collective"), ("individual", "Individual"), ("other", "Other")])
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Your Institution/Organisation/Collective/Individual name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About you')
    user_type = SelectField('Your Profile Type', choices=[("institution", "Institution"), ("organisation", "Organisation"), ("collective", "Collective"), ("individual", "Individual"), ("other", "Other")])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    body = TextAreaField('Opinion', validators=[Required()])
    name = StringField('Name/Alias', validators=[Length(0, 64)])
    age = IntegerField('Age')
    gender = SelectField('Gender', choices=[('f', 'Female'), ('m', 'Male'), ('o', 'Other'), ('p', 'Prefer Not to Say')])
    passion = StringField('Profession/Passion', validators=[Length(0, 200)])
    prompt = HiddenField()
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        current_event = Event.get_current()
        event_prompts_count = current_event.prompts.count()
        event_id = randint(0,(event_prompts_count - 1))
        random_prompt_text = current_event.prompts[event_id].prompt.text
        random_prompt_id = current_event.prompts[event_id].prompt.id
        self.prompt.data = random_prompt_id
        self.prompttext = random_prompt_text
        self.body.label.text = ''


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')

class EventForm(Form):
    location = StringField('Location Name', validators=[Required()])
    date_start = StringField('Event Start Date')
    date_end = StringField('Event End Date')
    current = BooleanField('This is our current event (all entries will refer to this, and will appear as default)')
    event_type = SelectField('Event Type', choices=[("exhibition", "Exhibition"), ("installation", "Installation"), ("workshop", "Workshop"), ("other", "Other")])
    submit = SubmitField('Submit')


class CollectionForm(Form):
    name = StringField('Collection Name or Alias', validators=[Required()])
    prompts = SelectMultipleField('Select Prompts', coerce=int, option_widget=None)
    public = BooleanField('This Collection can be seen and chosen by others')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.prompts.choices = [(prompt.id, prompt.text)
                             for prompt in Prompt.query.order_by(Prompt.text).all()]
        self.user = user

class PromptForm(Form):
    text = TextAreaField('Prompt Text', validators=[Required()])
    submit = SubmitField('Submit')
