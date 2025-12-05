# DJGramm TASK13 — План реалізації нових функцій

## Огляд завдання

Додати до існуючого проекту DJGramm наступні функції:

1. **Підписки (Following/Followers)** — користувачі можуть підписуватися на інших користувачів
2. **Новинна стрічка (News Feed)** — відображення подій від підписок (пости, підписки, лайки)
3. **Лайки** — вже реалізовано, потрібно перевірити та покращити UI
4. **Cloudinary** — інтеграція стороннього сервісу для зберігання зображень
5. **UI покращення** — використання Tailwind для сучасного дизайну
6. **Деплой** — розгортання на сервер
7. **Тести** — покриття нових функцій тестами

---

## Поточна архітектура

**Проект:** Django 5.x, Single App моноліт, PostgreSQL, Docker

**Існуючі моделі:**

- `User` (AbstractUser з email auth)
- `Profile` (One-to-One з User)
- `Post` (з caption, tags, images)
- `PostImage` (зображення поста)
- `Tag` (теги для постів)
- `Like` (лайки на постах)
- `Comment` (коментарі до постів)

**Існуючі views:**

- `FeedView` — відображає всі пости (потрібно змінити на новинну стрічку)
- `ProfileView`, `ProfileEditView`
- `PostCreateView`, `PostDetailView`, `PostUpdateView`, `PostDeleteView`
- `toggle_like` — AJAX лайк/анлайк
- `TagPostsView`

**Існуючі технології:**

- Tailwind CSS (CDN)
- Pillow для обробки зображень (локально)
- PostgreSQL для БД
- Docker для контейнеризації

---

## Нові вимоги

### 1. Модель Follow (Following/Followers)

**Структура:**

- `follower` — ForeignKey до User (хто підписується)
- `following` — ForeignKey до User (на кого підписуються)
- `created_at` — дата підписки
- `unique_together` — один користувач не може підписатися двічі на одного

**Методи:**

- `User.followers.count()` — кількість підписників
- `User.following.count()` — кількість підписок
- `User.is_following(user)` — перевірка підписки

### 2. Новинна стрічка (News Feed)

**Події для відображення:**

- Пости від користувачів, на яких підписано
- Підписки/відписки друзів (опціонально)
- Лайки на постах друзів (опціонально)

**Фільтрація:**

- Тільки пости від підписок
- Сортування: `-created_at` (найновіші спочатку)
- Пагінація: 12 постів на сторінку

### 3. Cloudinary інтеграція

**Заміна локального зберігання на Cloudinary:**

- Завантаження зображень на Cloudinary
- Отримання URL зображень з Cloudinary
- Видалення зображень при видаленні поста/профілю
- Fallback на локальне зберігання для розробки

### 4. UI покращення

**Компоненти:**

- Кнопка "Follow/Unfollow" на профілі
- Показ кількості підписників/підписок
- Покращений дизайн новинної стрічки
- Індикатори нових подій
- Responsive design для мобільних

---

## Фази реалізації

### Фаза 1: Модель Follow та міграції

#### Крок 1.1: Створення моделі Follow

**Файл:** `src/app/models.py`

```python
class Follow(models.Model):
    """Follow relationship between users."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["follower", "following"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
```

**Важливо:**

- `related_name="following"` — користувачі, на яких підписано
- `related_name="followers"` — користувачі, які підписались
- `unique_together` — запобігає дублюванню підписок
- Заборона підписки на самого себе (перевірка в view)
- Використати `select_related` та `prefetch_related` для оптимізації (перевірити через Django Debug Toolbar)

#### Крок 1.2: Додавання helper методів до User

**Файл:** `src/app/models.py` (клас User)

```python
def get_followers_count(self):
    """Return number of followers."""
    return self.followers.count()

def get_following_count(self):
    """Return number of users being followed."""
    return self.following.count()

def is_following(self, user):
    """Check if current user follows given user."""
    return self.following.filter(following=user).exists()
```

#### Крок 1.3: Створення міграції

