from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, IntegerField, DateField, SelectMultipleField, HiddenField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User, Prompt, Event, PromptEvent
from random import randint
from sqlalchemy.sql.expression import func, select

class PostForm(Form):
    body = TextAreaField('Opinion', validators=[Required()])
    name = StringField('Name/Alias', validators=[Length(0, 64)])
    age = IntegerField('Age')
    gender = SelectField('Gender', choices=[('f', 'Female'), ('m', 'Male'), ('o', 'Other'), ('p', 'Prefer Not to Say')])
    passion = StringField('Profession/Passion', validators=[Length(0, 200)])
    prompt = StringField()
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        current_event = Event.get_current()
        random_prompt_event = current_event.prompts.order_by(func.rand()).first()
        random_prompt = random_prompt_event.prompt
        self.random_prompt = random_prompt
        self.body.label.text = ''


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')