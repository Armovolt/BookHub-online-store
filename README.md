# Лабораторна робота 6: Інтеграція фронтенду з API та обробка помилок

- **Студент:** Дмитерчук Віталій Вадимович
- **Група:** ІПЗ-23
- **Команда:** "Ardoes"
- **Дата виконання:** Грудень 2025

## 📋 Опис проєкту
BookHub - це веб-додаток для онлайн книжкового магазину з повною інтеграцією фронтенду з RESTful API. У цій лабораторній роботі реалізовано пряму взаємодію JavaScript клієнта з API сервером, що дозволяє виконувати CRUD операції без перезавантаження сторінки.


## 📁 Структура проєкту

```
LAB3-4-FLASK-WEBAPP
├── __pycache__
├── .venv
├── api
│   ├── __pycache__
│   ├── __init__.py
│   └── routes.py
├── auth
│   ├── __pycache__
│   ├── __init__.py
│   └── routes.py
├── instance
├── lab-reports
├── screenshots_lab06
├── templates
│   ├── admin
│   │   ├── add_book.html
│   │   ├── books.html
│   │   ├── customers.html
│   │   ├── dashboard.html
│   │   ├── edit_book.html
│   │   ├── feedback.html
│   │   └── orders.html
│   ├── auth
│   │   ├── login.html
│   │   ├── profile.html
│   │   ├── register.html
│   ├── shop
│   │   ├── cart.html
│   │   └── checkout.html
│   ├── 404.html
│   ├── 500.html
│   ├── about.html
│   ├── api-demo.html
│   ├── base.html
│   ├── books.html
│   ├── index.html
│   └── reviews.html
├── .gitattributes
├── app.py
├── BookHub_API.postman_collection.json
├── models.py
├── README.md
└── requirements.txt
```

## 🔌 API Endpoints

### GET /api/v1/books
Отримує список всіх книг у магазині.

**Приклад запиту:** GET http://localhost:5000/api/v1/books

**Відповідь:**
```json
{
  "success": true,
  "count": 5,
  "books": [
    {
      "id": 1,
      "title": "Хіба що хтось стукне у двері",
      "author": "Стівен Кінг",
      "price": 350.0,
      "category": "Фантастика",
      "stock_quantity": 15,
      "in_stock": true
    }
  ]
}
```

### POST /api/v1/cart
Додає книгу до кошика користувача.

**Тіло запиту**:
```json

{
  "book_id": 1,
  "quantity": 2
}
```

**Відповідь:**
```json
{
  "success": true,
  "message": "Книга додана до кошика",
  "total_items": 2
}
```

### POST /api/v1/reviews
Створює новий відгук про книгу або магазин.

**Тіло запиту**:
```json

{
  "message": "Чудова книга! Рекомендую всім.",
  "rating": 5,
  "book_id": 1
}
```

**Відповідь:**
```json
{
  "success": true,
  "review": {
    "id": 4,
    "message": "Чудова книга! Рекомендую всім.",
    "rating": 5,
    "is_approved": false
  }
}
```

### GET /api/v1/search/books
Пошук книг за назвою або автором.

**Приклад запиту:** GET http://localhost:5000/api/v1/search/books?q=Стівен

**Відповідь:**
```json
{
  "success": true,
  "count": 1,
  "query": "Стівен",
  "books": [
    {
      "id": 1,
      "title": "Хіба що хтось стукне у двері",
      "author": "Стівен Кінг",
      "price": 350.0
    }
  ]
}
```

## 📸 Скріншоти роботи додатку
Демонстраційна сторінка API:
https://github.com/Armovolt/BookHub-online-store/blob/5ed9d49ac8f79a005cf13324cb417dd9e8d3ea5f/screenshots_lab06/01-api-demo-full.png

Демонстраційна сторінка показує пряму інтеграцію JavaScript фронтенду з REST API


Завантаження книг з API:
https://github.com/Armovolt/BookHub-online-store/blob/5ed9d49ac8f79a005cf13324cb417dd9e8d3ea5f/screenshots_lab06/02-books-loading.png

Книги завантажуються безпосередньо з API через JavaScript без перезавантаження сторінки


Форма додавання відгуку:
https://github.com/Armovolt/BookHub-online-store/blob/5ed9d49ac8f79a005cf13324cb417dd9e8d3ea5f/screenshots_lab06/03-review-form.png

Форма для створення відгуків через POST запит до API


Тестування доступності API:
https://github.com/Armovolt/BookHub-online-store/blob/5ed9d49ac8f79a005cf13324cb417dd9e8d3ea5f/screenshots_lab06/04-api-testing.png

Онлайн тестування різних endpoints API з відображенням HTTP статусів


Обробка помилок авторизації:
https://github.com/Armovolt/BookHub-online-store/blob/5ed9d49ac8f79a005cf13324cb417dd9e8d3ea5f/screenshots_lab06/05-auth-error.png

Коректна обробка HTTP статусів 401 (Unauthorized) та 403 (Forbidden)


Успішна відправка відгуку:
https://github.com/Armovolt/BookHub-online-store/blob/5ed9d49ac8f79a005cf13324cb417dd9e8d3ea5f/screenshots_lab06/06-success-review.png

Повідомлення про успішну відправку даних через API


## 🔗 Посилання
- [Посилання на GitHub](https://github.com/Armovolt/BookHub-online-store/tree/lab6-frontend)


## ✅ Висновки
В ході виконання лабораторної роботи №6 було успішно інтегровано фронтенд веб-додатку BookHub з RESTful API. Основні досягнення:

1. Реалізовано пряму взаємодію JavaScript з API - використання Fetch API та async/await для асинхронних запитів

2. Створено демонстраційну сторінку API - повна візуалізація роботи з API без перезавантаження сторінки

3. Реалізовано обробку помилок - коректна обробка HTTP статусів (200, 400, 401, 403, 404, 500)

4. Налаштовано CORS - дозвіл кросс-доменних запитів для взаємодії фронтенду з API

5. Покращено користувацький досвід - інтерактивні форми, сповіщення, індикатори завантаження

6. Протестовано всі основні сценарії - робота з авторизованими та неавторизованими користувачами

Найважливішим результатом стало те, що весь функціонал додатку тепер працює через API - додавання до кошика, створення відгуків, пошук книг виконуються через JavaScript без перезавантажень сторінки, що суттєво покращує користувацький досвід та продуктивність застосунку.

Лабораторна робота демонструє практичні навички роботи з сучасними веб-технологіями та готовність додатку до реального використання.