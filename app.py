from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
import os
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

metrics = PrometheusMetrics(app, group_by='endpoint')

metrics.info('app_info', 'Flask Application info', version='1.0.0')

# Конфигурация БД (Postgres)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Конфигурация Redis Кеша
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = os.environ.get('REDIS_URL')

db = SQLAlchemy(app)
cache = Cache(app)

# Модель данных
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/hello', methods=['GET'])
def hello():
    return "Hello, world!", 200
    
# CRUD Эндпоинты
@app.route('/items', methods=['POST'])
def create_item():
    data = request.json
    new_item = Item(name=data['name'])
    db.session.add(new_item)
    db.session.commit()
    cache.clear() 
    return jsonify({"id": new_item.id, "name": new_item.name}), 201

@app.route('/items', methods=['GET'])
@cache.cached(timeout=60)
def get_items():
    items = Item.query.all()
    return jsonify([{"id": i.id, "name": i.name} for i in items])

@app.route('/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    item = db.session.get(Item, id)
    db.session.delete(item)
    db.session.commit()
    cache.clear()
    return '', 204

@app.route('/items/<int:id>', methods=['PUT'])
def update_item(id):
    item = db.session.get(Item, id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    data = request.json
    item.name = data.get('name', item.name)
    
    db.session.commit()
    cache.clear()
    return jsonify({"id": item.id, "name": item.name})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
