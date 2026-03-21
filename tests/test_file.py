
async def test_upload(client, auth_headers):
    """Test that an authenticated user can upload a file successfully."""
    response = await client.post(
        "/files/",
        files={"file": ("test.txt", b"Test Content", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test.txt"
    assert data["file_size"] == len(b"Test Content")
    assert data["file_type"] == "text/plain"
    assert data["s3_key"]

async def test_upload_file_to_folder(client, auth_headers):
    """Test that a file can be uploaded directly into a specific folder."""
    folder_response = await client.post(
        "/folders/",
        json={"name": "Test Folder"},
        headers=auth_headers,
    )
    assert folder_response.status_code == 200
    folder_data = folder_response.json()
    file_response = await client.post(
        "/files/",
        files={"file": ("test.txt", b"Test Content", "text/plain")},
        params={"folder_id": folder_data["id"]},
        headers=auth_headers,
    )
    assert file_response.status_code == 200
    data = file_response.json()
    assert data["folder_id"] == folder_data["id"]
    assert data["name"] == "test.txt"
    assert data["s3_key"]
    assert data["file_type"] == "text/plain"

async def test_list_files(client, auth_headers):
    """Test that listing files returns only root-level files, excluding files inside folders."""
    folder_response = await client.post(
        "/folders/",
        json={"name": "Test Folder"},
        headers=auth_headers,
    )

    assert folder_response.status_code == 200

    files = [{"file": (f"test{i}.txt", b"File Content %d" % i, "text/plain")} for i in range(5)]
    created_files = []
    for file in files:
        response = await client.post(
            "/files/",
            files=file,
            headers=auth_headers,
        )
        created_files.append(response)

    await client.post(
        "/files/",
        files={"file": ("test1.txt", b"File Content 1", "text/plain")},
        params={"folder_id": folder_response.json()["id"]},
        headers=auth_headers,
    )
    list_files_response = await client.get(
        "/files/",
        headers=auth_headers
    )
    
    assert list_files_response.status_code == 200
    listed_files_data = list_files_response.json()
    assert isinstance(listed_files_data["files"], list)
    # File in folder should NOT appear when listing root-level files
    assert len(listed_files_data["files"]) == 5

async def test_get_file_by_id(client, auth_headers):
    """Test that a single file can be retrieved by its ID."""
    file_response = await client.post(
        "/files/",
        files={"file": ("test.txt", b"Test Content", "text/plain")},
        headers=auth_headers,
    )
    assert file_response.status_code == 200
    file_id = file_response.json()["id"]
    get_file_response = await client.get(
        f"/files/{file_id}",
        headers=auth_headers,
    )
    assert get_file_response.status_code == 200
    data = get_file_response.json()
    assert data["id"] == file_id

async def test_get_nonexistent_file(client, auth_headers):
    """Test that requesting a file that does not exist returns 404."""
    response = await client.get(
        "/files/12763",
        headers=auth_headers,
    )

    assert response.status_code == 404

async def test_download_file(client, auth_headers):
    """Test that a file can be downloaded and its content matches what was uploaded."""
    file_response = await client.post(
        "/files/",
        files={"file": ("test.txt", b"Test Content", "text/plain")},
        headers=auth_headers,
    )
    assert file_response.status_code == 200
    file_id = file_response.json()["id"]

    download_file_response = await client.get(
        f"/files/{file_id}/download",
        headers=auth_headers,
    )
    assert download_file_response.status_code == 200
    assert download_file_response.content == b"Test Content"

async def test_delete_file(client, auth_headers):
    """Test that an authenticated user can delete a file successfully."""
    file_response = await client.post(
        "/files/",
        files={"file": ("test.txt", b"Test Content", "text/plain")},
        headers=auth_headers,
    )
    assert file_response.status_code == 200
    file_id = file_response.json()["id"]

    delete_response = await client.delete(
        f"/files/{file_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

async def test_unauthenticated_access(client):
    """Test that file upload without a token is rejected with 401."""
    response = await client.post(
        "/files/",
        files={"file": ("test.txt", b"Unauthorized File", "text/plain")},
    )
    assert response.status_code == 401