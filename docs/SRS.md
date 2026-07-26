# Software Requirements Specification (SRS) - WariMitra

## 1. Introduction
This document specifies the software architecture, technical stack, database design, and non-functional requirements for the WariMitra platform.

## 2. System Architecture
WariMitra employs a cloud-native, microservices architecture designed for high availability, fault tolerance, and horizontal scalability.
- **Frontend:** Next.js (React) for Web Dashboards, Flutter for Cross-Platform Mobile Apps.
- **Backend:** Django with Django REST Framework (DRF) acting as the core API provider.
- **Database:** PostgreSQL for relational data, PostGIS for spatial data, Redis for caching and session management.
- **AI/ML:** Python-based prediction engines (using TensorFlow/PyTorch) deployed as microservices.
- **Infrastructure:** Docker containerization orchestrated via Kubernetes, with API Gateway routing and Load Balancing.

## 3. Database Architecture
- **Primary Database:** PostgreSQL 16
- **Extensions:** PostGIS (GIS & Maps), pgRouting (Route Optimization), UUID.
- **Key Schemas:** `authentication`, `pilgrim`, `dindi`, `volunteer`, `medical`, `police`, `temple`, `community_intelligence`, `government`, `ai`.
- **Optimization Strategy:** Read replicas, Redis caching, Time-Series partitioning (TimescaleDB) for historical GPS and sensor data.

## 4. API Design Standards
- RESTful JSON API using OpenAPI 3.1 standards.
- JWT-based stateless authentication with strict Role-Based Access Control (RBAC).
- Standardized HTTP status codes (200, 201, 400, 401, 403, 404, 422, 500).
- Robust rate-limiting and input validation mechanisms.

## 5. Non-Functional Requirements (NFRs)
- **Scalability:** Must support up to 5,000,000+ concurrent users with auto-scaling Kubernetes clusters.
- **Performance:** API response time < 200ms; Dashboard load < 3s; Mobile app launch < 2s.
- **Availability:** 99.9% uptime target with Multi-AZ deployment and automated failover.
- **Security:** End-to-end TLS 1.3 encryption, AES-256 for data at rest, WAF protection, and GDPR/DPDP compliance.
- **Offline Capability:** Mobile apps must function offline with queued actions (e.g., SOS) and cached map data.
