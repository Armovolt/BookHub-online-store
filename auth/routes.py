from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Order
import re

auth_bp = Blueprint('auth', __name__)

# ========== ВЕБ-ІНТЕРФЕЙС ==========
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Сторінка входу для користувачів (HTML форма)"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Отримуємо параметр reason для відображення спеціального повідомлення
    reason = request.args.get('reason', '')
    next_page = request.args.get('next', '')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Вітаємо, {username}!', 'success')
            
            # Перевіряємо чи є сторінка для повернення
            if request.form.get('next'):
                return redirect(request.form.get('next'))
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Невірний логін або пароль!', 'danger')
    
    return render_template('auth/login.html', reason=reason, next_page=next_page)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Сторінка реєстрації для користувачів (HTML форма)"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Валідація
        errors = []
        
        if len(username) < 3:
            errors.append('Логін повинен містити мінімум 3 символи')
        
        if password != confirm_password:
            errors.append('Паролі не співпадають')
        
        if len(password) < 6:
            errors.append('Пароль повинен містити мінімум 6 символів')
        
        # Перевірка email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            errors.append('Невірний формат email')
        
        # Перевірка унікальності
        if User.query.filter_by(username=username).first():
            errors.append('Цей логін вже використовується')
        
        if User.query.filter_by(email=email).first():
            errors.append('Цей email вже використовується')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')
        
        # Створення користувача
        user = User(
            username=username,
            email=email,
            is_admin=False  # Звичайний користувач
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Реєстрація успішна! Тепер ви можете увійти.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Вихід з системи"""
    logout_user()
    flash('Ви вийшли з системи', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Сторінка профілю користувача"""
    # Підраховуємо кількість замовлень користувача
    orders_count = Order.query.filter_by(user_id=current_user.id).count()
    return render_template('auth/profile.html', user=current_user, orders_count=orders_count)