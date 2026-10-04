"""Validation-only runtime probe; never included in the upstream contribution."""
import re
import subprocess
import sys

cases = [
    ("original small graph", "4\n4\n1 2 1\n4 1 2\n2 3 2\n1 3 5\n1 3\n", 3),
    ("isolated source equals target", "1\n0\n1 1\n", 0),
    ("unreachable directed target", "2\n0\n1 2\n", None),
    ("edge above signed 32-bit range", "2\n1\n1 2 2147483648\n1 2\n", 2147483648),
    ("edge wraps to a small int", "2\n1\n1 2 4294967301\n1 2\n", 4294967301),
    ("path above signed 32-bit range", "3\n2\n1 2 1500000000\n2 3 1500000000\n1 3\n", 3000000000),
    ("stale forward entry before frontiers meet", "7\n7\n1 2 10\n1 3 1\n3 2 1\n2 4 100\n4 5 100\n5 6 100\n6 7 100\n1 7\n", 402),
]
failures = 0
for name, data, expected in cases:
    result = subprocess.run([sys.argv[1]], input=data, text=True,
                            capture_output=True, timeout=10, check=False)
    match = re.search(r"Shortest Path Distance : (-?\d+)", result.stdout)
    actual = int(match.group(1)) if match else None
    passed = result.returncode == 0 and actual == expected
    if expected is None:
        passed = passed and "Target not reachable from source" in result.stdout
    print(f"{name}: exit={result.returncode} expected={expected} actual={actual} "
          f"{'PASS' if passed else 'FAIL'}", flush=True)
    if not passed:
        failures += 1
        print(result.stdout, result.stderr, flush=True)
print(f"RESULT {len(cases) - failures} passed, {failures} failed", flush=True)
sys.exit(1 if failures else 0)
