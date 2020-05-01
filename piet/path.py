def generate_path(n_iterations: int) -> str:
    """
    Generate path as a string of turtle instructions to trace a Hilbert curve II after a given
    number of iterations.

    Notes:
        Instructions are `F` (forward), `+` (turn right), `-` (turn left).
        https://elc.github.io/posts/plotting-fractals-step-by-step-with-python/#hilbert-curve-ii.
    """

    # L-system rules for Hilbert curve II
    rules = {'X': 'XFYFX+F+YFXFY-F-XFYFX', 'Y': 'YFXFY-F-XFYFX+F+YFXFY'}
    path = 'X'

    if n_iterations <= 0:
        return path

    for _ in range(n_iterations):
        path = ''.join(rules.get(c, c) for c in path)

    path = path.replace('X', '').replace('Y', '')

    return path


def stretch_path(path: str, factor: int) -> str:
    """
    Stretch a path so that `n` consecutive forwards (`F`) become  `n * factor` consecutive forwards.
    """

    path += '$'
    i = 0
    stretched_path = ''
    n_forward = 0
    while i < len(path):
        c = path[i] if path[i] != '$' else ''
        if c != 'F':
            forwards = 'F' * n_forward * factor if n_forward != 1 else 'F'
            stretched_path += forwards + c
            n_forward = 0
        else:
            n_forward += 1
        i += 1

    return stretched_path
