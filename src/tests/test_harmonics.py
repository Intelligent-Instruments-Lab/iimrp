import pytest
import numpy as np

from iimrp import *

@pytest.fixture
def setup() -> np.ndarray:
    H, N, A0_freq = MAX_HARMONICS, 88, 27.5
    harmonics = create_harmonics(H, N, A0_freq)
    return (harmonics, H, N, A0_freq)

def test_create_harmonics(setup):
    harmonics, H, N, A0_freq = setup
    # print(f"test_create_harmonics: {harmonics}")
    assert harmonics.shape == (N, H)
    assert harmonics[0,0] == A0_freq

