from typing import Optional

from pydantic import BaseModel


class GeneralInfo(BaseModel):
    title: str
    description: str


class Image(BaseModel):
    link: str
    description: Optional[str] = None


class Style(BaseModel):
    link: Optional[str] = None
    content: str


class Script(BaseModel):
    link: Optional[str] = None
    content: str