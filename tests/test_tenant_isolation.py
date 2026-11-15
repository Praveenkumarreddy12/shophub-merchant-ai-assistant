
def test_merchant_can_access_own_orders(
    client,
    merchant_1_headers
):
    response = client.get(
        "/orders",
        headers=merchant_1_headers
    )

    assert response.status_code == 200


def test_merchant_cannot_access_other_merchant_orders(
    client,
    merchant_1_headers
):
    # Merchant 1 tries to access Merchant 2's order.
    response = client.get(
        "/orders/lookup",
        params={"id": "E001"},
        headers=merchant_1_headers
    )

    # Foreign orders must not be exposed.
    if response.status_code == 200:
        data = response.json()
        assert data.get("status") is False

    else:
        assert response.status_code in (401, 403, 404)


def test_merchant_2_cannot_access_merchant_1_orders(
    client,
    merchant_2_headers
):
    response = client.get(
        "/orders/lookup",
        params={"id": "F001"},
        headers=merchant_2_headers
    )

    if response.status_code == 200:
        assert response.json().get("status") is False
    else:
        assert response.status_code in (401, 403, 404)


def test_orphan_token_cannot_access_orders(
    client,
    orphan_headers
):
    response = client.get(
        "/orders",
        headers=orphan_headers
    )

    assert response.status_code in (401, 403, 404)
