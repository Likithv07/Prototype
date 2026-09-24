# BhoomiSetu — Backend Foundation, Auth, Projects, Workflow, Field Evidence, Documents, Consent & Compensation
> **National Land Acquisition & Management Platform (SIH 2026)**  
> High-performance, modular monolith backend built with Python, FastAPI, SQLAlchemy 2.0 (async), PostGIS, Redis, and Alembic.

---

## 1. Modules Implemented

1. **System Health & Probes**:
   - `GET /health` (Root liveness)
   - `GET /api/v1/health` (Versioned liveness)
   - `GET /api/v1/health/ready` (PostgreSQL + PostGIS & Redis readiness)
2. **Authentication & RBAC**:
   - `POST /api/v1/auth/register` (Bcrypt/PBKDF2 password hashing, default role assignment)
   - `POST /api/v1/auth/login` (JWT token issuance)
   - `POST /api/v1/auth/refresh` (JWT token rotation)
   - `POST /api/v1/auth/logout` (JWT token revocation)
   - `GET  /api/v1/auth/me` (Profile, roles, permissions, jurisdiction)
3. **Projects**:
   - `POST /api/v1/projects` (Create project - Admin/Central/State)
   - `GET  /api/v1/projects` (List projects with state/district/status filtering and scope enforcement)
   - `GET  /api/v1/projects/{id}` (Get project details and lifecycle stages)
   - `PUT  /api/v1/projects/{id}` (Update project status, metrics, and progress)
   - `GET  /api/v1/projects/{id}/parcels` (List all parcels under project)
4. **Land Parcels & PostGIS Spatial Operations**:
   - `POST /api/v1/parcels` (Create cadastral parcel with PostGIS polygon geometry)
   - `GET  /api/v1/parcels` (List parcels with multi-tier geographic scope)
   - `GET  /api/v1/parcels/{id}` (Get parcel with GeoJSON and centroid)
   - `PUT  /api/v1/parcels/{id}` (Update parcel properties and spatial boundaries)
   - `GET  /api/v1/parcels/{id}/geojson` (Export as standard RFC 7946 GeoJSON Feature)
5. **Land Acquisition Workflow Engine**:
   - `GET  /api/v1/workflows/projects/{project_id}` (Active workflow state, current stage, SLA remaining days)
   - `POST /api/v1/workflows/projects/{project_id}/transitions` (Execute controlled atomic transition command)
   - `GET  /api/v1/workflows/projects/{project_id}/history` (Chronological transition ledger with user attribution)
   - `GET  /api/v1/workflows/projects/{project_id}/current-stage` (Active statutory stage metadata and SLA days)
   - `GET  /api/v1/workflows/projects/{project_id}/pending-actions` (List next legal actions available to requesting user)
6. **Field Survey, Geotagged Photos & Evidence**:
   - `POST /api/v1/field/assignments` (District Officer assigns parcel tasks)
   - `GET  /api/v1/field/assignments` (List assignments scoped to officer/jurisdiction)
   - `PUT  /api/v1/field/assignments/{id}/status` (Update task status: Pending → In Progress → Completed)
   - `POST /api/v1/field/surveys` (Submit structured physical asset enumeration)
   - `GET  /api/v1/field/surveys` (List survey records by parcel / project)
   - `POST /api/v1/field/photos` (Multipart upload with real magic-byte validation, SHA-256 hash, and RTK GPS coordinates)
   - `GET  /api/v1/field/photos` (List photos by parcel / assignment)
   - `POST /api/v1/field/documents` (Multipart upload: survey PDFs, deeds, consent forms)
   - `GET  /api/v1/field/documents` (List documents by parcel / assignment)
   - `PUT  /api/v1/field/evidence/{evidence_type}/{evidence_id}/verify` (Supervisory approval or rejection)
7. **Statutory Document Management & Strict Versioning**:
   - `POST /api/v1/documents` (Upload new statutory document, records master registry and version v1.0)
   - `POST /api/v1/documents/{id}/versions` (Upload immutable revision v2.0+ without overwriting earlier files)
   - `GET  /api/v1/documents` (List documents with category/project/parcel filters and scope enforcement)
   - `GET  /api/v1/documents/{id}` (Retrieve document master metadata and full version history)
   - `GET  /api/v1/documents/{id}/download` (Download verified binary file payload for authorized users)
   - `PUT  /api/v1/documents/{id}/verify` (Supervisory officer verification or rejection)
