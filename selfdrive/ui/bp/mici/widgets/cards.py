"""Full-page cards used by the BP paged sub-panels.

Each card is a Widget sized to fill an entire page (PagedScroller resizes them
on show). Layouts:

- BigToggleCard — name + (wrapped) sub on the left, big iOS-style switch on
  the right. Bound to a Params bool key.
- BigMultiToggleCard — name + sub + a label-cycling button on the right
  (replaces a BigMultiParamToggle for one-per-page layout).
- StatCard — caps key on top, huge value below.
- BigButtonCard — single big card: icon (left) + label (right). danger=True
  flips colors red.
- SsidRowCard — Wi-Fi network row: lock icon, SSID, status; bars on the right.
- BigCategoryTile — settings landing tile (icon + label).

Description wrapping: the sub label uses wrap_text=True with max_width set to
the available column. If a sub overflows even after wrap, it is rendered with
a smaller font (24 → 22 → 20 px) chosen at render time via measure_text_cached.
"""
import pyray as rl
from collections.abc import Callable
from typing import Union

from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.icon_widget import IconWidget
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.common.params import Params

from openpilot.selfdrive.ui.bp.mici.widgets import bp_palette as P


def _fit_single_line(label: UnifiedLabel, target_size: int, max_width: float,
                     min_size: int = 20, step: int = 2) -> int:
  """Shrink `label`'s font from target_size down to min_size until the text
  fits in max_width on a single line. Returns the chosen size and leaves the
  label set to that size.
  """
  text = label.text
  font = gui_app.font(label._font_weight)
  letter_spacing = label._letter_spacing
  # Walk down in `step`-sized chunks; stop the first time the text fits.
  for sz in range(target_size, min_size - 1, -step):
    spacing_px = sz * letter_spacing
    w = measure_text_cached(font, text, sz, spacing_px).x
    if w <= max_width:
      label.set_font_size(sz)
      return sz
  label.set_font_size(min_size)
  return min_size


CARD_PADDING_X = 24
CARD_PADDING_Y = 14

# Horizontal margin between the page edge and the card frame. Vertical margin
# stays small so cards still fill most of the page height.
CARD_MARGIN_X = 22
CARD_MARGIN_Y = 6
SWITCH_W = 110
SWITCH_H = 64
SWITCH_KNOB = 56


def _draw_panel_bg(r: rl.Rectangle, color: rl.Color = P.PANEL_BG, border: rl.Color = P.PANEL_BORDER) -> None:
  rl.draw_rectangle_rounded(r, 0.10, 16, color)
  rl.draw_rectangle_rounded_lines_ex(r, 0.10, 16, 1, border)


def _draw_frosted_card(r, tint=None) -> None:
  """Subtle frosted-glass card: translucent fill + soft top highlight + thin
  border. Sits on top of the BP radial gradient so the underlying color
  bleeds through, giving the depth the mockup has via backdrop-filter.

  `tint`: when given, used as a faint accent overlay (e.g. red for danger,
  blue for active). Otherwise the card is the neutral white-on-dark frost.
  """
  # Base fill — slightly more visible than P.PANEL_BG to read as glass over
  # the radial gradient.
  fill = rl.Color(0xFF, 0xFF, 0xFF, int(0.06 * 255))
  rl.draw_rectangle_rounded(r, 0.14, 14, fill)

  # Top-edge highlight: brighter strip at the top fading to transparent,
  # mimicking the glass-bevel look of frosted UI cards.
  hl_h = max(2, min(int(r.height * 0.35), 28))
  hl = rl.Rectangle(r.x + 1, r.y + 1, r.width - 2, hl_h)
  rl.draw_rectangle_gradient_v(int(hl.x), int(hl.y), int(hl.width), int(hl.height),
                                rl.Color(0xFF, 0xFF, 0xFF, int(0.06 * 255)),
                                rl.Color(0xFF, 0xFF, 0xFF, 0))

  # Optional accent tint (danger / active state).
  if tint is not None:
    overlay = rl.Color(tint.r, tint.g, tint.b, int(0.10 * 255))
    rl.draw_rectangle_rounded(r, 0.14, 14, overlay)

  # Visible frosted-glass border — 2px @ 18% alpha reads cleanly against the
  # radial gradient without looking heavy. Matches the mockup card outline.
  border = rl.Color(0xFF, 0xFF, 0xFF, int(0.18 * 255))
  rl.draw_rectangle_rounded_lines_ex(r, 0.14, 14, 2, border)


