from pydantic import BaseModel
from testfixtures import compare
from testfixtures.comparison import CompareContext


class SampleModel(BaseModel):
    id: int
    name: str


def test_compare_mapped_object_equal():
    obj1 = SampleModel(id=1, name="test")
    obj2 = SampleModel(id=1, name="test")
    # Test the registered comparison function through compare
    result = compare(obj1, obj2)
    assert result is None


def test_compare_mapped_object_different():
    from testfixtures import ShouldRaise

    obj1 = SampleModel(id=1, name="test")
    obj2 = SampleModel(id=2, name="test")
    # This should raise an assertion error since they're different
    with ShouldRaise(AssertionError):
        compare(obj1, obj2, strict=True)
