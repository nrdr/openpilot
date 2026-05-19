Flash your Honda EPS using a Comma device!

Credit goes to mmmorks for designing the scripts. Connectivity to Comma servers has been disabled on this branch.



* Simply install this branch: installer.comma.ai/nrdr/rwd-flasher-2026
* Perform the 1GB AGNOS update if needed (this is an older branch).
* After it compiles, simply connect to your device over SSH.



To flash your car:
* Make sure your Comma Power is connected to the OBD2 port.
* Run pfkill -f openpilot over SSH with the car OFF.
* Turn the car into full accessory mode (ON) but keep the engine off. Turn off the A/C to avoid wasting battery.
* Run python eps-update.py REPLACE_WITH_YOUR_FIRMWARE -b 1
* When you see that it aborts before peforming mutating actions, this is your key that it's ready.
* After you are fully commited and ready to flash, run python eps-update.py REPLACE_WITH_YOUR_FIRMWARE -b 1 --skip-checksum --danger 

* An example command would look like: python eps-update.py 39990-TXM-A040-linear-max.rwd --skip-checksum --danger
* Wait for the flashing process to take place, you will see errors on your dash as this happens.
* When fully completed, turn the car completely off. You are done! Then factory reset the device.

Additional Notes:
* To check to see if the flash worked, turn the car back on and move the wheel yourself. If you have any power steering at all, the flash was a sucess.
* If the worst happens and you crash halfway through the flash, do not worry - your EPS is not bricked. You will not have any power steering assist until it is done properly, however. You can easily run the same commands again and may need to power cycle the car/device a few times before being allowed to redo a failed flash.
