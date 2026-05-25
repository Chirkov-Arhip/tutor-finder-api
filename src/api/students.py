from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.db.base import get_db
from src.db.models.profile import StudentProfile, TutorProfile
from src.db.models.subject import Subject
from src.db.models.application import Application

router = APIRouter()

# Схемы данных
class StudentProfileRequest(BaseModel):
    user_id: int
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    age: int
    phone: str
    about: Optional[str] = None

class ApplicationRequest(BaseModel):
    student_id: int
    tutor_id: int
    subject_id: Optional[int] = None
    custom_subject: Optional[str] = None
    message: Optional[str] = None
    proposed_dates: Optional[str] = None

class TutorResponse(BaseModel):
    id: int
    last_name: str
    first_name: str
    middle_name: Optional[str]
    age: int
    experience: int
    about: Optional[str]
    subjects: list[dict]

    class Config:
        from_attributes = True

class ApplicationResponse(BaseModel):
    id: int
    status: str
    subject_id: Optional[int]
    custom_subject: Optional[str]

    class Config:
        from_attributes = True

# Эндпоинты
@router.post("/profile", status_code=201)
def create_profile(data: StudentProfileRequest, db: Session = Depends(get_db)):
    existing = db.query(StudentProfile).filter(
        StudentProfile.user_id == data.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Профиль уже существует")

    profile = StudentProfile(
        user_id=data.user_id,
        last_name=data.last_name,
        first_name=data.first_name,
        middle_name=data.middle_name,
        age=data.age,
        phone=data.phone,
        about=data.about
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"message": "Профиль создан", "id": profile.id}

@router.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return {"id": profile.id, "user_id": profile.user_id}

@router.get("/tutors")
def get_tutors(
    subject_id: Optional[int] = None,
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(TutorProfile)

    if subject_id:
        query = query.filter(TutorProfile.subjects.any(id=subject_id))
    if experience_min is not None:
        query = query.filter(TutorProfile.experience >= experience_min)
    if experience_max is not None:
        query = query.filter(TutorProfile.experience <= experience_max)
    if age_min is not None:
        query = query.filter(TutorProfile.age >= age_min)
    if age_max is not None:
        query = query.filter(TutorProfile.age <= age_max)

    tutors = query.all()

    result = []
    for t in tutors:
        result.append({
            "id": t.id,
            "last_name": t.last_name,
            "first_name": t.first_name,
            "middle_name": t.middle_name,
            "age": t.age,
            "experience": t.experience,
            "about": t.about,
            "subjects": [{"id": s.id, "name": s.name} for s in t.subjects]
        })
    return result


@router.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).filter(Subject.id <= 10).all()
    return [{"id": s.id, "name": s.name} for s in subjects]


@router.post("/apply", status_code=201)
def apply(data: ApplicationRequest, db: Session = Depends(get_db)):
    if data.subject_id:
        existing = db.query(Application).filter(
            Application.student_id == data.student_id,
            Application.tutor_id == data.tutor_id,
            Application.subject_id == data.subject_id,
            Application.status == "pending"
        ).first()
    elif data.custom_subject:
        existing = db.query(Application).filter(
            Application.student_id == data.student_id,
            Application.tutor_id == data.tutor_id,
            Application.custom_subject == data.custom_subject,
            Application.status == "pending"
        ).first()
    else:
        existing = None

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Заявка с таким предметом этому репетитору уже отправлена"
        )

    application = Application(
        student_id=data.student_id,
        tutor_id=data.tutor_id,
        subject_id=data.subject_id,
        custom_subject=data.custom_subject,
        message=data.message,
        proposed_dates=data.proposed_dates
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return {"message": "Заявка отправлена", "id": application.id}

@router.get("/profile/full/{user_id}")
def get_full_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return {
        "id": profile.id,
        "last_name": profile.last_name,
        "first_name": profile.first_name,
        "middle_name": profile.middle_name,
        "age": profile.age,
        "phone": profile.phone,
        "about": profile.about
    }

@router.patch("/profile/{user_id}")
def update_profile(user_id: int, data: dict, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль не найден")

    if "last_name" in data:
        profile.last_name = data["last_name"]
    if "first_name" in data:
        profile.first_name = data["first_name"]
    if "middle_name" in data:
        profile.middle_name = data["middle_name"]
    if "age" in data:
        profile.age = data["age"]
    if "about" in data:
        profile.about = data["about"]

    db.commit()
    return {"message": "Профиль обновлён"}

@router.get("/tutor-subjects/{tutor_id}")
def get_tutor_subjects(tutor_id: int, db: Session = Depends(get_db)):
    tutor = db.query(TutorProfile).filter(TutorProfile.id == tutor_id).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Репетитор не найден")
    return [{"id": s.id, "name": s.name} for s in tutor.subjects]
