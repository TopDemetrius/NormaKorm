import sqlite3
import os
from contextlib import contextmanager
from app.config import Config


class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')
        with self.get_connection() as conn:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            # Міграція: додати поле username якщо не існує
            cols = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
            if 'username' not in cols:
                conn.execute("ALTER TABLE users ADD COLUMN username TEXT")
            # Встановити username для існуючих записів без нього
            conn.execute(
                "UPDATE users SET username = 'admin' WHERE username IS NULL OR username = ''"
            )
            # Встановити дефолтний пароль якщо порожній
            from werkzeug.security import generate_password_hash
            rows = conn.execute(
                "SELECT id, password_hash FROM users WHERE password_hash IS NULL OR password_hash = ''"
            ).fetchall()
            for row in rows:
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (generate_password_hash('admin123'), row['id'])
                )
            # Якщо таблиця порожня — створити дефолтного адміна
            existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if existing == 0:
                from werkzeug.security import generate_password_hash as gph
                conn.execute(
                    "INSERT INTO users (username, name, email, position, password_hash) VALUES (?, ?, ?, ?, ?)",
                    ('admin', 'Адміністратор', 'admin@normakorm.ua', 'Адміністратор',
                     gph('admin123'))
                )

    # ========== Bird Types ==========
    def get_bird_types(self):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM bird_types ORDER BY id").fetchall()

    def add_bird_type(self, name, description=''):
        with self.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO bird_types (name, description) VALUES (?, ?)",
                (name, description)
            )
            return cur.lastrowid

    def delete_bird_type(self, bt_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM bird_types WHERE id = ?", (bt_id,))

    # ========== Age Groups ==========
    def get_age_groups(self, bird_type_id=None):
        with self.get_connection() as conn:
            if bird_type_id:
                return conn.execute(
                    "SELECT * FROM age_groups WHERE bird_type_id = ? ORDER BY sort_order",
                    (bird_type_id,)
                ).fetchall()
            return conn.execute("SELECT * FROM age_groups ORDER BY bird_type_id, sort_order").fetchall()

    def get_age_group(self, ag_id):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM age_groups WHERE id = ?", (ag_id,)).fetchone()

    def add_age_group(self, bird_type_id, name, sort_order=0):
        with self.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO age_groups (bird_type_id, name, sort_order) VALUES (?, ?, ?)",
                (bird_type_id, name, sort_order)
            )
            return cur.lastrowid

    def delete_age_group(self, ag_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM age_groups WHERE id = ?", (ag_id,))

    # ========== Nutrients ==========
    def get_nutrients(self, category=None):
        with self.get_connection() as conn:
            if category:
                return conn.execute(
                    "SELECT * FROM nutrients WHERE category = ? ORDER BY sort_order",
                    (category,)
                ).fetchall()
            return conn.execute("SELECT * FROM nutrients ORDER BY category, sort_order").fetchall()

    def get_nutrient(self, n_id):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM nutrients WHERE id = ?", (n_id,)).fetchone()

    # ========== Nutrient Norms ==========
    def get_nutrient_norms(self, age_group_id, category=None):
        with self.get_connection() as conn:
            if category:
                return conn.execute("""
                    SELECT nn.*, n.name as nutrient_name, n.unit, n.category
                    FROM nutrient_norms nn
                    JOIN nutrients n ON nn.nutrient_id = n.id
                    WHERE nn.age_group_id = ? AND n.category = ?
                    ORDER BY n.sort_order
                """, (age_group_id, category)).fetchall()
            return conn.execute("""
                SELECT nn.*, n.name as nutrient_name, n.unit, n.category
                FROM nutrient_norms nn
                JOIN nutrients n ON nn.nutrient_id = n.id
                WHERE nn.age_group_id = ?
                ORDER BY n.category, n.sort_order
            """, (age_group_id,)).fetchall()

    def set_nutrient_norm(self, age_group_id, nutrient_id, min_value, max_value):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO nutrient_norms (age_group_id, nutrient_id, min_value, max_value)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(age_group_id, nutrient_id) 
                DO UPDATE SET min_value = excluded.min_value, max_value = excluded.max_value
            """, (age_group_id, nutrient_id, min_value, max_value))

    def save_norms_batch(self, age_group_id, norms):
        """norms: list of dicts {nutrient_id, min_value, max_value}"""
        with self.get_connection() as conn:
            for norm in norms:
                conn.execute("""
                    INSERT INTO nutrient_norms (age_group_id, nutrient_id, min_value, max_value)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(age_group_id, nutrient_id) 
                    DO UPDATE SET min_value = excluded.min_value, max_value = excluded.max_value
                """, (age_group_id, norm['nutrient_id'], norm.get('min_value'), norm.get('max_value')))

    def delete_nutrient_norm(self, age_group_id, nutrient_id):
        """Видалити конкретну норму"""
        with self.get_connection() as conn:
            conn.execute(
                "DELETE FROM nutrient_norms WHERE age_group_id = ? AND nutrient_id = ?",
                (age_group_id, nutrient_id)
            )

    # ========== Ingredient Categories ==========
    def get_ingredient_categories(self):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM ingredient_categories ORDER BY id").fetchall()

    def add_ingredient_category(self, name, color='#6C3CE1'):
        with self.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO ingredient_categories (name, color) VALUES (?, ?)",
                (name, color)
            )
            return cur.lastrowid

    # ========== Ingredients ==========
    def get_ingredients(self, category_id=None, search=None):
        with self.get_connection() as conn:
            query = """
                SELECT i.*, ic.name as category_name, ic.color as category_color
                FROM ingredients i
                JOIN ingredient_categories ic ON i.category_id = ic.id
            """
            params = []
            conditions = []
            if category_id:
                conditions.append("i.category_id = ?")
                params.append(category_id)
            if search:
                conditions.append("i.name LIKE ?")
                params.append(f"%{search}%")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY ic.name, i.name"
            return conn.execute(query, params).fetchall()

    def get_ingredient(self, ing_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT i.*, ic.name as category_name, ic.color as category_color
                FROM ingredients i
                JOIN ingredient_categories ic ON i.category_id = ic.id
                WHERE i.id = ?
            """, (ing_id,)).fetchone()

    def add_ingredient(self, category_id, name, moisture=0, price=0, max_inclusion_pct=100):
        with self.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO ingredients (category_id, name, moisture, price, max_inclusion_pct) VALUES (?, ?, ?, ?, ?)",
                (category_id, name, moisture, price, max_inclusion_pct)
            )
            return cur.lastrowid

    def update_ingredient(self, ing_id, **kwargs):
        with self.get_connection() as conn:
            sets = ", ".join(f"{k} = ?" for k in kwargs)
            vals = list(kwargs.values()) + [ing_id]
            conn.execute(f"UPDATE ingredients SET {sets} WHERE id = ?", vals)

    def delete_ingredient(self, ing_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM ingredients WHERE id = ?", (ing_id,))

    # ========== Ingredient Nutrients ==========
    def get_ingredient_nutrients(self, ingredient_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT inu.*, n.name as nutrient_name, n.unit, n.category
                FROM ingredient_nutrients inu
                JOIN nutrients n ON inu.nutrient_id = n.id
                WHERE inu.ingredient_id = ?
                ORDER BY n.category, n.sort_order
            """, (ingredient_id,)).fetchall()

    def set_ingredient_nutrient(self, ingredient_id, nutrient_id, value):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO ingredient_nutrients (ingredient_id, nutrient_id, value)
                VALUES (?, ?, ?)
                ON CONFLICT(ingredient_id, nutrient_id) DO UPDATE SET value = excluded.value
            """, (ingredient_id, nutrient_id, value))

    def save_ingredient_nutrients_batch(self, ingredient_id, nutrients):
        """nutrients: list of dicts {nutrient_id, value}"""
        with self.get_connection() as conn:
            for n in nutrients:
                conn.execute("""
                    INSERT INTO ingredient_nutrients (ingredient_id, nutrient_id, value)
                    VALUES (?, ?, ?)
                    ON CONFLICT(ingredient_id, nutrient_id) DO UPDATE SET value = excluded.value
                """, (ingredient_id, n['nutrient_id'], n['value']))

    # ========== Rations ==========
    def get_rations(self, limit=None):
        with self.get_connection() as conn:
            query = """
                SELECT r.*, ag.name as age_group_name, bt.name as bird_type_name
                FROM rations r
                JOIN age_groups ag ON r.age_group_id = ag.id
                JOIN bird_types bt ON ag.bird_type_id = bt.id
                ORDER BY r.updated_at DESC
            """
            if limit:
                query += f" LIMIT {limit}"
            return conn.execute(query).fetchall()

    def get_ration(self, rat_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT r.*, ag.name as age_group_name, bt.name as bird_type_name
                FROM rations r
                JOIN age_groups ag ON r.age_group_id = ag.id
                JOIN bird_types bt ON ag.bird_type_id = bt.id
                WHERE r.id = ?
            """, (rat_id,)).fetchone()

    def add_ration(self, age_group_id, name, flock_size=1000):
        with self.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO rations (age_group_id, name, flock_size) VALUES (?, ?, ?)",
                (age_group_id, name, flock_size)
            )
            return cur.lastrowid

    def update_ration(self, rat_id, **kwargs):
        with self.get_connection() as conn:
            kwargs['updated_at'] = 'CURRENT_TIMESTAMP'
            sets = []
            vals = []
            for k, v in kwargs.items():
                if v == 'CURRENT_TIMESTAMP':
                    sets.append(f"{k} = CURRENT_TIMESTAMP")
                else:
                    sets.append(f"{k} = ?")
                    vals.append(v)
            vals.append(rat_id)
            conn.execute(f"UPDATE rations SET {', '.join(sets)} WHERE id = ?", vals)

    def delete_ration(self, rat_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM rations WHERE id = ?", (rat_id,))

    # ========== Ration Ingredients ==========
    def get_ration_ingredients(self, ration_id):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT ri.*, i.name as ingredient_name, i.price,
                       ic.name as category_name, ic.color as category_color
                FROM ration_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.id
                JOIN ingredient_categories ic ON i.category_id = ic.id
                WHERE ri.ration_id = ?
                ORDER BY ri.percentage DESC
            """, (ration_id,)).fetchall()

    def set_ration_ingredients(self, ration_id, ingredients):
        """ingredients: list of dicts {ingredient_id, percentage}"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM ration_ingredients WHERE ration_id = ?", (ration_id,))
            for ing in ingredients:
                if ing.get('percentage', 0) > 0:
                    conn.execute(
                        "INSERT INTO ration_ingredients (ration_id, ingredient_id, percentage) VALUES (?, ?, ?)",
                        (ration_id, ing['ingredient_id'], ing['percentage'])
                    )

    # ========== Price History ==========
    def get_price_history(self, ingredient_id=None, limit=50):
        with self.get_connection() as conn:
            if ingredient_id:
                return conn.execute("""
                    SELECT ph.*, i.name as ingredient_name
                    FROM price_history ph
                    JOIN ingredients i ON ph.ingredient_id = i.id
                    WHERE ph.ingredient_id = ?
                    ORDER BY ph.recorded_at DESC LIMIT ?
                """, (ingredient_id, limit)).fetchall()
            return conn.execute("""
                SELECT ph.*, i.name as ingredient_name
                FROM price_history ph
                JOIN ingredients i ON ph.ingredient_id = i.id
                ORDER BY ph.recorded_at DESC LIMIT ?
            """, (limit,)).fetchall()

    def add_price_record(self, ingredient_id, price):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO price_history (ingredient_id, price) VALUES (?, ?)",
                (ingredient_id, price)
            )
            conn.execute(
                "UPDATE ingredients SET price = ? WHERE id = ?",
                (price, ingredient_id)
            )

    def get_prices_with_history(self):
        with self.get_connection() as conn:
            return conn.execute("""
                SELECT i.id, i.name, i.price as current_price,
                       (SELECT ph.price FROM price_history ph 
                        WHERE ph.ingredient_id = i.id 
                        ORDER BY ph.recorded_at DESC LIMIT 1 OFFSET 1) as prev_price,
                       (SELECT ph.recorded_at FROM price_history ph 
                        WHERE ph.ingredient_id = i.id 
                        ORDER BY ph.recorded_at DESC LIMIT 1) as last_updated
                FROM ingredients i
                WHERE i.price > 0
                ORDER BY i.name
            """).fetchall()

    # ========== Users ==========
    def get_user(self, user_id=1):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    def get_user_by_username(self, username):
        with self.get_connection() as conn:
            return conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

    def get_all_users(self):
        with self.get_connection() as conn:
            return conn.execute("SELECT * FROM users ORDER BY id").fetchall()

    def add_user(self, username, password_hash, name, email='', position=''):
        with self.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, name, email, position) VALUES (?, ?, ?, ?, ?)",
                (username, password_hash, name, email, position)
            )
            return cur.lastrowid

    def update_user(self, user_id, **kwargs):
        with self.get_connection() as conn:
            sets = ", ".join(f"{k} = ?" for k in kwargs)
            vals = list(kwargs.values()) + [user_id]
            conn.execute(f"UPDATE users SET {sets} WHERE id = ?", vals)

    # ========== Analysis helpers ==========
    def analyze_ration(self, ration_id):
        """Аналіз раціону: порівняння фактичних значень з нормами"""
        ration = self.get_ration(ration_id)
        if not ration:
            return None

        ration_ings = self.get_ration_ingredients(ration_id)
        norms = self.get_nutrient_norms(ration['age_group_id'])
        all_nutrients = self.get_nutrients()

        # Порахувати фактичні значення поживних речовин у раціоні
        nutrient_totals = {}
        total_cost = 0
        for ri in ration_ings:
            pct = ri['percentage']
            ing_nutrients = self.get_ingredient_nutrients(ri['ingredient_id'])
            total_cost += (ri['price'] or 0) * pct / 100
            for inu in ing_nutrients:
                nid = inu['nutrient_id']
                nutrient_totals[nid] = nutrient_totals.get(nid, 0) + inu['value'] * pct / 100

        # Порівняти з нормами
        analysis = []
        for norm in norms:
            nid = norm['nutrient_id']
            actual = nutrient_totals.get(nid, 0)
            min_v = norm['min_value']
            max_v = norm['max_value']

            if min_v is not None and max_v is not None:
                if min_v <= actual <= max_v:
                    status = 'normal'
                elif actual < min_v:
                    deviation = (min_v - actual) / min_v * 100 if min_v else 0
                    status = 'warning' if deviation <= 10 else 'violation'
                else:
                    deviation = (actual - max_v) / max_v * 100 if max_v else 0
                    status = 'warning' if deviation <= 10 else 'violation'
            else:
                status = 'normal'

            analysis.append({
                'nutrient_name': norm['nutrient_name'],
                'unit': norm['unit'],
                'category': norm['category'],
                'min_value': min_v,
                'max_value': max_v,
                'actual_value': round(actual, 2),
                'status': status
            })

        overall = 'normal'
        if any(a['status'] == 'violation' for a in analysis):
            overall = 'violation'
        elif any(a['status'] == 'warning' for a in analysis):
            overall = 'warning'

        return {
            'analysis': analysis,
            'total_cost_per_kg': round(total_cost, 2),
            'overall_status': overall
        }

    def get_optimization_data(self, age_group_id, ingredient_ids):
        """Зібрати всі дані для оптимізації"""
        norms = self.get_nutrient_norms(age_group_id)
        ingredients_data = []
        for ing_id in ingredient_ids:
            ing = self.get_ingredient(ing_id)
            if ing:
                nutrients = self.get_ingredient_nutrients(ing_id)
                ingredients_data.append({
                    'id': ing['id'],
                    'name': ing['name'],
                    'price': ing['price'] or 0,
                    'max_inclusion_pct': ing['max_inclusion_pct'] or 100,
                    'nutrients': {n['nutrient_id']: n['value'] for n in nutrients}
                })

        norms_data = []
        for n in norms:
            norms_data.append({
                'nutrient_id': n['nutrient_id'],
                'nutrient_name': n['nutrient_name'],
                'unit': n['unit'],
                'min_value': n['min_value'],
                'max_value': n['max_value']
            })

        return {
            'ingredients': ingredients_data,
            'norms': norms_data
        }


# Singleton
db = Database()
