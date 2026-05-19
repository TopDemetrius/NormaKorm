from flask import Blueprint, render_template, request, jsonify
from app.models import db
from app.decorators import login_required

bp = Blueprint('prices', __name__)


@bp.route('/prices')
@login_required
def prices_page():
    return render_template('prices.html')


@bp.route('/api/prices')
def get_prices():
    prices = db.get_prices_with_history()
    result = []
    for p in prices:
        prev = p['prev_price']
        curr = p['current_price']
        change_pct = 0
        if prev and prev > 0:
            change_pct = round((curr - prev) / prev * 100, 1)
        result.append({
            'id': p['id'],
            'name': p['name'],
            'current_price': curr,
            'prev_price': prev,
            'change_pct': change_pct,
            'last_updated': p['last_updated']
        })
    return jsonify(result)


@bp.route('/api/prices/update', methods=['POST'])
def update_prices():
    """Оновити ціни — записувати в історію ЛИШЕ якщо ціна змінилась"""
    data = request.json  # [{ingredient_id, price}, ...]
    prices = data.get('prices', [])
    updated = 0
    for p in prices:
        ing_id = p['ingredient_id']
        new_price = p['price']
        # Отримати поточну ціну інгредієнта
        ing = db.get_ingredient(ing_id)
        if ing:
            old_price = ing['price'] or 0
            # Записувати в історію тільки якщо ціна реально змінилась
            if abs(new_price - old_price) > 0.001:
                db.add_price_record(ing_id, new_price)
                updated += 1
    return jsonify({'success': True, 'updated': updated})
