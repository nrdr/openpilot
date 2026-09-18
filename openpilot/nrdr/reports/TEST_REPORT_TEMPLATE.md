# Test Report: [Vehicle] - [YYYY-MM-DD]

Copy this file into the same folder as `[Vehicle]-Report-[YYYY-MM-DD].md`. Keep notes short; use `Unknown`, `N/A`, `None`, or `Not tested` instead of guessing or leaving fields blank. Tester name and suspected causes are optional.

Complete the report after the drive. Do not operate settings or take notes while driving, or deliberately provoke faults to fill out this template.

## Drive Setup

- Tester / handle (optional):
- Date, approximate time, and time zone:
- Vehicle (year, make, model, trim):
- Comma device:
- Branch, exact commit, and build date (not just "latest"):
- Driving model name and version / hash, if available:
- EPS part number and firmware version / modification, if known:
- Lateral controller and baseline tune / preset:
- Longitudinal control mode (stock / PCM or openpilot) and relevant assists:
- Starting settings or settings screenshot (include relevant steer-ratio source/value, actuator delay, friction/blend, and lane-centering values; preserve units):

## Roads & Conditions

- Total distance (miles or km):
- Road types and approximate percentages (total 100%):
  - Local / unmarked roads:
  - Divided highways:
  - Mountain / winding roads:
  - Other:
- Weather, visibility, and road surface (dry/wet, smooth/rough, etc.):
- Relevant vehicle conditions (tire or alignment changes, unusual load, etc.):
- Number of routes / sessions; any mid-drive offroad/onroad cycles or reboots:

## Driving Observations

Use one bullet per observation. Include speed and units, straight vs. curve, left vs. right, expected vs. actual behavior, and how often it happened. Give issues a short label (e.g., `A: left-turn understeer`) to match with logs below. Describe what worked well, too.

### Low / Medium Speeds: [range and units]

- [Observation, or Not tested]

### High Speeds: [range and units, or Not tested]

- [Observation, or Not tested]

## Adjustments & Results

Write `None` if unchanged. Otherwise, repeat this block for each change; note any settings changed together.

- Setting name and value before -> after (include units):
- Related observation / issue label:
- When it took effect (immediately, after LKAS re-engagement, offroad cycle, reboot, or unknown) and how you confirmed it:
- Result (better / worse / unchanged / unclear) and any trade-offs:
- Route / timestamp for the before-and-after comparison:

## Other Issues & Driver Interventions

- Issue label and description (lane changes, longitudinal behavior, settings/UI, alerts, etc.):
- Conditions, frequency, and driver action needed; include exact alert text if available:

## Logs & Timestamps

Repeat per event, including relevant segments from each route if the drive spans multiple sessions. Do not publish credentials or sensitive location details; share private logs with maintainers separately when needed.

- Issue / adjustment label:
- Route ID or log link, plus segment if known:
- Event time (elapsed time within the route, or clock time with time zone; specify which):
- Screenshot / clip link, if available:
- Logs uploaded / available / pending / unavailable:

## Suspected Causes (Optional)

- Keep hypotheses separate from observed behavior; note whether logs have actually been reviewed.