```bash
python manage.py makemigrations
python manage.py migrate
```

**Результат:** Модель Follow створена, міграція застосована

---

### Фаза 2: Views для підписок

#### Крок 2.1: View для підписки/відписки

**Файл:** `src/app/views.py`

**Функція:** `toggle_follow(request, username)`

**Логіка:**

1. Отримати користувача за username
2. Перевірити, що не підписується на себе
3. Створити або видалити Follow запис
4. Повернути JSON зі статусом та кількістю підписників

**URL:** `path("profile/<str:username>/follow/", views.toggle_follow, name="toggle_follow")`

#### Крок 2.2: Оновлення ProfileView

**Додати в контекст:**

- `is_following` — чи підписаний поточний користувач
- `followers_count` — кількість підписників
- `following_count` — кількість підписок
- `posts_count` — вже є

#### Крок 2.3: Список підписників/підписок

**Views:**

- `FollowersListView` — список підписників користувача
- `FollowingListView` — список підписок користувача

**URLs:**

- `profile/<username>/followers/`
- `profile/<username>/following/`

**Важливо для оптимізації:**

- Використати `select_related("user", "user__profile")` для завантаження профілів одним запитом
- Перевірити через Django Debug Toolbar (Фаза 3.5), що немає N+1 проблем

**Результат:** Повна функціональність підписок

---

### Фаза 3: Новинна стрічка (News Feed)

#### Крок 3.1: Оновлення FeedView

**Файл:** `src/app/views.py`

**Зміни в `get_queryset()`:**

```python
def get_queryset(self):
    """Show posts only from users being followed."""
    if not self.request.user.is_authenticated:
        return Post.objects.none()

    # Get IDs of users being followed
    following_ids = self.request.user.following.values_list(
        'following_id', flat=True
    )

    # Include own posts
    following_ids = list(following_ids) + [self.request.user.id]

    return Post.objects.filter(
        author_id__in=following_ids
    ).select_related(
        "author", "author__profile"
    ).prefetch_related(
        "images", "tags", "likes", "comments"
    )
```

**Примітка:** Після реалізації використати Django Debug Toolbar для перевірки кількості SQL-запитів та оптимізації (див. Фаза 3.5).

**Додати в контекст:**

- `following_count` — кількість підписок
- Повідомлення, якщо немає підписок

#### Крок 3.2: Оновлення шаблону feed.html

**Додати:**

- Повідомлення "Follow users to see their posts"
- Кнопка "Discover" для пошуку користувачів
- Показ кількості підписок

**Результат:** Новинна стрічка показує тільки пости від підписок

---

### Фаза 3.5: Налаштування Django Debug Toolbar (для оптимізації запитів)

**Невелика таска:** Додати Django Debug Toolbar для аналізу та оптимізації SQL-запитів.

**Мета:** Виявлення N+1 проблем, аналіз продуктивності запитів, оптимізація використання `select_related` та `prefetch_related`.

#### Крок 3.5.1: Встановлення

```bash
uv add --group dev django-debug-toolbar
```

#### Крок 3.5.2: Налаштування settings.py

```python
# Додати до INSTALLED_APPS (тільки для DEBUG)
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

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

#### Крок 3.5.3: Налаштування URLs

```python
# src/config/urls.py
if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
```

#### Крок 3.5.4: Перевірка та використання

1. Запустити сервер, відкрити будь-яку сторінку
2. Перевірити наявність панелі Django Debug Toolbar (справа на екрані)
3. Використовувати панель **SQL** для аналізу кількості запитів та виявлення N+1 проблем

**Важливо:** DjDT працює тільки в DEBUG режимі, не використовувати в production.

**Приклад оптимізації:**

```python
# Погано - N+1 запитів
posts = Post.objects.all()
for post in posts:
    print(post.author.username)

# Добре - 1 запит з JOIN
posts = Post.objects.select_related("author").all()

