# TAAB

An open-source platform for managing shared items and borrowing.

---

## Overview

TAAB is an open-source borrowing platform that helps families, friends, schools, clubs, and organizations manage shared items and track borrowing activities.

The project focuses on simplicity, transparency, and scalability while providing a clean REST API built with FastAPI.

---

## Features

### Implemented

### Authentication
- User registration
- User login
- JWT authentication
- OAuth2 password flow
- Password hashing with bcrypt
- Current user endpoint

### Item Management
- Create items
- View owned items
- Item categories
- Availability status
- Current borrow status
- Optimized query serialization (N+1 query prevention)
- Soft delete

### Borrowing (TAAB Workflow)
- Create borrow requests
- View sent requests
- View received requests
- Accept borrow requests
- Reject borrow requests
- Automatic rejection of competing pending requests
- Borrow ownership validation
- Two-way handover confirmation
- Two-way return confirmation
- Cancel pending/accepted requests
- Dispute management and resolution
- Strict active request constraints (Database & Logic level)

### Testing
- Comprehensive automated testing using pytest
- Complete lifecycle and edge-case coverage

---

### Planned

### Item Management
- Image upload
- Item search
- Item filtering

### Workspace
- Multiple workspaces
- Member invitations
- Roles & permissions

### Notifications
- Borrow request notifications
- Return reminders

### Dashboard
- Statistics
- Borrow analytics
- Borrow history

### Extras
- QR code support
- Docker deployment
- PostgreSQL support
- CI/CD integration

---

## Tech Stack

- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Alembic
- JWT
- Passlib (bcrypt)
- Uvicorn
- Pytest

---

## Project Status

Current version:

**Backend MVP in progress**

Implemented:

- Authentication
- Item management
- Borrow request workflow
- Full borrow lifecycle (Two-way confirmation & Disputes)
- Automated testing

Currently working on:

- Soft delete
- Image upload
- Frontend

---

## API

Swagger UI

```
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
```

OpenAPI

```
[http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
```

---

## Getting Started

```bash
git clone [https://github.com/TAH000k/TAAB.git](https://github.com/TAH000k/TAAB.git)

cd backend

python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

alembic upgrade head

# Run the server
uvicorn app.main:app --reload

# Run the automated tests
python -m pytest -v
```

---

## Roadmap

- [x] Backend setup
- [x] Database configuration
- [x] Authentication
- [x] User management
- [x] Item management
- [x] Borrow request workflow
- [x] Borrow lifecycle (Handover, Return, Dispute)
- [x] Automated Testing
- [x] Validation
- [x] Soft delete
- [ ] Image upload
- [ ] Search
- [ ] Notifications
- [ ] Workspace system
- [ ] Roles & permissions
- [ ] Statistics dashboard
- [ ] Frontend
- [ ] Docker
- [ ] PostgreSQL

---

## Contributing

Contributions, issues, and feature requests are welcome.

If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

## License

MIT License