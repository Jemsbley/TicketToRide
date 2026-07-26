
from __future__ import annotations
# TODO implement full view, probably use claude to generate this so I don't need to worry about visuals
"""
view should show to a specific player:
- their hand
- their tickets, outlined red if incomplete and green if complete
- their remaining trains, separated
- all other players remaining trains
- their score, separated
- all other players scores
- if the game is going around for its last turn
- the turn number
- the revealed cards at the top
- the number of remaining cards in the deck
- the number of remaining cards in the tickets pile
- all cities labeled
- all routes on the board, with their respective colors.
  - a claimed route will be outlined in the color it originally was and filled in with the color of the player who took
"""

"""
game_view.py — a lightweight pygame renderer for a Ticket to Ride
PlayerPerspectiveGameState. Persistent window, redraw-every-frame, clickable.

Quick start
-----------
    from game_view import GameView

    view = GameView(me=PlayerColor.RED)
    clock_fps = 60
    while not view.closed:
        for click in view.poll():          # pumps events, handles window close
            print(click.kind, click.data)  # <- your move logic would go here
        view.redraw(state)                 # draw the current state
        view.tick(clock_fps)               # cap the frame rate
    view.close()

The window stays live and responsive the whole time because `poll()` pumps the
OS event queue every frame. Two ways to read input:

  * `view.poll()` — non-blocking. Returns a list of Click objects for whatever
    was clicked since last call, and sets `view.closed` if the window's X was
    hit. Use this in a per-frame loop.

  * `view.wait_for_click(timeout=None)` — blocks until the player clicks a drawn
    element, keeping the window painted and responsive meanwhile. Returns the
    Click, or None if the window closed / it timed out. This is the natural
    "wait for a move".

  * `view.on_click(fn)` — also register callbacks; fn(Click) fires on every hit.

Clickable elements report *what* was clicked, never what it means (claiming a
route, drawing a card, etc. is your engine's job):

    Click.kind == "city"          -> {"city": <normalized name>}
    Click.kind == "route"         -> {"route_state", "track_color", "owner"}
    Click.kind == "hand_card"     -> {"card", "count"}
    Click.kind == "ticket"        -> {"ticket", "complete"}
    Click.kind == "revealed_card" -> {"card", "index"}

Assumptions (unchanged from the earlier version)
------------------------------------------------
* `me` (the perspective PlayerColor) isn't on your dataclass; pass it to
  GameView(me=...) or redraw(state, me=...). It separates "you" from others and
  drives ticket-completion checks.
* City coordinates: the standard US map is baked in (CITY_COORDS), matched by
  name (City.NEW_YORK -> "NEW YORK"). Override with GameView(coords={...}).
* Objects are read defensively (no import of your `a`/`e` modules):
    Route:  .color (Card or None), .length (int), endpoints via
            .city1/.city2 | .source/.dest | .start/.end | .a/.b
    Ticket: endpoints (same), points via .points | .value | .point_value
    RouteState.claims: dict[Card, PlayerColor | None] — one entry per parallel
            track; key is the track's colour, value its owner (None = open).
* "Final round" isn't a field, so it's derived: any player at
  <= FINAL_ROUND_TRAIN_THRESHOLD trains lights the banner.
"""


import math
from dataclasses import dataclass, field

import pygame

# --------------------------------------------------------------------------- #
# ADAPT HERE: colours, coordinates, rules                                     #
# --------------------------------------------------------------------------- #

FINAL_ROUND_TRAIN_THRESHOLD = 2


def _hx(s: str):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


CARD_COLORS = {
    "RED": _hx("#d64545"), "ORANGE": _hx("#e8862e"), "YELLOW": _hx("#f2c53d"),
    "GREEN": _hx("#3aa655"), "BLUE": _hx("#2b6cb0"), "PURPLE": _hx("#8e44ad"),
    "BLACK": _hx("#2b2b2b"), "WHITE": _hx("#f4f4f4"), "WILD": _hx("#9aa0a6"),
}
GRAY = _hx("#9aa0a6")

PLAYER_COLORS = {
    "GREEN": _hx("#2e7d32"), "BLUE": _hx("#1565c0"), "YELLOW": _hx("#f9a825"),
    "BLACK": _hx("#212121"), "RED": _hx("#c62828"),
}

