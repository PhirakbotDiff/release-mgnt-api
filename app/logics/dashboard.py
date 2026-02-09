from datetime import datetime, timedelta
from sqlalchemy.orm import Session # type: ignore
from sqlalchemy import func, extract # type: ignore

from app.models.deploy import Deployment


def get_top_deployment(db: Session):

    # Start of current month (UTC)
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    data = (
        db.query(
            Deployment.service,
            func.count(Deployment.id).label("count")
        )
        .filter(Deployment.created_at >= start_of_month)
        .group_by(Deployment.service)
        .order_by(func.count(Deployment.id).desc())
        .limit(4)
        .all()
    )


    return data

def get_last_thirthy_days(db: Session):

    last_30_days = datetime.utcnow() - timedelta(days=30)

    # Count deployments per service (last 30 days)
    data = (
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

    return data