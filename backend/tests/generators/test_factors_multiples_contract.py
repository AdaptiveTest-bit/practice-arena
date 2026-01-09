import pytest

from domain.content_generation.generators.factors_multiples import FactorsMultiplesIntegrated


@pytest.mark.parametrize("_", range(25))
def test_factors_multiples_question_has_meta_and_misconception_info(_):
    q = FactorsMultiplesIntegrated().generate()

    assert q.meta is not None
    assert q.misconception_info is not None
    assert len(q.misconception_info) == len(q.options)
    assert q.correct_option_index in range(len(q.options))
