from flask import Blueprint, render_template, jsonify
from app.models import db
from app.decorators import login_required

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    rations = db.get_rations(limit=10)
    # Аналіз відхилень
    deviations = []
    for r in rations:
        analysis = db.analyze_ration(r['id'])
        if analysis and analysis['overall_status'] != 'normal':
            # Знайти конкретні порушення
            violations = [a for a in analysis['analysis'] if a['status'] != 'normal']
            for v in violations[:1]:  # тільки перше порушення для кожного раціону
                deviation_pct = 0
                if v['min_value'] and v['actual_value'] < v['min_value']:
                    deviation_pct = round((v['min_value'] - v['actual_value']) / v['min_value'] * 100)
                    direction = 'нижче'
                elif v['max_value'] and v['actual_value'] > v['max_value']:
                    deviation_pct = round((v['actual_value'] - v['max_value']) / v['max_value'] * 100)
                    direction = 'вище'
                else:
                    direction = ''
                deviations.append({
                    'ration_name': r['name'],
                    'ration_id': r['id'],
                    'nutrient': v['nutrient_name'],
                    'deviation_pct': deviation_pct,
                    'direction': direction,
                    'status': v['status']
                })

    return render_template('index.html',
                           rations=rations,
                           deviations=deviations)


@bp.route('/api/dashboard-stats')
def dashboard_stats():
    rations = db.get_rations()
    return jsonify({
        'total_rations': len(rations),
        'normal': sum(1 for r in rations if db.analyze_ration(r['id']) and db.analyze_ration(r['id'])['overall_status'] == 'normal'),
    })
