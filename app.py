from flask import Flask, request, jsonify
from models.user import User
from models.lunch import Lunch
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), user.password):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Autenticação realizada com sucesso"})
    return jsonify({"message": "Credenciais inválidas"}), 400

@app.route("/create", methods=["POST"])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')  

    if username and password:
        hashedPassword = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        userAlreadyExists = User.query.filter_by(username=username).first()
        if userAlreadyExists:
            return jsonify({"message": "Usuário já existe"}), 400
        user = User(username=username, password=hashedPassword, role="user")
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário criado com sucesso"})
    return jsonify({"message": "Dados inválidas"}), 400

@app.route("/lunch", methods=["POST"])
@login_required
def create_lunch():
    data = request.json

    name = data.get('name')
    description = data.get('description')
    diet = data.get('diet')
    data = datetime.datetime.now()


    if name and description and diet:
        lunch = Lunch(name=name, description=description, diet = diet, date = data, id_user = current_user.id)
        db.session.add(lunch)
        db.session.commit()
        return jsonify({"message": "Refeição criada com sucesso !"}), 201
    return jsonify({"message": "Dados inválidos"}), 400

@app.route('/lunch/<int:id_lunch>', methods=["PUT"])
@login_required
def update_lunch(id_lunch):
    data = request.json
    lunch = Lunch.query.get(id_lunch)

    name = data.get('name')
    description = data.get('description')
    diet = data.get('diet')


    if current_user.id != lunch.id_user:
        return jsonify({"message": "Operação não permitida"}), 403
    if lunch:
        lunch.name = name
        lunch.description = description
        lunch.dieta = diet
        db.session.commit()
        return jsonify({"message": "Refeição atualizada com sucesso"})
    return jsonify({"message": "Refeição não encontrada"})

@app.route('/lunch/<int:id_lunch>', methods=["DELETE"])
@login_required
def delete_lunch(id_lunch):
    lunch = Lunch.query.get(id_lunch)


    if current_user.id == lunch.id_user:
        db.session.delete(lunch)
        db.session.commit()
        return jsonify({"message": "Refeição deletada com sucesso"})
    return jsonify({"message": "Refeição não encontrada"}), 404

@app.route('/lunch', methods=["GET"])
@login_required
def fetch_lunch():
    lunchs = Lunch.query.filter(Lunch.id_user == current_user.id).all()

    lunchs_dict = [lunch.to_dict() for lunch in lunchs]

    return jsonify(lunchs_dict)

@app.route("/lunch/<int:id_lunch>", methods=["GET"])
@login_required
def get_lunch(id_lunch):
    lunch = Lunch.query.get(id_lunch)

    return jsonify(lunch.to_dict())


if __name__ == '__main__':
    app.run(debug=True)
else:
    app.run()