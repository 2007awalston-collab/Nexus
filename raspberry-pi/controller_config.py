# Fixed controller-to-player assignments.
#
# Replace these example MAC addresses with your real ESP32 controller IDs.
# Controller IDs must match the format printed by the ESP32 Serial Monitor.

FIXED_PLAYER_ASSIGNMENTS = {
    # "94:A9:90:68:A1:90": 1,
    # "AA:BB:CC:11:22:33": 2,
    # "DD:EE:FF:44:55:66": 3,
}

# Per-controller LED timing calibration in milliseconds.
#
# Use a negative number if that controller's LED is consistently late.
# Use a positive number if that controller's LED is consistently early.
#
# Example:
# LED_TIMING_OFFSETS_MS = {
#     "AA:BB:CC:11:22:33": -120,
# }
LED_TIMING_OFFSETS_MS = {
}