# Для M2M - prefetch_related
posts = Post.objects.prefetch_related("tags", "likes").all()
```

**Детальна інструкція:** Див. `.cursor/docs/django-debug-toolbar-setup.md`

**Результат:** DjDT налаштований, можна аналізувати та оптимізувати SQL-запити

---

### Фаза 4: Cloudinary інтеграція

#### Крок 4.1: Встановлення та налаштування Cloudinary

**Встановлення пакету:**

```bash
uv add cloudinary
```

**Додати в `pyproject.toml`:**

```toml
dependencies = [
    # ... existing
    "cloudinary>=1.36.0",
]
```

**Реєстрація на Cloudinary:**

1. Перейти на https://cloudinary.com
2. Створити безкоштовний акаунт
3. Отримати:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

#### Крок 4.2: Налаштування settings.py

**Файл:** `src/config/settings.py`

**Додати в INSTALLED_APPS:**

```python
INSTALLED_APPS = [
    # ... existing
    "cloudinary",
    "cloudinary_storage",
]
```

**Додати налаштування Cloudinary:**

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Cloudinary settings
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

# Use Cloudinary for media files
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Initialize Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE["CLOUD_NAME"],
    api_key=CLOUDINARY_STORAGE["API_KEY"],
    api_secret=CLOUDINARY_STORAGE["API_SECRET"],
)
```

**Оновити MEDIA_URL (опціонально):**

```python
MEDIA_URL = "/media/"  # Cloudinary обробляє це автоматично
```

#### Крок 4.3: Оновлення моделей

**Файл:** `src/app/models.py`

**Змінити ImageField на CloudinaryField:**

```python
from cloudinary.models import CloudinaryField

class Profile(models.Model):
    # ... existing fields
    avatar = CloudinaryField("image", folder="avatars", blank=True)

class PostImage(models.Model):
    # ... existing fields
    image = CloudinaryField("image", folder="posts")
```

**Переваги CloudinaryField:**

- Автоматичне завантаження на Cloudinary
- Автоматичне отримання URL
- Автоматичне видалення при видаленні об'єкта
- Підтримка трансформацій (resize, crop, etc.)

#### Крок 4.4: Міграція даних (якщо є існуючі зображення)

**Створити management command:**

**Файл:** `src/app/management/commands/migrate_to_cloudinary.py`

```python
from django.core.management.base import BaseCommand
from app.models import Profile, PostImage
import cloudinary.uploader

class Command(BaseCommand):
    help = "Migrate existing images to Cloudinary"

    def handle(self, *args, **options):
        # Migrate Profile avatars
        for profile in Profile.objects.exclude(avatar=""):
            if profile.avatar:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    profile.avatar.path,
                    folder="avatars"
                )
                profile.avatar = result["public_id"]
                profile.save()

        # Migrate PostImage
        for post_image in PostImage.objects.all():
            if post_image.image:
                result = cloudinary.uploader.upload(
                    post_image.image.path,
                    folder="posts"
                )
                post_image.image = result["public_id"]
                post_image.save()
```

**Запуск:**

```bash
python manage.py migrate_to_cloudinary
```

#### Крок 4.5: Оновлення .env.example

**Додати:**

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

#### Крок 4.6: Fallback для розробки

**Опціонально:** Використовувати Cloudinary тільки в production

```python
# settings.py
if DEBUG:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
else:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
```

**Результат:** Всі зображення зберігаються на Cloudinary

---

### Фаза 5: UI покращення з Tailwind

#### Крок 5.1: Кнопка Follow/Unfollow

**Файл:** `src/templates/app/profile.html`

**Додати кнопку:**

```html
{% if user.is_authenticated and user != profile_user %}
<button
  id="follow-btn"
  data-username="{{ profile_user.username }}"
  class="px-4 py-2 rounded-lg {% if is_following %}bg-gray-200{% else %}bg-blue-500 text-white{% endif %}"
>
  {% if is_following %}Unfollow{% else %}Follow{% endif %}
</button>
{% endif %}
```

#### Крок 5.2: JavaScript для AJAX підписки

**Файл:** `src/static/js/follow.js` (новий)

