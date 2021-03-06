# cd /c/Users/bpars/"fullstack-nanodegree-vm"/vagrant/catalog

# cd /c/Users/bpars/"fullstack-nanodegree-vm"/ubuntu

from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius:
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps
                                 ('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s' %
           login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        response = make_response(json.dumps('''Failed to revoke token for
                                            given user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# disconnect user
@app.route('/disconnect')
def disconnect():
    gdisconnect()
    flash("You have successfully been logged out.")
    return redirect(url_for('showCatalog'))


# Check login status
def login_required(f):
    @wraps (f)
    def decorated_function(*args, **kargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kargs)
    return decorated_function





# Show all catagories
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    catalog = session.query(Catalog).order_by(asc(Catalog.name))
    featured = session.query(Item).filter_by(featured='yes').all()
    if 'username' not in login_session:
        return render_template('catalog.html', catalog=catalog,
                               featured=featured)
    else:
        return render_template('cataloguser.html', catalog=catalog,
                               featured=featured)


# catalog JSON
@app.route('/JSON/')
@app.route('/catalog/JSON/')
def catalogJSON():
    catalog = session.query(Catalog).order_by(asc(Catalog.name))
    featured = session.query(Item).filter_by(featured='yes').all()
    return jsonify(showCatalog=[i.serialize for i in catalog])


# Items View
@app.route('/catalog/<path:catalog_name>/')
@app.route('/catalog/<path:catalog_name>/item/')
def showItems(catalog_name):
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalog_id = catalog.id
    items = session.query(Item).filter_by(
        catalog_id=catalog_id).all()
    if 'username' not in login_session:
        return render_template('items.html', items=items, catalog=catalog)
    else:
        return render_template('itemsuser.html', items=items, catalog=catalog)


# items JSON
@app.route('/catalog/<path:catalog_name>/JSON/')
@app.route('/catalog/<path:catalog_name>/item/JSON/')
def itemsJSON(catalog_name):
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalog_id = catalog.id
    items = session.query(Item).filter_by(
        catalog_id=catalog_id).all()
    return jsonify(showItems=[i.serialize for i in items])


# Check user status
def user_required(user_id):
        if user_id != login_session['user_id']:
            return False
        else:
            return True


# Items Detail View
@app.route('/catalog/<path:catalog_name>/<int:item_id>/')
@app.route('/catalog/<path:catalog_name>/<int:item_id>/item/')
def showDetails(catalog_name, item_id):
    items = session.query(Item).filter_by(id=item_id).all()
    item = session.query(Item).filter_by(id=item_id).one()
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalog_id = catalog.id
    if 'username' not in login_session:
        return render_template('details.html', items=items)
    if user_required(item.user_id) == False:
        return render_template('detailsuser.html', items=items, catalog=catalog,
                               catalog_id=catalog_id)
    else:
        return render_template('detailsowner.html',
                               items=items, catalog=catalog,
                               catalog_id=catalog_id)

# Items Featured View
@app.route('/catalog/<int:catalog_id>/<int:item_id>/')
@app.route('/catalog/<int:catalog_id>/<int:item_id>/item/')
def showFeatured(catalog_id, item_id):
    items = session.query(Item).filter_by(id=item_id).all()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    catalog_name = catalog.name
    return showDetails(catalog_name, item_id)


# items detail JSON
@app.route('/catalog/<path:catalog_name>/<int:item_id>/item/JSON/')
def detailsJSON(catalog_name, item_id):
    items = session.query(Item).filter_by(id=item_id).all()
    return jsonify(showDetails=[i.serialize for i in items])


# Create a new item
@app.route('/catalog/<path:catalog_name>/item/add/', methods=['GET', 'POST'])
@login_required
def newItem(catalog_name):
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalog_id = catalog.id
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       price=request.form['price'],
                       featured=request.form['featured'],
                       catalog_id=catalog_id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.name)
        session.commit()
        return redirect(url_for('showItems', catalog_name=catalog_name,
                        catalog=catalog))
    else:
        return render_template('itemadd.html', catalog=catalog,
                               catalog_name=catalog_name)


# Delete a item
@app.route('/catalog/<path:catalog_name>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteItem(catalog_name, item_id):
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    catalog = session.query(Catalog).filter_by(name=catalog_name).one()
    catalog_id = catalog.id
    if user_required(itemToDelete.user_id) == False:
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', catalog_name=catalog_name))
    else:
        return render_template('itemdelete.html', item=itemToDelete,
                               catalog_name=catalog_name)


# Edit an item
@app.route('/catalog/<path:catalog_name>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def editItem(catalog_name, item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if user_required(editedItem.user_id) == False:
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['image']:
            editedItem.image = request.form['image']
        if request.form['featured']:
            editedItem.featured = request.form['featured']
        return redirect(url_for('showItems', catalog_name=catalog_name))
    else:
        return render_template('itemedit.html', item=editedItem,
                               catalog_name=catalog_name)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
