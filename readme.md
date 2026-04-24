# RecipeAI — Backend (Flask) + Frontend (Flutter)

Aplikasi pembuatan resep otomatis berbasis AI berdasarkan bahan yang dimasukkan,
dilengkapi kalkulasi kalori per bahan dan total.

---

## Struktur Proyek

```
recipe-app/
├── backend/               # Python Flask API
│   ├── app.py             # Entry point + factory
│   ├── config.py          # Konfigurasi (DB, JWT, LLM)
│   ├── requirements.txt
│   ├── .env.example
│   ├── app.http           # File uji endpoint
│   ├── models/
│   │   ├── user.py
│   │   └── recipe.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   └── recipe_routes.py
│   └── services/
│       └── ai_service.py  # Integrasi LLM API
│
└── frontend/              # Flutter App
    ├── pubspec.yaml
    └── lib/
        ├── main.dart
        ├── core/
        │   ├── constants/api_constants.dart
        │   └── theme/
        │       ├── app_theme.dart
        │       └── theme_notifier.dart
        ├── data/
        │   ├── models/
        │   │   ├── user_model.dart
        │   │   └── recipe_model.dart
        │   └── services/
        │       ├── auth_service.dart
        │       └── recipe_service.dart
        ├── providers/
        │   ├── auth_provider.dart
        │   └── recipe_provider.dart
        └── features/
            ├── auth/
            │   └── login_screen.dart
            └── recipes/
                ├── recipe_screen.dart
                └── recipe_detail_screen.dart
```

---

## Backend — Setup

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Buat file .env

```bash
cp .env.example .env
# Edit .env dan isi LLM_TOKEN dengan token kamu
```

### 3. Jalankan server

```bash
python app.py
```

Server berjalan di `http://localhost:8080`

### Akun default (auto-seed saat pertama run)

- **Username:** `admin`
- **Password:** `admin123`

---

## Frontend — Setup

### 1. Ganti base URL

Edit `lib/core/constants/api_constants.dart`:

```dart
static const String baseUrl = "http://<IP_SERVER_KAMU>:8080";
```

### 2. Install dependencies & run

```bash
cd frontend
flutter pub get
flutter run
```

---

## Alur Fitur

1. User login dengan akun admin
2. Halaman utama menampilkan daftar resep (pagination)
3. Tekan **Generate Resep** → masukkan bahan-bahan (dipisah koma)
4. AI menghasilkan resep lengkap + detail kalori per bahan
5. Resep tersimpan di database dan langsung ditampilkan di detail screen
6. User bisa hapus resep dari list

---

## Endpoint API

| Method | Endpoint          | Keterangan                |
| ------ | ----------------- | ------------------------- |
| POST   | /auth/login       | Login, dapat JWT token    |
| GET    | /auth/me          | Info user aktif           |
| POST   | /recipes/generate | Generate resep dari bahan |
| GET    | /recipes?page=1   | Daftar resep (pagination) |
| GET    | /recipes/:id      | Detail resep              |
| DELETE | /recipes/:id      | Hapus resep               |

---

## Catatan LLM

- `LLM_BASE_URL`: `https://delcom.org/api`
- `LLM_TOKEN`: isi dengan token milikmu di file `.env`
- Model default: `gpt-4o-mini` (bisa diganti di `.env` via `LLM_MODEL`)