8. **Landowner Consent & Mock E-Sign Simulation**:
   - `POST /api/v1/consent` (Create draft landowner consent record linked to cadastral parcel)
   - `GET  /api/v1/consent` (List consents scoped to citizen ownership or officer jurisdiction)
   - `GET  /api/v1/consent/{id}` (Retrieve consent record and verification status)
   - `GET  /api/v1/consent/{id}/history` (Retrieve immutable lifecycle audit log)
   - `POST /api/v1/consent/{id}/esign/initiate` (Simulate Aadhaar OTP dispatch - clearly marked mock)
   - `POST /api/v1/consent/{id}/esign/verify` (Simulate OTP verification with code 781923, records signature ref and QR)
   - `POST /api/v1/consent/{id}/submit` (Submit draft consent for administrative verification)
   - `PUT  /api/v1/consent/{id}/verify` (Officer verification or rejection, automatically syncs parcel consent status)
9. **Compensation Assessment & Statutory Award Management**:
   - `POST /api/v1/compensation/{parcel_id}/calculate` (Interactive statutory calculator under Sections 26-30 RFCTLARR Act 2013)
   - `GET  /api/v1/compensation/{parcel_id}` (Retrieve active assessment and itemized attached asset components)
   - `PUT  /api/v1/compensation/{id}` (Update assessment parameters / attached structures, trees, crops)
   - `POST /api/v1/compensation/{id}/submit` (Submit draft assessment for Section 31 statutory award review)
   - `POST /api/v1/compensation/{id}/approve` (Multi-gated supervisory approval and digital DSC Award issuance)
   - `POST /api/v1/compensation/{id}/reject` (Request formulation revision stating statutory grounds)
   - `GET  /api/v1/compensation/{id}/history` (Retrieve complete immutable formulation audit trail)
10. **Citizen Portal & Scoped Data Isolation (Unified Domain Services)**:
   - `GET  /api/v1/citizen/parcels` (List registered parcels belonging to authenticated citizen)
   - `GET  /api/v1/citizen/parcels/{id}` (Retrieve cadastral details and PostGIS spatial boundaries)
   - `GET  /api/v1/citizen/compensation/{parcel_id}` (Track statutory valuation, Solatium, interest, and award seal)
   - `GET  /api/v1/citizen/consent/{parcel_id}` (Check voluntary acquisition consent and Aadhaar eSign verification)
   - `POST /api/v1/citizen/consent/{parcel_id}/esign` (Submit verified Aadhaar eSign consent directly)
   - `GET  /api/v1/citizen/payment/{parcel_id}` (Track Direct Benefit Transfer route, PFMS mandate ID, and account status)
   - `POST /api/v1/citizen/grievances` (Lodge formal objection or dispute petition)
   - `GET  /api/v1/citizen/grievances` (List grievances lodged by authenticated citizen)
   - `GET  /api/v1/citizen/grievances/{id}` (Track grievance status, assigned officer, and hearing resolution findings)
   - `GET  /api/v1/citizen/notifications` (List alerts, gazette notices, and payment advisories)
   - `PUT  /api/v1/citizen/notifications/{id}/read` (Acknowledge and mark notification read)
   - `GET  /api/v1/citizen/rr-benefits` (Track RFCTLARR Second Schedule R&R entitlements, eligibility, and grants)
11. **Statutory Grievance Redressal (CPGRAMS Integrated)**:
   - `POST /api/v1/grievances` (Lodge petition)
   - `GET  /api/v1/grievances` (List grievances scoped to administrative jurisdiction)
   - `GET  /api/v1/grievances/{id}` (Retrieve petition details with attachments and timeline history)
   - `POST /api/v1/grievances/{id}/assign` (Allocate petition to revenue inquiry officer)
   - `PUT  /api/v1/grievances/{id}/status` (Update lifecycle review status)
   - `POST /api/v1/grievances/{id}/resolve` (Record formal inquiry findings and conclude resolution)
   - `POST /api/v1/grievances/{id}/documents` (Attach supporting title deed, affidavit, or revenue order)
   - `GET  /api/v1/grievances/{id}/history` (Retrieve complete immutable history)
