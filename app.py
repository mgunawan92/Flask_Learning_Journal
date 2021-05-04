# import corresponding flask features
from flask import (Flask, render_template, flash, redirect, url_for, g, abort)

# import flask login features
from flask_login import (LoginManager, login_user, logout_user, current_user, login_required)

#import password hash from bcrypt
from flask_bcrypt import check_password_hash

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'asildhguioawnflasnvklvasndfuaklsjnf'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# view for looking up a user id in the database
@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
	   
    # catch any user id mismatches (user does not exist in the system
    except modeld.DoesNotExist:
        return None


# view for connecting to the database
@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


# close database connection
@app.after_request
def after_request(response):
    g.db.close()
    return response


# index view
@app.route('/', methods=('POST', 'GET'))
def index():
    # view all entries in database, from newest to oldest
    entries = models.Entries.select().order_by(models.Entries.date.desc())
    
    return render_template('index.html', entries=entries)


# login view; will run user's entered credentials from LoginForm against current users. If provided email data matches pre-existing user email, login_user
@app.route('/login', methods=('POST', 'GET'))
def login():
    
    form = forms.LoginForm()
    
    if form.validate_on_submit():

        try:
            # match entered email in form to current User emails
            user = models.User.get(models.User.email == form.email.data)
    
        except models.DoesNotExist:
        # display error if no match was found
          flash("Credentials dont match", "error")
    
        else:
            # if match was found, run password check, and login_user if success
            if check_password_hash(user.password, form.password.data):
    
                login_user(user)
    
                flash("You have logged in", "success")
    
                return redirect(url_for('index'))
    
            else:
                flash("Credentials do not match any profile in the system", "error")
        
    return render_template('login.html', form=form)


# logout view, logout_user, then return to index
@app.route('/logout')
@login_required
def logout():
    
    logout_user()
    flash("You have logged out", "success")
    return redirect(url_for('index'))


# view for registering new user for learning journal
@app.route('/register', methods=('POST', 'GET'))
def register():
    
    form = forms.RegistrationForm()
    
    if form.validate_on_submit():
        models.User.create_user(username = form.username.data, email = form.email.data, password = form.password.data)
        
        flash("You have registered successfully", "success")
        
        return redirect(url_for('index'))
    
    return render_template('register.html', form=form)


# view for adding new journal entry, return to index once journal entry has been added
@app.route("/entries/new", methods=('POST', 'GET'))
@login_required
def new():
    
    form = forms.NewEntryForm()
    
    if form.validate_on_submit():
        models.Entries.create_entry(
            username = g.user._get_current_object(), 
            title = form.title.data.strip(), 
            date = form.date.data, 
            timeSpent = form.timeSpent.data, 
            whatILearned = form.whatILearned.data, 
            ResourcesToRemember = form.ResourcesToRemember.data,
        )
        
        flash("Journal entry added", "success")
        
        return redirect(url_for('index'))

    return render_template('new.html', form=form)



# view for viewing details of journal entry
@app.route("/entries")
@app.route("/entries/")
@app.route("/entries/<int:id>")
@app.route("/entries/<int:id>/")
def detail(id=None):
    
    if id:
        entry = models.Entries.select().where(models.Entries.id == id)
        if entry.count() == 0:
            abort(404)
        return render_template('detail.html', entry=entry)
    else:
        entries = models.Entries.select().order_by(models.Entries.date.desc())
        return render_template('index.html', entries=entries)



# view for editing specific entry
@app.route("/entries/<int:id>/edit", methods=('POST', 'GET'))
@login_required
def edit(id):
    
    form = forms.NewEntryForm()
    
    entry = models.Entries.select().where(models.Entries.id == id)
    
    if form.validate_on_submit():
        try:
            replacemententry = models.Entries.get(models.Entries.id == id)
            replacemententry.title = form.title.data.strip()
            replacemententry.date = form.date.data
            replacemententry.timeSpent = form.timeSpent.data
            replacemententry.whatILearned = form.whatILearned.data
            replacemententry.ResourcesToRemember = form.ResourcesToRemember.data
            replacemententry.save()
            
            flash("Journal Entry Updated", "success")
            return redirect(url_for('index'))
        except models.IntegrityError:
            flash("Journal Entry was Not Updated. Please try again.", "error")
            
    return render_template('edit.html', form=form, entry=entry)
            
            
# view for deleting specific journal entry
@app.route("/entries/<id>/delete")
@login_required
def delete(id):
    try:
        journal_entry = models.Entries.select().where(models.Entries.id == id).get()
    except models.DoesNotExist:
        abort(404)
    else:
        journal_entry.delete_instance()
        flash("Journal Entry has been Deleted", "success")
        
    return redirect(url_for('index'))


# view for handling all 404 errors
@app.errorhandler(404)
def abort_error(error):
    return render_template('404.html', error=error), 404

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username = 'testemail',
            email = 'testemail@test.com',
            password='testpassword',
            admin = True
        )
    except ValueError:
        pass
        
    app.run(debug=DEBUG, port=PORT, host=HOST)
