import pytest

# ====================
#     Health Check
# ====================

async def test_health_check(client):
    """Verify test setup works."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# ==================
#    Registration
# ==================

async def test_register_success(client):
    """Test successful registration"""
    user_data = {
        "email": "user@example.com",
        "password": "examplepassword123",
        "full_name": "Test User",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200

async def test_duplicate_email(client):
    """Test email duplication"""
    user_data = {
        "email": "user@example.com",
        "password": "examplepassword123",
        "full_name": "Test User",
    }
    first_user_create = await client.post("/auth/register", json=user_data)
    second_user_create = await client.post("/auth/register", json=user_data)
    assert second_user_create.status_code == 400

async def test_invalid_email_format(client):
    """Test invalid email format input"""
    user_data = {
        "email": "user!example.com",
        "password": "examplepassword123",
        "full_name": "Test User",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 422

async def test_short_password(client):
    """Test short password less than (8) characters"""
    user_data = {
        "email": "user@example.com",
        "password": "user",
        "full_name": "Test User",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 422


# ==================
#       Login
# ==================

async def test_successful_login(client, register_user):
    """Test successful login"""
    response = await client.post("/auth/login", json=register_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_wrong_password(client, register_user):
    """Test wrong password input behaviour"""
    login_data = {**register_user, "password": "wrongpassword123"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 401

async def test_non_existent_email(client, register_user):
    """Test Non-existent email login"""
    login_data = {**register_user, "email": "nonexistent@example.com"}
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 401