from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from flasgger import swag_from
from models import db, Book, Order, Feedback, Customer, User, OrderItem
from datetime import datetime

# ========== Створення Blueprint ==========
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# ========== КНИГИ ==========
@api_bp.route('/books', methods=['GET'])
@swag_from({
    'tags': ['Books'],
    'summary': 'Отримати всі книги',
    'description': 'Повертає список всіх книг у системі',
    'responses': {
        200: {
            'description': 'Успішно отримано список книг',
            'examples': {
                'application/json': {
                    'success': True,
                    'count': 5,
                    'books': [
                        {
                            'id': 1,
                            'title': 'Назва книги',
                            'author': 'Автор',
                            'price': 299.99,
                            'category': 'Фантастика',
                            'stock_quantity': 10,
                            'in_stock': True
                        }
                    ]
                }
            }
        }
    }
})
def get_books():
    """Отримати всі книги"""
    books = Book.query.all()
    return jsonify({
        'success': True,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })

@api_bp.route('/books/<int:book_id>', methods=['GET'])
@swag_from({
    'tags': ['Books'],
    'summary': 'Отримати деталі книги',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID книги'
        }
    ],
    'responses': {
        200: {
            'description': 'Успішно отримано деталі книги',
            'examples': {
                'application/json': {
                    'success': True,
                    'book': {
                        'id': 1,
                        'title': 'Назва книги',
                        'author': 'Автор',
                        'description': 'Опис книги',
                        'price': 299.99,
                        'category': 'Фантастика',
                        'stock_quantity': 10,
                        'in_stock': True
                    }
                }
            }
        },
        404: {
            'description': 'Книгу не знайдено'
        }
    }
})
def get_book(book_id):
    """Отримати деталі книги"""
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'error': 'Книгу не знайдено'}), 404
    return jsonify({'success': True, 'book': book.to_dict()})

@api_bp.route('/books', methods=['POST'])
@login_required
@swag_from({
    'tags': ['Books'],
    'summary': 'Створити нову книгу',
    'description': 'Створює нову книгу (тільки для адміністраторів)',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Нова книга'},
                    'author': {'type': 'string', 'example': 'Новий автор'},
                    'price': {'type': 'number', 'example': 299.99},
                    'description': {'type': 'string', 'example': 'Опис нової книги'},
                    'category': {'type': 'string', 'example': 'Фантастика'},
                    'stock_quantity': {'type': 'integer', 'example': 10},
                    'image_url': {'type': 'string', 'example': '/static/images/book.jpg'}
                },
                'required': ['title', 'author', 'price']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Книгу успішно створено',
            'examples': {
                'application/json': {
                    'success': True,
                    'book': {
                        'id': 1,
                        'title': 'Нова книга',
                        'author': 'Новий автор',
                        'price': 299.99
                    }
                }
            }
        },
        400: {
            'description': 'Неправильний запит'
        },
        403: {
            'description': 'Доступ заборонено'
        }
    }
})
def create_book():
    """Створити нову книгу (тільки адмін)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    data = request.get_json()
    if not all(key in data for key in ['title', 'author', 'price']):
        return jsonify({'success': False, 'error': 'Недостатньо даних'}), 400
    
    book = Book(
        title=data['title'],
        author=data['author'],
        price=data['price'],
        stock_quantity=data.get('stock_quantity', 10),
        description=data.get('description', ''),
        category=data.get('category'),
        image_url=data.get('image_url', '/static/images/default-book.jpg')
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({'success': True, 'book': book.to_dict()}), 201

@api_bp.route('/books/<int:book_id>', methods=['PUT'])
@login_required
@swag_from({
    'tags': ['Books'],
    'summary': 'Оновити книгу',
    'description': 'Оновлює інформацію про книгу (тільки для адміністраторів)',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID книги для оновлення'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'example': 'Оновлена назва'},
                    'author': {'type': 'string', 'example': 'Оновлений автор'},
                    'price': {'type': 'number', 'example': 349.99},
                    'description': {'type': 'string', 'example': 'Оновлений опис'},
                    'category': {'type': 'string', 'example': 'Драма'},
                    'stock_quantity': {'type': 'integer', 'example': 15},
                    'image_url': {'type': 'string', 'example': '/static/images/updated.jpg'},
                    'in_stock': {'type': 'boolean', 'example': True}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Книгу успішно оновлено',
            'examples': {
                'application/json': {
                    'success': True,
                    'book': {
                        'id': 1,
                        'title': 'Оновлена назва',
                        'author': 'Оновлений автор',
                        'price': 349.99
                    }
                }
            }
        },
        400: {
            'description': 'Неправильний запит'
        },
        403: {
            'description': 'Доступ заборонено'
        },
        404: {
            'description': 'Книгу не знайдено'
        }
    }
})
def update_book(book_id):
    """Оновити книгу (тільки адмін)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'error': 'Книгу не знайдено'}), 404
    
    data = request.get_json()
    
    # Оновлюємо тільки поля, які були передані
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'price' in data:
        book.price = data['price']
    if 'stock_quantity' in data:
        book.stock_quantity = data['stock_quantity']
    if 'description' in data:
        book.description = data['description']
    if 'category' in data:
        book.category = data['category']
    if 'image_url' in data:
        book.image_url = data['image_url']
    if 'in_stock' in data:
        book.in_stock = data['in_stock']
    
    db.session.commit()
    return jsonify({'success': True, 'book': book.to_dict()})