12. **Rehabilitation & Resettlement (R&R) Module (Second & Third Schedules)**:
   - `GET  /api/v1/rr/colonies` (Model resettlement colonies, social infrastructure, power/water commissioning)
   - `GET  /api/v1/rr/families` (List project-affected families subject to jurisdictional scope constraints)
   - `GET  /api/v1/rr/families/{id}` (Family demographics, Second Schedule eligibility, and itemized benefits)
   - `POST /api/v1/rr/families` (Register project-affected family from SIA census)
   - `POST /api/v1/rr/families/{id}/eligibility` (Record statutory eligibility determination under Second Schedule)
   - `POST /api/v1/rr/families/{id}/benefits` (Allocate alternative housing unit, livelihood grant, or shifting allowance)
   - `POST /api/v1/rr/benefits/{id}/disburse` (Record financial grant transfer reference and mark benefit as disbursed)

---

## 2. RFCTLARR 2013 Compensation Formula & Approval Gates

### Statutory Formulation (Sections 26–30):
$$\text{Basic Land Value} = \text{Land Area (Acres)} \times \text{Market Value per Unit (₹/Acre)}$$
$$\text{Multiplied Land Value} = \text{Basic Land Value} \times \text{Multiplier Factor (1.0 to 2.0)}$$
$$\text{Market Value Plus Assets} = \text{Multiplied Land Value} + \text{Attached Asset Valuation (Structures, Trees, Crops)}$$
$$\text{Solatium Amount} = \text{Market Value Plus Assets} \times (\text{Statutory Solatium 100\%} / 100)$$
$$\text{Additional Interest} = \text{Multiplied Land Value} \times (\text{Interest 12\% p.a.} / 100)$$
$$\text{Total Compensation Award} = \text{Market Value Plus Assets} + \text{Solatium Amount} + \text{Additional Interest}$$

### 6 Mandatory Approval Verification Gates:
1. **User Permission**: Only `DISTRICT_OFFICER`, `STATE_OFFICIAL`, or `ADMIN` with geographic jurisdiction can approve.
2. **Parcel Eligibility**: Parcel must be in active acquisition (`Under Verification` or `Notification Issued`), not disputed or already possessed.
3. **Required Field Evidence**: Must have at least 1 verified field photo or survey enumeration on record.
4. **Required Statutory Documents**: Must have at least 1 verified statutory document (Valuation Report or Title Deed).
5. **Workflow Stage Alignment**: Project must have progressed to or beyond `survey/land records` / `compensation` stages.
6. **Calculation Completeness**: Total compensation, basic land value, and solatium must be positive non-zero values.

---

## 3. Example API Requests

### 1. Interactive Calculation
```bash
curl -X POST http://localhost:8000/api/v1/compensation/TS-HYD-2026-001245/calculate \
  -H "Authorization: Bearer <OFFICER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "land_area_acres": 2.5,
    "market_value_per_acre": 1000000.0,
    "multiplier_factor": 1.5,
    "asset_valuation": 250000.0,
    "solatium_percentage": 100.0,
    "interest_percentage": 12.0
  }'
```

### 2. Approve Award under Section 31
```bash
curl -X POST http://localhost:8000/api/v1/compensation/COMP-TS-HYD-2026-001245/approve \
  -H "Authorization: Bearer <DISTRICT_OFFICER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "digital_signature_consent": true,
    "digital_seal_ref": "NIC-DSC-GOV-2026-9812",
    "approval_remarks": "Award certified under Section 31 of RFCTLARR Act 2013"
  }'
```

---

## 4. Running Automated Tests

```powershell
# Run citizen capabilities, data isolation, and grievance test suite
pytest -v app/tests/test_citizen_and_grievances.py

# Run compensation and awards test suite
pytest -v app/tests/test_compensation_and_awards.py

# Run documents and landowner consent test suite
pytest -v app/tests/test_documents_and_consent.py

# Run all test suites
pytest -v
```
