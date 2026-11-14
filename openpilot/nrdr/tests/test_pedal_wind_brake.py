"""Live Wind Brake wiring and the user's pedal-only formula; no vehicle I/O."""
import ast
from dataclasses import replace
from types import SimpleNamespace as NS

import numpy as np
import pytest

from opendbc.car.honda.values import CAR, HONDA_BOSCH, HondaFlags
from opendbc.sunnypilot.car.honda import gas_interceptor
from openpilot.nrdr.car.opendbc import HondaParamsProvider, SLOW_PARAM_GROUPS
from openpilot.nrdr.tests.test_honda_pcm_ui import ROOT, Widget, native_layout, state
from openpilot.nrdr.tests.test_opendbc_boundary import FakeParams
from openpilot.nrdr.tests.test_parked_tuning_schema import allowed, items_in
from openpilot.nrdr.tests.test_mvl_settings import encoded, rpc as rpc
from openpilot.nrdr.ui import honda_pcm
from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import DEFAULT_SRC, compile_schema


@pytest.mark.parametrize("car", list(CAR))
@pytest.mark.parametrize("offroad", [False, True])
def test_nidec_pedal_wind_toggle_can_save_live_without_requesting_restart(car, offroad):
  ui = state(carFingerprint=str(car), enableGasInterceptor=True)
  ui.params.values.update(IsOffroad=offroad, ModelSelection="Cheddar", HondaLiveLearningGas=True)
  expected = car not in HONDA_BOSCH
  assert honda_pcm.wind_brake_editable(ui.CP, ui.CP_SP, ui.params, is_offroad=offroad) == expected
  assert honda_pcm.save_pcm_choice(ui, "NrdrHondaWindBrake", False) == expected
  assert ui.params.writes == ([("NrdrHondaWindBrake", False)] if expected else [])
  assert ui.params.get("ModelSelection") == "Cheddar" and ui.params.get_bool("HondaLiveLearningGas")
  assert not honda_pcm.save_pcm_choice(ui, "NrdrHondaPcmMode", 2)


@pytest.mark.parametrize("compact", [False, True])
def test_both_native_uis_expose_the_same_live_pedal_control(compact):
  ui = state(carFingerprint="HONDA_CLARITY", enableGasInterceptor=True)
  ui.params.values["IsOffroad"] = False
  if compact:
    path = ROOT / "openpilot/nrdr/ui/settings/pcm_modes_mici.py"
    tree = ast.parse(path.read_text())
    tree.body = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "WindBrakeControl"]
    env = dict(vars(honda_pcm), BigToggle=Widget, ui_state=ui, tr=lambda value: value)
    exec(compile(tree, str(path), "exec"), env)
    control = env["WindBrakeControl"]()
    assert control.enabled()
    control._select(False)
    assert control.value is False
  else:
    layout = native_layout(ui)
    layout._update_state()
    assert layout._wind_brake.enabled and not layout._pcm_mode.enabled
    layout._wind_brake.kwargs["callback"](False)
    layout._update_state()
    assert layout._wind_brake.value is False
  assert ui.params.writes == [("NrdrHondaWindBrake", False)]


@pytest.mark.parametrize("pedal,pcm,offroad", [(True, False, False), (True, False, True),
                                               (False, True, False), (False, True, True),
                                               (False, False, False), (False, False, True)])
def test_sunnylink_visibility_and_write_conditions_match_hardware(pedal, pcm, offroad):
  item = next(item for item in items_in(compile_schema(DEFAULT_SRC)) if item["key"] == "NrdrHondaWindBrake")
  caps = dict(nrdr_personal_pedal_available=pedal, nrdr_honda_pcm_tuning_available=pcm, IsOffroad=offroad)
  assert allowed(item, caps, "visibility") == (pedal or pcm)
  assert allowed(item, caps) == (pedal or (pcm and offroad))
  assert "Pedal changes apply live" in item["details"]
  assert "leaves braking unchanged" in item["description"]
  assert "without changing your saved choice" in item["details"]


