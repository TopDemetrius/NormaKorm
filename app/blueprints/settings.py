from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db
from app.decorators import login_required

bp = Blueprint('settings', __name__)


@bp.route('/settings')
@login_required
def settings_page():
    user = db.get_user(session['user_id'])
    return render_template('settings.html', user=user)


@bp.route('/api/settings/profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    update_fields = {}
    for f in ['name', 'email', 'position']:
        if f in data:
            update_fields[f] = data[f]
    if update_fields:
        db.update_user(session['user_id'], **update_fields)
        # Оновити сесію якщо змінилось ім'я
        if 'name' in update_fields:
            session['user_name'] = update_fields['name']
            session['user_initials'] = ''.join(
                p[0].upper() for p in update_fields['name'].split()[:2]
            )
    return jsonify({'success': True})


@bp.route('/api/settings/password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not all([current_password, new_password, confirm_password]):
        return jsonify({'error': 'Заповніть усі поля'}), 400
    if len(new_password) < 6:
        return jsonify({'error': 'Новий пароль повинен містити щонайменше 6 символів'}), 400
    if new_password != confirm_password:
        return jsonify({'error': 'Паролі не співпадають'}), 400

    user = db.get_user(session['user_id'])
    if not user or not check_password_hash(user['password_hash'], current_password):
        return jsonify({'error': 'Невірний поточний пароль'}), 400

    db.update_user(session['user_id'], password_hash=generate_password_hash(new_password))
    return jsonify({'success': True})
