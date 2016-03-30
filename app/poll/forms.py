from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField, IntegerField, DateField, SelectMultipleField, HiddenField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User, Prompt, Event, PromptEvent, CollectionPrompt
from random import randint
from sqlalchemy.sql.expression import func, select

class PostForm(Form):
    body = TextAreaField('Opinion', validators=[Required()])
    name = StringField('Name/Alias', validators=[Length(0, 200)])
    age = IntegerField('Age')
    gender = SelectField('Gender', choices=[('f', 'Female'), ('m', 'Male'), ('o', 'Other'), ('p', 'Prefer Not to Say')])
    passion = StringField('Profession/Passion', validators=[Length(0, 200)])
    prompt = StringField()
    prompts = SelectField('Select a Question', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        current_event = Event.get_current(user)
        print current_event.name
        print current_event.user.username
        print CollectionPrompt.query.filter_by(collection=current_event.collection).all()
        self.prompts.choices = [(collection.prompt_id, collection.prompt.text)
                             for collection in CollectionPrompt.query.filter_by(collection=current_event.collection).all()]


class CommentForm(Form):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')