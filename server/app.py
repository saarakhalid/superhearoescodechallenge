from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    serialized_heroes = [hero.serialize() for hero in heroes]
    return jsonify(serialized_heroes), 200

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get_or_404(id)
    serialized_hero = hero.serialize()
    serialized_hero['hero_powers'] = [{'id': hp.id, 'strength': hp.strength} for hp in hero.hero_powers]
    return jsonify(serialized_hero), 200

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    serialized_powers = [power.serialize() for power in powers]
    return jsonify(serialized_powers), 200

@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power_operations(id):
    power = Power.query.get_or_404(id)
    if request.method == 'PATCH':
        data = request.json
        if 'description' in data and len(data['description']) < 20:
            return jsonify({'error': 'Description must be at least 20 characters long'}), 400
        if data:
            if 'name' in data:
                power.name = data['name']
            if 'description' in data:
                power.description = data['description']
            db.session.commit()
        return jsonify({'message': 'Power updated successfully'}), 200
    else:
        return jsonify(power.serialize()), 200

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.json
    if 'hero_id' not in data or 'power_id' not in data or 'strength' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    if data['strength'] not in ['Strong', 'Weak', 'Average']:
        return jsonify({'error': 'Strength must be Strong, Weak, or Average'}), 400
    hero_power = HeroPower(hero_id=data['hero_id'], power_id=data['power_id'], strength=data['strength'])
    db.session.add(hero_power)
    db.session.commit()
    return jsonify({'message': 'Hero power created successfully'}), 200

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