```javascript
document.addEventListener('DOMContentLoaded', function () {
  const followBtn = document.getElementById('follow-btn');
  if (followBtn) {
    followBtn.addEventListener('click', function () {
      const username = this.dataset.username;
      fetch(`/profile/${username}/follow/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        },
      })
        .then((response) => response.json())
        .then((data) => {
          followBtn.textContent = data.is_following ? 'Unfollow' : 'Follow';
          followBtn.classList.toggle('bg-blue-500');
          followBtn.classList.toggle('bg-gray-200');
          // Update followers count
          document.getElementById('followers-count').textContent =
            data.followers_count;
        });
    });
  }
});
```

#### Крок 5.3: Показ статистики профілю

**Додати в profile.html:**

```html
<div class="flex gap-6">
  <div><span class="font-bold">{{ posts_count }}</span> posts</div>
  <div>
    <span class="font-bold" id="followers-count">{{ followers_count }}</span>
    followers
  </div>
  <div><span class="font-bold">{{ following_count }}</span> following</div>
</div>
```

#### Крок 5.4: Покращення новинної стрічки

**Оновити feed.html:**

- Карточки постів з тінню та закругленими кутами
- Hover ефекти
- Плавні переходи
- Responsive grid layout

#### Крок 5.5: Список підписників/підписок

**Шаблони:**

- `followers_list.html` — список підписників
- `following_list.html` — список підписок

**Дизайн:**

- Аватар користувача
- Username та full_name
- Кнопка Follow/Unfollow (якщо не власний профіль)

**Результат:** Сучасний UI з Tailwind CSS

---

### Фаза 6: Тестування

#### Крок 6.1: Тести моделі Follow

**Файл:** `tests/test_models.py`

**Тести:**

- Створення підписки
- Заборона дублювання підписки
- Заборона підписки на себе
- Методи `get_followers_count()`, `get_following_count()`, `is_following()`

#### Крок 6.2: Тести views

**Файл:** `tests/test_views.py`

**Тести:**

- `toggle_follow` — підписка/відписка
- `FeedView` — показ тільки постів від підписок
- `FollowersListView`, `FollowingListView`
- Перевірка автентифікації

#### Крок 6.3: Тести Cloudinary (моки)

**Файл:** `tests/test_cloudinary.py` (новий)

**Тести:**

- Завантаження зображення на Cloudinary
- Отримання URL зображення
- Видалення зображення
- Fallback на локальне зберігання в DEBUG режимі

#### Крок 6.4: Оновлення factories

**Файл:** `tests/factories.py`

**Додати:**

```python
class FollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Follow

    follower = factory.SubFactory(UserFactory)
    following = factory.SubFactory(UserFactory)
```

**Ціль:** 80%+ покриття нових функцій

**Результат:** Повне покриття тестами

---

### Фаза 7: Деплой на сервер

#### Крок 7.1: Оновлення production settings

**Файл:** `src/config/settings.py`

**Перевірити:**

- `DEBUG = False`
- `SECRET_KEY` з env
- `ALLOWED_HOSTS` з env
- Cloudinary налаштування
- WhiteNoise для static files

#### Крок 7.2: Оновлення Dockerfile.prod

**Перевірити:**

- Встановлення залежностей (включаючи cloudinary)
- Збірка static files
- Міграції при старті

#### Крок 7.3: Оновлення docker-compose.prod.yml

**Додати змінні оточення:**

```yaml
environment:
  - CLOUDINARY_CLOUD_NAME=${CLOUDINARY_CLOUD_NAME}
  - CLOUDINARY_API_KEY=${CLOUDINARY_API_KEY}
  - CLOUDINARY_API_SECRET=${CLOUDINARY_API_SECRET}
