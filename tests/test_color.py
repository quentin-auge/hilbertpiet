import pytest

from hilbertpiet.color import Color

lightness_hue_params = [(lightness, hue) for lightness in range(4) for hue in range(7)]


@pytest.mark.parametrize('lightness, hue', lightness_hue_params)
def test_init(lightness, hue):
    color = Color(lightness, hue)
    for hue_shift in (0, 6, -6, 12, -12):
        for lightness_shift in (0, 3, -3, 6, -6):
            assert Color(lightness + lightness_shift, hue + hue_shift) == color


@pytest.mark.parametrize('lightness, hue', lightness_hue_params)
def test_to_from_name(lightness, hue):
    color = Color(lightness, hue)
    actual_color = Color.from_name(str(color))
    assert color == actual_color


invalid_color_names = ['graen', 'vdarkgreen', 'ightgreen', 'lightgreeen', 'darkgren']


@pytest.mark.parametrize('invalid_color_name', invalid_color_names)
def test_invalid_color_name(invalid_color_name):
    with pytest.raises(ValueError, match='Invalid color name'):
        color = Color.from_name(invalid_color_name)
        print(color)


color_name_to_codes = [('lightred', '#FFC0C0'), ('lightyellow', '#FFFFC0'),
                       ('lightgreen', '#C0FFC0'), ('lightcyan', '#C0FFFF'),
                       ('lightblue', '#C0C0FF'), ('lightmagenta', '#FFC0FF'),
                       ('red', '#FF0000'), ('yellow', '#FFFF00'), ('green', '#00FF00'),
                       ('cyan', '#00FFFF'), ('blue', '#0000FF'), ('magenta', '#FF00FF'),
                       ('darkred', '#C00000'), ('darkyellow', '#C0C000'),
                       ('darkgreen', '#00C000'), ('darkcyan', '#00C0C0'),
                       ('darkblue', '#0000C0'), ('darkmagenta', '#C000C0')]


@pytest.mark.parametrize('color_name, expected_color_code', color_name_to_codes)
def test_color_codes(color_name, expected_color_code):
    color = Color.from_name(color_name)
    color_code = color.code
    assert color_code == expected_color_code