# ------------------------------------------------------------
# Toggle (boolean)
# ------------------------------------------------------------
class BigToggleCard(Widget):
  def __init__(self, name: str, sub: str, param_key: str | None = None,
               initial: bool = False, on_change: Callable[[bool], None] | None = None):
    super().__init__()
    self._name_text = name
    self._sub_text = sub
    self._param_key = param_key
    self._on_change = on_change
    self._params = Params() if param_key else None

    self._on = bool(self._params.get_bool(param_key)) if param_key and self._params else initial

    self._name_label = UnifiedLabel(name, font_size=P.FS_NAME, font_weight=FontWeight.BOLD,
                                    text_color=P.TEXT, max_width=520, wrap_text=False, elide=False)
    self._sub_label = UnifiedLabel(sub, font_size=P.FS_SUB, font_weight=FontWeight.MEDIUM,
                                   text_color=P.MUTED, max_width=400, wrap_text=True,
                                   line_height=1.15)

  # ---- public ----
  @property
  def is_on(self) -> bool:
    return self._on

  def set_on(self, v: bool, persist: bool = True) -> None:
    self._on = v
    if persist and self._params and self._param_key:
      self._params.put_bool(self._param_key, v)
    if self._on_change:
      self._on_change(v)

  # ---- input ----
  def _handle_mouse_release(self, mouse_pos: MousePos):
    self.set_on(not self._on, persist=True)

  def _update_state(self):
    # Pick up external param changes (e.g. from another panel or a script)
    if self._params and self._param_key:
      external = bool(self._params.get_bool(self._param_key))
      if external != self._on:
        self._on = external

  # ---- render ----
  def _render(self, _):
    r = self._rect
    # Mockup: toggle rows have NO card frame — just text + switch on gradient.
    bg_rect = rl.Rectangle(r.x + CARD_MARGIN_X, r.y + CARD_MARGIN_Y,
                           r.width - CARD_MARGIN_X * 2, r.height - CARD_MARGIN_Y * 2)

    # Switch on right
    sw_y = bg_rect.y + (bg_rect.height - SWITCH_H) / 2
    sw_x = bg_rect.x + bg_rect.width - SWITCH_W - CARD_PADDING_X
    self._draw_switch(sw_x, sw_y)

    # Text column on left
    text_x = bg_rect.x + CARD_PADDING_X
    text_max_w = sw_x - text_x - 16

    # Name label — auto-shrink to fit horizontally
    name_y = bg_rect.y + CARD_PADDING_Y
    _fit_single_line(self._name_label, P.FS_NAME, text_max_w)
    self._name_label.set_max_width(int(text_max_w))
    self._name_label.set_position(text_x, name_y)
    self._name_label.render()

    # Sub label — wrap to text_max_w, step down font if too tall
    self._sub_label.set_max_width(int(text_max_w))
    sub_y = name_y + P.FS_NAME * 1.05 + 4

    # Auto-shrink: try 24 → 22 → 20 if sub would overflow available height.
    # Then set rect.height explicitly so all wrapped lines render.
    available_h = bg_rect.y + bg_rect.height - sub_y - CARD_PADDING_Y
    for sz in (P.FS_SUB, 22, 20):
      self._sub_label.set_font_size(sz)
      h = self._sub_label.get_content_height(int(text_max_w))
      if h <= available_h:
        break
    # Buffer rect.height: UnifiedLabel.get_content_height omits the line_height
    # multiplier on line 0, but _render applies it to every line — so total
    # measured by get_content_height is ~one factor short. Add a generous fudge
    # so all wrapped lines actually render.
    h = self._sub_label.get_content_height(int(text_max_w)) + self._sub_label.font_size * 0.5
    self._sub_label.set_rect(rl.Rectangle(text_x, sub_y, text_max_w, h))
    self._sub_label.render()

  def _draw_switch(self, x: float, y: float) -> None:
    track = rl.Rectangle(x, y, SWITCH_W, SWITCH_H)
    track_color = P.ACCENT if self._on else rl.Color(0xFF, 0xFF, 0xFF, int(0.10 * 255))
    rl.draw_rectangle_rounded(track, 1.0, 16, track_color)
    if self._on:
      # Soft halo
      glow = rl.Color(P.ACCENT.r, P.ACCENT.g, P.ACCENT.b, int(0.45 * 255))
      glow_rect = rl.Rectangle(x - 2, y - 2, SWITCH_W + 4, SWITCH_H + 4)
      rl.draw_rectangle_rounded_lines_ex(glow_rect, 1.0, 16, 2, glow)
    # Knob
    knob_x = x + (SWITCH_W - SWITCH_KNOB - 4) if self._on else x + 4
    knob_y = y + 4
    rl.draw_circle(int(knob_x + SWITCH_KNOB / 2), int(knob_y + SWITCH_KNOB / 2),
                   SWITCH_KNOB / 2, rl.WHITE)


