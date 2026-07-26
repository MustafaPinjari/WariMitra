# Functional Requirements Document (FRD) - WariMitra

## 1. System Overview
WariMitra is composed of a mobile application for pilgrims and field staff, a web dashboard for administrative control, a backend coordination engine, and a Community Intelligence Engine.

## 2. User Roles and Permissions (RBAC)
- **Pilgrim:** Access personal features, view maps, raise SOS, view announcements.
- **Volunteer:** Accept tasks, report incidents, verify reports.
- **Dindi Leader:** Manage groups, view member attendance, broadcast messages.
- **Medical Staff:** Manage patients, update inventory, dispatch ambulances.
- **Police Officer:** View assigned area, update incidents, manage road blocks.
- **NGO Coordinator:** Register resources, view demand, distribute inventory.
- **Government Admin:** View district dashboard, access analytics, trigger emergency protocols.
- **Super Admin:** Full platform access.

## 3. Module Breakdown

### 3.1 Pilgrim Module
- **Registration/Login:** OTP based authentication.
- **Home Dashboard:** Today's route, weather, announcements, quick actions.
- **Navigation (Maps):** Live map, route guidance, offline maps, facility locator (water, food, medical, toilets).
- **SOS Emergency:** One-tap SOS, location capture, routing to nearest responder.
- **Voice Assistant:** Multi-lingual voice commands for hands-free interaction (e.g., "Find water").
- **Offline Support:** Cached maps, queued SOS, offline navigation.

### 3.2 Volunteer Module
- **Task Management:** View assigned tasks, accept/resolve tasks.
- **Incident Reporting:** Report issues (e.g., water shortage, crowd congestion) with GPS and photos.
- **Verification System:** Act as verifiers for community-generated reports to increase trust score.

### 3.3 Dindi Leader Module
- **Group Management:** Add/remove members, view member profiles (blood group, emergency contact).
- **Tracking:** Live location of the entire group.
- **Broadcast:** Send text or voice messages to the group.

### 3.4 Medical Module
- **Patient Management:** Register patients via QR, record vital signs, diagnosis, and treatment.
- **Inventory:** Track medicine stock, expiry, and consumption.
- **Ambulance Dispatch:** Live tracking, assignment, ETA calculation.

### 3.5 Police & Security Module
- **Crowd & Traffic Management:** Monitor live heatmaps, manage road blocks, handle diversions.
- **Missing Person Management:** Report, generate search radius via AI, notify volunteers/family, track resolution.

### 3.6 Temple Management Module
- **Queue Management:** Live queue length, waiting time estimation, slot booking.
- **VIP Management:** Scheduled entry, dedicated queues.

### 3.7 NGO Module
- **Resource Registration:** Log available food, water, blankets.
- **Distribution Tracking:** Match supply with live pilgrim demand.

### 3.8 Government Dashboard
- **Live Monitoring:** GIS heatmaps, live pilgrim counts, resource consumption.
- **AI Predictions:** Crowd surge prediction, resource depletion forecast.

## 4. Community Intelligence Engine (CIE)
- Crowdsourced reporting validated by an AI engine (duplicate detection, image analysis).
- Trust scoring system for reporters based on historical accuracy.
