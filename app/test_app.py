"""Tests run without AWS: S3 and the AI calls are replaced with in-memory fakes."""
import io
import json

import pytest

import ai
import app as smartdrive


@pytest.fixture
def client(monkeypatch):
    store = {}  # pretend S3 bucket: key -> bytes / JSON text
    monkeypatch.setattr(smartdrive, "load_json", lambda key: json.loads(store.get(key, "{}")))
    monkeypatch.setattr(smartdrive, "save_json", lambda key, data: store.__setitem__(key, json.dumps(data)))
    monkeypatch.setattr(smartdrive, "put_file", lambda key, data, content_type: store.__setitem__(key, data))
    monkeypatch.setattr(smartdrive, "get_file", lambda key: store[key])
    monkeypatch.setattr(smartdrive, "delete_file", lambda key: store.pop(key))
    monkeypatch.setattr(smartdrive, "auto_tags", lambda name, data: ["Dog", "Grass"])
    smartdrive.app.config["TESTING"] = True
    return smartdrive.app.test_client()


def register(client, email, password="secret123"):
    return client.post("/register", data={"email": email, "password": password}, follow_redirects=True)


def login(client, email, password="secret123"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)


def upload(client, name="dog.jpg", data=b"fake image"):
    return client.post("/upload", data={"file": (io.BytesIO(data), name)},
                       content_type="multipart/form-data", follow_redirects=True)


def only_file():
    return next(iter(smartdrive.load_json(smartdrive.FILES).values()))


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_pages_need_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_register_and_login(client):
    register(client, "a@test.com")
    client.get("/logout")
    assert b"Wrong email or password" in login(client, "a@test.com", "wrong-password").data
    assert b"a@test.com" in login(client, "a@test.com").data


def test_upload_tags_and_search(client):
    register(client, "a@test.com")
    page = upload(client).data
    assert b"dog.jpg" in page and b"Grass" in page
    assert b"dog.jpg" in client.get("/?q=grass").data
    assert b"dog.jpg" not in client.get("/?q=cat").data


def test_share_with_another_user(client):
    register(client, "b@test.com")
    client.get("/logout")
    register(client, "a@test.com")
    upload(client)
    file_id = only_file()["id"]
    client.post(f"/share/{file_id}", data={"email": "b@test.com"})
    client.get("/logout")

    login(client, "b@test.com")
    assert b"dog.jpg" in client.get("/").data
    assert client.get(f"/download/{file_id}").data == b"fake image"


def test_strangers_cannot_download(client):
    register(client, "a@test.com")
    upload(client)
    file_id = only_file()["id"]
    client.get("/logout")
    register(client, "c@test.com")
    assert client.get(f"/download/{file_id}").status_code == 403


def test_public_link_on_and_off(client):
    register(client, "a@test.com")
    upload(client)
    file_id = only_file()["id"]
    client.post(f"/link/{file_id}")
    token = only_file()["public_token"]

    client.get("/logout")
    assert client.get(f"/s/{token}").data == b"fake image"

    login(client, "a@test.com")
    client.post(f"/link/{file_id}")
    assert client.get(f"/s/{token}").status_code == 404


def test_delete(client):
    register(client, "a@test.com")
    upload(client)
    client.post(f"/delete/{only_file()['id']}")
    assert smartdrive.load_json(smartdrive.FILES) == {}


def test_text_tags_use_most_common_phrases(monkeypatch):
    class FakeComprehend:
        def detect_key_phrases(self, Text, LanguageCode):
            return {"KeyPhrases": [{"Text": "the invoice"}, {"Text": "AWS"}, {"Text": "Invoice"}]}

    monkeypatch.setattr(ai.boto3, "client", lambda *args, **kwargs: FakeComprehend())
    assert ai.auto_tags("notes.txt", b"Invoice for AWS usage") == ["invoice", "AWS"]


def test_ai_failure_never_breaks_upload(monkeypatch):
    def broken_client(*args, **kwargs):
        raise RuntimeError("no AWS credentials")

    monkeypatch.setattr(ai.boto3, "client", broken_client)
    assert ai.auto_tags("photo.png", b"not really a png") == []
