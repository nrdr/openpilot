"""Bounded routes through existing widgets; absent native menus are not synthesized."""

SCENARIOS = {
  "tici": ("offroad", "settings", "lateral", "longitudinal", "longitudinal-pcm", "engine-braking", "overshoot", "steer-ratio", "override",
           "lane-centering", "dm", "accel-boost", "onroad", "onroad-sidebar", "onroad-personality", "onroad-longitudinal",
           "onroad-lane-centering", "onroad-dm", "onroad-accel-boost", "onroad-developer"),
  "mici": ("offroad", "settings", "longitudinal-pcm", "longitudinal-learning", "engine-braking", "overshoot", "overshoot-selector",
           "lane-centering", "dm", "accel-boost", "onroad",
           "onroad-settings", "onroad-personality", "onroad-longitudinal-pcm", "onroad-lane-centering", "onroad-dm",
           "onroad-accel-boost", "onroad-developer"),
}
UNSUPPORTED = {
  "tici": {
    "advanced-dm": "nrdr reminder-timing tuning is Sunnylink-schema-only; native Toggles exposes Always-On DM, not that menu.",
    "camera-and-live-control": "No road/cabin camera, model output, live controller, CAN, EPS firmware or physical display validation.",
  },
  "mici": {
    "lateral": "No nrdr lateral hub is wired into the mici settings tree.",
    "longitudinal": "No full nrdr longitudinal panel; capture the existing Device PCM and gas-learning controls instead.",
    "steer-ratio": "No native mici steer-ratio menu; the big-screen widget is not resized or transplanted here.",
    "override": "No native mici override-tuning menu.",
    "advanced-dm": "nrdr reminder-timing tuning is Sunnylink-schema-only; capture the native Always-On DM control instead.",
    "camera-and-live-control": "No road/cabin camera, model output, live controller, CAN, EPS firmware or physical display validation.",
  },
}
FIXTURE = "Synthetic Honda Civic/Nidec identity, openpilot longitudinal, no gas interceptor or EPS firmware; not a vehicle recording."
READ_ONLY_KEYS = ("NrdrExperimentalEngineBraking", "NrdrCruiseOverspeedAllowance", "AccelBoostSP")
TELEMETRY_SERVICES = ("carState", "carControl", "controlsState", "radarState", "laneCenteringStateSP")
MICI_LONGITUDINAL_INDEX = {"longitudinal-pcm": 2, "longitudinal-learning": 0, "engine-braking": 5, "overshoot": 6, "overshoot-selector": 6}


def open_read_only_selector(control, gui, params):
  saved = tuple(params.get(key) for key in READ_ONLY_KEYS)
  previous = gui._nav_stack[-1]
  assert control.enabled and control._click_callback is not None, "Overshoot control cannot open its selector"
  control._click_callback()  # Open only; never invoke an option's selection callback.
  assert tuple(params.get(key) for key in READ_ONLY_KEYS) == saved, "Opening the selector changed tuning params"
  assert gui._nav_stack[-1] is not previous, "Native overshoot selector did not open"
  return gui._nav_stack[-1]


def setup_vehicle_fixture():
  from opendbc.car.structs import car
  from openpilot.cereal import custom
  from openpilot.common.params import Params

  params = Params()  # Only called inside the worker's fresh OpenpilotPrefix.
  cp = car.CarParams(brand="honda", carFingerprint="HONDA_CIVIC", wheelbase=2.7, steerRatio=15.38,
                     openpilotLongitudinalControl=True, pcmCruise=True)
  cp_sp = custom.CarParamsSP.new_message(enableGasInterceptor=False)
  for key in ("CarParams", "CarParamsPersistent"):
    params.put(key, cp.to_bytes(), block=True)
  params.put("CarParamsSPPersistent", cp_sp.to_bytes(), block=True)
  for key, value in {"NrdrSuggestedSettings": False, "NrdrHandcraftedLateralTune": False,
                     "NrdrFirstRunSetupDone": True, "AlwaysOnDM": True, "AccelBoostSP": False}.items():
    params.put_bool(key, value, block=True)
  params.put("LaneGuidanceMode", 1, block=True)  # Star, solely to expose its tuning controls.
  params.put("DevUIInfo", 0, block=True)