```

#### Крок 7.4: Деплой

**Кроки:**

1. Підключитися до сервера
2. Оновити код (git pull)
3. Оновити залежності (uv sync)
4. Застосувати міграції (`python manage.py migrate`)
5. Зібрати static files (`python manage.py collectstatic`)
6. Перезапустити контейнери (`docker-compose -f docker-compose.prod.yml up -d`)

**Результат:** Проект розгорнуто на сервері

---

## Детальна інструкція по Cloudinary

### Що таке Cloudinary?

**Cloudinary** — хмарний сервіс для зберігання та обробки зображень та відео.

**Переваги:**

- Безкоштовний план: 25 GB storage, 25 GB bandwidth/місяць
- Автоматична оптимізація зображень
- Трансформації на льоту (resize, crop, filters)
- CDN для швидкої доставки
- Автоматичне видалення при видаленні об'єкта

### Реєстрація та отримання ключів

1. **Реєстрація:**

   - Перейти на https://cloudinary.com/users/register/free
   - Заповнити форму (email, пароль)
   - Підтвердити email

2. **Отримання ключів:**

   - Після входу перейти в Dashboard
   - Знайти секцію "Account Details"
   - Скопіювати:
     - **Cloud Name** (наприклад, `dxyz123`)
     - **API Key** (наприклад, `123456789012345`)
     - **API Secret** (наприклад, `abcdefghijklmnopqrstuvwxyz`)

3. **Збереження в .env:**
   ```env
   CLOUDINARY_CLOUD_NAME=dxyz123
   CLOUDINARY_API_KEY=123456789012345
   CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz
   ```

### Встановлення пакету

```bash
# Додати в pyproject.toml
uv add cloudinary

# Або вручну
pip install cloudinary
```

### Налаштування Django

**1. Додати в INSTALLED_APPS:**

```python
INSTALLED_APPS = [
    # ... existing
    "cloudinary",
    "cloudinary_storage",
]
```

**2. Налаштування в settings.py:**

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE["CLOUD_NAME"],
    api_key=CLOUDINARY_STORAGE["API_KEY"],
    api_secret=CLOUDINARY_STORAGE["API_SECRET"],
)
```

### Використання в моделях

**Заміна ImageField на CloudinaryField:**

```python
from cloudinary.models import CloudinaryField

class Profile(models.Model):
    avatar = CloudinaryField("image", folder="avatars", blank=True)

class PostImage(models.Model):
    image = CloudinaryField("image", folder="posts")
```

**Параметри CloudinaryField:**

- `"image"` — тип ресурсу (image, video, raw)
- `folder="avatars"` — папка в Cloudinary (організація)
- `blank=True` — опціональне поле

### Отримання URL зображення

**В шаблонах:**

```html
<!-- Автоматично отримує URL -->
<img src="{{ profile.avatar.url }}" alt="Avatar" />

<!-- З трансформаціями -->
<img
  src="{{ profile.avatar.url|cloudinary_url:width=200,height=200,crop='fill' }}"
  alt="Avatar"
/>
```

**В Python:**

```python
# Отримати URL
url = profile.avatar.url

# З трансформаціями
from cloudinary import cloudinary
url = cloudinary.CloudinaryImage(profile.avatar.public_id).build_url(
    width=200,
    height=200,
    crop="fill"
)
```

### Трансформації зображень

**Приклади:**

```python
# Resize
url = cloudinary.CloudinaryImage(public_id).build_url(width=300, height=300)

# Crop
url = cloudinary.CloudinaryImage(public_id).build_url(
    width=200,
    height=200,
    crop="fill",
    gravity="face"  # Обрізати по обличчю
)

# Filters
url = cloudinary.CloudinaryImage(public_id).build_url(
    effect="blur:300",  # Розмиття
    quality="auto"     # Авто-оптимізація
)
```

### Міграція існуючих зображень

**Якщо є локальні зображення:**

1. Створити management command (див. Фаза 4.4)
2. Запустити міграцію
3. Перевірити, що всі зображення завантажені

**Альтернатива:** Завантажити вручну через Cloudinary Dashboard

### Тестування Cloudinary

**Моки для тестів:**