@api_bp.route('/books/<int:book_id>', methods=['DELETE'])
@login_required
@swag_from({
    'tags': ['Books'],
    'summary': 'Видалити книгу',
    'description': 'Видаляє книгу з системи з вибором опції для відгуків (тільки для адміністраторів)',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID книги для видалення'
        },
        {
            'name': 'delete_reviews',
            'in': 'query',
            'type': 'boolean',
            'required': False,
            'description': 'Видалити відгуки на книгу? (false = залишити відгуки, true = видалити відгуки)'
        }
    ],
    'responses': {
        200: {
            'description': 'Книгу успішно видалено',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Книгу видалено',
                    'deleted_reviews_count': 0
                }
            }
        },
        400: {
            'description': 'Неможливо видалити книгу (є в замовленнях)'
        },
        403: {
            'description': 'Доступ заборонено'
        },
        404: {
            'description': 'Книгу не знайдено'
        }
    }
})
def delete_book(book_id):
    """Видалити книгу з опціями для відгуків (тільки адмін)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'error': 'Книгу не знайдено'}), 404
    
    # Перевіряємо, чи книга не в замовленнях
    order_items = OrderItem.query.filter_by(book_id=book_id).first()
    if order_items:
        return jsonify({'success': False, 'error': 'Неможливо видалити книгу, оскільки вона є в замовленнях'}), 400
    
    # Отримуємо параметр delete_reviews з запиту
    delete_reviews_param = request.args.get('delete_reviews', 'false')
    delete_reviews = delete_reviews_param.lower() == 'true'
    
    # Обробка відгуків
    feedbacks = Feedback.query.filter_by(book_id=book_id).all()
    deleted_reviews_count = 0
    
    if delete_reviews:
        # Видалити всі відгуки на цю книгу
        for feedback in feedbacks:
            db.session.delete(feedback)
            deleted_reviews_count += 1
    else:
        # Залишити відгуки, але встановити book_id = None
        for feedback in feedbacks:
            feedback.book_id = None
    
    # Видаляємо книгу
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Книгу видалено',
        'deleted_reviews_count': deleted_reviews_count,
        'kept_reviews_count': len(feedbacks) - deleted_reviews_count
    })

# ========== КОШИК ==========
@api_bp.route('/cart', methods=['GET'])
@login_required
@swag_from({
    'tags': ['Cart'],
    'summary': 'Отримати вміст кошика',
    'description': 'Повертає поточний вміст кошика користувача',
    'responses': {
        200: {
            'description': 'Успішно отримано вміст кошика',
            'examples': {
                'application/json': {
                    'success': True,
                    'cart': [
                        {
                            'book': {
                                'id': 1,
                                'title': 'Назва книги',
                                'price': 299.99
                            },
                            'quantity': 2,
                            'total': 599.98
                        }
                    ],
                    'total': 599.98,
                    'count': 1,
                    'total_items': 2
                }
            }
        },
        401: {
            'description': 'Користувач не авторизований'
        }
    }
})
def get_cart():
    """Отримати вміст кошика"""
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    total_items = 0
    
    for book_id_str, quantity in cart.items():
        try:
            book_id = int(book_id_str)
            book = Book.query.get(book_id)
            if book:
                item_total = book.price * quantity
                cart_items.append({
                    'book': book.to_dict(),
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
                total_items += quantity
        except ValueError:
            continue
    
    return jsonify({
        'success': True,
        'cart': cart_items,
        'total': round(total, 2),
        'count': len(cart_items),
        'total_items': total_items
    })

@api_bp.route('/cart', methods=['POST'])
@login_required
@swag_from({
    'tags': ['Cart'],
    'summary': 'Додати книгу до кошика',
    'description': 'Додає книгу до кошика користувача',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'book_id': {'type': 'integer', 'example': 1},
                    'quantity': {'type': 'integer', 'example': 1}
                },
                'required': ['book_id', 'quantity']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Книга успішно додана до кошика',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Книга додана до кошика',
                    'cart': {},
                    'total_items': 0
                }
            }
        },
        400: {
            'description': 'Невірний запит'
        },
        401: {
            'description': 'Користувач не авторизований'
        },
        404: {
            'description': 'Книгу не знайдено'
        }
    }
})
def add_to_cart():
    """Додати книгу до кошика"""
    data = request.get_json()
    if 'book_id' not in data or 'quantity' not in data:
        return jsonify({'success': False, 'error': 'Необхідно вказати book_id та quantity'}), 400
    
    book_id = data['book_id']
    quantity = int(data['quantity'])
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'error': 'Книгу не знайдено'}), 404
    
    if not book.in_stock:
        return jsonify({'success': False, 'error': 'Книга не в наявності'}), 400
    
    if quantity < 1:
        return jsonify({'success': False, 'error': 'Кількість має бути не менше 1'}), 400
    
    # Перевірка кількості на складі
    current_cart_quantity = session.get('cart', {}).get(str(book_id), 0)
    requested_total = current_cart_quantity + quantity
    
    if book.stock_quantity < requested_total:
        return jsonify({
            'success': False, 
            'error': f'Недостатньо книг на складі. Доступно: {book.stock_quantity}, в кошику: {current_cart_quantity}'
        }), 400
    
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    book_id_str = str(book_id)
    
    if book_id_str in cart:
        cart[book_id_str] += quantity
    else:
        cart[book_id_str] = quantity
    
    session['cart'] = cart
    session.modified = True
    
    # Обчислюємо загальну кількість товарів
    total_items = sum(cart.values())
    
    return jsonify({
        'success': True,
        'message': 'Книга додана до кошика',
        'cart': cart,
        'total_items': total_items
    })

@api_bp.route('/cart/<int:book_id>', methods=['PUT'])
@login_required
@swag_from({
    'tags': ['Cart'],
    'summary': 'Оновити кількість книги в кошику',
    'description': 'Змінює кількість певної книги в кошику',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID книги'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'quantity': {'type': 'integer', 'example': 3}
                },
                'required': ['quantity']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Кількість успішно оновлена',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Кількість оновлена',
                    'cart': {}
                }
            }
        },
        400: {
            'description': 'Невірний запит'
        },
        401: {
            'description': 'Користувач не авторизований'
        },
        404: {
            'description': 'Книгу не знайдено'
        }
    }
})
def update_cart_item(book_id):
    """Оновити кількість книги в кошику"""
    data = request.get_json()
    if 'quantity' not in data:
        return jsonify({'success': False, 'error': 'Необхідно вказати quantity'}), 400
    
    quantity = int(data['quantity'])
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'error': 'Книгу не знайдено'}), 404
    
    if quantity < 0:
        return jsonify({'success': False, 'error': 'Кількість має бути не менше 0'}), 400
    
    if quantity > book.stock_quantity:
        return jsonify({'success': False, 'error': 'Недостатньо книг на складі'}), 400
    
    cart = session.get('cart', {})
    book_id_str = str(book_id)
    
    if quantity == 0:
        # Видалити товар з кошика
        if book_id_str in cart:
            del cart[book_id_str]
            session['cart'] = cart
            session.modified = True
            return jsonify({
                'success': True,
                'message': 'Книга видалена з кошика',
                'cart': cart
            })
        else:
            return jsonify({'success': False, 'error': 'Цієї книги немає в кошику'}), 404
    else:
        # Оновити кількість
        cart[book_id_str] = quantity
        session['cart'] = cart
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Кількість оновлена',
            'cart': cart
        })

@api_bp.route('/cart/<int:book_id>', methods=['DELETE'])
@login_required
@swag_from({
    'tags': ['Cart'],
    'summary': 'Видалити книгу з кошика',
    'description': 'Видаляє конкретну книгу з кошика користувача',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID книги'
        }
    ],
    'responses': {
        200: {
            'description': 'Книга успішно видалена з кошика',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Книга видалена з кошика',
                    'cart': {}
                }
            }
        },
        401: {
            'description': 'Користувач не авторизований'
        },
        404: {
            'description': 'Книгу не знайдено в кошику'
        }
    }
})
def remove_from_cart(book_id):
    """Видалити книгу з кошика"""
    cart = session.get('cart', {})
    book_id_str = str(book_id)
    
    if book_id_str in cart:
        del cart[book_id_str]
        session['cart'] = cart
        session.modified = True
        
        # Обчислюємо загальну кількість товарів
        total_items = sum(cart.values())
        
        return jsonify({
            'success': True,
            'message': 'Книга видалена з кошика',
            'cart': cart,
            'total_items': total_items
        })
    else:
        return jsonify({'success': False, 'error': 'Цієї книги немає в кошику'}), 404

@api_bp.route('/cart', methods=['DELETE'])
@login_required
@swag_from({
    'tags': ['Cart'],
    'summary': 'Очистити кошик',
    'description': 'Повністю очищає кошик користувача',
    'responses': {
        200: {
            'description': 'Кошик успішно очищено',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Кошик очищено'
                }
            }
        },
        401: {
            'description': 'Користувач не авторизований'
        }
    }
})
def clear_cart():
    """Очистити кошик"""
    session.pop('cart', None)
    return jsonify({
        'success': True,
        'message': 'Кошик очищено'
    })

# ========== КОРИСТУВАЧІ ==========
@api_bp.route('/users/me', methods=['GET'])
@login_required
@swag_from({
    'tags': ['Users'],
    'summary': 'Отримати профіль поточного користувача',
    'description': 'Повертає інформацію про поточного авторизованого користувача',
    'responses': {
        200: {
            'description': 'Успішно отримано профіль користувача',
            'examples': {
                'application/json': {
                    'success': True,
                    'user': {
                        'id': 1,
                        'username': 'user',
                        'email': 'user@bookhub.com',
                        'is_admin': False,
                        'created_at': '2024-01-01T00:00:00'
                    }
                }
            }
        },
        401: {
            'description': 'Користувач не авторизований'
        }
    }
})
def get_current_user_profile():
    """Отримати профіль поточного користувача"""
    return jsonify({'success': True, 'user': current_user.to_dict()})

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@swag_from({
    'tags': ['Users'],
    'summary': 'Отримати профіль користувача',
    'description': 'Отримує профіль користувача (адмін або власник профілю)',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID користувача'
        }
    ],
    'responses': {
        200: {
            'description': 'Успішно отримано профіль користувача',
            'examples': {
                'application/json': {
                    'success': True,
                    'user': {
                        'id': 1,
                        'username': 'user',
                        'email': 'user@bookhub.com',
                        'is_admin': False
                    }
                }
            }
        },
        403: {
            'description': 'Доступ заборонено'
        },
        404: {
            'description': 'Користувача не знайдено'
        }
    }
})
def get_user(user_id):
    """Отримати профіль користувача (адмін або власник)"""
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'Користувача не знайдено'}), 404
    
    return jsonify({'success': True, 'user': user.to_dict()})

# ========== ВІДГУКИ ==========
@api_bp.route('/reviews', methods=['GET'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Отримати всі відгуки',
    'description': 'Повертає список всіх відгуків у системі',
    'responses': {
        200: {
            'description': 'Успішно отримано список відгуків',
            'examples': {
                'application/json': {
                    'success': True,
                    'count': 5,
                    'reviews': [
                        {
                            'id': 1,
                            'name': 'Ім\'я користувача',
                            'message': 'Текст відгуку',
                            'rating': 5,
                            'book_title': 'Назва книги'
                        }
                    ]
                }
            }
        }
    }
})
def get_reviews():
    """Отримати всі відгуки"""
    reviews = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return jsonify({
        'success': True,
        'count': len(reviews),
        'reviews': [review.to_dict() for review in reviews]
    })

@api_bp.route('/reviews', methods=['POST'])
@login_required
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Створити новий відгук',
    'description': 'Створює новий відгук від імені поточного користувача',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Чудова книга!'},
                    'rating': {'type': 'integer', 'example': 5},
                    'book_id': {'type': 'integer', 'example': 1}
                },
                'required': ['message', 'rating']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Відгук успішно створено',
            'examples': {
                'application/json': {
                    'success': True,
                    'review': {
                        'id': 1,
                        'message': 'Чудова книга!',
                        'rating': 5
                    }
                }
            }
        },
        400: {
            'description': 'Неправильний запит'
        },
        401: {
            'description': 'Користувач не авторизований'
        }
    }
})
def create_review():
    """Створити новий відгук"""
    data = request.get_json()
    
    if 'message' not in data or 'rating' not in data:
        return jsonify({'success': False, 'error': 'Недостатньо даних'}), 400
    
    review = Feedback(
        user_id=current_user.id,
        name=current_user.username,
        email=current_user.email,
        message=data['message'],
        rating=data['rating'],
        book_id=data.get('book_id'),
        is_approved=False
    )
    
    db.session.add(review)
    db.session.commit()
    
    return jsonify({'success': True, 'review': review.to_dict()}), 201

@api_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@login_required
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Оновити відгук',
    'description': 'Оновлює відгук (тільки власник або адміністратор)',
    'parameters': [
        {
            'name': 'review_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID відгуку для оновлення'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Оновлений текст відгуку'},
                    'rating': {'type': 'integer', 'example': 4},
                    'book_id': {'type': 'integer', 'example': 2}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Відгук успішно оновлено',
            'examples': {
                'application/json': {
                    'success': True,
                    'review': {
                        'id': 1,
                        'message': 'Оновлений текст відгуку',
                        'rating': 4
                    }
                }
            }
        },
        403: {
            'description': 'Доступ заборонено'
        },
        404: {
            'description': 'Відгук не знайдено'
        }
    }
})
def update_review(review_id):
    """Оновити відгук (власник або адмін)"""
    review = Feedback.query.get(review_id)
    
    if not review:
        return jsonify({'success': False, 'error': 'Відгук не знайдено'}), 404
    
    if not current_user.is_admin and review.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    data = request.get_json()
    if 'message' in data:
        review.message = data['message']
    if 'rating' in data:
        review.rating = data['rating']
    if 'book_id' in data:
        review.book_id = data['book_id']
    
    db.session.commit()
    return jsonify({'success': True, 'review': review.to_dict()})

@api_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@login_required
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Видалити відгук',
    'description': 'Видаляє відгук (тільки власник або адміністратор)',
    'parameters': [
        {
            'name': 'review_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID відгуку для видалення'
        }
    ],
    'responses': {
        200: {
            'description': 'Відгук успішно видалено',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Відгук видалено'
                }
            }
        },
        403: {
            'description': 'Доступ заборонено'
        },
        404: {
            'description': 'Відгук не знайдено'
        }
    }
})
def delete_review(review_id):
    """Видалити відгук (власник або адмін)"""
    review = Feedback.query.get(review_id)
    
    if not review:
        return jsonify({'success': False, 'error': 'Відгук не знайдено'}), 404
    
    if not current_user.is_admin and review.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    db.session.delete(review)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Відгук видалено'})

# ========== ЗАМОВЛЕННЯ ==========
@api_bp.route('/orders', methods=['GET'])
@login_required
@swag_from({
    'tags': ['Orders'],
    'summary': 'Отримати замовлення користувача',
    'description': 'Повертає список замовлень (для адміністратора - всі, для користувача - тільки свої)',
    'responses': {
        200: {
            'description': 'Успішно отримано список замовлень',
            'examples': {
                'application/json': {
                    'success': True,
                    'count': 3,
                    'orders': [
                        {
                            'id': 1,
                            'total_amount': 599.98,
                            'status': 'pending',
                            'created_at': '2024-01-01T00:00:00'
                        }
                    ]
                }
            }
        },
        401: {
            'description': 'Користувач не авторизований'
        }
    }
})
def get_orders():
    """Отримати замовлення користувача"""
    if current_user.is_admin:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id).all()
    
    return jsonify({
        'success': True,
        'count': len(orders),
        'orders': [order.to_dict() for order in orders]
    })

@api_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
@swag_from({
    'tags': ['Orders'],
    'summary': 'Отримати деталі замовлення',
    'description': 'Отримує детальну інформацію про конкретне замовлення',
    'parameters': [
        {
            'name': 'order_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID замовлення'
        }
    ],
    'responses': {
        200: {
            'description': 'Успішно отримано деталі замовлення',
            'examples': {
                'application/json': {
                    'success': True,
                    'order': {
                        'id': 1,
                        'total_amount': 599.98,
                        'status': 'pending',
                        'items': [
                            {
                                'book_id': 1,
                                'quantity': 2,
                                'price': 299.99
                            }
                        ]
                    }
                }
            }
        },
        403: {
            'description': 'Доступ заборонено'
        },
        404: {
            'description': 'Замовлення не знайдено'
        }
    }
})
def get_order(order_id):
    """Отримати деталі замовлення"""
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'success': False, 'error': 'Замовлення не знайдено'}), 404
    
    if not current_user.is_admin and order.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    return jsonify({'success': True, 'order': order.to_dict()})

@api_bp.route('/orders', methods=['POST'])
@login_required
@swag_from({
    'tags': ['Orders'],
    'summary': 'Створити нове замовлення',
    'description': 'Створює нове замовлення на основі вмісту кошика користувача',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'book_id': {'type': 'integer'},
                                'quantity': {'type': 'integer'}
                            }
                        },
                        'example': [
                            {'book_id': 1, 'quantity': 2},
                            {'book_id': 2, 'quantity': 1}
                        ]
                    }
                },
                'required': ['items']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Замовлення успішно створено',
            'examples': {
                'application/json': {
                    'success': True,
                    'order': {
                        'id': 1,
                        'total_amount': 899.97,
                        'status': 'pending'
                    }
                }
            }
        },
        400: {
            'description': 'Невірний запит'
        },
        401: {
            'description': 'Користувач не авторизований'
        }
    }
})
def create_order():
    """Створити нове замовлення"""
    data = request.get_json()
    
    if 'items' not in data or not data['items']:
        return jsonify({'success': False, 'error': 'Немає товарів у замовленні'}), 400
    
    total_amount = 0
    items = data['items']
    
    for item in items:
        book = Book.query.get(item['book_id'])
        if not book:
            return jsonify({'success': False, 'error': f'Книга з ID {item["book_id"]} не знайдена'}), 404
        
        if book.stock_quantity < item['quantity']:
            return jsonify({'success': False, 'error': f'Недостатньо книг "{book.title}" на складі'}), 400
        
        total_amount += book.price * item['quantity']
    
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status='pending',
        created_at=datetime.utcnow()
    )
    db.session.add(order)
    db.session.flush()
    
    for item in items:
        book = Book.query.get(item['book_id'])
        order_item = OrderItem(
            order_id=order.id,
            book_id=book.id,
            quantity=item['quantity'],
            price=book.price
        )
        db.session.add(order_item)
        
        book.stock_quantity -= item['quantity']
        if book.stock_quantity <= 0:
            book.in_stock = False
    
    db.session.commit()
    
    return jsonify({'success': True, 'order': order.to_dict()}), 201

# ========== КЛІЄНТИ ==========
@api_bp.route('/customers', methods=['GET'])
@login_required
@swag_from({
    'tags': ['Customers'],
    'summary': 'Отримати список клієнтів',
    'description': 'Повертає список всіх клієнтів (тільки для адміністраторів)',
    'responses': {
        200: {
            'description': 'Успішно отримано список клієнтів',
            'examples': {
                'application/json': {
                    'success': True,
                    'count': 10,
                    'customers': [
                        {
                            'id': 1,
                            'name': 'Ім\'я клієнта',
                            'email': 'client@example.com',
                            'orders_count': 5
                        }
                    ]
                }
            }
        },
        403: {
            'description': 'Доступ заборонено'
        }
    }
})
def get_customers():
    """Отримати список клієнтів (тільки адмін)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    customers = Customer.query.all()
    return jsonify({
        'success': True,
        'count': len(customers),
        'customers': [customer.to_dict() for customer in customers]
    })

