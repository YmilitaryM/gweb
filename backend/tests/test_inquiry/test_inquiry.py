import pytest


@pytest.mark.asyncio
async def test_submit_inquiry_public(client):
    resp = await client.post(
        "/api/v1/inquiries",
        json={
            "company_name": "测试公司",
            "contact_name": "张三",
            "phone": "13800138000",
            "message": "你好，我想咨询产品信息。",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_admin_list_inquiries(client, auth_headers):
    from app.apps.inquiry.service import create_inquiry

    await create_inquiry(
        company_name="公司A",
        contact_name="李四",
        phone="13900139000",
        message="咨询信息",
    )
    await create_inquiry(
        company_name="公司B",
        contact_name="王五",
        phone="13700137000",
        message="合作意向",
    )

    resp = await client.get("/api/v1/admin/inquiries", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_admin_list_inquiries_requires_auth(client):
    resp = await client.get("/api/v1/admin/inquiries")
    assert resp.status_code == 401
