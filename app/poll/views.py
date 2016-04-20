from flask import Flask, render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import poll
from .forms import PostForm, DrawForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Event, Prompt, PromptEvent
from ..decorators import admin_required, permission_required
from sqlalchemy.sql.expression import func, select
import base64
import os, json

@poll.route('/', methods=['GET', 'POST'])
def home():
    user = User.query.filter_by(username="mediumra_re").first()
    event = Event.query.filter_by(name="The General Opinions").first()
    form = PostForm(user=user)
    print form.prompts.data
    if form.validate_on_submit():

        post = Post(user=user)
        post.name = form.name.data

        post.age = form.age.data
        post.gender = form.gender.data
        post.body = form.body.data
        post.passion = form.passion.data
        post.event = event
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser
        post.prompt = Prompt.query.filter_by(id=form.prompts.data).first()
        post.user = user
        db.session.add(post)
        db.session.commit()
        flash('Submitted')
        return redirect(url_for('poll.home'))
        return redirect(url_for('poll.cheers_user', user=user.username, event=post.event.name_slug))

    return render_template('poll/poll.html', form=form, user=user, event=event, draw=False, return_to="/poll")

@poll.route('/draw', methods=['GET', 'POST'])
def draw():
    user = User.query.filter_by(username="mediumra_re").first()
    event = Event.query.filter_by(name="The General Opinions").first()
    form = PostForm(user=user)
    print form.prompts.data
    if form.validate_on_submit():

        post = Post(user=user)
        post.name = form.name.data

        post.age = form.age.data
        post.gender = form.gender.data
        post.body = form.body.data
        post.passion = form.passion.data
        post.event = event
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser
        post.prompt = Prompt.query.filter_by(id=form.prompts.data).first()
        post.user = user

        if form.image_uri.data > 0:
            post.image_uri = form.image_uri.data
            details_concat = ('-').join([str(form.age.data), form.gender.data, form.passion.data])
            details_space = details_concat.split(' ')
            deets = ('-').join(details_space).lower()
            image_file = post.event.name_slug + deets
            post.image_file = image_file
            data_full = form.image_uri.data
            data = data_full.split(',')[1]
            fh = open("data/images/"+image_file+".png", "wb")
            fh.write(data.decode('base64'))
            fh.close()

        db.session.add(post)
        db.session.commit()
        flash('Submitted')
        return redirect(url_for('poll.home'))
        return redirect(url_for('poll.cheers_user', user=user.username, event=post.event.name_slug))

    return render_template('poll/poll.html', form=form, user=user, event=event, draw=True, return_to="/poll/draw")

@poll.route('/<username>/draw', methods=['GET', 'POST'])
def draw_user(username):
    user = User.query.filter_by(username=username).first()
    form = PostForm(user=user)
    event = Event.get_current(user=user)

    print form.prompts.data
    if form.validate_on_submit():

        post = Post(user=user)
        post.name = form.name.data

        post.age = form.age.data
        post.gender = form.gender.data
        post.body = form.body.data
        post.passion = form.passion.data
        post.event = event
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser
        post.prompt = Prompt.query.filter_by(id=form.prompts.data).first()
        post.user = user

        post.image_uri = form.image_uri.data
        details_concat = ('-').join([str(form.age.data), form.gender.data, form.passion.data])
        details_space = details_concat.split(' ')
        deets = ('-').join(details_space).lower()
        image_file = post.event.name_slug + deets
	app = Flask(__name__)
	APP_ROOT = os.path.dirname(os.path.abspath(__file__))
	UPLOAD_FOLDER = os.path.join(APP_ROOT, '/var/www/html/newlynpolls/app/static/data/images')
	app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        post.image_file = image_file
        data_full = form.image_uri.data
        try:
            data = data_full.split(',')[1]
        except:
            pass
        else:
            fh = open((os.path.join(app.config['UPLOAD_FOLDER'], image_file+'.png')), "wb")
            fh.write(data.decode('base64'))
            fh.close()
        db.session.add(post)
        db.session.commit()
        flash('Submitted')
        return redirect(url_for('poll.cheers_user', user=user.username, event=post.event.name_slug))

    return render_template('poll/poll.html', form=form, user=user, event=event, draw=True, return_to="/poll/" + user.username + "/draw")

