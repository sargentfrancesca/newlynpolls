from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import poll
from .forms import PostForm 
from .. import db
from ..models import Permission, Role, User, Post, Comment, Event, Prompt, PromptEvent
from ..decorators import admin_required, permission_required
from sqlalchemy.sql.expression import func, select

@poll.route('/', methods=['GET', 'POST'])
def home():

    return render_template('poll/home.html')


@poll.route('/vote', methods=['GET', 'POST'])
def voting():
    user = User.query.filter_by(username="mediumra_re").first()
    form = PostForm(user=user)
    print form.prompts.data
    if form.validate_on_submit():

        post = Post(user=user)
        post.name = form.name.data

        post.age = form.age.data
        post.gender = form.gender.data
        post.body = form.body.data
        post.passion = form.passion.data
        post.event = Event.query.filter_by(name="The General Opinion").first()
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser
        post.prompt = Prompt.query.filter_by(id=form.prompts.data).first()
        post.user = user
        db.session.add(post)
        db.session.commit()
        flash('Submitted')
        return redirect(url_for('poll.home'))

    return render_template('poll/poll.html', form=form, user=user)

@poll.route('/<username>', methods=['GET', 'POST'])
def vote(username):
    user = User.query.filter_by(username=username).first()
    print "User 1", username
    form = PostForm(user=user)
    print form.prompts.data
    if form.validate_on_submit():

        post = Post(user=user)
        post.name = form.name.data

        post.age = form.age.data
        post.gender = form.gender.data
        post.body = form.body.data
        post.passion = form.passion.data
        post.event = Event.get_current(user=user)
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser
        print "Prompt", Prompt.query.filter_by(id=form.prompt.data).first()
        post.prompt = Prompt.query.filter_by(id=form.prompts.data).first()
        post.user = user
        db.session.add(post)
        db.session.commit()
        flash('Submitted')
        return redirect(url_for('poll.home'))

    return render_template('poll/poll.html', form=form, user=user)


@poll.route('/random/all')
def randompoll():
    random_opinion = Post.query.order_by(func.rand()).first()

    request.randomtype = 'all'

    return render_template('poll/random.html', post=random_opinion)

@poll.route('/randomajax')
def randomajax():
    random_opinion = [Post.query.order_by(func.rand()).first()]

    opinions = [(r.body, r.prompt.text) for r in random_opinion]
    return jsonify(opinions=opinions) 

@poll.route('/randomeventajax/<int:id>')
def randomeventajax(id):
    event = Event.query.get_or_404(id)
    random_opinion = [Post.query.filter_by(event=event).order_by(func.rand()).first()]

    opinions = [(r.body, r.prompt.text) for r in random_opinion]
    return jsonify(opinions=opinions)

@poll.route('/randomtodayajax/')
def randomtodayajax():
    event = Event.get_current()
    random_opinion = [Post.query.filter_by(event=event).order_by(func.rand()).first()]

    opinions = [(r.body, r.prompt.text) for r in random_opinion]
    return jsonify(opinions=opinions)

@poll.route('/random/event/<int:id>')
def randomeventpoll(id):
    event = Event.query.get_or_404(id)
    random_opinion = Post.query.filter_by(event=event).order_by(func.rand()).first()

    request.randomtype = 'individual'

    return render_template('poll/random.html', post=random_opinion)

@poll.route('/random/today')
def randomtoday():
    event = Event.get_current()
    posts = Post.query.filter_by(event=event).order_by(func.rand()).first()

    request.randomtype = 'individual-today'

    return render_template('poll/random.html', post=posts)

@poll.route('/all')
def opinions():
    posts = Post.query.order_by(Post.id.desc()).all()

    return render_template('poll/plain_posts.html', posts=posts)

@poll.route('/today/<username>')
def todays_opinions(username):
    user = User.query.filter_by(username=username).first()
    event = Event.get_current(user)
    posts = Post.query.filter_by(event=event).order_by(func.rand()).all()

    return render_template('poll/plain_posts.html', posts=posts)
