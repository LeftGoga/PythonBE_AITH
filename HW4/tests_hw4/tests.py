import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from HW4.demo_service.api.main import create_app
from HW4.demo_service.core.users import UserService, UserInfo, UserRole, password_is_longer_than_8
from HW4.demo_service.api.utils import initialize
from http import HTTPStatus

@pytest.fixture
def client():
    app = create_app()
    user_service = UserService(password_validators=[password_is_longer_than_8, lambda pwd: any(char.isdigit() for char in pwd)])
    user_service.register(
        UserInfo(
            username="admin",
            name="admin",
            birthdate=datetime.fromtimestamp(0.0),
            role=UserRole.ADMIN,
            password="superSecretAdminPassword123",
        )
    )
    app.state.user_service = user_service
    return TestClient(app)

@pytest.fixture
def user_service():
    return UserService(password_validators=[password_is_longer_than_8])

@pytest.fixture
def registered_user(client):
    response = client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1970-01-01T00:00:00",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    return response.json()

@pytest.mark.parametrize(
    "username, password, expected_status",
    [
        ("testuser", "testpassword123", 200),
        ("nonexistent", "testpassword123", 401),
        ("testuser", "wrongpassword", 401),
    ],
)
def test_get_user_api(client, registered_user, username, password, expected_status):
    response = client.post(
        "/user-get",
        params={"username": username},
        auth=(username, password),
    )
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    "user_id, expected_status",
    [
        (1, 200),
        (999, 400),  # Исправлено на 400, так как это Bad Request
    ],
)
def test_promote_user_api(client, registered_user, user_id, expected_status):
    response = client.post(
        "/user-promote",
        params={"id": user_id},
        auth=("admin", "superSecretAdminPassword123"),
    )
    assert response.status_code == expected_status

def test_register_user(user_service):
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime.fromtimestamp(0.0),
        password="testpassword123",
    )
    entity = user_service.register(user_info)
    assert entity.info.username == "testuser"
    assert entity.info.name == "Test User"
    assert entity.info.role == UserRole.USER

def test_get_user_by_username(user_service):
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime.fromtimestamp(0.0),
        password="testpassword123",
    )
    user_service.register(user_info)
    entity = user_service.get_by_username("testuser")
    assert entity.info.username == "testuser"

def test_get_user_by_id(user_service):
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime.fromtimestamp(0.0),
        password="testpassword123",
    )
    entity = user_service.register(user_info)
    fetched_entity = user_service.get_by_id(entity.uid)
    assert fetched_entity.info.username == "testuser"

def test_grant_admin(user_service):
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime.fromtimestamp(0.0),
        password="testpassword123",
    )
    entity = user_service.register(user_info)
    user_service.grant_admin(entity.uid)
    fetched_entity = user_service.get_by_id(entity.uid)
    assert fetched_entity.info.role == UserRole.ADMIN

def test_password_validation(user_service):
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime.fromtimestamp(0.0),
        password="short",
    )
    with pytest.raises(ValueError):
        user_service.register(user_info)

def test_register_user_api(client):
    response = client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1970-01-01T00:00:00",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_get_user_api_unauthorized(client):
    response = client.post(
        "/user-get",
        params={"username": "testuser"},
    )
    assert response.status_code == 401

def test_requires_admin_forbidden(client, registered_user):
    response = client.post(
        "/user-promote",
        params={"id": 1},
        auth=("testuser", "testpassword123"),
    )
    assert response.status_code == 403

def test_value_error_handler(client, registered_user):
    response = client.post(
        "/user-get",
        params={"id": 1, "username": "testuser"},
        auth=("testuser", "testpassword123"),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "both id and username are provided"

def test_register_user_duplicate_username(user_service):
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime.fromtimestamp(0.0),
        password="testpassword123",
    )
    user_service.register(user_info)
    with pytest.raises(ValueError):
        user_service.register(user_info)

def test_get_user_by_username_not_found(user_service):
    entity = user_service.get_by_username("nonexistent")
    assert entity is None

def test_get_user_by_id_not_found(user_service):
    entity = user_service.get_by_id(999)
    assert entity is None

def test_grant_admin_not_found(user_service):
    with pytest.raises(ValueError):
        user_service.grant_admin(999)

def test_get_user_both_id_and_username_provided(client, registered_user):
    response = client.post(
        "/user-get",
        params={"id": 1, "username": "testuser"},
        auth=("testuser", "testpassword123"),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "both id and username are provided"

def test_get_user_neither_id_nor_username_provided(client, registered_user):
    response = client.post(
        "/user-get",
        auth=("testuser", "testpassword123"),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "neither id nor username are provided"

def test_password_is_longer_than_8():
    assert password_is_longer_than_8("longpassword") is True
    assert password_is_longer_than_8("short") is False

def test_author_dep(client, registered_user):
    response = client.post(
        "/user-get",
        params={"username": "testuser"},
        auth=("testuser", "testpassword123"),
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_user_service_dep(client, registered_user):
    response = client.post(
        "/user-get",
        params={"id": 2},
        auth=("testuser", "testpassword123"),
    )

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

@pytest.fixture
def app():
    app = create_app()
    user_service = UserService(password_validators=[password_is_longer_than_8, lambda pwd: any(char.isdigit() for char in pwd)])
    user_service.register(
        UserInfo(
            username="admin",
            name="admin",
            birthdate=datetime.fromtimestamp(0.0),
            role=UserRole.ADMIN,
            password="superSecretAdminPassword123",
        )
    )
    app.state.user_service = user_service
    return app

def test_initialize(app):
    async def run_initialize():
        async with initialize(app):
            pass

    import asyncio
    asyncio.run(run_initialize())

    assert isinstance(app.state.user_service, UserService)
    assert app.state.user_service.get_by_username("admin") is not None

def test_get_user_not_found(client, registered_user):
    response = client.post(
        "/user-get",
        params={"id": 999},  # Несуществующий ID
        auth=("testuser", "testpassword123"),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"