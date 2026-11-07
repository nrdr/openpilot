"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from enum import IntFlag


RDX_TJB_A220_PTM = b"39990-TJB,A220\x00\x00"


class HondaFlagsSP(IntFlag):
  NIDEC_HYBRID = 1
  EPS_MODIFIED = 2
  HYBRID_ALT_BRAKEHOLD = 4
  HAS_CAMERA_MESSAGES = 8
  STOCK_LONGITUDINAL = 16
  CLARITY_INTERCEPTOR_BRAKE_CAPABLE = 32


class HondaSafetyFlagsSP:
  NIDEC_HYBRID = 1
  GAS_INTERCEPTOR = 2
  STOCK_LONGITUDINAL = 4
  GAS_INTERCEPTOR_THRESHOLD_512 = 8
  CLARITY_INTERCEPTOR_BRAKE = 16
