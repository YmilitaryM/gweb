import csv
import io
from datetime import datetime, timezone

from sqlalchemy import select, func
from app.core.database import async_session
from app.apps.audit.models import AuditLog

_EXPORT_LIMIT = 10000


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    except ValueError:
        raise ValueError(f"Invalid date format: {value!r}, expected ISO 8601 (e.g. 2026-01-01)")


def _apply_filters(query, user_id=None, action=None, resource_type=None, start_date=None, end_date=None):
    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    if start_dt is not None:
        query = query.where(AuditLog.created_at >= start_dt)
    if end_dt is not None:
        query = query.where(AuditLog.created_at <= end_dt)
    return query


async def create_audit_log(
    user_id: int,
    username: str,
    action: str,
    resource_type: str,
    resource_id: int | None = None,
    resource_name: str | None = None,
    detail: dict | None = None,
    ip_address: str | None = None,
):
    async with async_session() as db:
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            detail=detail,
            ip_address=ip_address,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log


async def list_audit_logs(
    page: int = 1,
    size: int = 20,
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> tuple[list[AuditLog], int]:
    async with async_session() as db:
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        query = _apply_filters(query, user_id, action, resource_type, start_date, end_date)
        count_query = _apply_filters(count_query, user_id, action, resource_type, start_date, end_date)

        result_total = await db.execute(count_query)
        total = result_total.scalar() or 0

        query = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * size).limit(size)
        result = await db.execute(query)
        return list(result.scalars().all()), total


async def export_csv_data(
    user_id: int | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    async with async_session() as db:
        query = select(AuditLog)
        query = _apply_filters(query, user_id, action, resource_type, start_date, end_date)
        query = query.order_by(AuditLog.created_at.desc()).limit(_EXPORT_LIMIT)
        result = await db.execute(query)
        logs = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "时间", "用户ID", "用户名", "操作", "资源类型", "资源ID", "资源名称", "详情", "IP地址"])
    for log in logs:
        writer.writerow([
            log.id,
            log.created_at.isoformat() if log.created_at else "",
            log.user_id,
            log.username,
            log.action,
            log.resource_type,
            log.resource_id or "",
            log.resource_name or "",
            str(log.detail) if log.detail else "",
            log.ip_address or "",
        ])
    return output.getvalue()
