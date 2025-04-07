# TgPostman

**TgPostman** is a Telegram scheduled posting system built with Django, DRF, Celery, and RabbitMQ.  
It allows users to register, connect Telegram chats and channels, and schedule HTML-formatted messages and files to be
sent at a specific time or after a delay.

---

## 🚀 Features

- 🔐 User registration and API key-based authentication
- 💬 Add Telegram chats/channels by ID and validate write access
- 📝 Create scheduled posts with:
    - Text (supports HTML)
    - Files (documents, images, etc.)
    - Multiple destinations (chats/channels)
    - Exact time or delay in seconds
- 👀 Web dashboard for post management
- ⚙️ REST API for integration
- 📦 Asynchronous message sending using Celery + RabbitMQ
- 🌐 Swagger and ReDoc documentation

---

## 🖼️ Tech Stack

- **Backend:** Django + Django REST Framework
- **Queue:** Celery + RabbitMQ
- **DB:** PostgreSQL
- **Docs:** drf-yasg (Swagger/OpenAPI)
- **Deployment:** Docker + docker-compose

---

## 🧑‍💻 Quickstart (Docker)

### 1. Clone the project

```bash
git clone https://github.com/dym-dino/TgPostman.git
cd TgPostman
cp .env.example .env
```

### 2. Set up environment variables

Set up a `.env` 

### 3. Build and run all services

```
docker-compose up --build
```

### 4. Access the project

| URL                                | Description                                |
|------------------------------------|--------------------------------------------|
| `http://localhost:8000/`           | Web dashboard (user panel)                 |
| `http://localhost:8000/login/`     | Login page                                 |
| `http://localhost:8000/register/`  | User registration                          |
| `http://localhost:8000/swagger/`   | Swagger UI for API                         |
| `http://localhost:8000/redoc/`     | ReDoc documentation                        |
| `http://localhost:8000/code_docs/` | Sphinx documentation                        |
| `http://localhost:15672/`          | RabbitMQ Management UI (`guest` / `guest`) |

---

### 5. (Optional) Create superuser

To access the Django admin interface:

```bash
docker-compose exec django python manage.py createsuperuser
```

Then visit: http://localhost:8000/admin/

---

## 🧪 Testing

### With Docker:

```bash
docker-compose exec django pytest
```

---

## 🧾 License

MIT License. See [LICENSE](LICENSE) file.

---