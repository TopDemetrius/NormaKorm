from flask import Blueprint, render_template, request, jsonify
from app.models import db
from app.decorators import login_required

bp = Blueprint('rations', __name__)


@bp.route('/rations')
@login_required
def rations_page():
    bird_types = db.get_bird_types()
    species_tree = []
    for bt in bird_types:
        age_groups = db.get_age_groups(bt['id'])
        species_tree.append({
            'id': bt['id'],
            'name': bt['name'],
            'age_groups': [dict(ag) for ag in age_groups]
        })
    return render_template('rations.html', species_tree=species_tree)


@bp.route('/api/rations')
def get_rations():
    rations = db.get_rations()
    result = []
    for r in rations:
        analysis = db.analyze_ration(r['id'])
        result.append({
            'id': r['id'],
            'name': r['name'],
            'bird_type_name': r['bird_type_name'],
            'age_group_name': r['age_group_name'],
            'age_group_id': r['age_group_id'],
            'flock_size': r['flock_size'],
            'status': analysis['overall_status'] if analysis else 'draft',
            'total_cost': analysis['total_cost_per_kg'] if analysis else 0,
            'created_at': r['created_at'],
            'updated_at': r['updated_at']
        })
    return jsonify(result)


@bp.route('/api/rations/<int:rat_id>')
def get_ration(rat_id):
    r = db.get_ration(rat_id)
    if not r:
        return jsonify({'error': 'Not found'}), 404
    ration_ings = db.get_ration_ingredients(rat_id)
    analysis = db.analyze_ration(rat_id)
    return jsonify({
        'id': r['id'],
        'name': r['name'],
        'bird_type_name': r['bird_type_name'],
        'age_group_name': r['age_group_name'],
        'age_group_id': r['age_group_id'],
        'flock_size': r['flock_size'],
        'ingredients': [{
            'ingredient_id': ri['ingredient_id'],
            'ingredient_name': ri['ingredient_name'],
            'percentage': ri['percentage'],
            'price': ri['price'],
            'cost': round((ri['price'] or 0) * ri['percentage'] / 100, 4)
        } for ri in ration_ings],
        'analysis': analysis
    })


@bp.route('/api/rations', methods=['POST'])
def add_ration():
    data = request.json
    rat_id = db.add_ration(
        age_group_id=data['age_group_id'],
        name=data['name'],
        flock_size=data.get('flock_size', 1000)
    )
    if 'ingredients' in data:
        db.set_ration_ingredients(rat_id, data['ingredients'])
    return jsonify({'success': True, 'id': rat_id})


@bp.route('/api/rations/<int:rat_id>', methods=['PUT'])
def update_ration(rat_id):
    data = request.json
    update_fields = {}
    for field in ['name', 'age_group_id', 'flock_size']:
        if field in data:
            update_fields[field] = data[field]
    if update_fields:
        db.update_ration(rat_id, **update_fields)
    if 'ingredients' in data:
        db.set_ration_ingredients(rat_id, data['ingredients'])
    return jsonify({'success': True})


@bp.route('/api/rations/<int:rat_id>', methods=['DELETE'])
def delete_ration(rat_id):
    db.delete_ration(rat_id)
    return jsonify({'success': True})


@bp.route('/api/rations/<int:rat_id>/analyze')
def analyze_ration(rat_id):
    analysis = db.analyze_ration(rat_id)
    if not analysis:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(analysis)
