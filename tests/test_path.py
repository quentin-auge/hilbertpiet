import pytest

from piet.path import stretch_path

n_forwards_factors_params = [(n_forwards, factor)
                             for n_forwards in range(4)
                             for factor in range(1, 4)]


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_start_end(n_forwards, factor):
    path = 'F' * n_forwards

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = 'F' * expected_n_forwards

    assert stretch_path(path, factor) == expected_path


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_start(n_forwards, factor):
    path = '+' + 'F' * n_forwards

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = '+' + 'F' * expected_n_forwards

    assert stretch_path(path, factor) == expected_path


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_end(n_forwards, factor):
    path = 'F' * n_forwards + '+'

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = 'F' * expected_n_forwards + '+'

    assert stretch_path(path, factor) == expected_path


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_middle(n_forwards, factor):
    path = '+' + 'F' * n_forwards + '+'

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = '+' + 'F' * expected_n_forwards + '+'

    assert stretch_path(path, factor) == expected_path


@pytest.mark.parametrize('n_forwards,factor', n_forwards_factors_params)
def test_stretch_path_mixed_middle(n_forwards, factor):
    path = '+' + 'F' * n_forwards * 2
    path += '-o-' + 'F' * n_forwards * 3
    path += '-p-' + 'F' * n_forwards + '+'

    expected_n_forwards = 1 if n_forwards == 1 else n_forwards * factor
    expected_path = '+' + 'F' * n_forwards * 2 * factor
    expected_path += '-o-' + 'F' * n_forwards * 3 * factor
    expected_path += '-p-' + 'F' * expected_n_forwards + '+'

    assert stretch_path(path, factor) == expected_path
