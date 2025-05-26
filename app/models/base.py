from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class eMailAttachment(BaseModel, extra="forbid"):
    attachment_name: str
    attachment_binary: bytes


class Questionare(BaseModel, extra="forbid"):
    questionaire_comments: Optional[str] = None
    questionaire_related_company: Optional[Organisation]
    questionaire_date: date


class Person(BaseModel, extra="forbid"):
    person_id: Optional[int] = None
    stakeholder_id: int
    person_salutation: Optional[str] = None
    person_firstname: Optional[str] = None
    person_lastname: str
    person_gender: str
    person_phone: Optional[str] = None
    person_mobile: Optional[str] = None
    person_mail: Optional[str] = None
    person_birthday: Optional[int] = None
    person_street: Optional[str] = None
    person_zip: Optional[str] = None
    person_state: Optional[str] = None
    person_city: Optional[str] = None
    person_country_iso: str
    person_customer_flag: bool
    person_comments: Optional[str] = None
    person_company_function: Optional[str] = None
    person_created: Optional[datetime] = None
    person_updated: Optional[datetime] = None
    person_created_by: Optional[int] = None
    person_updated_by: Optional[int] = None


class Organisation(BaseModel, extra="forbid"):
    organisation_id: Optional[int] = None
    organisation_name: str
    organisation_vat_id: Optional[str] = None
    organisation_legal_form: Optional[str] = None
    organisation_legal_registration_number: Optional[str] = None
    organisation_legal_registry: Optional[str] = None
    organisation_street: Optional[str] = None
    organisation_zip: Optional[str] = None
    organisation_state: Optional[str] = None
    organisation_city: Optional[str] = None
    organisation_country_iso: Optional[str] = None
    organisation_created: Optional[datetime] = None
    organisation_updated: Optional[datetime] = None
    organisation_created_by: Optional[int] = None
    organisation_updated_by: Optional[int] = None


class eMailMessage(BaseModel, extra="forbid"):
    sender_name: Optional[str] = None
    sender_eMail: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_eMail: Optional[str] = None
    cc_eMail: Optional[List[str]] = None
    bcc_eMail: Optional[List[str]] = None
    message_subject: Optional[str] = None
    message_plain: Optional[str] = None
    message_md: Optional[str] = None
    message_html: Optional[str] = None
    message_template: Optional[str] = None
    message_attachments: Optional[List[eMailAttachment]] = None
