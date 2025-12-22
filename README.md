# DJGramm

Instagram-like photo sharing application built with Django.

## Tech Stack

- **Backend:** Python 3.12+, Django 5.x
- **Frontend:** Webpack, Tailwind CSS, ES6 Modules
- **Database:** PostgreSQL 16
- **Package Manager:** UV (Python), npm (Node.js)
- **Containerization:** Docker + Docker Compose
- **Web Server:** Nginx + Gunicorn
- **CI/CD:** GitLab CI, GitHub Actions

## Quick Start

### Prerequisites

- Python 3.12+, UV, Node.js 20+, npm, Docker & Docker Compose

### Development Setup

```bash
# Clone and install
git clone <repository-url>
cd djgramm

# Install Python dependencies
uv sync

# Install Node.js dependencies
npm install

# Build frontend assets
npm run build

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start database
docker compose up db -d

# Run migrations and create superuser
cd src
uv run python manage.py migrate
uv run python manage.py createsuperuser

# (Optional) Seed test data
uv run python ../scripts/seed_data.py
uv run python manage.py sync_tags

# Build frontend assets (in watch mode for development)
npm run dev

# In another terminal, run development server
uv run python manage.py runserver 9000
```

Open: http://127.0.0.1:9000/

**Note:** For development, run `npm run dev` in watch mode to automatically rebuild frontend assets on changes.

### Docker Development

```bash
# Build and run
docker compose up --build

# Execute commands
docker compose exec web uv run python manage.py createsuperuser
docker compose exec web uv run python manage.py sync_tags
```

## Features

- **User Authentication** — Email-based registration and login
- **Photo Posts** — Upload multiple images per post (up to 10) with drag & drop
- **Image Carousel** — Navigate through multiple images with keyboard/swipe support
- **Comments** — Add, edit, and delete comments on posts
- **Likes** — AJAX-powered like/unlike functionality
- **Hashtags** — Automatic tag extraction from captions (`#tag`)
- **Tag Filtering** — Browse posts by tags
- **User Profiles** — View and edit profiles with avatars
- **Admin Panel** — Full Django admin interface

### Automatic Tag Extraction

Hashtags in captions are automatically extracted and converted to clickable tags:

- **Example:** `"Beautiful #sunset #travel photos!"`
- **Result:** Tags `sunset` and `travel` are created and linked to the post
- **For existing posts:** Run `python manage.py sync_tags`

## Frontend Development

```bash
# Build frontend assets (production)
npm run build

# Build frontend assets (development with watch mode)
npm run dev

# Analyze bundle size
npm run build:analyze
```

## Testing

```bash
# Run tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=src/app --cov-report=term-missing

# Linting
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Production Deployment

### 1. Environment Configuration

Create `.env.prod`:

```env
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
POSTGRES_DB=djgramm
POSTGRES_USER=djgramm_user
POSTGRES_PASSWORD=secure-password-here
SECURE_SSL_REDIRECT=True
```

### 2. Deploy

```bash
# Build and start (frontend assets are built automatically in Dockerfile)
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker-compose.prod.yml exec web uv run python manage.py migrate
docker compose -f docker-compose.prod.yml exec web uv run python manage.py createsuperuser
```

**Note:** Frontend assets are automatically built during Docker image build process.

### 3. SSL Certificates

Place SSL certificates in `docker/certs/`:

- `fullchain.pem`
- `privkey.pem`

Then uncomment HTTPS configuration in `docker/nginx.conf`.

## Project Structure

### Current Structure (after TASK14)

```
djgramm/
├── frontend/                    # ✨ Frontend build system
│   ├── src/                    # Source files for webpack
│   │   ├── js/                 # JavaScript modules
│   │   │   ├── index.js       # Entry point
│   │   │   ├── feed.js        # Feed functionality
│   │   │   ├── follow.js      # Follow/unfollow
│   │   │   ├── post_detail.js # Post detail page
│   │   │   ├── post_form.js   # Post creation form
│   │   │   ├── theme.js       # Dark/light theme
│   │   │   └── utils/         # Shared utilities
│   │   │       ├── csrf.js    # CSRF token helpers
│   │   │       ├── ajax.js    # AJAX utilities
│   │   │       ├── errorHandler.js
│   │   │       └── eventManager.js
│   │   └── css/               # CSS source files
│   │       └── main.css       # Tailwind directives
│   ├── dist/                   # Built files (gitignored)
│   │   ├── main.js            # Compiled JavaScript bundle
│   │   ├── styles.css         # Compiled Tailwind CSS
│   │   └── *.chunk.js         # Code-split chunks
│   └── tests/                  # Frontend tests (Jest)
├── src/
│   ├── config/                 # Django settings, urls, wsgi
│   ├── app/                    # Main application
│   │   ├── management/        # Management commands
│   │   └── templatetags/      # Custom template tags
│   ├── templates/             # HTML templates
│   │   └── base.html          # Base template (uses compiled assets)
│   └── static/                 # Django static files
│       └── dist/              # Copied from frontend/dist (via collectstatic)
├── tests/                       # Pytest tests
├── docker/                     # Docker configs
├── scripts/                     # Utility scripts
├── docs/                        # Documentation
├── package.json                 # ✨ Node.js dependencies
├── webpack.config.js            # ✨ Webpack configuration
├── tailwind.config.js          # ✨ Tailwind CSS configuration
└── postcss.config.js           # ✨ PostCSS configuration
```

### Previous Structure (before TASK14)

```
djgramm/
├── src/
│   ├── config/                 # Django settings, urls, wsgi
│   ├── app/                    # Main application
│   │   ├── management/
│   │   └── templatetags/
│   ├── templates/              # HTML templates
│   │   └── base.html          # Used Tailwind CDN
│   └── static/                 # Static files (uncompiled)
│       ├── js/                 # Individual JS files
│       │   ├── main.js
│       │   ├── follow.js
│       │   ├── feed.js
│       │   └── post_detail.js
│       └── css/
│           └── style.css
├── tests/
├── docker/
├── scripts/
└── docs/
```

### Key Changes

**New directories:**

- `frontend/` — централізована папка для frontend розробки
  - `frontend/src/` — вихідні файли (JS, CSS модулі)
  - `frontend/dist/` — зібрані файли (створюються webpack, gitignored)
  - `frontend/tests/` — тести для JavaScript модулів

**Reorganized files:**

- JavaScript файли переміщені з `src/static/js/` → `frontend/src/js/`
- Створено модульну структуру з утилітами (`utils/`)
- CSS з Tailwind директивами в `frontend/src/css/main.css`

**New configuration files:**

- `package.json` — Node.js залежності та npm скрипти
- `webpack.config.js` — налаштування збірки з оптимізаціями
- `tailwind.config.js` — конфігурація Tailwind з content paths
- `postcss.config.js` — інтеграція Tailwind та Autoprefixer

**Build process:**

```
frontend/src/  →  webpack  →  frontend/dist/  →  collectstatic  →  src/static/dist/
(source files)    (build)      (compiled)         (Django)          (served)
```

**Benefits:**

- ✅ Модульна організація коду (ES6 modules)
- ✅ Автоматична оптимізація (мініфікація, tree shaking)
- ✅ Локальна збірка Tailwind (замість CDN)
- ✅ Code splitting для кращого кешування
- ✅ Централізовані утиліти (видалено дублювання)

## Management Commands

```bash
# Sync tags from captions for all existing posts
uv run python manage.py sync_tags

