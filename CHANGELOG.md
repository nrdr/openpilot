# nrdr — Release Notes

User-facing notes per release. For the deep technical log (params, files, root causes), see `NRDR_CHANGELOG.md`.

---

## 2026-06-12 — The everything update

-Force Update now does the real thing: one press and the device checks, downloads, installs and reboots itself with zero extra presses. The old sync script that choked on parameter changes is gone for good.
-Tune Report made it to the UI like promised: it lives at the top of Lateral Tuning with Scan and View buttons, and it now opens with a Tuning Score out of 10 plus plain-English findings ("scored 8 out of 10, with the most error on left turns at 42 mph - logs show PID values might be undertuned at this speed") and suggestions that name the exact slider to move. The advanced per-speed tables are still underneath for the data people.
-PID Tune Information sits right below it - one tap shows the kp/ki/kf values your car is actually running based on its fingerprint, plus steer ratio, actuator delay and geometry.
-Keep Feedforward Static is now split into separate lateral and longitudinal toggles (both default ON), so raising a PID scale boosts error correction only and never inflates the feedforward with it.
-Center Scale is now Center Boost, shown as a percentage so it actually makes sense (50% instead of 0.50). All the speed interp logic is gone - one static value across every speed - and a new Center Boost Threshold slider lets you decide exactly how centered the wheel needs to be before the boost is active.
-Driver Override Threshold is now a slider (1200 = Honda stock; on cars with a different stock threshold your value applies proportionally so 1200 always means stock). The old override tolerance toggle is renamed to Hysteresis and now defaults OFF.
-Minimum Steer Speed slider at the bottom of Lateral Tuning (default 0 = stock): below your chosen speed, no steering torque is commanded at all - for those who don't want the wheel moving at a standstill.
-Party Tricks is now called "Special". The Alternative Dashboard is split into two independent designs: Speed (stock / lead speed / GPS speed / cluster speed in your set-speed slot, always whole mph) and Distance (stock / radar bars that close in with the lead / velocity bars that push out under acceleration). Non-stock designs now stay on the cluster permanently with the mini car and lead icon lit - not just while engaged.
-NEW Cruise Button Sub-Mode (the Dynamic HUD): pressing the distance button or set/resume first wakes a preview on your real dashboard - the bars light up with your CURRENT personality (parked or driving, any design) and your set speed shows if cruise is engaged, all blinking. Only presses made during the preview actually change anything. The window is adjustable from 5 to 60 seconds and the blink starts lazy and accelerates continuously until it falls off, so you always know how much time is left.
-NEW Show Footage (in Special): pick a drive, get a QR code on the device screen, scan it with any phone on the device hotspot and watch the recorded video right there. Built for the roadside "can I see the footage?" moment - no laptop, no SSH, no cloud. The file server now defaults ON to support this.
-NEW Clear Dashboard Fault Codes (default ON, in Special): the cluster fault clearing that used to be hardcoded is now a toggle, so nobody is forced into it - turn it OFF and you get full stock behavior back including the FCW chime. And for dead-camera cars: the "Auto High Beam System Problem" mystery is finally solved. There was never a code to clear - the cluster raises it when the camera's own broadcast message times out. A new Spoof Camera Messages toggle keeps that message alive and the fault never appears.
-The home screen now shows the device's IP address instead of the old joke line, so SSH and footage access are always one glance away.
-Sunnylink got real attention: the econ 4th personality finally shows on the website, both dashboard designs are proper dropdowns, and there's a new Remote Actions panel - you can fire Force Update or a Tune Report scan from the website and watch the status and score summary come back, from anywhere the device has signal.
-AGNOS is now per-device: comma 4 runs 18.4, the C3X runs 18.3 (comma's real C3X images - same firmware as 18.4 with the correct system), and the C3 keeps its own lane. One branch serves all three safely, and the AGNOS 18.x build issues (fonts, loggerd) are fixed.
-Builds now push three branches every run: the dated staging branch, nrdr-nightly (always the latest), and nrdr-clean - a single clean commit that uploads to comma's servers with none of the konik-specific changes, for anyone who wants the features without leaving the stock ecosystem. The device also reboots itself after every build, which kills the corrupted "ghost install" state for good.

Upcoming areas of focus:

-First real-car shakedown of the Dynamic HUD
-On-device footage playback (the QR flow is step one)
-Hunting the 12-14 mph tune spike with the new scored Tune Report

---

## 2026-06-09

-Tune Report over SSH which I'm currently optimizing to find errors in our tune; you can run it against your drives to find out how closely the tune followed the model's plan. UI and Sunnylink versions coming soon.
-4th economy personality has been added, so 4 bars instead of 3. With it comes an even larger following distance and more soft jerk limits.
-All of my default settings are applied even after a factory reset, and an option to download my default preferred model and OSM maps appears on any fresh installation. Training and Sunnylink are auto-completed every time.
-PID Tune Scale is now alongside the same 3 speed ranges that the Low Pass Filter can be tuned, side by side so you can see each one.
-Party Tricks added: injection testing (see the max torque available from your car with a press of a button) and dashboard mini-HUD designs - render the lead car speed or your own GPS speed to your dashboard, with lead animations that change with distance.
-All menu elements consolidated into 5 sub menus which are easy to understand and intuitive.
-Time to install from a complete factory reset is insanely low compared to 6 months ago: up and running in under 5 minutes with all settings configured.

---

## Earlier

The February-through-May arc (live tuning system, LPF/notch filters, unwind logic, learned-param controls, the module era) is documented in `NRDR_CHANGELOG.md`.
