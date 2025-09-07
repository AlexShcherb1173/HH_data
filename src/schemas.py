from dataclasses import dataclass
from typing import Optional

@dataclass
class Company:
    company_id: int
    name: str
    area_name: Optional[str] = None
    url: Optional[str] = None

@dataclass
class Vacancy:
    vacancy_id: int
    company_id: int
    name: str
    description: Optional[str] = None
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    salary_currency: Optional[str] = None
    area_name: Optional[str] = None
    url: Optional[str] = None