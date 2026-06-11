import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact


class ContactRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_external_user_id(self, external_user_id: str) -> Contact | None:
        result = await self.db.execute(
            select(Contact).where(Contact.external_user_id == external_user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        external_user_id: str,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company_name: str | None = None,
    ) -> Contact:
        contact = Contact(
            id=uuid.uuid4(),
            external_user_id=external_user_id,
            name=name,
            email=email,
            phone=phone,
            company_name=company_name,
        )
        self.db.add(contact)
        await self.db.flush()
        return contact

    async def update(
        self,
        contact: Contact,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company_name: str | None = None,
    ) -> Contact:
        if name is not None:
            contact.name = name
        if email is not None:
            contact.email = email
        if phone is not None:
            contact.phone = phone
        if company_name is not None:
            contact.company_name = company_name
        await self.db.flush()
        return contact

    async def get_or_create(
        self,
        external_user_id: str,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        company_name: str | None = None,
    ) -> tuple[Contact, bool]:
        contact = await self.get_by_external_user_id(external_user_id)
        if contact:
            contact = await self.update(
                contact, name=name, email=email, phone=phone, company_name=company_name
            )
            return contact, False
        contact = await self.create(
            external_user_id=external_user_id,
            name=name,
            email=email,
            phone=phone,
            company_name=company_name,
        )
        return contact, True
