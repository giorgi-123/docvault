import pytest

# ====================
#     Health Check
# ====================

@pytest.mark.asyncio
async def test_health_check(client):
    """Verify test setup works."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# ==================
#    Registration
# ==================

@pytest.mark.asyncio
async def test_register_success(client):
    """Test successful registration"""
    user_data = {
        "email": "user@example.com",
        "password": "examplepassword123",
        "full_name": "Test User",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200

@pytest.mark.asyncio
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

@pytest.mark.asyncio
async def test_invalid_email_format(client):
    """Test invalid email format input"""
    user_data = {
        "email": "user!example.com",
        "password": "examplepassword123",
        "full_name": "Test User",
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 422

@pytest.mark.asyncio
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

# @pytest.mark.asyncio
@pytest.mark.skip(reason="not yet implemented")
async def test_successful_login(client):
    """Test successful login"""
    pass

# @pytest.mark.asyncio
@pytest.mark.skip(reason="not yet implemented")
async def test_wrong_password(client):
    """Test wrong password input behaviour"""
    pass

# @pytest.mark.asyncio
@pytest.mark.skip(reason="not yet implemented")
async def test_non_existent_email(client):
    """Test Non-existent email login"""
    pass