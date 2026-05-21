import pytest


@pytest.mark.asyncio
async def test_create_session(client):
    resp = await client.post("/api/v1/chat/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data


@pytest.mark.asyncio
async def test_send_message(client):
    # Create session first
    sess = await client.post("/api/v1/chat/sessions")
    session_id = sess.json()["session_id"]

    resp = await client.post("/api/v1/chat/message", json={
        "session_id": session_id, "message": "What is your company about?"
    })
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_get_session_history(client):
    sess = await client.post("/api/v1/chat/sessions")
    session_id = sess.json()["session_id"]

    # Send a message to create history
    await client.post("/api/v1/chat/message", json={
        "session_id": session_id, "message": "Hello"
    })

    resp = await client.get(f"/api/v1/chat/sessions/{session_id}")
    assert resp.status_code == 200
    messages = resp.json()
    assert len(messages) == 2  # user + assistant


@pytest.mark.asyncio
async def test_admin_list_sessions(client, auth_headers):
    # Create a session first
    await client.post("/api/v1/chat/sessions")
    await client.post("/api/v1/chat/message", json={
        "session_id": (
            await client.post("/api/v1/chat/sessions")
        ).json()["session_id"],
        "message": "Hi"
    })

    resp = await client.get("/api/v1/admin/chat/sessions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_admin_chat_stats(client, auth_headers):
    resp = await client.get("/api/v1/admin/chat/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_sessions" in data