# ------------------------------------------------------------
# 3+ state toggle (e.g. driving personality)
# ------------------------------------------------------------
class BigMultiToggleCard(Widget):
  def __init__(self, name: str, sub: str, options: list[str],
               param_key: str | None = None, on_change: Callable[[int], None] | None = None,
               initial_idx: int = 0):
    super().__init__()
    self._name = name
    self._options = options
    self._param_key = param_key
    self._on_change = on_change
    self._params = Params() if param_key else None
    self._idx = self._read_idx(initial_idx)

    self._name_label = UnifiedLabel(name, font_size=P.FS_NAME, font_weight=FontWeight.BOLD,
                                    text_color=P.TEXT, max_width=520, wrap_text=False, elide=False)
    self._sub_label = UnifiedLabel(sub, font_size=P.FS_SUB, font_weight=FontWeight.MEDIUM,
                                   text_color=P.MUTED, max_width=400, wrap_text=True,
                                   line_height=1.15)
    # Value pill text — wide max_width so we never elide; pill bounding box
    # is computed from measured text in _render and capped to card width.
    self._value_label = UnifiedLabel("", font_size=36, font_weight=FontWeight.BOLD,
                                     text_color=P.ACCENT2, max_width=520, wrap_text=False,
                                     letter_spacing=0.04, elide=False)

  def _read_idx(self, default: int) -> int:
    if not self._params or not self._param_key:
      return default
    val = self._params.get(self._param_key)
    if val is None:
      return default
    # Params returns int for INT keys, bool/None for BOOL, bytes/str otherwise.
    if isinstance(val, bool):
      return 1 if val else 0
    if isinstance(val, int):
      return max(0, min(len(self._options) - 1, val))
    if isinstance(val, (bytes, str)):
      try:
        return int(val)
      except (TypeError, ValueError):
        return default
    return default

  def _persist(self):
    if self._params and self._param_key:
      # Use put_nonblocking with the right type. We don't know the param type
      # at construction time, so try int first (covers LongitudinalPersonality,
      # mici_complication, etc.), then fall back to bool for 2-option keys.
      try:
        self._params.put_nonblocking(self._param_key, int(self._idx))
      except TypeError:
        try:
          self._params.put_bool_nonblocking(self._param_key, bool(self._idx))
        except TypeError:
          self._params.put_nonblocking(self._param_key, str(self._idx))
    if self._on_change:
      self._on_change(self._idx)

  def _handle_mouse_release(self, _):
    self._idx = (self._idx + 1) % len(self._options)
    self._persist()

  def _render(self, _):
    r = self._rect
    # Mockup: multi-toggle has NO frame around content. Only the value pill
    # (drawn below) has accent fill.
    bg_rect = rl.Rectangle(r.x + CARD_MARGIN_X, r.y + CARD_MARGIN_Y,
                           r.width - CARD_MARGIN_X * 2, r.height - CARD_MARGIN_Y * 2)

    text_x = bg_rect.x + CARD_PADDING_X
    text_max_w = bg_rect.width - CARD_PADDING_X * 2

    # ---- Title (full width, top) — auto-shrink to fit
    name_y = bg_rect.y + CARD_PADDING_Y
    _fit_single_line(self._name_label, P.FS_NAME, text_max_w)
    self._name_label.set_max_width(int(text_max_w))
    self._name_label.set_position(text_x, name_y)
    self._name_label.render()

    # ---- Big centered value pill (bottom half) ----
    # Pill width follows the text. We try the target font (36px) first; if
    # the resulting pill would exceed available card width, shrink the font
    # rather than the text.
    value_text = self._options[self._idx].upper()
    self._value_label.set_text(value_text)

    PILL_PAD_X = 36
    PILL_TARGET = 36
    PILL_MIN = 22
    pill_max_inner_w = bg_rect.width - CARD_PADDING_X * 2 - PILL_PAD_X * 2

    chosen_size = _fit_single_line(self._value_label, PILL_TARGET, pill_max_inner_w, min_size=PILL_MIN)

    # Now measure at the chosen size so vw is exact for this frame.
    font = gui_app.font(self._value_label._font_weight)
    spacing_px = chosen_size * self._value_label._letter_spacing
    vw = measure_text_cached(font, value_text, chosen_size, spacing_px).x

    pill_w = vw + PILL_PAD_X * 2
    pill_h = 70
    px = bg_rect.x + (bg_rect.width - pill_w) / 2
    bottom_band_y = bg_rect.y + bg_rect.height * 0.45
    bottom_band_h = bg_rect.height * 0.55 - CARD_PADDING_Y
    py = bottom_band_y + (bottom_band_h - pill_h) / 2

    pill = rl.Rectangle(px, py, pill_w, pill_h)
    rl.draw_rectangle_rounded(pill, 1.0, 16, rl.Color(P.ACCENT.r, P.ACCENT.g, P.ACCENT.b, int(0.20 * 255)))
    rl.draw_rectangle_rounded_lines_ex(pill, 1.0, 16, 1,
                                        rl.Color(P.ACCENT.r, P.ACCENT.g, P.ACCENT.b, int(0.55 * 255)))
    # Vertically center the (possibly shrunk) text in the pill.
    self._value_label.set_position(px + (pill_w - vw) / 2,
                                   py + (pill_h - chosen_size) / 2 - 2)
    self._value_label.render()


