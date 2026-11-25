"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from enum import IntFlag


RDX_TJB_A220_PTM = b"39990-TJB,A220\x00\x00"

# These builds have a different command law from earlier comma-only revisions.
PTM_EPS_REVISIONS = {
  "HONDA_RIDGELINE": b"39990-T6Z,A110",  # rev b5
  "HONDA_ODYSSEY": b"39990-THR,A020",  # 2026-11-10
}


class HondaFlagsSP(IntFlag):
  NIDEC_HYBRID = 1
  EPS_MODIFIED = 2
  HYBRID_ALT_BRAKEHOLD = 4
  HAS_CAMERA_MESSAGES = 8
  STOCK_LONGITUDINAL = 16
  CLARITY_INTERCEPTOR_BRAKE_CAPABLE = 32
  CLARITY_ANGLE_MODE = 64  # angle-loop EPS build (0x04 on): steerControlType angle, see clarity_eps.py
  EPS_ANGLE_PTM = 128  # EPS reports the angle PTM software ID ('+' in both separator slots, 39990+TRW+A020)


class HondaSafetyFlagsSP:
  NIDEC_HYBRID = 1
  GAS_INTERCEPTOR = 2
  STOCK_LONGITUDINAL = 4
  GAS_INTERCEPTOR_THRESHOLD_512 = 8
  CLARITY_INTERCEPTOR_BRAKE = 16
  CLARITY_ANGLE = 32  # Clarity angle-mode EPS: panda's angle rule on 0xE4 (honda.h HONDA_PARAM_SP_CLARITY_ANGLE)
