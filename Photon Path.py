"""
PHOTON PATH - A Laser Reflection Puzzle
=========================================
A Computer Graphics mini-project demonstrating 8 classic algorithms
inside one real, playable Pygame game.

CONTROLS
    UP / DOWN arrow   -> rotate the laser emitter
    SPACE (hold)      -> switch to WIDE BEAM / spotlight mode
                         (demonstrates Sutherland-Hodgman polygon clipping)
    B                 -> toggle laser rendering between DDA and Bresenham
    R                 -> reset the puzzle (clears the flood-fill glow)
    ESC / close window -> quit

OBJECTIVE
    Rotate the emitter so the laser bounces off the mirrors and reaches
    the golden target circle. When it does, a flood-fill "glow" spreads
    through the room.

ALGORITHM MAP (search these function names, one per requirement)
    1. dda_line                 -> draws every laser segment (default mode)
    2. bresenham_line           -> draws walls/mirror outlines, and the
                                    laser itself when 'B' is toggled on
    3. cohen_sutherland_clip    -> clips each raw laser ray to the screen
                                    rectangle before it is drawn
    4. liang_barsky_clip        -> quick-rejects a mirror using its
                                    bounding box before doing exact
                                    reflection math (real perf optimisation)
    5. polygon_clip_line        -> (general/Cyrus-Beck polygon clipping)
                                    clips the laser segment against the
                                    convex GLASS block so only the portion
                                    inside the glass is drawn "refracted"
    6. scanline_fill            -> fills mirrors, the glass block and the
                                    target circle (as a polygon) with color
    7. flood_fill               -> spreads the victory "glow" outward from
                                    the target once the puzzle is solved
    8. sutherland_hodgman_clip  -> clips the wide-beam spotlight polygon
                                    against the hexagonal arena boundary
"""

import sys
import math
from collections import deque

import pygame

# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60

BG_COLOR       = (12, 14, 20)
WALL_COLOR     = (150, 150, 160)
MIRROR_COLOR   = (90, 160, 230)
GLASS_COLOR    = (120, 220, 200)
TARGET_COLOR   = (240, 180, 40)
BEAM_COLOR     = (255, 80, 60)
BEAM_GLASS_COL = (255, 210, 120)
GLOW_COLOR     = (255, 235, 150)
CONE_COLOR     = (255, 230, 120)
ARENA_COLOR    = (60, 65, 80)

MAX_BOUNCES = 6
RAY_LENGTH  = 2000     # a "long enough" raw ray length before clipping