# ------------------------------------------------------------
# Stat card
# ------------------------------------------------------------
class StatCard(Widget):
  def __init__(self, key: str, value: Union[str, Callable[[], str]],
               variant: str = "default"):
    """variant: 'default' (huge bold), 'small' (60px), 'mono' (Inter Bold mono-ish)."""
    super().__init__()
    self._key = key
    self._value = value
    self._variant = variant

    val_size = {"small": 60, "mono": 56}.get(variant, P.FS_STAT_VAL)
    self._target_val_size = val_size
    self._key_label = UnifiedLabel(key.upper(), font_size=P.FS_STAT_KEY, font_weight=FontWeight.BOLD,
                                   text_color=P.MUTED, letter_spacing=0.10,
                                   max_width=520, wrap_text=False, elide=False)
    self._val_label = UnifiedLabel("", font_size=val_size,
                                   font_weight=FontWeight.BOLD,
                                   text_color=P.TEXT, letter_spacing=-0.02,
                                   max_width=520, wrap_text=False, elide=False)

  def _resolve_value(self) -> str:
    return self._value() if callable(self._value) else str(self._value)

  def _render(self, _):
    r = self._rect
    bg_rect = rl.Rectangle(r.x + CARD_MARGIN_X, r.y + CARD_MARGIN_Y, r.width - CARD_MARGIN_X * 2, r.height - CARD_MARGIN_Y * 2)
    _draw_frosted_card(bg_rect)

    self._val_label.set_text(self._resolve_value())

    text_x = bg_rect.x + CARD_PADDING_X
    text_max_w = bg_rect.width - CARD_PADDING_X * 2

    key_y = bg_rect.y + bg_rect.height * 0.30
    self._key_label.set_position(text_x, key_y)
    self._key_label.render()

    # Auto-shrink value to fit horizontally — long values like "Ford F-150
    # Hybrid Lariat" should size down rather than elide.
    chosen = _fit_single_line(self._val_label, self._target_val_size, text_max_w, min_size=24)
    val_y = bg_rect.y + bg_rect.height * 0.42
    self._val_label.set_max_width(int(text_max_w))
    self._val_label.set_position(text_x, val_y)
    self._val_label.render()


