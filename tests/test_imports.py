import childespython

def test_imports():
    assert hasattr(childespython, "ChildesDataset")
    assert hasattr(childespython, "Transcript")

    from childespython import ChildesDataset, Transcript

    assert ChildesDataset is not None
    assert Transcript is not None
