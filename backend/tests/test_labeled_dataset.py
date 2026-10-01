from collections import Counter

from app.data.comments import comments
from eval.evaluate import load_dataset
from eval.metrics import LABELS

SOURCES = {"fixture", "reddit"}


def test_every_item_is_well_formed():
    for item in load_dataset():
        assert set(item) == {"id", "product_id", "text", "label", "source"}
        assert item["label"] in LABELS
        assert item["source"] in SOURCES
        assert item["text"].strip()


def test_ids_are_unique():
    ids = [item["id"] for item in load_dataset()]

    assert len(ids) == len(set(ids))


def test_every_fixture_comment_appears_exactly_once_with_its_product():
    fixture_items = [i for i in load_dataset() if i["source"] == "fixture"]
    labeled = Counter((i["product_id"], i["text"]) for i in fixture_items)
    expected = Counter(
        (product_id, text)
        for product_id, texts in comments.items()
        for text in texts
    )

    assert labeled == expected