# Dry run
uv run python manage.py sync_tags --dry-run
```

## API Endpoints

| URL                               | Method   | Description           |
| --------------------------------- | -------- | --------------------- |
| `/`                               | GET      | Feed (posts list)     |
| `/register/`                      | GET/POST | User registration     |
| `/login/`                         | GET/POST | User login            |
| `/logout/`                        | POST     | User logout           |
| `/profile/<username>/`            | GET      | User profile          |
| `/profile/edit/`                  | GET/POST | Edit profile          |
| `/post/new/`                      | GET/POST | Create post           |
| `/post/<pk>/`                     | GET      | Post detail           |
| `/post/<pk>/edit/`                | GET/POST | Edit post             |
| `/post/<pk>/delete/`              | POST     | Delete post           |
| `/post/<pk>/like/`                | POST     | Toggle like (AJAX)    |
| `/post/<pk>/comment/`             | POST     | Add comment (AJAX)    |
| `/post/<pk>/comment/<id>/edit/`   | POST     | Edit comment (AJAX)   |
| `/post/<pk>/comment/<id>/delete/` | POST     | Delete comment (AJAX) |
| `/post/<pk>/reorder-images/`      | POST     | Reorder images (AJAX) |
| `/tag/<slug>/`                    | GET      | Posts by tag          |
| `/admin/`                         | GET      | Admin panel           |

## Test Accounts

After running seed script:

| Role  | Email             | Password    |
| ----- | ----------------- | ----------- |
| Admin | admin@djgramm.net | admin       |
| User  | user1@example.com | testpass123 |

## Documentation

- [Implementation Plan](docs/TASK12_PLAN.md) — детальний план реалізації проекту
- [UML Schema](docs/UML_SCHEMA.md) — діаграма моделей даних
- [Frontend Build Plan](docs/TASK14_PLAN.md) — план налаштування webpack та Tailwind CSS
- [Deployment Guide](.cursor/HETZNER_DEPLOYMENT_QUICK_START.md) — інструкція з деплою на Hetzner

## TASK14 Implementation Summary

**Frontend Build System** — реалізовано повну інтеграцію webpack та Tailwind CSS згідно з [планом](docs/TASK14_PLAN.md).

### Основні зміни:

**Структура проекту:**

- Створено `frontend/` директорію з `src/` (вихідні файли) та `dist/` (зібрані файли)
- JavaScript модулі переміщені в `frontend/src/js/` з модульною структурою
- Створено утиліти в `frontend/src/js/utils/` (CSRF, AJAX, error handling, event management)
- CSS файли в `frontend/src/css/` з Tailwind директивами

**Конфігурація:**

- `package.json` — Node.js залежності та npm скрипти
- `webpack.config.js` — налаштування збірки з мініфікацією та code splitting
- `tailwind.config.js` — конфігурація Tailwind з правильними content paths
- `postcss.config.js` — інтеграція Tailwind та Autoprefixer

**Django інтеграція:**

- Оновлено `src/config/settings.py` — `STATICFILES_DIRS` вказує на `frontend/dist`
- Оновлено `src/templates/base.html` — замінено Tailwind CDN на локальні зібрані файли
- Оновлено `.gitignore` — додано `node_modules/`, `frontend/dist/`

**Docker та деплой:**

- Оновлено `docker/Dockerfile.prod` — додано multi-stage build з frontend-builder
- Автоматична збірка frontend під час створення Docker образу
- Валідація зібраних файлів перед `collectstatic`

**Оптимізації:**

- Tree shaking для видалення невикористаного коду
- Мініфікація JavaScript та CSS в production
- Code splitting для окремих chunk файлів
- Централізовані утиліти (видалено дублювання CSRF функцій)
- Event delegation для динамічних елементів

**Тестування:**

- Додано тести для static files (`tests/test_static_files.py`)
- Перевірка наявності зібраних файлів після збірки

Детальний план реалізації: [docs/TASK14_PLAN.md](docs/TASK14_PLAN.md)

## License

MIT
