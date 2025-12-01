# DJGramm - Implementation Plan
## Django Monolith (Single App)

---

## 1. Project Overview

**DJGramm** — Instagram-like photo sharing application.

**Stack:**
- Python 3.12+ / Django 5.x
- PostgreSQL 16
- UV (pyproject.toml)
- Docker + Docker Compose
- GitLab CI/CD
- Pillow (thumbnails)
- pytest-django

---

## 2. Project Structure

```
djgramm/
├── src/
│   ├── config/                    # Django settings
│   │   ├── __init__.py
│   │   ├── settings.py            # Single settings (env-based)
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── app/                       # Single app (scale: rename to apps/)
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── forms.py
│   │   ├── models.py              # ALL MODELS
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── services.py
│   │   └── signals.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── registration/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── app/
│   │       ├── feed.html
│   │       ├── post_detail.html
│   │       ├── post_form.html
│   │       ├── profile.html
│   │       └── profile_edit.html
│   │
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   │
│   └── manage.py
│
├── tests/
│   ├── conftest.py
│   ├── factories.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_services.py
│
├── docker/
│   ├── Dockerfile
│   └── entrypoint.sh
│
├── scripts/
│   └── seed_data.py
│
├── .env.example
├── .gitignore
├── .gitlab-ci.yml
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

**~25 files total**

### Scaling Strategy
```
# NOW (single app)
src/app/models.py          ← all models

# LATER (multi-app)
src/apps/
├── users/models.py        ← User, Profile
├── posts/models.py        ← Post, PostImage, Tag, Like
└── core/utils.py          ← shared utilities
```

---

## 3. Models (один файл models.py)

| Model | Fields | Relations |
|-------|--------|-----------|
| **User** | email✱, username, is_email_verified | AbstractUser |
| **Profile** | full_name, bio, avatar | 1:1 → User |
| **Post** | caption, created_at, updated_at | FK → User, M2M → Tag |
| **PostImage** | image, order, created_at | FK → Post |
| **Tag** | name✱, slug✱ | M2M → Post |
| **Like** | created_at | FK → User + Post (unique) |

✱ = unique

---

## 4. Implementation Phases

### Phase 1: Setup (Day 1)

```bash
uv init djgramm
cd djgramm
uv add django psycopg[binary] pillow python-dotenv gunicorn whitenoise
uv add --dev pytest pytest-django pytest-cov factory-boy ruff
```

**Tasks:**
- Django project в `src/config/`
- Single app `src/app/`
- Docker + docker-compose.yml
- PostgreSQL connection
- `.env.example`

**Deliverable:** `docker compose up` → Django works

---

### Phase 2: Models (Day 2)

**All in `src/app/models.py`:**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    caption = models.TextField(max_length=2200, blank=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/")
    order = models.PositiveIntegerField(default=0)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ["user", "post"]
```

**Signal** в `signals.py` — auto-create Profile.

**Deliverable:** `makemigrations` + `migrate` pass

---

### Phase 3: Admin (Day 3)

**`admin.py`** — register all models:
- UserAdmin + ProfileInline
- PostAdmin + PostImageInline  
- TagAdmin (prepopulated slug)
- LikeAdmin

**Deliverable:** `/admin/` works, CRUD all models

---

### Phase 4: Views & URLs (Day 4-5)

**views.py:**
```python
# Auth
RegisterView, login, logout

# Profile  
ProfileView, ProfileEditView

# Posts
FeedView (ListView, paginate_by=12)
PostDetailView
PostCreateView
PostUpdateView  
PostDeleteView
toggle_like (AJAX)

# Tags
TagPostsView
```

**urls.py:**
```
/                      → feed
/register/             → register
/login/, /logout/      → auth

/profile/<username>/   → profile
/profile/edit/         → edit profile

/post/new/             → create
/post/<pk>/            → detail
/post/<pk>/edit/       → edit
/post/<pk>/delete/     → delete
/post/<pk>/like/       → toggle like

/tag/<slug>/           → posts by tag
```

**Deliverable:** All routes work

---

### Phase 5: Forms + Images (Day 6)

**forms.py:**
- RegistrationForm
- ProfileForm
- PostForm + PostImageFormSet

**services.py:**
- `generate_thumbnail(image, size)`
- `validate_image(file)` — max 10MB, JPEG/PNG/WebP

**Deliverable:** Image upload + thumbnail generation

---

### Phase 6: Templates (Day 7-8)

```
base.html              → layout, navbar, messages
registration/
  login.html           → login form
  register.html        → registration
app/
  feed.html            → posts grid + pagination
  post_detail.html     → single post + likes
  post_form.html       → create/edit form
  profile.html         → user profile
  profile_edit.html    → edit form
```

**Static:** CSS (Tailwind CDN or custom), JS (like toggle)

**Deliverable:** Complete UI

---

### Phase 7: Seed Data (Day 9)

**scripts/seed_data.py** using factories:
- 20 users + profiles
- 100 posts
- 200 images
- 10 tags
- 500 likes

**Deliverable:** Realistic test data

---

### Phase 8: Tests (Day 10-11)

```
tests/
├── conftest.py        → fixtures (client, user, post)
├── factories.py       → UserFactory, PostFactory, etc.
├── test_models.py     → model methods, constraints
├── test_views.py      → all endpoints
└── test_services.py   → image processing
```

**Target:** 80%+ coverage

```bash
uv run pytest --cov=src/app
```

**Deliverable:** Green tests, coverage report

---

### Phase 9: CI/CD (Day 12)

**.gitlab-ci.yml:**
```yaml
stages:
  - lint
  - test
  - build

lint:
  script: uv run ruff check src/

test:
  services:
    - postgres:16
  script: uv run pytest --cov

build:
  script: docker build -t djgramm .
```

**Deliverable:** Pipeline passes

---

### Phase 10: Deploy (Day 13-14)

**Production checklist:**
- [ ] DEBUG=False
- [ ] SECRET_KEY from env
- [ ] ALLOWED_HOSTS
- [ ] WhiteNoise for static
- [ ] PostgreSQL (managed)
- [ ] Media storage (S3/Cloud)
- [ ] HTTPS

**Cloud options:**
1. **Railway** (найпростіший)
2. AWS Free Tier
3. Google Cloud
4. Azure

**Deliverable:** Live app with HTTPS

---

## 5. Environment Variables

```env
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:pass@db:5432/djgramm
```

---

## 6. Timeline

| Phase | Days | Result |
|-------|------|--------|
| Setup | 1 | Docker + Django |
| Models | 1 | 6 models |
| Admin | 1 | Admin panel |
| Views | 2 | All routes |
| Forms | 1 | Image upload |
| Templates | 2 | UI |
| Seed | 1 | Test data |
| Tests | 2 | 80% coverage |
| CI/CD | 1 | Pipeline |
| Deploy | 2 | Live app |
| **Total** | **14** | **MVP** |

---

## 7. Чому Single App?

| Multi-app | Single app |
|-----------|------------|
| 50+ файлів | ~25 файлів |
| 3+ apps | 1 app |
| Складна навігація | Все в одному місці |
| Circular imports | Немає проблем |
| Для великих команд | Для 1-3 розробників |

**Single app ідеальний для:**
- Навчальних проектів
- MVP
- Проектів з 1-3 розробниками
- Швидкої перевірки ментором

**Коли розбивати на apps:**
- Коли модуль можна використати в іншому проекті
- Коли команда > 5 людей
- Коли є чітка bounded context
