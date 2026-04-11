from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.ai import AIConsultRequest, AIConsultResponse
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/consult", response_model=AIConsultResponse)
def ai_consult(
    payload: AIConsultRequest,
    session: Session = Depends(get_session),
) -> AIConsultResponse:
    return ai_service.recommend_treatment(payload.query, session)