# ==========================================================================
# 1. DDA LINE DRAWING ALGORITHM
# ==========================================================================
def dda_line(x1, y1, x2, y2):
    """Return list of integer pixel points from (x1,y1) to (x2,y2) using DDA."""
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        return [(round(x1), round(y1))]
    x_inc = dx / steps
    y_inc = dy / steps
    points = []
    x, y = x1, y1
    for _ in range(steps + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    return points


# ==========================================================================
# 2. BRESENHAM'S LINE DRAWING ALGORITHM
# ==========================================================================
def bresenham_line(x1, y1, x2, y2):
    """Return list of integer pixel points from (x1,y1) to (x2,y2) using Bresenham."""
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    err = dx - dy
    x, y = x1, y1
    while True:
        points.append((x, y))
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return points


def draw_points(surface, points, color, width_px=1):
    """Blit a list of (x,y) pixel points onto a surface (with optional thickness)."""
    for (x, y) in points:
        if width_px <= 1:
            if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
                surface.set_at((x, y), color)
        else:
            pygame.draw.circle(surface, color, (x, y), width_px // 2)


# ==========================================================================
# 3. COHEN-SUTHERLAND LINE CLIPPING ALGORITHM
# ==========================================================================
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def _cs_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= TOP
    elif y > ymax:
        code |= BOTTOM
    return code


def cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    """Clip segment (x1,y1)-(x2,y2) to the rectangle. Returns clipped
    (x1,y1,x2,y2) tuple, or None if the segment is fully outside."""
    code1 = _cs_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = _cs_code(x2, y2, xmin, ymin, xmax, ymax)

    while True:
        if code1 == 0 and code2 == 0:                 # both inside -> accept
            return (x1, y1, x2, y2)
        if code1 & code2 != 0:                         # share an outside zone -> reject
            return None

        code_out = code1 if code1 != 0 else code2
        if code_out & BOTTOM:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y = ymax
        elif code_out & TOP:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y = ymin
        elif code_out & RIGHT:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x = xmax
        else:  # LEFT
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x = xmin

        if code_out == code1:
            x1, y1 = x, y
            code1 = _cs_code(x1, y1, xmin, ymin, xmax, ymax)
        else:
            x2, y2 = x, y
            code2 = _cs_code(x2, y2, xmin, ymin, xmax, ymax)


# ==========================================================================
# 4. LIANG-BARSKY LINE CLIPPING ALGORITHM
# ==========================================================================
def liang_barsky_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    """Clip segment to rectangle using the parametric Liang-Barsky test.
    Used as a cheap 'can this ray possibly hit this mirror's bounding
    box' rejection test before exact reflection maths."""
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    u1, u2 = 0.0, 1.0

    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None            # parallel and outside -> reject
        else:
            t = qi / pi
            if pi < 0:
                u1 = max(u1, t)
            else:
                u2 = min(u2, t)

    if u1 > u2:
        return None
    nx1, ny1 = x1 + u1 * dx, y1 + u1 * dy
    nx2, ny2 = x1 + u2 * dx, y1 + u2 * dy
    return (nx1, ny1, nx2, ny2)


# ==========================================================================
# 5. (GENERAL) POLYGON CLIPPING - Cyrus-Beck clip of a LINE against a
#    convex polygon.  Used to find the portion of the laser that passes
#    through the glass block, so it can be drawn as "refracted light".
# ==========================================================================
def polygon_clip_line(x1, y1, x2, y2, polygon):
    """Clip segment (x1,y1)-(x2,y2) against a convex polygon (vertices
    given clockwise in screen/y-down coordinates). Returns the clipped
    (x1,y1,x2,y2) tuple, or None if there is no overlap."""
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    n = len(polygon)

    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        normal = (edge[1], -edge[0])           # outward normal (clockwise, y-down)
        w = (x1 - p1[0], y1 - p1[1])
        num = -(normal[0] * w[0] + normal[1] * w[1])
        den = normal[0] * dx + normal[1] * dy

        if den == 0:
            if num < 0:
                return None                     # parallel & outside this edge
            continue

        t = num / den
        if den < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)

    if t0 > t1:
        return None
    return (x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy)


# ==========================================================================
# 6. SCAN-LINE POLYGON FILLING ALGORITHM
# ==========================================================================
def scanline_fill(surface, polygon, color):
    """Classic scan-line polygon fill using an edge table / active edge list."""
    ys = [p[1] for p in polygon]
    y_min, y_max = int(math.floor(min(ys))), int(math.ceil(max(ys)))
    n = len(polygon)

    for y in range(y_min, y_max + 1):
        x_intersections = []
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            if y1 == y2:
                continue                        # skip horizontal edges
            if min(y1, y2) <= y < max(y1, y2):
                t = (y - y1) / (y2 - y1)
                x = x1 + t * (x2 - x1)
                x_intersections.append(x)
        x_intersections.sort()
        for i in range(0, len(x_intersections) - 1, 2):
            x_start = int(round(x_intersections[i]))
            x_end = int(round(x_intersections[i + 1]))
            for x in range(x_start, x_end + 1):
                if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
                    surface.set_at((x, y), color)


def circle_polygon(cx, cy, r, sides=24):
    """Approximate a circle as a polygon so it can go through scanline_fill."""
    return [
        (cx + r * math.cos(2 * math.pi * i / sides),
         cy + r * math.sin(2 * math.pi * i / sides))
        for i in range(sides)
    ]


# ==========================================================================
# 7. FLOOD FILL ALGORITHM
# ==========================================================================
def flood_fill_step(surface, frontier, visited, boundary_color, fill_color, budget):
    """Process up to `budget` pixels of a queue-based (BFS) flood fill per
    call, so the glow visibly spreads across several frames instead of
    filling instantly."""
    w, h = surface.get_width(), surface.get_height()
    processed = 0
    while frontier and processed < budget:
        x, y = frontier.popleft()
        if not (0 <= x < w and 0 <= y < h):
            continue
        if (x, y) in visited:
            continue
        visited.add((x, y))
        current = surface.get_at((x, y))[:3]
        if current == boundary_color:
            continue
        surface.set_at((x, y), fill_color)
        processed += 1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in visited:
                frontier.append((nx, ny))
    return len(frontier) > 0


# ==========================================================================
# 8. SUTHERLAND-HODGMAN POLYGON CLIPPING ALGORITHM
# ==========================================================================
def sutherland_hodgman_clip(subject_polygon, clip_polygon):
    """Clip `subject_polygon` against a CONVEX `clip_polygon`
    (vertices clockwise, y-down). Returns the resulting polygon
    (list of points), possibly empty."""

    def inside(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

    def intersect(p1, p2, a, b):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = a
        x4, y4 = b
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return p2
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    output = list(subject_polygon)
    cn = len(clip_polygon)

    for i in range(cn):
        if not output:
            break
        a, b = clip_polygon[i], clip_polygon[(i + 1) % cn]
        input_list = output
        output = []
        n = len(input_list)
        for j in range(n):
            cur = input_list[j]
            prev = input_list[j - 1]
            cur_in = inside(cur, a, b)
            prev_in = inside(prev, a, b)
            if cur_in:
                if not prev_in:
                    output.append(intersect(prev, cur, a, b))
                output.append(cur)
            elif prev_in:
                output.append(intersect(prev, cur, a, b))
    return output


# ==========================================================================
# GEOMETRY HELPERS (not one of the 8, just plumbing)
# ==========================================================================
def segment_intersection(p1, p2, p3, p4):
    """Return intersection point of segment p1-p2 and segment p3-p4, or None."""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def reflect(dx, dy, mx1, my1, mx2, my2):
    """Reflect direction (dx,dy) off the mirror line (mx1,my1)-(mx2,my2)."""
    mdx, mdy = mx2 - mx1, my2 - my1
    length = math.hypot(mdx, mdy)
    nx, ny = -mdy / length, mdx / length          # unit normal
    dot = dx * nx + dy * ny
    rx = dx - 2 * dot * nx
    ry = dy - 2 * dot * ny
    return rx, ry


def bbox_of(p1, p2):
    return (min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1]))


