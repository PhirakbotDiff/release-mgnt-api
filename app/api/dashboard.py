from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session # type: ignore
from app.auth.security import get_current_user, get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["Dashboard Stats"])


@router.get("/", response_model=DashboardStats, summary="List Dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "services": {
            "total": 25,
            "percentage": 43,
            "type": "up"
        },
        "deployments": {
            "total": 168,
            "percentage": 9.05,
            "type": "down"
        },
        "monthlyData": [138, 5, 8, 4, 6, 3, 5, 4, 6, 5, 7, 5],
    }
