# Phase 2.2 Complete: Database Bottleneck (Transaction Locks) — RESOLVED

## Problem
`GpsPing` and `LiveDensity` were both stored in standard PostgreSQL. At pilgrimage scale (millions of simultaneous users), constant writes to these tables would:
- Exhaust all database IOPS
- Cause row-level and table-level transaction locks
- Cascade into a full backend outage

## Solution

### LiveDensity → Redis GEO (Fully Moved)
The `LiveDensity` model has been **completely removed** from PostgreSQL. Real-time crowd density is now managed entirely in Redis using GEO commands (`GEOADD`, `GEORADIUS`), which:
- Run in-memory (microsecond latency, zero DB locks)
- Automatically handle geospatial radius queries
- Fail gracefully: if Redis is down, density returns 0 — the backend stays alive

**Files changed:**
- `apps/gps/models.py` — `LiveDensity` class removed
- `apps/gps/redis_density.py` — NEW: `LiveDensityManager` class
- `apps/gps/migrations/0003_timescaledb_and_remove_livedensity.py` — NEW: drops the DB table
- `apps/gps/tests/test_redis_density.py` — NEW: 7 unit tests, all passing ✅

### GpsPing → TimescaleDB Hypertable
The `GpsPing` model stays in PostgreSQL but is converted into a **TimescaleDB hypertable** partitioned by `created_at`. This means:
- Inserts are routed to the current time-partition chunk (no full-table locks)
- Historical queries are range-scanned across chunks (dramatically faster)
- Automatic data pruning / retention policies can be added later

**Files changed:**
- `docker-compose.yml` — PostgreSQL image changed to `timescale/timescaledb-ha:pg16-latest`
- `apps/gps/migrations/0003_timescaledb_and_remove_livedensity.py` — executes `create_hypertable`

### Infrastructure
- `requirements.txt` — Added `daphne`, `channels`, `channels-redis`, `django-extensions`, `django-debug-toolbar`
- `config/settings/test.py` — NEW: lightweight test settings (SQLite in-memory, no GDAL)

## Test Results
```
7 passed in 0.85s  ✅
```
- `test_update_density_success`
- `test_update_density_when_not_connected`
- `test_get_density_in_radius_returns_user_count`
- `test_get_density_in_radius_when_not_connected`
- `test_density_level_50_percent`
- `test_density_level_capped_at_100`
- `test_density_level_zero_when_empty`

## Next Steps (Phase 2.3)
- Add Celery task to prune stale Redis density entries (users inactive >5 min)
- Add TimescaleDB retention policy to auto-drop GPS pings older than 30 days
- Move `GpsPing` writes to a Celery async task to prevent HTTP request blocking
