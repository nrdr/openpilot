#pragma once

#include <string>
#include <unordered_map>

#include "openpilot/cereal/gen/cpp/log.capnp.h"

inline static std::unordered_map<std::string, ParamKeyAttributes> keys = {
    {"AccessToken", {CLEAR_ON_MANAGER_START | DONT_LOG, STRING}},
    {"AdbEnabled", {PERSISTENT | BACKUP, BOOL}},
    {"AlwaysOnDM", {PERSISTENT | BACKUP, BOOL}},
    {"ApiCache_Device", {PERSISTENT, STRING}},
    {"ApiCache_FirehoseStats", {PERSISTENT, JSON}},
    {"AssistNowToken", {PERSISTENT, STRING}},
    {"AthenadPid", {PERSISTENT, INT}},
    {"AthenadUploadQueue", {PERSISTENT, JSON}},
    {"AthenadRecentlyViewedRoutes", {PERSISTENT, STRING}},
    {"BootCount", {PERSISTENT, INT}},
    {"CalibrationParams", {PERSISTENT, BYTES}},
    {"CameraDebugExpGain", {CLEAR_ON_MANAGER_START, STRING}},
    {"CameraDebugExpTime", {CLEAR_ON_MANAGER_START, STRING}},
    {"CarBatteryCapacity", {PERSISTENT, INT}},
    {"CarParams", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BYTES}},
    {"CarParamsCache", {CLEAR_ON_MANAGER_START, BYTES}},
    {"CarParamsPersistent", {PERSISTENT, BYTES}},
    {"CarParamsPrevRoute", {PERSISTENT, BYTES}},
    {"CompletedTrainingVersion", {PERSISTENT, STRING, "0"}},
    {"ControlsReady", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BOOL}},
    {"CurrentBootlog", {PERSISTENT, STRING}},
    {"CurrentRoute", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, STRING}},
    {"DisableLogging", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BOOL}},
    {"DisablePowerDown", {PERSISTENT | BACKUP, BOOL}},
    {"DisableUpdates", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"DisengageOnAccelerator", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"DongleId", {PERSISTENT, STRING}},
    {"DoReboot", {CLEAR_ON_MANAGER_START, BOOL}},
    {"DoShutdown", {CLEAR_ON_MANAGER_START, BOOL}},
    {"DoUninstall", {CLEAR_ON_MANAGER_START, BOOL}},
    {"DriverTooDistracted", {CLEAR_ON_MANAGER_START | CLEAR_ON_IGNITION_ON, BOOL}},
    {"DriverLockoutCount", {CLEAR_ON_MANAGER_START | CLEAR_ON_IGNITION_ON, INT, "0"}},
    {"AlphaLongitudinalEnabled", {PERSISTENT | DEVELOPMENT_ONLY | BACKUP, BOOL}},
    {"ExperimentalMode", {PERSISTENT | BACKUP, BOOL}},
    {"ExperimentalModeConfirmed", {PERSISTENT | BACKUP, BOOL}},
    {"FirmwareQueryDone", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BOOL}},
    {"ForcePowerDown", {PERSISTENT, BOOL}},
    {"GitBranch", {PERSISTENT, STRING}},
    {"GitCommit", {PERSISTENT, STRING}},
    {"GitCommitDate", {PERSISTENT, STRING}},
    {"GitDiff", {PERSISTENT, STRING}},
    {"GithubSshKeys", {PERSISTENT | BACKUP, STRING}},
    {"GithubUsername", {PERSISTENT | BACKUP, STRING}},
    {"GitRemote", {PERSISTENT, STRING}},
    {"GsmApn", {PERSISTENT | BACKUP, STRING}},
    {"GsmMetered", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"GsmRoaming", {PERSISTENT | BACKUP, BOOL}},
    {"HardwareSerial", {PERSISTENT, STRING}},
    {"HasAcceptedTerms", {PERSISTENT, STRING, "0"}},
    {"HondaGasFactorParams", {PERSISTENT, FLOAT}},
    {"HondaWindFactorParams", {PERSISTENT, FLOAT}},
    {"InstallDate", {PERSISTENT, TIME}},
    {"IsDriverViewEnabled", {CLEAR_ON_MANAGER_START, BOOL}},
    {"IsEngaged", {PERSISTENT, BOOL}},
    {"IsLdwEnabled", {PERSISTENT | BACKUP, BOOL}},
    {"IsLiveStreaming", {CLEAR_ON_MANAGER_START, BOOL}},
    {"IsMetric", {PERSISTENT | BACKUP, BOOL}},
    {"IsOffroad", {CLEAR_ON_MANAGER_START, BOOL}},
    {"IsRhdDetected", {PERSISTENT, BOOL}},
    {"IsReleaseBranch", {CLEAR_ON_MANAGER_START, BOOL}},
    {"IsTestedBranch", {CLEAR_ON_MANAGER_START, BOOL}},
    {"JoystickDebugMode", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL}},
    {"LanguageSetting", {PERSISTENT | BACKUP, STRING, "en"}},
    {"LastAthenaPingTime", {CLEAR_ON_MANAGER_START, INT}},
    {"LastGPSPosition", {PERSISTENT, STRING}},
    {"LastManagerExitReason", {CLEAR_ON_MANAGER_START, STRING}},
    {"LastOffroadStatusPacket", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, JSON}},
    {"LastAgnosPowerMonitorShutdown", {CLEAR_ON_MANAGER_START, STRING}},
    {"LastPowerDropDetected", {CLEAR_ON_MANAGER_START, STRING}},
    {"LastUpdateException", {CLEAR_ON_MANAGER_START, STRING}},
    {"LastUpdateRouteCount", {PERSISTENT, INT, "0"}},
    {"LastUpdateTime", {PERSISTENT, TIME}},
    {"LastUpdateUptimeOnroad", {PERSISTENT, FLOAT, "0.0"}},
    {"LiveDelay", {PERSISTENT | BACKUP, BYTES}},
    {"LiveParameters", {PERSISTENT, JSON}},
    {"LiveParametersV2", {PERSISTENT, BYTES}},
    {"LivestreamEncoderBitrate", {CLEAR_ON_MANAGER_START | DONT_LOG, INT}},
    {"LivestreamRequestKeyframe", {CLEAR_ON_MANAGER_START | DONT_LOG, BOOL}},
    {"LiveTorqueParameters", {PERSISTENT | DONT_LOG, BYTES}},
    {"LocationFilterInitialState", {PERSISTENT, BYTES}},
    {"LateralManeuverMode", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL}},
    {"LongitudinalManeuverMode", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL}},
    {"LongitudinalPersonality", {PERSISTENT | BACKUP, INT, std::to_string(static_cast<int>(cereal::LongitudinalPersonality::STANDARD))}},
    {"NetworkMetered", {PERSISTENT | BACKUP, BOOL}},
    {"ObdMultiplexingChanged", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BOOL}},
    {"ObdMultiplexingEnabled", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BOOL}},
    {"Offroad_CarUnrecognized", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, JSON}},
    {"Offroad_ConnectivityNeeded", {CLEAR_ON_MANAGER_START, JSON}},
    {"Offroad_ConnectivityNeededPrompt", {CLEAR_ON_MANAGER_START, JSON}},
    {"Offroad_ExcessiveActuation", {PERSISTENT, JSON}},
    {"Offroad_NeosUpdate", {CLEAR_ON_MANAGER_START, JSON}},
    {"Offroad_NoFirmware", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, JSON}},
    {"Offroad_Recalibration", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, JSON}},
    {"Offroad_TemperatureTooHigh", {CLEAR_ON_MANAGER_START, JSON}},
    {"Offroad_UnregisteredHardware", {CLEAR_ON_MANAGER_START, JSON}},
    {"Offroad_UpdateFailed", {CLEAR_ON_MANAGER_START, JSON}},
    {"Offroad_DriverMonitoringUncertain", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, JSON}},
    {"OnroadCycleRequested", {CLEAR_ON_MANAGER_START, BOOL}},
    {"OpenpilotEnabledToggle", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"PandaHeartbeatLost", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL}},
    {"PrimeType", {PERSISTENT, INT}},
    {"RecordAudio", {PERSISTENT | BACKUP, BOOL}},
    {"RecordAudioFeedback", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"RecordFront", {PERSISTENT | BACKUP, BOOL}},
    {"RecordFrontLock", {PERSISTENT, BOOL}},  // for the internal fleet
    {"RemoteAccessPinEnabled", {PERSISTENT, BOOL}},  // opt-in PIN gate for Live View + Remote SSH (unset/false = open)
    {"RemoteAccessPinSalt", {PERSISTENT | DONT_LOG, BYTES}},
    {"RemoteAccessPinHash", {PERSISTENT | DONT_LOG, BYTES}},
    {"RemoteAccessPinIterations", {PERSISTENT, INT, "150000"}},
    {"LiveViewEnabled", {PERSISTENT | BACKUP, BOOL, "1"}},  // on by default; owner-only (portal requires the user's own login)
    {"LiveView", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL}},  // streamer sets this while a session is active
    {"SecOCKey", {PERSISTENT | DONT_LOG | BACKUP, STRING}},
    {"ShowDebugInfo", {PERSISTENT, BOOL}},
    {"RouteCount", {PERSISTENT, INT, "0"}},
    {"SnoozeUpdate", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL}},
    {"SshEnabled", {PERSISTENT | BACKUP, BOOL}},
    {"TermsVersion", {PERSISTENT, STRING}},
    {"TorqueBar", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"TrainingVersion", {PERSISTENT, STRING}},
    {"UbloxAvailable", {PERSISTENT, BOOL}},
    {"UpdateAvailable", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BOOL}},
    {"UpdateFailedCount", {CLEAR_ON_MANAGER_START, INT}},
    {"UpdaterAvailableBranches", {PERSISTENT, STRING}},
    {"UpdaterCurrentDescription", {CLEAR_ON_MANAGER_START, STRING}},
    {"UpdaterCurrentReleaseNotes", {CLEAR_ON_MANAGER_START, BYTES}},
    {"UpdaterFetchAvailable", {CLEAR_ON_MANAGER_START, BOOL}},
    {"UpdaterNewDescription", {CLEAR_ON_MANAGER_START, STRING}},
    {"UpdaterNewReleaseNotes", {CLEAR_ON_MANAGER_START, BYTES}},
    {"UpdaterState", {CLEAR_ON_MANAGER_START, STRING}},
    {"UpdaterTargetBranch", {CLEAR_ON_MANAGER_START, STRING}},
    {"UpdaterLastFetchTime", {PERSISTENT, TIME}},
    {"UptimeOffroad", {PERSISTENT, FLOAT, "0.0"}},
    {"UptimeOnroad", {PERSISTENT, FLOAT, "0.0"}},
    {"UsbGpuPresent", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL}},
    {"UsbGpuCompiled", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL}},
    {"Version", {PERSISTENT, STRING}},

    // --- sunnypilot params --- //
    {"ApiCache_DriveStats", {PERSISTENT, JSON}},
    {"AutoLaneChangeBsmDelay", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"AutoLaneChangeTimer", {PERSISTENT | BACKUP, INT, "0"}},
    {"BlinkerLateralReengageDelay", {PERSISTENT | BACKUP, INT, "0"}},  // seconds
    {"BlinkerMinLateralControlSpeed", {PERSISTENT | BACKUP, INT, "20"}},  // MPH or km/h
    {"BlinkerPauseLateralControl", {PERSISTENT | BACKUP, INT, "0"}},
    {"Brightness", {PERSISTENT | BACKUP, INT, "0"}},
    {"CarList", {PERSISTENT, JSON}},
    {"CarParamsSP", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, BYTES}},
    {"CarParamsSPCache", {CLEAR_ON_MANAGER_START, BYTES}},
    {"CarParamsSPPersistent", {PERSISTENT, BYTES}},
    {"CarPlatformBundle", {PERSISTENT | BACKUP, JSON}},
    {"ChevronInfo", {PERSISTENT | BACKUP, INT, "4"}},
    {"CompletedSunnylinkConsentVersion", {PERSISTENT, STRING, "0"}},
    {"CustomAccIncrementsEnabled", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"CustomAccLongPressIncrement", {PERSISTENT | BACKUP, INT, "5"}},
    {"CustomAccShortPressIncrement", {PERSISTENT | BACKUP, INT, "1"}},
    {"DeviceBootMode", {PERSISTENT | BACKUP, INT, "0"}},
    {"DevUIInfo", {PERSISTENT | BACKUP, INT, "0"}},
    {"EnableCopyparty", {PERSISTENT | BACKUP, BOOL}},
    {"EnableGithubRunner", {PERSISTENT | BACKUP, BOOL}},
    {"GreenLightAlert", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"GithubRunnerSufficientVoltage", {CLEAR_ON_MANAGER_START , BOOL}},
    {"HasAcceptedTermsSP", {PERSISTENT, STRING, "0"}},
    {"HideVEgoUI", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"IntelligentCruiseButtonManagement", {PERSISTENT | BACKUP , BOOL}},
    {"InteractivityTimeout", {PERSISTENT | BACKUP, INT, "0"}},
    {"IsDevelopmentBranch", {CLEAR_ON_MANAGER_START, BOOL}},
    {"IsReleaseSpBranch", {CLEAR_ON_MANAGER_START, BOOL}},
    {"LaneCentering", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"LaneCenteringE2EAuthority", {PERSISTENT | BACKUP, FLOAT, "1.0"}},
    {"LaneCenteringPauseOnSignal", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"LaneCenterOffset", {PERSISTENT | BACKUP, FLOAT, "0.0"}},
    {"LastGPSPositionLLK", {PERSISTENT, STRING}},
    {"LeadDepartAlert", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"MaxTimeOffroad", {PERSISTENT | BACKUP, INT, "1800"}},
    {"ModelRunnerTypeCache", {CLEAR_ON_ONROAD_TRANSITION, INT}},
    {"OffroadMode", {CLEAR_ON_MANAGER_START, BOOL}},
    {"Offroad_TiciSupport", {CLEAR_ON_MANAGER_START, JSON}},
    {"OnroadScreenOffBrightness", {PERSISTENT | BACKUP, INT, "0"}},
    {"OnroadScreenOffBrightnessMigrated", {PERSISTENT | BACKUP, STRING, "0.0"}},
    {"OnroadScreenOffTimer", {PERSISTENT | BACKUP, INT, "15"}},
    {"OnroadScreenOffTimerMigrated", {PERSISTENT | BACKUP, STRING, "0.0"}},
    {"OnroadUploads", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"QuickBootToggle", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"QuietMode", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"RainbowMode", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"RocketFuel", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"ShowAdvancedControls", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"ShowTurnSignals", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"StandstillTimer", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"TrueVEgoUI", {PERSISTENT | BACKUP, BOOL, "0"}},

    // MADS params
    {"Mads", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"MadsMainCruiseAllowed", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"MadsSteeringMode", {PERSISTENT | BACKUP, INT, "0"}},
    {"MadsUnifiedEngagementMode", {PERSISTENT | BACKUP, BOOL, "1"}},

    // Model Manager params
    {"ModelManager_ActiveBundle", {PERSISTENT, JSON}},
    {"ModelManager_ClearCache", {CLEAR_ON_MANAGER_START, BOOL}},
    {"ModelManager_DownloadIndex", {CLEAR_ON_MANAGER_START | CLEAR_ON_ONROAD_TRANSITION, INT}},
    {"ModelManager_Favs", {PERSISTENT | BACKUP, STRING}},
    {"ModelManager_LastSyncTime", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, INT, "0"}},
    {"ModelManager_ModelsCache", {PERSISTENT | BACKUP, JSON}},

    // Neural Network Lateral Control
    {"NeuralNetworkLateralControl", {PERSISTENT | BACKUP, BOOL, "0"}},

    // sunnylink params
    {"EnableSunnylinkUploader", {PERSISTENT | BACKUP, BOOL}},
    {"LastSunnylinkPingTime", {CLEAR_ON_MANAGER_START, INT}},
    {"ParamsVersion", {PERSISTENT, INT}},
    {"SunnylinkCache_Roles", {PERSISTENT, STRING}},
    {"SunnylinkCache_Users", {PERSISTENT, STRING}},
    {"SunnylinkDongleId", {PERSISTENT, STRING}},
    {"SunnylinkdPid", {PERSISTENT, INT}},
    {"SunnylinkEnabled", {PERSISTENT, BOOL, "1"}},
    {"SunnylinkTempFault", {CLEAR_ON_MANAGER_START | CLEAR_ON_OFFROAD_TRANSITION, BOOL, "0"}},

    // Backup Manager params
    {"BackupManager_CreateBackup", {PERSISTENT, BOOL}},
    {"BackupManager_RestoreVersion", {PERSISTENT, STRING}},

    // sunnypilot car specific params
    {"HondaEnforceStockLongitudinal", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"HyundaiLongitudinalTuning", {PERSISTENT | BACKUP, INT, "0"}},
    {"SubaruStopAndGo", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"SubaruStopAndGoManualParkingBrake", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"TeslaCoopSteering", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"TeslaMadsScreenButton", {PERSISTENT | BACKUP, INT, "0"}},
    {"ToyotaEnforceStockLongitudinal", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"ToyotaStopAndGoHack", {PERSISTENT | BACKUP, BOOL, "0"}},

    {"DynamicExperimentalControl", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"BlindSpot", {PERSISTENT | BACKUP, BOOL, "0"}},

    // sunnypilot model params
    {"CameraOffset", {PERSISTENT | BACKUP, FLOAT, "0.0"}},
    {"LagdToggle", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"LagdToggleDelay", {PERSISTENT | BACKUP, FLOAT, "0.2"}},
    {"LagdValueCache", {PERSISTENT, FLOAT, "0.2"}},
    {"LaneTurnDesire", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"LaneTurnValue", {PERSISTENT | BACKUP, FLOAT, "19.0"}},
    {"PlanplusControl", {PERSISTENT | BACKUP, FLOAT, "1.0"}},

    // mapd
    {"MapAdvisorySpeedLimit", {CLEAR_ON_ONROAD_TRANSITION, FLOAT}},
    {"MapdVersion", {PERSISTENT, STRING}},
    {"MapSpeedLimit", {CLEAR_ON_ONROAD_TRANSITION, FLOAT, "0.0"}},
    {"NextMapSpeedLimit", {CLEAR_ON_ONROAD_TRANSITION, JSON}},
    {"Offroad_OSMUpdateRequired", {CLEAR_ON_MANAGER_START, JSON}},
    {"OsmDbUpdatesCheck", {CLEAR_ON_MANAGER_START, BOOL}},  // mapd database update happens with device ON, reset on boot
    {"OSMDownloadBounds", {PERSISTENT, STRING}},
    {"OsmDownloadedDate", {PERSISTENT, STRING, "0.0"}},
    {"OSMDownloadLocations", {PERSISTENT, JSON}},
    {"OSMDownloadProgress", {CLEAR_ON_MANAGER_START, JSON}},
    {"OsmLocal", {PERSISTENT, BOOL}},
    {"OsmLocationName", {PERSISTENT, STRING}},
    {"OsmLocationTitle", {PERSISTENT, STRING}},
    {"OsmLocationUrl", {PERSISTENT, STRING}},
    {"OsmStateName", {PERSISTENT, STRING, "All"}},
    {"OsmStateTitle", {PERSISTENT, STRING}},
    {"OsmWayTest", {PERSISTENT, STRING}},
    {"RoadName", {CLEAR_ON_ONROAD_TRANSITION, STRING}},
    {"RoadNameToggle", {PERSISTENT | BACKUP, BOOL, "0"}},

    // Speed Limit
    {"SpeedLimitMode", {PERSISTENT | BACKUP, INT, "1"}},
    {"SpeedLimitOffsetType", {PERSISTENT | BACKUP, INT, "0"}},
    {"SpeedLimitPolicy", {PERSISTENT | BACKUP, INT, "3"}},
    {"SpeedLimitValueOffset", {PERSISTENT | BACKUP, INT, "0"}},

    // Smart Cruise Control
    {"MapTargetVelocities", {CLEAR_ON_ONROAD_TRANSITION, STRING}},
    {"SmartCruiseControlMap", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"SmartCruiseControlVision", {PERSISTENT | BACKUP, BOOL, "0"}},

    // nrdr params
    {"LatPScaleLowSpeed", {PERSISTENT | BACKUP, INT, "100"}},   // lateral P scale (below 25 mph)
    {"LatPScaleStandard", {PERSISTENT | BACKUP, INT, "100"}},   // lateral P scale (25-50 mph)
    {"LatPScaleHighway", {PERSISTENT | BACKUP, INT, "100"}},    // lateral P scale (50 mph+)
    {"LatIScaleLowSpeed", {PERSISTENT | BACKUP, INT, "100"}},   // lateral I scale (below 25 mph)
    {"LatIScaleStandard", {PERSISTENT | BACKUP, INT, "100"}},   // lateral I scale (25-50 mph)
    {"LatIScaleHighway", {PERSISTENT | BACKUP, INT, "100"}},    // lateral I scale (50 mph+)
    {"LatFScaleLowSpeed", {PERSISTENT | BACKUP, INT, "100"}},   // lateral feedforward scale (below 25 mph)
    {"LatFScaleStandard", {PERSISTENT | BACKUP, INT, "100"}},   // lateral feedforward scale (25-50 mph)
    {"LatFScaleHighway", {PERSISTENT | BACKUP, INT, "100"}},    // lateral feedforward scale (50 mph+)
    {"LongPidTuneScale", {PERSISTENT | BACKUP, INT, "100"}},
    {"NrdrCruiseMismatchCorrection", {PERSISTENT | BACKUP, FLOAT, "100"}}, // % scale on final cruise target so actual speed matches set (100.0 = off)
    {"HondaCenterScale", {PERSISTENT | BACKUP, FLOAT, "0.5"}},
    {"HondaPidFriction", {PERSISTENT | BACKUP, FLOAT, "0.5"}},  // legacy direct torque-space friction overlay for modified-EPS Honda PID
    // DEPRECATED notch-filter keys: all readers removed, but kept REGISTERED so stale bytecode /
    // mid-OTA devices resolve them instead of crash-looping the card on UnknownKeyName. Do NOT
    // delete until the fleet has updated well past this release (see two-phase removal note).
    {"HondaNotchEnabled", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"HondaNotchFreq", {PERSISTENT | BACKUP, FLOAT, "7.5"}},
    {"HondaNotchQ", {PERSISTENT | BACKUP, FLOAT, "1.5"}},
    {"NrdrLearnSteerRatio", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"NrdrSteerRatioOffset", {PERSISTENT | BACKUP, FLOAT, "0.0"}},  // uniform +/-5.0 shift of the measured SR(angle) curve; applied only when NrdrLearnSteerRatio is off
    {"NrdrSteerRatioMin", {PERSISTENT | BACKUP, FLOAT, "16.84"}},   // DEPRECATED (replaced by NrdrSteerRatioOffset): kept registered so removed readers can't UnknownKeyName-crash
    {"NrdrSteerRatioMax", {PERSISTENT | BACKUP, FLOAT, "12.74"}},   // DEPRECATED (replaced by NrdrSteerRatioOffset): kept registered
    {"NrdrLearnStiffness", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"NrdrLearnAngleOffset", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"HondaUnwindFreeze", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"HondaUnwindLookahead", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"HondaStoppingDecelRate", {PERSISTENT | BACKUP, INT, "30"}},
    {"NrdrIncreaseOverrideTolerance", {PERSISTENT | BACKUP, BOOL, "0"}},  // UI label: Increase Driver Override Hysteresis (default OFF)
    {"NrdrDriverOverrideThreshold", {PERSISTENT | BACKUP, INT, "2400"}},  // steeringPressed threshold; 1200 = stock, proportional on non-1200 cars
    {"NrdrOverrideThresholdCenterBoost", {PERSISTENT | BACKUP, INT, "1200"}},  // override threshold used when wheel is within the Center Boost degree band (straights); easy override on straights, no false drops on curves
    {"HondaOverrideFadeDownSecs", {PERSISTENT | BACKUP, FLOAT, "0"}},
    {"HondaOverrideFadeUpSecs", {PERSISTENT | BACKUP, FLOAT, "1.5"}},
    {"HondaOverrideTorqueScale", {PERSISTENT | BACKUP, INT, "0"}},
    {"HondaDriverAssistDuringOverride", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"HondaLiveLearningGas", {PERSISTENT | BACKUP, BOOL, "1"}},
    {"HondaTorqueLowPassFilter", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"HondaLpfTauLowSpeed", {PERSISTENT | BACKUP, FLOAT, "0.1"}},
    {"HondaLpfTauStandard", {PERSISTENT | BACKUP, FLOAT, "0.1"}},
    {"HondaLpfTauHighway", {PERSISTENT | BACKUP, FLOAT, "0.1"}},
    {"NrdrFirstRunSetupDone", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"NrdrAutoSelectModel", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"StaticFeedforwardLong", {PERSISTENT | BACKUP, BOOL, "1"}},     // long PID scale multiplies P+I only; kf stays tuned
    {"NrdrHondaEcuMatchedLong", {PERSISTENT | BACKUP, BOOL, "0"}},   // Honda Nidec: ECU-matched longitudinal (accel rate-limit + coast deadband + sign-change hold-off); OFF = stock
    {"NrdrFordOemLateral", {PERSISTENT | BACKUP, BOOL, "0"}},        // Ford: OEM-style 4-signal lateral (curvature_rate + path_angle + human-turn); OFF = stock curvature-only
    {"NrdrFordHumanTurn", {PERSISTENT | BACKUP, BOOL, "1"}},         // Ford OEM lateral: zero steer during a held manual turn, ramp back on release (anti-"throws me off")
    {"NrdrFordLanePositioning", {PERSISTENT | BACKUP, BOOL, "1"}},   // Ford OEM lateral: path_angle lane-centering PID (added authority/centering)
    {"NrdrFordLanePosGain", {PERSISTENT | BACKUP, INT, "100"}},      // Ford OEM lateral: lane-centering strength % (100 = 1.0x)
    {"NrdrFordMaxLatAccel", {PERSISTENT | BACKUP, FLOAT, "2.4"}},    // Ford OEM lateral: max lateral-accel ceiling m/s^2 (stock ~2.4; raise to fix "runs out of torque")
    {"HondaInjectionTest", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"HondaAltDashboardSpeed", {PERSISTENT | BACKUP, INT, "0"}},     // 0 Stock, 1 Lead Speed, 2 GPS Speed, 3 Cluster Speed
    {"HondaAltDashboardDistance", {PERSISTENT | BACKUP, INT, "0"}},  // 0 Stock, 1 Radar, 2 Velocity
    {"NrdrHondaDashVariantB", {PERSISTENT | BACKUP, BOOL, "0"}},     // Honda cluster mini-speed rounding variant: OFF = Variant A (3 dashed lanes, default), ON = Variant B (4 dashed lanes). UI placeholder; no backend yet.
    {"NrdrMinSteerSpeed", {PERSISTENT | BACKUP, INT, "1"}},          // mph; below this speed no steering torque is commanded (0 = stock, steer always)
    {"NrdrClearDashFaults", {PERSISTENT | BACKUP, BOOL, "1"}},       // zero FCM/icon faults + FCW chime on the cluster; OFF = stock passthrough
    {"HondaSpoofCameraMessages", {PERSISTENT | BACKUP, BOOL, "0"}},  // dead camera: spoof CAMERA_MESSAGES (0x35E) to stop the Auto High Beam fault
    {"NrdrCruiseButtonSubMode", {PERSISTENT | BACKUP, BOOL, "0"}},   // Dynamic HUD: distance/set/resume buttons preview before acting (default OFF)
    {"NrdrCruiseButtonSubModeSecs", {PERSISTENT | BACKUP, INT, "15"}}, // sub-mode window length (5-60s); blink ramp spans the whole window
    {"NrdrHudSubModeUntil", {CLEAR_ON_MANAGER_START, FLOAT, "0"}},   // monotonic deadline of the active HUD sub-mode window
    // Sunnylink remote actions (consumed and cleared by nrdr_remoted)
    {"NrdrRemoteForceUpdate", {CLEAR_ON_MANAGER_START, BOOL, "0"}},  // website "button": run the updater chain
    {"NrdrRemoteTuneScan", {CLEAR_ON_MANAGER_START, BOOL, "0"}},     // website "button": run tune_report.py
    {"NrdrRemoteStatus", {CLEAR_ON_MANAGER_START, STRING, "idle"}},  // remote action status line shown on the website
    {"NrdrTuneReportSummary", {PERSISTENT, STRING, ""}},             // per-speed summary table from the last tune scan
    {"NrdrCarTuneInfo", {PERSISTENT, STRING, ""}},                   // Car & Tune Info readout for the Sunnylink info row (written by nrdr_remoted)
    {"NrdrCarTuneDetails", {PERSISTENT, STRING, ""}},                // multiline live data injected into the Sunnylink Profile info modal
    {"NrdrCarControllerInfo", {PERSISTENT, STRING, ""}},             // concise read-only Controller row in Sunnylink Car & Tune Info
    {"NrdrCarHandcraftedInfo", {PERSISTENT, STRING, ""}},            // active fingerprint-scoped handcrafted profile name/version
    {"NrdrCarPidLowInfo", {PERSISTENT, STRING, ""}},                 // concise read-only low-speed PID scale row
    {"NrdrCarPidMidInfo", {PERSISTENT, STRING, ""}},                 // concise read-only standard-speed PID scale row
    {"NrdrCarPidHighInfo", {PERSISTENT, STRING, ""}},                // concise read-only highway PID scale row
    {"NrdrCarDampingInfo", {PERSISTENT, STRING, ""}},                // concise read-only rate-damping row
    {"NrdrCarCenterInfo", {PERSISTENT, STRING, ""}},                 // concise read-only center-boost row
    {"NrdrCarNnlcInfo", {PERSISTENT, STRING, ""}},                   // concise read-only NNLC settings row
    {"NrdrCarSteerRatioInfo", {PERSISTENT, STRING, ""}},             // concise read-only steer-ratio settings row
    {"NrdrCarLearningInfo", {PERSISTENT, STRING, ""}},               // concise read-only live-learning settings row
    {"NrdrCarHelpersInfo", {PERSISTENT, STRING, ""}},                // concise read-only stiction/StarPilot row
    {"NrdrStarPilotPid", {PERSISTENT | BACKUP, BOOL, "0"}},          // borrowed StarPilot _pid_output_scale (center boost + turn-in/per-direction scaling); 0 = clean PID/F + D
    {"NrdrHandcraftedLateralTune", {PERSISTENT | BACKUP, BOOL, "1"}}, // fingerprint-scoped, versioned road-tested lateral profile; unsupported cars ignore it
    {"NrdrNnlcEnabled", {PERSISTENT | BACKUP, BOOL, "1"}},            // Clarity hybrid: allow the NNLC half of the controller (OFF = PID only)
    {"NrdrNnlcActivationSpeed", {PERSISTENT | BACKUP, INT, "30"}},    // mph; center of the smooth PID -> NNLC speed handoff
    {"NrdrNnlcKpGain", {PERSISTENT | BACKUP, INT, "100"}},            // NNLC feedback proportional gain, percent of 1.0
    {"NrdrNnlcKfGain", {PERSISTENT | BACKUP, INT, "50"}},             // NNLC neural feedforward gain, percent of 1.0
    {"NrdrNnlcKiGain", {PERSISTENT | BACKUP, INT, "10"}},             // NNLC feedback integral gain, percent of 1.0
    {"NrdrTuneLearner", {PERSISTENT | BACKUP, BOOL, "1"}},           // 2D online lateral auto-tuner (learned per-cell FF trim); 0 = off
    {"NrdrLatStiction", {PERSISTENT | BACKUP, BOOL, "0"}},           // lateral stiction: emulated EPS breakaway hold/move stage (NRDR_LATERAL_STICTION.md)
    {"NrdrTuneLearnerReset", {PERSISTENT, BOOL, "0"}},               // momentary: device zeroes the learned trim map, then clears this
    {"NrdrTuneLearnerStrength", {PERSISTENT | BACKUP, INT, "100"}},   // learned-trim authority cap, % of steer_max (0-100 via UI slider)
    {"NrdrTuneLearnerRate", {PERSISTENT | BACKUP, INT, "50"}},       // learning speed, % of reference rate (0 freezes learning)
    {"NrdrTuneLearnerMap", {PERSISTENT | BACKUP | DONT_LOG, BYTES}}, // learned trim surface (2 x speed x angle float32 blob)
    {"HondaCenterBoostThreshold", {PERSISTENT | BACKUP, FLOAT, "3"}},  // deg from center where Center Scale is active
    {"HondaCenterBoostMinSpeed", {PERSISTENT | BACKUP, INT, "50"}},  // mph; below this speed center boost is disabled (low-speed center-oscillation fix)
    {"HondaUnwindBoostSeconds", {PERSISTENT | BACKUP, FLOAT, "1"}},  // s; unwind FF boost is held for the first N seconds of each unwind, then fades out
    {"HondaUnwindFfMultiplier", {PERSISTENT | BACKUP, FLOAT, "2"}},  // peak unwind feedforward multiplier at a standstill (fades to 1x by ~22mph)
    {"NrdrLatRateDamping", {PERSISTENT | BACKUP, INT, "30"}},          // %; rate-damping (D) strength, 0 = off (torque opposing steering-wheel rate to damp low-speed oscillation)
    {"NrdrLatRateDampingFadeSpeed", {PERSISTENT | BACKUP, INT, "30"}},  // mph; rate damping fades to zero by this speed, where tire self-aligning torque resumes damping
    {"HondaSteerDeltaLimiter", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"HondaSteerDeltaUp", {PERSISTENT | BACKUP, FLOAT, "3"}},
    {"HondaSteerDeltaDown", {PERSISTENT | BACKUP, FLOAT, "3"}},
    {"HondaPidTuneScale", {PERSISTENT | BACKUP, INT, "100"}},
    {"HondaStopAccel", {PERSISTENT | BACKUP, FLOAT, "-2"}},
    {"HondaStoppingDecelRateLong", {PERSISTENT | BACKUP, FLOAT, "0.3"}},
    {"HondaVEgoStopping", {PERSISTENT | BACKUP, FLOAT, "0.5"}},
    {"HondaVEgoStarting", {PERSISTENT | BACKUP, FLOAT, "0.5"}},
    {"HondaCivicRadarTryout", {PERSISTENT | BACKUP, BOOL, "0"}},  // EXPERIMENTAL Bosch radar try-out; opt-in only (Special panel)

    // Torque lateral control custom params
    {"CustomTorqueParams", {PERSISTENT | BACKUP , BOOL}},
    {"EnforceTorqueControl", {PERSISTENT | BACKUP, BOOL}},
    {"LiveTorqueParamsToggle", {PERSISTENT | BACKUP , BOOL}},
    {"LiveTorqueParamsRelaxedToggle", {PERSISTENT | BACKUP , BOOL}},
    {"TorqueControlTune", {PERSISTENT | BACKUP, FLOAT, "0.0"}},
    {"TorqueParamsOverrideEnabled", {PERSISTENT | BACKUP, BOOL, "0"}},
    {"TorqueParamsOverrideFriction", {PERSISTENT | BACKUP, FLOAT, "0.1"}},
    {"TorqueParamsOverrideLatAccelFactor", {PERSISTENT | BACKUP, FLOAT, "2.5"}},
};
