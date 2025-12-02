# DJGramm

Instagram-like photo sharing application built with Django.

## Tech Stack

- **Backend:** Python 3.12+, Django 5.x
- **Database:** PostgreSQL 16
- **Package Manager:** UV
- **Containerization:** Docker + Docker Compose
- **Web Server:** Nginx + Gunicorn
- **CI/CD:** GitLab CI

## Quick Start (Development)

### Prerequisites

- Python 3.12+
- UV package manager
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd djgramm

# Install dependencies
uv sync
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Database

```bash
docker compose up db -d
```

### 4. Run Migrations

```bash
cd src
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

### 5. Seed Data (Optional)

```bash
uv run python ../scripts/seed_data.py

# Sync tags from existing posts (if posts were created before tag extraction feature)
uv run python manage.py sync_tags
```

### 6. Run Development Server

```bash
uv run python manage.py runserver 9000
```

Open: http://127.0.0.1:9000/

## Development with Docker

```bash
# Build and run
docker compose up --build

# Access: http://localhost:9000

# View logs
docker compose logs -f web

# Stop
docker compose down

# Execute commands in container
docker compose exec web uv run python manage.py createsuperuser
docker compose exec web uv run python manage.py sync_tags
```

## Testing

```bash
# Run all tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=src/app --cov-report=term-missing

# Run linting
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Production Deployment

### 1. Configure Environment

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

### 2. Deploy with Docker Compose

```bash
# Build and start
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations
docker compose -f docker-compose.prod.yml exec web uv run python manage.py migrate

# Create superuser
docker compose -f docker-compose.prod.yml exec web uv run python manage.py createsuperuser

# Sync tags for existing posts (if needed)
docker compose -f docker-compose.prod.yml exec web uv run python manage.py sync_tags
```

### 3. SSL Certificates

Place your SSL certificates in `docker/certs/`:

- `fullchain.pem`
- `privkey.pem`

Then uncomment HTTPS configuration in `docker/nginx.conf`.

## Features

- **User Authentication** — Email-based registration and login
- **Photo Posts** — Upload multiple images per post with captions
- **Automatic Tag Extraction** — Hashtags in captions (`#tag`) are automatically extracted and linked
- **Likes** — AJAX-powered like/unlike functionality
- **User Profiles** — View and edit user profiles
- **Tag Filtering** — Browse posts by tags
- **Admin Panel** — Full Django admin interface

### Automatic Tag Extraction

When creating or editing a post, hashtags in the caption are automatically extracted and converted to tags:

- **Example:** `"Beautiful #sunset #travel photos!"`
- **Result:** Tags `sunset` and `travel` are created (if they don't exist) and linked to the post
- **UI:** Hashtags become clickable links that filter posts by tag

**For existing posts:** Run `python manage.py sync_tags` to extract tags from posts created before this feature was implemented.

## Project Structure

```
djgramm/
├── src/
│   ├── config/          # Django settings
│   ├── app/             # Main application
│   │   ├── management/  # Management commands
│   │   └── templatetags/ # Custom template tags
│   ├── templates/       # HTML templates
│   └── static/          # Static files
├── tests/               # Pytest tests
├── docker/              # Docker configs
├── scripts/             # Utility scripts
└── docs/                # Documentation
```

## Management Commands

```bash
# Sync tags from captions for all existing posts
uv run python manage.py sync_tags

# Dry run (show what would be synced)
uv run python manage.py sync_tags --dry-run
```

## Documentation

- [Implementation Plan](docs/TASK12_PLAN.md) — детальний план реалізації проекту з усіма фазами
- [UML Schema](docs/UML_SCHEMA.md) — діаграма моделей даних
- [Tag Extraction Plan](.cursor/TAG_EXTRACTION_PLAN.md) — план автоматичного витягування тегів

## API Endpoints

| URL                    | Method   | Description        |
| ---------------------- | -------- | ------------------ |
| `/`                    | GET      | Feed (posts list)  |
| `/register/`           | GET/POST | User registration  |
| `/login/`              | GET/POST | User login         |
| `/logout/`             | POST     | User logout        |
| `/profile/<username>/` | GET      | User profile       |
| `/profile/edit/`       | GET/POST | Edit profile       |
| `/post/new/`           | GET/POST | Create post        |
| `/post/<pk>/`          | GET      | Post detail        |
| `/post/<pk>/edit/`     | GET/POST | Edit post          |
| `/post/<pk>/delete/`   | POST     | Delete post        |
| `/post/<pk>/like/`     | POST     | Toggle like (AJAX) |
| `/tag/<slug>/`         | GET      | Posts by tag       |
| `/admin/`              | GET      | Admin panel        |

## Test Accounts

After running seed script:

| Role  | Email             | Password    |
| ----- | ----------------- | ----------- |
| Admin | admin@djgramm.net | admin       |
| User  | user1@example.com | testpass123 |

## License

MIT
