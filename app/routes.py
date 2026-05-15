from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import get_db, User
import bcrypt
import os

main = Blueprint('main', __name__)

# HOME
@main.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM content ORDER BY created_at DESC")
    movies = cursor.fetchall()
    db.close()
    return render_template('index.html', movies=movies)

# REGISTER
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'user')",
                         (username, email, hashed.decode('utf-8')))
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('main.login'))
        except:
            flash('Email already exists!', 'danger')
        finally:
            db.close()
    return render_template('register.html')

# LOGIN
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        db.close()
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            user_obj = User(user['id'], user['username'], user['email'], user['role'])
            login_user(user_obj)
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials!', 'danger')
    return render_template('login.html')

# LOGOUT
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# USER DASHBOARD
@main.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM content ORDER BY created_at DESC")
    movies = cursor.fetchall()
    db.close()
    return render_template('dashboard.html', movies=movies)

# WATCH PAGE
@main.route('/watch/<int:id>')
@login_required
def watch(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM content WHERE id = %s", (id,))
    movie = cursor.fetchone()
    db.close()
    return render_template('watch.html', movie=movie)

# ADMIN DASHBOARD
@main.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM content ORDER BY created_at DESC")
    movies = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()['count']
    db.close()
    return render_template('admin.html', movies=movies, user_count=user_count)

# ADMIN ADD CONTENT
@main.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_content():
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        genre = request.form['genre']
        youtube_url = request.form['youtube_url']
        thumbnail = request.form['thumbnail']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO content (title, description, genre, youtube_url, thumbnail) VALUES (%s, %s, %s, %s, %s)",
                      (title, description, genre, youtube_url, thumbnail))
        db.commit()
        db.close()
        flash('Content added!', 'success')
        return redirect(url_for('main.admin'))
    return render_template('add_content.html')

# ADMIN DELETE CONTENT
@main.route('/admin/delete/<int:id>')
@login_required
def delete_content(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.dashboard'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM content WHERE id = %s", (id,))
    db.commit()
    db.close()
    flash('Content deleted!', 'success')
    return redirect(url_for('main.admin'))

# QUICK SWITCH
@main.route('/switch/<role>')
def switch(role):
    db = get_db()
    cursor = db.cursor()
    if role == 'admin':
        cursor.execute("SELECT * FROM users WHERE role='admin' LIMIT 1")
    else:
        cursor.execute("SELECT * FROM users WHERE role='user' LIMIT 1")
    user = cursor.fetchone()
    db.close()
    if user:
        user_obj = User(user['id'], user['username'], user['email'], user['role'])
        login_user(user_obj)
        flash(f'Switched to {role} account!', 'success')
    return redirect(url_for('main.dashboard'))