# ========== ПОШУК ==========
@api_bp.route('/search/books', methods=['GET'])
@swag_from({
    'tags': ['Search'],
    'summary': 'Пошук книг',
    'description': 'Шукає книги за назвою або автором',
    'parameters': [
        {
            'name': 'q',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Пошуковий запит'
        }
    ],
    'responses': {
        200: {
            'description': 'Успішно виконано пошук',
            'examples': {
                'application/json': {
                    'success': True,
                    'count': 3,
                    'query': 'пошуковий запит',
                    'books': [
                        {
                            'id': 1,
                            'title': 'Знайдена книга',
                            'author': 'Автор'
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Відсутній пошуковий запит'
        }
    }
})
def search_books():
    """Пошук книг за назвою або автором"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': False, 'error': 'Введіть пошуковий запит'}), 400
    
    books = Book.query.filter(
        (Book.title.contains(query)) | (Book.author.contains(query))
    ).all()
    
    return jsonify({
        'success': True,
        'count': len(books),
        'query': query,
        'books': [book.to_dict() for book in books]
    })

# ========== СТАТИСТИКА ==========
@api_bp.route('/stats', methods=['GET'])
@login_required
@swag_from({
    'tags': ['Statistics'],
    'summary': 'Отримати статистику системи',
    'description': 'Повертає статистичні дані про систему (тільки для адміністраторів)',
    'responses': {
        200: {
            'description': 'Успішно отримано статистику',
            'examples': {
                'application/json': {
                    'success': True,
                    'stats': {
                        'total_books': 50,
                        'total_orders': 100,
                        'total_reviews': 75,
                        'total_customers': 30,
                        'total_users': 40,
                        'pending_orders': 5,
                        'pending_reviews': 3
                    }
                }
            }
        },
        403: {
            'description': 'Доступ заборонено'
        }
    }
})
def get_stats():
    """Отримати статистику (тільки адмін)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403
    
    stats = {
        'total_books': Book.query.count(),
        'total_orders': Order.query.count(),
        'total_reviews': Feedback.query.count(),
        'total_customers': Customer.query.count(),
        'total_users': User.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'pending_reviews': Feedback.query.filter_by(is_approved=False).count()
    }
    
    return jsonify({'success': True, 'stats': stats})

# ========== АВТОРИЗАЦІЯ ==========
@api_bp.route('/auth/register', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Реєстрація користувача',
    'description': 'Реєструє нового користувача в системі',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'новийкористувач'},
                    'email': {'type': 'string', 'example': 'user@example.com'},
                    'password': {'type': 'string', 'example': 'securepassword123'}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Користувача успішно зареєстровано',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Користувача створено',
                    'user': {
                        'id': 1,
                        'username': 'новийкористувач',
                        'email': 'user@example.com'
                    }
                }
            }
        },
        400: {
            'description': 'Неправильний запит або користувач вже існує'
        }
    }
})
def api_register():
    """Реєстрація через API"""
    data = request.get_json()
    
    if not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({'success': False, 'error': 'Недостатньо даних'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'error': 'Цей логін вже використовується'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'error': 'Цей email вже використовується'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        is_admin=False
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Користувача створено',
        'user': user.to_dict()
    }), 201

