from app.pricing import can_transition, compute_price


def test_prix_standard():
    # 4.90 + 10 kg x 0.80 + 100 km x 0.05 = 17.90
    assert compute_price(10, 100) == 17.90


def test_prix_minimum():
    # 4.90 + 0.80 + 0.05 = 5.75 -> relevé au minimum de 6.00
    assert compute_price(1, 1) == 6.00


def test_prix_express_majore_de_30_pourcent():
    # 17.90 x 1.30 = 23.27
    assert compute_price(10, 100, express=True) == 23.27


def test_transitions_autorisees():
    assert can_transition("CREATED", "IN_TRANSIT")
    assert can_transition("IN_TRANSIT", "DELIVERED")


def test_transitions_interdites():
    assert not can_transition("DELIVERED", "IN_TRANSIT")
    assert not can_transition("CREATED", "DELIVERED")
    assert not can_transition("INCONNU", "CREATED")
