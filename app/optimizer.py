"""
Модуль оптимізації раціонів через лінійне програмування (PuLP).
Три режими: мінімальна вартість, максимальна поживність, збалансований.
"""
from pulp import (
    LpProblem, LpMinimize, LpMaximize, LpVariable,
    LpStatus, value, PULP_CBC_CMD
)


def optimize_ration(ingredients, norms, mode='min_cost', max_budget=None):
    """
    Оптимізація складу раціону.

    Args:
        ingredients: list of dicts:
            {id, name, price, max_inclusion_pct, nutrients: {nutrient_id: value}}
        norms: list of dicts:
            {nutrient_id, nutrient_name, unit, min_value, max_value}
        mode: 'min_cost' | 'max_nutrition' | 'balanced'
        max_budget: float | None — максимальна вартість 1 кг (₴/кг)

    Returns:
        dict: {success, status, ingredients: [{id, name, percentage, cost}],
               total_cost, nutrient_analysis: [{...}]}
    """

    if not ingredients:
        return {'success': False, 'status': 'Немає доступних інгредієнтів', 'ingredients': []}

    # --- Створення задачі ---
    if mode == 'max_nutrition':
        prob = LpProblem("RationOptimization", LpMaximize)
    else:
        prob = LpProblem("RationOptimization", LpMinimize)

    # Змінні: відсоток кожного інгредієнта (0..max_inclusion_pct)
    x = {}
    for ing in ingredients:
        x[ing['id']] = LpVariable(
            f"x_{ing['id']}",
            lowBound=0,
            upBound=ing.get('max_inclusion_pct', 100)
        )

    # --- Обмеження 1: Сума = 100% ---
    prob += sum(x[ing['id']] for ing in ingredients) == 100, "TotalPercent"

    # Виключаємо норми, для яких жоден інгредієнт не має даних
    # (обмеження виду 0 >= min_v завжди нерозв'язне)
    active_norms = [
        n for n in norms
        if any(ing['nutrients'].get(n['nutrient_id'], 0) > 0 for ing in ingredients)
    ]

    # --- Обмеження 2: Норми поживних речовин ---
    for norm in active_norms:
        nid = norm['nutrient_id']
        min_v = norm.get('min_value')
        max_v = norm.get('max_value')

        nutrient_expr = sum(
            ing['nutrients'].get(nid, 0) * x[ing['id']] / 100
            for ing in ingredients
        )

        if min_v is not None:
            prob += nutrient_expr >= min_v, f"MinNutrient_{nid}"
        if max_v is not None:
            prob += nutrient_expr <= max_v, f"MaxNutrient_{nid}"

    # --- Цільова функція ---
    cost_expr = sum(
        ing['price'] * x[ing['id']] / 100
        for ing in ingredients
    )

    if mode == 'min_cost':
        prob += cost_expr
    elif mode == 'max_nutrition':
        # Максимізуємо нормалізовану суму базових нутрієнтів (енергія, протеїн, жир)
        # Нормалізація по max_value дозволяє рівномірно враховувати всі три показники
        key_norms = [n for n in active_norms if n.get('category') == 'basic'] or active_norms
        key_norms = key_norms[:3]
        norm_maxes = {n['nutrient_id']: max(n.get('max_value') or 1, 0.001) for n in key_norms}
        nutrition_score = sum(
            (ing['nutrients'].get(nid, 0) / norm_maxes[nid]) * x[ing['id']] / 100
            for ing in ingredients
            for nid in norm_maxes
        )
        prob += nutrition_score
        if max_budget:
            prob += cost_expr <= max_budget, "BudgetLimit"
    elif mode == 'balanced':
        penalty = []
        for norm in active_norms:
            nid = norm['nutrient_id']
            min_v = norm.get('min_value')
            max_v = norm.get('max_value')
            if min_v is not None and max_v is not None:
                target = (min_v + max_v) / 2
                nutrient_val = sum(
                    ing['nutrients'].get(nid, 0) * x[ing['id']] / 100
                    for ing in ingredients
                )
                dev_pos = LpVariable(f"dev_pos_{nid}", lowBound=0)
                dev_neg = LpVariable(f"dev_neg_{nid}", lowBound=0)
                prob += nutrient_val - target == dev_pos - dev_neg, f"DevBalance_{nid}"
                penalty.append(dev_pos + dev_neg)

        if penalty:
            prob += 0.7 * cost_expr + 0.3 * sum(penalty)
        else:
            prob += cost_expr

        if max_budget:
            prob += cost_expr <= max_budget, "BudgetLimit"

    # --- Розв'язання ---
    solver = PULP_CBC_CMD(msg=0)
    prob.solve(solver)

    status = LpStatus[prob.status]

    if status != 'Optimal':
        # --- Спроба знайти найкраще можливе рішення без жорстких норм ---
        diagnostics = _diagnose_infeasibility(ingredients, active_norms)
        relaxed_result = _optimize_relaxed(ingredients, active_norms, mode, max_budget)

        if relaxed_result:
            relaxed_result['is_relaxed'] = True
            relaxed_result['diagnostics'] = diagnostics
            relaxed_result['status'] = (
                '⚠️ Точне рішення неможливе — показано найкращий наближений варіант'
            )
            return relaxed_result

        # Relaxed теж не вдався — якщо задано бюджет, пояснюємо чому
        if max_budget:
            min_possible = _estimate_min_cost(ingredients)
            diagnostics['recommendations'].insert(0, {
                'type': 'budget',
                'icon': '💰',
                'title': f'Бюджет {max_budget} ₴/кг недосяжний',
                'text': (
                    f'З обраних інгредієнтів мінімальна вартість суміші — '
                    f'орієнтовно {min_possible:.1f} ₴/кг. '
                    f'Збільшіть бюджет або встановіть "Без обмежень" (0).'
                )
            })

        return {
            'success': False,
            'status': f'Оптимальне рішення не знайдено ({status})',
            'ingredients': [],
            'diagnostics': diagnostics
        }

    # --- Результати ---
    result_ingredients = []
    total_cost = 0
    for ing in ingredients:
        pct = value(x[ing['id']])
        if pct and pct > 0.01:
            cost_per_unit = ing['price'] * pct / 100
            total_cost += cost_per_unit
            result_ingredients.append({
                'id': ing['id'],
                'name': ing['name'],
                'percentage': round(pct, 2),
                'cost': round(cost_per_unit, 4),
                'price': ing['price']
            })

    result_ingredients.sort(key=lambda r: r['percentage'], reverse=True)

    # --- Аналіз поживних речовин ---
    nutrient_analysis = []
    for norm in norms:
        nid = norm['nutrient_id']
        actual = sum(
            ing['nutrients'].get(nid, 0) * value(x[ing['id']]) / 100
            for ing in ingredients
            if value(x[ing['id']]) and value(x[ing['id']]) > 0
        )
        min_v = norm.get('min_value')
        max_v = norm.get('max_value')

        if min_v is not None and max_v is not None:
            if min_v <= actual <= max_v:
                st = 'normal'
            elif actual < min_v:
                dev = (min_v - actual) / min_v * 100 if min_v else 0
                st = 'warning' if dev <= 10 else 'violation'
            else:
                dev = (actual - max_v) / max_v * 100 if max_v else 0
                st = 'warning' if dev <= 10 else 'violation'
        else:
            st = 'normal'

        nutrient_analysis.append({
            'nutrient_id': nid,
            'nutrient_name': norm['nutrient_name'],
            'unit': norm['unit'],
            'min_value': min_v,
            'max_value': max_v,
            'actual_value': round(actual, 2),
            'status': st
        })

    return {
        'success': True,
        'status': 'Оптимальне рішення знайдено',
        'ingredients': result_ingredients,
        'total_cost': round(total_cost, 2),
        'nutrient_analysis': nutrient_analysis
    }


