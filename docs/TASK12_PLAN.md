# DJGramm — План реалізації

## Огляд проекту

**DJGramm** — Instagram-подібний застосунок для обміну фотографіями.

| Технологія     | Версія/Опис           |
| -------------- | --------------------- |
| Python         | 3.12+                 |
| Django         | 5.x                   |
| PostgreSQL     | 16                    |
| UV             | менеджер залежностей  |
| Docker         | контейнеризація       |
| Pillow         | обробка зображень     |
| pytest-django  | тестування            |

---

## Архітектура

**Monolith Single App** — всі моделі та логіка в одному застосунку `app/`.

```
djgramm/
├── src/
│   ├── config/          # Django settings, urls, wsgi
│   ├── app/             # Єдиний застосунок
│   ├── templates/       # HTML шаблони
│   └── static/          # CSS, JS
├── tests/               # pytest тести
├── docker/              # Dockerfile, entrypoint
└── scripts/             # seed data
```

---

## Моделі даних

| Модель        | Опис                      | Зв'язки              |
| ------------- | ------------------------- | -------------------- |
| **User**      | Користувач (email auth)   | AbstractUser         |
| **Profile**   | Профіль користувача       | 1:1 → User           |
| **Post**      | Публікація                | FK → User, M2M → Tag |
| **PostImage** | Зображення публікації     | FK → Post            |
| **Tag**       | Тег                       | M2M → Post           |
| **Like**      | Лайк                      | FK → User + Post     |

---

## Фази реалізації

### Фаза 1: Налаштування проекту ✅
**Тривалість:** 1 день | **Статус:** Завершено

- [x] Ініціалізація UV проекту
- [x] Встановлення залежностей (Django, psycopg, Pillow, pytest)
- [x] Створення Django проекту в `src/config/`
- [x] Налаштування Docker + docker-compose
- [x] Підключення PostgreSQL
- [x] Файл `.env.example`

**Зроблено:** `pyproject.toml`, `docker-compose.yml`, `Dockerfile`, налаштування PostgreSQL на порту 55432

---

### Фаза 2: Моделі ✅
**Тривалість:** 1 день | **Статус:** Завершено

- [x] Створення всіх моделей в `app/models.py`
- [x] Custom User з email автентифікацією
- [x] Profile з автостворенням через signal
- [x] Post, PostImage, Tag, Like
- [x] Міграції

**Зроблено:** 6 моделей з `__str__`, `get_absolute_url`, `Meta.ordering`, сигнал для авто-створення Profile

---

### Фаза 3: Адмін-панель ✅
**Тривалість:** 1 день | **Статус:** Завершено

- [x] Реєстрація всіх моделей в `admin.py`
- [x] Inline для Profile та PostImage
- [x] Фільтри та пошук

**Зроблено:** UserAdmin + ProfileInline, PostAdmin + PostImageInline, TagAdmin з prepopulated_fields

---

### Фаза 4: Views та URLs ✅
**Тривалість:** 2 дні | **Статус:** Завершено

**Ендпоінти:**

| URL                    | View            | Опис              |
| ---------------------- | --------------- | ----------------- |
| `/`                    | FeedView        | Стрічка постів    |
| `/register/`           | RegisterView    | Реєстрація        |
| `/login/`, `/logout/`  | Auth            | Автентифікація    |
| `/profile/<username>/` | ProfileView     | Профіль           |
| `/profile/edit/`       | ProfileEditView | Редагування       |
| `/post/new/`           | PostCreateView  | Створення посту   |
| `/post/<pk>/`          | PostDetailView  | Деталі посту      |
| `/post/<pk>/edit/`     | PostUpdateView  | Редагування посту |
| `/post/<pk>/delete/`   | PostDeleteView  | Видалення посту   |
| `/post/<pk>/like/`     | toggle_like     | Лайк (AJAX)       |
| `/tag/<slug>/`         | TagPostsView    | Пости по тегу     |

**Зроблено:** 12 views (CBV + FBV), LoginRequiredMixin, UserPassesTestMixin для захисту

---

### Фаза 5: Форми та обробка зображень ✅
**Тривалість:** 1 день | **Статус:** Завершено

