<div align="center">

# TAAB

**An open-source platform for managing shared items and borrowing.**

</div>

---

## Overview

TAAB is a modern borrowing management platform that helps families, teams, schools, and organizations track shared items.

Instead of focusing only on books, TAAB is designed to manage any borrowable item, including books, tools, electronics, board games, cameras, sports equipment, and more.

The goal is to provide a simple, secure, and scalable system for recording ownership, borrowing history, and item availability.

---

## Core Concepts

- Workspace-based architecture
- User authentication with JWT
- Role-based access control
- Borrowing workflow
- Item history
- Invitation system

---

## Features

### Implemented

- JWT Authentication
- Password hashing (bcrypt)
- OAuth2 integration
- SQLAlchemy ORM
- FastAPI REST API

### Planned

- Workspace management
- Member invitations
- Item management
- Borrow & return workflow
- Borrow history
- QR code support
- Statistics dashboard
- Notifications
- Multi-language support

---

## Technology Stack

| Component | Technology |
|----------|------------|
| Backend | FastAPI |
| ORM | SQLAlchemy 2 |
| Database | SQLite (PostgreSQL planned) |
| Authentication | JWT + OAuth2 |
| Password Hashing | bcrypt |
| Validation | Pydantic |
| Server | Uvicorn |

---

## Roadmap

- [x] Project initialization
- [x] Database configuration
- [x] User authentication
- [ ] Workspace model
- [ ] Membership system
- [ ] Item model
- [ ] Borrowing system
- [ ] Search
- [ ] Statistics
- [ ] Notifications
- [ ] Docker support

---

## Project Structure

```text
backend/
│
├── app/
│   ├── auth.py
│   ├── database.py
│   ├── security.py
│   ├── crud/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── main.py
│
├── requirements.txt
└── README.md
```

---

## Getting Started

```bash
git clone https://github.com/TAH000k/TAAB.git

cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Interactive documentation:

```
http://127.0.0.1:8000/docs
```

---

## Project Status

TAAB is currently under active development.

The authentication system has been completed and development is now focused on the core borrowing architecture.

---

## Contributing

Contributions are welcome.

If you would like to improve TAAB, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.