def _optimize_relaxed(ingredients, norms, mode='min_cost', max_budget=None):
    """
    Fallback: оптимізація без жорстких обмежень норм.
    Норми стають м'якими (штрафні змінні slack).
    Завжди повертає рішення, навіть якщо воно порушує деякі норми.
    """
    try:
        prob = LpProblem("RationRelaxed", LpMinimize)

        x = {}
        for ing in ingredients:
            x[ing['id']] = LpVariable(
                f"rx_{ing['id']}",
                lowBound=0,
                upBound=ing.get('max_inclusion_pct', 100)
            )

        # Обов'язкове: сума = 100%
        prob += sum(x[ing['id']] for ing in ingredients) == 100, "TotalPercent"

        # Вартість
        cost_expr = sum(
            ing['price'] * x[ing['id']] / 100
            for ing in ingredients
        )

        # М'які обмеження норм зі штрафними змінними
        slack_vars = []
        for norm in norms:
            nid = norm['nutrient_id']
            min_v = norm.get('min_value')
            max_v = norm.get('max_value')

            nutrient_expr = sum(
                ing['nutrients'].get(nid, 0) * x[ing['id']] / 100
                for ing in ingredients
            )

            if min_v is not None and min_v > 0:
                s_min = LpVariable(f"rs_min_{nid}", lowBound=0)
                prob += nutrient_expr + s_min >= min_v, f"SoftMin_{nid}"
                # Нормалізований штраф відносно цільового значення
                slack_vars.append(s_min * (100.0 / max(min_v, 0.001)))

            if max_v is not None and max_v > 0:
                s_max = LpVariable(f"rs_max_{nid}", lowBound=0)
                prob += nutrient_expr - s_max <= max_v, f"SoftMax_{nid}"
                slack_vars.append(s_max * (100.0 / max(max_v, 0.001)))

        penalty = sum(slack_vars) if slack_vars else 0

        if mode == 'min_cost':
            # Мінімізуємо вартість, норми вторинні
            prob += cost_expr + 0.001 * penalty
        elif mode == 'max_nutrition':
            # Максимізуємо нормалізовану поживність (нормуємо по max_value щоб
            # енергія не домінувала над протеїном)
            key_norms = [n for n in norms if n.get('category') == 'basic'] or norms
            key_norms = key_norms[:3]
            norm_maxes = {n['nutrient_id']: max(n.get('max_value') or 1, 0.001)
                          for n in key_norms}
            nutrition_score = sum(
                (ing['nutrients'].get(nid, 0) / norm_maxes[nid]) * x[ing['id']] / 100
                for ing in ingredients
                for nid in norm_maxes
            )
            prob += -nutrition_score + 0.001 * penalty
        else:
            # balanced: мінімізуємо порушення норм, вартість вторинна
            prob += 0.1 * cost_expr + 0.9 * penalty

        # Бюджет — жорстке обмеження навіть у relaxed-режимі.
        # Якщо він недосяжний з поточними інгредієнтами — повернемо None.
        if max_budget:
            prob += cost_expr <= max_budget, "HardBudget"

        solver = PULP_CBC_CMD(msg=0)
        prob.solve(solver)

        if LpStatus[prob.status] not in ('Optimal', 'Not Solved'):
            return None

        # Збираємо результати
        result_ingredients = []
        total_cost = 0
        for ing in ingredients:
            pct = value(x[ing['id']])
            if pct and pct > 0.01:
                cost_per_unit = ing['price'] * pct / 100
                total_cost += cost_per_unit
                result_ingredients.append({
                    'id': ing['id'],
                    'name': ing['name'],
                    'percentage': round(pct, 2),
                    'cost': round(cost_per_unit, 4),
                    'price': ing['price']
                })

        result_ingredients.sort(key=lambda r: r['percentage'], reverse=True)

        # Аналіз поживних речовин
        nutrient_analysis = []
        for norm in norms:
            nid = norm['nutrient_id']
            actual = sum(
                ing['nutrients'].get(nid, 0) * value(x[ing['id']]) / 100
                for ing in ingredients
                if value(x[ing['id']]) and value(x[ing['id']]) > 0
            )
            min_v = norm.get('min_value')
            max_v = norm.get('max_value')

            if min_v is not None and max_v is not None:
                if min_v <= actual <= max_v:
                    st = 'normal'
                elif actual < min_v:
                    dev = (min_v - actual) / min_v * 100 if min_v else 0
                    st = 'warning' if dev <= 10 else 'violation'
                else:
                    dev = (actual - max_v) / max_v * 100 if max_v else 0
                    st = 'warning' if dev <= 10 else 'violation'
            else:
                st = 'normal'

            nutrient_analysis.append({
                'nutrient_id': nid,
                'nutrient_name': norm['nutrient_name'],
                'unit': norm['unit'],
                'min_value': min_v,
                'max_value': max_v,
                'actual_value': round(actual, 2),
                'status': st
            })

        return {
            'success': True,
            'ingredients': result_ingredients,
            'total_cost': round(total_cost, 2),
            'nutrient_analysis': nutrient_analysis
        }

    except Exception:
        return None


