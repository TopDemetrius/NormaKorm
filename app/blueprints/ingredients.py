from flask import Blueprint, render_template, request, jsonify
from app.models import db
from app.decorators import login_required

bp = Blueprint('ingredients', __name__)


@bp.route('/ingredients')
@login_required
def ingredients_page():
    categories = db.get_ingredient_categories()
    return render_template('ingredients.html', categories=categories)


@bp.route('/api/ingredients')
def get_ingredients():
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    ingredients = db.get_ingredients(category_id=category_id, search=search if search else None)
    result = []
    for ing in ingredients:
        nutrients = db.get_ingredient_nutrients(ing['id'])
        nutrient_map = {}
        for n in nutrients:
            nutrient_map[n['nutrient_name']] = n['value']
        result.append({
            'id': ing['id'],
            'name': ing['name'],
            'category_id': ing['category_id'],
            'category_name': ing['category_name'],
            'category_color': ing['category_color'],
            'moisture': ing['moisture'],
            'price': ing['price'],
            'max_inclusion_pct': ing['max_inclusion_pct'],
            'nutrients': nutrient_map
        })
    return jsonify(result)


@bp.route('/api/ingredients', methods=['POST'])
def add_ingredient():
    data = request.json
    ing_id = db.add_ingredient(
        category_id=data['category_id'],
        name=data['name'],
        moisture=data.get('moisture', 0),
        price=data.get('price', 0),
        max_inclusion_pct=data.get('max_inclusion_pct', 100)
    )
    # Зберегти поживний склад
    if 'nutrients' in data:
        db.save_ingredient_nutrients_batch(ing_id, data['nutrients'])
    # Записати ціну в історію
    if data.get('price', 0) > 0:
        db.add_price_record(ing_id, data['price'])
    return jsonify({'success': True, 'id': ing_id})


@bp.route('/api/ingredients/<int:ing_id>', methods=['PUT'])
def update_ingredient(ing_id):
    data = request.json
    update_fields = {}
    for field in ['name', 'category_id', 'moisture', 'price', 'max_inclusion_pct']:
        if field in data:
            update_fields[field] = data[field]
    if update_fields:
        db.update_ingredient(ing_id, **update_fields)
    # Оновити поживний склад
    if 'nutrients' in data:
        db.save_ingredient_nutrients_batch(ing_id, data['nutrients'])
    # Записати нову ціну
    if 'price' in data and data['price'] > 0:
        db.add_price_record(ing_id, data['price'])
    return jsonify({'success': True})


@bp.route('/api/ingredients/<int:ing_id>', methods=['DELETE'])
def delete_ingredient(ing_id):
    try:
        db.delete_ingredient(ing_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/api/nutrients')
def get_nutrients():
    category = request.args.get('category')
    nutrients = db.get_nutrients(category)
    return jsonify([dict(n) for n in nutrients])
