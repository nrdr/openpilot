"""BluePilot MICI palette — single source of truth for the new home + settings UI.

All colors mirror mockups/mici_home.html so a tweak here propagates everywhere.
"""
import pyray as rl

# Accent (blue → cyan)
ACCENT       = rl.Color(0x4A, 0x8C, 0xFF, 0xFF)   # --accent
ACCENT2      = rl.Color(0x7E, 0xE0, 0xFF, 0xFF)   # --accent2
HALO         = rl.Color(0x4A, 0x8C, 0xFF, int(0.45 * 255))

# Text
TEXT         = rl.Color(0xF4, 0xF8, 0xFF, 0xFF)
MUTED        = rl.Color(0xF4, 0xF8, 0xFF, int(0.55 * 255))
DIM          = rl.Color(0xF4, 0xF8, 0xFF, int(0.30 * 255))

# Backgrounds
BG_DEEP      = rl.Color(0x02, 0x06, 0x0F, 0xFF)
BG_TOPLEFT   = rl.Color(0x14, 0x32, 0x6E, 0xFF)   # blue glow corner
PANEL_BG     = rl.Color(0xFF, 0xFF, 0xFF, int(0.04 * 255))
PANEL_BORDER = rl.Color(0xFF, 0xFF, 0xFF, int(0.07 * 255))

# Wordmark gradient targets (we draw with a single solid tint per state until
# we ship pre-baked gradient PNGs)
WORDMARK_BLUE   = rl.Color(0xCF, 0xEA, 0xFF, 0xFF)
WORDMARK_AMBER  = rl.Color(0xFF, 0xD8, 0x7A, 0xFF)
WORDMARK_GREY   = rl.Color(0x99, 0xA3, 0xB4, 0xFF)

# Status
READY   = rl.Color(0x4A, 0xDE, 0x80, 0xFF)
WARN    = rl.Color(0xFB, 0xBF, 0x24, 0xFF)
OFFLINE = rl.Color(0x6B, 0x72, 0x80, 0xFF)
DANGER  = rl.Color(0xF8, 0x71, 0x71, 0xFF)

# Aurora glow color tints (used inner color for radial circle gradient)
AURORA_BLUE_INNER  = rl.Color(0x4A, 0x8C, 0xFF, int(0.32 * 255))
AURORA_AMBER_INNER = rl.Color(0xFB, 0xBF, 0x24, int(0.36 * 255))
AURORA_GREY_INNER  = rl.Color(0x78, 0x82, 0x96, int(0.18 * 255))
AURORA_OUTER       = rl.Color(0x00, 0x00, 0x00, 0x00)

# Font sizes (post FONT_SCALE: framework multiplies by 1.16 internally for MICI)
FS_WORDMARK = 96
FS_PILL     = 26
FS_META     = 22
FS_NAME     = 40   # one-per-page card title
FS_SUB      = 24   # one-per-page card description
FS_STAT_KEY = 22
FS_STAT_VAL = 80
FS_BTN_LBL  = 44
FS_PAGE_CTR = 18