def send_developer_telemetry(pm):
  """Synthetic display readings only. No controller, vehicle or CAN process runs."""
  from openpilot.cereal import messaging

  values = {
    "carState": {"vEgo": 20.0, "steeringAngleDeg": 3.5, "standstill": False},
    "carControl": {"latActive": True},
    "controlsState": {"curvature": 0.001, "lateralControlState": {"pidState": {"active": True, "steeringAngleDesiredDeg": 4.0}}},
    "radarState": {"leadOne": {"present": True, "dRel": 35.0, "vRel": -1.0}},
    "laneCenteringStateSP": {"laneGuidanceMode": 2, "blendfulDetailsValid": True, "blendfulTrust": 0.8, "blendfulActive": True},
  }
  for service, fields in values.items():
    message = messaging.new_message(service)
    message.valid = True
    setattr(message, service, fields)
    pm.send(service, message)


def focus_item(scroller, item, horizontal):
  """Scroll the existing container; do not replace/reparent/render a stand-in widget."""
  assert item.is_visible, "Requested control is hidden by native capability gating"
  if horizontal:
    center_x = scroller.rect.x + (scroller.rect.width - item.rect.width) / 2
    scroller.scroll_to(item.rect.x - center_x, smooth=False)
  else:
    scroller.scroll_panel.set_offset(scroller.scroll_panel._offset_filter_y.x - (item.rect.y - scroller.rect.y))


