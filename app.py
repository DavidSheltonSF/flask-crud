from flask import Flask, render_template, session, abort, request, redirect, url_for
from models.usuario import db
from controllers.usuario import app as usuario_controller
import requests

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.sqlite3"
# It's important to use session
app.secret_key = "$$$581489*@Abscaracha"
# Register the usuario's blueprint
app.register_blueprint(usuario_controller, url_prefix="/usuario/")


def check_email_exists(email):
    resp = requests.get(f"http://127.0.0.1:5000/usuario/getuser/{email}").json()
    return bool(resp["data"])


def check_passwd_exists(email, password):
    resp = requests.get(f"http://127.0.0.1:5000/usuario/getuser/{email}").json()
    if resp["data"]:
        return resp["data"]["senha"] == password
    else:
        return False


# Decorator to import libs in HTML code
@app.template_filter()
def import_lib(lib_name):
  return __import__(lib_name)


@app.route("/")
def index():
    username = None
    if "username" in session:
        username = session["username"]
    return render_template("index.html", username=username)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # Check the email
        valid_email= check_email_exists(request.form["useremail"])
        # Check the password
        valid_passwd = check_passwd_exists(request.form["useremail"], request.form["userpassword"])
        # Verifica as credenciais do usuário
        if valid_email and valid_passwd:
            # Request to get user data using email
            resp = requests.get(f"http://127.0.0.1:5000/usuario/getuser/{request.form['useremail']}").json()
            session["username"] = resp["data"]["nome"]
            # redirect to index
            return redirect(url_for("index"), code=302)
        else:
            # Abord with Unauthorized code
            abort(401)
    else:
        return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        usuario = {
            "nome": request.form["username"],
            "sobrenome": request.form["userlastname"],
            "email": request.form["useremail"],
            "senha": request.form["userpassword"],
            "dataDeAniversario": request.form["userbirthday"],
            "genero": request.form["usergender"],
        }
        url = "http://127.0.0.1:5000/usuario/add"
        resp = requests.post(url=url, json=usuario)
        return redirect(url_for("login"))
    else:
        return render_template("register.html")


@app.route("/edit/<useremail>", methods=["POST", "GET"])
def edit(useremail):
    
    if request.method == "POST":
        usuario = {
            "nome": request.form["username"],
            "sobrenome": request.form["userlastname"],
            "email": request.form["useremail"],
            "senha": request.form["userpassword"],
            "dataDeAniversario": request.form["userbirthday"],
            "genero": request.form["usergender"],
        }
        url = f"http://127.0.0.1:5000/usuario/edit/{useremail}"
        resp = requests.put(url=url, json=usuario)
        return redirect(url_for("table"))

    else:
        url = url = f"http://127.0.0.1:5000/usuario/getuser/{useremail}"
        resp = requests.get(url=url).json()
        usuario = resp["data"]
        return render_template("edit.html", usuario=usuario)


@app.route("/delete/<useremail>")
def delete(useremail):
    url = url = f"http://127.0.0.1:5000/usuario/delete/{useremail}"
    resp = requests.delete(url=url)
    return redirect(url_for("table"))

@app.route("/table")
def table():
    resp = requests.get("http://127.0.0.1:5000/usuario/").json()
    usuarios = resp["data"]
    return render_template("table.html", usuarios=usuarios)


@app.route("/logout")
def logout():
    # Remove the username from the session
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Inicia e configura o banco de dados
    db.init_app(app=app)
    # Crea as tabelas apenas se a aplicação estiver pronta
    with app.test_request_context():
        db.create_all()
    app.run(debug=True)