# ------------------------------------------------------------
# Big button card (Pair, Reboot, Power Off, ...)
# ------------------------------------------------------------
class BigButtonCard(Widget):
  ICON_BOX = 60  # bounding box for the icon — drawn aspect-preserving inside

  def __init__(self, label: str, icon: Union[str, rl.Texture, None] = None,
               on_click: Callable | None = None, danger: bool = False):
    super().__init__()
    self._danger = danger
    if isinstance(icon, str):
      # Force a small bounding-box load so we never blow up to 256+ px for
      # icons authored at large native sizes.
      icon = gui_app.texture(icon, self.ICON_BOX, self.ICON_BOX)
    self._icon = icon
    self._label = UnifiedLabel(label, font_size=P.FS_BTN_LBL, font_weight=FontWeight.BOLD,
                               text_color=(P.DANGER if danger else P.TEXT),
                               max_width=520, wrap_text=False, elide=False)
    if on_click is not None:
      self.set_click_callback(on_click)
    # No _handle_mouse_release override — use the framework's default which
    # fires self._click_callback. This way both ctor on_click= and external
    # set_click_callback() work.

  def _render(self, _):
    r = self._rect
    bg_rect = rl.Rectangle(r.x + CARD_MARGIN_X, r.y + CARD_MARGIN_Y, r.width - CARD_MARGIN_X * 2, r.height - CARD_MARGIN_Y * 2)

    tint = None
    if self._danger:
      tint = P.DANGER
    elif self.is_pressed:
      tint = P.ACCENT
    _draw_frosted_card(bg_rect, tint=tint)
    # Add a slightly stronger danger border so destructive buttons read
    # immediately, not only when reading the label.
    if self._danger:
      border = rl.Color(P.DANGER.r, P.DANGER.g, P.DANGER.b, int(0.55 * 255))
      rl.draw_rectangle_rounded_lines_ex(bg_rect, 0.14, 14, 1, border)

    icon_col_w = (self.ICON_BOX + 28) if self._icon is not None else 0
    label_x = bg_rect.x + CARD_PADDING_X + icon_col_w
    label_max_w = int(bg_rect.x + bg_rect.width - CARD_PADDING_X - label_x)

    # Icon — centered vertically in its own column on the left
    if self._icon is not None:
      icon_x = bg_rect.x + CARD_PADDING_X
      icon_y = bg_rect.y + (bg_rect.height - self._icon.height) / 2
      tint = P.DANGER if self._danger else P.TEXT
      rl.draw_texture(self._icon, int(icon_x), int(icon_y), tint)

    # Label — auto-shrink so the full text always fits the remaining width.
    chosen = _fit_single_line(self._label, P.FS_BTN_LBL, label_max_w)
    self._label.set_max_width(label_max_w)
    lbl_y = bg_rect.y + (bg_rect.height - chosen) / 2 - 2
    self._label.set_position(label_x, lbl_y)
    self._label.render()


