# MaDongDong Blog

[中文](README.md)

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

A full-stack, frontend-backend separated blog system built on `FastAPI + Vue 3 + SQLite`, supporting public-facing display and admin management. Supports three languages: Chinese, English, and Japanese.

## Features

### Backend (FastAPI)

- Health check, app lifecycle initialization, and first-run installation wizard
- Installation wizard configures: site domain (auto-detected), JWT signing key (auto-generated), database connection (SQLite by default)
- On completion, settings are auto-written to `.env`; domain config auto-generates 4 CORS variants (http/https × domain/www.domain)
- JWT login authentication and role-based authorization (admin / author / reader)
- Fine-grained capability permission system: 15 capabilities with `require_capability()` decorator support
- CSRF protection (double-submit cookie pattern, protecting all write requests)
- Article capabilities: create / update / approve / reject / auto-summary / scheduled publish / revision history
- Article slug URLs: `/article/{slug}`, auto-generated, regenerated on title change
- Article trash: delete → soft-delete → restore / permanent delete
- Article locking: prevents concurrent editing (15-minute auto-expiry, unlockable by lock owner or admin)
- Category management (CRUD, hierarchical categories supported)
- Tag management (CRUD)
- Media library management (file upload, auto image resolution extraction, folder management, bulk move/delete)
- Comment management and moderation (approve / reject / permanent delete / spam mark / trash)
- Friend link management (public submission, admin review/edit/delete)
- Site config and navigation item management (incl. homepage hero image, background music, footer copyright/ICP/police filing info)
- Server-level config management (domain, JWT key, database connection, upload directory)
- User management (create/edit/delete/bulk role change)
- Application passwords (API auth enhancement, create/delete/query)
- Profile update (avatar base64 storage, nickname, email, password)
- Public web endpoints: home / article detail / search / comment submission / friend links / archive / categories / tags
- RSS Feed (`/api/v1/web/rss`), Sitemap (`/api/v1/web/sitemap.xml`), and robots.txt (`/api/v1/web/robots.txt`)
- View deduplication (same IP counts only once per article per 24 hours)
- Rate limiting (per-endpoint config, brute-force protection)
- Login failure lockout (DB-persisted, 6 failures = 15-minute lock, auto-cleanup on startup)
- Math CAPTCHA (HMAC-signed, prevents bulk registration and brute-force)
- Cookie isolation (admin / web frontends use separate cookie namespaces)
- Automatic database migration (new columns added on startup)
- URL 301 redirect system (trailing slash removal, lowercase path normalization, www/non-www redirect)
- Old slug redirect (old slugs saved on title change, 301 redirect supported)

### Web Frontend (Vue 3)

- Responsive layout, dark mode toggle
- Homepage hero image, background music player (BGM), hot articles sidebar
- Article detail page: Markdown rendering, table of contents, view count, tag list, prev/next navigation
- Comment system: supports anonymous and logged-in submissions, Markdown preview, review status display
- Search: real-time overlay search with keyboard navigation
- Archive page: collapsible year/month grouping
- Categories page: hierarchical category display with article count
- Tag page: article list filtered by tag
- Friend links page: displays approved links + submission form
- User auth: login / register / profile update / logout
- i18n: Chinese / English / Japanese switchable
- RSS Feed, Sitemap, robots.txt

### Admin Frontend (Vue 3)

- JWT-based login, auto-redirect on expiry
- Dashboard shell with sidebar navigation (single-page, no full reloads)
- Article management: rich Markdown editor (Vditor), publish / draft / scheduled publish / revision history / lock status
- Category & tag management
- Media library: upload, folder management, bulk operations
- Comment moderation: approve / reject / spam / trash
- User management: create / edit / delete / bulk role change
- Friend link management: review / edit / delete
- Site config: title, subtitle, logo, hero image, BGM, footer, ICP/police filing, CORS domain
- Server config: domain, JWT key, database URL, upload dir
- Application passwords management

## Security Features

