from app.utils.risk_classifier import classify_risk


def test_low_risk():
    assert classify_risk(0.2) == "Bajo"


def test_medium_risk():
    assert classify_risk(0.5) == "Medio"


def test_high_risk():
    assert classify_risk(0.9) == "Alto"


def test_invalid_probability():
    try:
        classify_risk(1.5)
        assert False
    except ValueError:
        assert True


def test_invalid_thresholds():
    try:
        classify_risk(
            probability=0.5,
            low_threshold=0.8,
            high_threshold=0.4
        )
        assert False
    except ValueError:
        assert True