# ==========================================================================
# LEVEL DATA
# ==========================================================================
EMITTER_POS = (60, HEIGHT // 2)

WALLS = [
    ((0, 0), (WIDTH, 0)),
    ((WIDTH, 0), (WIDTH, HEIGHT)),
    ((WIDTH, HEIGHT), (0, HEIGHT)),
    ((0, HEIGHT), (0, 0)),
    ((300, 0), (300, 220)),
    ((300, 420), (300, HEIGHT)),
    ((600, 150), (600, 500)),
]

MIRRORS = [
    ((520, 80), (620, 130)),
    ((250, 480), (350, 430)),
    ((700, 250), (760, 340)),
]

GLASS_RECT = [(360, 260), (470, 260), (470, 340), (360, 340)]   # clockwise TL,TR,BR,BL

TARGET_POS = (820, 450)
TARGET_RADIUS = 18

# Convex hexagonal arena used only for the Sutherland-Hodgman spotlight clip
ARENA_POLY = [
    (150, 40), (750, 40), (860, 300),
    (750, 560), (150, 560), (40, 300),
]


# ==========================================================================
# BEAM SIMULATION
# ==========================================================================
def simulate_beam(origin, angle_rad, mirrors, walls, glass_poly):
    """Cast the laser from `origin` at `angle_rad`, bouncing off mirrors,
    stopping at walls, and reports whether it reached the target.
    Returns: list of dicts describing each visible segment, and a bool
    hit_target."""
    segments = []
    x, y = origin
    dx, dy = math.cos(angle_rad), math.sin(angle_rad)
    hit_target = False

    for _ in range(MAX_BOUNCES):
        raw_end = (x + dx * RAY_LENGTH, y + dy * RAY_LENGTH)

        # -- find the closest thing the raw ray hits: a wall, a mirror,
        #    or the target --
        closest_t = None
        closest_point = raw_end
        hit_kind = None
        hit_mirror = None

        for (w1, w2) in walls:
            pt = segment_intersection((x, y), raw_end, w1, w2)
            if pt:
                t = math.hypot(pt[0] - x, pt[1] - y)
                if closest_t is None or t < closest_t:
                    closest_t, closest_point, hit_kind, hit_mirror = t, pt, "wall", None

        for (m1, m2) in mirrors:
            # ---- ALGORITHM 4 in action: quick bounding-box rejection ----
            mbb = bbox_of(m1, m2)
            clipped = liang_barsky_clip(x, y, raw_end[0], raw_end[1], *mbb)
            if clipped is None:
                continue   # ray cannot possibly reach this mirror -> skip exact test
            pt = segment_intersection((x, y), raw_end, m1, m2)
            if pt:
                t = math.hypot(pt[0] - x, pt[1] - y)
                if closest_t is None or t < closest_t:
                    closest_t, closest_point, hit_kind, hit_mirror = t, pt, "mirror", (m1, m2)

        # target check (small circle treated as a point-radius test along the ray)
        tx, ty = TARGET_POS
        # project target onto ray direction
        proj = (tx - x) * dx + (ty - y) * dy
        if proj > 0:
            px, py = x + dx * proj, y + dy * proj
            if math.hypot(px - tx, py - ty) <= TARGET_RADIUS:
                if closest_t is None or proj < closest_t:
                    closest_t, closest_point, hit_kind, hit_mirror = proj, (px, py), "target", None

        end_point = closest_point

        # ---- ALGORITHM 5 in action: clip this segment against the glass ----
        glass_seg = polygon_clip_line(x, y, end_point[0], end_point[1], glass_poly)

        segments.append({
            "start": (x, y),
            "end": end_point,
            "glass": glass_seg,     # sub-segment inside the glass block (or None)
        })

        if hit_kind in (None, "wall", "target"):
            hit_target = (hit_kind == "target")
            break

        # bounce off the mirror and continue the loop
        x, y = end_point
        dx, dy = reflect(dx, dy, hit_mirror[0][0], hit_mirror[0][1],
                          hit_mirror[1][0], hit_mirror[1][1])

    return segments, hit_target


# ==========================================================================
# RENDERING
# ==========================================================================
def draw_level(surface, use_dda):
    surface.fill(BG_COLOR)

    # arena boundary (context only) drawn with Bresenham
    n = len(ARENA_POLY)
    for i in range(n):
        pts = bresenham_line(*ARENA_POLY[i], *ARENA_POLY[(i + 1) % n])
        draw_points(surface, pts, ARENA_COLOR)

    # walls -> ALGORITHM 2 (Bresenham)
    for (w1, w2) in WALLS:
        pts = bresenham_line(w1[0], w1[1], w2[0], w2[1])
        draw_points(surface, pts, WALL_COLOR, width_px=3)

    # mirrors -> outline Bresenham, fill via scan-line as a thin polygon
    for (m1, m2) in MIRRORS:
        mdx, mdy = m2[0] - m1[0], m2[1] - m1[1]
        length = math.hypot(mdx, mdy)
        nx, ny = -mdy / length * 4, mdx / length * 4
        quad = [(m1[0] + nx, m1[1] + ny), (m2[0] + nx, m2[1] + ny),
                (m2[0] - nx, m2[1] - ny), (m1[0] - nx, m1[1] - ny)]
        scanline_fill(surface, quad, MIRROR_COLOR)          # ALGORITHM 6
        pts = bresenham_line(m1[0], m1[1], m2[0], m2[1])
        draw_points(surface, pts, (220, 240, 255))

    # glass block -> filled via scan-line
    scanline_fill(surface, GLASS_RECT, GLASS_COLOR)          # ALGORITHM 6
    n = len(GLASS_RECT)
    for i in range(n):
        pts = bresenham_line(*GLASS_RECT[i], *GLASS_RECT[(i + 1) % n])
        draw_points(surface, pts, (200, 255, 240))

    # target -> filled via scan-line (as a polygon approximation of a circle)
    scanline_fill(surface, circle_polygon(*TARGET_POS, TARGET_RADIUS), TARGET_COLOR)

    # emitter marker
    pygame.draw.circle(surface, (255, 255, 255), EMITTER_POS, 6)


def draw_beam(surface, segments, use_dda, screen_rect):
    xmin, ymin, xmax, ymax = screen_rect
    for seg in segments:
        x1, y1 = seg["start"]
        x2, y2 = seg["end"]

        # ---- ALGORITHM 3 in action: clip against the screen rectangle ----
        clipped = cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
        if clipped is None:
            continue
        cx1, cy1, cx2, cy2 = clipped

        line_fn = dda_line if use_dda else bresenham_line
        draw_points(surface, line_fn(cx1, cy1, cx2, cy2), BEAM_COLOR, width_px=3)

        if seg["glass"]:
            gx1, gy1, gx2, gy2 = seg["glass"]
            draw_points(surface, line_fn(gx1, gy1, gx2, gy2), BEAM_GLASS_COL, width_px=5)


def draw_spotlight(surface, origin, angle_rad, half_angle=0.35, length=1200):
    """Wide-beam mode: build a triangular cone and clip it against the
    hexagonal arena boundary using Sutherland-Hodgman (ALGORITHM 8),
    then fill the resulting polygon with scan-line fill (ALGORITHM 6)."""
    ox, oy = origin
    a1 = angle_rad - half_angle
    a2 = angle_rad + half_angle
    cone = [
        (ox, oy),
        (ox + length * math.cos(a1), oy + length * math.sin(a1)),
        (ox + length * math.cos(a2), oy + length * math.sin(a2)),
    ]
    clipped = sutherland_hodgman_clip(cone, ARENA_POLY)
    if len(clipped) >= 3:
        glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        scanline_fill(glow, clipped, (*CONE_COLOR, 70))
        surface.blit(glow, (0, 0))


# ==========================================================================
# MAIN GAME LOOP
# ==========================================================================
def main(test_frames=None):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Photon Path")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    angle = 0.0
    use_dda = True
    solved = False
    flood_frontier = deque()
    flood_visited = set()
    glow_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    frame_count = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_b:
                    use_dda = not use_dda
                elif event.key == pygame.K_r:
                    solved = False
                    flood_frontier.clear()
                    flood_visited.clear()
                    glow_layer.fill((0, 0, 0, 0))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            angle -= 0.02
        if keys[pygame.K_DOWN]:
            angle += 0.02
        wide_mode = keys[pygame.K_SPACE]

        segments, hit_target = simulate_beam(EMITTER_POS, angle, MIRRORS, WALLS, GLASS_RECT)

        if hit_target and not solved:
            solved = True
            flood_visited.clear()
            flood_frontier = deque([(int(TARGET_POS[0]), int(TARGET_POS[1]))])

        # ---- ALGORITHM 7 in action: grow the glow a little each frame ----
        if solved and flood_frontier:
            flood_fill_step(glow_layer, flood_frontier, flood_visited,
                             boundary_color=(0, 0, 0, 0) if False else WALL_COLOR,
                             fill_color=(*GLOW_COLOR, 90), budget=250)

        draw_level(screen, use_dda)
        if wide_mode:
            draw_spotlight(screen, EMITTER_POS, angle)
        else:
            draw_beam(screen, segments, use_dda, (0, 0, WIDTH - 1, HEIGHT - 1))

        if solved:
            screen.blit(glow_layer, (0, 0))

        hud_lines = [
            f"Line algo: {'DDA' if use_dda else 'Bresenham'}  (press B to toggle)",
            "Hold SPACE for wide-beam spotlight (Sutherland-Hodgman)",
            "UP/DOWN: rotate    R: reset",
            "SOLVED! Glow is flood-filling the room." if solved else "Aim for the golden target.",
        ]
        for i, line in enumerate(hud_lines):
            surf = font.render(line, True, (230, 230, 230))
            screen.blit(surf, (10, 10 + i * 20))

        pygame.display.flip()
        clock.tick(FPS)

        frame_count += 1
        if test_frames is not None and frame_count >= test_frames:
            running = False

    pygame.quit()


if __name__ == "__main__":
    if "--test" in sys.argv:
        main(test_frames=120)
        print("SELF-TEST OK: ran 120 frames without error.")
    else:
        main()