# Theme
BG          = _hx("#efe9dc")
MAP_BG      = _hx("#dcecd6")
PANEL_BG    = _hx("#faf6ec")
PANEL_EDGE  = _hx("#c9bfa6")
RULE_COL    = _hx("#d8ccae")
CITY_FILL   = _hx("#fffaf0")
INK         = _hx("#222222")
INK_SOFT    = _hx("#555555")
GOOD        = _hx("#2e7d32")
BAD         = _hx("#c62828")

# Standard Ticket to Ride USA board. x grows east, y grows north.
CITY_COORDS = {
    "VANCOUVER": (0.6, 8.6), "CALGARY": (2.1, 8.9), "WINNIPEG": (4.9, 8.9),
    "SAULT STE MARIE": (7.5, 8.1), "MONTREAL": (10.3, 8.5), "SEATTLE": (0.5, 7.8),
    "HELENA": (3.2, 7.2), "DULUTH": (5.7, 7.3), "TORONTO": (8.9, 7.6),
    "BOSTON": (11.5, 7.5), "PORTLAND": (0.3, 6.9), "OMAHA": (5.2, 5.9),
    "CHICAGO": (6.7, 6.3), "PITTSBURGH": (8.5, 6.3), "NEW YORK": (10.5, 6.7),
    "SALT LAKE CITY": (2.6, 5.6), "DENVER": (3.9, 5.2), "KANSAS CITY": (5.3, 5.0),
    "SAINT LOUIS": (6.3, 5.0), "WASHINGTON": (9.9, 5.9), "SAN FRANCISCO": (0.4, 4.8),
    "LAS VEGAS": (1.8, 4.4), "NASHVILLE": (7.1, 4.6), "RALEIGH": (9.3, 4.8),
    "LOS ANGELES": (1.0, 3.6), "PHOENIX": (2.3, 3.2), "SANTA FE": (3.5, 3.8),
    "OKLAHOMA CITY": (4.9, 3.8), "LITTLE ROCK": (6.1, 3.8), "ATLANTA": (7.9, 3.8),
    "CHARLESTON": (9.3, 3.6), "EL PASO": (3.3, 2.6), "DALLAS": (5.3, 2.8),
    "HOUSTON": (5.5, 1.8), "NEW ORLEANS": (6.7, 1.8), "MIAMI": (9.7, 1.2),
}

_CARD_ORDER = ["RED", "ORANGE", "YELLOW", "GREEN", "BLUE",
               "PURPLE", "BLACK", "WHITE", "WILD"]

# --------------------------------------------------------------------------- #
# Defensive readers                                                           #
# --------------------------------------------------------------------------- #

def _enum_name(x):
    if x is None:
        return None
    return getattr(x, "name", str(x))


def city_key(city):
    if city is None:
        return None
    name = getattr(city, "name", None) or str(city)
    return name.replace("_", " ").strip().upper()


def city_label(key):
    return " ".join(w.capitalize() for w in key.split())


def card_color(card):
    if card is None:
        return GRAY
    return CARD_COLORS.get(_enum_name(card).upper(), GRAY)


def player_color(pc):
    if pc is None:
        return GRAY
    return PLAYER_COLORS.get(_enum_name(pc).upper(), GRAY)


def _pair(obj):
    for a, b in (("city1", "city2"), ("source", "dest"), ("start", "end"),
                 ("a", "b"), ("u", "v"), ("from_city", "to_city"),
                 ("city_a", "city_b"), ("origin", "destination")):
        if hasattr(obj, a) and hasattr(obj, b):
            return getattr(obj, a), getattr(obj, b)
    try:
        seq = list(obj)
        if len(seq) >= 2:
            return seq[0], seq[1]
    except TypeError:
        pass
    return None, None


def route_length(route):
    for attr in ("length", "len", "num_cars", "cars", "cost"):
        v = getattr(route, attr, None)
        if isinstance(v, int) and v > 0:
            return v
    return 1


def ticket_points(ticket):
    for attr in ("points", "value", "point_value", "score"):
        v = getattr(ticket, attr, None)
        if isinstance(v, int):
            return v
    return 0


def _lighten(rgb, amt):
    return tuple(int(c + (255 - c) * amt) for c in rgb)