@poll.route('/<username>', methods=['GET', 'POST'])
def vote(username):
    user = User.query.filter_by(username=username).first()
    form = PostForm(user=user)
    event = Event.get_current(user=user)
    print form.prompts.data
    if form.validate_on_submit():

        post = Post(user=user)
        post.name = form.name.data

        post.age = form.age.data
        post.gender = form.gender.data
        post.body = form.body.data
        post.passion = form.passion.data
        post.event = event
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser
        print "Prompt", Prompt.query.filter_by(id=form.prompt.data).first()
        post.prompt = Prompt.query.filter_by(id=form.prompts.data).first()
        post.user = user

        db.session.add(post)
        db.session.commit()
        flash('Submitted')
        return redirect(url_for('poll.cheers_user', user=user.username, event=post.event.name_slug))

    return render_template('poll/poll.html', form=form, user=user, event=event, draw=False, return_to="/poll/" + user.username)

@poll.route('/cheers/<user>/<event>')
def cheers_user(user, event):
    user = User.query.filter_by(username=user).first()
    event = Event.get_current(user)
    posts = Post.query.filter_by(event=event).order_by(Post.id.desc()).all()

    if request.referrer != None:
        return_to = request.referrer
    else:
        return_to = request.environ['PATH_INFO']
    try:
        if request.cookies['presentation_mode']:
            return render_template('poll/thanks.html', type="presentation", posts=posts, return_to=return_to)
    except KeyError:
        return render_template('poll/thanks.html', type="basic", posts=posts, return_to=return_to)

@poll.route('/cheers/<user>/<event>/archive')
def cheers_user_archive(user, event):
    user = User.query.filter_by(username=user).first()
    event = Event.query.filter_by(name_slug=event).first()
    posts = Post.query.filter_by(event=event).order_by(Post.id.desc()).all()

    try:
        if request.cookies['presentation_mode']:
            return render_template('poll/thanks.html', type="presentation", posts=posts)
    except KeyError:
        return render_template('poll/thanks.html', type="basic", posts=posts)

    
@poll.route('/cheers')
def cheers():
    try:
        if request.cookies['presentation_mode']:
            return render_template('poll/thanks.html', type="presentation")
    except KeyError:
        return render_template('poll/thanks.html', type="basic")

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

@poll.route('/randomtodayajax/<username>')
def randomtodayajax(username):
    user = User.query.filter_by(username=username).first()
    event = Event.get_current(user)
    random_opinion = [Post.query.filter_by(event=event).order_by(func.rand()).first()]

    opinions = [(r.body, r.prompt.text, r.image_file) for r in random_opinion]
    return jsonify(opinions=opinions)

@poll.route('/random/event/<int:id>')
def randomeventpoll(id):
    event = Event.query.get_or_404(id)
    random_opinion = Post.query.filter_by(event=event).order_by(func.rand()).first()

    request.randomtype = 'individual'

    return render_template('poll/random.html', post=random_opinion)

@poll.route('/random/today/<username>')
def randomtoday(username):
    user = User.query.filter_by(username=username).first()
    event = Event.get_current(user)
    posts = Post.query.filter_by(event=event).order_by(func.rand()).first()

    request.randomtype = 'individual-today'

    return render_template('poll/random.html', post=posts)

@poll.route('/all')
def opinions():
    posts = Post.query.order_by(Post.id.desc()).all()

    return render_template('poll/plain_posts.html', posts=posts)

@poll.route('/all/<username>')
def opinions_user(username):
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(user=user).order_by(Post.id.desc()).all()

    return render_template('poll/plain_posts.html', posts=posts)

@poll.route('/<username>/<event>')
def opinions_user_event(username, event):
    user = User.query.filter_by(username=username).first()
    event = Event.query.filter_by(user=user, name_slug=event).first()
    posts = Post.query.filter_by(event=event).order_by(Post.id.desc()).all()

    return render_template('poll/plain_posts.html', posts=posts)

# event = Event.query.get(11)
# print event.get_slug()

@poll.route('/today/<username>')
def todays_opinions(username):
    user = User.query.filter_by(username=username).first()
    event = Event.get_current(user)
    posts = Post.query.filter_by(event=event).order_by(Post.id.desc()).all()

    return render_template('poll/plain_posts.html', posts=posts)

@poll.route('/ajax/vote', methods=['POST'])
def vote_ajax():
    value = request.form['value']
    post_id = request.form['post_id']

    post = Post.query.get_or_404(post_id)
    yay = post.yay
    nay = post.nay

    if value == 'yay':
        post.yay = yay + 1
    else:
        post.nay = nay + 1

    db.session.add(post)
    db.session.commit()

    return json.dumps({'status':'OK','yay':post.yay,'nay':post.nay, 'id':post.id});

