from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === ЗАМЕНИ на свою ссылку ===
WEBHOOK_BASE = 'https://b24-sh6nwy.bitrix24.ru/rest/1/lve25sfdf6h4ieri'

# === Найти игрока по имени ===
def get_lead_by_name(name):
    url = f'{WEBHOOK_BASE}/crm.lead.list.json'
    response = requests.post(url, json={
        "filter": {
            "NAME": name
        },
        "select": ["ID", "NAME", "OPPORTUNITY"]
    })
    leads = response.json().get("result", [])
    return leads[0] if leads else None


# === Обновить баллы ===
def update_score(lead_id, new_score):
    url = f'{WEBHOOK_BASE}/crm.lead.update.json'
    payload = {
        "id": lead_id,
        "fields": {
            "OPPORTUNITY": new_score
        }
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200


# === Игровой API: Обновить баллы игрока ===
@app.route('/update_score', methods=['POST'])
def update_player_score():
    data = request.get_json()
    name = data.get('name')
    score = data.get('score')

    if not name or score is None:
        return jsonify({"error": "name and score required"}), 400

    lead = get_lead_by_name(name)
    if not lead:
        return jsonify({"error": "player not found"}), 404

    success = update_score(lead['ID'], score)
    if success:
        return jsonify({"message": "score updated"}), 200
    else:
        return jsonify({"error": "update failed"}), 500


# === Таблица лидеров: имя и баллы ===
@app.route('/leaderboard')
def leaderboard():
    url = f'{WEBHOOK_BASE}/crm.lead.list.json'
    response = requests.post(url, json={
        "order": {"OPPORTUNITY": "DESC"},
        "filter": {"TITLE": "Игрок"},
        "select": ["NAME", "OPPORTUNITY"]
    })
    leads = response.json().get("result", [])

    table = []
    for lead in leads:
        table.append({
            "name": lead.get("NAME", "Без имени"),
            "score": float(lead.get("OPPORTUNITY", 0))
        })

    return jsonify(table)


if __name__ == '__main__':
    app.run(debug=True)