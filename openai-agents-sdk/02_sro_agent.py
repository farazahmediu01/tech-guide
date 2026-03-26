from pydantic import BaseModel, Field
from enum import StrEnum


class Days(StrEnum):
    MWF = "MWF"
    TTS = "TTS"


class Slots(StrEnum):
    SLOT_1 = "9-11"
    SLOT_2 = "11-1"
    SLOT_3 = "1-3"
    SLOT_4 = "3-5"
    SLOT_5 = "5-7"
    SLOT_6 = "7-9"


class Batch(BaseModel):
    code: str
    day: Days
    solt: Slots
    faculty: str
    student_count: int
    current_semester: str
    current_book: str


class Student(BaseModel):
    id: int
    name: str
    course: str
    contact: str
    batch: Batch
    email: str | None = None
    fee_dues: int = 0


class SROContext(BaseModel):
    students: list[Student] = Field(default_factory=list)


#
def check_slots():
    pass
