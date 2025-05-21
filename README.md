
# ⚖️ Law Firm Management System

A Django-powered web platform to streamline operations for law firms — enabling secure, role-based dashboards for firms, lawyers, and clients, with real-time communication, billing, scheduling, and document management.

---

## 📌 Key Features

- 🔐 **User Authentication & Role Access**: Firms, lawyers, and clients have dedicated accounts and views.
- 📁 **Case Management**: Assign lawyers to cases, track statuses, attach documents.
- 📅 **Calendar Integration**: Case-related events, scheduling tools.
- 💬 **Real-Time Chat**: Case-centric group chat via Pusher.
- 📄 **Document Handling**: Upload and manage client/lawyer documents.
- ⏱️ **Time & Billing Tracking**: Manage billable hours and expenses.
- 📊 **Dashboard Views**: Summary panels for each role type.

---

## 🏗️ Tech Stack

| Layer         | Technology         |
|---------------|--------------------|
| Backend        | Django (Python)    |
| Database       | PostgreSQL         |
| Frontend       | Django Templates + Bootstrap |
| Real-time Chat | Pusher Channels    |
| Config Mgmt    | `.env` + `python-dotenv`    |

---

## 📁 Directory Structure

```
Law-Firm-Management-System/
├── accounts/           # User registration and authentication
├── billing/            # Time and billing logic
├── calendar_app/       # Scheduling and calendar integration
├── cases/              # Case-related models, views, templates
├── chat/               # Real-time messaging logic
├── config/             # Django settings and URLs
├── media/              # Uploaded files (e.g. lawyer profiles)
├── static/             # Static CSS/JS assets
├── .gitignore
├── LICENSE
├── manage.py
├── requirements.txt
└── .env (not committed)  # Sensitive config
```

---

## ⚙️ Setup Instructions

### 1. 🔃 Clone the Repository

```bash
git clone https://github.com/Qambar-12/Law-Firm-Management-System.git
cd Law-Firm-Management-System
```

### 2. 🐍 Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

> If needed, regenerate `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

## 🔐 Environment Configuration

Create a `.env` file at the project root (same level as `manage.py`) and include the following:

```env
# PostgreSQL DB
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email (SMTP)
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True

# Pusher (Realtime chat)
PUSHER_APP_ID=your_pusher_app_id
PUSHER_KEY=your_pusher_key
PUSHER_SECRET=your_pusher_secret
PUSHER_CLUSTER=your_cluster
```

> ✅ Don't forget to add `.env` to your `.gitignore`.

---

## 🛠️ Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🚀 Run the Development Server

```bash
python manage.py runserver
```

Then visit: [http://localhost:8000](http://localhost:8000)

---

## 👥 Roles in the System

| Role     | Capabilities |
|----------|--------------|
| **Law Firm** | Add clients & lawyers, manage contracts & cases |
| **Lawyer**   | View assigned cases, chat, upload documents |
| **Client**   | Track case progress, chat with lawyers |

---

## 🤝 Contribution Guide

1. Fork this repo
2. Create a new feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to your fork (`git push origin feature/my-feature`)
5. Create a Pull Request

---

## 📄 License

MIT License. See [`LICENSE`](./LICENSE) for details.
