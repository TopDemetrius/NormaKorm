from flask import Blueprint, render_template, request, jsonify
from app.models import db
from app.decorators import login_required
import sqlite3

bp = Blueprint('species', __name__)


@bp.route('/species')
@login_required
def species_page():
    bird_types = db.get_bird_types()
    species_tree = []
    for bt in bird_types:
        age_groups = db.get_age_groups(bt['id'])
        species_tree.append({
            'id': bt['id'],
            'name': bt['name'],
            'age_groups': [dict(ag) for ag in age_groups]
        })
    return render_template('species.html', species_tree=species_tree)


@bp.route('/api/nutrients')
def get_nutrients():
    """Повертає список поживних речовин (опціонально за категорією)"""
    category = request.args.get('category', None)
    nutrients = db.get_nutrients(category)
    return jsonify([{
        'id': n['id'],
        'name': n['name'],
        'unit': n['unit'],
        'category': n['category'],
        'sort_order': n['sort_order']
    } for n in nutrients])


@bp.route('/api/species/norms/<int:age_group_id>')
def get_norms(age_group_id):
    category = request.args.get('category', None)
    # Повертаємо ВСІ поживні речовини категорії, з нормами якщо є
    nutrients = db.get_nutrients(category)
    norms = db.get_nutrient_norms(age_group_id, category)
    norms_map = {n['nutrient_id']: n for n in norms}

    result = []
    for nut in nutrients:
        norm = norms_map.get(nut['id'])
        result.append({
            'id': norm['id'] if norm else None,
            'nutrient_id': nut['id'],
            'nutrient_name': nut['name'],
            'unit': nut['unit'],
            'category': nut['category'],
            'min_value': norm['min_value'] if norm else None,
            'max_value': norm['max_value'] if norm else None
        })
    return jsonify(result)


@bp.route('/api/species/norms', methods=['POST'])
def save_norms():
    data = request.json
    age_group_id = data.get('age_group_id')
    norms = data.get('norms', [])
    if not age_group_id:
        return jsonify({'error': 'age_group_id required'}), 400
    db.save_norms_batch(age_group_id, norms)
    return jsonify({'success': True})


@bp.route('/api/species/norms/delete', methods=['POST'])
def delete_norm():
    """Видалити конкретну норму для вікової групи"""
    data = request.json
    age_group_id = data.get('age_group_id')
    nutrient_id = data.get('nutrient_id')
    if not age_group_id or not nutrient_id:
        return jsonify({'error': 'age_group_id and nutrient_id required'}), 400
    db.delete_nutrient_norm(age_group_id, nutrient_id)
    return jsonify({'success': True})


@bp.route('/api/species/add', methods=['POST'])
def add_species():
    data = request.json
    action = data.get('action')  # 'bird_type' or 'age_group'
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Назва не може бути порожньою'}), 400

    try:
        if action == 'bird_type':
            bt_id = db.add_bird_type(name, data.get('description', ''))
            return jsonify({'success': True, 'id': bt_id})
        elif action == 'age_group':
            bird_type_id = data.get('bird_type_id')
            if not bird_type_id:
                return jsonify({'error': 'Оберіть вид птиці'}), 400
            ag_id = db.add_age_group(bird_type_id, name, data.get('sort_order', 0))
            return jsonify({'success': True, 'id': ag_id})
        return jsonify({'error': 'Invalid action'}), 400
    except sqlite3.IntegrityError:
        return jsonify({'error': f'Запис з назвою "{name}" вже існує'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/api/species/bird-type/<int:bt_id>', methods=['DELETE'])
def delete_bird_type(bt_id):
    try:
        db.delete_bird_type(bt_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/api/species/age-group/<int:ag_id>', methods=['DELETE'])
def delete_age_group(ag_id):
    try:
        db.delete_age_group(ag_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
