On or around the morning of September 13, 2026, I drove my 2018 Honda Civic Touring running the latest firmware for my 39990-TEG-A010 EPS. I was running the TSFDO Model alongside the handcrafted lateral tuning as a baseline.

Throughout my drive, I drove around 75 total miles which were captured across a few routes today (offroad/onroad cycles) were done mid-drive.

I drove on the following types of roads (%):
-Neighborhood/Local Unmarked Roads (10%)
-4 Lane Divided Highways (US Route 211) (50%)
-2/3 Lane Mountain Pass Painted Roads (US Route 211 through Shenandoah National Park) (40%)

Observations at low and medium speeds (0-50mph):
-Consistent understeer on both left and right switchbacks, creating the illusion torque had ran out even when that was not the case. The sharper the turn, the more understeer there was.
-Steering slightly delayed from optimal output. I could feel this when the curvy sections straightened out and the car did not properly follow the trajectory that would normally have been kept. Not a major delay, but improper actuator delay calculation could also be the cause of the understeer.
-Towards the end of the drive, I accidentally faulted the LKAS by grabbing the wheel too quickly, but this is because it failed to unwind out of a turn onto a new local road.
-Near the very end of my drive, I drove in circles inside of a cul-de-sac in order to gather more steer ratio data at very high angles.
-Steering output was very smooth with stutter or oscillations being pretty much nonexistent. No issues with that.

Attempted Adjustments:
I was briefly adjusting the yaw friction value and the total output added to the controller. I stayed within the 5-10% range since going towards 15% usually results in low frequency oscillations.

Observations at high speeds (50mph+):
While lane centering was active, on sharper or more aggressive highway curves, there was plenty of low-frequency oscillations mid-turn that were not present while driving straight.

Attempted Adjustments:
I changed the Lane-Centering Strength param from 1.0 to 0.3 (0.3 is the default) but it did not fix that behavior. It did make the lane centering strength weaker, but ironically it was both understeering AND oscillations did not go away. So I have very little confidence this is the issue.
I changed the friction applied value (PIF/Torque Blend) from 10% to 5% but it did not appear to make a difference, while still making the rest of the output worse or more delayed.
Logs should demonstrate what the cause was, or which value is the most overtuned.

Other Bugs/Noticeable Issues:
Sometimes, lane changes are too weak to the point where they do not always fully move the car over to the new lane. However, I will refrain from making any adjustments to this until tuning is locked in to a set value since the tune itself can also create this issue.
For the live tuning value PIF/Torque Blend, I noticed that it was not actually taking effect until I turned LKAS off and on again. This caught me off guard since I had to redo some of my tuning after this discovery due to falsely thinking it was live.
All lane centering values are not live either/require offroad to change. Each controller based tuning param, steer ratio param, and lane centering param is supposed to be live and take effect while actually driving just like the rest of the live values. This defeats trying to fix issues in real time.
Nidec PCM long with speed limit assist is broken and the speed limit controller is trying to manually change the PCM speed instead of setting the internal maximum speed to a very high number (80mph or similar) like how it was before. This causes major jerking since Nidecs block out control if the car actually blocks accel commands if too close to the upper limit.