# ------------------------------------------------------------
# Wi-Fi SSID row card
# ------------------------------------------------------------
class SsidRowCard(Widget):
  def __init__(self, ssid: str, secured: bool, strength: int, connected: bool = False,
               on_click: Callable | None = None):
    """strength: 0..4."""
    super().__init__()
    self._ssid_text = ssid
    self._secured = secured
    self._strength = max(0, min(4, strength))
    self._connected = connected

    self._ssid_label = UnifiedLabel(ssid, font_size=P.FS_NAME, font_weight=FontWeight.BOLD,
                                    text_color=P.TEXT, max_width=400, wrap_text=False, elide=False)
    self._sub_label = UnifiedLabel("", font_size=P.FS_SUB, font_weight=FontWeight.BOLD,
                                   text_color=P.MUTED, max_width=400, wrap_text=False,
                                   letter_spacing=0.04)
    if on_click is not None:
      self.set_click_callback(on_click)

  def _render(self, _):
    r = self._rect
    bg_rect = rl.Rectangle(r.x + CARD_MARGIN_X, r.y + CARD_MARGIN_Y, r.width - CARD_MARGIN_X * 2, r.height - CARD_MARGIN_Y * 2)

    if self._connected:
      tint = P.ACCENT
      sub_color = P.ACCENT2
      bar_color = P.ACCENT2
    else:
      tint = None
      sub_color = P.MUTED
      bar_color = P.TEXT

    _draw_frosted_card(bg_rect, tint=tint)
    if self._connected:
      border = rl.Color(P.ACCENT.r, P.ACCENT.g, P.ACCENT.b, int(0.45 * 255))
      rl.draw_rectangle_rounded_lines_ex(bg_rect, 0.14, 14, 1, border)

    # Lock icon (procedural — small rounded rect over a hollow shackle).
    lock_x = bg_rect.x + 18
    lock_y = bg_rect.y + (bg_rect.height - 36) / 2
    if self._secured:
      _draw_lock(lock_x, lock_y, 28, P.MUTED)

    # SSID + sub — auto-shrink so long SSIDs don't get truncated
    text_x = lock_x + 40
    bars_x = bg_rect.x + bg_rect.width - 70
    ssid_max_w = bars_x - text_x - 12
    _fit_single_line(self._ssid_label, P.FS_NAME, ssid_max_w)
    self._ssid_label.set_position(text_x, bg_rect.y + 18)
    self._ssid_label.render()

    self._sub_label.set_text("CONNECTED" if self._connected else ("WPA2" if self._secured else "OPEN"))
    self._sub_label.set_text_color(sub_color)
    self._sub_label.set_position(text_x, bg_rect.y + 18 + P.FS_NAME + 4)
    self._sub_label.render()

    # Bars on the right
    self._draw_bars(bg_rect.x + bg_rect.width - 70, bg_rect.y + bg_rect.height / 2 - 20,
                    self._strength, bar_color)

  def _draw_bars(self, x: float, y: float, lit: int, color: rl.Color) -> None:
    HEIGHTS = (12, 22, 32, 42)
    bar_w = 8
    gap = 5
    for i, h in enumerate(HEIGHTS):
      cx = x + i * (bar_w + gap)
      cy = y + (HEIGHTS[-1] - h)
      c = color if i < lit else rl.Color(0xFF, 0xFF, 0xFF, int(0.25 * 255))
      rl.draw_rectangle(int(cx), int(cy), bar_w, int(h), c)


def _draw_lock(x: float, y: float, size: int, color: rl.Color) -> None:
  """Procedural padlock glyph at (x, y), height = size."""
  body_h = size * 0.55
  body_w = size * 0.85
  body_x = x + (size - body_w) / 2
  body_y = y + size - body_h
  rl.draw_rectangle_rounded(rl.Rectangle(body_x, body_y, body_w, body_h), 0.20, 8, color)
  # Shackle: arc above
  shackle_r = size * 0.30
  cx = x + size / 2
  cy = body_y - shackle_r * 0.10
  rl.draw_ring(rl.Vector2(cx, cy), shackle_r * 0.65, shackle_r, 180, 360, 16, color)


# ------------------------------------------------------------
# Settings landing tile
# ------------------------------------------------------------
class BigCategoryTile(Widget):
  # Wider tiles — ~3 visible on the 536-wide MICI screen so each tile reads
  # as a substantial card rather than a thin column. Extra tiles scroll
  # horizontally; the framework's scroll-indicator pill below hints at this.
  TILE_WIDTH = 150
  TILE_HEIGHT = 180

  def __init__(self, label: str, icon: Union[str, rl.Texture, None] = None,
               on_click: Callable | None = None):
    super().__init__()
    if isinstance(icon, str):
      icon = gui_app.texture(icon, 64, 64)
    self._icon = icon
    self._label = UnifiedLabel(label, font_size=22, font_weight=FontWeight.BOLD,
                               text_color=P.TEXT, max_width=180, wrap_text=False, elide=False)
    # Default natural size; parent (Scroller) reads rect.width to lay out.
    self.set_rect(rl.Rectangle(0, 0, self.TILE_WIDTH, self.TILE_HEIGHT))
    if on_click is not None:
      self.set_click_callback(on_click)

  def _render(self, _):
    r = self._rect
    # Slightly inset so the frosted-card border has room to breathe between
    # adjacent tiles in the menu strip.
    pad = 6
    bg_rect = rl.Rectangle(r.x + pad, r.y + pad, r.width - pad * 2, r.height - pad * 2)

    _draw_frosted_card(bg_rect, tint=P.ACCENT if self.is_pressed else None)

    # PNG icon centered slightly above middle
    if self._icon is not None:
      ix = bg_rect.x + (bg_rect.width - self._icon.width) / 2
      iy = bg_rect.y + bg_rect.height * 0.32 - self._icon.height / 2
      rl.draw_texture(self._icon, int(ix), int(iy), P.TEXT)

    # Label below icon — auto-shrink so longer labels still fit
    label_max = bg_rect.width - 12
    _fit_single_line(self._label, 22, label_max, min_size=14)
    lw = max(self._label.text_width, 1)
    lx = bg_rect.x + (bg_rect.width - lw) / 2
    ly = bg_rect.y + bg_rect.height * 0.78
    self._label.set_position(lx, ly)
    self._label.render()


