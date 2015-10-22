from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm, EventForm, PromptForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Event, Prompt, PromptEvent
from ..decorators import admin_required, permission_required
from sqlalchemy.sql.expression import func, select


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():

        post = Post()
        post.name = form.name.data
        post.age = form.age.data
        post.gender = form.gender.data
        post.body = form.body.data
        post.passion = form.passion.data        
        post.user=current_user._get_current_object()
        post.event = Event.get_current()
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser

        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    

    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)

@main.route('/poll', methods=['GET', 'POST'])
def poll():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():

        post = Post()
        post.name = form.name.data
        post.age = form.age.data
        post.gender = form.gender.data
        post.body = form.body.data
        post.passion = form.passion.data        
        post.user=current_user._get_current_object()
        post.event = Event.get_current()
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser
        db.session.add(post)
        flash('Submitted')
        return redirect(url_for('.poll'))

    return render_template('poll.html', form=form)

@main.route('/random/all')
def randompoll():
    random_opinion = Post.query.order_by(func.rand()).first()

    return render_template('random.html', post=random_opinion)

@main.route('/random/event/<int:id>')
def randomeventpoll(id):
    event = Event.query.get_or_404(id)
    random_opinion = Post.query.filter_by(event=event).order_by(func.rand()).first()

    return render_template('random.html', post=random_opinion)

@main.route('/opinion/all')
def opinions():
    posts = Post.query.all()

    return render_template('posts.html', posts=posts)

@main.route('/opinion/<filt>/<value>')
def opinionfilter(filt, value):
    kwargs = {
        filt : value
    }
    posts = Post.query.filter_by(**kwargs).all()

    return render_template('posts.html', posts=posts)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)



@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.name = form.name.data
        post.age = form.age.data
        post.gender = form.gender.data
        post.passion = form.passion.data 
        post.platform = request.user_agent.platform
        post.browser = request.user_agent.browser       
        post.user=current_user._get_current_object()
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))

    form.name.data = post.name
    form.age.data = post.age
    form.gender.data = post.gender
    form.passion.data = post.passion
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/event/<int:id>', methods=['GET', 'POST'])
def event(id):
    event = Event.query.get_or_404(id)
    return render_template('event.html', event=event)

@main.route('/event/all')
def events():
    events = Event.query.all()

    return render_template('events.html', events=events)

@main.route('/event/add', methods=['GET', 'POST'])
def postevent():
    title = 'Add an Event'
    form = EventForm(user=user)
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():

        event = Event()
        event.location = form.location.data
        event.date = form.date.data
        event.user = current_user._get_current_object()

        for prompt in form.prompts.data:
            single = Prompt.query.get(prompt)
            last_event = Event.query.order_by(Event.id.desc()).first()
            event_id = (int(last_event.id))
            event_id_1 = event_id + 1
            check = PromptEvent.query.filter_by(prompt_id=single.id, event_id=event_id_1).first()

            if check != None:
                pass
            else:
                new = PromptEvent(prompt_id=single.id, event_id=event_id_1)

            db.session.add(new)


        current = form.current.data

        if current == True:
            event.set_current()

        db.session.add(event)
                   
        return redirect(url_for('.index'))
    
    events = Event.query.all()
    return render_template('post_event.html', form=form, events=events, title=title)

@main.route('/event/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def editevent(id):

    event = Event.query.get_or_404(id)

    if not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = EventForm(user=user)

    existing = PromptEvent.query.filter_by(event_id=event.id).all()

    for e in existing:
        db.session.delete(e)

    if form.validate_on_submit():
        event.location = form.location.data
        event.date = form.date.data
        event.user = current_user._get_current_object()

        for prompt in form.prompts.data:
            single = Prompt.query.get(prompt)

            check = PromptEvent.query.filter_by(prompt_id=single.id, event_id=event.id).first()

            if check != None:
                pass
            else:
                new = PromptEvent(prompt_id=single.id, event_id=event.id)
                db.session.add(new)

        
        
        current = form.current.data

        if current == True:
            event.set_current()

        db.session.add(event)

        flash('The event has been updated.')
        return redirect(url_for('.event', id=event.id))

    form.location.data = event.location
    form.date.data = event.date
    form.current.data = event.current

    choices = []

    for prompt in event.prompts:
        prompt_id = int(prompt.prompt_id)
        choices.append(prompt_id)

    print choices
    form.prompts.data = choices

    return render_template('edit_post.html', form=form)

@main.route('/prompt/add', methods=['GET', 'POST'])
def postprompt():
    title = 'Add a prompt'
    form = PromptForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():

        prompt = Prompt()
        prompt.text = form.text.data
        
    
        db.session.add(prompt)
        return redirect(url_for('.postprompt'))
    
    prompts = Prompt.query.all()
    return render_template('post_event.html', form=form, prompts=prompts)

@main.route('/prompt/edit/<int:id>', methods=['GET', 'POST'])
def editprompt(id):
    prompt = Prompt.query.get_or_404(id) 
    title = 'Edit prompt'
    form = PromptForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():       
        
        prompt.text = form.text.data
        
    
        db.session.add(prompt)
        return redirect(url_for('.prompt', id=prompt.id))
    
    form.text.data = prompt.text

    prompts = Prompt.query.all()
    return render_template('post_event.html', form=form, prompts=prompts)


@main.route('/prompt/<int:id>')
def prompt(id):
    prompt = Prompt.query.get_or_404(id)
    return render_template('prompt.html', prompt=prompt)

@main.route('/prompt/all')
def prompts():
    prompts = Prompt.query.all()
    return render_template('prompts.html', prompts=prompts)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
