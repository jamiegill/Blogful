from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
import datetime
from . import app
from .database import session, Entry, User

@app.route("/")
@app.route("/page/<int:page>")
@app.route("/page/<int:page>/limit=<float:paginate_by>")
@app.route("/page/<int:page>/limit=<int:paginate_by>")
def entries(page=1, paginate_by=10):
    # Zero-indexed page
    if isinstance(paginate_by, float):
        paginate_by=10
    page_index = page - 1
    
    count = session.query(Entry).count()
    
    start = page_index * paginate_by
    end = start + paginate_by
    
    total_pages = (count - 1) // paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0
    
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]
    
    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        paginate_by=paginate_by
    )
    
@app.route("/entry/<int:id>")
def single_entry(id):
    entries = session.query(Entry).filter_by(id=id)
    return render_template("single_entry.html",
         entries=entries
    )
    
    
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")
    
@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<int:id>/edit", methods=["GET"])
@login_required
def edit_entry_get(id):
    entries = session.query(Entry).filter_by(id=id)
    return render_template("edit_entry.html",
    entries = entries
    )
    
@app.route("/entry/<int:id>/edit", methods=["POST"])
@login_required
def edit_entry_post(id):
    current_entry_id = session.query(User.id).join(Entry).filter(Entry.id==id).first()[0]
    if current_entry_id != current_user.id:
        flash ("You didn't create this post so you cannot edit/delete the post", "danger")
        return redirect(url_for("edit_entry_post", id=id))
    else:
        title=request.form["title"],
        content=request.form["content"]
        update_record = session.query(Entry).filter_by(id=id).first()
        update_record.title = title
        update_record.content = content
        session.commit()
        return redirect(url_for("edit_entry_post", id=id))

@app.route("/entry/<int:id>/delete", methods=["GET"])
@login_required
def delete_entry_get(id):
    entries = session.query(Entry).filter_by(id=id)
    return render_template("delete_entry.html",
    entries = entries
    )

@app.route("/entry/<int:id>/delete", methods=["POST"])
@login_required
def delete_entry_post(id):
    current_entry_id = session.query(User.id).join(Entry).filter(Entry.id==id).first()[0]
    if current_entry_id != current_user.id:
        flash ("You didn't create this post so you cannot edit/delete the post", "danger")
        return redirect(url_for("edit_entry_post", id=id))
    else:
        delete_record = session.query(Entry).filter_by(id=id).first()
        session.delete(delete_record)
        session.commit()
        return redirect(url_for("entries"))
    
@app.route("/login", methods=['GET'])
def login_get():
    return render_template("login.html")
    
@app.route("/login", methods=['POST'])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
        
    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
    
@app.route("/logout", methods=['GET'])
def logout_get():
    logout_user()
    return redirect(url_for("entries"))
        