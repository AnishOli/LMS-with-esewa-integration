<div align="center">

<h1>📚 LearnNepal LMS</h1>
<h3>A Full-Featured Learning Management System with eSewa Payment Integration</h3>

<p>
  <img src="https://img.shields.io/badge/Django-6.0.4-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
  <img src="https://img.shields.io/badge/eSewa-60BB46?style=for-the-badge&logo=esewa&logoColor=white" alt="eSewa"/>
</p>

<p>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License: MIT"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"/>
  <img src="https://img.shields.io/github/last-commit/AnishOli/LMS-with-esewa-integration?style=flat-square" alt="Last Commit"/>
</p>

<br/>

> **LearnNepal LMS** is a production-ready Learning Management System built with Django, featuring role-based access control, structured course content delivery, interactive quizzes, peer discussion forums, and fully integrated **eSewa payment gateway** for the Nepali market.

</div>

---

## ✨ Features

### 🔐 Authentication & User Roles
- Email-based authentication (no username required)
- Three distinct roles: **Student**, **Instructor**, and **Admin**
- Custom `AbstractUser` model with role-aware property helpers
- Secure session management with Django's built-in middleware

### 📖 Course Management
- Instructors can **create, edit, and delete** their own courses
- Hierarchical content structure: **Course → Modules → Lessons**
- Lessons support **video URLs** (YouTube/external), **direct video uploads**, **PDF attachments**, and **text content**
- Auto-generated **slugs** for SEO-friendly URLs
- Course **cover images** with Django media handling
- Course **categories** with slug-based filtering

### 🎓 Enrollment & Payments
- **Free course** enrollment with a single click
- **Paid course** flow with full **eSewa v2 payment gateway** integration
  - HMAC-SHA256 signature generation for secure requests
  - Server-side signature **verification** on payment success callback
  - Payment status tracking: `PENDING → COMPLETE / FAILED`
- Prevents duplicate enrollments
- Instructors see a real-time **revenue dashboard** with total students and income

### 🧠 Quizzes
- Module-level quizzes with configurable **passing score** (percentage-based)
- MCQ format: Questions with multiple answer choices, one marked correct
- **Quiz attempt** tracking with score and pass/fail result stored per student

### 💬 Discussion Forums
- Every course automatically gets a **dedicated forum**
- Students and instructors can create **threads** and post **replies**
- Threads ordered by most-recently-updated for active discussion visibility

### 🛡️ Access Control
- Lesson content is gated: only **enrolled students** or the **course instructor** can view lessons
- Instructor dashboard only accessible to users with the `instructor` role
- All sensitive views protected by `@login_required`

---

## 🏗️ Project Architecture

```
LMS/
├── accounts/           # Custom user model, auth views (register/login/logout)
├── courses/            # Course, Module, Lesson models + instructor dashboard
├── enrollments/        # Enrollment, Payment models + eSewa payment flow
├── forums/             # Forum, Thread, Reply models for course discussions
├── quizzes/            # Quiz, Question, Answer, QuizAttempt models
├── lms_project/        # Django project settings, root URL config
├── templates/          # Jinja/Django HTML templates (base + per-app)
├── static/             # CSS, JS, images
├── media/              # User-uploaded files (course covers, videos, PDFs)
└── manage.py
```

### Data Model Overview

```
User (AbstractUser)
 └── role: student | instructor | admin

Category
 └── Course (instructor FK, category FK)
      └── Module (ordered)
           ├── Lesson (video_url / video_file / pdf_file / content)
           └── Quiz
                └── Question
                     └── Answer (is_correct)

Enrollment (student ↔ course, unique_together)
 └── Payment (transaction_uuid, status: PENDING|COMPLETE|FAILED)

Forum (1-to-1 with Course)
 └── Thread (author FK)
      └── Reply (author FK)

QuizAttempt (student FK, quiz FK, score, passed)
```

---

## 💳 eSewa Payment Flow

