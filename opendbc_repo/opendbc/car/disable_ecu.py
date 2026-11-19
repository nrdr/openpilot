from opendbc.car.can_definitions import CanData
from opendbc.car.carlog import carlog
from opendbc.car.isotp_parallel_query import IsoTpParallelQuery

EXT_DIAG_REQUEST = b'\x10\x03'
EXT_DIAG_RESPONSE = b'\x50\x03'

COM_CONT_RESPONSE = b''

# UDS 0x14 ClearDiagnosticInformation for all DTC groups (0xFFFFFF), positive response 0x54
CLEAR_DTC_REQUEST = b'\x14\xff\xff\xff'
CLEAR_DTC_RESPONSE = b'\x54'

# 29-bit functional (broadcast) diagnostic address; targets every ECU on the bus
FUNCTIONAL_ADDR_29BIT = 0x18DB33F1
# ISO-TP single frame carrying CLEAR_DTC_REQUEST (0x14 ClearDiagnosticInformation, all groups)
CLEAR_DTC_ISOTP_SF = bytes([len(CLEAR_DTC_REQUEST)]) + CLEAR_DTC_REQUEST + b'\x00' * (7 - len(CLEAR_DTC_REQUEST))


def clear_all_dtcs(can_send, buses, functional_addr=FUNCTIONAL_ADDR_29BIT):
  """Broadcast UDS 0x14 ClearDiagnosticInformation (all DTC groups) to every ECU on the given buses
  using the functional (broadcast) address. Best-effort; no responses are collected.

  This is used to clear stored DTCs that other ECUs may have latched due to a disabled radar, so they
  don't report stale faults on a later drive.

  WARNING: this clears stored DTCs on ALL ECUs on the bus, including unrelated and safety-relevant
  modules, so genuine fault codes are erased too. Only use it when you specifically need to clear
  cross-ECU faults."""
  for bus in buses:
    carlog.warning(f"clear all DTCs (functional) on bus {bus} ...")
    can_send([CanData(functional_addr, CLEAR_DTC_ISOTP_SF, bus)])


def clear_ecu_dtcs(can_recv, can_send, bus=0, addr=0x7d0, sub_addr=None, timeout=0.1, retry=10):
  """Enter the extended diagnostic session and clear an ECU's stored DTCs (UDS 0x14), without
  disabling its communication."""
  carlog.warning(f"ecu clear DTCs {hex(addr), sub_addr} ...")

  for i in range(retry):
    try:
      query = IsoTpParallelQuery(can_send, can_recv, bus, [(addr, sub_addr)], [EXT_DIAG_REQUEST], [EXT_DIAG_RESPONSE])

      for _, _ in query.get_data(timeout).items():
        carlog.warning("clear diagnostic information ...")
        query = IsoTpParallelQuery(can_send, can_recv, bus, [(addr, sub_addr)], [CLEAR_DTC_REQUEST], [CLEAR_DTC_RESPONSE])
        query.get_data(timeout)

        carlog.warning("ecu DTCs cleared")
        return True

    except Exception:
      carlog.exception("ecu clear DTCs exception")

    carlog.error(f"ecu clear DTCs retry ({i + 1}) ...")
  carlog.error("ecu clear DTCs failed")
  return False


def disable_ecu(can_recv, can_send, bus=0, addr=0x7d0, sub_addr=None, com_cont_req=b'\x28\x83\x01', timeout=0.1, retry=10, clear_dtc=False):
  """Silence an ECU by disabling sending and receiving messages using UDS 0x28.
  The ECU will stay silent as long as openpilot keeps sending Tester Present.

  This is used to disable the radar in some cars. Openpilot will emulate the radar.
  WARNING: THIS DISABLES AEB!

  When clear_dtc is set, stored DTCs are cleared (UDS 0x14) after entering the extended
  diagnostic session and before disabling communication. This prevents stale fault codes
  accumulated while the ECU was disabled from being reported on a later drive."""
  carlog.warning(f"ecu disable {hex(addr), sub_addr} ...")

  for i in range(retry):
    try:
      query = IsoTpParallelQuery(can_send, can_recv, bus, [(addr, sub_addr)], [EXT_DIAG_REQUEST], [EXT_DIAG_RESPONSE])

      for _, _ in query.get_data(timeout).items():
        # clear stored DTCs while the ECU can still process requests (before disabling comms)
        if clear_dtc:
          carlog.warning("clear diagnostic information ...")
          query = IsoTpParallelQuery(can_send, can_recv, bus, [(addr, sub_addr)], [CLEAR_DTC_REQUEST], [CLEAR_DTC_RESPONSE])
          query.get_data(timeout)

        carlog.warning("communication control disable tx/rx ...")

        query = IsoTpParallelQuery(can_send, can_recv, bus, [(addr, sub_addr)], [com_cont_req], [COM_CONT_RESPONSE])
        query.get_data(0)

        carlog.warning("ecu disabled")
        return True

    except Exception:
      carlog.exception("ecu disable exception")

    carlog.error(f"ecu disable retry ({i + 1}) ...")
  carlog.error("ecu disable failed")
  return False
