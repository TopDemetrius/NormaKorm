import io
import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, send_file
from app.models import db
from app.decorators import login_required

bp = Blueprint('reports', __name__)


@bp.route('/reports')
@login_required
def reports_page():
    return render_template('reports.html')


@bp.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Генерація PDF-звіту"""
    try:
        from fpdf import FPDF
    except ImportError:
        return jsonify({'error': 'fpdf2 не встановлено'}), 500

    data = request.json
    report_type = data.get('type', 'rations')  # rations, ingredients, prices, optimization
    date_from = data.get('date_from')
    date_to = data.get('date_to')

    pdf = FPDF()
    pdf.add_page()

    # Шрифт з підтримкою кирилиці
    font_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')
    font_path = os.path.join(font_dir, 'DejaVuSans.ttf')
    font_bold_path = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')

    if os.path.exists(font_path):
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.add_font('DejaVu', 'B', font_bold_path, uni=True)
        font_name = 'DejaVu'
    else:
        font_name = 'Helvetica'

    # Заголовок
    pdf.set_font(font_name, 'B', 16)
    pdf.cell(0, 10, 'НормаКорм — Звіт', ln=True, align='C')
    pdf.set_font(font_name, '', 10)
    pdf.cell(0, 8, f'Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")}', ln=True, align='C')
    if date_from:
        period_str = f'Період: {date_from}'
        if date_to:
            period_str += f' — {date_to}'
        pdf.cell(0, 8, period_str, ln=True, align='C')
    pdf.ln(5)

    if report_type == 'rations':
        _generate_rations_report(pdf, font_name, date_from, date_to)
    elif report_type == 'ingredients':
        _generate_ingredients_report(pdf, font_name)
    elif report_type == 'prices':
        _generate_prices_report(pdf, font_name)
    elif report_type == 'optimization':
        _generate_optimization_report(pdf, font_name, data)

    # Повернути PDF як файл
    pdf_bytes = pdf.output()
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)

    filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


def _generate_rations_report(pdf, font_name, date_from=None, date_to=None):
    pdf.set_font(font_name, 'B', 14)
    pdf.cell(0, 10, 'Звіт по раціонах', ln=True)
    pdf.ln(3)

    rations = db.get_rations()

    # Фільтрація за датою
    if date_from:
        rations = [r for r in rations if r['created_at'] and r['created_at'] >= date_from]
    if date_to:
        rations = [r for r in rations if r['created_at'] and r['created_at'] <= date_to + ' 23:59:59']

    if not rations:
        pdf.set_font(font_name, '', 11)
        pdf.cell(0, 8, 'Раціони не знайдено за вказаний період.', ln=True)
        return

    # Заголовки таблиці
    pdf.set_font(font_name, 'B', 9)
    col_widths = [60, 30, 35, 25, 20, 20]
    headers = ['Назва', 'Вид птиці', 'Вік', "Погол.", 'Вартість', 'Статус']
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1)
    pdf.ln()

    pdf.set_font(font_name, '', 8)
    for r in rations:
        analysis = db.analyze_ration(r['id'])
        status_text = {'normal': 'Норма', 'warning': 'Попер.', 'violation': 'Поруш.'}.get(
            analysis['overall_status'] if analysis else 'draft', 'Чернетка'
        )
        cost = f"{analysis['total_cost_per_kg']:.2f}" if analysis else '-'

        vals = [
            r['name'][:30],
            r['bird_type_name'][:15],
            r['age_group_name'][:18],
            str(r['flock_size']),
            cost,
            status_text
        ]
        for i, v in enumerate(vals):
            pdf.cell(col_widths[i], 7, v, border=1)
        pdf.ln()

    # Детальний аналіз кожного раціону
    for r in rations:
        pdf.ln(5)
        pdf.set_font(font_name, 'B', 11)
        pdf.cell(0, 8, f'Раціон: {r["name"]}', ln=True)

        ration_ings = db.get_ration_ingredients(r['id'])
        if ration_ings:
            pdf.set_font(font_name, 'B', 9)
            pdf.cell(60, 7, 'Інгредієнт', border=1)
            pdf.cell(25, 7, '%', border=1)
            pdf.cell(30, 7, 'Ціна ₴/кг', border=1)
            pdf.cell(30, 7, 'Вартість', border=1)
            pdf.ln()

            pdf.set_font(font_name, '', 8)
            total_cost = 0
            for ri in ration_ings:
                cost = (ri['price'] or 0) * ri['percentage'] / 100
                total_cost += cost
                pdf.cell(60, 6, ri['ingredient_name'][:28], border=1)
                pdf.cell(25, 6, f"{ri['percentage']:.1f}", border=1)
                pdf.cell(30, 6, f"{ri['price'] or 0:.2f}", border=1)
                pdf.cell(30, 6, f"{cost:.4f}", border=1)
                pdf.ln()

            pdf.set_font(font_name, 'B', 9)
            pdf.cell(85, 7, 'Всього', border=1)
            pdf.cell(30, 7, f"{total_cost:.2f}", border=1)
            pdf.ln()


def _generate_ingredients_report(pdf, font_name):
    pdf.set_font(font_name, 'B', 14)
    pdf.cell(0, 10, 'Довідник інгредієнтів', ln=True)
    pdf.ln(3)

    ingredients = db.get_ingredients()
    pdf.set_font(font_name, 'B', 9)
    cols = [50, 30, 25, 25, 25, 25]
    headers = ['Назва', 'Категорія', 'Волог. %', 'Ціна ₴/кг', 'Макс. %', 'Протеїн']
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 8, h, border=1)
    pdf.ln()

    pdf.set_font(font_name, '', 8)
    for ing in ingredients:
        nutrients = db.get_ingredient_nutrients(ing['id'])
        protein = next((n['value'] for n in nutrients if 'протеїн' in n['nutrient_name'].lower()), 0)
        vals = [
            ing['name'][:25],
            ing['category_name'][:15],
            f"{ing['moisture']:.1f}",
            f"{ing['price']:.2f}",
            f"{ing['max_inclusion_pct']:.0f}",
            f"{protein:.1f}"
        ]
        for i, v in enumerate(vals):
            pdf.cell(cols[i], 6, v, border=1)
        pdf.ln()


def _generate_prices_report(pdf, font_name):
    pdf.set_font(font_name, 'B', 14)
    pdf.cell(0, 10, 'Звіт по цінах', ln=True)
    pdf.ln(3)

    prices = db.get_prices_with_history()
    pdf.set_font(font_name, 'B', 9)
    cols = [50, 35, 35, 30, 40]
    headers = ['Інгредієнт', 'Поточна ціна', 'Попередня', 'Зміна %', 'Оновлено']
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 8, h, border=1)
    pdf.ln()

    pdf.set_font(font_name, '', 8)
    for p in prices:
        prev = p['prev_price'] or 0
        change = round((p['current_price'] - prev) / prev * 100, 1) if prev > 0 else 0
        date_str = p['last_updated'][:10] if p['last_updated'] else '-'
        vals = [
            p['name'][:25],
            f"{p['current_price']:.2f} ₴/кг",
            f"{prev:.2f} ₴/кг" if prev else '-',
            f"{change:+.1f}%",
            date_str
        ]
        for i, v in enumerate(vals):
            pdf.cell(cols[i], 6, v, border=1)
        pdf.ln()


def _generate_optimization_report(pdf, font_name, data):
    pdf.set_font(font_name, 'B', 14)
    pdf.cell(0, 10, 'Звіт оптимізації раціону', ln=True)
    pdf.ln(3)

    result = data.get('result', {})
    if not result:
        pdf.set_font(font_name, '', 11)
        pdf.cell(0, 8, 'Дані оптимізації не надано.', ln=True)
        return

    pdf.set_font(font_name, '', 10)
    pdf.cell(0, 7, f"Статус: {result.get('status', '-')}", ln=True)
    pdf.cell(0, 7, f"Вартість 1 кг: {result.get('total_cost', 0):.2f} грн", ln=True)
    pdf.ln(3)

    ings = result.get('ingredients', [])
    if ings:
        pdf.set_font(font_name, 'B', 9)
        pdf.cell(70, 8, 'Інгредієнт', border=1)
        pdf.cell(30, 8, '%', border=1)
        pdf.cell(40, 8, 'Вартість ₴/кг', border=1)
        pdf.ln()

        pdf.set_font(font_name, '', 8)
        for ing in ings:
            pdf.cell(70, 6, ing['name'][:35], border=1)
            pdf.cell(30, 6, f"{ing['percentage']:.2f}", border=1)
            pdf.cell(40, 6, f"{ing['cost']:.4f}", border=1)
            pdf.ln()