```
Student clicks "Enroll" on a paid course
        │
        ▼
Enrollment created (is_active=False)
Payment created (status=PENDING, UUID generated)
        │
        ▼
HMAC-SHA256 signature computed
Checkout form submitted to eSewa gateway
        │
        ├─── Success ──► /enrollments/esewa/success/
        │                  Server verifies signature
        │                  Payment → COMPLETE
        │                  Enrollment → is_active=True
        │                  Student redirected to course
        │
        └─── Failure ──► /enrollments/esewa/failure/
                           Error message shown
                           Enrollment remains inactive
```

---

## ⚙️ Tech Stack

| Layer        | Technology                         |
|--------------|------------------------------------|
| Backend      | Django 6.0.4                       |
| Language     | Python 3.x                         |
| Database     | SQLite (dev) / PostgreSQL (prod)   |
| Auth         | Django AbstractUser (email-based)  |
| Payments     | eSewa v2 (HMAC-SHA256)             |
| Media        | Django FileField + ImageField      |
| Templating   | Django Template Language           |
| Static Files | Django Staticfiles                 |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- Git
- A virtual environment tool (`venv` or `virtualenv`)

### 1. Clone the Repository

```bash
git clone https://github.com/AnishOli/LMS-with-esewa-integration.git
cd LMS-with-esewa-integration
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requiremnets.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (or set these directly in `settings.py` for local dev):

```env
SECRET_KEY=your-secret-django-key
DEBUG=True
ESEWA_MERCHANT_CODE=EPAYTEST
ESEWA_SECRET_KEY=8gBm/:&EnhH.1/q
```

> **Note:** The values above are eSewa's **sandbox/test** credentials. Replace with your live merchant credentials for production.

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Navigate to **http://127.0.0.1:8000/** to see the application.

---

## 🗺️ URL Structure

| URL Pattern                            | App          | Description                          |
|----------------------------------------|--------------|--------------------------------------|
| `/`                                    | —            | Home page                            |
| `/admin/`                              | Django Admin | Admin panel                          |
| `/accounts/register/`                  | accounts     | User registration                    |
| `/accounts/login/`                     | accounts     | User login                           |
| `/accounts/logout/`                    | accounts     | User logout                          |
| `/courses/`                            | courses      | Browse all courses                   |
| `/courses/<slug>/`                     | courses      | Course detail page                   |
| `/courses/<slug>/lesson/<id>/`         | courses      | Lesson viewer (enrolled users only)  |
| `/courses/instructor/`                 | courses      | Instructor dashboard                 |
| `/courses/create/`                     | courses      | Create a new course                  |
| `/enrollments/enroll/<course_id>/`     | enrollments  | Initiate enrollment / payment        |
| `/enrollments/esewa/success/`          | enrollments  | eSewa payment success callback       |
| `/enrollments/esewa/failure/`          | enrollments  | eSewa payment failure callback       |
| `/quizzes/...`                         | quizzes      | Quiz attempt and result pages        |

---

## 🔒 Security Highlights

- **HMAC-SHA256 signature verification** on every eSewa callback — prevents spoofed payment confirmations
- **CSRF protection** enabled on all forms via Django middleware
- **Login-required** guards on all sensitive views
- **Enrollment ownership checks** — students can only access courses they're enrolled in
- Instructor actions scoped to their **own courses only** (course edit/delete)

---

## 🛠️ Development Notes

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files (for production)
```bash
python manage.py collectstatic
```

### Creating a Test Instructor Account
1. Register normally via `/accounts/register/`
2. Go to `/admin/` and change the user's role to `instructor`
3. Login and access the instructor dashboard at `/courses/instructor/`

---

## 📦 Dependencies

See [`requiremnets.txt`](./requiremnets.txt) for the full list. Key packages include:

- `Django` — Core web framework
- `Pillow` — Image processing for course cover uploads



## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Anish Oli**

- GitHub: [@AnishOli](https://github.com/AnishOli)
- Repository: [LMS-with-esewa-integration](https://github.com/AnishOli/LMS-with-esewa-integration)

---

<div align="center">
  <p>Made with ❤️ for the Nepali learning community</p>
  <p>⭐ Star this repo if you find it useful!</p>
</div>
