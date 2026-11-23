import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


DIRECTIONS = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))
MOVES = ((1, 1), (-1, 2), (2, -1), (-1, -1), (1, -2), (-2, 1))


def step(points):
    counts = Counter((first + delta_first, second + delta_second)
                     for first, second in points for delta_first, delta_second in DIRECTIONS)
    return points | {point for point, count in counts.items() if count >= 2}


def hexagon(lower, width, point):
    first, second = point
    return 0 <= first <= width and 0 <= second <= width and lower <= first + second <= 2 * width - lower


def shape(seed_count, iteration):
    width = seed_count - 1 + 2 * iteration
    return {
        ((2 * first + second) // 3 - iteration, (second - first) // 3)
        for first in range(width + 1)
        for second in range(width + 1)
        if first % 3 == second % 3 and iteration < first + second < 2 * width - iteration
    }


def corner_twice(iteration):
    quotient, residue = divmod(iteration, 3)
    return 3 * quotient * quotient + (3, 5, 7)[residue] * quotient + (2, 2, 4)[residue]


def count_formula(seed_count, iteration):
    if iteration == 0:
        return seed_count
    if iteration == 1:
        return 3 * seed_count - 2
    width = seed_count - 1 + 2 * iteration
    return sum(((width + 3 - residue) // 3) ** 2 for residue in range(3)) - corner_twice(iteration)


def clipped_shape(seed_count, iteration):
    return {point for point in shape(seed_count, iteration) if abs(point[1]) <= iteration}


def shannon(iteration):
    if iteration == 0:
        return 2
    return (3 * iteration * iteration + 5 * iteration + (0, 4, 2)[iteration % 3]) // 3


def coefficients(numerator, denominator, length):
    result = []
    assert denominator[0] == 1
    for index in range(length):
        value = numerator[index] if index < len(numerator) else 0
        value -= sum(denominator[offset] * result[index - offset]
                     for offset in range(1, min(index + 1, len(denominator))))
        result.append(value)
    return result


def selected_moves(lower, width, point):
    first, second = point
    if first + second == lower - 1:
        return ((1, 1), (-1, 2)) if first >= 1 else ((1, 1), (2, -1))
    if first + second == 2 * width - lower + 1:
        return ((-1, -1), (1, -2)) if first <= width - 1 else ((-1, -1), (-2, 1))
    if first == -1:
        return ((2, -1), (1, 1)) if second <= lower + 1 else ((2, -1), (1, -2))
    if first == width + 1:
        return ((-2, 1), (-1, -1)) if width - second <= lower + 1 else ((-2, 1), (-1, 2))
    if second == -1:
        return ((-1, 2), (1, 1)) if first <= lower + 1 else ((-1, 2), (-2, 1))
    if second == width + 1:
        return ((1, -2), (-1, -1)) if width - first <= lower + 1 else ((1, -2), (2, -1))
    raise AssertionError('Missing boundary case')


def verify():
    geometry_cases = 0
    geometry_classes = Counter()
    for first in range(-4, 5):
        for second in range(-4, 5):
            norm = first * first + first * second + second * second
            if 0 < norm <= 4:
                common = {(delta_first, delta_second) for delta_first, delta_second in DIRECTIONS
                          if (delta_first - first, delta_second - second) in DIRECTIONS}
                assert norm in (1, 3, 4)
                assert len(common) == (1 if norm == 4 else 2)
                geometry_cases += 1
                geometry_classes[norm] += 1
    hex_cases = 0
    boundary_cases = 0
    for lower in range(3, 13):
        for width in range(lower + 2, lower + 13):
            for first in range(-3, width + 4):
                for second in range(-3, width + 4):
                    point = (first, second)
                    old = hexagon(lower, width, point)
                    expanded = hexagon(lower + 1, width + 2, (first + 1, second + 1))
                    neighbors = sum(hexagon(lower, width, (first + delta_first, second + delta_second))
                                    for delta_first, delta_second in MOVES)
                    assert expanded == (old or neighbors >= 2)
                    if expanded and not old:
                        chosen = selected_moves(lower, width, point)
                        assert len(set(chosen)) == 2
                        assert all(move in MOVES for move in chosen)
                        assert all(hexagon(lower, width, (first + delta_first, second + delta_second))
                                   for delta_first, delta_second in chosen)
                        boundary_cases += 1
                    hex_cases += 1
    counts = {}
    growth_cases = 0
    for seed_count in range(2, 6):
        points = {(index, 0) for index in range(seed_count)}
        terms = []
        for iteration in range(41):
            terms.append(len(points))
            assert len(points) == count_formula(seed_count, iteration)
            if iteration >= 2:
                assert points == shape(seed_count, iteration)
            if iteration == 2:
                intervals = {-2: (2, seed_count - 1), -1: (0, seed_count),
                             0: (0, seed_count - 1), 1: (-1, seed_count - 1),
                             2: (0, seed_count - 3)}
                rows = {(first, second) for second, (left, right) in intervals.items()
                        for first in range(left, right + 1)}
                assert points == rows
            if seed_count == 2:
                assert len(points) == shannon(iteration)
            if seed_count == 3:
                expected = iteration * iteration + 3 * iteration + (1 if iteration > 0 and iteration % 3 == 0 else 3)
                assert len(points) == expected
            if seed_count == 4:
                assert 3 * len(points) == 3 * iteration * iteration + 13 * iteration + 12 + 2 * (iteration % 3)
            if seed_count == 5 and iteration >= 2:
                assert len(points) == shannon(iteration) + 4 * iteration + 7
                assert 3 * len(points) == 3 * iteration * iteration + 17 * iteration + 25 - 2 * ((iteration - 1) % 3)
            points = step(points)
            growth_cases += 1
        counts[str(seed_count)] = terms
    algebra_cases = 0
    denominator = [1, -2, 1, -1, 2, -1]
    numerators = {
        2: [2, 0, 2, 0, 4, -2],
        3: [3, 1, 2, -3, 5, -2],
        4: [4, 2, 2, -4, 2],
        5: [5, 3, 2, -5, 1, -2, 2],
    }
    for seed_count, numerator in numerators.items():
        terms = coefficients(numerator, denominator, 1001)
        assert terms == [count_formula(seed_count, iteration) for iteration in range(1001)]
        algebra_cases += len(terms)
    barker = coefficients([2, 0, 2, -2, 2, 2], [1, -1, 0, -1, 1], 1002)
    for iteration in range(2, 1001):
        increment = shannon(iteration) - shannon(iteration - 1)
        assert increment == 2 * iteration + (2 if iteration % 3 == 1 else 0)
        assert increment == barker[iteration + 1]
        algebra_cases += 1
    assert barker[3] == 4 and shannon(3) - shannon(2) == 6
    general_growth_cases = 0
    stable_count_cases = 0
    onset_obstructions = 0
    for seed_count in range(2, 21):
        points = {(index, 0) for index in range(seed_count)}
        for iteration in range(31):
            if iteration >= 2:
                complete_hexagon = shape(seed_count, iteration)
                assert points == clipped_shape(seed_count, iteration)
                assert (points == complete_hexagon) == (iteration >= seed_count - 3)
                if iteration >= seed_count - 3:
                    assert len(points) == count_formula(seed_count, iteration)
                    stable_count_cases += 1
                else:
                    witness = (1, iteration + 1)
                    assert witness in complete_hexagon - points
                    onset_obstructions += 1
                if iteration >= max(2, seed_count):
                    assert count_formula(seed_count + 3, iteration) - len(points) == 4 * iteration + 2 * seed_count + 3
            points = step(points)
            general_growth_cases += 1
    six_seed_points = {(index, 0) for index in range(6)}
    six_seed_points = step(step(six_seed_points))
    assert len(six_seed_points) == 28
    assert shape(6, 2) - six_seed_points == {(1, 3), (4, -3)}
    petal = coefficients([0, 1, 5, 6, 11, -5], denominator, 1004)
    petal_relations = 0
    second_difference_cases = 0
    for iteration in range(2, 1001):
        assert petal[iteration + 3] == 3 * count_formula(5, iteration) - 2
        petal_relations += 1
    for iteration in range(3, 1004):
        assert petal[iteration] - 2 * petal[iteration - 1] + petal[iteration - 2] == (6, 12, 0)[iteration % 3]
        second_difference_cases += 1
    for iteration in range(4, 1001):
        assert count_formula(5, iteration) - 2 * count_formula(5, iteration - 1) + count_formula(5, iteration - 2) == (2, 4, 0)[iteration % 3]
        second_difference_cases += 1
    return {
        'arithmetic': 'exact Python integers; no floating-point operations',
        'circle_displacements': {'coordinate_box': [-4, 4], 'eligible_cases': geometry_cases,
                                 'norm_classes': dict(sorted(geometry_classes.items()))},
        'hexagon_identity': {'A': [3, 12], 'L_minus_A': [2, 12], 'candidate_points': hex_cases,
                             'constructive_boundary_cases': boundary_cases},
        'growth': {'seed_counts': [2, 3, 4, 5], 'iterations': [0, 40], 'states': growth_cases,
                   'first_eleven_counts': {key: value[:11] for key, value in counts.items()}},
        'generating_functions_and_increments': {'iterations': [0, 1000], 'identities_checked': algebra_cases},
        'arbitrary_seed_shapes': {'seed_counts': [2, 20], 'iterations': [0, 30],
                                 'states': general_growth_cases, 'stable_count_cases': stable_count_cases,
                                 'pre_stabilization_witnesses': onset_obstructions,
                                 'six_seed_step_two': {'occupied': 28, 'unclipped': 30,
                                                      'extra_axial_sites': [[1, 3], [4, -3]]}},
        'sibling_series': {'five_seed_petal_relations': petal_relations,
                           'periodic_second_difference_identities': second_difference_cases,
                           'scope': 'The petal sequence here is defined by the cited rational generating function.'},
        'scope': 'Finite checks support the written all-iteration proof in note.tex; the bounds above are finite.',
        'status': 'pass',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    result = verify()
    result['checker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    content = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if arguments.output:
        arguments.output.write_text(content)
    print(content, end='')


if __name__ == '__main__':
    main()