def _estimate_min_cost(ingredients):
    """Оцінює мінімальну вартість 1 кг суміші з обраних інгредієнтів.
    Заповнює від найдешевшого, враховуючи max_inclusion_pct."""
    sorted_ings = sorted(ingredients, key=lambda i: i['price'])
    remaining = 100.0
    total = 0.0
    for ing in sorted_ings:
        pct = min(remaining, ing.get('max_inclusion_pct', 100))
        total += ing['price'] * pct / 100
        remaining -= pct
        if remaining <= 0:
            break
    return total


def _diagnose_infeasibility(ingredients, norms):

    """
    Аналізує причини нерозв'язності задачі оптимізації.
    Перевіряє кожну норму окремо: чи може набір інгредієнтів 
    теоретично її задовольнити.
    """
    problems = []       # конкретні проблемні обмеження
    recommendations = [] # рекомендації
    missing_data = []    # нутрієнти без даних в інгредієнтах

    for norm in norms:
        nid = norm['nutrient_id']
        n_name = norm['nutrient_name']
        unit = norm.get('unit', '')
        min_v = norm.get('min_value')
        max_v = norm.get('max_value')

        if min_v is None and max_v is None:
            continue

        # Знайти максимально та мінімально досяжне значення нутрієнта
        # при будь-якій комбінації інгредієнтів (сума = 100%)
        values = []
        has_data = False
        for ing in ingredients:
            val = ing['nutrients'].get(nid, 0)
            values.append(val)
            if val > 0:
                has_data = True

        if not values:
            continue

        # Теоретичний максимум: 100% найкращого інгредієнта
        # Теоретичний мінімум: 100% найгіршого інгредієнта
        # (з урахуванням max_inclusion_pct — складніше, але для діагностики достатньо)
        max_possible = max(values)
        min_possible = min(values)

        # Скільки інгредієнтів містять цей нутрієнт
        providers = [ing['name'] for ing in ingredients if ing['nutrients'].get(nid, 0) > 0]

        if not has_data:
            # Жоден інгредієнт не містить даних про цей нутрієнт
            if min_v is not None and min_v > 0:
                missing_data.append({
                    'nutrient': n_name,
                    'unit': unit,
                    'min_required': min_v,
                    'severity': 'critical'
                })
        else:
            # Перевіряємо чи можна досягти мінімуму
            if min_v is not None and max_possible < min_v:
                problems.append({
                    'nutrient': n_name,
                    'unit': unit,
                    'type': 'below_min',
                    'required_min': min_v,
                    'max_achievable': round(max_possible, 4),
                    'deficit': round(min_v - max_possible, 4),
                    'providers': providers
                })
            # Перевіряємо чи можна не перевищити максимум
            elif max_v is not None and min_possible > max_v:
                problems.append({
                    'nutrient': n_name,
                    'unit': unit,
                    'type': 'above_max',
                    'required_max': max_v,
                    'min_achievable': round(min_possible, 4),
                    'excess': round(min_possible - max_v, 4),
                    'providers': providers
                })

    # Генерація рекомендацій
    if missing_data:
        nutrient_names = ', '.join(m['nutrient'] for m in missing_data[:5])
        recommendations.append({
            'type': 'missing_data',
            'icon': '📊',
            'title': 'Відсутні дані поживності інгредієнтів',
            'text': f'Жоден обраний інгредієнт не має даних для: {nutrient_names}. '
                    f'Заповніть поживний склад інгредієнтів на вкладці "Інгредієнти" '
                    f'або видаліть ці норми на вкладці "Види та норми".'
        })

    if problems:
        for p in problems[:3]:
            if p['type'] == 'below_min':
                recommendations.append({
                    'type': 'constraint',
                    'icon': '⬇️',
                    'title': f'{p["nutrient"]}: неможливо досягти мінімуму',
                    'text': f'Потрібно мін. {p["required_min"]} {p["unit"]}, '
                            f'а максимально досяжне значення — {p["max_achievable"]} {p["unit"]}. '
                            f'Додайте інгредієнт з вищим вмістом цього показника '
                            f'або зменшіть мінімальну норму.'
                })
            elif p['type'] == 'above_max':
                recommendations.append({
                    'type': 'constraint',
                    'icon': '⬆️',
                    'title': f'{p["nutrient"]}: неможливо знизити нижче максимуму',
                    'text': f'Максимум норми {p["required_max"]} {p["unit"]}, '
                            f'а мінімально досяжне — {p["min_achievable"]} {p["unit"]}. '
                            f'Додайте інгредієнти з нижчим вмістом або збільшіть максимальну норму.'
                })

    if not recommendations:
        recommendations.append({
            'type': 'general',
            'icon': '🔧',
            'title': 'Конфлікт обмежень',
            'text': 'Кожне обмеження окремо може бути задоволене, але разом вони конфліктують. '
                    'Спробуйте: додати більше інгредієнтів, послабити норми (розширити діапазони), '
                    'або збільшити максимальний % включення інгредієнтів.'
        })

    return {
        'problems': problems,
        'missing_data': missing_data,
        'recommendations': recommendations,
        'total_norms': len(norms),
        'problem_count': len(problems) + len(missing_data)
    }
