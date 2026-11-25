import pytest
from app.models.product import Product, ProductVariant


@pytest.fixture()
def seeded_products(db_session):
    blusa = Product(
        name="Blusa Vela",
        description="Blusa liviana de lino natural",
        price=33000,
        categoria="BLUSA",
        is_unique=False,
        variants=[
            ProductVariant(color="Bordo", talle="S", stock=2),
            ProductVariant(color="Bordo", talle="M", stock=3),
            ProductVariant(color="Beige", talle="L", stock=1),
        ],
    )
    jean = Product(
        name="Jean Recto Vintage",
        description="Denim rígido tiro alto",
        price=48000,
        categoria="PANTALON",
        is_unique=True,
        color="Terracota",
        talle="38",
        stock=1,
    )
    remera = Product(
        name="Remera Básica Algodón",
        description="Algodón peinado suave",
        price=19500,
        categoria="REMERA",
        is_unique=False,
        variants=[ProductVariant(color="Negro", talle="M", stock=4)],
    )
    campera = Product(
        name="Campera Cuero Eco",
        description="Forrada en satén",
        price=62000,
        categoria="ABRIGO",
        is_unique=True,
        color="Negro",
        talle="M",
        stock=0,
    )
    db_session.add_all([blusa, jean, remera, campera])
    db_session.commit()
    return [blusa, jean, remera, campera]


def test_search_by_name_case_insensitive(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "VELA"})
    assert res.status_code == 200
    data = res.json()
    assert [p["name"] for p in data] == ["Blusa Vela"]


def test_search_by_category(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "pantalon"})
    assert res.status_code == 200
    data = res.json()
    assert [p["name"] for p in data] == ["Jean Recto Vintage"]


def test_search_by_description(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "lino"})
    assert res.status_code == 200
    data = res.json()
    assert [p["name"] for p in data] == ["Blusa Vela"]


def test_search_by_unique_product_color(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "terracota"})
    assert res.status_code == 200
    data = res.json()
    assert [p["name"] for p in data] == ["Jean Recto Vintage"]


def test_search_by_variant_color_without_duplicates(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "bordo"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "Blusa Vela"


def test_search_matches_both_unique_and_variant_color(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "negro"})
    assert res.status_code == 200
    names = {p["name"] for p in res.json()}
    assert names == {"Remera Básica Algodón", "Campera Cuero Eco"}


def test_search_respects_limit(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "negro", "limit": 1})
    assert res.status_code == 200
    assert len(res.json()) == 1

    all_limited = client.get("/api/v1/products/", params={"limit": 2})
    assert all_limited.status_code == 200
    assert len(all_limited.json()) == 2

    over_limit = client.get("/api/v1/products/", params={"limit": 101})
    assert over_limit.status_code == 422


def test_search_no_results(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "inexistente123"})
    assert res.status_code == 200
    assert res.json() == []


def test_search_blank_query_returns_all(client, seeded_products):
    res = client.get("/api/v1/products/", params={"q": "   "})
    assert res.status_code == 200
    assert len(res.json()) == len(seeded_products)