- **Authentication**: JWT (RS256-style signing), refresh token rotation, login lockout (6 failures → 15-min lock)
- **Request Protection**: CSRF double-submit cookie on all write requests, per-endpoint rate limiting
- **Input Validation**: Pydantic schemas at API boundary, XSS filtering on comment HTML
- **XSS Protection**: DOMPurify sanitization for all user-generated content rendered in the browser
- **Other Security Headers**: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`
- **CORS**: Origin allowlist auto-generated from site domain (4 variants), no wildcard in production

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Framework | FastAPI (Python 3.13+) |
| ORM | SQLAlchemy 2 (async) |
| Database | SQLite (aiosqlite) |
| Auth | JWT (python-jose) |
| Validation | Pydantic v2 |
| Server | Uvicorn |

### Frontend
| Layer | Technology |
|---|---|
| Framework | Vue 3 + Vite |
| Language | TypeScript |
| Routing | Vue Router 4 |
| Markdown (web) | md-editor-v3 (read-only) + marked + DOMPurify |
| Markdown (admin) | Vditor |
| i18n | vue-i18n |

## Project Structure

```
madongdong/
├── app/                        # FastAPI backend
│   ├── api/
│   │   ├── admin/              # Protected admin endpoints
│   │   ├── web.py              # Public web endpoints
│   │   └── install.py          # Installation wizard
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── database.py         # Async SQLAlchemy engine
│   │   ├── security.py         # JWT + role/capability guards
│   │   └── init_db.py          # DB init + seed on startup
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic layer
│   └── utils/                  # Shared utilities (response helpers, etc.)
├── web/                        # Public-facing Vue 3 frontend (port 5173)
│   └── src/
│       ├── views/              # Page components
│       ├── components/         # Shared UI components
│       ├── api.ts              # Centralized API client
│       ├── router.ts           # Routes + install-check guard
│       ├── types.ts            # Shared TypeScript types
│       └── locales/            # i18n message files
├── admin/                      # Admin dashboard Vue 3 frontend (port 5174)
│   └── src/
│       ├── views/              # Admin panel components
│       ├── api.ts              # Admin API client
│       └── router.ts           # Admin routes + auth guard
├── assets/                     # Shared utilities (resolveAssetUrl, etc.)
├── scripts/                    # Build-time scripts (URL safety scanner)
└── docs/                       # Documentation assets
```

## Local Development Setup

### 1. Backend

```bash
# Clone and enter project root
git clone https://github.com/Lumosylva/madongdong.git
cd madongdong

# Create and activate virtual environment
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and edit as needed
cp .env.example .env

# Start backend (auto-reloads on file change)
uvicorn app.main:app --reload
# API available at http://127.0.0.1:8000
```

`.env` minimum config:
```env
SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite+aiosqlite:///./madongdong.db
UPLOAD_DIR=app/static/uploads
```

### 2. Web Frontend

```bash
cd web
cp .env.example .env   # or create manually
npm install
npm run dev
# http://127.0.0.1:5173
```

`web/.env`:
```env
VITE_API_BASE=/api/v1
VITE_ADMIN_BASE_PATH=/admin
```

### 3. Admin Frontend

```bash
cd admin
cp .env.example .env
npm install
npm run dev
# http://127.0.0.1:5174
```

`admin/.env`:
```env
VITE_API_BASE=/api/v1
VITE_WEB_BASE_URL=
```

### 4. First-Run Installation

On first launch, navigate to `http://127.0.0.1:5173` — you will be automatically redirected to the installation wizard at `/install`. Complete the three-step wizard to initialize the site, create the admin account, and configure optional settings (ICP filing, copyright, comment moderation).

## Default Admin Account

After the installation wizard completes, log in to the admin panel at `http://127.0.0.1:5174` using the credentials you set during installation. The wizard auto-writes all settings to `.env` — no manual editing required.

## API Reference

All API endpoints are prefixed with `/api/v1`. Responses follow a unified envelope format via `app/utils/response.py`.

### Installation

| Method | Path | Description |
|--------|------|-------------|
| GET | `/install/status` | Check installation status |
| POST | `/install` | Run installation wizard |

### Admin Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/admin/auth/login` | Admin login (returns JWT) |
| GET | `/admin/auth/me` | Get current user info |
| POST | `/admin/auth/logout` | Logout |
| POST | `/admin/auth/captcha` | Get math CAPTCHA |

