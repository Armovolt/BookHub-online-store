from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flasgger import Swagger
from flask_cors import CORS
from models import db, Book, Customer, Order, OrderItem, Feedback, User
from api.routes import api_bp
from auth.routes import auth_bp
from datetime import datetime
import os
import secrets

app = Flask(__name__)

# Генерація безпечного секретного ключа
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SWAGGER'] = {
    'title': 'BookHub API Documentation',
    'description': 'RESTful API для онлайн книжкового магазину BookHub. Лабораторна робота №5',
    'uiversion': 3,
    'specs_route': '/api/docs/',
    'tags': [
        {
            'name': 'Books',
            'description': 'Операції з книгами'
        },
        {
            'name': 'Users',
            'description': 'Операції з користувачами'
        },
        {
            'name': 'Cart',
            'description': 'Операції з кошиком'
        },
        {
            'name': 'Orders',
            'description': 'Операції з замовленнями'
        },
        {
            'name': 'Reviews',
            'description': 'Операції з відгуками'
        },
        {
            'name': 'Auth',
            'description': 'Авторизація та реєстрація'
        },
        {
            'name': 'Search',
            'description': 'Пошук книг'
        },
        {
            'name': 'Statistics',
            'description': 'Статистика системи'
        }
    ],
    'specs': [
        {
            'endpoint': 'apispec',
            'route': '/api/docs/apispec.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'static_url_path': '/api/docs/static',
    'swagger_ui': True,
    'swagger_ui_bundle_js': '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js',
    'swagger_ui_standalone_preset_js': '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js',
    'jquery_js': '//unpkg.com/jquery@2.2.4/dist/jquery.min.js',
    'swagger_ui_css': '//unpkg.com/swagger-ui-dist@3/swagger-ui.css'
}

# Ініціалізація бази даних
db.init_app(app)

# Ініціалізація CORS для API
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True
    }
})

# Ініціалізація Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Реєстрація Blueprints
app.register_blueprint(api_bp)
app.register_blueprint(auth_bp)

# Ініціалізація Swagger
swagger = Swagger(app)

# Функція для створення тестових даних
def init_test_data():
    with app.app_context():
        # Створюємо адміна, якщо його немає
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@bookhub.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print('Адмін створений: логін=admin, пароль=admin123')
        
        # Додаємо тестові книги, якщо їх немає
        if Book.query.count() == 0:
            sample_books = [
                Book(
                    title="Хіба що хтось стукне у двері", 
                    author="Стівен Кінг", 
                    description="Збірник оповідань від короля жахів. 12 історій, що вражають глибиною та непередбачуваністю.",
                    price=350.0, 
                    category="Фантастика",
                    stock_quantity=15,
                    in_stock=True
                ),
                Book(
                    title="Проєкт 'Розі'", 
                    author="Енді Вейр", 
                    description="Наукова фантастика від автора 'Марсіянина'. Захоплива історія про космічні пригоди.",
                    price=280.0, 
                    category="Фантастика",
                    stock_quantity=20,
                    in_stock=True
                ),
                Book(
                    title="Чотири вітри", 
                    author="Крістін Ханна", 
                    description="Історична драма про силу родинних зв'язків у складні часи.",
                    price=320.0, 
                    category="Драма",
                    stock_quantity=10,
                    in_stock=True
                ),
                Book(
                    title="Гаррі Поттер і філософський камінь", 
                    author="Дж. К. Роулінг", 
                    description="Перша книга знаменитої серії про молодого чарівника.",
                    price=290.0, 
                    category="Фентезі",
                    stock_quantity=25,
                    in_stock=True
                ),
                Book(
                    title="Війна і мир", 
                    author="Лев Толстой", 
                    description="Класика світової літератури про долі людей під час наполеонівських воєн.",
                    price=420.0, 
                    category="Класика",
                    stock_quantity=8,
                    in_stock=True
                )
            ]
            db.session.bulk_save_objects(sample_books)
            print('Тестові книги додані до бази даних!')
        
        # Створюємо звичайного користувача для тестування
        test_user = User.query.filter_by(username='user').first()
        if not test_user:
            test_user = User(
                username='user',
                email='user@bookhub.com',
                is_admin=False
            )
            test_user.set_password('user123')
            db.session.add(test_user)
            print('Тестовий користувач створений: логін=user, пароль=user123')
        
        # Додаємо тестові відгуки
        if Feedback.query.count() == 0 and Book.query.count() > 0:
            test_feedbacks = [
                Feedback(
                    name="Анна",
                    email="anna@example.com",
                    message="Чудова книга! Рекомендую всім любителям фантастики.",
                    rating=5,
                    book_id=1,
                    is_approved=True
                ),
                Feedback(
                    name="Олексій",
                    email="oleksiy@example.com",
                    message="Дуже цікава історія, не міг відірватись.",
                    rating=4,
                    book_id=2,
                    is_approved=True
                ),
                Feedback(
                    name="Марія",
                    email="maria@example.com",
                    message="Відмінний сервіс та швидка доставка. Дякую!",
                    rating=5,
                    book_id=None,
                    is_approved=True
                )
            ]
            db.session.bulk_save_objects(test_feedbacks)
            print('Тестові відгуки додані до бази даних!')
        
        db.session.commit()

