# Django Debug Toolbar — Інструкція по використанню

## Зміст

1. [Вступ](#вступ)
2. [Встановлення та налаштування](#встановлення-та-налаштування)
3. [Основні панелі](#основні-панелі)
4. [Виявлення N+1 проблем](#виявлення-n1-проблем)
5. [Оптимізація запитів](#оптимізація-запитів)
6. [Приклади з проекту DJGramm](#приклади-з-проекту-djgramm)
7. [Корисні поради](#корисні-поради)

---

## Вступ

**Django Debug Toolbar** — це потужний інструмент для налагодження та профілювання Django-додатків. Він надає детальну інформацію про:

- SQL-запити та їх час виконання
- Шаблони та контекст
- Статичні файли
- Кешування
- Сигнали
- Профілювання коду

**Важливо:** DjDT працює тільки в режимі `DEBUG=True` і **не повинен** використовуватися в production!

---

## Встановлення та налаштування

### 1. Встановлення

Пакет вже додано в `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "django-debug-toolbar>=4.3.0,<5.0",
]
```

Встановлення:

```bash
uv sync --group dev
```

### 2. Налаштування settings.py

В `src/config/settings.py` вже налаштовано:

```python
# Django Debug Toolbar Configuration (тільки для DEBUG)
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ] + MIDDLEWARE
    INTERNAL_IPS = ["127.0.0.1", "localhost"]

    # Для Docker
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TEMPLATE_CONTEXT": True,
        "SHOW_COLLAPSED": True,
    }
```

### 3. Налаштування URLs

В `src/config/urls.py`:

```python
if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
```

### 4. Перевірка роботи

1. Запустіть сервер: `uv run python manage.py runserver`
2. Відкрийте будь-яку сторінку (наприклад, `http://127.0.0.1:8000/`)
3. Справа на екрані має з'явитися панель Django Debug Toolbar

---

## Основні панелі

### 1. SQL Panel (SQL-запити)

**Найважливіша панель для оптимізації!**

Показує:
- **Кількість SQL-запитів** — скільки запитів виконано
- **Час виконання** — час кожного запиту
- **SQL-код** — повний SQL-код запиту
- **Stacktrace** — де в коді виконано запит

**Як використовувати:**
1. Відкрийте будь-яку сторінку
2. Натисніть на панель **SQL**
3. Подивіться на кількість запитів — якщо їх багато (>10-20), можлива N+1 проблема

### 2. Templates Panel (Шаблони)

Показує:
- Які шаблони використані
- Контекст, переданий у шаблон
- Шлях до файлів шаблонів

**Корисно для:**
- Перевірки доступних змінних у шаблоні
- Відстеження наслідування шаблонів

### 3. Timer Panel (Таймер)

Показує:
- Загальний час обробки запиту
- Час виконання різних етапів (middleware, views, templates)

### 4. Request Panel (Запит)

Показує:
- HTTP-метод (GET, POST)
- Headers
- GET/POST параметри
- Cookies
- Session data

### 5. Static Files Panel (Статичні файли)

Показує:
- Які статичні файли завантажені
- Час завантаження

### 6. Cache Panel (Кеш)

Показує:
- Запити до кешу
- Hit/Miss статистику

### 7. Signals Panel (Сигнали)

Показує:
- Які сигнали викликані
- Час виконання

### 8. Profiling Panel (Профілювання)

Показує:
- Виклики функцій
- Час виконання кожної функції
- Дерево викликів

---

## Виявлення N+1 проблем

### Що таке N+1 проблема?

**N+1 проблема** — коли для кожного об'єкта виконується окремий SQL-запит.

**Приклад проблеми:**

```python
# ❌ Погано - N+1 запитів
posts = Post.objects.all()  # 1 запит
for post in posts:  # N запитів (по одному для кожного поста)
    print(post.author.username)  # Запит для кожного автора!
```

**Результат:** Якщо є 10 постів, виконається **11 запитів** (1 + 10).

### Як виявити в Django Debug Toolbar?

1. Відкрийте сторінку зі списком постів
2. Подивіться на панель **SQL**
3. Якщо кількість запитів **більша за кількість об'єктів** — це N+1 проблема!

**Приклад:**
- 12 постів на сторінці
- 25 SQL-запитів в панелі
- **Проблема!** Має бути ~5-10 запитів

---

## Оптимізація запитів

### 1. select_related() — для ForeignKey та OneToOne

**Використовується для:** Зв'язків один-до-одного (ForeignKey, OneToOne)

**Приклад:**

```python
# ❌ Погано - N+1 запитів
posts = Post.objects.all()
for post in posts:
    print(post.author.username)  # Запит для кожного автора

# ✅ Добре - 1 запит з JOIN
posts = Post.objects.select_related("author").all()
for post in posts:
    print(post.author.username)  # Дані вже завантажені!
```

**В проекті DJGramm:**

```python
# src/app/views.py - FeedView
def get_queryset(self):
    return Post.objects.select_related(
        "author",           # ForeignKey до User
        "author__profile"   # OneToOne через User до Profile
    ).prefetch_related("images", "tags", "likes", "comments")
```

### 2. prefetch_related() — для ManyToMany та зворотних ForeignKey

**Використовується для:** Зв'язків багато-до-багатьох (ManyToMany) та зворотних ForeignKey

**Приклад:**

```python
# ❌ Погано - N+1 запитів
posts = Post.objects.all()
for post in posts:
    for image in post.images.all():  # Запит для кожного поста!
        print(image.url)

# ✅ Добре - 2 запити (1 для постів, 1 для зображень)
posts = Post.objects.prefetch_related("images").all()
for post in posts:
    for image in post.images.all():  # Дані вже завантажені!
        print(image.url)
```

**В проекті DJGramm:**

```python
# src/app/views.py - FeedView
def get_queryset(self):
    return Post.objects.select_related(
        "author", "author__profile"
    ).prefetch_related(
        "images",      # ManyToMany через PostImage
        "tags",        # ManyToMany до Tag
        "likes",       # Зворотний ForeignKey від Like
        "comments"     # Зворотний ForeignKey від Comment
    )
```

### 3. Комбінація select_related() та prefetch_related()

**Приклад з проекту:**

```python
# src/app/views.py - PostDetailView
def get_queryset(self):
    return Post.objects.select_related("author").prefetch_related(
        "images",
        "tags",
        "likes",
        "comments__author"  # Вкладений prefetch для автора коментаря
    )
```

### 4. values_list() для оптимізації

**Коли використовувати:** Коли потрібні тільки ID або конкретні поля

**Приклад з проекту:**

```python
# src/app/views.py - FeedView.get_context_data()
context["user_liked_posts"] = set(
    Like.objects.filter(user=self.request.user).values_list(
        "post_id", flat=True  # Тільки ID, не весь об'єкт
    )
)
```

**Переваги:**
- Менше даних з БД
- Швидше виконання
- Менше пам'яті

---

## Приклади з проекту DJGramm

### 1. FeedView — оптимізований запит

**Файл:** `src/app/views.py`

```python
class FeedView(ListView):
    def get_queryset(self):
        """Show all posts with optimized queries."""
        return Post.objects.select_related(
            "author",           # JOIN для автора
            "author__profile"   # JOIN для профілю автора
        ).prefetch_related(
            "images",           # Prefetch для зображень
            "tags",             # Prefetch для тегів
            "likes",            # Prefetch для лайків
            "comments"          # Prefetch для коментарів
        )
```

**Результат:**
- Без оптимізації: ~50+ SQL-запитів для 12 постів
- З оптимізацією: ~5-7 SQL-запитів

### 2. NewsFeedView — фільтрація з оптимізацією

```python
class NewsFeedView(ListView):
    def get_queryset(self):
        following_ids = list(
            self.request.user.following.values_list("id", flat=True)
        )
        following_ids.append(self.request.user.id)

        return (
            Post.objects.filter(author_id__in=following_ids)
            .select_related("author", "author__profile")
            .prefetch_related("images", "tags", "likes", "comments")
        )
```

**Оптимізації:**
- `values_list("id", flat=True)` — тільки ID, не об'єкти
- `select_related()` — JOIN для автора та профілю
- `prefetch_related()` — один запит для всіх зображень/тегів/лайків

### 3. ProfileView — оптимізація постів користувача

```python
class ProfileView(DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["posts"] = (
            self.object.posts
            .select_related("author")      # JOIN для автора
            .prefetch_related("images")    # Prefetch для зображень
            .order_by("-created_at")
        )
        return context
```

### 4. FollowersListView — оптимізація через Follow модель

```python
class FollowersListView(ListView):
    def get_queryset(self):
        self.target_user = get_object_or_404(
            User, username=self.kwargs["username"]
        )
        # Використовуємо Follow модель з select_related
        return (
            Follow.objects.filter(following=self.target_user)
            .select_related("follower", "follower__profile")
            .order_by("-created_at")
        )
```

**Чому select_related?**
- `Follow` — проміжна модель (through model)
- `follower` — ForeignKey до User
- `follower__profile` — OneToOne через User до Profile
- Використовуємо JOIN замість окремих запитів

### 5. FollowingListView — аналогічна оптимізація

```python
class FollowingListView(ListView):
    def get_queryset(self):
        self.target_user = get_object_or_404(
            User, username=self.kwargs["username"]
        )
        return (
            Follow.objects.filter(follower=self.target_user)
            .select_related("following", "following__profile")
            .order_by("-created_at")
        )
```

### 5. PostDetailView — вкладений prefetch

```python
class PostDetailView(DetailView):
    def get_queryset(self):
        return Post.objects.select_related("author").prefetch_related(
            "images",
            "tags",
            "likes",
            "comments__author"  # Вкладений prefetch для автора коментаря
        )
```

**Вкладений prefetch:**
- `comments__author` — спочатку завантажує коментарі, потім авторів коментарів
- Один запит замість N+1

---

## Корисні поради

### 1. Завжди перевіряйте кількість запитів

**Правило:** Для сторінки зі списком об'єктів має бути **<10 SQL-запитів**

**Як перевірити:**
1. Відкрийте сторінку
2. Подивіться на панель **SQL**
3. Підрахуйте кількість запитів

### 2. Використовуйте select_related() для ForeignKey

**Коли:**
- Доступ до `post.author.username`
- Доступ до `user.profile.bio`

**Приклад:**
```python
Post.objects.select_related("author", "author__profile")
```

### 3. Використовуйте prefetch_related() для ManyToMany

**Коли:**
- Доступ до `post.images.all()`
- Доступ до `post.tags.all()`
- Доступ до `user.followers.all()`

**Приклад:**
```python
Post.objects.prefetch_related("images", "tags")
```

### 4. Комбінуйте select_related() та prefetch_related()

**Приклад:**
```python
Post.objects.select_related("author").prefetch_related("images", "tags")
```

### 5. Використовуйте values_list() для ID

**Коли потрібні тільки ID:**

```python
# ✅ Добре
user_ids = User.objects.filter(is_active=True).values_list("id", flat=True)

# ❌ Погано (якщо потрібні тільки ID)
users = User.objects.filter(is_active=True)
user_ids = [user.id for user in users]
```

### 6. Перевіряйте через Django Debug Toolbar

**Після оптимізації:**
1. Відкрийте сторінку
2. Перевірте кількість SQL-запитів
3. Порівняйте з попереднім результатом

### 7. Уникайте зайвих запитів у шаблонах

**❌ Погано:**
```django
{% for post in posts %}
    {{ post.author.username }}  {# Запит для кожного поста! #}
    {{ post.likes.count }}       {# Запит для кожного поста! #}
{% endfor %}
```

**✅ Добре:**
```python
# В view
posts = Post.objects.select_related("author").prefetch_related("likes")
context["posts"] = posts
```

```django
{% for post in posts %}
    {{ post.author.username }}  {# Дані вже завантажені #}
    {{ post.likes.count }}      {# Дані вже завантажені #}
{% endfor %}
```

---

## Чеклист оптимізації

Перед деплоєм перевірте:

- [ ] Кількість SQL-запитів < 10 для списків
- [ ] Використано `select_related()` для ForeignKey
- [ ] Використано `prefetch_related()` для ManyToMany
- [ ] Немає зайвих запитів у шаблонах
- [ ] Використано `values_list()` для ID
- [ ] Перевірено через Django Debug Toolbar

---

## Додаткові ресурси

- [Офіційна документація Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)
- [Django ORM оптимізація](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [select_related vs prefetch_related](https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-related)

---

## Підсумок

Django Debug Toolbar — незамінний інструмент для:
- ✅ Виявлення N+1 проблем
- ✅ Оптимізації SQL-запитів
- ✅ Аналізу продуктивності
- ✅ Налагодження додатку

**Пам'ятайте:** Завжди перевіряйте кількість SQL-запитів перед деплоєм!

