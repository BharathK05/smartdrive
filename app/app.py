"""SmartDrive: a tiny Google Drive clone.

Everything is stored in one S3 bucket:
    files/<owner>/<id>-<name>   the uploaded files
    db/users.json               email -> password hash
    db/files.json               file id -> file record (owner, AI tags, sharing)
"""
import io
import json
import os
import secrets
import threading
import uuid
from datetime import datetime, timezone
from functools import wraps

import boto3
from flask import Flask, abort, flash, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from ai import auto_tags

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-secret"),
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10 MB upload limit
    SESSION_COOKIE_SAMESITE="Lax",
)

BUCKET = os.environ.get("S3_BUCKET", "")
USERS = "db/users.json"
FILES = "db/files.json"

s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
lock = threading.Lock()  # only one request at a time may change the JSON files


# ---------- S3 storage helpers ----------

def load_json(key):
    try:
        return json.loads(s3.get_object(Bucket=BUCKET, Key=key)["Body"].read())
    except s3.exceptions.NoSuchKey:
        return {}


def save_json(key, data):
    s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(data, indent=2), ContentType="application/json")


def put_file(key, data, content_type):
    s3.put_object(Bucket=BUCKET, Key=key, Body=data, ContentType=content_type)


def get_file(key):
    return s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()


def delete_file(key):
    s3.delete_object(Bucket=BUCKET, Key=key)


# ---------- helpers ----------

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def owned(files, file_id):
    """Return the file record if the logged-in user owns it, otherwise 404."""
    record = files.get(file_id)
    if not record or record["owner"] != session["email"]:
        abort(404)
    return record


def send_record(record):
    return send_file(io.BytesIO(get_file(record["key"])), mimetype=record["type"],
                     as_attachment=True, download_name=record["name"])


@app.template_filter("filesize")
def filesize(n):
    if n < 1024:
        return f"{n} B"
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


@app.template_filter("nicedate")
def nicedate(iso):
    return datetime.fromisoformat(iso).strftime("%d %b %Y").lstrip("0")


@app.errorhandler(413)
def too_large(_error):
    flash("That file is too big. The limit is 10 MB.", "error")
    return redirect(url_for("index"))


# ---------- auth ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or len(password) < 6:
            flash("Enter an email and a password of at least 6 characters.", "error")
            return render_template("register.html", email=email)
        with lock:
            users = load_json(USERS)
            if email in users:
                flash("That email already has an account. Sign in instead.", "error")
                return render_template("register.html", email=email)
            users[email] = {"password": generate_password_hash(password)}
            save_json(USERS, users)
        session["email"] = email
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = load_json(USERS).get(email)
        if user and check_password_hash(user["password"], request.form.get("password", "")):
            session["email"] = email
            return redirect(url_for("index"))
        flash("Wrong email or password. Try again.", "error")
        return render_template("login.html", email=email)
    return render_template("login.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- files ----------

@app.get("/")
@login_required
def index():
    me = session["email"]
    view = "shared" if request.args.get("view") == "shared" else "mine"
    q = request.args.get("q", "").strip().lower()
    everything = sorted(load_json(FILES).values(), key=lambda f: f["uploaded"], reverse=True)
    mine = [f for f in everything if f["owner"] == me]
    files = mine if view == "mine" else [f for f in everything if me in f["shared_with"]]
    if q:
        files = [f for f in files if q in f["name"].lower() or any(q in t.lower() for t in f["tags"])]
    return render_template("index.html", files=files, view=view, q=q, used=sum(f["size"] for f in mine))


@app.post("/upload")
@login_required
def upload():
    incoming = request.files.get("file")
    if not incoming or not incoming.filename:
        flash("Choose a file to upload first.", "error")
        return redirect(url_for("index"))

    data = incoming.read()
    file_id = uuid.uuid4().hex[:12]
    key = f"files/{session['email']}/{file_id}-{secure_filename(incoming.filename) or 'file'}"
    content_type = incoming.mimetype or "application/octet-stream"
    put_file(key, data, content_type)

    record = {
        "id": file_id,
        "owner": session["email"],
        "name": incoming.filename,
        "key": key,
        "size": len(data),
        "type": content_type,
        "tags": auto_tags(incoming.filename, data),
        "shared_with": [],
        "public_token": None,
        "uploaded": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with lock:
        files = load_json(FILES)
        files[file_id] = record
        save_json(FILES, files)
    flash(f"Uploaded {incoming.filename}.")
    return redirect(url_for("index"))


@app.get("/download/<file_id>")
@login_required
def download(file_id):
    record = load_json(FILES).get(file_id)
    if not record:
        abort(404)
    if session["email"] != record["owner"] and session["email"] not in record["shared_with"]:
        abort(403)
    return send_record(record)


@app.post("/delete/<file_id>")
@login_required
def delete(file_id):
    with lock:
        files = load_json(FILES)
        record = owned(files, file_id)
        delete_file(record["key"])
        del files[file_id]
        save_json(FILES, files)
    flash(f"Deleted {record['name']}.")
    return redirect(url_for("index"))


# ---------- sharing ----------

@app.post("/share/<file_id>")
@login_required
def share(file_id):
    email = request.form.get("email", "").strip().lower()
    back_to_panel = redirect(url_for("index", _anchor=f"share-{file_id}"))
    with lock:
        if email not in load_json(USERS):
            flash(f"There is no SmartDrive user called {email}. Ask them to create an account first.", "error")
            return back_to_panel
        files = load_json(FILES)
        record = owned(files, file_id)
        if email == record["owner"]:
            flash("You already own this file.", "error")
            return back_to_panel
        if email not in record["shared_with"]:
            record["shared_with"].append(email)
            save_json(FILES, files)
    flash(f"Shared {record['name']} with {email}.")
    return back_to_panel


@app.post("/link/<file_id>")
@login_required
def toggle_link(file_id):
    with lock:
        files = load_json(FILES)
        record = owned(files, file_id)
        record["public_token"] = None if record["public_token"] else secrets.token_urlsafe(16)
        save_json(FILES, files)
    flash("Anyone with the link can now download this file." if record["public_token"] else "Link turned off.")
    return redirect(url_for("index", _anchor=f"share-{file_id}"))


@app.get("/s/<token>")
def public_download(token):
    for record in load_json(FILES).values():
        if record["public_token"] and secrets.compare_digest(record["public_token"], token):
            return send_record(record)
    abort(404)


if __name__ == "__main__":
    app.run(debug=True)
