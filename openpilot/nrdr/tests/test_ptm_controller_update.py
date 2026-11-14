"""PTM donor update: exact firmware admission, calibration law and unchanged saved IDs."""
import ast
import __future__
from dataclasses import replace
import json
import math
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace as NS

import numpy as np

from opendbc.sunnypilot.car.honda.values_ext import HondaFlagsSP, PTM_EPS_REVISIONS
from openpilot.nrdr.features.lateral import vfn_eps_core as core
from openpilot.nrdr.features.lateral.controller_selection import (
  ODYSSEY_PROFILE, RIDGELINE_PROFILE, firmware_controller_profile, firmware_controller_selected,
)
from openpilot.nrdr.features.lateral.honda_rack_map import get_rack_map_table
from openpilot.nrdr.features.lateral.honda_vgr import get_honda_vgr_profile


def car(fingerprint, firmware, modified=True):
  return (NS(brand="honda", carFingerprint=fingerprint, carFw=[NS(ecu="eps", fwVersion=firmware)],
             lateralTuning=NS(which=lambda: "pid")), NS(flags=HondaFlagsSP.EPS_MODIFIED.value if modified else 0))


class TestPtmUpdate(unittest.TestCase):
  def test_ptm_geometry_is_explicit_and_cached(self):
    from openpilot.nrdr.features.lateral.steer_ratio_tuning import resolve_steer_ratio_selection
    from openpilot.nrdr.features.lateral.honda_vgr import ptm_inverse
    cp, _ = car("HONDA_CLARITY", b"39990-TRW-A020")
    cp.steerRatio, cp.wheelbase = 16.5, 2.75
    # Value 3 is Firmware geometry; the stored setting is not changed by the controller.
    from openpilot.nrdr.features.lateral.steer_ratio_tuning import SteerRatioMode
    settings = {"NrdrSteerRatioMode": int(SteerRatioMode.FIRMWARE)}
    normal = resolve_steer_ratio_selection(cp, settings)
    ptm = resolve_steer_ratio_selection(cp, settings, ptm_baseline=True)
    self.assertFalse(normal.rack_map.ptm_baseline)
    self.assertTrue(ptm.rack_map.ptm_baseline)
    self.assertIs(ptm.rack_map, resolve_steer_ratio_selection(cp, settings, ptm_baseline=True).rack_map)
    linear, angles = ptm_inverse(get_honda_vgr_profile(cp))
    grid = np.unique(np.r_[angles, np.linspace(0., angles[-1], 1001)])
    path = np.radians(np.interp(grid, angles, linear)) / np.interp(grid, ptm.rack_map.table.ratio_bp, ptm.rack_map.table.ratio_v)
    np.testing.assert_array_equal(ptm.rack_map.angle_grid, grid)
    np.testing.assert_array_equal(ptm.rack_map.path_grid, path)
    for mode in (SteerRatioMode.COMMA, SteerRatioMode.MANUAL):
      options = {"NrdrSteerRatioMode": int(mode)}
      a, b = resolve_steer_ratio_selection(cp, options), resolve_steer_ratio_selection(cp, options, ptm_baseline=True)
      self.assertEqual(a.ratio_at(100.), b.ratio_at(100.))

  @unittest.skipIf(sys.platform == "win32", "native realtime dependencies")
  def test_hardcoded_delay_and_model_ramp(self):
    from openpilot.nrdr.features.lateral.yaw_control_timing import command_delay
    from openpilot.nrdr.features.lateral.model_source import ModelActionRamp
    saved = {"NrdrYawCommandDelayLow": .29, "NrdrYawCommandDelayHigh": .01}
    np.testing.assert_allclose([command_delay(saved, v) for v in (0., 10., 12.5, 15., 30.)], [.2, .2, .15, .1, .1])
    self.assertEqual(saved, {"NrdrYawCommandDelayLow": .29, "NrdrYawCommandDelayHigh": .01})
    ramp = ModelActionRamp()
    self.assertEqual(ramp.update(.002, False, False), .002)
    self.assertEqual(ramp.update(.007, True, True), .002)
    np.testing.assert_allclose([ramp.update(.007, False, True) for _ in range(6)], [.003, .004, .005, .006, .007, .007])

  @unittest.skipIf(sys.platform == "win32", "native realtime dependencies")
  def test_model_processing_is_ptm_only_and_longitudinal_is_unchanged(self):
    from openpilot.selfdrive.controls.lib import drive_helpers as helpers
    from openpilot.selfdrive.modeld.constants import ModelConstants, Plan
    root = Path(__file__).resolve().parents[2]
    def function(path, name, namespace):
      node, = [n for n in ast.walk(ast.parse((root / path).read_text())) if isinstance(n, ast.FunctionDef) and n.name == name]
      exec(compile(ast.Module(body=[node], type_ignores=[]), path, "exec",
                   flags=__future__.annotations.compiler_flag), namespace)
      return namespace[name]

    namespace = {**vars(helpers), "np": np, "ModelConstants": ModelConstants, "Plan": Plan,
                 "log": NS(ModelDataV2=NS(Action=lambda **kw: NS(**kw))), "PTM_LAT_SMOOTH_SECONDS": .1,
                 "LAT_SMOOTH_SECONDS": 0., "LONG_SMOOTH_SECONDS": .3, "MIN_LAT_CONTROL_SPEED": .3}
    function("sunnypilot/modeld_v2/fill_model_msg.py", "get_curvature_from_output", namespace)
    prev = NS(desiredCurvature=.001, desiredAcceleration=.1)
    model = NS(constants=ModelConstants, mlsim=True, PLANPLUS_CONTROL=1., generation=9,
               LAT_SMOOTH_SECONDS=0., LONG_SMOOTH_SECONDS=.3, MIN_LAT_CONTROL_SPEED=.3)
    for path in ("selfdrive/modeld/modeld.py", "sunnypilot/modeld_v2/modeld.py"):
      action = function(path, "get_action_from_model", namespace)
      for output in ({"action": np.array([[1., .4]])}, {"plan": np.zeros((1, 33, 15))}):
        args = (output, prev, .18, .3, 20.)
        if path.startswith("sunnypilot"):
          args = (model, *args)
        normal = action(*args)
        disabled = action(*args, ptm_controller=False)
        ptm = action(*args, ptm_controller=True)
        self.assertEqual(vars(normal), vars(disabled))
        self.assertEqual((ptm.desiredAcceleration, ptm.shouldStop), (normal.desiredAcceleration, normal.shouldStop))
        self.assertAlmostEqual(ptm.desiredCurvature, helpers.smooth_value(normal.desiredCurvature, prev.desiredCurvature, .1))

    times = np.array([0., .1, .2, .3, .4])
    yaws, rates = times ** 2, times * 0
    normal = helpers.get_curvature_from_plan(yaws, rates, times, 20., .1)
    ptm = helpers.get_curvature_from_plan(yaws, rates, times, 20., .1, min_stable_delay=0.)
    self.assertAlmostEqual(normal, helpers.curv_from_psis(.03, 0., 20., .1))
    self.assertAlmostEqual(ptm, helpers.curv_from_psis(.01, 0., 20., .1))

  @unittest.skipIf(sys.platform == "win32", "native parameter bindings")
  def test_native_command_source_transition_and_inactive_output(self):
    from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
    from openpilot.nrdr.features.lateral.yaw_control_timing import command_delay
    for fingerprint, version, retained in (("HONDA_CLARITY", b"39990-TRW-A020", 0),
                                           ("HONDA_ODYSSEY", PTM_EPS_REVISIONS["HONDA_ODYSSEY"], 10)):
      cp, sp = car(fingerprint, version)
      cp.steerRatio, cp.wheelbase, cp.steerLimitTimer = 16.5, 2.75, .8
      controller = LatControlFirmware(cp, sp, None, .01)
      full = command_delay(None, 8., calibration=controller.firmware_profile.calibration)
      controller.update_model_v2(NS(meta=NS(laneChangeState=NS(raw=0)), action=NS(lateralSource="plan")))
      self.assertAlmostEqual(controller._command_delay(8.), .99 * full)
      for _ in range(99):
        value = controller._command_delay(8.)
      self.assertAlmostEqual(value, 0.)
      controller.update_model_v2(NS(meta=NS(laneChangeState=NS(raw=0)), action=NS(lateralSource="actionHead")))
      for _ in range(100):
        value = controller._command_delay(8.)
      self.assertAlmostEqual(value, full)
      controller.steer_ratio_selection = NS(desired_angle_no_offset=lambda *a: 5.)
      state = NS(vEgo=20., steeringAngleDeg=5., steeringRateDeg=0., steeringPressed=False, steeringTorque=0.)
      params = NS(roll=0., angleOffsetDeg=0.)
      for _ in range(100):
        controller.update(True, state, None, params, False, .001, None, False, .2)
      self.assertGreater(controller.core.ff_weight, 0.)
      self.assertEqual(controller.ride_through_frames, retained)
      for i in range(11):
        controller.reset()  # controlsd also calls reset while inactive
        output, _, log = controller.update(False, state, None, params, False, .001, None, False, .2)
        self.assertEqual(output, 0.)
        self.assertFalse(log.active)
        if i < retained:
          self.assertGreater(controller.core.ff_weight, 0.)
        else:
          self.assertEqual((controller.core.output, controller.core.pid.i, controller.core.ff_weight), (0., 0., 0.))

  def test_shared_native_and_remote_name_keeps_value_one(self):
    root = Path(__file__).resolve().parents[2]
    schema = json.loads((root / "sunnypilot/sunnylink/settings_ui.json").read_text())
    def items(value):
      if isinstance(value, dict):
        if value.get("key") == "NrdrLateralController" and "options" in value:
          yield value
        for child in value.values():
          yield from items(child)
      elif isinstance(value, list):
        for child in value:
          yield from items(child)
    selector, = items(schema)
    self.assertEqual([(o["value"], o["label"]) for o in selector["options"]], [(0, "PIF Control"), (1, "PTM Controller")])
    source = (root / "nrdr/ui/settings/pidf_ground.py").read_text()
    tree = ast.parse(source)
    label, = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_controller_label"]
    label.decorator_list = []
    for saved in (1, "1", b"1", 0):
      env = {"tr": lambda text: text, "ui_state": NS(params={"NrdrLateralController": saved})}
      exec(compile(ast.Module(body=[label], type_ignores=[]), "native_controller_label", "exec"), env)
      self.assertEqual(env["_controller_label"](), "PIF Control" if saved == 0 else "PTM Controller")
    self.assertIn('options.append(tr("PTM Controller"))', source)
    self.assertIn("options.index(dialog.selection)", source)

  def test_exact_new_revision_and_saved_selection(self):
    for fingerprint, profile in (("HONDA_ODYSSEY", ODYSSEY_PROFILE), ("HONDA_RIDGELINE", RIDGELINE_PROFILE)):
      version = PTM_EPS_REVISIONS[fingerprint]
      cp, sp = car(fingerprint, version + b"\0\0")
      self.assertIs(firmware_controller_profile(cp, sp), profile)
      for selection in (1, "1", b"1"):
        self.assertTrue(firmware_controller_selected({"NrdrLateralController": selection}, cp, sp))
      self.assertFalse(firmware_controller_selected({"NrdrLateralController": 0}, cp, sp))
      for unsupported in (version.replace(b",", b"-"), version.replace(b"-", b","), version + b"-other"):
        self.assertIsNone(firmware_controller_profile(*car(fingerprint, unsupported)))
      self.assertIsNone(firmware_controller_profile(*car(fingerprint, version, modified=False)))
      self.assertIsNone(firmware_controller_profile(*car("HONDA_CIVIC", version)))
      geometry = get_honda_vgr_profile(cp)
      for angle in (-600., -90., 0., 90., 600.):
        self.assertEqual(geometry.physical_to_linear(angle), angle)
      self.assertIsNotNone(get_rack_map_table(cp))

  def test_inverse_and_internal_clamp(self):
    for cal in (core.ODYSSEY_THR_A020, core.RIDGELINE_T6Z_A110):
      for load in (-7000., -2000., -50., 0., 50., 2000., 7000.):
        for rate in (-300., -40., 0., 40., 300.):
          target = core.r5_for_motion(load, rate, cal=cal)
          expected = load if cal.p_clamp is None else np.clip(load, -cal.p_clamp * cal.scale_q8 / 256.,
                                                            cal.p_clamp * cal.scale_q8 / 256.)
          self.assertAlmostEqual(core.firmware_output(target, rate, cal=cal), expected, places=6)
    self.assertEqual(core.RIDGELINE_T6Z_A110.kff, 0.)
    self.assertEqual(core.RIDGELINE_T6Z_A110.p_clamp, 942.)
    self.assertEqual(core.RIDGELINE_T6Z_A110.output_ceiling(), 3732 / 4096)
    self.assertEqual(core.ODYSSEY_THR_A020.output_ceiling(), 1.)

  def test_existing_calibration_law_is_unchanged(self):
    for cal in (core.CLARITY_A020, core.CIVIC_BOSCH_C020, core.CIVIC_TEG_A010, core.INSIGHT_TXM_A040,
                core.CIVIC_TBA_C120, core.CIVIC_TGG_A120, core.CIVIC_TBA_A030, core.CRV_TLA_A040,
                core.CRV_TLA_A220, core.RDX_TJB_A220):
      self.assertEqual((cal.kff, cal.scale_q8, cal.p_clamp), (45., 256., None))
      for target in np.linspace(-30000., 30000., 31):
        for rate in (-100., 0., 100.):
          r6 = core.firmware_r6(rate, 30., cal)
          before = 256. * (core.firmware_kp(target, cal) * (target - r6) + 45. * target) / 1024. / 256.
          self.assertEqual(core.firmware_output(target, rate, 30., cal), before)

  def test_new_core_outputs_remain_bounded_and_reset(self):
    for cal, load in ((core.ODYSSEY_THR_A020, core.ODYSSEY_THR_EPS_LOAD),
                      (core.RIDGELINE_T6Z_A110, core.RIDGELINE_T6Z_EPS_LOAD)):
      controller = core.HondaEpsLateralCore([0.], [.03], [0.], [.01], .01,
        ff=core.HondaEpsFirmwareFeedforward(.01, cal=cal, load=load))
      for i in range(400):
        output = controller.update(10. + 5. * math.sin(i / 30.), 0., 10., 20., .01, i % 80 < 10, False)
        self.assertTrue(math.isfinite(output))
        self.assertLessEqual(abs(output), cal.output_ceiling())
      controller.reset()
      self.assertEqual((controller.output, controller.pid.i, controller.ff_weight), (0., 0., 0.))

  @unittest.skipIf(sys.platform == "win32", "native parameter bindings")
  def test_native_timing_and_transport(self):
    from opendbc.car import gen_empty_fingerprint, structs
    from opendbc.car.honda.interface import CarInterface
    from opendbc.car.honda.values import CAR, CarControllerParams
    from opendbc.sunnypilot.car.tests.runtime_config import make_test_car_config
    from openpilot.nrdr.features.lateral.controller_selection import RDX_PROFILE
    from openpilot.nrdr.features.lateral.latcontrol_fw import LatControlFirmware
    from openpilot.nrdr.features.lateral.yaw_control_timing import command_delay, prediction_delay_schedule

    self.assertAlmostEqual(command_delay(None, 5., calibration="crv_tla_a040"), .18)
    self.assertAlmostEqual(command_delay(None, 20., calibration="crv_tla_a040"), 0.)
    self.assertAlmostEqual(command_delay(None, 5., calibration="crv_tla_a220"), .12)
    self.assertEqual(prediction_delay_schedule(RDX_PROFILE)[1], (.15, .40, .40, .22, .30))
    for name in PTM_EPS_REVISIONS:
      candidate = getattr(CAR, name)
      for modified in (False, True):
        version = PTM_EPS_REVISIONS[name]
        if not modified:
          version = version.replace(b",", b"-")
        fw = [structs.CarParams.CarFw(ecu="eps", fwVersion=version + b"\0\0")]
        fingerprint, config = gen_empty_fingerprint(), make_test_car_config()
        cp = CarInterface.get_params(candidate, fingerprint, fw, alpha_long=False, is_release=False,
                                     docs=False, interface_config=config)
        cp.carFw = fw  # normally attached by car_helpers after get_params
        sp = CarInterface.get_params_sp(cp, candidate, fingerprint, fw, alpha_long=False, is_release_sp=False, docs=False)
        if not modified:
          self.assertIsNone(firmware_controller_profile(cp, sp))
          continue
        params = CarControllerParams(cp)
        self.assertEqual(params.STEER_MAX, 4096)
        self.assertEqual(params.STEER_LOOKUP_BP, [-4096, 0, 4096])
        self.assertEqual(params.STEER_LOOKUP_BP, params.STEER_LOOKUP_V)
        self.assertIsNotNone(firmware_controller_profile(cp, sp),
                             (str(cp.brand), str(cp.carFingerprint), cp.lateralTuning.which(), sp.flags))
        controller = LatControlFirmware(cp, sp, None, .01)
        self.assertEqual(controller.core.ff.cal.e4_per_output, params.STEER_MAX)
        self.assertIsNotNone(controller.delay_schedule)
        config.honda.provider.live_tuning = replace(config.honda.provider.live_tuning,
          override_fade_up_s=0.0, steer_delta_limiter_enabled=False, live_learning_gas=False)
        ci = CarInterface(cp, sp, config)
        ci.update([])
        ci.CS.out.vEgo = 20.0
        ci.CS.out.standstill = False
        ci.CS.out.steeringPressed = False
        ci.CS.out.steeringTorque = 0.0
        ci.CS.steer_control_active = True
        for tick, (active, output) in enumerate(((True, -.5), (True, .5), (False, .5))):
          cc = structs.CarControl(enabled=active, latActive=active)
          cc.actuators.torque = output
          returned, messages = ci.apply(cc.as_reader(), structs.CarControlSP(), tick * 10_000_000)
          frame, = [data for address, data, _ in messages if address == 0xE4]
          expected = int(-4096 * output) if active else 0
          self.assertEqual(int.from_bytes(frame[:2], "big", signed=True), expected)
          self.assertEqual(returned.torqueOutputCan, expected)


if __name__ == "__main__":
  unittest.main()
