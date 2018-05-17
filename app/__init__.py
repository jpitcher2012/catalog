import httplib2
import json
import os
import random
import requests
import string

from flask import Flask, flash, jsonify, redirect, request
from flask import make_response, render_template, url_for
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.utils import secure_filename

from models import Base, Breed, Group, User

CLIENT_ID = json.loads(open('/var/www/catalog/app/client_secrets.json',
                            'r').read())['web']['client_id']

# Connect to database and create database session
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
app.config['UPLOADS'] = '/static'

# Show all groups
@app.route('/')
@app.route('/groups/')
def showGroups():
    groups = session.query(Group)
    return render_template('groups.html', groups=groups)


# JSON endpoint for showing all groups
@app.route('/groups/JSON/')
def showGroupsJSON():
    groups = session.query(Group)
    return jsonify(groups=[g.serialize for g in groups])


# Show all breeds for a given group
@app.route('/groups/<int:group_id>/')
@app.route('/groups/<int:group_id>/breeds/')
def showGroupBreeds(group_id):
    if 'user_id' in login_session:
        user = login_session['user_id']
    else:
        user = ''
    group = session.query(Group).filter_by(id=group_id).one()
    breeds = session.query(Breed).filter_by(group_id=group_id)
    breeds = breeds.order_by(asc(Breed.name)).all()
    return render_template('breeds.html',
                           breeds=breeds, group=group, user_id=user)


# JSON endpoint for showing all breeds for a given group
@app.route('/groups/<int:group_id>/breeds/JSON/')
def showGoupBreedsJSON(group_id):
    breeds = session.query(Breed).filter_by(group_id=group_id).all()
    return jsonify(Breeds=[b.serialize for b in breeds])


# Show info for a specific breed
@app.route('/groups/<int:group_id>/breeds/<int:breed_id>/')
def showBreedInfo(group_id, breed_id):
    if 'user_id' in login_session:
        user = login_session['user_id']
    else:
        user = ''
    group = session.query(Group).filter_by(id=group_id).one()
    breed = session.query(Breed).filter_by(id=breed_id).one()
    return render_template('breedInfo.html',
                           breed=breed, group=group, user_id=user)


# JSON endpoint for info on a specific breed
@app.route('/groups/<int:group_id>/breeds/<int:breed_id>/JSON/')
def showBreedInfoJSON(group_id, breed_id):
    breed = session.query(Breed).filter_by(id=breed_id).one()
    return jsonify(breed.serialize)


# Add a new breed to a group
@app.route('/groups/<int:group_id>/breeds/add/', methods=['GET', 'POST'])
def addBreed(group_id):
    if 'username' not in login_session:
        return redirect('/showLogin')
    group = session.query(Group).filter_by(id=group_id).one()
    if request.method == 'POST':
        newBreed = Breed(name=request.form['name'],
                         description=request.form['description'],
                         height=request.form['height'],
                         weight=request.form['weight'],
                         group_id=group_id,
                         user_id=login_session['user_id'])
        session.add(newBreed)
        session.commit()

        if 'picture' in request.files:
            picture = request.files['picture']
            if picture.filename != '':
                filename = 'breed%s.jpg' % newBreed.id
                picture.save(os.path.join(app.config['UPLOADS'], filename))
                newBreed.picture = filename
                session.add(newBreed)
                session.commit()

        flash('New Breed %s Successfully Created' % newBreed.name)
        return redirect(url_for('showBreedInfo',
                                breed_id=newBreed.id, group_id=group.id))
    else:
        return render_template('addBreed.html', group=group)


# Edit a breed
@app.route('/groups/<int:group_id>/breeds/<int:breed_id>/edit/',
           methods=['GET', 'POST'])
def editBreed(group_id, breed_id):
    if 'username' not in login_session:
        return redirect('/showLogin')
    breed = session.query(Breed).filter_by(id=breed_id).one()
    if login_session['user_id'] != breed.user_id:
        flash('Access Denied')
        return redirect(url_for('showGroupBreeds', group_id=group_id))
    else:
        group = session.query(Group).filter_by(id=group_id).one()
        if request.method == 'POST':
            breed.name = request.form['name']
            breed.description = request.form['description']
            breed.height = request.form['height']
            breed.weight = request.form['weight']

            if 'picture' in request.files:
                picture = request.files['picture']
                if picture.filename != '':
                    filename = 'breed%s.jpg' % breed.id
                    picture.save(os.path.join(app.config['UPLOADS'], filename))
                    breed.picture = filename

            session.add(breed)
            session.commit()
            flash('Breed Successfully Edited')
            return redirect(url_for('showBreedInfo',
                                    breed_id=breed.id, group_id=group_id))
        else:
            return render_template('editBreed.html', breed=breed, group=group)


# Delete a breed
@app.route('/groups/<int:group_id>/breeds/<int:breed_id>/delete/',
           methods=['GET', 'POST'])
def deleteBreed(group_id, breed_id):
    if 'username' not in login_session:
        return redirect('/showLogin')
    breed = session.query(Breed).filter_by(id=breed_id).one()
    if login_session['user_id'] != breed.user_id:
        flash('Access Denied')
        return redirect(url_for('showGroupBreeds', group_id=group_id))
    else:
        group = session.query(Group).filter_by(id=group_id).one()
        if request.method == 'POST':
            if breed.picture:
                os.remove(os.path.join(app.config['UPLOADS'], breed.picture))

            session.delete(breed)
            session.commit()
            flash('Breed Successfully Deleted')
            return redirect(url_for('showGroupBreeds', group_id=group_id))
        else:
            return render_template('deleteBreed.html',
                                   breed=breed, group=group)


# Display login page
@app.route('/showLogin/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Log in
@app.route('/login', methods=['POST'])
def login():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    provider = request.args.get('provider')

    if provider == 'google':
        gconnect(request.data)

    elif provider == 'facebook':
        fbconnect(request.data)

    # See if user exists; if not, create a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Display the successful login message
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("You are now logged in as %s" % login_session['username'])
    return output


# Log in (Google)
def gconnect(auth_code):
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/app/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']


# Log in (Facebook)
def fbconnect(access_token):
    # Exchange client token for long-lived server-side token
    app_id = json.loads(open('/var/www/catalog/app/fb_client_secrets.json',
                             'r').read())['web']['app_id']
    app_secret = json.loads(open('/var/www/catalog/app/fb_client_secrets.json',
                                 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s' % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.8/me?access_token=%s'
           '&fields=name,id,email' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]


# Log out
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']

        flash("You have successfully been logged out.")
        return redirect(url_for('showGroups'))
    else:
        flash("You are not logged in.")
        return redirect(url_for('showGroups'))


# Log out (Google)
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('User not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        response = make_response(json.dumps('Failed to revoke token.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Log out (Facebook)
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]


# Create a new user in the database
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get a user from the database by id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Get a user from the database by email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.run()
