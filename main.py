from functools import wraps
from flask import Flask, jsonify, request, render_template, make_response, redirect, url_for, session
from forms import LoginForm, PostCreateForm
from utils import access_token_request, activate_user_request, post_create_request, post_list_request, users_list_request, user_retrieve_request, user_me_request

app = Flask(__name__)
app.config["SECRET_KEY"] = "SUPERSECRETKEY"

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.cookies.get("access"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(form.data)
        tokens = access_token_request(
            username=form.username.data,
            password=form.password.data,
        )
        session["access"] = tokens["access"]
        session["refresh"] = tokens["refresh"]
        session.modified = True
        return redirect(url_for("users_list"))
    return render_template("login.html", form=form)


@app.route("/users", methods=["GET"])
@login_required
def users_list():
    users = users_list_request()
    return render_template("users_list.html", users=users)


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/users/<int:user_id>", methods=["GET"])
@login_required
def users_detail(user_id):
    user = user_retrieve_request(user_id)
    return render_template("user_detail.html", user=user)


@app.route("/activate/<string:register_token>", methods=["GET"])
def activate_user(register_token):
    session.clear()
    activate_user_request(register_token)
    return redirect(url_for("login"))


@app.route("/me-ajax", methods=["GET"])
def me_ajax():
    user = user_me_request()
    return jsonify(user), 200


@app.route("/posts", methods=["GET"])
def post_list():
    form = PostCreateForm()
    posts = post_list_request()
    print(list(filter(lambda x: x["user"]["username"]=="admin", posts)))
    return render_template("posts.html", form=form, posts=posts)

@app.route("/post-create-ajax", methods=["POST"])
def post_create_ajax():
    description = request.form.get("description")
    post = post_create_request(description=description)
    return jsonify(post), 201

if __name__=="__main__":
    app.run()
