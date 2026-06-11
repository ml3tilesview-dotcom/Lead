"""Integration tests for the chat API endpoint."""

import uuid

import pytest


def make_request(**kwargs):
    base = {
        "external_user_id": str(uuid.uuid4()),
        "external_message_id": str(uuid.uuid4()),
        "message": "Hello, I am interested in your product",
        "platform": "website",
    }
    base.update(kwargs)
    return base


@pytest.mark.asyncio
async def test_hot_lead_response(client):
    payload = make_request(message="I would like to book a demo please")
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lead_evaluation"]["lead_temperature"] == "hot"
    assert data["handoff_required"] is True
    assert data["duplicate"] is False
    assert data["conversation_status"] == "handed_off"


@pytest.mark.asyncio
async def test_warm_lead_response(client):
    payload = make_request(message="What features do you have for tile designers?")
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lead_evaluation"]["lead_temperature"] == "warm"
    assert data["handoff_required"] is False


@pytest.mark.asyncio
async def test_cold_lead_response(client):
    payload = make_request(message="Looks interesting, tell me more")
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lead_evaluation"]["lead_temperature"] == "cold"
    assert data["handoff_required"] is False


@pytest.mark.asyncio
async def test_not_lead_response(client):
    payload = make_request(message="I am applying for a job, here is my resume")
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lead_evaluation"]["is_lead"] is False


@pytest.mark.asyncio
async def test_demo_handoff(client):
    payload = make_request(
        message="I need a demo of your product",
        name="John Smith",
        email="john@example.com",
    )
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["handoff_required"] is True
    assert data["lead_evaluation"]["handoff_required"] is True


@pytest.mark.asyncio
async def test_pricing_handoff(client):
    payload = make_request(message="What is the pricing for 5 stores?")
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["handoff_required"] is True


@pytest.mark.asyncio
async def test_human_request_handoff(client):
    payload = make_request(message="I want to speak to a human agent")
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["handoff_required"] is True


@pytest.mark.asyncio
async def test_duplicate_message(client):
    msg_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    payload = make_request(
        external_user_id=user_id,
        external_message_id=msg_id,
        message="Hello world",
    )
    resp1 = await client.post("/api/v1/chat/messages", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["duplicate"] is False

    resp2 = await client.post("/api/v1/chat/messages", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["duplicate"] is True
    assert resp2.json()["processing_status"] == "duplicate"


@pytest.mark.asyncio
async def test_blank_message_rejected(client):
    payload = make_request(message="   ")
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_email_rejected(client):
    payload = make_request(email="not-an-email")
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_database_persistence(client):
    user_id = str(uuid.uuid4())
    payload = make_request(
        external_user_id=user_id,
        message="I would like a quotation for your product",
        name="Alice",
        email="alice@example.com",
    )
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    conv_id = data["conversation_id"]

    # Verify conversation is retrievable
    conv_resp = await client.get(f"/api/v1/conversations/{conv_id}")
    assert conv_resp.status_code == 200
    assert conv_resp.json()["id"] == conv_id


@pytest.mark.asyncio
async def test_conversation_messages_history(client):
    user_id = str(uuid.uuid4())
    payload = make_request(
        external_user_id=user_id,
        message="Tell me more about your platform",
    )
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    conv_id = resp.json()["conversation_id"]

    msg_resp = await client.get(f"/api/v1/conversations/{conv_id}/messages")
    assert msg_resp.status_code == 200
    msg_data = msg_resp.json()
    assert msg_data["total"] >= 2  # inbound + outbound
    assert msg_data["conversation_id"] == conv_id


@pytest.mark.asyncio
async def test_ai_disabled_after_handover(client):
    user_id = str(uuid.uuid4())
    msg_id = str(uuid.uuid4())

    # First message triggers handoff
    payload = make_request(
        external_user_id=user_id,
        external_message_id=msg_id,
        message="I need a demo right now please",
    )
    resp = await client.post("/api/v1/chat/messages", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["handoff_required"] is True
    conv_id = data["conversation_id"]

    # Second message from same user — AI should be disabled
    payload2 = make_request(
        external_user_id=user_id,
        external_message_id=str(uuid.uuid4()),
        message="Hello, are you there?",
    )
    resp2 = await client.post("/api/v1/chat/messages", json=payload2)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["conversation_id"] == conv_id
    assert data2["conversation_status"] == "handed_off"


@pytest.mark.asyncio
async def test_resume_ai_endpoint(client):
    user_id = str(uuid.uuid4())
    # Create conversation via handoff
    payload = make_request(
        external_user_id=user_id,
        message="Please give me a quote",
    )
    resp = await client.post("/api/v1/chat/messages", json=payload)
    conv_id = resp.json()["conversation_id"]

    # Resume AI
    resume_resp = await client.post(f"/api/v1/conversations/{conv_id}/resume-ai")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["ai_enabled"] is True
    assert resume_resp.json()["status"] == "active"