@api_bp.route('/auth/login', methods=['POST'])
@swag_from({
    'tags': ['Auth'],
    'summary': 'Вхід користувача',
    'description': 'Автентифікує користувача та повертає токен сесії',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'user'},
                    'password': {'type': 'string', 'example': 'password123'},
                    'remember': {'type': 'boolean', 'example': False}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Вхід успішний',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Вхід успішний',
                    'user': {
                        'id': 1,
                        'username': 'user',
                        'email': 'user@example.com'
                    }
                }
            }
        },
        400: {
            'description': 'Неправильний запит'
        },
        401: {
            'description': 'Невірний логін або пароль'
        }
    }
})
def api_login():
    """Вхід через API"""
    data = request.get_json()
    
    if 'username' not in data or 'password' not in data:
        return jsonify({'success': False, 'error': 'Необхідно вказати логін та пароль'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'error': 'Невірний логін або пароль'}), 401
    
    from flask_login import login_user
    login_user(user, remember=data.get('remember', False))
    
    return jsonify({
        'success': True,
        'message': 'Вхід успішний',
        'user': user.to_dict()
    })

# ========== ПОМИЛКИ ==========
@api_bp.errorhandler(400)
def bad_request_error(error):
    return jsonify({'success': False, 'error': 'Неправильний запит'}), 400

@api_bp.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'success': False, 'error': 'Не авторизовано'}), 401

@api_bp.errorhandler(403)
def forbidden_error(error):
    return jsonify({'success': False, 'error': 'Доступ заборонено'}), 403

@api_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({'success': False, 'error': 'Ресурс не знайдено'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Внутрішня помилка сервера'}), 500