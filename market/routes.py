from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, current_user


@app.route('/')
@app.route('/home')
def index_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
def market_page():
    # purchase fn
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == 'POST':
        purchased_item = request.form.get('purchased_item')
        fetch_item = Item.query.filter_by(name=purchased_item).first()
        if fetch_item:
            fetch_item.buy(current_user)
            flash(f"Congratulations! You bought {fetch_item.name} for ₱{fetch_item.price}", category='success')
            return redirect(url_for('market_page'))
        # Sell fn
        sold_item = request.form.get('sold_item')
        item_to_sell = Item.query.filter_by(name=sold_item).first()
        if item_to_sell:
            if current_user.can_sell(item_to_sell):
                item_to_sell.sell(current_user)
                flash(f"Congratulations! You sold {item_to_sell.name} for ₱{item_to_sell.price}", category='success')
                return redirect(url_for('market_page'))
            else:
                flash(f"Something went wrong with selling {item_to_sell.name}", category='danger')
        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items,
                               selling_form=selling_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        create_user = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password.data)
        db.session.add(create_user)
        db.session.commit()
        login_user(create_user)
        flash(f'Success! You are now Registered! as: {form.username.data}', category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error creating user {err_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Welcome back {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("Successfully log out!", category='warning')
    return redirect(url_for('index_page'))