def _text_on(rgb):
    lum = (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255
    return INK if lum > 0.6 else (255, 255, 255)


def _point_segment_dist(px, py, p1, p2):
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    seg2 = dx * dx + dy * dy
    if seg2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / seg2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


# --------------------------------------------------------------------------- #
# Ticket completion (union-find)                                             #
# --------------------------------------------------------------------------- #

class _DSU:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


# --------------------------------------------------------------------------- #
# Click result                                                                #
# --------------------------------------------------------------------------- #

@dataclass
class Click:
    kind: str
    data: dict = field(default_factory=dict)
    pos: tuple = (0, 0)          # pixel position of the click


# --------------------------------------------------------------------------- #
# The view                                                                    #
# --------------------------------------------------------------------------- #

class GameView:
    def __init__(self, me=None, coords=None, size=(1360, 820),
                 title="Ticket to Ride", fps=60):
        self.me = me
        self.coords = dict(CITY_COORDS)
        if coords:
            for k, v in coords.items():
                self.coords[k.replace("_", " ").strip().upper()] = v

        pygame.init()
        pygame.display.set_caption(title)
        self.w, self.h = size
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.fps = fps

        self.f_big = self._font(24, bold=True)
        self.f_hdr = self._font(17, bold=True)
        self.f_med = self._font(15)
        self.f_small = self._font(13)
        self.f_tiny = self._font(12)
        self.f_mono = self._font(13, mono=True)
        self.f_label = self._font(13, bold=True)

        self._regions = []
        self._click_cbs = []
        self._closed = False
        self._last_state = None
        self._layout()

    # -- setup helpers ---------------------------------------------------- #

    @staticmethod
    def _font(size, bold=False, mono=False):
        family = "dejavusansmono,consolas,courier" if mono else "dejavusans,arial"
        return pygame.font.SysFont(family, size, bold=bold)

    def _layout(self):
        self.panel_w = max(300, int(self.w * 0.24))
        self.top_h = 66
        self.panel = pygame.Rect(self.w - self.panel_w, 0, self.panel_w, self.h)
        self.map_rect = pygame.Rect(0, self.top_h,
                                    self.w - self.panel_w, self.h - self.top_h)
        self.top_rect = pygame.Rect(0, 0, self.w - self.panel_w, self.top_h)

        xs = [c[0] for c in self.coords.values()]
        ys = [c[1] for c in self.coords.values()]
        self.minx, self.maxx = min(xs), max(xs)
        self.miny, self.maxy = min(ys), max(ys)
        pad = 46
        span_x = (self.maxx - self.minx) or 1
        span_y = (self.maxy - self.miny) or 1
        self.scale = min((self.map_rect.w - 2 * pad) / span_x,
                         (self.map_rect.h - 2 * pad) / span_y)
        draw_w = span_x * self.scale
        draw_h = span_y * self.scale
        self.ox = self.map_rect.x + (self.map_rect.w - draw_w) / 2
        self.oy = self.map_rect.y + (self.map_rect.h - draw_h) / 2
        self.draw_h = draw_h

    def _w2s(self, wx, wy):
        sx = self.ox + (wx - self.minx) * self.scale
        sy = self.oy + self.draw_h - (wy - self.miny) * self.scale   # flip y
        return (sx, sy)

    # -- public: input / persistence ------------------------------------- #

    def on_click(self, callback):
        self._click_cbs.append(callback)
        return callback

    def remove_click_callback(self, callback):
        if callback in self._click_cbs:
            self._click_cbs.remove(callback)

    def poll(self):
        """Pump the event queue once; return a list of Clicks (may be empty).
        Sets .closed if the window was closed. Non-blocking."""
        clicks = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._closed = True
            elif event.type == pygame.VIDEORESIZE:
                self.w, self.h = event.w, event.h
                self.screen = pygame.display.set_mode((self.w, self.h),
                                                      pygame.RESIZABLE)
                self._layout()
                if self._last_state is not None:
                    self.redraw(self._last_state)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                hit = self._hit_test(event.pos)
                if hit is not None:
                    click = Click(kind=hit["kind"], data=hit["data"],
                                  pos=event.pos)
                    clicks.append(click)
                    for cb in list(self._click_cbs):
                        cb(click)
        return clicks

    def wait_for_click(self, timeout=None):
        """Block until a drawn element is clicked; keep the window live.
        Returns the Click, or None if closed / timed out."""
        start = pygame.time.get_ticks()
        while not self._closed:
            clicks = self.poll()
            if clicks:
                return clicks[0]
            if self._last_state is not None:
                self.redraw(self._last_state)
            self.tick(self.fps)
            if timeout is not None and \
                    (pygame.time.get_ticks() - start) / 1000.0 >= timeout:
                return None
        return None

    def tick(self, fps=None):
        self.clock.tick(fps or self.fps)

    @property
    def closed(self):
        return self._closed

    def close(self):
        self._closed = True
        pygame.quit()

    def screenshot(self, path):
        pygame.image.save(self.screen, path)

    # -- hit testing ------------------------------------------------------ #

    def _hit_test(self, pos):
        x, y = pos
        best_seg, best_d = None, None
        for reg in reversed(self._regions):
            shape = reg["shape"]
            if shape == "circle":
                cx, cy, r = reg["geom"]
                if math.hypot(x - cx, y - cy) <= r:
                    return reg
            elif shape == "rect":
                if reg["geom"].collidepoint(x, y):
                    return reg
            elif shape == "segment":
                p1, p2, tol = reg["geom"]
                d = _point_segment_dist(x, y, p1, p2)
                if d <= tol and (best_d is None or d < best_d):
                    best_seg, best_d = reg, d
        return best_seg

    def _reg_circle(self, x, y, r, kind, **data):
        self._regions.append({"shape": "circle", "geom": (x, y, r),
                              "kind": kind, "data": data})

    def _reg_rect(self, rect, kind, **data):
        self._regions.append({"shape": "rect", "geom": rect,
                              "kind": kind, "data": data})

    def _reg_segment(self, p1, p2, tol, kind, **data):
        self._regions.append({"shape": "segment", "geom": (p1, p2, tol),
                              "kind": kind, "data": data})

    # -- drawing ---------------------------------------------------------- #

    def redraw(self, state, me=None):
        """Draw one full frame from `state` and flip. Safe to call every frame."""
        if me is not None:
            self.me = me
        self._last_state = state
        self._regions = []

        self.screen.fill(BG)
        owned = self._owned_edges(state)
        self._draw_map(state, owned)
        self._draw_top(state)
        self._draw_panel(state, owned)
        pygame.display.flip()

    def _owned_edges(self, state):
        dsu = _DSU()
        for rs in getattr(state, "routes", []) or []:
            claims = getattr(rs, "claims", {}) or {}
            if self.me in claims.values():
                c1, c2 = _pair(getattr(rs, "route", rs))
                k1, k2 = city_key(c1), city_key(c2)
                if k1 and k2:
                    dsu.union(k1, k2)
        return dsu

    def _blit(self, text, pos, font, color, anchor="topleft"):
        img = font.render(str(text), True, color)
        rect = img.get_rect(**{anchor: pos})
        self.screen.blit(img, rect)
        return rect

    # ---- map ----

    def _draw_map(self, state, owned):
        pygame.draw.rect(self.screen, MAP_BG, self.map_rect)
        prev = self.screen.get_clip()
        self.screen.set_clip(self.map_rect)

        # faint ticket guide lines for my tickets
        for t in getattr(state, "my_tickets", []) or []:
            k1, k2 = (city_key(c) for c in _pair(t))
            if k1 in self.coords and k2 in self.coords:
                complete = (k1 in owned.parent and k2 in owned.parent
                            and owned.find(k1) == owned.find(k2))
                self._dashed_line(self._w2s(*self.coords[k1]),
                                  self._w2s(*self.coords[k2]),
                                  GOOD if complete else BAD)

        # routes
        for rs in getattr(state, "routes", []) or []:
            route = getattr(rs, "route", rs)
            k1, k2 = (city_key(c) for c in _pair(route))
            if k1 not in self.coords or k2 not in self.coords:
                continue
            s1 = self._w2s(*self.coords[k1])
            s2 = self._w2s(*self.coords[k2])
            length = route_length(route)
            claims = getattr(rs, "claims", {}) or {}
            tracks = list(claims.items()) or [(getattr(route, "color", None), None)]
            n = len(tracks)
            for i, (track_color, owner) in enumerate(tracks):
                offset = (i - (n - 1) / 2) * (0.16 * self.scale)
                a1, a2 = self._offset_seg(s1, s2, offset)
                self._draw_track(a1, a2, length, card_color(track_color),
                                 player_color(owner) if owner is not None else None)
                self._reg_segment(a1, a2, 0.07 * self.scale + 3, "route",
                                  route_state=rs, track_color=track_color,
                                  owner=owner)

        # cities
        r = max(5, int(0.11 * self.scale))
        for key, (wx, wy) in self.coords.items():
            x, y = self._w2s(wx, wy)
            pygame.draw.circle(self.screen, CITY_FILL, (int(x), int(y)), r)
            pygame.draw.circle(self.screen, INK, (int(x), int(y)), r, 2)
            self._blit(city_label(key), (x, y - r - 2), self.f_label, INK,
                       anchor="midbottom")
            self._reg_circle(x, y, r + 5, "city", city=key)

        self.screen.set_clip(prev)

    @staticmethod
    def _offset_seg(s1, s2, offset):
        (x1, y1), (x2, y2) = s1, s2
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1e-9
        px, py = -dy / d, dx / d
        return ((x1 + px * offset, y1 + py * offset),
                (x2 + px * offset, y2 + py * offset))

    def _draw_track(self, a1, a2, length, orig_color, owner_color):
        (x1, y1), (x2, y2) = a1, a2
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1e-9
        ux, uy = dx / d, dy / d
        px, py = -uy, ux
        half_w = max(3, 0.06 * self.scale)
        seg = d / max(1, length)
        half_len = seg * 0.5 * 0.74
        fill = owner_color if owner_color else _lighten(orig_color, 0.55)
        border = orig_color
        for k in range(max(1, length)):
            t = (k + 0.5) / max(1, length)
            cx, cy = x1 + dx * t, y1 + dy * t
            corners = [
                (cx + ux * half_len + px * half_w, cy + uy * half_len + py * half_w),
                (cx + ux * half_len - px * half_w, cy + uy * half_len - py * half_w),
                (cx - ux * half_len - px * half_w, cy - uy * half_len - py * half_w),
                (cx - ux * half_len + px * half_w, cy - uy * half_len + py * half_w),
            ]
            pygame.draw.polygon(self.screen, fill, corners)
            pygame.draw.polygon(self.screen, border, corners, 2)

    def _dashed_line(self, p1, p2, color, dash=8, gap=7, width=2):
        (x1, y1), (x2, y2) = p1, p2
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1e-9
        ux, uy = dx / d, dy / d
        n = int(d // (dash + gap))
        for k in range(n + 1):
            s = k * (dash + gap)
            e = min(s + dash, d)
            pygame.draw.line(self.screen, color,
                             (x1 + ux * s, y1 + uy * s),
                             (x1 + ux * e, y1 + uy * e), width)

    # ---- top strip: revealed cards ----

    def _draw_top(self, state):
        pygame.draw.rect(self.screen, BG, self.top_rect)
        self._blit("Revealed", (14, self.top_h // 2), self.f_hdr, INK_SOFT,
                   anchor="midleft")
        x = 110
        cw, ch = 46, 40
        for idx, card in enumerate(getattr(state, "revealed_cards", []) or []):
            rect = pygame.Rect(x, (self.top_h - ch) // 2, cw, ch)
            self._chip(rect, card_color(card), label=_short(card))
            self._reg_rect(rect, "revealed_card", card=card, index=idx)
            x += cw + 10

    # ---- side panel ----

    def _draw_panel(self, state, owned):
        pygame.draw.rect(self.screen, PANEL_BG, self.panel)
        pygame.draw.rect(self.screen, PANEL_EDGE, self.panel, 2)
        L = self.panel.x + 14
        R = self.panel.right - 14
        y = 16

        y = self._blit(f"You: {_enum_name(self.me) or '?'}", (L, y),
                       self.f_big, player_color(self.me)).bottom + 6

        turn = getattr(state, "turn_number", "?")
        cur = _enum_name(getattr(state, "player_turn", None)) or "?"
        y = self._blit(f"Turn {turn}   \u00b7   {cur} to move", (L, y),
                       self.f_med, INK).bottom + 8

        trains = getattr(state, "trains_remaining", {}) or {}
        if any(v <= FINAL_ROUND_TRAIN_THRESHOLD for v in trains.values()):
            banner = pygame.Rect(L, y, R - L, 26)
            pygame.draw.rect(self.screen, BAD, banner, border_radius=6)
            self._blit("FINAL ROUND", banner.center, self.f_hdr,
                       (255, 255, 255), anchor="center")
            y = banner.bottom + 8

        lr_owner = getattr(state, "longest_road_owner", None)
        lr_len = getattr(state, "longest_road_length", 0)
        y = self._blit(f"Longest road: {_enum_name(lr_owner) or '\u2014'} ({lr_len})",
                       (L, y), self.f_small, player_color(lr_owner)).bottom + 8
        y = self._rule(L, R, y)

        # players
        y = self._blit("Players", (L, y), self.f_hdr, INK).bottom + 4
        scores = getattr(state, "scores", {}) or {}
        players = list(getattr(state, "players", []) or scores.keys())
        players.sort(key=lambda p: (p != self.me, _enum_name(p) or ""))
        for p in players:
            is_me = (p == self.me)
            row = pygame.Rect(L - 2, y, R - L + 4, 24)
            if is_me:
                pygame.draw.rect(self.screen, _lighten(player_color(p), 0.82),
                                 row, border_radius=5)
            sw = pygame.Rect(L + 2, y + 4, 22, 16)
            self._chip(sw, player_color(p))
            name = (_enum_name(p) or "?") + ("  (you)" if is_me else "")
            self._blit(name, (L + 32, y + 12), self.f_med, INK, anchor="midleft")
            self._blit(f"{scores.get(p, 0):>3} pts  {trains.get(p, 0):>2} tr",
                       (R, y + 12), self.f_mono, INK_SOFT, anchor="midright")
            y = row.bottom + 3
        y = self._rule(L, R, y + 4)

        # hand
        y = self._blit("Your hand", (L, y), self.f_hdr, INK).bottom + 6
        hand = getattr(state, "my_hand", []) or []
        counts, card_by_name = {}, {}
        for c in hand:
            nm = _enum_name(c)
            counts[nm] = counts.get(nm, 0) + 1
            card_by_name.setdefault(nm, c)
        cw, ch, gap = 44, 30, 8
        per_row = max(1, (R - L + gap) // (cw + gap))
        col = 0
        row_y = y
        drew = False
        for nm in _CARD_ORDER:
            if nm not in counts:
                continue
            drew = True
            if col == per_row:
                col = 0
                row_y += ch + gap
            rect = pygame.Rect(L + col * (cw + gap), row_y, cw, ch)
            self._chip(rect, CARD_COLORS.get(nm, GRAY), label=str(counts[nm]))
            self._reg_rect(rect, "hand_card", card=card_by_name[nm],
                           count=counts[nm])
            col += 1
        y = (row_y + ch + 8) if drew else \
            self._blit("(empty)", (L, y), self.f_small, INK_SOFT).bottom + 6
        y = self._rule(L, R, y)

        # tickets
        y = self._blit("Your tickets", (L, y), self.f_hdr, INK).bottom + 6
        for t in getattr(state, "my_tickets", []) or []:
            k1, k2 = (city_key(c) for c in _pair(t))
            complete = (k1 in owned.parent and k2 in owned.parent
                        and owned.find(k1) == owned.find(k2))
            edge = GOOD if complete else BAD
            box = pygame.Rect(L, y, R - L, 26)
            pygame.draw.rect(self.screen, (255, 255, 255), box, border_radius=6)
            pygame.draw.rect(self.screen, edge, box, 2, border_radius=6)
            self._reg_rect(box, "ticket", ticket=t, complete=complete)
            label = f"{city_label(k1 or '?')} \u2192 {city_label(k2 or '?')}"
            self._blit(label, (L + 8, box.centery), self.f_small, INK,
                       anchor="midleft")
            self._blit(ticket_points(t), (R - 8, box.centery), self.f_label,
                       edge, anchor="midright")
            y = box.bottom + 6
        y = self._rule(L, R, y)

        # piles
        deck = getattr(state, "deck_left", "?")
        tix = getattr(state, "tickets_left", "?")
        self._blit(f"Deck: {deck}    Tickets pile: {tix}", (L, y),
                   self.f_med, INK)

    # ---- small drawing helpers ----

    def _rule(self, L, R, y):
        pygame.draw.line(self.screen, RULE_COL, (L, y), (R, y), 1)
        return y + 10

    def _chip(self, rect, color, label=None):
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        pygame.draw.rect(self.screen, INK, rect, 1, border_radius=6)
        if label is not None:
            self._blit(label, rect.center, self.f_label, _text_on(color),
                       anchor="center")


def _short(card):
    name = (_enum_name(card) or "?").upper()
    return "\u2605" if name == "WILD" else name[0]