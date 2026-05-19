from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            error = 'Заповніть усі поля'
        else:
            user = db.get_user_by_username(username)
            if user is None:
                error = 'Невірний логін або пароль'
            elif not check_password_hash(user['password_hash'], password):
                error = 'Невірний логін або пароль'
            else:
                session.clear()
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_initials'] = ''.join(
                    p[0].upper() for p in user['name'].split()[:2]
                ) if user['name'] else 'U'
                session['user_position'] = user['position'] or ''
                return redirect(url_for('main.index'))

    return render_template('login.html', error=error)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        position = request.form.get('position', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')

        if not all([name, username, password, password2]):
            error = 'Заповніть усі обов\'язкові поля'
        elif len(password) < 6:
            error = 'Пароль повинен містити щонайменше 6 символів'
        elif password != password2:
            error = 'Паролі не співпадають'
        elif db.get_user_by_username(username):
            error = f'Логін «{username}» вже зайнятий'
        else:
            password_hash = generate_password_hash(password)
            user_id = db.add_user(username, password_hash, name, email, position)
            session.clear()
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_initials'] = ''.join(
                p[0].upper() for p in name.split()[:2]
            ) if name else 'U'
            session['user_position'] = position
            return redirect(url_for('main.index'))

    return render_template('register.html', error=error)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