# Створення таблиць та тестових даних
with app.app_context():
    db.create_all()
    init_test_data()

# ========== ОСНОВНІ МАРШРУТИ ==========
@app.route('/')
def index():
    featured_books = Book.query.filter_by(in_stock=True).limit(4).all()
    return render_template('index.html', featured_books=featured_books, user=current_user)

@app.route('/about')
def about():
    return render_template('about.html', user=current_user)

@app.route('/books')
def books():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Book.query.filter_by(in_stock=True)
    
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))
    
    books_list = query.all()
    categories = db.session.query(Book.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('books.html', books=books_list, categories=categories, 
                         selected_category=category, search_query=search, user=current_user)

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        # Перевіряємо авторизацію
        if not current_user.is_authenticated:
            flash('Для залишення відгуку потрібно увійти.', 'danger')
            return redirect(url_for('auth.login', reason='review'))
        
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        rating = request.form.get('rating', 5)
        book_id = request.form.get('book_id')
        
        # Використовуємо дані авторизованого користувача
        name = current_user.username
        email = current_user.email
        
        # Валідація даних
        errors = []
        if not message:
            errors.append("Будь ласка, введіть текст відгуку")
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            approved_feedbacks = Feedback.query.filter_by(is_approved=True).order_by(Feedback.created_at.desc()).all()
            books_list = Book.query.all()
            return render_template('reviews.html', feedbacks=approved_feedbacks, books=books_list, user=current_user)
        
        try:
            rating = int(rating)
        except:
            rating = 5
        
        if rating < 1:
            rating = 1
        if rating > 5:
            rating = 5
        
        feedback = Feedback(
            name=name,
            email=email if email else None,
            message=message,
            rating=rating,
            book_id=book_id if book_id else None,
            user_id=current_user.id  # Обов'язково прив'язуємо до користувача
        )
        
        db.session.add(feedback)
        db.session.commit()
        flash('Дякуємо за ваш відгук! Він буде опублікований після перевірки.', 'success')
        return redirect(url_for('reviews'))
    
    approved_feedbacks = Feedback.query.filter_by(is_approved=True).order_by(Feedback.created_at.desc()).all()
    books_list = Book.query.all()
    return render_template('reviews.html', feedbacks=approved_feedbacks, books=books_list, user=current_user)

# ========== МАГАЗИН (API-based) ==========
@app.route('/cart')
@login_required
def cart_page():
    """Сторінка кошика (використовує API для отримання даних)"""
    try:
        # Імпортуємо тут, щоб уникнути циркулярних імпортів
        from api.routes import get_cart
        cart_response = get_cart()
        
        if cart_response.status_code != 200:
            cart_data = {'success': False, 'cart': []}
        else:
            cart_data = cart_response.get_json()
        
        if cart_data.get('success'):
            cart_items = cart_data.get('cart', [])
            total = cart_data.get('total', 0)
        else:
            cart_items = []
            total = 0
            
        return render_template('shop/cart.html', cart_items=cart_items, total=total, user=current_user)
    except Exception as e:
        print(f"Error loading cart page: {e}")
        return render_template('shop/cart.html', cart_items=[], total=0, user=current_user)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформлення замовлення"""
    # Перевіряємо кошик через API
    from api.routes import get_cart
    cart_response = get_cart()
    
    if cart_response.status_code != 200:
        flash('Ваш кошик порожній!', 'warning')
        return redirect(url_for('books'))
    
    cart_data = cart_response.get_json()
    
    if not cart_data.get('success') or not cart_data.get('cart'):
        flash('Ваш кошик порожній!', 'warning')
        return redirect(url_for('books'))
    
    cart_items = cart_data.get('cart', [])
    total = cart_data.get('total', 0)
    
    if request.method == 'POST':
        # Створення клієнта (якщо ще немає)
        customer = Customer.query.filter_by(email=current_user.email).first()
        if not customer:
            customer = Customer(
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form.get('phone', ''),
                address=request.form['address'],
                user_id=current_user.id
            )
            db.session.add(customer)
        else:
            customer.name = request.form['name']
            customer.phone = request.form.get('phone', '')
            customer.address = request.form['address']
        
        db.session.flush()
        
        # Створення замовлення
        order = Order(
            customer_id=customer.id,
            user_id=current_user.id,
            total_amount=total,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()
        
        # Додавання товарів до замовлення
        for item in cart_items:
            book = Book.query.get(item['book']['id'])
            if book:
                order_item = OrderItem(
                    order_id=order.id,
                    book_id=book.id,
                    quantity=item['quantity'],
                    price=book.price
                )
                db.session.add(order_item)
                
                # Оновлення кількості на складі
                book.stock_quantity -= item['quantity']
                if book.stock_quantity <= 0:
                    book.in_stock = False
        
        # Очищення кошика через API
        from api.routes import clear_cart
        clear_cart()
        
        db.session.commit()
        
        flash(f'Замовлення #{order.id} успішно створено! Дякуємо за покупку!', 'success')
        return redirect(url_for('index'))
    
    return render_template('shop/checkout.html', cart_items=cart_items, total=total, user=current_user)

# ========== АДМІН-ПАНЕЛЬ ==========
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    stats = {
        'total_books': Book.query.count(),
        'total_orders': Order.query.count(),
        'total_reviews': Feedback.query.count(),
        'total_customers': Customer.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count()
    }
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    pending_feedbacks = Feedback.query.filter_by(is_approved=False).count()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_orders=recent_orders,
                         pending_feedbacks=pending_feedbacks,
                         user=current_user)

@app.route('/admin/feedback')
@login_required
def admin_feedback():
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin/feedback.html', feedbacks=feedbacks, user=current_user)

@app.route('/admin/approve_feedback/<int:feedback_id>')
@login_required
def approve_feedback(feedback_id):
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    feedback = Feedback.query.get_or_404(feedback_id)
    feedback.is_approved = True
    db.session.commit()
    flash('Відгук схвалено', 'success')
    return redirect(url_for('admin_feedback'))

@app.route('/admin/delete_feedback/<int:feedback_id>')
@login_required
def delete_feedback(feedback_id):
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Відгук видалено', 'success')
    return redirect(url_for('admin_feedback'))

@app.route('/admin/books')
@login_required
def admin_books():
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    books_list = Book.query.all()
    return render_template('admin/books.html', books=books_list, user=current_user)

@app.route('/admin/add_book', methods=['GET', 'POST'])
@login_required
def admin_add_book():
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            description=request.form['description'],
            price=float(request.form['price']),
            category=request.form['category'],
            stock_quantity=int(request.form['stock_quantity']),
            in_stock=bool(request.form.get('in_stock')),
            image_url=request.form.get('image_url', '/static/images/default-book.jpg')
        )
        db.session.add(book)
        db.session.commit()
        flash('Книгу додано успішно!', 'success')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/add_book.html', user=current_user)

@app.route('/admin/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_book(book_id):
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.description = request.form['description']
        book.price = float(request.form['price'])
        book.category = request.form['category']
        book.stock_quantity = int(request.form['stock_quantity'])
        book.in_stock = bool(request.form.get('in_stock'))
        book.image_url = request.form.get('image_url', '/static/images/default-book.jpg')
        
        db.session.commit()
        flash(f'Книгу "{book.title}" успішно оновлено!', 'success')
        return redirect(url_for('admin_books'))
    
    return render_template('admin/edit_book.html', book=book, user=current_user)

@app.route('/admin/delete_book/<int:book_id>')
@login_required
def admin_delete_book(book_id):
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(book_id)
    title = book.title
    
    # Перевіряємо, чи книга не в замовленнях
    order_items = OrderItem.query.filter_by(book_id=book_id).first()
    if order_items:
        flash('Неможливо видалити книгу, оскільки вона є в замовленнях!', 'danger')
        return redirect(url_for('admin_books'))
    
    db.session.delete(book)
    db.session.commit()
    flash(f'Книгу "{title}" успішно видалено!', 'success')
    return redirect(url_for('admin_books'))

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, user=current_user)

@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash('Статус замовлення оновлено!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/customers')
@login_required
def admin_customers():
    if not current_user.is_admin:
        flash('Доступ заборонено!', 'danger')
        return redirect(url_for('index'))
    
    customers = Customer.query.all()
    return render_template('admin/customers.html', customers=customers, user=current_user)

# ========== API ДОКУМЕНТАЦІЯ ==========
@app.route('/api')
def api_docs():
    return redirect('/api/docs')

# ========== ПОМИЛКИ ==========
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', user=current_user), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', user=current_user), 500

# Middleware для оновлення сесії
@app.before_request
def make_session_permanent():
    session.permanent = True

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')