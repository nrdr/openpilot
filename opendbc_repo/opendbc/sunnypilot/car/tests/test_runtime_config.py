from dataclasses import FrozenInstanceError, MISSING, fields
from pathlib import Path

import pytest

from opendbc.car import structs
from opendbc.car.car_helpers import interfaces
from opendbc.car.gm.values import CAR as GM
from opendbc.sunnypilot.car.hyundai.longitudinal.helpers import LongitudinalTuningType
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP
from opendbc.sunnypilot.car.interfaces import (
  _initialize_coop_steering,
  _initialize_custom_longitudinal_tuning,
  _initialize_stop_and_go,
  _initialize_tesla_mads_screen_button,
  _initialize_toyota,
  setup_interfaces,
)
from opendbc.sunnypilot.car.runtime_config import (
  HondaCarConfig,
  HondaLiveTuning,
  HyundaiCarConfig,
  SubaruCarConfig,
  SunnypilotCarConfig,
  TeslaCarConfig,
  ToyotaCarConfig,
)
from opendbc.sunnypilot.car.subaru.values_ext import SubaruFlagsSP, SubaruSafetyFlagsSP
from opendbc.sunnypilot.car.tesla.values import MadsScreenButtonType, TeslaFlagsSP, TeslaSafetyFlagsSP
from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config
from opendbc.sunnypilot.car.toyota.values import ToyotaFlagsSP


CONFIG_TYPES = (
  HondaLiveTuning,
  HondaCarConfig,
  HyundaiCarConfig,
  SubaruCarConfig,
  TeslaCarConfig,
  ToyotaCarConfig,
  SunnypilotCarConfig,
)

FORMER_PARAM_KEYS = (
  "HondaBoschARadar",
  "HondaEnforceStockLongitudinal",
  "HyundaiLongitudinalTuning",
  "SubaruStopAndGo",
  "SubaruStopAndGoManualParkingBrake",
  "TeslaCoopSteering",
  "TeslaMadsScreenButton",
  "ToyotaEnforceStockLongitudinal",
  "ToyotaStopAndGoHack",
  "HondaGasFactorParams",
  "HondaWindFactorParams",
  "HondaOverrideFadeDownSecs",
  "HondaOverrideFadeUpSecs",
  "HondaOverrideTorqueScale",
  "HondaDriverAssistDuringOverride",
  "HondaLiveLearningGas",
  "HondaTorqueLowPassFilter",
  "HondaLpfTauLowSpeed",
  "HondaLpfTauStandard",
  "HondaLpfTauHighway",
  "HondaSteerDeltaLimiter",
  "HondaSteerDeltaUp",
  "HondaSteerDeltaDown",
  "HondaStoppingDecelRate",
  "NrdrIncreaseOverrideTolerance",
  "NrdrDriverOverrideThreshold",
  "HondaCenterBoostThreshold",
  "NrdrOverrideThresholdCenterBoost",
  "HondaAltDashboardSpeed",
  "HondaAltDashboardDistance",
  "NrdrClearDashFaults",
  "HondaSpoofCameraMessages",
  "NrdrCruiseButtonSubMode",
  "NrdrHudSubModeUntil",
  "NrdrHondaEcuMatchedLong",
  "NrdrHondaFullBrakeAuthority",
  "NrdrRoenAccelerationLimits",
)


def test_runtime_configuration_is_frozen_and_has_no_opendbc_owned_defaults():
  config = make_test_car_config()
  with pytest.raises(FrozenInstanceError):
    config.honda.bosch_a_radar = False

  for config_type in CONFIG_TYPES:
    for field in fields(config_type):
      assert field.default is MISSING
      assert field.default_factory is MISSING


def test_opendbc_production_has_no_openpilot_params_or_former_string_keys():
  package_root = Path(__file__).resolve().parents[3]
  production_sources = [
    path for path in package_root.rglob("*.py")
    if "tests" not in path.parts
  ]

  for path in production_sources:
    source = path.read_text(encoding="utf-8")
    assert "openpilot.common.params" not in source, path
    for key in FORMER_PARAM_KEYS:
      assert f'"{key}"' not in source, (path, key)