### User Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/users` | List users |
| POST | `/admin/users` | Create user |
| PUT | `/admin/users/{id}` | Update user |
| DELETE | `/admin/users/{id}` | Delete user |
| POST | `/admin/users/bulk-role` | Bulk change roles |
| GET/POST/DELETE | `/admin/users/me/app-passwords` | Application passwords |

### Articles

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/articles` | List articles (paginated, filterable) |
| POST | `/admin/articles` | Create article |
| GET | `/admin/articles/{id}` | Get article detail |
| PUT | `/admin/articles/{id}` | Update article |
| DELETE | `/admin/articles/{id}` | Soft delete (move to trash) |
| POST | `/admin/articles/{id}/publish` | Publish article |
| POST | `/admin/articles/{id}/approve` | Approve article |
| POST | `/admin/articles/{id}/reject` | Reject article |
| POST | `/admin/articles/{id}/restore` | Restore from trash |
| DELETE | `/admin/articles/{id}/permanent` | Permanently delete |
| GET | `/admin/articles/{id}/revisions` | Revision history |
| POST | `/admin/articles/{id}/lock` | Lock article |
| DELETE | `/admin/articles/{id}/lock` | Unlock article |

### Categories & Tags

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/admin/categories` | List / create categories |
| PUT/DELETE | `/admin/categories/{id}` | Update / delete category |
| GET/POST | `/admin/tags` | List / create tags |
| PUT/DELETE | `/admin/tags/{id}` | Update / delete tag |

### Media

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/media` | List media files |
| POST | `/admin/media/upload` | Upload file |
| DELETE | `/admin/media/{id}` | Delete file |
| POST | `/admin/media/bulk-move` | Bulk move to folder |
| POST | `/admin/media/bulk-delete` | Bulk delete |
| GET/POST/DELETE | `/admin/media/folders` | Folder management |

### Comments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/comments` | List comments |
| POST | `/admin/comments/{id}/approve` | Approve |
| POST | `/admin/comments/{id}/reject` | Reject |
| POST | `/admin/comments/{id}/spam` | Mark as spam |
| DELETE | `/admin/comments/{id}` | Permanent delete |

### Friend Links

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/friend-links` | List friend links |
| POST | `/admin/friend-links` | Create friend link |
| PUT | `/admin/friend-links/{id}` | Update |
| DELETE | `/admin/friend-links/{id}` | Delete |

### Site Config

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/site-config` | Get site config |
| PUT | `/admin/site-config` | Update site config |
| GET/POST/PUT/DELETE | `/admin/site-config/nav-items` | Navigation items |
| GET/PUT | `/admin/server-config` | Server-level config |

### Public Web Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/web/home` | Homepage data |
| GET | `/web/articles/{slug}` | Article detail by slug |
| GET | `/web/search` | Full-text search |
| POST | `/web/comments` | Submit comment |
| GET | `/web/friend-links` | Public friend links |
| POST | `/web/friend-links` | Submit friend link application |
| GET | `/web/archive` | Archive list |
| GET | `/web/categories` | Category tree |
| GET | `/web/categories/{slug}` | Articles by category |
| GET | `/web/tags/{slug}` | Articles by tag |
| GET | `/web/rss` | RSS Feed |
| GET | `/web/sitemap.xml` | Sitemap |
| GET | `/web/robots.txt` | robots.txt |
| POST | `/web/auth/login` | Web user login |
| POST | `/web/auth/register` | Web user register |
| GET | `/web/auth/me` | Current web user |
| PUT | `/web/auth/profile` | Update profile |

## Role Permission Matrix

| Permission | Admin | Author | Reader |
|------------|:-----:|:------:|:------:|
| Publish articles | ✓ | ✓ | — |
| Approve / reject articles | ✓ | — | — |
| Manage all users | ✓ | — | — |
| Manage categories & tags | ✓ | ✓ | — |
| Manage media library | ✓ | ✓ | — |
| Moderate comments | ✓ | — | — |
| Manage friend links | ✓ | — | — |
| Update site config | ✓ | — | — |
| Update server config | ✓ | — | — |
| Submit comments | ✓ | ✓ | ✓ |
| Update own profile | ✓ | ✓ | ✓ |

