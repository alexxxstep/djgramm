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

```
djgramm/
├── src/
│   ├── config/          # Django settings, urls, wsgi
│   ├── app/             # Main application (models, views, forms)
│   │   ├── management/  # Management commands
│   │   └── templatetags/ # Custom template tags
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS, images
├── tests/               # Pytest tests
├── docker/              # Docker configs
├── scripts/             # Utility scripts
└── docs/                # Documentation
```

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
- [Deployment Guide](.cursor/HETZNER_DEPLOYMENT_QUICK_START.md) — інструкція з деплою на Hetzner

## License

MIT