@pytest.mark.parametrize("selected", [False, True])
@pytest.mark.parametrize("compressed", [False, True])
@pytest.mark.parametrize("offroad", [False, True])
def test_remote_pedal_toggle_is_live_typed_and_preserves_other_settings(rpc, selected, compressed, offroad):
  save, params, caps = rpc
  caps.update(nrdr_personal_pedal_available=True, nrdr_honda_pcm_tuning_available=False)
  params.values.update(IsOffroad=offroad, ModelSelection="Cheddar", HondaLiveLearningGas=True, NrdrLongitudinalController=3)
  save({"NrdrHondaWindBrake": encoded(int(selected), compressed)}, compressed)
  assert params.writes == [("NrdrHondaWindBrake", selected), ("ParamsVersion", "1")]
  assert params.get("ModelSelection") == "Cheddar" and params.get_bool("HondaLiveLearningGas")
  assert params.get("NrdrLongitudinalController") == 3


def test_remote_write_rechecks_vehicle_and_rejects_malformed_values(rpc):
  save, params, caps = rpc
  caps.update(nrdr_personal_pedal_available=True, nrdr_honda_pcm_tuning_available=False)
  params.values["IsOffroad"] = False
  with pytest.raises(ValueError):
    save({"NrdrHondaWindBrake": encoded("invalid")})
  assert not params.writes
  calls = 0

  def capabilities():
    nonlocal calls
    calls += 1
    return caps if calls == 1 else dict(caps, nrdr_personal_pedal_available=False)

  save.__globals__["_vehicle_tuning_capabilities"] = capabilities
  with pytest.raises(ValueError):
    save({"NrdrHondaWindBrake": encoded(0)})
  assert not params.writes


@pytest.mark.parametrize("saved", [None, False, True])
def test_existing_snapshot_refreshes_wind_choice_without_control_thread_disk_reads(saved):
  params = FakeParams({"NrdrHondaWindBrake": saved})
  provider = HondaParamsProvider(params, start_worker=False)
  try:
    initial = provider.get_live_tuning()
    assert initial.pedal_wind_brake is (saved is not False)
    before = len(params.reads)
    for _ in range(100):
      assert provider.get_live_tuning() is initial
    assert len(params.reads) == before
    params.values["NrdrHondaWindBrake"] = not initial.pedal_wind_brake
    for _ in SLOW_PARAM_GROUPS:
      provider.poll_once()
    updated = provider.get_live_tuning()
    assert updated.pedal_wind_brake is not initial.pedal_wind_brake
    assert replace(updated, generation=initial.generation, pedal_wind_brake=initial.pedal_wind_brake) == initial
    assert not params.writes
  finally:
    provider.close()


@pytest.mark.parametrize("personal", [False, True])
@pytest.mark.parametrize("roen", [False, True])
def test_pedal_formula_on_off_and_live_changes_preserve_clipping_ramp_and_disengagement(monkeypatch, personal, roen):
  monkeypatch.setattr(gas_interceptor, "create_gas_interceptor_command", lambda packer, gas, frame: (gas, frame))
  cp = NS(flags=HondaFlags.NIDEC | (HondaFlags.PERSONAL_PEDAL if personal else 0))
  controller = gas_interceptor.GasInterceptorCarController(cp, NS(enableGasInterceptor=True))
  last = 0.
  for frame in range(500):
    speed = (frame % 90) / 2
    gas = (frame % 37) / 25 - .1
    brake = (frame % 11) / 20
    wind = float(np.interp(speed, [0., 2.3, 35.], [.001, .002, .15]))
    enabled = (frame // 30) % 2 == 0
    active = frame % 45 > 5
    multiplier = float(np.interp(speed, [0., 10.], [.4, 1.])) if personal else gas_interceptor.gas_multiplier(speed, roen)
    request = gas - brake + wind * 3 / 4 if enabled else gas
    expected = min(float(np.clip(multiplier * request, 0., 1.)) if active else 0., last + .004)
    result = controller.update(NS(longActive=active), NS(out=NS(vEgo=speed)), gas, brake, wind,
                               None, frame, roen, wind_brake_enabled=enabled)
    assert controller.gas == expected and result == [(expected, frame // 2)]
    if not active:
      assert controller.gas == 0.
    last = expected


def test_default_remains_on_and_non_interceptor_emits_no_pedal_frames(monkeypatch):
  monkeypatch.setattr(gas_interceptor, "create_gas_interceptor_command", lambda *args: args)
  controller = gas_interceptor.GasInterceptorCarController(NS(flags=HondaFlags.NIDEC), NS(enableGasInterceptor=False))
  assert controller.update(NS(longActive=True), NS(out=NS(vEgo=25.)), .2, .1, .1, None, 0, wind_brake_enabled=False) == []
  assert controller.gas == 0.
  assert gas_interceptor.GasInterceptorCarController.update.__kwdefaults__["wind_brake_enabled"] is True
