from flask import Blueprint, render_template, request, jsonify
from app.models import db
from app.optimizer import optimize_ration
from app.decorators import login_required

bp = Blueprint('optimization', __name__)


@bp.route('/optimization')
@login_required
def optimization_page():
    bird_types = db.get_bird_types()
    species_tree = []
    for bt in bird_types:
        age_groups = db.get_age_groups(bt['id'])
        species_tree.append({
            'id': bt['id'],
            'name': bt['name'],
            'age_groups': [dict(ag) for ag in age_groups]
        })
    ingredients = db.get_ingredients()
    categories = db.get_ingredient_categories()
    return render_template('optimization.html',
                           species_tree=species_tree,
                           all_ingredients=ingredients,
                           categories=categories)


@bp.route('/api/optimize', methods=['POST'])
def run_optimization():
    data = request.json
    age_group_id = data.get('age_group_id')
    ingredient_ids = data.get('ingredient_ids', [])
    mode = data.get('mode', 'min_cost')
    max_budget = data.get('max_budget')

    if not age_group_id or not ingredient_ids:
        return jsonify({
            'success': False,
            'status': 'Виберіть вікову групу та хоча б один інгредієнт'
        }), 400

    # Зібрати дані
    opt_data = db.get_optimization_data(age_group_id, ingredient_ids)

    # Запустити оптимізацію
    result = optimize_ration(
        ingredients=opt_data['ingredients'],
        norms=opt_data['norms'],
        mode=mode,
        max_budget=max_budget
    )

    return jsonify(result)
