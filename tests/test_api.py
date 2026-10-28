COLIS = {
    "reference": "FR-0001",
    "recipient": "Atelier Martin",
    "city": "Lyon",
    "weight_kg": 10,
    "distance_km": 100,
}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "up"}


def test_version(client):
    r = client.get("/version")
    assert r.status_code == 200
    assert set(r.json()) == {"version", "commit", "env"}


def test_creation_sans_cle_refusee(client):
    r = client.post("/shipments", json=COLIS)
    assert r.status_code == 401


def test_creation_et_lecture(client, auth):
    r = client.post("/shipments", json=COLIS, headers=auth)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "CREATED"
    assert body["price_eur"] == 17.90

    r = client.get(f"/shipments/{body['id']}")
    assert r.status_code == 200
    assert r.json()["reference"] == "FR-0001"


def test_reference_en_double(client, auth):
    client.post("/shipments", json=COLIS, headers=auth)
    r = client.post("/shipments", json=COLIS, headers=auth)
    assert r.status_code == 409


def test_cycle_de_vie(client, auth):
    sid = client.post("/shipments", json=COLIS, headers=auth).json()["id"]
    r = client.patch(f"/shipments/{sid}/status", json={"status": "IN_TRANSIT"}, headers=auth)
    assert r.status_code == 200
    r = client.patch(f"/shipments/{sid}/status", json={"status": "CREATED"}, headers=auth)
    assert r.status_code == 422


def test_import_csv(client, auth):
    csv_data = (
        "reference;recipient;city;weight_kg;distance_km;express\n"
        "FR-0101;Boulangerie Roux;Nantes;2.5;380;oui\n"
        "FR-0102;Garage Lopez;Lille;-4;220;non\n"
    )
    files = {"file": ("colis.csv", csv_data, "text/csv")}
    r = client.post("/shipments/import", files=files, headers=auth)
    assert r.status_code == 200
    assert r.json()["created"] == 1
    assert len(r.json()["errors"]) == 1
