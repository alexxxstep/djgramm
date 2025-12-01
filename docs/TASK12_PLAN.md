# DJGramm — План реалізації

## Огляд проекту

**DJGramm** — Instagram-подібний застосунок для обміну фотографіями.

| Технологія | Версія/Опис |
|------------|-------------|
| Python | 3.12+ |
| Django | 5.x |
| PostgreSQL | 16 |
| UV | менеджер залежностей |
| Docker | контейнеризація |
| Pillow | обробка зображень |
| pytest-django | тестування |

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

| Модель | Опис | Зв'язки |
|--------|------|---------|
| **User** | Користувач (email auth) | AbstractUser |
| **Profile** | Профіль користувача | 1:1 → User |
| **Post** | Публікація | FK → User, M2M → Tag |
| **PostImage** | Зображення публікації | FK → Post |
| **Tag** | Тег | M2M → Post |
| **Like** | Лайк | FK → User + Post |

---

## Фази реалізації

### Фаза 1: Налаштування проекту
**Тривалість:** 1 день

- [ ] Ініціалізація UV проекту
- [ ] Встановлення залежностей (Django, psycopg, Pillow, pytest)
- [ ] Створення Django проекту в `src/config/`
- [ ] Налаштування Docker + docker-compose
- [ ] Підключення PostgreSQL
- [ ] Файл `.env.example`

**Результат:** `docker compose up` запускає Django

---

### Фаза 2: Моделі
**Тривалість:** 1 день

- [ ] Створення всіх моделей в `app/models.py`
- [ ] Custom User з email автентифікацією
- [ ] Profile з автостворенням через signal
- [ ] Post, PostImage, Tag, Like
- [ ] Міграції

**Результат:** `makemigrations` + `migrate` успішні

---

### Фаза 3: Адмін-панель
**Тривалість:** 1 день

- [ ] Реєстрація всіх моделей в `admin.py`
- [ ] Inline для Profile та PostImage
- [ ] Фільтри та пошук

**Результат:** Повний CRUD через `/admin/`

---

### Фаза 4: Views та URLs
**Тривалість:** 2 дні

**Ендпоінти:**
| URL | View | Опис |
|-----|------|------|
| `/` | FeedView | Стрічка постів |
| `/register/` | RegisterView | Реєстрація |
| `/login/`, `/logout/` | Auth | Автентифікація |
| `/profile/<username>/` | ProfileView | Профіль |
| `/profile/edit/` | ProfileEditView | Редагування |
| `/post/new/` | PostCreateView | Створення посту |
| `/post/<pk>/` | PostDetailView | Деталі посту |
| `/post/<pk>/like/` | toggle_like | Лайк (AJAX) |
| `/tag/<slug>/` | TagPostsView | Пости по тегу |

**Результат:** Всі маршрути працюють

---

### Фаза 5: Форми та обробка зображень
**Тривалість:** 1 день

- [ ] RegistrationForm, ProfileForm, PostForm
- [ ] PostImageFormSet для множинних зображень
- [ ] Сервіс генерації thumbnail
- [ ] Валідація зображень (10MB, JPEG/PNG/WebP)

**Результат:** Завантаження зображень працює

---

### Фаза 6: Шаблони та UI
**Тривалість:** 2 дні

- [ ] `base.html` — layout, navbar, messages
- [ ] `registration/` — login, register
- [ ] `app/` — feed, post_detail, post_form, profile
- [ ] Tailwind CSS (CDN)
- [ ] JavaScript для лайків

**Результат:** Завершений UI

---

### Фаза 7: Тестові дані
**Тривалість:** 1 день

- [ ] Factory Boy фабрики
- [ ] Seed script: 20 users, 100 posts, 10 tags

**Результат:** Реалістичні тестові дані

---

### Фаза 8: Тестування
**Тривалість:** 2 дні

- [ ] Fixtures в `conftest.py`
- [ ] Тести моделей
- [ ] Тести views
- [ ] Тести сервісів

**Ціль:** 80%+ покриття

---

### Фаза 9: CI/CD
**Тривалість:** 1 день

- [ ] GitLab CI pipeline
- [ ] Stage: lint (ruff)
- [ ] Stage: test (pytest + postgres)
- [ ] Stage: build (docker)

**Результат:** Pipeline проходить

---

### Фаза 10: Деплой
**Тривалість:** 2 дні

**Checklist:**
- [ ] DEBUG=False
- [ ] SECRET_KEY з env
- [ ] ALLOWED_HOSTS
- [ ] WhiteNoise для static
- [ ] HTTPS

**Результат:** Живий застосунок

---

## Загальний таймлайн

| Фаза | Дні | Результат |
|------|-----|-----------|
| Налаштування | 1 | Docker + Django |
| Моделі | 1 | 6 моделей |
| Адмін | 1 | Admin панель |
| Views | 2 | Всі маршрути |
| Форми | 1 | Upload зображень |
| Шаблони | 2 | UI |
| Seed | 1 | Тестові дані |
| Тести | 2 | 80% coverage |
| CI/CD | 1 | Pipeline |
| Деплой | 2 | Production |
| **Всього** | **14** | **MVP** |

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

