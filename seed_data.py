"""
Мінімальні seed-дані: лише індики (Племінний корм).
"""


def seed_all(db):
    """Наповнити БД мінімальними початковими даними"""

    # ===== Категорії інгредієнтів =====
    cat_grain   = db.add_ingredient_category('Зернові',    '#4CAF50')
    cat_protein = db.add_ingredient_category('Білкові',    '#2196F3')
    cat_mineral = db.add_ingredient_category('Мінеральні', '#9C27B0')
    cat_vitamin = db.add_ingredient_category('Вітамінні',  '#FF9800')
    cat_other   = db.add_ingredient_category('Інші',       '#607D8B')

    # ===== Вид птиці =====
    bt_turkey = db.add_bird_type('Індик', 'Індики')

    # ===== Вікова група =====
    ag_turkey = db.add_age_group(bt_turkey, 'Плем інне стадо', 1)

    # ===== Поживні речовини =====
    # Basic
    n_energy     = _add_n(db, 'Обмінна енергія',   'ккал/кг', 'basic',        1)
    n_protein    = _add_n(db, 'Сирий протеїн',      '%',       'basic',        2)
    n_fat        = _add_n(db, 'Сирий жир',          '%',       'basic',        3)
    n_fiber      = _add_n(db, 'Сира клітковина',    '%',       'basic',        4)
    n_calcium    = _add_n(db, 'Кальцій',            '%',       'basic',        5)
    n_phosphorus = _add_n(db, 'Фосфор',             '%',       'basic',        6)
    n_sodium     = _add_n(db, 'Натрій',             '%',       'basic',        7)
    n_chlorine   = _add_n(db, 'Хлор',              '%',       'basic',        8)
    n_linoleic   = _add_n(db, 'Лінолева кислота',   '%',       'basic',        9)

    # Per head
    n_feed_day    = _add_n(db, 'Корм',    'г/гол/день',    'per_head', 1)
    n_protein_day = _add_n(db, 'Протеїн', 'г/гол/день',    'per_head', 2)
    n_energy_day  = _add_n(db, 'Енергія', 'ккал/гол/день', 'per_head', 3)
    n_ca_day      = _add_n(db, 'Кальцій', 'г/гол/день',    'per_head', 4)
    n_p_day       = _add_n(db, 'Фосфор',  'г/гол/день',    'per_head', 5)

    # Amino acids
    n_lysine     = _add_n(db, 'Лізин',            '%', 'amino_acid', 1)
    n_methionine = _add_n(db, 'Метіонін',          '%', 'amino_acid', 2)
    n_met_cys    = _add_n(db, 'Метіонін+Цистин',   '%', 'amino_acid', 3)
    n_threonine  = _add_n(db, 'Треонін',           '%', 'amino_acid', 4)
    n_tryptophan = _add_n(db, 'Триптофан',         '%', 'amino_acid', 5)
    n_arginine   = _add_n(db, 'Аргінін',           '%', 'amino_acid', 6)

    # Microelements
    n_fe = _add_n(db, 'Залізо',   'мг/кг', 'microelement', 1)
    n_cu = _add_n(db, 'Мідь',     'мг/кг', 'microelement', 2)
    n_zn = _add_n(db, 'Цинк',     'мг/кг', 'microelement', 3)
    n_mn = _add_n(db, 'Марганець','мг/кг', 'microelement', 4)
    n_co = _add_n(db, 'Кобальт',  'мг/кг', 'microelement', 5)
    n_i  = _add_n(db, 'Йод',      'мг/кг', 'microelement', 6)
    n_se = _add_n(db, 'Селен',    'мг/кг', 'microelement', 7)

    # Vitamins
    n_va  = _add_n(db, 'Вітамін A',  'тис. МО/кг', 'vitamin', 1)
    n_vd3 = _add_n(db, 'Вітамін D3', 'тис. МО/кг', 'vitamin', 2)
    n_ve  = _add_n(db, 'Вітамін E',  'мг/кг',      'vitamin', 3)
    n_vk  = _add_n(db, 'Вітамін K',  'мг/кг',      'vitamin', 4)
    n_vb1 = _add_n(db, 'Вітамін B1', 'мг/кг',      'vitamin', 5)
    n_vb2 = _add_n(db, 'Вітамін B2', 'мг/кг',      'vitamin', 6)

    # ===== Інгредієнти зі скріншоту =====
    # Зернові
    ing_wheat   = db.add_ingredient(cat_grain,   'Пшениця',         13.5,  10.00, 60)
    ing_corn    = db.add_ingredient(cat_grain,   'Кукурудза',       14.0,  10.00, 70)

    # Білкові
    ing_soy     = db.add_ingredient(cat_protein, 'Соя',             12.0,  18.00, 30)
    ing_makuha  = db.add_ingredient(cat_protein, 'Макуха',          11.5,   9.50, 25)
    ing_kistna  = db.add_ingredient(cat_protein, 'Кістна',           8.0,  12.00,  7)

    # Мінеральні
    ing_salt    = db.add_ingredient(cat_mineral, 'Сіль',             0.5,  30.00,  0.5)
    ing_mel     = db.add_ingredient(cat_mineral, 'Мел - Вапняк',     1.0,   3.00, 10)

    # Вітамінні / інші
    ing_sorbent = db.add_ingredient(cat_other,   'Сорбент',          0.0,   3.00,  1)
    ing_vitamins= db.add_ingredient(cat_vitamin, 'Вітаміни',         0.0,  45.00,  0.5)
    ing_lysine_s= db.add_ingredient(cat_other,   'Сульфат лізина',   0.0, 115.00,  0.2)
    ing_met     = db.add_ingredient(cat_other,   'Метіонін',         0.0, 350.00,  0.1)
    ing_micro   = db.add_ingredient(cat_other,   'Мікроелементи',    0.0,  30.00,  0.1)
    ing_ve      = db.add_ingredient(cat_vitamin, 'Вітамін Е',        0.0,  80.00,  0.05)

    # ===== Поживний склад інгредієнтів =====
    # Пшениця
    _set_ing_nutrients(db, ing_wheat, [
        (n_energy, 3100), (n_protein, 11.5), (n_fat, 1.8),
        (n_fiber, 2.7), (n_calcium, 0.05), (n_phosphorus, 0.35),
        (n_sodium, 0.02), (n_lysine, 0.36), (n_methionine, 0.22),
        (n_met_cys, 0.43), (n_threonine, 0.32), (n_tryptophan, 0.13),
        (n_arginine, 0.55),
    ])

    # Кукурудза
    _set_ing_nutrients(db, ing_corn, [
        (n_energy, 3350), (n_protein, 8.5), (n_fat, 4.2),
        (n_fiber, 2.2), (n_calcium, 0.02), (n_phosphorus, 0.28),
        (n_sodium, 0.01), (n_lysine, 0.24), (n_methionine, 0.18),
        (n_met_cys, 0.36), (n_threonine, 0.29), (n_tryptophan, 0.06),
        (n_arginine, 0.38),
    ])

    # Соя
    _set_ing_nutrients(db, ing_soy, [
        (n_energy, 2230), (n_protein, 44.0), (n_fat, 2.5),
        (n_fiber, 6.0), (n_calcium, 0.25), (n_phosphorus, 0.65),
        (n_sodium, 0.01), (n_lysine, 2.80), (n_methionine, 0.62),
        (n_met_cys, 1.28), (n_threonine, 1.74), (n_tryptophan, 0.58),
        (n_arginine, 3.30),
    ])

    # Макуха (соняшниковий шрот)
    _set_ing_nutrients(db, ing_makuha, [
        (n_energy, 2100), (n_protein, 38.0), (n_fat, 1.5),
        (n_fiber, 12.0), (n_calcium, 0.35), (n_phosphorus, 0.95),
        (n_sodium, 0.02), (n_lysine, 1.40), (n_methionine, 0.80),
        (n_met_cys, 1.50), (n_threonine, 1.30), (n_tryptophan, 0.45),
        (n_arginine, 3.10),
    ])

    # Кістна (м'ясо-кісткове борошно)
    _set_ing_nutrients(db, ing_kistna, [
        (n_energy, 2400), (n_protein, 50.0), (n_fat, 12.0),
        (n_fiber, 2.0), (n_calcium, 11.00), (n_phosphorus, 5.50),
        (n_sodium, 0.60), (n_lysine, 2.50), (n_methionine, 0.70),
        (n_met_cys, 1.10), (n_threonine, 1.60),
    ])

    # Сіль
    _set_ing_nutrients(db, ing_salt, [
        (n_energy, 0), (n_protein, 0), (n_calcium, 0),
        (n_phosphorus, 0), (n_sodium, 39.0), (n_chlorine, 60.0),
    ])

    # Мел-Вапняк
    _set_ing_nutrients(db, ing_mel, [
        (n_energy, 0), (n_protein, 0), (n_fat, 0),
        (n_fiber, 0), (n_calcium, 38.00), (n_phosphorus, 0.02),
        (n_sodium, 0.05),
    ])

    # Сорбент (сорбент на основі бентоніту, нейтральний по нутрієнтах)
    _set_ing_nutrients(db, ing_sorbent, [
        (n_energy, 0), (n_protein, 0), (n_fat, 0), (n_fiber, 0),
        (n_calcium, 0.5), (n_phosphorus, 0), (n_sodium, 0),
    ])

    # Вітаміни (полівітамінний премікс для індиків)
    _set_ing_nutrients(db, ing_vitamins, [
        (n_va,  10000.0),   # тис. МО/кг → вказуємо як тис. МО/кг
        (n_vd3,  2000.0),
        (n_ve,   5000.0),
        (n_vk,    500.0),
        (n_vb1,   300.0),
        (n_vb2,   600.0),
    ])

    # Сульфат лізина (L-Lysine sulfate ~51% лізину)
    _set_ing_nutrients(db, ing_lysine_s, [
        (n_lysine, 51.0),
        (n_protein, 58.0),
    ])

    # Метіонін (DL-Methionine ~99% чистий)
    _set_ing_nutrients(db, ing_met, [
        (n_methionine, 99.0),
        (n_met_cys,    99.0),
        (n_protein,    58.0),
    ])

    # Мікроелементи (мінеральний премікс для індиків)
    _set_ing_nutrients(db, ing_micro, [
        (n_fe,  8000.0),
        (n_cu,   800.0),
        (n_zn,  8000.0),
        (n_mn,  9000.0),
        (n_co,    60.0),
        (n_i,    100.0),
        (n_se,    30.0),
    ])

    # Вітамін Е (50% концентрат токоферолу = 500 000 мг/кг)
    _set_ing_nutrients(db, ing_ve, [
        (n_ve, 500000.0),
    ])

    # Записати початкові ціни в історію
    for ing_id, price in [
        (ing_wheat,     10.00),
        (ing_corn,      10.00),
        (ing_soy,       18.00),
        (ing_makuha,     9.50),
        (ing_kistna,    12.00),
        (ing_salt,      30.00),
        (ing_mel,        3.00),
        (ing_sorbent,    3.00),
        (ing_vitamins,  45.00),
        (ing_lysine_s, 115.00),
        (ing_met,      350.00),
        (ing_micro,     30.00),
        (ing_ve,        80.00),
    ]:
        db.add_price_record(ing_id, price)

    # ===== Норми для племінного стада індиків =====
    _set_norms(db, ag_turkey, [
        # Норми %
        (n_energy,     2700, 2800),
        (n_protein,    14.0, 16.0),
        (n_fat,         3.0,  5.0),
        (n_fiber,       4.0,  6.0),
        (n_calcium,     2.5,  3.0),
        (n_phosphorus,  0.60, 0.70),
        (n_sodium,      0.15, 0.20),
        (n_chlorine,    0.15, 0.25),
        (n_linoleic,    1.0,  1.5),
        # На голову/день
        (n_feed_day,    250,  300),
        (n_protein_day,  35,   48),
        (n_energy_day,  675,  840),
        (n_ca_day,       6.0,  9.0),
        (n_p_day,        1.5,  2.1),
        # Амінокислоти
        (n_lysine,      0.65, 0.75),
        (n_methionine,  0.30, 0.36),
        (n_met_cys,     0.55, 0.65),
        (n_threonine,   0.45, 0.55),
        (n_tryptophan,  0.14, 0.18),
        (n_arginine,    1.00, 1.20),
        # Мікроелементи (мг/кг)
        (n_fe,  60,  80),
        (n_cu,   6,   8),
        (n_zn,  60,  80),
        (n_mn,  70,  90),
        (n_co,  0.4, 0.6),
        (n_i,   0.5, 0.8),
        (n_se,  0.2, 0.3),
        # Вітаміни
        (n_va,  10,  12),
        (n_vd3,  2.5, 3.5),
        (n_ve,  30,  50),
        (n_vk,   2,   4),
        (n_vb1,  2,   3),
        (n_vb2,  4,   6),
    ])

    # ===== Раціон "Племінний корм" =====
    # Значення зі скріншоту (кг на 1000 кг = %)
    # Пшениця 115 кг = 11.5%, Кукурудза 535 кг = 53.5%, Соя 125 кг = 12.5%,
    # Макуха 165 кг = 16.5%, Сіль 3 кг = 0.3%, Мел-Вапняк 54 кг = 5.4%,
    # Сорбент 2 кг = 0.2%, Вітаміни 400 г = 0.04%, Сульфат лізина 800 г = 0.08%,
    # Кістна 10 кг = 1.0%, Метіонін 200 г = 0.02%, Мікроелементи 600 г = 0.06%,
    # Вітамін Е 50 г = 0.005%
    # Сума ≈ 100% (залишки у 0.005% округлено до 0.01 для int)
    rat_id = db.add_ration(ag_turkey, 'Племінний корм', flock_size=1000)
    db.set_ration_ingredients(rat_id, [
        {'ingredient_id': ing_wheat,    'percentage': 11.50},
        {'ingredient_id': ing_corn,     'percentage': 52.39},
        {'ingredient_id': ing_soy,      'percentage': 12.50},
        {'ingredient_id': ing_makuha,   'percentage': 16.50},
        {'ingredient_id': ing_salt,     'percentage':  0.30},
        {'ingredient_id': ing_mel,      'percentage':  5.40},
        {'ingredient_id': ing_sorbent,  'percentage':  0.20},
        {'ingredient_id': ing_vitamins, 'percentage':  0.04},
        {'ingredient_id': ing_lysine_s, 'percentage':  0.08},
        {'ingredient_id': ing_kistna,   'percentage':  1.00},
        {'ingredient_id': ing_met,      'percentage':  0.02},
        {'ingredient_id': ing_micro,    'percentage':  0.06},
        {'ingredient_id': ing_ve,       'percentage':  0.01},
    ])

    # ===== Вид птиці: Курка =====
    bt_chicken = db.add_bird_type('Курка', 'Кури')

    # ===== Вікова група =====
    ag_hen = db.add_age_group(bt_chicken, 'Несучка', 1)

    # ===== Норми для несучки =====
    _set_norms(db, ag_hen, [
        # Базові показники
        (n_energy,      2700, 2800),
        (n_protein,     16.0, 17.0),
        (n_fat,          3.0,  5.0),
        (n_fiber,        3.0,  5.0),
        (n_calcium,      3.4,  3.8),   # підвищений Ca — для шкаралупи яєць
        (n_phosphorus,  0.55, 0.65),
        (n_sodium,      0.15, 0.18),
        (n_chlorine,    0.12, 0.20),
        (n_linoleic,     1.0,  1.5),
        # На голову / день (120 г корму/голову — типово для несучки)
        (n_feed_day,    115,  125),
        (n_protein_day,  18,   21),
        (n_energy_day,  310,  350),
        (n_ca_day,      3.9,  4.7),
        (n_p_day,       0.63, 0.81),
        # Амінокислоти
        (n_lysine,      0.72, 0.80),
        (n_methionine,  0.34, 0.38),
        (n_met_cys,     0.63, 0.70),
        (n_threonine,   0.55, 0.62),
        (n_tryptophan,  0.16, 0.19),
        (n_arginine,    0.80, 0.95),
        # Мікроелементи (мг/кг)
        (n_fe,  50,  60),
        (n_cu,   5,   7),
        (n_zn,  50,  60),
        (n_mn,  60,  70),
        (n_co,  0.3, 0.5),
        (n_i,   0.5, 0.8),
        (n_se,  0.1, 0.2),
        # Вітаміни
        (n_va,   8,  10),
        (n_vd3,  2.0, 3.0),
        (n_ve,  20,  30),
        (n_vk,   1.5, 3.0),
        (n_vb1,  1.5, 2.5),
        (n_vb2,  3.0, 5.0),
    ])

    # ===== Раціон "Корм несучки" =====
    # Склад розраховано на 1000 кг партії (кг → %)
    # Висока частка мелу (вапняку) забезпечує кальцій для шкаралупи яєць
    # Кукурудза 570 кг + Пшениця 130 кг + Соя 170 кг + Макуха 50 кг
    # + Мел-Вапняк 69.2 кг + Кістна 5 кг + Сіль 3 кг + Сорбент 0.6 кг
    # + Вітаміни 0.4 кг + Мікроелементи 0.6 кг + Метіонін 0.3 кг
    # + Сульфат лізина 0.8 кг + Вітамін Е 0.1 кг = 1000 кг (100%)
    rat_hen = db.add_ration(ag_hen, 'Корм несучки', flock_size=5000)
    db.set_ration_ingredients(rat_hen, [
        {'ingredient_id': ing_corn,     'percentage': 57.00},
        {'ingredient_id': ing_wheat,    'percentage': 13.00},
        {'ingredient_id': ing_soy,      'percentage': 17.00},
        {'ingredient_id': ing_makuha,   'percentage':  5.00},
        {'ingredient_id': ing_mel,      'percentage':  6.92},
        {'ingredient_id': ing_kistna,   'percentage':  0.50},
        {'ingredient_id': ing_salt,     'percentage':  0.30},
        {'ingredient_id': ing_sorbent,  'percentage':  0.06},
        {'ingredient_id': ing_vitamins, 'percentage':  0.04},
        {'ingredient_id': ing_micro,    'percentage':  0.06},
        {'ingredient_id': ing_met,      'percentage':  0.03},
        {'ingredient_id': ing_lysine_s, 'percentage':  0.08},
        {'ingredient_id': ing_ve,       'percentage':  0.01},
    ])

    print("[OK] Seed data loaded successfully")


def _add_n(db, name, unit, category, sort_order):
    """Додати поживну речовину"""
    with db.get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO nutrients (name, unit, category, sort_order) VALUES (?, ?, ?, ?)",
            (name, unit, category, sort_order)
        )
        return cur.lastrowid


def _set_norms(db, age_group_id, norms):
    """norms: [(nutrient_id, min_val, max_val), ...]"""
    for n_id, min_v, max_v in norms:
        db.set_nutrient_norm(age_group_id, n_id, min_v, max_v)


def _set_ing_nutrients(db, ingredient_id, nutrients):
    """nutrients: [(nutrient_id, value), ...]"""
    for n_id, val in nutrients:
        db.set_ingredient_nutrient(ingredient_id, n_id, val)


if __name__ == '__main__':
    from app.models import Database
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'normakorm.db')
    d = Database(db_path)
    d.init_db()
    seed_all(d)
