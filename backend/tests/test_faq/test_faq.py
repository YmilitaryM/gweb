import pytest


@pytest.mark.asyncio
async def test_list_faqs_public(client):
    from app.apps.faq.service import create_faq

    await create_faq(
        question_zh="常见问题1",
        question_en="FAQ 1",
        answer_zh="答案1",
        answer_en="Answer 1",
        order=1,
        is_published=True,
    )
    await create_faq(
        question_zh="常见问题2",
        question_en="FAQ 2",
        answer_zh="答案2",
        answer_en="Answer 2",
        order=2,
        is_published=True,
    )
    await create_faq(
        question_zh="未发布",
        question_en="Unpublished",
        answer_zh="",
        answer_en="",
        order=3,
        is_published=False,
    )

    resp = await client.get("/api/v1/faqs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["question_zh"] == "常见问题1"


@pytest.mark.asyncio
async def test_create_faq(client, auth_headers):
    resp = await client.post(
        "/api/v1/admin/faqs",
        json={
            "question_zh": "新问题",
            "question_en": "New Question",
            "answer_zh": "新答案",
            "answer_en": "New Answer",
            "order": 1,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["question_zh"] == "新问题"
    assert data["is_published"] is True


@pytest.mark.asyncio
async def test_create_faq_requires_auth(client):
    resp = await client.post(
        "/api/v1/admin/faqs",
        json={
            "question_zh": "未授权",
            "question_en": "Unauthorized",
            "answer_zh": "",
            "answer_en": "",
        },
    )
    assert resp.status_code == 401
