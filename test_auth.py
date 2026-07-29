def test_signup_success(client):
    response = client.post("/auth/signup", json={
        "email": "pytestuser@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "pytestuser@example.com"
    assert data["role"] == "user"
    assert "password" not in data
    assert "hashed_password" not in data


def test_signup_duplicate_email_fails(client):
    client.post("/auth/signup", json={
        "email": "dupe@example.com",
        "password": "testpass123"
    })
    response = client.post("/auth/signup", json={
        "email": "dupe@example.com",
        "password": "differentpass456"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success(client):
    client.post("/auth/signup", json={
        "email": "loginuser@example.com",
        "password": "testpass123"
    })
    response = client.post("/auth/login", data={
        "username": "loginuser@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_fails(client):
    client.post("/auth/signup", json={
        "email": "wrongpassuser@example.com",
        "password": "correctpass123"
    })
    response = client.post("/auth/login", data={
        "username": "wrongpassuser@example.com",
        "password": "incorrectpass456"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_protected_route_without_token_fails(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_protected_route_with_valid_token(client):
    client.post("/auth/signup", json={
        "email": "meuser@example.com",
        "password": "testpass123"
    })
    login_response = client.post("/auth/login", data={
        "username": "meuser@example.com",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "meuser@example.com"