<div align="center">

<img src="https://img.shields.io/badge/WariMitra-Digital%20Wari%20Ecosystem-FF6B00?style=for-the-badge" alt="WariMitra Banner"/>

# 🕉️ WariMitra — Digital Wari Ecosystem

**The world's first unified digital platform for large-scale religious pilgrimage management.**

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?style=flat-square&logo=flutter&logoColor=white)](https://flutter.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![WebSockets](https://img.shields.io/badge/WebSockets-Django%20Channels-5865F2?style=flat-square)](https://channels.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

[Live Demo](#) · [API Docs](#api-documentation) · [Report Bug](https://github.com/MustafaPinjari/WariMitra/issues) · [Request Feature](https://github.com/MustafaPinjari/WariMitra/issues)

---

</div>

## 📖 Overview

**WariMitra** ("Wari Friend") is a comprehensive digital platform designed to transform the management of the **Wari pilgrimage** — one of Maharashtra's most sacred annual traditions, where millions of pilgrims (Varkaris) walk hundreds of kilometers to the holy city of Pandharpur.

The platform replaces fragmented WhatsApp groups, paper registers, and manual coordination with a **single intelligent ecosystem** connecting every stakeholder — pilgrims, volunteers, NGOs, medical teams, police, temple authorities, and government agencies.

### 🎯 The Problem We Solve

| Challenge | Impact |
|---|---|
| No real-time crowd visibility | Stampede risks, bottlenecks |
| Delayed emergency response | Preventable medical fatalities |
| Fragmented communication | Resource wastage & duplication |
| Manual missing person tracking | Hours of search time |
| No predictive planning | Reactive rather than proactive management |
| Uneven resource distribution | Shortages in some areas, surplus in others |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    WariMitra Platform                     │
├──────────────────┬──────────────────┬────────────────────┤
│  Mobile App      │  Web Dashboard   │  Backend API       │
│  (Flutter)       │  (Next.js 15)    │  (Django 6.0 DRF)  │
│                  │                  │                    │
│  • Pilgrim App   │  • Govt Control  │  • 22 Modules      │
│  • Volunteer App │    Center        │  • REST + WS APIs  │
│  • SOS Trigger   │  • Live Ops      │  • AI Predictions  │
│  • Offline Mode  │  • Analytics     │  • Real-time Events│
└──────────────────┴──────────────────┴────────────────────┘
                              │
              ┌───────────────┴────────────────┐
              │        PostgreSQL 16            │
              │    + Django Channels (WS)       │
              └────────────────────────────────┘
```

---

## ✨ Key Features

### 🆘 Emergency & SOS
- **One-tap SOS** — Pilgrims can trigger an emergency alert with a single long-press
- **Real-time WebSocket broadcast** — Incidents appear instantly on the Government Dashboard
- **GPS-pinned incident cards** — Location, severity, and incident type surfaced immediately
- **Dispatch tracking** — Assign and track response units in real-time

### 👥 Crowd Intelligence
- **Live density monitoring** — Visual heatmaps of crowd concentration along the Wari route
- **AI-driven bottleneck prediction** — Predicts congestion 30–60 minutes ahead
- **Route diversion alerts** — Broadcast alternate paths to pilgrims and traffic units

### 🏥 Medical Operations
- **Medical camp locator** — Nearest camp with current capacity, staff, and supplies
- **Patient tracking** — Centralized patient registry across all medical camps
- **Ambulance routing** — GPS-aware routing that avoids crowd bottlenecks

### 🔍 Missing Person Management
- **AI-assisted search** — Photo-based matching using ML on uploaded images
- **Family alert broadcasts** — Instantly notify registered family contacts
- **Reunification dashboard** — Centralized tracking for all open missing person cases

### 🛕 Temple Queue Management
- **Live queue wait times** — Updated every few minutes from ground staff
- **Virtual token system** — Pilgrims get a time slot without standing in line
- **Darshan slot pre-booking** — Reduce temple entry congestion

### 📦 NGO & Resource Management
- **Resource registry** — Food, water, shelter, and medical supplies in one view
- **Request-fulfillment pipeline** — NGOs can request and fulfill resources digitally
- **Cross-NGO coordination** — Shared visibility prevents duplication of effort

### 📣 Communication Hub
- **Multi-language support** — Marathi, Hindi, and English
- **Voice announcements** — For digitally inexperienced pilgrims
- **Targeted push notifications** — Segment by location, role, or dindi group

### 📊 Government Analytics
- **Real-time command center** — Unified view of all active operations
- **Historical insights** — Year-on-year trend analysis for better planning
- **Resource allocation AI** — Suggests optimal deployment of police, medical, and volunteers

---

## 🗂️ Project Structure

```
WariMitra/
├── backend/                    # Django 6.0 REST API + WebSocket Server
│   ├── apps/
│   │   ├── ai_predictions/     # ML prediction engine (crowd, health risk)
│   │   ├── analytics/          # Government dashboard data aggregation
│   │   ├── authentication/     # JWT-based auth, role-based access
│   │   ├── community/          # Community incident reporting
│   │   ├── dindi/              # Dindi group management
│   │   ├── government/         # Government portal APIs
│   │   ├── maps/               # Geospatial services
│   │   ├── medical/            # Medical camp, patient, ambulance
│   │   ├── missing_person/     # Missing person case management
│   │   ├── navigation/         # Route and waypoint management
│   │   ├── ngo/                # NGO resource management
│   │   ├── notifications/      # Push notifications (FCM)
│   │   ├── pilgrims/           # Pilgrim registration & profiles
│   │   ├── police/             # Police unit management
│   │   ├── sos/                # Emergency SOS + WebSocket consumers
│   │   ├── temple/             # Temple queue management
│   │   ├── users/              # User accounts & roles
│   │   ├── volunteers/         # Volunteer assignment & tracking
│   │   └── weather/            # Weather data integration
│   ├── config/                 # Django settings (dev/prod/test)
│   └── requirements/           # base.txt / dev.txt / prod.txt
│
├── frontend/                   # Next.js 15 Government Dashboard
│   └── src/
│       ├── app/                # Next.js App Router pages
│       │   ├── page.tsx        # System Overview (dark glassmorphism)
│       │   └── sos/page.tsx    # Live SOS Operations Dashboard
│       ├── components/
│       │   └── layout/         # Sidebar dock, Topbar
│       └── features/           # Feature-specific components
│
├── mobile/                     # Flutter Pilgrim & Volunteer App
│   └── lib/
│       ├── screens/            # Home, SOS, Services screens
│       ├── widgets/            # SpringButton (physics-based)
│       ├── features/           # Feature-level modules
│       ├── services/           # API & WebSocket services
│       └── providers/          # State management (Riverpod)
│
├── database/                   # PostgreSQL schemas & migrations
├── docs/                       # BRD, SRS, FRD, Development Guidelines
├── infrastructure/             # Docker, Nginx, deployment configs
├── postman/                    # API collection for testing
└── tests/                      # End-to-end and integration tests
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| Flutter SDK | 3.x |
| PostgreSQL | 15+ |
| Redis | 6+ (for Django Channels) |

---

### 1. Backend Setup (Django)

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate    # Windows
source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements/development.txt

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials and secret key

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The API is now available at **`http://localhost:8000/api/v1/`**

---

### 2. Frontend Setup (Next.js Dashboard)

```bash
cd frontend
npm install
npm run dev
```

The Government Dashboard is available at **`http://localhost:3000`**

---

### 3. Mobile App Setup (Flutter)

```bash
cd mobile
flutter pub get

# Run on Chrome (recommended for development without Android Studio)
flutter run -d chrome

# Run on Android emulator
flutter run -d emulator-5554

# Run on physical device
flutter run
```

---

### 4. Environment Variables

Create `backend/.env`:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=warimitra
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🔌 API Documentation

The REST API follows standard DRF conventions. All endpoints are prefixed with `/api/v1/`.

| Module | Endpoint | Description |
|---|---|---|
| Auth | `/api/v1/auth/` | JWT token obtain, refresh, verify |
| Pilgrims | `/api/v1/pilgrims/` | Pilgrim registration & profiles |
| SOS | `/api/v1/sos/` | Emergency incident creation & listing |
| Medical | `/api/v1/medical/` | Medical camps, patients, ambulances |
| NGO | `/api/v1/ngo/` | NGO resources and requests |
| Temple | `/api/v1/temple/` | Queue status and slot management |
| Community | `/api/v1/community/` | Incident reports from pilgrims |
| Police | `/api/v1/police/` | Police unit management |
| AI Predictions | `/api/v1/predictions/` | Crowd & risk forecasting |

Full Postman collection: [`/postman/WariMitra.json`](postman/)

### WebSocket Endpoints

| Channel | URL | Description |
|---|---|---|
| SOS Live Feed | `ws://localhost:8000/ws/sos/` | Real-time emergency incident stream |

---

## 🎨 Design System

WariMitra uses a premium dark-glass aesthetic built on Emil Kowalski's design philosophy:

- **Dark Canvas** — `#0B0F19` base with layered translucency
- **Glassmorphism** — `backdrop-blur-xl` cards with `bg-white/5` fills
- **Ambient Glows** — Soft radial gradient halos behind key UI elements
- **Spring Physics** — Custom `SpringButton` widget mirrors Apple's `damping: 1.0 / response: 0.3s`
- **Typography** — Tight `letter-spacing: -0.02em` on headers, Inter font throughout

---

## 👥 Stakeholders & Roles

| Role | Platform | Capabilities |
|---|---|---|
| Pilgrim | Mobile App | SOS, locate services, route navigation, missing person report |
| Volunteer | Mobile App | Task management, reporting, coordination |
| Dindi Leader | Mobile App | Group management, member tracking |
| NGO | Mobile App / Web | Resource management, volunteer coordination |
| Medical Staff | Mobile App | Patient intake, ambulance dispatch |
| Police | Mobile App | Unit management, traffic coordination |
| Temple Authority | Mobile App / Web | Queue management, announcements |
| Government Official | Web Dashboard | Analytics, command center, reporting |
| System Admin | Admin Panel | User management, role control |

---

## 🧠 AI & Predictions

WariMitra includes an AI prediction engine (`apps/ai_predictions`) that provides:

- **Crowd Density Forecasting** — Predicts pilgrim volume at checkpoints 1–2 hours ahead
- **Health Risk Scoring** — Identifies high-risk segments based on temperature, crowd density, and historical incident data
- **Resource Demand Prediction** — Estimates food, water, and medical supply requirements per zone

---

## 🛡️ Security

- **JWT Authentication** — Access tokens (15min) + refresh tokens (7 days)
- **Role-Based Access Control (RBAC)** — Fine-grained permissions per role
- **HTTPS Enforced** — All production traffic over TLS
- **Rate Limiting** — API throttling on sensitive endpoints
- **Audit Logging** — All admin actions are logged (`apps/audit`)

---

## 📸 Screenshots

| Government Dashboard | SOS Operations | Mobile Home | Mobile SOS |
|---|---|---|---|
| Dark Glass Command Center | Live Incident Feed | Spatial Glassmorphism UI | Physics-based SOS Button |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add: AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

Please read our [Development Guidelines](docs/Development_Guidelines.md) before contributing.

---

## 📄 Documents

| Document | Description |
|---|---|
| [BRD](docs/BRD.md) | Business Requirements Document |
| [SRS](docs/SRS.md) | Software Requirements Specification |
| [FRD](docs/FRD.md) | Functional Requirements Document |
| [Feature Workflows](docs/Feature_Workflows.md) | Detailed user flows |
| [Development Guidelines](docs/Development_Guidelines.md) | Coding standards & conventions |

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- The **Varkari community** and millions of pilgrims whose safety inspired this platform
- **Maharashtra Government** for their vision of digital transformation in public services
- Built with ❤️ for India's cultural heritage

---

<div align="center">

**WariMitra** — *Preserving the spirit of Wari, empowered by technology.*

Made with 🕉️ by [Mustafa Pinjari](https://github.com/MustafaPinjari)

</div>