# ------------------------------------------------------------
# Select-list tile (horizontal scroller item: vehicle make/model, saved networks, ...)
#
# Horizontal scroll matches the rest of the BP UI (settings landing, sub-panels)
# and avoids the swipe-down vs. scroll-back-to-top conflict that vertical
# NavWidget children hit (see NavScroller._back_enabled).
# ------------------------------------------------------------
class BPSelectTile(Widget):
  """Frosted tile used by BPSelectPanel.

  Layout: icon top-center, label bottom (auto-shrunk to fit). `selected=True`
  paints an accent tint + accent border for the currently-chosen entry.
  """
  TILE_WIDTH = 170
  TILE_HEIGHT = 180
  ICON_BOX = 64
  LABEL_FS = 22

  def __init__(self, label: str, icon: Union[str, rl.Texture, None] = None,
               selected: bool = False, on_click: Callable | None = None,
               width: int | None = None, height: int | None = None,
               wrap_label: bool = False):
    super().__init__()
    self._selected = selected
    self._wrap_label = wrap_label
    if isinstance(icon, str):
      icon = gui_app.texture(icon, self.ICON_BOX, self.ICON_BOX)
    self._icon = icon
    self._label = UnifiedLabel(label, font_size=self.LABEL_FS, font_weight=FontWeight.BOLD,
                               text_color=P.TEXT, max_width=240,
                               wrap_text=wrap_label, line_height=1.10, elide=False)
    w = width if width is not None else self.TILE_WIDTH
    h = height if height is not None else self.TILE_HEIGHT
    self.set_rect(rl.Rectangle(0, 0, w, h))
    if on_click is not None:
      self.set_click_callback(on_click)

  def _render(self, _):
    r = self._rect
    pad = 6
    bg_rect = rl.Rectangle(r.x + pad, r.y + pad, r.width - pad * 2, r.height - pad * 2)

    if self._selected:
      tint = P.ACCENT
    elif self.is_pressed:
      tint = P.ACCENT
    else:
      tint = None
    _draw_frosted_card(bg_rect, tint=tint)
    if self._selected:
      border = rl.Color(P.ACCENT.r, P.ACCENT.g, P.ACCENT.b, int(0.55 * 255))
      rl.draw_rectangle_rounded_lines_ex(bg_rect, 0.14, 14, 2, border)

    # Icon centered slightly above middle.
    if self._icon is not None:
      ix = bg_rect.x + (bg_rect.width - self._icon.width) / 2
      iy = bg_rect.y + bg_rect.height * 0.30 - self._icon.height / 2
      tint_color = P.ACCENT2 if self._selected else P.TEXT
      rl.draw_texture(self._icon, int(ix), int(iy), tint_color)

    # Label below icon
    label_max = int(bg_rect.width - 12)
    if self._wrap_label:
      # Multi-line: try font sizes 22 → 18 → 16 until 3 wrapped lines fit
      # in the lower 65% of the tile.
      max_lbl_h = bg_rect.height * 0.62
      chosen = self.LABEL_FS
      for sz in (self.LABEL_FS, 20, 18, 16):
        self._label.set_font_size(sz)
        self._label.set_max_width(label_max)
        h = self._label.get_content_height(label_max)
        chosen = sz
        if h <= max_lbl_h:
          break
      h = self._label.get_content_height(label_max) + chosen * 0.5
      lbl_y = bg_rect.y + bg_rect.height * 0.55
      self._label.set_rect(rl.Rectangle(bg_rect.x + 6, lbl_y,
                                         label_max, h))
      self._label.render()
    else:
      # Single-line: auto-shrink horizontally to fit.
      chosen = _fit_single_line(self._label, self.LABEL_FS, label_max, min_size=14)
      lw = max(self._label.text_width, 1)
      lx = bg_rect.x + (bg_rect.width - lw) / 2
      ly = bg_rect.y + bg_rect.height * 0.74
      self._label.set_position(lx, ly)
      self._label.render()
