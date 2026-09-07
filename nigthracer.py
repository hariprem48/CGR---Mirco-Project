import sys
import math
from collections import deque

import pygame

# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60

WORLD_W, WORLD_H = 2000, 1500
TRACK_CENTER = (WORLD_W // 2, WORLD_H // 2)
OUTER_RX, OUTER_RY = 800, 550
INNER_RX, INNER_RY = 480, 280
TRACK_SIDES = 20

BG_COLOR      = (5, 6, 10)
WALL_COLOR    = (170, 170, 180)
ASPHALT_COLOR = (40, 42, 48)
GRASS_COLOR   = (18, 40, 20)
BARRIER_COLOR = (210, 90, 60)
CHECK_COLOR   = (240, 220, 60)
RAY_COLOR     = (255, 235, 150)
CONE_FILL     = (255, 225, 130)
CAR_COLOR     = (230, 230, 240)
MASK_TRACK    = (255, 255, 255, 255)

MASK_CELL = 8          # grid resolution for the track/grass classification
NUM_RAYS = 11
CONE_HALF_ANGLE = 0.42
RAY_LENGTH = 340


# ==========================================================================
# 1. DDA LINE DRAWING ALGORITHM
# ==========================================================================
def dda_line(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        return [(round(x1), round(y1))]
    x_inc, y_inc = dx / steps, dy / steps
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
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
    points = []
    dx, dy = abs(x2 - x1), abs(y2 - y1)
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
    code1 = _cs_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = _cs_code(x2, y2, xmin, ymin, xmax, ymax)
    while True:
        if code1 == 0 and code2 == 0:
            return (x1, y1, x2, y2)
        if code1 & code2 != 0:
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
        else:
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
    dx, dy = x2 - x1, y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
        else:
            t = qi / pi
            if pi < 0:
                u1 = max(u1, t)
            else:
                u2 = min(u2, t)
    if u1 > u2:
        return None
    return (x1 + u1 * dx, y1 + u1 * dy, x1 + u2 * dx, y1 + u2 * dy)


# ==========================================================================
# 5. (GENERAL) POLYGON CLIPPING - Cyrus-Beck clip of a line against a
#    convex polygon. Used to stop a headlight ray at the barrier obstacle.
# ==========================================================================
def polygon_clip_line(x1, y1, x2, y2, polygon):
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    n = len(polygon)
    for i in range(n):
        p1, p2 = polygon[i], polygon[(i + 1) % n]
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        normal = (edge[1], -edge[0])
        w = (x1 - p1[0], y1 - p1[1])
        num = -(normal[0] * w[0] + normal[1] * w[1])
        den = normal[0] * dx + normal[1] * dy
        if den == 0:
            if num < 0:
                return None
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
    ys = [p[1] for p in polygon]
    y_min, y_max = int(math.floor(min(ys))), int(math.ceil(max(ys)))
    y_min = max(y_min, 0)
    y_max = min(y_max, surface.get_height() - 1)
    n = len(polygon)
    for y in range(y_min, y_max + 1):
        xs = []
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            if y1 == y2:
                continue
            if min(y1, y2) <= y < max(y1, y2):
                t = (y - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            x_start = max(int(round(xs[i])), 0)
            x_end = min(int(round(xs[i + 1])), surface.get_width() - 1)
            for x in range(x_start, x_end + 1):
                surface.set_at((x, y), color)


def ellipse_polygon(cx, cy, rx, ry, sides):
    """Points ordered so the loop appears clockwise on a y-down screen."""
    return [
        (cx + rx * math.cos(2 * math.pi * i / sides),
         cy + ry * math.sin(2 * math.pi * i / sides))
        for i in range(sides)
    ]


# ==========================================================================
# 7. FLOOD FILL ALGORITHM
# ==========================================================================
def flood_fill_full(surface, seed, boundary_color, fill_color):
    """Run a queue-based flood fill to completion (used once, at load
    time, to classify the whole track interior)."""
    w, h = surface.get_width(), surface.get_height()
    visited = [[False] * w for _ in range(h)]
    q = deque([seed])
    sx, sy = seed
    if not (0 <= sx < w and 0 <= sy < h):
        return
    while q:
        x, y = q.popleft()
        if not (0 <= x < w and 0 <= y < h) or visited[y][x]:
            continue
        visited[y][x] = True
        if surface.get_at((x, y))[:3] == boundary_color:
            continue
        surface.set_at((x, y), fill_color)
        q.append((x + 1, y))
        q.append((x - 1, y))
        q.append((x, y + 1))
        q.append((x, y - 1))


def flood_fill_step(surface, frontier, visited, boundary_color, fill_color, budget):
    """Budgeted, per-frame flood fill used to grow the minimap's
    'discovered road' fog."""
    w, h = surface.get_width(), surface.get_height()
    processed = 0
    while frontier and processed < budget:
        x, y = frontier.popleft()
        if not (0 <= x < w and 0 <= y < h) or (x, y) in visited:
            continue
        visited.add((x, y))
        if surface.get_at((x, y))[:3] == boundary_color:
            continue
        surface.set_at((x, y), fill_color)
        processed += 1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in visited:
                frontier.append((nx, ny))


# ==========================================================================
# 8. SUTHERLAND-HODGMAN POLYGON CLIPPING ALGORITHM
# ==========================================================================
def sutherland_hodgman_clip(subject_polygon, clip_polygon):
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


def signed_area(poly):
    s = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return s / 2


def ensure_clockwise(poly):
    """sutherland_hodgman_clip's inside-test assumes the same winding
    used throughout this file; flip the polygon if it came out backwards."""
    return poly if signed_area(poly) >= 0 else list(reversed(poly))


# ==========================================================================
# GEOMETRY HELPERS
# ==========================================================================
def segment_intersection(p1, p2, p3, p4):
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


def bbox_of(p1, p2, pad=0):
    return (min(p1[0], p2[0]) - pad, min(p1[1], p2[1]) - pad,
            max(p1[0], p2[0]) + pad, max(p1[1], p2[1]) + pad)


def poly_edges(poly):
    n = len(poly)
    return [(poly[i], poly[(i + 1) % n]) for i in range(n)]


# ==========================================================================
# LEVEL DATA
# ==========================================================================
OUTER_POLY = ellipse_polygon(*TRACK_CENTER, OUTER_RX, OUTER_RY, TRACK_SIDES)
INNER_POLY = ellipse_polygon(*TRACK_CENTER, INNER_RX, INNER_RY, TRACK_SIDES)
OUTER_EDGES = poly_edges(OUTER_POLY)
INNER_EDGES = poly_edges(INNER_POLY)
ALL_WALL_EDGES = OUTER_EDGES + INNER_EDGES

START_POS = (TRACK_CENTER[0], TRACK_CENTER[1] - (OUTER_RY + INNER_RY) / 2)
START_ANGLE = -math.pi / 2

BARRIER = [                                    # a static roadside obstacle
    (TRACK_CENTER[0] - 40, TRACK_CENTER[1] - (OUTER_RY + INNER_RY) / 2 - 220),
    (TRACK_CENTER[0] + 40, TRACK_CENTER[1] - (OUTER_RY + INNER_RY) / 2 - 220),
    (TRACK_CENTER[0] + 40, TRACK_CENTER[1] - (OUTER_RY + INNER_RY) / 2 - 160),
    (TRACK_CENTER[0] - 40, TRACK_CENTER[1] - (OUTER_RY + INNER_RY) / 2 - 160),
]

MID_R = (OUTER_RX + INNER_RX) / 2, (OUTER_RY + INNER_RY) / 2


def _mid_point(angle_deg):
    a = math.radians(angle_deg)
    return (TRACK_CENTER[0] + MID_R[0] * math.cos(a),
            TRACK_CENTER[1] + MID_R[1] * math.sin(a))


def _checkpoint_at(angle_deg):
    a = math.radians(angle_deg)
    outer_pt = (TRACK_CENTER[0] + OUTER_RX * math.cos(a), TRACK_CENTER[1] + OUTER_RY * math.sin(a))
    inner_pt = (TRACK_CENTER[0] + INNER_RX * math.cos(a), TRACK_CENTER[1] + INNER_RY * math.sin(a))
    return (outer_pt, inner_pt)


CHECKPOINTS = [_checkpoint_at(90), _checkpoint_at(210), _checkpoint_at(330)]


# ==========================================================================
# TRACK / GRASS MASK  (built once with FLOOD FILL - algorithm 7a)
# ==========================================================================
def build_track_mask():
    mw, mh = WORLD_W // MASK_CELL, WORLD_H // MASK_CELL
    mask = pygame.Surface((mw, mh))
    mask.fill((0, 0, 0))
    boundary = (255, 0, 0)

    def scaled(poly):
        return [(x / MASK_CELL, y / MASK_CELL) for (x, y) in poly]

    outer_s, inner_s = scaled(OUTER_POLY), scaled(INNER_POLY)
    for i in range(len(outer_s)):
        draw_points(mask, bresenham_line(*outer_s[i], *outer_s[(i + 1) % len(outer_s)]), boundary)
    for i in range(len(inner_s)):
        draw_points(mask, bresenham_line(*inner_s[i], *inner_s[(i + 1) % len(inner_s)]), boundary)

    seed_world = _mid_point(90)
    seed = (int(seed_world[0] / MASK_CELL), int(seed_world[1] / MASK_CELL))
    flood_fill_full(mask, seed, boundary, MASK_TRACK[:3])
    return mask


def is_on_track(mask, wx, wy):
    mx, my = int(wx / MASK_CELL), int(wy / MASK_CELL)
    if not (0 <= mx < mask.get_width() and 0 <= my < mask.get_height()):
        return False
    return mask.get_at((mx, my))[:3] == MASK_TRACK[:3]


# ==========================================================================
# CAR
# ==========================================================================
class Car:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.y = START_POS
        self.angle = START_ANGLE
        self.speed = 0.0
        self.checkpoints_hit = set()
        self.laps = 0

    def update(self, keys, on_track):
        accel = 220.0 if on_track else 90.0
        max_speed = 260.0 if on_track else 90.0
        turn_rate = 2.4

        if keys[pygame.K_UP]:
            self.speed += accel * DT
        if keys[pygame.K_DOWN]:
            self.speed -= accel * 1.4 * DT
        self.speed *= 0.98 if on_track else 0.90
        self.speed = max(-max_speed * 0.5, min(max_speed, self.speed))

        steer = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
        if abs(self.speed) > 5:
            self.angle += steer * turn_rate * DT * (self.speed / max_speed)

        prev = (self.x, self.y)
        self.x += math.cos(self.angle) * self.speed * DT
        self.y += math.sin(self.angle) * self.speed * DT

        for i, (a, b) in enumerate(CHECKPOINTS):
            if segment_intersection(prev, (self.x, self.y), a, b):
                self.checkpoints_hit.add(i)
        if len(self.checkpoints_hit) == len(CHECKPOINTS):
            self.laps += 1
            self.checkpoints_hit.clear()


DT = 1.0 / FPS


# ==========================================================================
# HEADLIGHT CONE  (rays 1/2/3/5, cone assembly, then clipped by 8)
# ==========================================================================
def nearest_edge(pos, edges):
    best, best_d = None, None
    px, py = pos
    for (a, b) in edges:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        d = (mx - px) ** 2 + (my - py) ** 2
        if best_d is None or d < best_d:
            best, best_d = (a, b), d
    return best


def cast_headlight(car, use_dda):
    """Sample NUM_RAYS rays across the cone, stop each at the nearest wall
    or the barrier, and return:
        - ray_world_segments: [(start, end), ...] for drawing
        - cone_polygon: the resulting light polygon (world coords), already
          clipped to the local lane corridor via Sutherland-Hodgman
    """
    origin = (car.x, car.y)
    ray_segments = []
    cone_points = [origin]

    for i in range(NUM_RAYS):
        t = i / (NUM_RAYS - 1)
        a = car.angle - CONE_HALF_ANGLE + t * (2 * CONE_HALF_ANGLE)
        raw_end = (origin[0] + math.cos(a) * RAY_LENGTH, origin[1] + math.sin(a) * RAY_LENGTH)

        closest_t, closest_pt = None, raw_end
        for (w1, w2) in ALL_WALL_EDGES:
            pt = segment_intersection(origin, raw_end, w1, w2)
            if pt:
                d = math.hypot(pt[0] - origin[0], pt[1] - origin[1])
                if closest_t is None or d < closest_t:
                    closest_t, closest_pt = d, pt

        # ---- ALGORITHM 5 in action: stop the ray at the barrier too ----
        barrier_clip = polygon_clip_line(origin[0], origin[1], raw_end[0], raw_end[1], BARRIER)
        if barrier_clip:
            bx1, by1, bx2, by2 = barrier_clip
            d = math.hypot(bx1 - origin[0], by1 - origin[1])
            if closest_t is None or d < closest_t:
                closest_t, closest_pt = d, (bx1, by1)

        ray_segments.append((origin, closest_pt))
        cone_points.append(closest_pt)

    # ---- ALGORITHM 8 in action: clip the raw cone to the local lane ----
    outer_seg = nearest_edge(origin, OUTER_EDGES)
    inner_seg = nearest_edge(origin, INNER_EDGES)
    corridor = ensure_clockwise([outer_seg[0], outer_seg[1], inner_seg[1], inner_seg[0]])
    clipped_cone = sutherland_hodgman_clip(cone_points, corridor)
    if len(clipped_cone) < 3:
        clipped_cone = cone_points

    return ray_segments, clipped_cone


# ==========================================================================
# RENDERING
# ==========================================================================
def world_to_screen(cam, p):
    return (p[0] - cam[0] + WIDTH / 2, p[1] - cam[1] + HEIGHT / 2)


def draw_track(surface, cam):
    outer_screen = [world_to_screen(cam, p) for p in OUTER_POLY]
    inner_screen = [world_to_screen(cam, p) for p in INNER_POLY]
    scanline_fill(surface, outer_screen, ASPHALT_COLOR)   # ALGORITHM 6
    scanline_fill(surface, inner_screen, GRASS_COLOR)      # ALGORITHM 6 (island)

    viewport = (-40, -40, WIDTH + 40, HEIGHT + 40)
    for (w1, w2) in ALL_WALL_EDGES:
        s1, s2 = world_to_screen(cam, w1), world_to_screen(cam, w2)
        # ---- ALGORITHM 4 in action: cheap broad-phase culling ----
        clipped = liang_barsky_clip(s1[0], s1[1], s2[0], s2[1], *viewport)
        if clipped is None:
            continue
        cx1, cy1, cx2, cy2 = clipped
        # ---- ALGORITHM 3 in action: exact clip to the real window ----
        final = cohen_sutherland_clip(cx1, cy1, cx2, cy2, 0, 0, WIDTH - 1, HEIGHT - 1)
        if final is None:
            continue
        draw_points(surface, bresenham_line(*final), WALL_COLOR, width_px=3)

    barrier_screen = [world_to_screen(cam, p) for p in BARRIER]
    scanline_fill(surface, barrier_screen, BARRIER_COLOR)   # ALGORITHM 6
    n = len(barrier_screen)
    for i in range(n):
        draw_points(surface, bresenham_line(*barrier_screen[i], *barrier_screen[(i + 1) % n]),
                    (255, 200, 180))

    for (a, b) in CHECKPOINTS:
        s1, s2 = world_to_screen(cam, a), world_to_screen(cam, b)
        draw_points(surface, bresenham_line(*s1, *s2), CHECK_COLOR, width_px=2)


def draw_headlight(surface, cam, ray_segments, cone_polygon, use_dda):
    line_fn = dda_line if use_dda else bresenham_line
    for (a, b) in ray_segments:
        s1, s2 = world_to_screen(cam, a), world_to_screen(cam, b)
        clipped = cohen_sutherland_clip(s1[0], s1[1], s2[0], s2[1], 0, 0, WIDTH - 1, HEIGHT - 1)
        if clipped:
            draw_points(surface, line_fn(*clipped), RAY_COLOR, width_px=1)

    cone_screen = [world_to_screen(cam, p) for p in cone_polygon]
    glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    scanline_fill(glow, cone_screen, (*CONE_FILL, 55))     # ALGORITHM 6
    surface.blit(glow, (0, 0))


def draw_car(surface, cam, car):
    p = world_to_screen(cam, (car.x, car.y))
    front = world_to_screen(cam, (car.x + math.cos(car.angle) * 14, car.y + math.sin(car.angle) * 14))
    pygame.draw.circle(surface, CAR_COLOR, (int(p[0]), int(p[1])), 7)
    pygame.draw.line(surface, CAR_COLOR, p, front, 3)


def draw_minimap(surface, mask, discovered, car, font):
    mw, mh = 180, 135
    ox, oy = WIDTH - mw - 14, 14
    panel = pygame.Surface((mw, mh))
    scale_x, scale_y = mw / mask.get_width(), mh / mask.get_height()
    small_mask = pygame.transform.smoothscale(mask, (mw, mh))
    panel.blit(small_mask, (0, 0))

    small_fog = pygame.transform.smoothscale(discovered, (mw, mh))
    panel.blit(small_fog, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    cx = int(car.x / MASK_CELL * scale_x)
    cy = int(car.y / MASK_CELL * scale_y)
    pygame.draw.circle(panel, (255, 60, 60), (cx, cy), 3)
    surface.blit(panel, (ox, oy))
    pygame.draw.rect(surface, (200, 200, 200), (ox, oy, mw, mh), 1)


# ==========================================================================
# MAIN GAME LOOP
# ==========================================================================
def main(test_frames=None):
    global DT
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Night Racer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    track_mask = build_track_mask()                        # ALGORITHM 7a (once)
    discovered = pygame.Surface(track_mask.get_size(), pygame.SRCALPHA)
    fog_frontier = deque()
    fog_visited = set()

    car = Car()
    use_dda = True
    show_minimap = True

    frame_count = 0
    running = True
    while running:
        DT = clock.tick(FPS) / 1000.0
        DT = min(DT, 1 / 30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_l:
                    use_dda = not use_dda
                elif event.key == pygame.K_m:
                    show_minimap = not show_minimap
                elif event.key == pygame.K_r:
                    car.reset()

        keys = pygame.key.get_pressed()
        on_track = is_on_track(track_mask, car.x, car.y)
        car.update(keys, on_track)

        # ---- ALGORITHM 7b in action: grow the minimap fog a little each frame ----
        mx, my = int(car.x / MASK_CELL), int(car.y / MASK_CELL)
        if (mx, my) not in fog_visited:
            fog_frontier.append((mx, my))
        flood_fill_step(discovered, fog_frontier, fog_visited,
                         boundary_color=(0, 0, 0), fill_color=(60, 140, 255, 120), budget=120)

        cam = (car.x, car.y)
        ray_segments, cone_polygon = cast_headlight(car, use_dda)

        screen.fill(BG_COLOR)
        draw_track(screen, cam)
        draw_headlight(screen, cam, ray_segments, cone_polygon, use_dda)
        draw_car(screen, cam, car)
        if show_minimap:
            draw_minimap(screen, track_mask, discovered, car, font)

        hud = [
            f"Ray algo: {'DDA' if use_dda else 'Bresenham'}  (L to toggle)   Laps: {car.laps}",
            f"Checkpoints hit this lap: {len(car.checkpoints_hit)}/{len(CHECKPOINTS)}",
            "On tarmac" if on_track else "OFF TRACK - slow!",
            "UP/DOWN drive, LEFT/RIGHT steer, M minimap, R reset",
        ]
        for i, line in enumerate(hud):
            surf = font.render(line, True, (230, 230, 230))
            screen.blit(surf, (10, 10 + i * 20))

        pygame.display.flip()

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