def build_preview_script(pm, main_layout, variant, device, markers):
  from openpilot.cereal import log, messaging
  from openpilot.common.hardware import HARDWARE
  from openpilot.selfdrive.ui.tests.diff.replay import FPS
  from openpilot.selfdrive.ui.tests.diff.replay_script import Script, send_onroad
  from openpilot.selfdrive.ui.ui_state import ui_state
  from openpilot.system.ui.lib.application import gui_app

  big = device == "tici"
  assert variant == ("tizi" if big else "mici")
  assert HARDWARE.get_device_type() == device and gui_app.big_ui() == big
  assert (gui_app.width, gui_app.height) == ((2160, 1080) if big else (536, 240))
  assert main_layout._onboarding_window.completed, "Onboarding obscures the preview"
  ui_state.update_params()  # Load fixture CP before any capability-gated menu is selected.
  assert ui_state.CP.brand == "honda" and ui_state.CP.carFingerprint == "HONDA_CIVIC"
  markers.update(size=[gui_app.width, gui_app.height], fixture=FIXTURE, unsupported=UNSUPPORTED[device],
                 layout_class=f"{type(main_layout).__module__}.{type(main_layout).__name__}")
  script = Script(FPS)
  selected = {}
  saved_tuning = tuple(ui_state.params.get(key) for key in READ_ONLY_KEYS)

  if big:
    from openpilot.selfdrive.ui.layouts.main import MainState
    # Import the extended enum from the settings module AFTER MainLayout initializes it.
    from openpilot.selfdrive.ui.layouts.settings.settings import PanelType
    from openpilot.nrdr.ui.settings.layout import PanelType as NrdrPanel
    from openpilot.nrdr.ui.settings.lateral_tuning import LateralPanel

    settings = main_layout._layouts[MainState.SETTINGS]
    nrdr = settings._panels[PanelType.NRDR].instance
    lateral = nrdr._lateral_layout
    longitudinal = nrdr._longitudinal_layout
    toggles = settings._panels[PanelType.TOGGLES].instance
    cruise = settings._panels[PanelType.CRUISE].instance

  def send_state(started):
    if started:
      send_onroad(pm)  # Stock panda/ignition fixture; no control/camera processes.
    state = messaging.new_message("deviceState")
    state.deviceState.started = started
    state.deviceState.deviceType = device
    state.deviceState.networkType = log.DeviceState.NetworkType.wifi
    pm.send("deviceState", state)
    alert = messaging.new_message("selfdriveState")
    alert.selfdriveState.personality = log.LongitudinalPersonality.standard
    if selected.get("route") == "developer":
      alert.selfdriveState.enabled = True
      alert.selfdriveState.active = True
      alert.selfdriveState.state = log.SelfdriveState.OpenpilotState.enabled
      send_developer_telemetry(pm)
    pm.send("selfdriveState", alert)

  def navigate(route):
    checks = []
    scroller = None
    ui_state.params.put("DevUIInfo", 2 if route == "developer" else 0, block=True)
    ui_state.update_params()
    if big:
      top = main_layout
      if route in ("offroad", "onroad", "sidebar", "developer"):
        main_layout._set_mode_for_state()
        if route == "sidebar":
          main_layout._sidebar.set_visible(True)
        state = MainState.HOME if route == "offroad" else MainState.ONROAD
        checks.append((main_layout, "_current_mode", state))
        widget = main_layout._layouts[state]
        if route == "sidebar":
          checks.append((main_layout._sidebar, "is_visible", True))
      elif route == "accel-boost":
        main_layout.open_settings(PanelType.CRUISE)
        checks.extend(((main_layout, "_current_mode", MainState.SETTINGS), (settings, "_current_panel", PanelType.CRUISE)))
        widget, scroller = cruise.accel_boost_toggle, cruise._scroller
      elif route in ("dm", "personality"):
        main_layout.open_settings(PanelType.TOGGLES)
        checks.extend(((main_layout, "_current_mode", MainState.SETTINGS), (settings, "_current_panel", PanelType.TOGGLES)))
        widget = toggles._toggles["AlwaysOnDM"] if route == "dm" else toggles._long_personality_setting
        scroller = toggles._scroller
      else:
        main_layout.open_settings(PanelType.NRDR)
        checks.extend(((main_layout, "_current_mode", MainState.SETTINGS), (settings, "_current_panel", PanelType.NRDR)))
        panel = NrdrPanel.NRDR if route == "settings" else (
          NrdrPanel.LONGITUDINAL if route.startswith("longitudinal") or route in ("engine-braking", "overshoot") else NrdrPanel.LATERAL)
        nrdr._set_current_panel(panel)
        checks.append((nrdr, "_current_panel", panel))
        widget = nrdr if route == "settings" else nrdr._panel_widget(panel)
        if panel == NrdrPanel.LATERAL:
          subpanel = {"lateral": LateralPanel.HUB, "steer-ratio": LateralPanel.STEER_RATIO,
                      "override": LateralPanel.OVERRIDE, "lane-centering": LateralPanel.LANE_CENTERING}[route]
          lateral._set_panel(subpanel)
          checks.append((lateral, "_current_panel", subpanel))
          widget = lateral if route == "lateral" else lateral._panel_widget(subpanel)
        focused_controls = {"longitudinal-pcm": "_pcm_mode", "engine-braking": "_engine_braking", "overshoot": "_cruise_overspeed_allowance"}
        if route in focused_controls:
          widget, scroller = getattr(longitudinal, focused_controls[route]), longitudinal._scroller
    else:
      gui_app.pop_widgets_to(main_layout, instant=True)
      top = main_layout
      if route in ("offroad", "onroad", "developer"):
        widget = main_layout._home_layout if route == "offroad" else main_layout._onroad_layout
        main_layout._scroll_to(widget, smooth=False)
        if route == "developer":
          widget = widget._strip_dev_ui
      else:
        settings_mici = main_layout._settings_layout
        gui_app.push_widget(settings_mici)
        top = settings_mici
        widget = top
        if route in MICI_LONGITUDINAL_INDEX:
          top = settings_mici._device_panel
          gui_app.push_widget(top)
          widget = top._longitudinal_controls[MICI_LONGITUDINAL_INDEX[route]]
          scroller = top._scroller
          if route == "overshoot-selector":
            top = widget = open_read_only_selector(widget, gui_app, ui_state.params)
            scroller = None
        elif route in ("dm", "personality", "lane-centering", "accel-boost"):
          top = settings_mici._toggles_panel
          gui_app.push_widget(top)
          if route == "lane-centering":
            top = top._lane_centering_panel
            gui_app.push_widget(top)
            widget = top._lane_guidance_mode
          elif route == "accel-boost":
            widget = top._accel_boost_toggle
          else:
            widget = dict(top._refresh_toggles)["AlwaysOnDM"] if route == "dm" else top._personality_toggle
          scroller = top._scroller
        else:
          assert route == "settings", f"No native mici route for {route}"
    selected.update(widget=widget, top=top, checks=checks, scroller=scroller, route=route)

  def focus():
    if selected["scroller"] is not None:
      focus_item(selected["scroller"], selected["widget"], horizontal=not big)

  def checkpoint(name):
    assert tuple(ui_state.params.get(key) for key in READ_ONLY_KEYS) == saved_tuning, "Preview changed protected tuning params"
    assert ui_state.started == name.startswith("onroad"), f"Wrong started state for {name}"
    assert gui_app._should_render and not gui_app.widget_in_stack(main_layout._onboarding_window)
    assert gui_app._nav_stack[-1] is selected["top"], f"Wrong navigation stack for {name}"
    for obj, attr, expected in selected["checks"]:
      assert getattr(obj, attr) == expected, f"Native menu rejected {name}: {attr}"
    widget = selected["widget"]
    assert widget.is_visible and widget.rect.width > 0 and widget.rect.height > 0
    x, y = widget.rect.x + widget.rect.width / 2, widget.rect.y + widget.rect.height / 2
    assert 0 <= x <= gui_app.width and 0 <= y <= gui_app.height, f"Requested {name} control is outside the viewport"
    if selected["route"] == "developer":
      assert ui_state.developer_ui == 2, "Right-side developer display is not enabled"
      for service in TELEMETRY_SERVICES:
        assert ui_state.sm.alive[service] and ui_state.sm.valid[service] and ui_state.sm.recv_frame[service] > ui_state.started_frame, service
      assert ui_state.sm["controlsState"].lateralControlState.which() == "pidState"
      assert ui_state.sm["carState"].steeringAngleDeg == 3.5 and ui_state.sm["radarState"].leadOne.dRel == 35.0
    markers["captures"][name] = {
      "frame": gui_app.frame, "started": bool(ui_state.started), "route": selected["route"],
      "widget_class": f"{type(widget).__module__}.{type(widget).__name__}",
    }

  script.set_send(lambda: send_state(False), wait_after=FPS)
  for name in SCENARIOS[device]:
    if name == "onroad":
      if big:
        script.setup(main_layout._set_mode_for_state, wait_after=1)
      else:
        script.setup(lambda: gui_app.pop_widgets_to(main_layout, instant=True), wait_after=1)
      # Real mici transition delay + scrolling; no forcing the onroad state.
      script.set_send(lambda: send_state(True), wait_after=5 * FPS)
    route = name.removeprefix("onroad-")
    script.setup(lambda route=route: navigate(route), wait_after=FPS // 2)
    script.setup(focus, wait_after=FPS // 2)
    script.setup(lambda name=name: checkpoint(name), wait_after=1)
  script.end()
  markers["end_frame"] = script.frame
  assert script.frame <= 30 * FPS, "Preview must remain bounded to 30 seconds of rendered frames"
  return script.entries