def test_typed_provider_boundary_preserves_factor_and_live_snapshot_identity():
  config = make_test_car_config()
  provider = config.honda.provider

  provider.initialize_live_learning_gas(True)
  assert provider.enable_gas_interceptor is True
  assert provider.get_live_tuning() is provider.live_tuning
  assert provider.load_longitudinal_factors("HONDA_CLARITY") == (1.0, 1.0)

  provider.persist_longitudinal_factors(1.1, 0.9, "HONDA_CLARITY")
  assert provider.persisted == [(1.1, 0.9, "HONDA_CLARITY")]


def test_generic_interface_override_forwards_the_boundary_without_behavior_changes():
  config = make_test_car_config()
  car_interface = interfaces[GM.CHEVROLET_BOLT_EUV]
  cp = car_interface.get_non_essential_params(GM.CHEVROLET_BOLT_EUV, config)
  cp_sp = car_interface.get_non_essential_params_sp(cp, GM.CHEVROLET_BOLT_EUV)

  interface = car_interface(cp, cp_sp, config)

  assert interface.interface_config is config


def test_standalone_hosts_keep_non_nrdr_setup_without_opendbc_defaults():
  calls = []

  class Interface:
    @staticmethod
    def get_longitudinal_tuning_sp(CP, CP_SP):
      calls.append((CP, CP_SP))

  cp = structs.CarParams(brand="mock")
  cp_sp = structs.CarParamsSP()

  setup_interfaces(Interface, cp, cp_sp, None)

  assert calls == [(cp, cp_sp)]


def test_typed_startup_fields_drive_the_same_interface_flags():
  class Interface:
    @staticmethod
    def get_longitudinal_tuning_sp(CP, CP_SP):
      return CP_SP

  cp = structs.CarParams()
  cp.brand = "hyundai"
  cp_sp = structs.CarParamsSP()
  _initialize_custom_longitudinal_tuning(
    Interface,
    cp,
    cp_sp,
    HyundaiCarConfig(longitudinal_tuning=LongitudinalTuningType.DYNAMIC),
  )
  assert cp_sp.flags & HyundaiFlagsSP.LONG_TUNING_DYNAMIC

  cp = structs.CarParams()
  cp.brand = "tesla"
  cp_sp = structs.CarParamsSP(flags=TeslaFlagsSP.HAS_VEHICLE_BUS.value)
  tesla = TeslaCarConfig(cooperative_steering=True, mads_screen_button=MadsScreenButtonType.THREE_FINGER)
  _initialize_coop_steering(cp, cp_sp, tesla)
  _initialize_tesla_mads_screen_button(cp, cp_sp, tesla)
  assert cp_sp.flags & TeslaFlagsSP.COOP_STEERING
  assert cp_sp.flags & TeslaFlagsSP.MADS_SCREEN_BUTTON_3_FINGER
  assert cp_sp.safetyParam & TeslaSafetyFlagsSP.MADS_SCREEN_BUTTON_3_FINGER

  cp = structs.CarParams()
  cp.brand = "subaru"
  cp_sp = structs.CarParamsSP()
  _initialize_stop_and_go(cp, cp_sp, SubaruCarConfig(stop_and_go=True, stop_and_go_manual_parking_brake=True))
  assert cp_sp.flags & SubaruFlagsSP.STOP_AND_GO
  assert cp_sp.flags & SubaruFlagsSP.STOP_AND_GO_MANUAL_PARKING_BRAKE
  assert cp_sp.safetyParam & SubaruSafetyFlagsSP.STOP_AND_GO

  cp = structs.CarParams()
  cp.brand = "toyota"
  cp.openpilotLongitudinalControl = True
  cp_sp = structs.CarParamsSP()
  _initialize_toyota(cp, cp_sp, ToyotaCarConfig(enforce_stock_longitudinal=False, stop_and_go_hack=True))
  assert cp_sp.flags & ToyotaFlagsSP.STOP_AND_GO_HACK
