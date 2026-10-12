from status.labels import FIVE_STATUSES, is_valid_status


def test_exactly_five_statuses():
    assert len(FIVE_STATUSES) == 5


def test_known_labels_valid():
    for label in FIVE_STATUSES:
        assert is_valid_status(label) is True


def test_unknown_label_invalid():
    assert is_valid_status('some other label') is False
