"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from opendbc.car.structs import CarParams
from opendbc.car.honda.values import CAR

Ecu = CarParams.Ecu

FW_VERSIONS_EXT = {
  CAR.HONDA_ACCORD: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TVA,A150\x00\x00',
    ],
  },
  CAR.HONDA_CIVIC: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TBA,A030\x00\x00',
    ],
  },
  CAR.HONDA_CIVIC_BOSCH: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TGG,A020\x00\x00',
      b'39990-TGG,A120\x00\x00',
    ],
  },
  CAR.HONDA_CRV_5G: {
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TLA,A040\x00\x00',
    ],
  },
  CAR.HONDA_CLARITY: {
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TRW-A910\x00\x00',
    ],
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TRW-A010\x00\x00',
      b'57114-TRW-A020\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TRW-A020\x00\x00',
      b'39990-TRW,A020\x00\x00',  # modified firmware
      b'39990,TRW,A020\x00\x00',  # extra modified firmware
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TRW-A210\x00\x00',
      b'77959-TRW-A220\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TRW-A010\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TRW-A110\x00\x00',
    ],
  },
  CAR.HONDA_ACCORD_9G: {
    (Ecu.gateway, 0x18DAEFF1, None): [
      b'38897-T3W-0130\x00\x00',
    ],
    (Ecu.vsa, 0x18DA28F1, None): [
      b'57114-T2F-X840\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18DAB0F1, None): [
      b'36161-T2F-A140\x00\x00',
      b'36161-T3Z-A830\x00\x00'
    ],
    (Ecu.srs, 0x18DA53F1, None): [
      b'77959-T2F-A030\x00\x00',
      b'77959-T3Z-A020\x00\x00',
    ],
  },
  CAR.ACURA_MDX_3G: {
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TRX-H130\x00\x00',
      b'57114-TYS-A910\x00\x00', # unknown
      b'57114-TZ6-A810\x00\x00', # unknown
      b'57114-TZ6-A910\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TYS-A020\x00\x00', # unknown
      b'36161-TZ6-A340\x00\x00', # unknown
      b'36161-TZ6-A640\x00\x00', # unknown
      b'36161-TZ6-A730\x00\x00',
      b'36161-TRX-A820\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TRX-A710\x00\x00',
      b'54008-TZ5-A710\x00\x00', # unknown
      b'54008-TZ5-A911\x00\x00',
      b'54008-TZ5-A910\x00\x00',
      b'77959-TZ5-A110\x00\x00', # unknown
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TRX-A011\x00\x00',
      b'77959-TZ5-A110\x00\x00',
      b'77959-TZ5-A220\x00\x00',
    ],
    (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TYR-A011\x00\x00', # unknown
      b'38897-TZ5-A110\x00\x00', # unknown
      b'38897-TRX-A220\x00\x00',
    ],
    (Ecu.transmission, 0x18da1ef1, None): [
      b'28101-5DH-A400\x00\x00', # unknown
      b'28101-5DH-A401\x00\x00', # unknown
      b'28101-5NC-A310\x00\x00',
      b'28101-5NC-A770\x00\x00',
      b'28101-5NC-A740\x00\x00', # unknown
      b'28103-5NC-B210\x00\x00', # unknown
    ],
  },
  CAR.ACURA_MDX_3G_MMR: {
    (Ecu.vsa, 0x18da28f1, None): [
      b'57114-TRX-H130\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TYT-A220\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TRX-A011\x00\x00',
    ],
  },
  CAR.ACURA_RLX: {
    (Ecu.fwdRadar, 0x18dab0f1, None): [
      b'36161-TY3-A030\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18da0bf1, None): [
      b'54008-TY3-J010\x00\x00',
    ],
    (Ecu.srs, 0x18da53f1, None): [
      b'77959-TY3-L130\x00\x00',
    ],
     (Ecu.gateway, 0x18daeff1, None): [
      b'38897-TY3-A020\x00\x00',
    ],
     (Ecu.hud, 0x18da61f1, None): [
      b'78209-TY3-A110\x00\x00',
    ],
    (Ecu.eps, 0x18da30f1, None): [
      b'39990-TY3-J030\x00\x00',
    ],
  },
  CAR.ACURA_TLX_1G: {
    (Ecu.gateway, 0x18DAEFF1, None): [
      b'38897-TZ4-A010\x00\x00',
    ],
    (Ecu.fwdRadar, 0x18DAB0F1, None): [
      b'36161-TZ4-A120\x00\x00',
      b'36161-TZ7-A520\x00\x00',
      b'36161-TZ7-A710\x00\x00',
    ],
    (Ecu.vsa, 0x18DA28F1, None): [
      b'57114-TZ4-A510\x00\x00',
      b'57114-TZ7-A730\x00\x00',
    ],
    (Ecu.transmission, 0x18DA1EF1, None): [
      b'28101-5L9-A410\x00\x00',
      b'28101-5L9-A690\x00\x00',
    ],
    (Ecu.shiftByWire, 0x18DA0BF1, None): [
      b'54008-TZ3-A820\x00\x00',
      b'54008-TZ3-A830\x00\x00',
    ],
    (Ecu.srs, 0x18DA53F1, None): [
      b'77959-TZ3-A510\x00\x00',
      b'77959-TZ4-A510\x00\x00',
      b'77959-TZ7-A020\x00\x00',
    ],
  },
}
