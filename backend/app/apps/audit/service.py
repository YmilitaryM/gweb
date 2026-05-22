import csv
import io
from datetime import datetime, timezone

from sqlalchemy import select, func
from app.core.database import async_session
from app.apps.audit.models import AuditLog


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

        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
            count_query = count_query.where(AuditLog.resource_type == resource_type)
        if start_date:
            start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
            query = query.where(AuditLog.created_at >= start_dt)
            count_query = count_query.where(AuditLog.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
            query = query.where(AuditLog.created_at <= end_dt)
            count_query = count_query.where(AuditLog.created_at <= end_dt)

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
        if user_id is not None:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if start_date:
            start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
            query = query.where(AuditLog.created_at >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
            query = query.where(AuditLog.created_at <= end_dt)

        query = query.order_by(AuditLog.created_at.desc())
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
