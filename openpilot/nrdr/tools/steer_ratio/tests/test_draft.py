import csv
import gzip
import hashlib
import json

import pytest

from openpilot.nrdr.tools.steer_ratio.draft import build_draft, main


def rows():
  return [{'fingerprint': 'TEST_CAR', 'eps_firmware': 'EPS_V1', 'vehicle_model_id': 'geometry1',
           'phase': 'steady', 'quality': 'relaxed', 'command_output_available': 'True', 'safety_limited': 'False',
           'angle_deg': angle, 'effective_ratio': ratio, 'timestamp': second + .1, 'speed_mps': 12,
           'route_id': route, 'direction': direction, 'software_id': 'config1'}
          for route in ('route1', 'route2') for direction in ('left', 'right')
          for second in range(3) for angle, ratio in ((3, 16), (8, 15))]


def build(samples):
  return build_draft(samples, 'TEST_CAR', 'EPS_V1')


def test_draft_keeps_observed_anchors_and_labels_unmeasured_extensions():
  result = build(rows())
  assert result['angles_deg'] == [0, 3, 8]
  assert result['ratios'] == [16, 16, 15]
  assert result['ratio_domain'] == 'vehicle-model'
  assert result['anchors'][0]['evidence'] == 'held-nearest-anchor-not-measured-at-zero'
  assert all(anchor['evidence'] == 'provisional-command-conditioned' for anchor in result['anchors'][1:])
  assert result['coverage'][0]['routes'] == 2
  assert result['coverage'][0]['paired_routes'] == 2
  assert result['coverage'][0]['occupied_seconds'] == 12
  assert result['coverage'][0]['observations'][0]['configurations'][0]['software'] == 'config1'
  assert 'unmeasured extrapolation' in result['outside_range']


@pytest.mark.parametrize('key,value', [('fingerprint', 'OTHER'), ('eps_firmware', 'EPS_V2'),
                                     ('phase', 'transient'), ('quality', 'experimental'),
                                     ('command_output_available', 'False'), ('safety_limited', 'True'),
                                     ('vehicle_model_id', 'unknown'), ('software_id', 'unknown'),
                                     ('route_id', ''), ('direction', 'unknown'),
                                     ('effective_ratio', float('nan')), ('effective_ratio', 26),
                                     ('angle_deg', -1), ('angle_deg', 450), ('speed_mps', 0), ('timestamp', '')])
def test_other_vehicles_and_unsupported_samples_never_change_anchors(key, value):
  original = rows()
  contaminated = [dict(row, **{key: value}) for row in original]
  result = build(original + contaminated)
  assert result['angles_deg'] == [0, 3, 8]
  assert result['ratios'] == [16, 16, 15]
  assert sum(result['rejected_samples'].values()) == len(contaminated)


def test_geometry_mixtures_are_rejected_not_averaged():
  with pytest.raises(ValueError, match='one known vehicle-model'):
    build(rows() + [dict(row, vehicle_model_id='geometry2') for row in rows()])


def test_route_and_direction_coverage_required():
  with pytest.raises(ValueError, match='fewer than two'):
    build([row for row in rows() if row['route_id'] == 'route1'])
  with pytest.raises(ValueError, match='fewer than two'):
    build([row for row in rows() if row['direction'] == 'left'])


def test_one_large_angle_observation_does_not_become_an_anchor():
  result = build(rows() + [dict(rows()[0], angle_deg=120)])
  assert result['angles_deg'] == [0, 3, 8]
  assert result['coverage'][-1]['used'] is False
  assert result['coverage'][-1]['occupied_seconds'] == 1


def test_repeated_frames_do_not_increase_support_or_reweight_routes():
  samples = rows()
  varied = [dict(row, effective_ratio=row['effective_ratio'] + (0.4 if row['route_id'] == 'route1' else 0)) for row in samples]
  dense = varied + [row for row in varied if row['route_id'] == 'route1'] * 50
  assert build(dense)['ratios'] == build(varied)['ratios']
  assert build(dense)['coverage'][0]['occupied_seconds'] == build(varied)['coverage'][0]['occupied_seconds']


def test_configurations_are_balanced_within_route_direction():
  samples = rows()
  new_config = [dict(row, software_id='config2', effective_ratio=row['effective_ratio'] + 1) for row in samples]
  extended = [dict(row, timestamp=row['timestamp'] + second) for second in range(10, 20) for row in new_config]
  assert build(samples + extended)['ratios'] == [16.5, 16.5, 15.5]


def test_wide_route_disagreement_is_retained_but_not_used():
  samples = [dict(row, effective_ratio=20 if row['route_id'] == 'route1' else 12) for row in rows()]
  with pytest.raises(ValueError, match='fewer than two'):
    build(samples)


def test_draft_rejects_reversed_angle_to_curvature_mapping():
  samples = [dict(row, effective_ratio=8 if row['angle_deg'] == 3 else 25) for row in rows()]
  with pytest.raises(ValueError, match='reverse the angle-to-curvature mapping'):
    build(samples)


@pytest.mark.parametrize('kwargs', [{'fingerprint': 'unknown'}, {'eps_firmware': ''}, {'min_routes': 1}, {'min_seconds': 0}])
def test_invalid_fit_configuration_is_rejected(kwargs):
  with pytest.raises(ValueError):
    build_draft(rows(), **({'fingerprint': 'TEST_CAR', 'eps_firmware': 'EPS_V1'} | kwargs))


def test_cli_records_hash_and_refuses_overwrite(tmp_path):
  samples, output = tmp_path / 'samples.csv.gz', tmp_path / 'draft.json'
  with gzip.open(samples, 'wt', newline='', encoding='utf-8') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows()[0]))
    writer.writeheader()
    writer.writerows(rows())
  args = [str(samples), '--fingerprint', 'TEST_CAR', '--eps-firmware', 'EPS_V1', '--output', str(output)]
  assert main(args) == 0
  contents = output.read_bytes()
  result = json.loads(contents)
  assert result['source_sha256'] == hashlib.sha256(samples.read_bytes()).hexdigest()
  with pytest.raises(FileExistsError):
    main(args)
  assert output.read_bytes() == contents
