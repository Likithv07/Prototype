import uuid
from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user import Permission, Role, User, user_roles
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


# Default system roles and key permissions matrix
DEFAULT_ROLE_PERMISSIONS = {
    "ADMIN": [
        ("admin:all", "Full system administrator access", "auth"),
        ("project:create", "Create new projects", "project"),
        ("project:read", "Read all projects", "project"),
        ("project:update", "Update all projects", "project"),
        ("parcel:create", "Create land parcels", "parcel"),
        ("parcel:read", "Read all parcels", "parcel"),
        ("parcel:update", "Update all parcels", "parcel"),
        ("survey:conduct", "Conduct field surveys", "survey"),
        ("compensation:approve", "Approve compensation awards", "compensation"),
        ("grievance:resolve", "Resolve citizen grievances", "grievance"),
    ],
    "CENTRAL_OFFICIAL": [
        ("project:create", "Create new projects", "project"),
        ("project:read", "Read all national projects", "project"),
        ("project:update", "Update projects", "project"),
        ("parcel:read", "Read parcels nationwide", "parcel"),
        ("analytics:national", "View national dashboard metrics", "analytics"),
        ("reports:export", "Export national reports", "reports"),
    ],
    "STATE_OFFICIAL": [
        ("project:read", "Read state projects", "project"),
        ("project:update", "Update state projects", "project"),
        ("parcel:read", "Read state parcels", "parcel"),
        ("parcel:update", "Update state parcels", "parcel"),
        ("compensation:review", "Review state compensation awards", "compensation"),
        ("sla:monitor", "Monitor state SLAs", "sla"),
    ],
    "DISTRICT_OFFICER": [
        ("project:read", "Read district projects", "project"),
        ("parcel:create", "Create district parcels", "parcel"),
        ("parcel:read", "Read district parcels", "parcel"),
        ("parcel:update", "Update district parcels", "parcel"),
        ("survey:assign", "Assign field officers to surveys", "survey"),
        ("compensation:approve", "Approve district awards", "compensation"),
        ("grievance:resolve", "Resolve district grievances", "grievance"),
    ],
    "FIELD_OFFICER": [
        ("parcel:read", "Read assigned parcels", "parcel"),
        ("survey:conduct", "Perform field survey and boundary verification", "survey"),
        ("evidence:upload", "Upload geotagged photos and field documents", "evidence"),
        ("verification:submit", "Submit field survey reports", "verification"),
    ],
    "CITIZEN": [
        ("citizen:read_self", "View owned parcels and claims", "citizen"),
        ("consent:submit", "Submit voluntary land acquisition consent", "consent"),
        ("grievance:create", "File land and compensation grievances", "grievance"),
        ("claim:track", "Track status of compensation payments", "claim"),
    ],
}


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository handling User, Role, and Permission data access."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch user with eager-loaded roles and permissions."""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by unique email."""
        stmt = (
            select(User)
            .where(User.email == email.strip().lower())
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Fetch user by unique username."""
        stmt = (
            select(User)
            .where(User.username == username.strip().lower())
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Fetch user matching either username or email."""
        cleaned = identifier.strip().lower()
        stmt = (
            select(User)
            .where(or_(User.username == cleaned, User.email == cleaned))
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Fetch a Role entity by name."""
        stmt = (
            select(Role)
            .where(Role.name == name.upper())
            .options(selectinload(Role.permissions))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def seed_system_roles_and_permissions(self) -> None:
        """Seed default roles and granular permissions if not already present."""
        for role_name, perms in DEFAULT_ROLE_PERMISSIONS.items():
            role_stmt = select(Role).where(Role.name == role_name).options(selectinload(Role.permissions))
            role_res = await self.session.execute(role_stmt)
            role = role_res.scalars().first()

            if not role:
                role = Role(
                    name=role_name,
                    description=f"System role for {role_name.replace('_', ' ').title()}",
                    is_system_role=True,
                )
                self.session.add(role)
                await self.session.flush()

            for code, name, module in perms:
                perm_stmt = select(Permission).where(Permission.code == code)
                perm_res = await self.session.execute(perm_stmt)
                perm = perm_res.scalars().first()

                if not perm:
                    perm = Permission(code=code, name=name, module=module)
                    self.session.add(perm)
                    await self.session.flush()

                if perm not in role.permissions:
                    role.permissions.append(perm)

        await self.session.flush()

