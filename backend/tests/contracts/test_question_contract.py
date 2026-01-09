import pytest

from domain.content_generation.generators.factors_multiples import FactorsMultiplesIntegrated


def _assert_meta_contract(q):
    assert isinstance(q.meta, dict)
    for k in ["subject", "chapter", "concept_id", "concept_key", "difficulty", "bloom_level"]:
        assert k in q.meta, f"meta missing {k}"


def _assert_misconception_contract(q):
    assert isinstance(q.misconception_info, list)
    assert len(q.misconception_info) == len(q.options)

    seen = set()
    for m in q.misconception_info:
        assert "option_index" in m
        assert "value" in m
        assert "is_correct" in m
        seen.add(m["option_index"])

    assert seen == set(range(len(q.options)))

    # Ensure exactly one correct option exists.
    correct_count = sum(1 for m in q.misconception_info if m.get("is_correct") is True)
    assert correct_count == 1


@pytest.mark.parametrize("_", range(20))
def test_generated_questions_meet_contract(_):
    gen = FactorsMultiplesIntegrated()
    q = gen.generate()

    _assert_meta_contract(q)
    _assert_misconception_contract(q)
