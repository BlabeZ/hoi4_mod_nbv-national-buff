"""Reserve space for audited sidebar layouts when building the interface.

This is NOT runtime GUI detection and does not inspect a user's playsets.
The shipped fixed slot is safe for the known layouts, so normal game launching
needs no helper. Unknown layouts require another audited reservation.
"""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int


DEFAULT = Rect(0, -202, 77, 77)
GAP = 10

# Coordinates use the entry's raid_filter parent. KR shares this parent, so its
# runtime height/position cancels. EAW's other parent is bottom-right anchored:
# at raid_filter height zero its lore background/button union is (-11,-4,87,74).
# A positive native raid_filter height only moves NBV farther above that union.
# We reserve this nearest possible union rather than reading foreign flags or
# referencing a modifier/trigger that would be undefined without that mod.
RESERVATIONS = (
    ('KR Mitteleuropa', Rect(0, -115, 77, 77)),
    ('EAW lore sidebar background and button', Rect(-11, -4, 87, 74)),
)
AUDITED_OTHER_LAYOUTS = ('TFR: top-bar entry', 'BUFF UI: politics-tab entry')


def too_close(a, b, gap=GAP):
    return (a.x < b.x + b.width + gap and a.x + a.width + gap > b.x
            and a.y < b.y + b.height + gap and a.y + a.height + gap > b.y)


def reserve_upward(candidate, obstacles, gap=GAP):
    """Monotonically move up until all fixed obstacles have the required gap.

    Every step clears at least one rectangle permanently; at most N steps are
    needed. Recheck the whole set because one shift can encounter another box.
    """
    if gap < 0 or candidate.width <= 0 or candidate.height <= 0:
        raise ValueError('Invalid sidebar dimensions or gap')
    boxes = tuple(obstacles)
    if any(box.width <= 0 or box.height <= 0 for box in boxes):
        raise ValueError('Invalid obstacle dimensions')
    trace = []
    for _ in range(len(boxes) + 1):
        collisions = [box for box in boxes if too_close(candidate, box, gap)]
        if not collisions:
            return candidate, trace
        next_y = min(box.y - candidate.height - gap for box in collisions)
        assert next_y < candidate.y
        trace.append({'from_y': candidate.y, 'to_y': next_y})
        candidate = Rect(candidate.x, next_y, candidate.width, candidate.height)
    raise AssertionError('Upward reservation did not converge')


def placement():
    selected, shifts = reserve_upward(DEFAULT, (rect for _, rect in RESERVATIONS))
    return {
        'method': 'build_time_static_reservation_for_audited_layouts',
        'runtime_collision_detection': False,
        'requires_custom_launcher': False,
        'excluded_families': ['TNO and its submods'],
        'parent': 'raid_filter', 'gap': GAP,
        'default': asdict(DEFAULT), 'position': asdict(selected), 'shifts': shifts,
        'reservations': [{'name': name, **asdict(rect)} for name, rect in RESERVATIONS],
        'other_audited_layouts': list(AUDITED_OTHER_LAYOUTS),
        'icon': {'native_frame': [55, 41], 'position': [11, 18],
                 'button_position': [3, 3], 'button_size': [71, 71]},
        'limits': ['Audited installed layouts only; future layout changes need re-audit.',
                   'Unknown dynamically positioned controls and transient popups are not detected.',
                   'No generic screen-bounds guarantee at arbitrary GUI scales.'],
    }
