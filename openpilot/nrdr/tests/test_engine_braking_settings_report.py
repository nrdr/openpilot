from types import SimpleNamespace as NS

from openpilot.nrdr.features.longitudinal.engine_braking import EngineBrakeSettingsReporter


def test_reports_first_consumed_choice_and_changes_not_every_frame():
  reports = []
  live = NS(record_applied_settings=lambda *args, **kwargs: reports.append((args, kwargs)))
  reporter = EngineBrakeSettingsReporter()
  for generation in range(100):
    reporter.update(live, generation, enabled=True, allowance_mph=5, supported=True)
  reporter.update(live, 100, enabled=False, allowance_mph=5, supported=True)
  reporter.update(live, 101, enabled=False, allowance_mph=10, supported=True)
  reporter.update(live, 102, enabled=False, allowance_mph=10, supported=False)
  assert len(reports) == 4
  assert reports[0] == (('pcm_engine_braking', 0),
                        {'configured_enabled': True, 'allowance_mph': 5, 'supported': True})
  assert reports[1][1]['configured_enabled'] is False
  assert reports[2][1]['allowance_mph'] == 10
  assert reports[3][1]['supported'] is False


def test_diagnostic_failure_does_not_propagate_or_mutate_setting():
  calls = []

  def fail(*args, **kwargs):
    calls.append(args)
    raise OSError('diagnostic unavailable')

  live = NS(record_applied_settings=fail)
  reporter = EngineBrakeSettingsReporter()
  for _ in range(10):
    reporter.update(live, 1, enabled=True, allowance_mph=5, supported=True)
  assert len(calls) == 1
  assert reporter.last == (True, 5, True)
