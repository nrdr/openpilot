#pragma once

#include "opendbc/safety/declarations.h"

// All common address checks except SCM_BUTTONS and ENGINE_DATA which aren't on some safety configurations
#define HONDA_BASE_RX_CHECKS(pt_bus)                                                                                                      \
  {.msg = {{0x1A6, (pt_bus), 8, 25U, .max_counter = 3U, .ignore_quality_flag = true},                  /* SCM_BUTTONS */       \
           {0x296, (pt_bus), 4, 25U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }}},                                 \
  {.msg = {{0x17C, (pt_bus), 8, 100U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  /* POWERTRAIN_DATA */  \

// All common address checks except SCM_BUTTONS which isn't on one Nidec safety configuration
#define HONDA_COMMON_NO_SCM_FEEDBACK_RX_CHECKS(pt_bus)                                                                                    \
  HONDA_BASE_RX_CHECKS(pt_bus)                                                                                                            \
  {.msg = {{0x158, (pt_bus), 8, 100U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  /* ENGINE_DATA */      \

#define HONDA_COMMON_RX_CHECKS(pt_bus)                                                                                                    \
  HONDA_COMMON_NO_SCM_FEEDBACK_RX_CHECKS(pt_bus)                                                                                          \
  {.msg = {{0x326, (pt_bus), 8, 10U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  /* SCM_FEEDBACK */  \

// For radarless cars without ENGINE_DATA, swap in ABS_SENSOR for low-speed movement checks.
#define HONDA_NO_ENGINE_DATA_RX_CHECKS(pt_bus)                                                                                            \
  HONDA_BASE_RX_CHECKS(pt_bus)                                                                                                            \
  {.msg = {{0x20E, (pt_bus), 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  /* ABS_SENSOR */        \
  {.msg = {{0x326, (pt_bus), 8, 10U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  /* SCM_FEEDBACK */  \

// Alternate brake message is used on some Honda Bosch, and Honda Bosch radarless (where PT bus is 0)
#define HONDA_ALT_BRAKE_ADDR_CHECK(pt_bus)                                                                                              \
  {.msg = {{0x1BE, (pt_bus), 3, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  /* BRAKE_MODULE */  \

#define HONDA_GAS_INTERCEPTOR_ADDR_CHECK \
  {.msg = {{0x201, 0, 6, 50U, .max_counter = 15U, .ignore_checksum = true, .ignore_counter = true, .ignore_quality_flag = true}, { 0 }, { 0 }}}, \

// Clarity angle mode: STEERING_SENSORS, the measured angle the angle rule checks the target against
#define HONDA_CLARITY_ANGLE_ADDR_CHECK \
  {.msg = {{0x14A, 0, 8, 100U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}}, \

#define HONDA_N_COMMON_TX_MSGS \
  {0xE4,  0, 5, .check_relay = true},   \
  {0x194, 0, 4, .check_relay = true},   \
  {0x33D, 0, 5, .check_relay = true},   \

#define HONDA_N_COMMON_LONG_TX_MSGS \
  {0x1FA, 0, 8, .check_relay = false},  \
  {0x30C, 0, 8, .check_relay = true},   \

enum {
  HONDA_BTN_NONE = 0,
  HONDA_BTN_MAIN = 1,
  HONDA_BTN_CANCEL = 2,
  HONDA_BTN_SET = 3,
  HONDA_BTN_RESUME = 4,
};

static int honda_brake = 0;
static bool honda_brake_switch_prev = false;
static bool honda_alt_brake_msg = false;
static bool honda_fwd_brake = false;
static bool honda_bosch_long = false;
static bool honda_bosch_radarless = false;
static bool honda_bosch_canfd = false;
static bool honda_nidec_hybrid = false;
static bool honda_clarity_brake_guard = false;
static bool honda_clarity_brake_eligible = false;
static bool honda_clarity_pedal_seen = false;
static bool honda_stock_longitudinal = false;
static bool honda_gas_interceptor_threshold_512 = false;
static bool honda_no_engine_data_msg = false;
static unsigned int honda_abs_prev_fl = 0U;
static unsigned int honda_abs_prev_fr = 0U;
static unsigned int honda_abs_prev_rl = 0U;
static unsigned int honda_abs_prev_rr = 0U;
static unsigned int honda_abs_prev_counter_checksum = 0xFFU;
// counts down on each stock SCM_BUTTONS rx, topped up on each OP SCM_BUTTONS tx to the camera:
// the stock buttons are only blocked from forwarding while OP's replacement stream is actually flowing
static int honda_op_buttons_fresh = 0;
typedef enum {HONDA_NIDEC, HONDA_BOSCH} HondaHw;
static HondaHw honda_hw = HONDA_NIDEC;


static unsigned int honda_get_pt_bus(void) {
  return ((honda_hw == HONDA_BOSCH) && !honda_bosch_radarless && !honda_bosch_canfd) ? 1U : 0U;
}

static uint32_t honda_get_checksum(const CANPacket_t *msg) {
  int checksum_byte = GET_LEN(msg) - 1U;
  return (uint8_t)(msg->data[checksum_byte]) & 0xFU;
}

static uint32_t honda_compute_checksum(const CANPacket_t *msg) {
  int len = GET_LEN(msg);
  uint8_t checksum = 0U;
  unsigned int addr = msg->addr;
  while (addr > 0U) {
    checksum += (uint8_t)(addr & 0xFU); addr >>= 4;
  }
  for (int j = 0; j < len; j++) {
    uint8_t byte = msg->data[j];
    checksum += (uint8_t)(byte & 0xFU) + (byte >> 4U);
    if (j == (len - 1)) {
      checksum -= (byte & 0xFU);  // remove checksum in message
    }
  }
  return (uint8_t)((8U - checksum) & 0xFU);
}

static uint8_t honda_get_counter(const CANPacket_t *msg) {
  uint8_t cnt = 0U;
  if (msg->addr == 0x201U) {
    // Signal: PEDAL_COUNTER
    cnt = msg->data[4] & 0x0FU;
  } else {
    int counter_byte = GET_LEN(msg) - 1U;
    cnt = (msg->data[counter_byte] >> 4U) & 0x3U;
  }
  return cnt;
}

static int HONDA_GET_INTERCEPTOR(const CANPacket_t *msg) {
  uint16_t val1 = (uint16_t)((uint16_t)msg->data[0] << 8U) | (uint16_t)msg->data[1];
  uint16_t val2 = (uint16_t)((uint16_t)msg->data[2] << 8U) | (uint16_t)msg->data[3];
  uint16_t avg  = (uint16_t)((val1 + val2) / 2U);

  return (int)avg;
}

// Clarity angle-mode EPS (sunnypilot safety param HONDA_PARAM_SP_CLARITY_ANGLE, Nidec only, ported from the night-star7
// personal branch e6676c283f / fbf15b2cbb). The modified EPS firmware reads 0xE4 bytes 0-1 as a steering-wheel angle
// target, in the units of its own STEERING_SENSORS (0x14A) STEER_ANGLE (0.1 deg, same sign), when byte 2 bit 7 (request)
// and bit 5 (angle payload) are both set; byte 3 sets the mode and the loop's authority (only reduces it; not checked).
// A target of 0 steers to center, so the torque rule "bytes 0-1 must be 0" does not protect an angle car.
// Rules: the standard vehicle-model angle rule of the other angle brands (steer_angle_cmd_checks_vm: 3.6 m/s^2 lateral
// accel, 3.6 m/s^3 lateral jerk, at speed - 1 m/s, last target reset to the measured angle after a violation or while
// not steering), with the angle for a lateral acceleration taken from the EPS's own clamp table (angle_ref AMAX, which
// matches the car: v x yaw rate / table accel = 1.02) instead of a bicycle model, plus Honda's frame format:
//  - lateral not allowed, or request and payload not both set: bytes 0-1, request and payload must all be 0
//  - steering needs a measured angle (0x14A, an RX check in this mode) no older than 50 ms
//  - |target| <= the 3.6 m/s^2 angle: 0.9 x the EPS 4.0 m/s^2 table, extended as 1/v^2 below 5 and above 30 m/s,
//    capped at 500 deg. No exemptions.
//  - per-frame step <= the angle the jerk limit allows in 10 ms: with jerk = accel = 3.6, that is the 3.6 m/s^2 angle
//    per second (31.8 deg/s at 20 m/s), and never more than the EPS's own jump threshold
//  - the first target after not steering or after a blocked frame is within one step of the measured angle (any of
//    the last 6 0x14A samples when that target is checked)
// Evidence: rwd-xray lab/clarity/PANDA_ANGLE_SAFETY_20261121 (re-simulated sender on the owner's drives, closed loop).
#define HONDA_PARAM_SP_CLARITY_ANGLE 32U
#define HONDA_ANGLE_MEAS_TIMEOUT_US 50000U
#define HONDA_ANGLE_MAX 5000  // 0.1 deg
static bool honda_angle_mode = false;
static int honda_angle_last = 0;
static bool honda_angle_from_wheel = true;   // the next target's step is measured from the wheel, not the last target
static bool honda_angle_meas_seen = false;
static uint32_t honda_angle_meas_ts = 0U;

static void honda_angle_reset(bool enabled) {
  honda_angle_mode = enabled;
  honda_angle_last = 0;
  honda_angle_from_wheel = true;
  honda_angle_meas_seen = false;
  honda_angle_meas_ts = 0U;
}

static float honda_angle_interp(const float *xs, const float *ys, int n, float x) {
  float ret = ys[n - 1];
  if (x <= xs[0]) {
    ret = ys[0];
  } else {
    for (int i = 0; i < (n - 1); i++) {
      if (x < xs[i + 1]) {
        ret = ys[i] + ((ys[i + 1] - ys[i]) * (x - xs[i]) / (xs[i + 1] - xs[i]));
        break;
      }
    }
  }
  return ret;
}

// the 3.6 m/s^2 steering-wheel angle at speed (m/s, >= 1), 0.1 deg
static float honda_angle_accel_limit(float speed) {
  static const float V[8] = {5., 8., 10., 12., 16., 20., 25., 30.};
  static const float LIM[8] = {3411., 1440., 981., 722.7, 450., 317.7, 231.3, 183.6};  // 0.9 x angle_ref AMAX
  float lim;
  if (speed < V[0]) {
    lim = LIM[0] * (V[0] * V[0]) / (speed * speed);
  } else if (speed > V[7]) {
    lim = LIM[7] * (V[7] * V[7]) / (speed * speed);
  } else {
    lim = honda_angle_interp(V, LIM, 8, speed);
  }
  return SAFETY_MIN(lim, (float)HONDA_ANGLE_MAX);
}

static bool honda_lateral_allowed(void) {
  return controls_allowed || controls_allowed_lateral;
}

static void honda_angle_rx(const CANPacket_t *msg, unsigned int pt_bus) {
  if (honda_angle_mode && (msg->bus == pt_bus)) {
    if (msg->addr == 0x158U) {
      UPDATE_VEHICLE_SPEED(((msg->data[0] << 8) | msg->data[1]) * 0.01 / 3.6);  // XMISSION_SPEED, 0.01 kph
    }
    if (msg->addr == 0x14AU) {  // an RX check in angle mode: checksum, counter and rate already verified
      update_sample(&angle_meas, to_signed((msg->data[0] << 8) | msg->data[1], 16));
      honda_angle_meas_seen = true;
      honda_angle_meas_ts = microsecond_timer_get();
    }
  }
}

static bool honda_angle_tx_violation(const CANPacket_t *msg) {
  static const float V[9] = {0., 5., 8., 10., 12., 15., 20., 25., 30.};
  static const float JUMP[9] = {40., 40., 31., 25., 19., 10., 10., 10., 10.};          // EPS jump threshold, 0.1 deg per frame
  const int target = to_signed((msg->data[0] << 8) | msg->data[1], 16);
  const bool request = GET_BIT(msg, 23U);
  const bool payload = GET_BIT(msg, 21U);
  const bool steering = request && payload;
  bool violation = false;

  if (!honda_lateral_allowed() || !steering) {
    violation = (target != 0) || request || payload;
  } else {
    // fudge the speed down 1 m/s: both limits only widen as speed falls
    const float speed = SAFETY_MAX(((float)vehicle_speed.min / VEHICLE_SPEED_FACTOR) - 1.0f, 1.0f);
    const bool meas_fresh = honda_angle_meas_seen &&
      (safety_get_ts_elapsed(microsecond_timer_get(), honda_angle_meas_ts) <= HONDA_ANGLE_MEAS_TIMEOUT_US);
    const float lim = honda_angle_accel_limit(speed);
    // jerk limit: with lateral jerk = lateral accel = 3.6, the angle rate is the accel angle per second (100 Hz frames)
    const float step = SAFETY_MIN(lim / 100.0f, honda_angle_interp(V, JUMP, 9, speed));
    const int step_can = (int)(step + 1.0f);
    const int lim_can = (int)(lim + 1.0f);
    // from the wheel: within one step of the last 6 measured samples (the standard's inactive check uses the same
    // min/max window; openpilot's carState angle is 10-20 ms older than the newest 0x14A); otherwise of the last target
    const int hi = honda_angle_from_wheel ? SAFETY_CLAMP(angle_meas.max, -HONDA_ANGLE_MAX, HONDA_ANGLE_MAX) : honda_angle_last;
    const int lo = honda_angle_from_wheel ? SAFETY_CLAMP(angle_meas.min, -HONDA_ANGLE_MAX, HONDA_ANGLE_MAX) : honda_angle_last;
    violation = !meas_fresh;
    violation |= safety_max_limit_check(target, hi + step_can, lo - step_can);
    violation |= safety_max_limit_check(target, lim_can, -lim_can);
  }
  honda_angle_last = target;
  // not steering, or a violation: the next target must be within one step of the wheel, measured when it is checked
  // (the standard resets the last target to the measured angle here; checking against the samples current at the next
  // frame follows a wheel that moves in between)
  honda_angle_from_wheel = violation || !honda_lateral_allowed() || !steering;
  return violation;
}

static void honda_rx_hook(const CANPacket_t *msg) {
  const bool pcm_cruise = ((honda_hw == HONDA_BOSCH) && !honda_bosch_long) || ((honda_hw == HONDA_NIDEC) && !enable_gas_interceptor);
  unsigned int pt_bus = honda_get_pt_bus();
  honda_angle_rx(msg, pt_bus);

  // sample speed - 0x158 used for all supported Hondas except Integra (use 0x20E abs_sensor message)
  if (honda_no_engine_data_msg && (msg->addr == 0x20EU)) {
    if (msg->data[7] != honda_abs_prev_counter_checksum) {  // occasionally car sends repeated abs_sensor messages, need to ignore
      vehicle_moving = ((msg->data[0] != honda_abs_prev_fl) || (msg->data[1] != honda_abs_prev_fr) || (msg->data[2] != honda_abs_prev_rl) || (msg->data[3] != honda_abs_prev_rr));
    }
    honda_abs_prev_fl = msg->data[0];
    honda_abs_prev_fr = msg->data[1];
    honda_abs_prev_rl = msg->data[2];
    honda_abs_prev_rr = msg->data[3];
    honda_abs_prev_counter_checksum = msg->data[7];
  } else if (msg->addr == 0x158U) {
    vehicle_moving = msg->data[0] | msg->data[1];
  } else {
    // no change to vehicle_moving
  }

  // check ACC main state
  // 0x326 for all Bosch and some Nidec, 0x1A6 for some Nidec
  if ((msg->addr == 0x326U) || (msg->addr == 0x1A6U)) {
    acc_main_on = GET_BIT(msg, ((msg->addr == 0x326U) ? 28U : 47U));
    if (!acc_main_on) {
      controls_allowed = false;
    }
  }

  // enter controls when PCM enters cruise state
  if (pcm_cruise && (msg->addr == 0x17CU)) {
    const bool cruise_engaged = GET_BIT(msg, 38U);
    // engage on rising edge
    if (cruise_engaged && !cruise_engaged_prev) {
      controls_allowed = true;
    }

    // Since some Nidec cars can brake down to 0 after the PCM disengages,
    // we don't disengage when the PCM does.
    if (!cruise_engaged && (honda_hw != HONDA_NIDEC)) {
      controls_allowed = false;
    }
    cruise_engaged_prev = cruise_engaged;
  }

  // state machine to enter and exit controls for button enabling
  // 0x1A6 for the ILX, 0x296 for the Civic Touring
  if (((msg->addr == 0x1A6U) || (msg->addr == 0x296U)) && (msg->bus == pt_bus)) {
    // stock buttons act as the clock for the OP button takeover freshness (see honda_bosch_fwd_hook)
    if (honda_op_buttons_fresh > 0) {
      honda_op_buttons_fresh--;
    }

    int button = (msg->data[0] & 0xE0U) >> 5;

    int cruise_setting = (msg->data[(msg->addr == 0x296U) ? 0U : 5U] & 0x0CU) >> 2U;
    if (cruise_setting == 1) {
      mads_button_press = MADS_BUTTON_PRESSED;
    } else if (cruise_setting == 0) {
      mads_button_press = MADS_BUTTON_NOT_PRESSED;
    } else {
    }

    // enter controls on the falling edge of set or resume
    bool set = (button != HONDA_BTN_SET) && (cruise_button_prev == HONDA_BTN_SET);
    bool res = (button != HONDA_BTN_RESUME) && (cruise_button_prev == HONDA_BTN_RESUME);
    if (acc_main_on && !pcm_cruise && (set || res)) {
      controls_allowed = true;
    }

    // exit controls once main or cancel are pressed
    if ((button == HONDA_BTN_MAIN) || (button == HONDA_BTN_CANCEL)) {
      controls_allowed = false;
    }
    cruise_button_prev = button;
  }

  // user brake signal on 0x17C reports applied brake from computer brake on accord
  // and crv, which prevents the usual brake safety from working correctly. these
  // cars have a signal on 0x1BE which only detects user's brake being applied so
  // in these cases, this is used instead.
  // most hondas: 0x17C
  // accord, crv: 0x1BE
  if (honda_alt_brake_msg) {
    if (msg->addr == 0x1BEU) {
      brake_pressed = GET_BIT(msg, 4U);
    }
  } else {
    if (msg->addr == 0x17CU) {
      // also if brake switch is 1 for two CAN frames, as brake pressed is delayed
      const bool brake_switch = GET_BIT(msg, 32U);
      brake_pressed = (GET_BIT(msg, 53U)) || (brake_switch && honda_brake_switch_prev);
      honda_brake_switch_prev = brake_switch;
    }
  }

  // length check because bosch hardware also uses this id (0x201 w/ len = 8)
  if (msg->addr == 0x201U) {
    // The Nidec interceptor RX check admits only bus 0, DLC 6. Do not unlock the higher limit on host flags alone.
    if (honda_clarity_brake_eligible) {
      honda_clarity_pedal_seen = true;
    }
    // panda interceptor threshold needs to be equivalent to openpilot threshold to avoid controls mismatches
    // If thresholds are mismatched then it is possible for panda to see the gas fall and rise while openpilot is in the pre-enabled state
    // 492 is calculated from the DBC gains; noisy Pilot/Odyssey/Ridgeline pedals use the host-provided 512 threshold flag.
    const int honda_gas_interceptor_thrsld = honda_gas_interceptor_threshold_512 ? 512 : 492;

    int gas_interceptor = HONDA_GET_INTERCEPTOR(msg);
    gas_pressed = gas_interceptor > honda_gas_interceptor_thrsld;

    gas_interceptor_prev = gas_interceptor;
  }

  if (!enable_gas_interceptor) {
    if (msg->addr == 0x17CU) {
      gas_pressed = msg->data[0] != 0U;
    }
  }

  // disable stock Honda AEB in alternative experience
  if (!(alternative_experience & ALT_EXP_DISABLE_STOCK_AEB)) {
    if ((msg->bus == 2U) && (msg->addr == 0x1FAU)) {
      bool honda_stock_aeb = GET_BIT(msg, 29U);
      int honda_stock_brake = (msg->data[0] << 2) | (msg->data[1] >> 6);

      if (honda_nidec_hybrid) {
        honda_stock_brake = (msg->data[6] << 2) | (msg->data[7] >> 6);
      }

      // Forward AEB when stock braking is higher than openpilot braking
      // only stop forwarding when AEB event is over
      if (!honda_stock_aeb) {
        honda_fwd_brake = false;
      } else if (honda_stock_brake >= honda_brake) {
        honda_fwd_brake = true;
      } else {
        // Leave Honda forward brake as is
      }
    }
  }
}

static bool honda_tx_hook(const CANPacket_t *msg) {

  const LongitudinalLimits HONDA_BOSCH_LONG_LIMITS = {
    .max_accel = 200,   // accel is used for brakes
    .min_accel = -350,

    .max_gas = 2200,
    .inactive_gas = -30000,
  };

  const LongitudinalLimits HONDA_NIDEC_LONG_LIMITS = {
    .max_gas = 198,  // 0xc6
    .max_brake = 255,

    .inactive_speed = 0,
  };

  bool tx = true;

  unsigned int bus_pt = honda_get_pt_bus();
  unsigned int bus_buttons = (honda_bosch_radarless) ? 2U : bus_pt;  // the camera controls ACC on radarless Bosch cars

  // ACC_HUD: safety check (nidec w/o pedal)
  if ((msg->addr == 0x30CU) && (msg->bus == bus_pt)) {
    int pcm_speed = (msg->data[0] << 8) | msg->data[1];
    int pcm_gas = msg->data[2];

    bool violation = false;
    violation |= longitudinal_speed_checks(pcm_speed, HONDA_NIDEC_LONG_LIMITS);
    violation |= longitudinal_gas_checks(pcm_gas, HONDA_NIDEC_LONG_LIMITS);
    // While the driver is on the gas, longitudinal_allowed is false and the checks above only pass an
    // all-zero ACC_HUD. The carcontroller mirrors the driver's own pedal onto PCM_GAS through the
    // override; blocking those frames starves the PCM of ACC_HUD and it drops ACC_STATUS
    // ("Cruise Is Off" takeover on every override), so let them through while the pedal is pressed.
    if (violation && !gas_pressed) {
      tx = false;
    }
  }

  // BRAKE: safety check (nidec)
  if ((msg->addr == 0x1FAU) && (msg->bus == bus_pt)) {
    const int standard_brake = (msg->data[0] << 2) | (msg->data[1] >> 6);
    const int hybrid_brake = (msg->data[6] << 2) | (msg->data[7] >> 6);
    const int brake = honda_nidec_hybrid ? hybrid_brake : standard_brake;
    if (honda_clarity_brake_guard) {
      const LongitudinalLimits clarity_hybrid_limits = {.max_brake = honda_clarity_pedal_seen ? 320 : 255};
      // Independent fields. Neither may request any brake when longitudinal actuation is disallowed.
      if (longitudinal_brake_checks(standard_brake, HONDA_NIDEC_LONG_LIMITS) || longitudinal_brake_checks(hybrid_brake, clarity_hybrid_limits)) {
        tx = false;
      }
    } else if (longitudinal_brake_checks(brake, HONDA_NIDEC_LONG_LIMITS)) {
      tx = false;
    } else {
      // No violation: tx unchanged (final else required by MISRA 15.7)
    }
    if (honda_fwd_brake) {
      tx = false;
    }
    // A rejected Clarity request never reached the car; don't let it suppress a subsequent stock AEB.
    if (!honda_clarity_brake_guard || tx) {
      honda_brake = brake;
    }
  }

  // BRAKE/GAS: safety check (bosch)
  if ((msg->addr == 0x1DFU) && (msg->bus == bus_pt)) {
    int accel = (msg->data[3] << 3) | ((msg->data[4] >> 5) & 0x7U);
    accel = to_signed(accel, 11);

    int gas = (msg->data[0] << 8) | msg->data[1];
    gas = to_signed(gas, 16);

    bool violation = false;
    violation |= longitudinal_accel_checks(accel, HONDA_BOSCH_LONG_LIMITS);
    violation |= longitudinal_gas_checks(gas, HONDA_BOSCH_LONG_LIMITS);
    if (violation) {
      tx = false;
    }
  }

  // ACCEL: safety check (radarless)
  if ((msg->addr == 0x1C8U) && (msg->bus == bus_pt)) {
    int accel = (msg->data[0] << 4) | (msg->data[1] >> 4);
    accel = to_signed(accel, 12);

    bool violation = false;
    violation |= longitudinal_accel_checks(accel, HONDA_BOSCH_LONG_LIMITS);
    if (violation) {
      tx = false;
    }
  }

  // STEER: safety check
  if (honda_angle_mode && (msg->addr == 0xE4U)) {
    if (honda_angle_tx_violation(msg)) {
      tx = false;
    }
  } else if ((msg->addr == 0xE4U) || (msg->addr == 0x194U)) {
    if (!(controls_allowed || controls_allowed_lateral)) {
      bool steer_applied = msg->data[0] | msg->data[1];
      if (steer_applied) {
        tx = false;
      }
    }
  } else {
    // not a steering message
  }

  // Bosch supplemental control check
  if (msg->addr == 0xE5U) {
    if ((GET_BYTES(msg, 0, 4) != 0x10800004U) || ((GET_BYTES(msg, 4, 4) & 0x00FFFFFFU) != 0x0U)) {
      tx = false;
    }
  }

  // FORCE CANCEL: safety check only relevant when spamming the cancel button in Bosch HW
  // ensuring that only the cancel button press is sent (VAL 2) when controls are off.
  // This avoids unintended engagements while still allowing resume spam
  // On CAN FD, buttons are also sent to the camera (bus 2) to take over SCM_BUTTONS while engaged,
  // so the same check applies there.
  const bool is_buttons_bus = (msg->bus == bus_buttons) || (honda_bosch_canfd && (msg->bus == 2U));
  if (((msg->addr == 0x1A6U) || (msg->addr == 0x296U)) && !controls_allowed && is_buttons_bus) {
    if (((msg->data[0] >> 5) & 0x7U) != 2U) {
      tx = false;
    }
  }

  // OP is streaming SCM_BUTTONS to the camera: block the stock buttons from forwarding while this
  // stream stays fresh (see honda_bosch_fwd_hook). Topped up here so the block fails safe: if OP
  // stops sending (e.g. it refuses to engage while the panda's button state machine allowed controls),
  // the stock buttons resume forwarding within ~10 button frames (~0.4 s).
  if (tx && (msg->addr == 0x296U) && (msg->bus == 2U)) {
    honda_op_buttons_fresh = 10;
  }

  // Only tester present ("\x02\x3E\x80\x00\x00\x00\x00\x00") allowed on diagnostics address
  // On CAN FD the radar is silenced from CarController once the comma relay is open (rather than from
  // CarInterface.init() under the ELM327 mode, which raced the safety-mode switch and could leave the
  // brake module without ACC_CONTROL long enough to latch CRUISE_FAULT), so additionally allow exactly
  // the extended-diagnostic-session request and the suppressed-response CommunicationControl
  // disableRxAndTx request. The corresponding enable stays blocked: re-enabling the radar into OP's
  // ACC_CONTROL stream would double up control messages while driving.
  if (msg->addr == 0x18DAB0F1U) {
    const uint32_t first_bytes = GET_BYTES(msg, 0, 4);
    bool allowed = (first_bytes == 0x00803E02U);
    if (honda_bosch_canfd) {
      allowed = allowed || (first_bytes == 0x00031002U);  // 02 10 03: extended diagnostic session
      allowed = allowed || (first_bytes == 0x03832803U);  // 03 28 83 03: CommunicationControl disable rx/tx
    }
    if (!allowed || (GET_BYTES(msg, 4, 4) != 0x0U)) {
      tx = false;
    }
  }

  // GAS: safety check (interceptor)
  if (msg->addr == 0x200U) {
    if (longitudinal_interceptor_checks(msg)) {
      tx = false;
    }
  }

  return tx;
}

static safety_config honda_nidec_init(uint16_t param) {
  // 0x1FA is dynamically forwarded based on stock AEB
  // 0xE4 is steering on all cars except CRV and RDX, 0x194 for CRV and RDX,
  // 0x1FA is brake control, 0x30C is acc hud, 0x33D is lkas hud
  static CanMsg HONDA_N_TX_MSGS[] = {
    HONDA_N_COMMON_TX_MSGS
    HONDA_N_COMMON_LONG_TX_MSGS
    {0x1A6, 0, 8, .check_relay = false},
  };

  static CanMsg HONDA_N_STOCK_LONGITUDINAL_TX_MSGS[] = {
    HONDA_N_COMMON_TX_MSGS
    {0x1A6, 0, 8, .check_relay = false},
  };

  static CanMsg HONDA_N_INTERCEPTOR_TX_MSGS[] = {
    HONDA_N_COMMON_TX_MSGS
    HONDA_N_COMMON_LONG_TX_MSGS
    {0x200, 0, 6, .check_relay = false},
    {0x1A6, 0, 8, .check_relay = false},
  };

  // RLX steer-bus bridge: the EPS and the stock LKAS camera are on a separate bus, and a bridge panda relays the
  // camera's LKAS_HUD (0x33D) onto the powertrain bus so openpilot can read LKAS_PROBLEM. A received 0x33D on bus 0
  // is therefore expected rather than a relay malfunction, and it is a checked message like the rest of the car.
  static CanMsg HONDA_N_RLX_BRIDGE_TX_MSGS[] = {{0xE4, 0, 5, .check_relay = true}, {0x194, 0, 4, .check_relay = true}, {0x1FA, 0, 8, .check_relay = false},
                                                {0x30C, 0, 8, .check_relay = true}, {0x33D, 0, 5, .check_relay = false}};

  const uint16_t HONDA_PARAM_NIDEC_ALT = 4;
  const uint16_t HONDA_PARAM_RLX_STEER_BRIDGE = 64;

  const uint16_t HONDA_PARAM_SP_NIDEC_HYBRID = 1;
  const uint16_t HONDA_PARAM_GAS_INTERCEPTOR = 2;
  const uint16_t HONDA_PARAM_STOCK_LONGITUDINAL = 4;
  const uint16_t HONDA_PARAM_GAS_INTERCEPTOR_THRESHOLD_512 = 8;
  const uint16_t HONDA_PARAM_SP_CLARITY_INTERCEPTOR_BRAKE = 16;

  honda_hw = HONDA_NIDEC;
  honda_brake = 0;
  honda_brake_switch_prev = false;
  honda_fwd_brake = false;
  honda_alt_brake_msg = false;
  honda_bosch_long = false;
  honda_bosch_radarless = false;
  honda_bosch_canfd = false;
  honda_no_engine_data_msg = false;
  honda_op_buttons_fresh = 0;
  honda_gas_interceptor_threshold_512 = false;

  safety_config ret;

  bool enable_nidec_alt = GET_FLAG(param, HONDA_PARAM_NIDEC_ALT);
  const bool rlx_steer_bridge = GET_FLAG(param, HONDA_PARAM_RLX_STEER_BRIDGE);

  honda_nidec_hybrid = GET_FLAG(current_safety_param_sp, HONDA_PARAM_SP_NIDEC_HYBRID);
  enable_gas_interceptor = GET_FLAG(current_safety_param_sp, HONDA_PARAM_GAS_INTERCEPTOR);
  honda_stock_longitudinal = GET_FLAG(current_safety_param_sp, HONDA_PARAM_STOCK_LONGITUDINAL);
  honda_gas_interceptor_threshold_512 = GET_FLAG(current_safety_param_sp, HONDA_PARAM_GAS_INTERCEPTOR_THRESHOLD_512);
  honda_clarity_brake_guard = GET_FLAG(current_safety_param_sp, HONDA_PARAM_SP_CLARITY_INTERCEPTOR_BRAKE);
  // Exact Clarity configuration: not RLX/alternate Nidec, stock-long, or a different pedal threshold. The angle-mode
  // bit is independent of the pedal calibration, so it is set on both sides of this exact match.
  honda_clarity_brake_eligible = (param == 0U) && ((current_safety_param_sp | HONDA_PARAM_SP_CLARITY_ANGLE) ==
                                  (HONDA_PARAM_SP_CLARITY_INTERCEPTOR_BRAKE | HONDA_PARAM_SP_NIDEC_HYBRID |
                                   HONDA_PARAM_GAS_INTERCEPTOR | HONDA_PARAM_SP_CLARITY_ANGLE));
  // angle mode only on the Clarity's bus layout (never with the RLX steer-bus bridge, where the EPS is on another bus)
  honda_angle_reset(GET_FLAG(current_safety_param_sp, HONDA_PARAM_SP_CLARITY_ANGLE) && !rlx_steer_bridge);
  honda_clarity_pedal_seen = false;

  if (rlx_steer_bridge) {
    // RLX uses the alternate SCM messages, plus the bridged LKAS_HUD on the powertrain bus
    static RxCheck honda_nidec_rlx_bridge_rx_checks[] = {
      HONDA_COMMON_NO_SCM_FEEDBACK_RX_CHECKS(0)
      {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
      {.msg = {{0x33D, 0, 5, 10U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // LKAS_HUD (stock camera, bridged)
    };

    SET_RX_CHECKS(honda_nidec_rlx_bridge_rx_checks, ret);
  } else if (enable_nidec_alt) {
    // For Nidecs with main on signal on an alternate msg (missing 0x326)
    static RxCheck honda_nidec_alt_rx_checks[] = {
      HONDA_COMMON_NO_SCM_FEEDBACK_RX_CHECKS(0)
      {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
    };

    SET_RX_CHECKS(honda_nidec_alt_rx_checks, ret);
  } else {
    // Nidec includes BRAKE_COMMAND
    static RxCheck honda_nidec_common_rx_checks[] = {
      HONDA_COMMON_RX_CHECKS(0)
      {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
    };

    SET_RX_CHECKS(honda_nidec_common_rx_checks, ret);
  }

  if (honda_stock_longitudinal) {
    SET_TX_MSGS(HONDA_N_STOCK_LONGITUDINAL_TX_MSGS, ret);
  } else if (enable_gas_interceptor) {
    SET_TX_MSGS(HONDA_N_INTERCEPTOR_TX_MSGS, ret);
  } else if (rlx_steer_bridge) {
    SET_TX_MSGS(HONDA_N_RLX_BRIDGE_TX_MSGS, ret);
  } else {
    SET_TX_MSGS(HONDA_N_TX_MSGS, ret);
  }

  if (enable_gas_interceptor) {
    if (enable_nidec_alt) {
      static RxCheck honda_nidec_alt_interceptor_rx_checks[] = {
        HONDA_COMMON_NO_SCM_FEEDBACK_RX_CHECKS(0)
        {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
        HONDA_GAS_INTERCEPTOR_ADDR_CHECK
      };

      SET_RX_CHECKS(honda_nidec_alt_interceptor_rx_checks, ret);
    } else {
      static RxCheck honda_nidec_common_interceptor_rx_checks[] = {
        HONDA_COMMON_RX_CHECKS(0)
        {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
        HONDA_GAS_INTERCEPTOR_ADDR_CHECK
      };

      SET_RX_CHECKS(honda_nidec_common_interceptor_rx_checks, ret);
    }
  }

  if (honda_angle_mode) {
    // the same checks plus STEERING_SENSORS (0x14A): the measured angle the angle rule bounds the target against (the
    // rule never steers without a fresh one)
    if (enable_gas_interceptor && enable_nidec_alt) {
      static RxCheck honda_nidec_alt_interceptor_angle_rx_checks[] = {
        HONDA_COMMON_NO_SCM_FEEDBACK_RX_CHECKS(0)
        {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
        HONDA_GAS_INTERCEPTOR_ADDR_CHECK
        HONDA_CLARITY_ANGLE_ADDR_CHECK
      };
      SET_RX_CHECKS(honda_nidec_alt_interceptor_angle_rx_checks, ret);
    } else if (enable_gas_interceptor) {
      static RxCheck honda_nidec_common_interceptor_angle_rx_checks[] = {
        HONDA_COMMON_RX_CHECKS(0)
        {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
        HONDA_GAS_INTERCEPTOR_ADDR_CHECK
        HONDA_CLARITY_ANGLE_ADDR_CHECK
      };
      SET_RX_CHECKS(honda_nidec_common_interceptor_angle_rx_checks, ret);
    } else if (enable_nidec_alt) {
      static RxCheck honda_nidec_alt_angle_rx_checks[] = {
        HONDA_COMMON_NO_SCM_FEEDBACK_RX_CHECKS(0)
        {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
        HONDA_CLARITY_ANGLE_ADDR_CHECK
      };
      SET_RX_CHECKS(honda_nidec_alt_angle_rx_checks, ret);
    } else {
      static RxCheck honda_nidec_common_angle_rx_checks[] = {
        HONDA_COMMON_RX_CHECKS(0)
        {.msg = {{0x1FA, 2, 8, 50U, .max_counter = 3U, .ignore_quality_flag = true}, { 0 }, { 0 }}},  // BRAKE_COMMAND
        HONDA_CLARITY_ANGLE_ADDR_CHECK
      };
      SET_RX_CHECKS(honda_nidec_common_angle_rx_checks, ret);
    }
  }

  return ret;
}

static safety_config honda_bosch_init(uint16_t param) {
  honda_angle_reset(false);
  honda_clarity_brake_guard = false;
  honda_clarity_brake_eligible = false;
  honda_clarity_pedal_seen = false;
  static CanMsg HONDA_BOSCH_TX_MSGS[] = {{0xE4, 0, 5, .check_relay = true}, {0xE5, 0, 8, .check_relay = true}, {0x296, 1, 4, .check_relay = false},
                                         {0x33D, 0, 5, .check_relay = true}, {0x33D, 0, 8, .check_relay = true}, {0x33DA, 0, 5, .check_relay = true}, {0x33DB, 0, 8, .check_relay = true}};  // Bosch

  static CanMsg HONDA_BOSCH_LONG_TX_MSGS[] = {{0xE4, 1, 5, .check_relay = true}, {0x1DF, 1, 8, .check_relay = true}, {0x1EF, 1, 8, .check_relay = false},
                                              {0x1FA, 1, 8, .check_relay = false}, {0x30C, 1, 8, .check_relay = false}, {0x33D, 1, 5, .check_relay = true}, {0x33D, 1, 8, .check_relay = true},
                                              {0x33DA, 1, 5, .check_relay = true}, {0x33DB, 1, 8, .check_relay = true}, {0x39F, 1, 8, .check_relay = false},
                                              {0x18DAB0F1, 1, 8, .check_relay = false}};  // Bosch w/ gas and brakes

  static CanMsg HONDA_RADARLESS_TX_MSGS[] = {{0xE4, 0, 5, .check_relay = true}, {0x296, 2, 4, .check_relay = false}, {0x33D, 0, 8, .check_relay = true},
                                             {0x6CD5554, 0, 8, .check_relay = true}, {0xF31AA54, 0, 8, .check_relay = true},
                                             {0x6CD5557, 0, 8, .check_relay = true}};  // Bosch radarless (HUD_OBJECTS authored in stock ACC too)

  static CanMsg HONDA_RADARLESS_LONG_TX_MSGS[] = {{0xE4, 0, 5, .check_relay = true}, {0x33D, 0, 8, .check_relay = true}, {0x1C8, 0, 8, .check_relay = true},
                                                  {0x30C, 0, 8, .check_relay = true}, {0x296, 2, 4, .check_relay = false}, {0x6CD5554, 0, 8, .check_relay = true},
                                                  {0xF31AA54, 0, 8, .check_relay = true}, {0x6CD5557, 0, 8, .check_relay = true}};  // Bosch radarless w/ gas and brakes

  // 0x296 on bus 2: OP takes over SCM_BUTTONS towards the camera to auto-disable stock LKAS and to block
  // the driver's LKAS button while engaged (the physical SCM_BUTTONS is blocked from forwarding, see fwd hook)
  static CanMsg HONDA_CANFD_TX_MSGS[] = {{0xE4, 0, 5, .check_relay = true}, {0x296, 0, 4, .check_relay = false}, {0x296, 2, 4, .check_relay = false},
                                         {0x33D, 0, 8, .check_relay = true}}; // Bosch CANFD

  // The radar look-alikes (0x310, 0x6CD5558, 0x6CD5559, 0xF31AA52, 0xF31AA5C, 0x1A45AA4E) are consumed by both
  // the camera (behind the relay on the camera bus, 2) and the powertrain (radar bus, 0). openpilot TX is not
  // forwarded across the open relay, so each is sent on both buses; the control messages stay on bus 0.
  static CanMsg HONDA_CANFD_LONG_TX_MSGS[] = {{0xE4, 0, 5, .check_relay = true}, {0x1DF, 0, 8, .check_relay = true}, {0x1EF, 0, 8, .check_relay = false},
                                              {0x30C, 0, 8, .check_relay = false}, {0x33D, 0, 8, .check_relay = true}, {0x296, 2, 4, .check_relay = false},
                                              {0x18DAB0F1, 0, 8, .check_relay = false},
                                              {0x310, 0, 8, .check_relay = false}, {0x6CD5558, 0, 8, .check_relay = true}, {0x6CD5559, 0, 8, .check_relay = false},
                                              {0xF31AA52, 0, 8, .check_relay = false}, {0xF31AA5C, 0, 8, .check_relay = true}, {0x1A45AA4E, 0, 8, .check_relay = false},
                                              {0x310, 2, 8, .check_relay = false}, {0x6CD5558, 2, 8, .check_relay = true}, {0x6CD5559, 2, 8, .check_relay = false},
                                              {0xF31AA52, 2, 8, .check_relay = false}, {0xF31AA5C, 2, 8, .check_relay = true}, {0x1A45AA4E, 2, 8, .check_relay = false}};

  const uint16_t HONDA_PARAM_ALT_BRAKE = 1;
  const uint16_t HONDA_PARAM_RADARLESS = 8;
  const uint16_t HONDA_PARAM_BOSCH_CANFD = 16;
  const uint16_t HONDA_PARAM_NO_ENGINE_DATA_MSG = 128;

  // Bosch radarless and CAN-FD have the powertrain bus on bus 0
  static RxCheck honda_bosch_pt0_rx_checks[] = {
    HONDA_COMMON_RX_CHECKS(0)
  };

  static RxCheck honda_bosch_pt0_alt_brake_rx_checks[] = {
    HONDA_COMMON_RX_CHECKS(0)
    HONDA_ALT_BRAKE_ADDR_CHECK(0)
  };

  // Only used by no-engine-data radarless configurations (e.g. Integra).
  static RxCheck honda_bosch_radarless_no_engine_data_rx_checks[] = {
    HONDA_NO_ENGINE_DATA_RX_CHECKS(0)
  };

  // Bosch has powertrain on bus 1, verified 0x1A6 does not exist
  static RxCheck honda_bosch_pt1_rx_checks[] = {
    HONDA_COMMON_RX_CHECKS(1)
  };

  static RxCheck honda_bosch_pt1_alt_brake_rx_checks[] = {
    HONDA_COMMON_RX_CHECKS(1)
    HONDA_ALT_BRAKE_ADDR_CHECK(1)
  };

  honda_hw = HONDA_BOSCH;
  honda_brake_switch_prev = false;
  honda_op_buttons_fresh = 0;
  honda_bosch_radarless = GET_FLAG(param, HONDA_PARAM_RADARLESS);
  honda_bosch_canfd = GET_FLAG(param, HONDA_PARAM_BOSCH_CANFD);
  honda_no_engine_data_msg = GET_FLAG(param, HONDA_PARAM_NO_ENGINE_DATA_MSG);
  honda_abs_prev_fl = 0U;
  honda_abs_prev_fr = 0U;
  honda_abs_prev_rl = 0U;
  honda_abs_prev_rr = 0U;
  honda_abs_prev_counter_checksum = 0xFFU;
  // Checking for alternate brake override from safety parameter
  honda_alt_brake_msg = GET_FLAG(param, HONDA_PARAM_ALT_BRAKE);
  honda_stock_longitudinal = false;
  honda_gas_interceptor_threshold_512 = false;

  // radar disabled so allow gas/brakes
#ifdef ALLOW_DEBUG
  const uint16_t HONDA_PARAM_BOSCH_LONG = 2;
  honda_bosch_long = GET_FLAG(param, HONDA_PARAM_BOSCH_LONG);
#endif

  safety_config ret;
  if (honda_no_engine_data_msg && honda_bosch_radarless) {
    SET_RX_CHECKS(honda_bosch_radarless_no_engine_data_rx_checks, ret);
  } else if (honda_bosch_radarless || honda_bosch_canfd) {
    if (honda_alt_brake_msg) {
      SET_RX_CHECKS(honda_bosch_pt0_alt_brake_rx_checks, ret);
    } else {
      SET_RX_CHECKS(honda_bosch_pt0_rx_checks, ret);
    }
  } else {
   if (honda_alt_brake_msg) {
     SET_RX_CHECKS(honda_bosch_pt1_alt_brake_rx_checks, ret);
   } else {
     SET_RX_CHECKS(honda_bosch_pt1_rx_checks, ret);
   }
  }

  if (honda_bosch_radarless) {
    if (honda_bosch_long) {
      SET_TX_MSGS(HONDA_RADARLESS_LONG_TX_MSGS, ret);
    } else {
      SET_TX_MSGS(HONDA_RADARLESS_TX_MSGS, ret);
    }
  } else if (honda_bosch_canfd) {
    if (honda_bosch_long) {
      SET_TX_MSGS(HONDA_CANFD_LONG_TX_MSGS, ret);
    } else {
      SET_TX_MSGS(HONDA_CANFD_TX_MSGS, ret);
    }
  } else {
    if (honda_bosch_long) {
      SET_TX_MSGS(HONDA_BOSCH_LONG_TX_MSGS, ret);
    } else {
      SET_TX_MSGS(HONDA_BOSCH_TX_MSGS, ret);
    }
  }
  return ret;
}

static bool honda_nidec_fwd_hook(int bus_num, int addr) {
  bool block_msg = false;

  if (bus_num == 2) {
    // forwarded if stock AEB is active
    bool is_brake_msg = addr == 0x1FA;
    block_msg = is_brake_msg && !honda_fwd_brake && !honda_stock_longitudinal;
  }

  return block_msg;
}

const safety_hooks honda_nidec_hooks = {
  .init = honda_nidec_init,
  .rx = honda_rx_hook,
  .tx = honda_tx_hook,
  .fwd = honda_nidec_fwd_hook,
  .get_counter = honda_get_counter,
  .get_checksum = honda_get_checksum,
  .compute_checksum = honda_compute_checksum,
};

static bool honda_bosch_fwd_hook(int bus_num, int addr) {
  bool block_msg = false;

  // On radarless and CAN FD, OP takes over SCM_BUTTONS (0x296) towards the camera when engaged, to
  // auto-disable stock LKAS and block the driver's LKAS button (the touch-steering-wheel timer would
  // otherwise force a disengagement). Only block the stock buttons while OP's replacement stream is
  // actually flowing (honda_op_buttons_fresh): the camera needs SCM_BUTTONS content beyond the buttons
  // (it raises an adaptive high beam error when the message goes missing), so a bare controls_allowed
  // gate would starve it whenever the panda allows controls but OP refuses to engage.
  if ((honda_bosch_radarless || honda_bosch_canfd) && controls_allowed && (honda_op_buttons_fresh > 0) &&
      (bus_num == 0) && (addr == 0x296)) {
    block_msg = true;
  }

  // CAN FD: the radar disable handshake happens after the relay is open, so block the radar's UDS
  // responses from forwarding to the camera (the camera doesn't need them)
  if (honda_bosch_canfd && (bus_num == 0) && (addr == 0x18DAF1B0)) {
    block_msg = true;
  }

  return block_msg;
}

const safety_hooks honda_bosch_hooks = {
  .init = honda_bosch_init,
  .rx = honda_rx_hook,
  .tx = honda_tx_hook,
  .fwd = honda_bosch_fwd_hook,
  .get_counter = honda_get_counter,
  .get_checksum = honda_get_checksum,
  .compute_checksum = honda_compute_checksum,
};
