from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy import func, extract
from app.auth.security import get_current_user, get_db
from app.models.user import User
from app.models.service import Service
from app.models.deploy import Deployment
from app.schemas.dashboard import DashboardStats
from datetime import datetime, timedelta
from app.utils.tools import calc_percentage

router = APIRouter(prefix="/dashboard", tags=["Dashboard Stats"])


@router.get("/list", response_model=DashboardStats, summary="List Dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    now = datetime.utcnow()
    start_this_month = now.replace(day=1)
    start_last_month = (start_this_month - timedelta(days=1)).replace(day=1)

    # --------------------
    # SERVICES
    # --------------------
    services_total = db.query(func.count(Service.id)).scalar()

    services_this_month = (
        db.query(func.count(Service.id))
        .filter(Service.created_at >= start_this_month)
        .scalar()
    )

    services_last_month = (
        db.query(func.count(Service.id))
        .filter(
            Service.created_at >= start_last_month,
            Service.created_at < start_this_month
        )
        .scalar()
    )

    services_pct, services_trend = calc_percentage(
        services_this_month, services_last_month
    )

    # --------------------
    # DEPLOYMENTS
    # --------------------
    deployments_total = db.query(func.count(Deployment.id)).scalar()

    deployments_this_month = (
        db.query(func.count(Deployment.id))
        .filter(Deployment.created_at >= start_this_month)
        .scalar()
    )

    deployments_last_month = (
        db.query(func.count(Deployment.id))
        .filter(
            Deployment.created_at >= start_last_month,
            Deployment.created_at < start_this_month
        )
        .scalar()
    )

    deployments_pct, deployments_trend = calc_percentage(
        deployments_this_month, deployments_last_month
    )

    # --------------------
    # MONTHLY DEPLOYMENTS (Jan–Dec)
    # --------------------
    monthly_raw = (
        db.query(
            extract("month", Deployment.created_at).label("month"),
            func.count(Deployment.id)
        )
        .filter(extract("year", Deployment.created_at) == now.year)
        .group_by("month")
        .all()
    )

    monthly_map = {int(m): c for m, c in monthly_raw}
    monthly_data = [monthly_map.get(m, 0) for m in range(1, 13)]

    return {
        "services": {
            "total": services_total,
            "percentage": services_pct,
            "type": services_trend,
        },
        "deployments": {
            "total": deployments_total,
            "percentage": deployments_pct,
            "type": deployments_trend,
        },
        "monthlyData": monthly_data,
    }


@router.get("/top-deployments")
def top_deployments(db: Session = Depends(get_db)):
    last_30_days = datetime.utcnow() - timedelta(days=30)

    # Count deployments per service (last 30 days)
    rows = (
        db.query(
            Deployment.service,
            func.count(Deployment.id).label("count")
        )
        .filter(Deployment.created_at >= last_30_days)
        .group_by(Deployment.service)
        .order_by(func.count(Deployment.id).desc())
        .limit(4)
        .all()
    )

    if not rows:
        return []

    # ✅ total count, not max
    total_count = sum(row.count for row in rows)

    result = []
    for service, count in rows:
        percentage = round((count / total_count) * 100, 2)

        result.append({
            "service": service,
            "count": count,
            "percentage": percentage
        })
    
    return result
