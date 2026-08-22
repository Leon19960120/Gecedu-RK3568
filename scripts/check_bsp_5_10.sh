#!/bin/sh
# Read-only BSP 5.10 runtime inspection helper for GecEdu RK3568.
set -u

section() {
    printf '\n== %s ==\n' "$1"
}

run() {
    printf '$ %s\n' "$*"
    "$@" 2>&1 || true
}

section "Kernel"
run uname -a
if [ -r /proc/device-tree/model ]; then
    printf 'model: '
    tr -d '\0' < /proc/device-tree/model
    printf '\n'
fi
if [ -r /proc/device-tree/compatible ]; then
    printf 'compatible:\n'
    tr '\0' '\n' < /proc/device-tree/compatible
fi

section "IIO"
for dev in /sys/bus/iio/devices/iio:device*; do
    [ -e "$dev" ] || continue
    name="$(cat "$dev/name" 2>/dev/null || echo unknown)"
    printf '%s name=%s\n' "$dev" "$name"
    ls "$dev" 2>/dev/null | sed 's/^/  /'
done

section "I2C Clients"
for client in /sys/bus/i2c/devices/[0-9]-*; do
    [ -e "$client" ] || continue
    name="$(cat "$client/name" 2>/dev/null || echo unknown)"
    if [ -L "$client/driver" ]; then
        driver="$(basename "$(readlink "$client/driver")")"
    else
        driver="UNBOUND"
    fi
    printf '%s name=%s driver=%s\n' "$(basename "$client")" "$name" "$driver"
done

section "Key I2C Targets"
for id in 0-0051 1-005d 2-0023 2-0050 2-0069; do
    path="/sys/bus/i2c/devices/$id"
    if [ -e "$path" ]; then
        name="$(cat "$path/name" 2>/dev/null || echo unknown)"
        if [ -L "$path/driver" ]; then
            driver="$(basename "$(readlink "$path/driver")")"
        else
            driver="UNBOUND"
        fi
        printf '%s present name=%s driver=%s\n' "$id" "$name" "$driver"
    else
        printf '%s missing\n' "$id"
    fi
done

section "Input"
if [ -r /proc/bus/input/devices ]; then
    cat /proc/bus/input/devices
else
    echo "/proc/bus/input/devices not available"
fi

section "RTC"
for rtc in /sys/class/rtc/rtc*; do
    [ -e "$rtc" ] || continue
    name="$(cat "$rtc/name" 2>/dev/null || echo unknown)"
    printf '%s name=%s\n' "$(basename "$rtc")" "$name"
done

section "DRM"
run ls /sys/class/drm

section "CAN"
if command -v ip >/dev/null 2>&1; then
    run ip -details link show type can
else
    echo "ip command not found"
fi

section "Important dmesg Lines"
if command -v dmesg >/dev/null 2>&1; then
    dmesg | grep -iE 'rk3568|rockchip-drm|dw-mipi|panel|goodix|gt911|mpu6050|bh1750|pcf8563|rtc|saradc|rknpu|can|failed|error|defer|warn' | tail -200 || true
else
    echo "dmesg command not found"
fi
