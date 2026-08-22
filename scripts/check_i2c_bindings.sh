#!/bin/sh
# Read-only helper: list I2C clients that do not currently have a bound driver.
set -u

printf 'I2C clients without driver binding:\n'
found=0

for client in /sys/bus/i2c/devices/[0-9]-*; do
    [ -e "$client" ] || continue
    [ -L "$client/driver" ] && continue
    name="$(cat "$client/name" 2>/dev/null || echo unknown)"
    of_node="no"
    [ -e "$client/of_node" ] && of_node="yes"
    printf '%s name=%s of_node=%s\n' "$(basename "$client")" "$name" "$of_node"
    found=1
done

if [ "$found" -eq 0 ]; then
    echo "none"
fi

printf '\nKey expected clients:\n'
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
