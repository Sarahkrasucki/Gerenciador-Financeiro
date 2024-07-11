from flask import Flask, request, redirect, url_for, render_template, flash
import csv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Cria uma instância do Flask chamada app e configura a chave secreta para garantir a segurança do aplicativo.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Substitua por uma chave secreta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de usuário
# define o modelo de usuário usando SQLAlchemy, criando a classe User. 
# O modelo de usuário tem três campos: id, username e password. 
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # O campo id é uma chave primária, e username é único para cada usuário.
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Configura o Flask-Login para gerenciar a autenticação de usuários.
@login_manager.user_loader
# Implementa a função load_user que é usada para carregar um usuário com base no user_id armazenado na sessão.
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/", methods=["GET", "POST"])
def login():
    
    # Login_user(user) do Flask-Login, e a função redirect redireciona o usuário para a rota 'transactions'.
    # Se as credenciais estiverem incorretas, a página de login é renderizada usando render_template.
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("transactions"))
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def return_login():
    
    # Login_user(user) do Flask-Login, e a função redirect redireciona o usuário para a rota 'transactions'.
    # Se as credenciais estiverem incorretas, a página de login é renderizada usando render_template.
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("transactions"))
    flash("Dados de login inválidos. Tente novamente!", "error")  # Exibe uma mensagem de erro
    return render_template("login.html")

@app.route("/transactions")
def transactions():
    # Lista para armazenar as transações lidas do arquivo CSV
    transaction_list = []

    # Abre o arquivo CSV e le as transações
    with open('uploads/transactions.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            # Cada linha do CSV é uma lista de valores
            data, descricao, valor = row
            transaction_list.append({
                'data': data,
                'descricao': descricao,
                'valor': valor 
            })

    # Renderize o modelo HTML 'transactions.html' e passe a lista de transações
    return render_template("transactions.html", transactions=transaction_list)
   
@app.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        data = request.form["data"]
        descricao = request.form["descricao"]
        valor = request.form["valor"]

        # Verifique se os campos não estão vazios
        if not data or not descricao or not valor:
            flash("Todos os campos são obrigatórios.", "error")
        else:
            try:
                valor = float(valor)  # Verifique se o valor é um número válido
                with open('uploads/transactions.csv', 'a', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow([data, descricao, valor])
                
                flash("Transação adicionada com sucesso!", "success")
            except ValueError:
                flash("Valor deve ser um número válido.", "error")
        

    return render_template("add_transactions.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        existing_user = User.query.filter_by(username='username').first()
        if not existing_user:
            # Crie um usuário de exemplo apenas se ele não existir
            user = User(username='username', password='password')
            db.session.add(user)
            db.session.commit()
    app.run(debug=True)