- [x] RegistrationForm, ProfileForm, PostForm
- [x] PostImageFormSet для множинних зображень
- [x] Сервіс генерації thumbnail
- [x] Валідація зображень (10MB, JPEG/PNG/WebP)

**Зроблено:** `forms.py`, `services.py` з `validate_image()`, `generate_thumbnail()`, `process_uploaded_image()`

---

### Фаза 6: Шаблони та UI ✅
**Тривалість:** 2 дні | **Статус:** Завершено

- [x] `base.html` — layout, navbar, messages
- [x] `registration/` — login, register
- [x] `app/` — feed, post_detail, post_form, profile
- [x] Tailwind CSS (CDN)
- [x] JavaScript для лайків

**Зроблено:** 11 шаблонів, Tailwind + Poppins font, AJAX лайки, пагінація, responsive design

---

### Фаза 7: Тестові дані ✅
**Тривалість:** 1 день | **Статус:** Завершено

- [x] Factory Boy фабрики
- [x] Seed script: 20 users, 100 posts, 10 tags

**Зроблено:** `tests/factories.py` (6 фабрик), `scripts/seed_data.py` (21 user, 102 posts, 147 images, 448 likes)

---

### Фаза 8: Тестування ✅
**Тривалість:** 2 дні | **Статус:** Завершено

- [x] Fixtures в `conftest.py`
- [x] Тести моделей
- [x] Тести views
- [x] Тести сервісів

**Ціль:** 80%+ покриття | **Результат:** 97% coverage ✅

**Зроблено:** 74 тести (25 models + 35 views + 14 services), 12 fixtures

---

### Фаза 9: CI/CD ✅
**Тривалість:** 1 день | **Статус:** Завершено

- [x] GitLab CI pipeline
- [x] Stage: lint (ruff)
- [x] Stage: test (pytest + postgres)
- [x] Stage: build (docker)

**Зроблено:** `.gitlab-ci.yml` з 5 jobs, ruff конфігурація в `pyproject.toml`

---

### Фаза 10: Деплой ✅
**Тривалість:** 2 дні | **Статус:** Завершено

**Checklist:**

- [x] DEBUG=False
- [x] SECRET_KEY з env
- [x] ALLOWED_HOSTS
- [x] WhiteNoise для static
- [x] HTTPS (налаштування готові)

**Зроблено:** `Dockerfile.prod`, `docker-compose.prod.yml`, `nginx.conf`, production security settings

---

## Загальний таймлайн

| Фаза         | Дні       | Результат        | Статус |
| ------------ | --------- | ---------------- | ------ |
| Налаштування | 1         | Docker + Django  | ✅     |
| Моделі       | 1         | 6 моделей        | ✅     |
| Адмін        | 1         | Admin панель     | ✅     |
| Views        | 2         | Всі маршрути     | ✅     |
| Форми        | 1         | Upload зображень | ✅     |
| Шаблони      | 2         | UI               | ✅     |
| Seed         | 1         | Тестові дані     | ✅     |
| Тести        | 2         | 97% coverage     | ✅     |
| CI/CD        | 1         | Pipeline         | ✅     |
| Деплой       | 2         | Production ready | ✅     |
| **Всього**   | **14**    | **MVP**          | ✅     |

---

## Змінні оточення

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:pass@db:5432/djgramm
```

---

## Ключові принципи

1. **Single App** — простота та швидкість розробки
2. **select_related / prefetch_related** — уникнення N+1
3. **CBV** — Class-Based Views для стандартних операцій
4. **FBV** — Function-Based для простих дій (like toggle)
5. **Signals** — автоматичне створення Profile

---

## Підсумок

**Проект DJGramm повністю завершено!**

| Метрика          | Значення          |
| ---------------- | ----------------- |
| Моделей          | 6                 |
| Views            | 12                |
| Шаблонів         | 11                |
| Тестів           | 74                |
| Coverage         | 97%               |
| CI/CD jobs       | 5                 |
| Seed users       | 21                |
| Seed posts       | 102               |

**Готовий до production deploy!**