## Deployment

### Development

```bash
# Terminal 1 — backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2 — web frontend
cd web && npm run dev

# Terminal 3 — admin frontend
cd admin && npm run dev
```

### Production (Nginx + Uvicorn)

```bash
# Build both frontends
cd web && npm run build
cd admin && npm run build

# Start backend with multiple workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Nginx config example:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    # Admin frontend (built output)
    location /admin/ {
        alias /path/to/madongdong/admin/dist/;
        try_files $uri $uri/ /admin/index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static uploads
    location /uploads/ {
        alias /path/to/madongdong/app/static/uploads/;
    }

    # Web frontend (built output, catch-all)
    location / {
        root /path/to/madongdong/web/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

### Docker

```bash
# Build image
docker build -t madongdong .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/madongdong.db:/app/madongdong.db \
  -v $(pwd)/uploads:/app/app/static/uploads \
  --env-file .env \
  madongdong
```

## URL Risk Scan

Both frontends run a hardcoded URL safety check before every build:

```bash
node ../scripts/check-hardcoded-urls.mjs
```

The scanner detects `http://`, `ws://`, `localhost:`, `127.0.0.1:`, and absolute domain strings in source files. The build fails if any disallowed patterns are found. Allowed patterns and scanned directories are configured in `scripts/check-hardcoded-urls.config.json` — edit that file only; do not modify the script itself.

## Preview

<table>
<tr>
<td><img src="assets/images/01.png" width="360"/></td>
<td><img src="assets/images/02.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/03.png" width="360"/></td>
<td><img src="assets/images/04.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/05.png" width="360"/></td>
<td><img src="assets/images/06.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/07.png" width="360"/></td>
<td><img src="assets/images/08.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/09.png" width="360"/></td>
<td><img src="assets/images/10.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/11.png" width="360"/></td>
<td><img src="assets/images/12.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/13.png" width="360"/></td>
<td><img src="assets/images/14.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/15.png" width="360"/></td>
<td><img src="assets/images/16.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/17.png" width="360"/></td>
<td><img src="assets/images/18.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/19.png" width="360"/></td>
<td><img src="assets/images/20.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/21.png" width="360"/></td>
<td><img src="assets/images/22.png" width="360"/></td>
</tr>
<tr>
<td><img src="assets/images/23.png" width="360"/></td>
<td><img src="assets/images/24.png" width="360"/></td>
</tr>
</table>

## Changelog

### 2026-07-03
- Web frontend: add article QR code sharing and social share buttons (Weibo, copy link)
- Web frontend: add homepage background music player (BGM) component

### 2026-07-02
- Backend: add article locking mechanism (15-minute auto-expiry, unlock by owner or admin)
- Admin: display lock status and locked-by info in article list
- Backend: fix comment `updated_at` field not updating on status change

### 2026-07-01
- Backend: complete article revision history (auto-save on publish, compare diffs)
- Admin: add revision history panel to article editor
- Backend: add old slug redirect system (301 redirect on title change)

### 2026-06-21
- Backend: add fine-grained capability permission system (15 capabilities, `require_capability()` decorator)
- Backend: add application passwords API (create / delete / query)
- Admin: application passwords management panel

### 2026-06-16
- Backend: add math CAPTCHA (HMAC-signed, prevents brute-force)
- Backend: add login failure lockout (6 failures → 15-minute lock, DB-persisted)
- Web & Admin: integrate CAPTCHA on login and register forms

### 2026-06-15
- Initial public release
- FastAPI backend with JWT auth, role-based access control, CSRF protection
- Vue 3 web frontend with i18n (zh-CN / en / ja), dark mode, comment system
- Vue 3 admin dashboard with Vditor Markdown editor
- One-click installation wizard

## License

MIT © [Lumosylva](https://github.com/Lumosylva/madongdong)

---

> Issues & feedback: [github.com/Lumosylva/madongdong/issues](https://github.com/Lumosylva/madongdong/issues)
