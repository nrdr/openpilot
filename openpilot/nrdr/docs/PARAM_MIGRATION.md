# nrdr Param Migration

## The rule
openpilot `Params.get()` raises `UnknownKeyName` on a key that is not in the
compiled `params_keys.h` — it does **not** return `None`. Any code path that
reads a key absent from the registry crashes the process: the card dies on
engage and crash-loops (LKAS faults, "car unrecognized", disengage-yell-recover).

## Removing a param key — two phase, across releases
1. **Release N:** delete every reader. **Keep the key registered** in
   `params_keys.h`.
2. **Release N+1**, after the fleet has updated past N: delete the key from
   `params_keys.h`.

Never remove the readers and the key in the same release for a compiled / OTA
fleet. A device with stale `.pyc` or a half-applied update runs an old reader
against the new registry and crashes. The registry entry is the safety net that
spans the update window.

## Reading a param — always
Route through the hardened helpers `get_param_bool` / `get_param_float`
(`latcontrol_pid.py`, Honda `carcontroller.py`). They catch `UnknownKeyName`
and return the default. Never call `params.get*()` on an nrdr/Honda key raw in a
hot path.

## 2026-07 notch incident
`HondaNotchEnabled` / `HondaNotchFreq` / `HondaNotchQ` were removed from
`params_keys.h` in the same change that removed their readers. Stale `.pyc` on
updating devices kept old readers alive → `UnknownKeyName` → card crash-loop on
`nrdr-nightly`. Fix: re-registered the three keys as deprecated and hardened the
read helpers. The keys stay registered until a later release, then get deleted
per the two-phase rule above.
