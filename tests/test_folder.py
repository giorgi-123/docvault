
async def test_create_folder(client, auth_headers):
    """Test that an authenticated user can create a folder successfully."""
    response = await client.post(
        "/folders/",
        json={"name": "Test Folder"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Folder"

async def test_create_subfolder(client, auth_headers):
    """Test that a folder can be created as a child of another folder."""
    root_folder = await client.post(
        "/folders/", 
        json={"name": "Root Folder"}, 
        headers=auth_headers,
    )
    root_folder_data = root_folder.json()
    child_folder = await client.post(
        "/folders/",
        json={"name": "Child Folder", "parent_id": root_folder_data["id"]},
        headers=auth_headers,
    )
    assert child_folder.status_code == 200
    child_folder_data = child_folder.json()
    assert child_folder_data["parent_id"] == root_folder_data["id"]
    assert child_folder_data["name"] == "Child Folder"

async def test_list_folders(client, auth_headers):
    """Test that listing folders returns all root-level folders for the authenticated user."""
    folders = [{"name": f"Folder {i}"} for i in range(5)]
    created_folders = []
    for folder in folders:
        response = await client.post(
            "/folders/",
            json=folder,
            headers=auth_headers,
        )
        created_folders.append(response)
    
    list_folders_response = await client.get(
        "/folders/",
        headers=auth_headers,
    )

    assert list_folders_response.status_code == 200
    data = list_folders_response.json()
    assert isinstance(data["folders"], list)
    assert len(data["folders"]) == 5

async def test_get_folder_by_id(client, auth_headers):
    """Test that a single folder can be retrieved by its ID."""
    folder = await client.post(
        "/folders/",
        json={"name": "Test Folder"},
        headers=auth_headers,
    )
    folder_data = folder.json()
    folder_id = folder_data["id"]
    response = await client.get(
        f"/folders/{folder_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == folder_id

async def test_get_nonexistent_folder(client, auth_headers):
    """Test that requesting a folder that does not exist returns 404."""
    response = await client.get(
        "/folders/24", # since we are not creating anything and there is not record with id 24 in database ...
        headers=auth_headers,
    )
    assert response.status_code == 404

async def test_delete_folder(client, auth_headers):
    """Test that an authenticated user can delete a folder successfully."""
    folder = await client.post(
        "/folders/",
        json={"name": "Deletable Folder"},
        headers=auth_headers,
    )
    folder_data = folder.json()
    folder_id = folder_data["id"]
    
    response = await client.delete(
        f"/folders/{folder_id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

async def test_delete_folder_with_subfolders(client, auth_headers):
    """Test that deleting a folder with subfolders is blocked and returns 403."""
    parent_folder_response = await client.post(
        "/folders/",
        json={"name": "Parent Folder"},
        headers=auth_headers,
    )
    parent_data = parent_folder_response.json()
    parent_id = parent_data["id"]

    await client.post(
        "/folders/",
        json={"name": "Child Folder", "parent_id": parent_id},
        headers=auth_headers,
    )
    delete_response = await client.delete(
        f"/folders/{parent_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 403

async def test_unauthenticated_access(client):
    """Test that requests without a token are rejected with 401."""
    response = await client.post(
        "/folders/",
        json={"name": "Unauthorized Folder"},
    )

    assert response.status_code == 401

async def test_wrong_access_token(client):
    """Test that requests with an invalid token are rejected with 401."""
    response = await client.post(
        "/folders/",
        json={"name": "Unauthorized Folder"},
        headers={"Authorization": "Bearer somekindoftoken"}
    )

    assert response.status_code == 401
