from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    citizen,
    compensation,
    consent,
    documents,
    field,
    grievances,
    health,
    parcels,
    projects,
    rr,
    workflows,
)

api_router = APIRouter()

# Core System Health
api_router.include_router(health.router, prefix="/health", tags=["System Health"])

# Authentication & RBAC
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])

# Infrastructure Projects
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

# Cadastral Land Parcels & PostGIS
api_router.include_router(parcels.router, prefix="/parcels", tags=["Land Parcels"])

# Lifecycle Workflow Engine & State Machine
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflow Engine"])

# Field Survey, Geotagged Photos & Evidence
api_router.include_router(field.router, prefix="/field", tags=["Field Survey & Evidence"])

# Statutory Documents & Immutable Versioning
api_router.include_router(documents.router, prefix="/documents", tags=["Statutory Documents & Versioning"])

# Landowner Consent & Mock E-Sign Simulation
api_router.include_router(consent.router, prefix="/consent", tags=["Landowner Consent & E-Sign"])

# Statutory Compensation Formulation & Section 31 Awards
api_router.include_router(compensation.router, prefix="/compensation", tags=["Compensation & Awards"])

# Citizen-Facing Portal (Reuses Domain Services)
api_router.include_router(citizen.router, prefix="/citizen", tags=["Citizen Portal"])

# Statutory Grievance Redressal & Petitions (CPGRAMS)
api_router.include_router(grievances.router, prefix="/grievances", tags=["Grievance Redressal"])

# Rehabilitation & Resettlement (R&R)
api_router.include_router(rr.router, prefix="/rr", tags=["Rehabilitation & Resettlement (R&R)"])
