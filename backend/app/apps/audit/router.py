from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.apps.audit.schemas import AuditLogOut
from app.apps.audit.service import list_audit_logs, export_csv_data
from app.apps.auth.router import get_current_user

router = APIRouter(
    prefix="/api/v1/admin/audit-logs",
    tags=["admin-audit"],
    dependencies=[Depends(get_current_user)],
)


@router.get("")
async def list_logs(
    page: int = 1,
    size: int = 20,
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    items, total = await list_audit_logs(
        page=page, size=size, user_id=user_id, action=action,
        resource_type=resource_type, start_date=start_date, end_date=end_date,
    )
    return {
        "items": [AuditLogOut.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "size": size,
    }


@router.get("/export")
async def export_logs(
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    csv_content = await export_csv_data(
        user_id=user_id, action=action,
        resource_type=resource_type, start_date=start_date, end_date=end_date,
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )
