import serial
import time

ser = serial.Serial('/dev/ttyACM0', baudrate=38400, timeout=2)

def ubx_checksum(msg):
    ck_a, ck_b = 0, 0
    for byte in msg:
        ck_a = (ck_a + byte) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return bytes([ck_a, ck_b])

def send_ubx(msg):
    full = b'\xB5\x62' + msg
    full += ubx_checksum(msg)
    ser.write(full)

def read_response(timeout=2.0):
    start = time.time()
    buf = bytearray()
    while time.time() - start < timeout:
        if ser.in_waiting:
            buf.extend(ser.read(ser.in_waiting))
        time.sleep(0.05)
    return bytes(buf)

# ── 1. Poll port config ──────────────────────────────────────────
print("=== Polling USB port config ===")
send_ubx(bytes([0x06, 0x00, 0x01, 0x00, 0x03]))  # CFG-PRT poll USB
time.sleep(0.5)
raw = read_response(1.0)
print("Raw response:", raw.hex())

# ── 2. Enable RTCM3X input on USB port ──────────────────────────
print("\n=== Enabling RTCM3X input on USB ===")
# CFG-VALSET: RAM + Flash, key 0x10770004 (CFG-USBINPROT-RTCM3X) = 1
cfg_valset = bytes([
    0x06, 0x8A,              # CFG-VALSET class/id
    0x09, 0x00,              # length = 9
    0x00,                    # version
    0x03,                    # layers: RAM(1) + Flash(2)
    0x00, 0x00,              # reserved
    0x04, 0x00, 0x77, 0x10, # key: CFG-USBINPROT-RTCM3X
    0x01                     # value: enable
])
send_ubx(cfg_valset)
time.sleep(0.5)
raw = read_response(1.0)
print("Raw response:", raw.hex())
# Look for B5 62 05 01 = UBX-ACK-ACK (success)
# or      B5 62 05 00 = UBX-ACK-NAK (failure)
if b'\x05\x01' in raw:
    print("✓ RTCM3X input ENABLED")
elif b'\x05\x00' in raw:
    print("✗ NAK - command rejected, may need different key for your firmware version")
else:
    print("? No ACK received")

# ── 3. Enable RXM-RTCM output so we can see ACKs ────────────────
print("\n=== Enabling UBX-RXM-RTCM output on USB ===")
# CFG-VALSET: key 0x20910268 (CFG-MSGOUT-UBX_RXM_RTCM_USB) = 1
rxm_rtcm_out = bytes([
    0x06, 0x8A,
    0x09, 0x00,
    0x00,
    0x03,
    0x00, 0x00,
    0x68, 0x02, 0x91, 0x20,  # key: CFG-MSGOUT-UBX_RXM_RTCM_USB
    0x01                      # rate: 1
])
send_ubx(rxm_rtcm_out)
time.sleep(0.5)
raw = read_response(1.0)
if b'\x05\x01' in raw:
    print("✓ RXM-RTCM output ENABLED")
elif b'\x05\x00' in raw:
    print("✗ NAK")

# ── 4. Watch for RXM-RTCM messages for 10 seconds ───────────────
print("\n=== Watching for RXM-RTCM ACKs (10s) ===")
start = time.time()
buf = bytearray()
while time.time() - start < 10:
    if ser.in_waiting:
        buf.extend(ser.read(ser.in_waiting))
    # Scan for UBX-RXM-RTCM (B5 62 02 32)
    i = 0
    while i < len(buf) - 10:
        if buf[i] == 0xB5 and buf[i+1] == 0x62 and buf[i+2] == 0x02 and buf[i+3] == 0x32:
            flags    = buf[i+6]
            msg_type = (buf[i+9] << 8) | buf[i+8]
            used     = bool(flags & 0x01)
            print(f"  RXM-RTCM: type={msg_type} {'ACCEPTED ✓' if used else 'NOT USED ✗'}")
            buf = buf[i+10:]
            i = 0
        else:
            i += 1
    time.sleep(0.05)

ser.close()
