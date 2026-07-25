# TAAB

An open-source platform for managing shared items and borrowing.

---

## Overview

TAAB is designed to help families, friends, schools, and organizations manage shared items and keep track of borrowing activities.

The platform provides a secure and scalable backend for organizing items, managing members, and recording borrowing history.

---

## Features

### Current

- User authentication
- JWT access tokens
- OAuth2 authentication flow
- Password hashing with bcrypt
- RESTful API built with FastAPI

### Planned

- Workspace management
- Member invitations
- Item management
- Borrowing and returning
- Borrow history
- Search
- Notifications
- QR code support
- Statistics dashboard

---

## Tech Stack

- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT
- Passlib
- Uvicorn

---

## Roadmap

- [x] Backend setup
- [x] Database configuration
- [x] Authentication
- [x] Item management
- [ ] Borrowing system
- [ ] Notifications
- [ ] Statistics
- [ ] Workspace system
- [ ] Membership system
- [ ] Docker support

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

API:

```
http://127.0.0.1:8000
```

Documentation:

```
http://127.0.0.1:8000/docs
```

---

## Contributing

Contributions are welcome. Feel free to open an issue or submit a pull request.

---

## License

MIT License
