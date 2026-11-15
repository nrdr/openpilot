#!/usr/bin/env python3
from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.honda.bosch_a_radar import BOSCH_A_DBC_NAME, BoschARadar
from opendbc.car.honda.values import DBC
from opendbc.car.interfaces import RadarInterfaceBase


def _create_nidec_can_parser(car_fingerprint):
  radar_messages = [0x400] + list(range(0x430, 0x43A)) + list(range(0x440, 0x446))
  messages = [(m, 20) for m in radar_messages]
  return CANParser(DBC[car_fingerprint][Bus.radar], messages, 1)


class RadarInterface(RadarInterfaceBase):
  def __init__(self, CP, CP_SP):
    super().__init__(CP, CP_SP)
    self.radar_fault = False
    self.radar_wrong_config = False
    self.radar_off_can = CP.radarUnavailable
    self.bosch_a_radar = (not self.radar_off_can and Bus.radar in DBC[CP.carFingerprint] and
                          DBC[CP.carFingerprint][Bus.radar] == BOSCH_A_DBC_NAME)
    # The Bosch-A object-bank decoder lives in bosch_a_radar.BoschARadar; this class only selects and delegates.
    self.bosch_a = None
    # Ego speed, set by card before each update; the Bosch-A decoder's reversing-coast bound reads it.
    self.v_ego: float | None = None

    if self.radar_off_can:
      self.rcp = None
      self.trigger_msg = 0x445
    elif self.bosch_a_radar:
      self.bosch_a = BoschARadar(CP, CP_SP)
      self.rcp = self.bosch_a.rcp
      self.trigger_msg = self.bosch_a.trigger_msg
    else:
      # Nidec
      self.rcp = _create_nidec_can_parser(CP.carFingerprint)
      self.trigger_msg = 0x445
      self.track_id = 0

    self.updated_messages = set()

  @property
  def point_statuses(self) -> dict[int, int] | None:
    """Bosch-A F0 STATUS per point of the last RadarData returned; None for other radars."""
    return self.bosch_a.point_statuses if self.bosch_a is not None else None

  def update(self, can_strings):
    if self.bosch_a is not None:
      self.bosch_a.v_ego = self.v_ego
      return self.bosch_a.update(can_strings)

    if self.radar_off_can or self.rcp is None:
      return super().update(None)

    vls = self.rcp.update(can_strings)
    self.updated_messages.update(vls)

    if self.trigger_msg not in self.updated_messages:
      return None

    rr = self._update(self.updated_messages)
    self.updated_messages.clear()
    return rr

  def _update(self, updated_messages):
    if self.bosch_a is not None:
      self.bosch_a.v_ego = self.v_ego
      return self.bosch_a._update_bosch_a(updated_messages)
    return self._update_nidec(updated_messages)

  def _update_nidec(self, updated_messages):
    ret = structs.RadarData()

    for ii in sorted(updated_messages):
      cpt = self.rcp.vl[ii]
      if ii == 0x400:
        # check for radar faults
        self.radar_fault = cpt['RADAR_STATE'] != 0x79
        self.radar_wrong_config = cpt['RADAR_STATE'] == 0x69
      elif cpt['LONG_DIST'] < 255:
        if ii not in self.pts or cpt['NEW_TRACK']:
          self.pts[ii] = structs.RadarData.RadarPoint()
          self.pts[ii].trackId = self.track_id
          self.track_id += 1
        self.pts[ii].dRel = cpt['LONG_DIST']  # from front of car
        self.pts[ii].yRel = -cpt['LAT_DIST']  # in car frame's y axis, left is positive
        self.pts[ii].vRel = cpt['REL_SPEED']
      else:
        if ii in self.pts:
          del self.pts[ii]

    if not self.rcp.can_valid:
      ret.errors.canError = True
    if self.radar_fault:
      ret.errors.radarFault = True
    if self.radar_wrong_config:
      ret.errors.wrongConfig = True

    ret.points = list(self.pts.values())

    return ret
