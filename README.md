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
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 3. SSL Certificates

Place your SSL certificates in `docker/certs/`:

- `fullchain.pem`
- `privkey.pem`

Then uncomment HTTPS configuration in `docker/nginx.conf`.

## Project Structure

```
djgramm/
├── src/
│   ├── config/          # Django settings
│   ├── app/             # Main application
│   ├── templates/       # HTML templates
│   └── static/          # Static files
├── tests/               # Pytest tests
├── docker/              # Docker configs
├── scripts/             # Utility scripts
└── docs/                # Documentation
```

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
