PRAGMA foreign_keys = ON;

-- Види птиці
CREATE TABLE IF NOT EXISTS bird_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT ''
);

-- Вікові групи
CREATE TABLE IF NOT EXISTS age_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bird_type_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (bird_type_id) REFERENCES bird_types(id) ON DELETE CASCADE
);

-- Поживні речовини
CREATE TABLE IF NOT EXISTS nutrients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT '%',
    category TEXT NOT NULL DEFAULT 'basic',
    sort_order INTEGER DEFAULT 0
);
-- category: 'basic', 'per_head', 'amino_acid', 'microelement', 'vitamin'

-- Норми поживних речовин для вікової групи
CREATE TABLE IF NOT EXISTS nutrient_norms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age_group_id INTEGER NOT NULL,
    nutrient_id INTEGER NOT NULL,
    min_value REAL,
    max_value REAL,
    FOREIGN KEY (age_group_id) REFERENCES age_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (nutrient_id) REFERENCES nutrients(id) ON DELETE CASCADE,
    UNIQUE(age_group_id, nutrient_id)
);

-- Категорії інгредієнтів
CREATE TABLE IF NOT EXISTS ingredient_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#6C3CE1'
);

-- Інгредієнти
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    moisture REAL DEFAULT 0,
    price REAL DEFAULT 0,
    max_inclusion_pct REAL DEFAULT 100,
    FOREIGN KEY (category_id) REFERENCES ingredient_categories(id) ON DELETE RESTRICT
);

-- Поживний склад інгредієнтів
CREATE TABLE IF NOT EXISTS ingredient_nutrients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL,
    nutrient_id INTEGER NOT NULL,
    value REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    FOREIGN KEY (nutrient_id) REFERENCES nutrients(id) ON DELETE CASCADE,
    UNIQUE(ingredient_id, nutrient_id)
);

-- Раціони
CREATE TABLE IF NOT EXISTS rations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age_group_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    flock_size INTEGER DEFAULT 1000,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (age_group_id) REFERENCES age_groups(id) ON DELETE RESTRICT
);

-- Склад раціону
CREATE TABLE IF NOT EXISTS ration_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ration_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    percentage REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (ration_id) REFERENCES rations(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT,
    UNIQUE(ration_id, ingredient_id)
);

-- Історія цін
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL,
    price REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- Користувачі
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    name TEXT NOT NULL DEFAULT '',
    email TEXT DEFAULT '',
    position TEXT DEFAULT '',
    password_hash TEXT DEFAULT ''
);

-- Індекси
CREATE INDEX IF NOT EXISTS idx_age_groups_bird_type ON age_groups(bird_type_id);
CREATE INDEX IF NOT EXISTS idx_nutrient_norms_ag ON nutrient_norms(age_group_id);
CREATE INDEX IF NOT EXISTS idx_ingredient_nutrients_ing ON ingredient_nutrients(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_ration_ingredients_rat ON ration_ingredients(ration_id);
CREATE INDEX IF NOT EXISTS idx_price_history_ing ON price_history(ingredient_id);