```python
from unittest.mock import patch, MagicMock

@patch('cloudinary.uploader.upload')
def test_upload_image(mock_upload):
    mock_upload.return_value = {
        'public_id': 'test_image',
        'url': 'https://res.cloudinary.com/...'
    }
    # Тест завантаження
```

### Troubleshooting

**Проблема:** Зображення не завантажуються

- Перевірити ключі в .env
- Перевірити інтернет-з'єднання
- Перевірити права доступу до Cloudinary

**Проблема:** Помилка "Invalid API credentials"

- Перевірити правильність ключів
- Перевірити, що ключі не мають пробілів

**Проблема:** Зображення видаляються автоматично

- Це нормально, CloudinaryField автоматично видаляє при видаленні об'єкта
- Для збереження використати `keep=True` в налаштуваннях

---

## Змінні оточення

**Оновити `.env.example`:**

```env
# Django
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:pass@db:5432/djgramm

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

---

## Загальний таймлайн

| Фаза                 | Результат                    |
| -------------------- | ---------------------------- |
| Модель Follow        | Модель + міграції            |
| Views підписок       | Підписка/відписка            |
| Новинна стрічка      | Feed з підписок              |
| Django Debug Toolbar | Налаштування для оптимізації |
| Cloudinary           | Зберігання на Cloudinary     |
| UI покращення        | Сучасний дизайн              |
| Тестування           | Покриття тестами             |
| Деплой               | Розгорнуто на сервері        |

---

## Ключові принципи

1. **Збереження архітектури** — Single App моноліт
2. **Оптимізація запитів** — `select_related`, `prefetch_related` для Follow, аналіз через Django Debug Toolbar
3. **AJAX для інтерактивності** — Follow/Unfollow без перезавантаження
4. **Cloudinary для production** — локальне зберігання для розробки (опціонально)
5. **Тести для всіх функцій** — мінімум 80% покриття
6. **Responsive design** — мобільна версія
7. **Діагностика продуктивності** — Django Debug Toolbar для виявлення N+1 проблем

---

## Checklist перед завершенням

- [ ] Модель Follow створена та міграції застосовані
- [ ] Views для підписок працюють
- [ ] Новинна стрічка показує тільки пости від підписок
- [ ] Django Debug Toolbar налаштований для оптимізації запитів (опціонально)
  - [ ] Встановлено залежність через `uv add --group dev django-debug-toolbar`
  - [ ] Налаштовано INSTALLED_APPS, MIDDLEWARE, INTERNAL_IPS (тільки для DEBUG)
  - [ ] Додано URLs в `urls.py` (тільки для DEBUG)
  - [ ] Перевірено роботу toolbar та аналіз SQL-запитів
- [ ] SQL-запити оптимізовані (перевірено через DjDT)
  - [ ] Виявлено та виправлено N+1 проблеми в FeedView
  - [ ] Виправлено N+1 проблеми в списках підписників/підписок
  - [ ] Використано `select_related` та `prefetch_related` де потрібно
- [ ] Cloudinary налаштований та працює
- [ ] Всі зображення завантажені на Cloudinary
- [ ] UI покращений з Tailwind
- [ ] Тести написані та проходять
- [ ] Деплой на сервер виконано
- [ ] Документація оновлена

---

## Додаткові ресурси

- [Cloudinary Django Documentation](https://cloudinary.com/documentation/django_image_and_video_upload)
- [Cloudinary Python SDK](https://cloudinary.com/documentation/django_integration)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Django Follow System Tutorial](https://www.youtube.com/watch?v=example)
- [Django Debug Toolbar Documentation](https://django-debug-toolbar.readthedocs.io/en/latest/) — для оптимізації запитів

---

## Підсумок

**TASK13 додає до проекту:**

- Систему підписок (Following/Followers)
- Новинну стрічку з постами від підписок
- Інтеграцію Cloudinary для зберігання зображень
- Покращений UI з Tailwind CSS
- Django Debug Toolbar для оптимізації запитів (dev-середовище)
- Повне тестування нових функцій
- Production-ready деплой

**Готово до початку реалізації!**
