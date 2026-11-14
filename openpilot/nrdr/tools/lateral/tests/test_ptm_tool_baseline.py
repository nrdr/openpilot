"""Focused checks for offline PTM tools; no Params writes or controller execution."""
import contextlib
import io
import inspect
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from openpilot.cereal import log
from openpilot.nrdr.features.lateral.honda_vgr import ptm_inverse
from openpilot.nrdr.tools.lateral import eps_common, eps_fit_rack_map, eps_fit_yaw_scale, eps_report


class TestPtmToolBaseline(unittest.TestCase):
  def test_sampled_inverse_matches_controller_baseline(self):
    for profile in eps_common.HONDA_VGR_PROFILES:
      for got, expected in zip(eps_common.vgr_inverse(profile), ptm_inverse(profile), strict=True):
        np.testing.assert_array_equal(got, expected)

  def test_prediction_schedule_uses_selected_calibration(self):
    profile = SimpleNamespace(calibration='civic_bosch_c020', prediction_schedule=True)
    self.assertEqual(eps_common.prediction_schedule(profile)[1], (.28, .28, .28, .26, .26))
    profile.calibration = 'clarity_a020'
    self.assertEqual(eps_common.prediction_schedule(profile)[1], (.15, .08, .10, .20, .30))
    self.assertIsNone(eps_common.prediction_schedule(None))

  def test_report_uses_ptm_rack_interpolation(self):
    rack = eps_common.rack_map('HONDA_CLARITY', '39990-TRW,A020', 16.5)
    self.assertTrue(rack.ptm_baseline)
    self.assertEqual(rack.table.ratio_v[0], 17.34)

  def test_offline_rdx_yaw_baseline(self):
    self.assertEqual(eps_common.YAW_RATE_CALIBRATION['ACURA_RDX_3G'], (.2511, 512.3, -.20))

  def test_donor_road_curve_loading_and_prediction(self):
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp)/'honda_lateral_common.py'
      path.write_text("BP = [0., 100.]\nV = [18., 16.]\nHONDA_SR_CURVE_BY_FP = {'HONDA_CLARITY': (BP, V)}\n")
      curve = eps_fit_rack_map.road_curves(path)['HONDA_CLARITY']
    fit = eps_fit_rack_map.Fit(([0., 100.], [0., 100.]), 2.75)
    data = np.array([[10., 50., 0., .01]])
    expected = (np.radians(50.)/(17.*2.75) + 9.81*(-.00061)*.01)/(1.+.00061*100.)
    self.assertAlmostEqual(fit.predict_curve(data, curve)[0], expected)

  def test_yaw_no_pairs_reports_insufficient_data(self):
    with patch.object(eps_fit_yaw_scale, 'read_route', return_value=([], [], [])), \
         patch.object(eps_fit_yaw_scale, 'pairs', return_value=(512., np.empty((0, 3)))), \
         patch('sys.argv', ['tool', '--bus', '0', 'empty']), contextlib.redirect_stdout(io.StringIO()):
      with self.assertRaisesRegex(SystemExit, 'no straight-to-straight GPS pairs'):
        eps_fit_yaw_scale.main()

  def test_contiguous_yaw_time_axis_preserves_donor_pairs(self):
    t = np.arange(6000)*.01
    counts = np.where((t>=10.) & (t<20.), 36., 0.)
    Y = np.c_[t, 512.+counts]
    V = np.c_[t, np.where(t<5., 0., 10.)]
    gt = np.arange(60.)
    heading = np.interp(gt-.4, t, np.cumsum(counts)*.0025)
    G = np.c_[gt, heading, np.full(60,10.), np.ones(60)]
    source = inspect.getsource(eps_fit_yaw_scale.pairs).replace('np.ascontiguousarray(Y[:, 0])', 'Y[:, 0]')
    scope = {'np':np, 'RIGHT_LOSS_BP':eps_common.RIGHT_LOSS_BP, 'GPS_LAG':.4}
    exec(source, scope)
    expected_zero, expected = scope['pairs'](Y,G,V)
    zero, actual = eps_fit_yaw_scale.pairs(Y,G,V)
    self.assertGreater(len(actual), 10)
    self.assertEqual(zero, expected_zero)
    np.testing.assert_array_equal(actual, expected)

  def test_report_reads_command_delay_from_nrdr_telemetry(self):
    event = log.Event.new_message(logMonoTime=1_000_000_000)
    state = event.init('controlsState').lateralControlState.init('pidState')
    state.epsFfActive = True
    state.commandDelay = .2
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp)/'rlog'
      path.write_bytes(event.to_bytes())
      rows, _ = eps_report.read([str(path)])
    self.assertAlmostEqual(rows['cmd'][0, 1], .2, places=6)

  def test_report_subtracts_logged_command_delay_only(self):
    n = 700
    s = {'t':np.arange(n)*.01, 'v':np.full(n, 7.), 'k':np.full(n, .01),
         'ok':np.ones(n,dtype=bool), 'bl':np.zeros(n), 'cmd':np.full(n,.2)}
    model = np.c_[s['t'], s['k']]
    for delay, expected in ((.2, 'on-time 0.16 s'), (np.nan, 'on-time 0.36 s')):
      s['cmd'][:] = delay
      output = io.StringIO()
      with patch.object(eps_report, 'best_lag', return_value=.4), \
           patch.object(eps_report, 'shipped_delay_schedule', return_value=([3.,12.],[.1,.1])), \
           contextlib.redirect_stdout(output):
        eps_report.timing(s, model, {})
      self.assertIn(expected, output.getvalue())
      if np.isnan(delay):
        self.assertIn('command delay not logged, not subtracted', output.getvalue())

  def test_report_compares_schedule_at_sampled_speeds(self):
    n = 700
    s = {'t':np.arange(n)*.01, 'v':np.full(n, 16.), 'k':np.full(n, .01),
         'ok':np.ones(n,dtype=bool), 'bl':np.zeros(n), 'cmd':np.full(n,.1)}
    output = io.StringIO()
    with patch.object(eps_report, 'best_lag', return_value=.28), \
         patch.object(eps_report, 'shipped_delay_schedule', return_value=([12.,20.],[.1,.2])), \
         contextlib.redirect_stdout(output):
      eps_report.timing(s, np.c_[s['t'],s['k']], {})
    self.assertIn('schedule 0.15 s', output.getvalue())
    self.assertNotIn('schedule 0.20 s', output.getvalue())


if __name__ == '__main__':
  unittest.main()
