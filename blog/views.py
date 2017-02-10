from flask import render_template, request, redirect, url_for
import datetime
from . import app
from .database import session, Entry

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
def add_entry_get():
    return render_template("add_entry.html")
    
@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<int:id>/edit", methods=["GET"])
def edit_entry_get(id):
    entries = session.query(Entry).filter_by(id=id)
    return render_template("edit_entry.html",
    entries = entries
    )
    
@app.route("/entry/<int:id>/edit", methods=["POST"])
def edit_entry_post(id):
    title=request.form["title"],
    content=request.form["content"]
    update_record = session.query(Entry).filter_by(id=id).first()
    update_record.title = title
    update_record.content = content
    session.commit()
    return redirect(url_for("edit_entry_post", id=id))

@app.route("/entry/<int:id>/delete", methods=["GET"])
def delete_entry_get(id):
    entries = session.query(Entry).filter_by(id=id)
    return render_template("delete_entry.html",
    entries = entries
    )

@app.route("/entry/<int:id>/delete", methods=["POST"])
def delete_entry_post(id):
    delete_record = session.query(Entry).filter_by(id=id).first()
    session.delete(delete_record)
    session.commit()
    return redirect(url_for("entries"))