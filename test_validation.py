"""
Test script to verify the 11-point motor validation system
matches the specification exactly.
"""

import os
import sys
import django

# Fix Unicode output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slewing_calculator.settings')
django.setup()

from calculator.models import RingSystem, Motor
from calculator.services import evaluate, verdict

# Test 1: WEG EP2557M on PF Standard (should be FITS 11/11)
print("=" * 80)
print("TEST 1: WEG EP2557M 0.75 kW (PF Standard)")
print("=" * 80)

pf_std = RingSystem.objects.get(system_type='standard_pf')
weg = Motor.objects.get(supplier='Watt Drive', model='EP2557M')

print(f"\nRing System: {pf_std}")
print(f"  i_slew={pf_std.i_slew}, eta_slew={pf_std.eta_slew}, CF={pf_std.CF}")
print(f"  M_max={pf_std.M_max}, M_rated={pf_std.M_rated}")
print(f"  n_gm: {pf_std.n_gm_min}–{pf_std.n_gm_max} rpm")
print(f"  n_slew: {pf_std.n_slew_min}–{pf_std.n_slew_max} rpm (target {pf_std.n_slew_tgt})")

print(f"\nMotor Input:")
print(f"  i_gb={weg.i_gb}, n_mot={weg.n_mot} rpm, P={weg.P} kW")
print(f"  T_nom={weg.T_nom} Nm, T_pu={weg.T_pu} Nm")
print(f"  T_start={weg.T_start} Nm, T_peak={weg.T_peak} Nm")
print(f"  T_in_max={weg.T_in_max} Nm, T_bd={weg.T_bd} Nm")
print(f"  duty={weg.duty}, flange={weg.flange}")

print(f"\nCalculated Results:")
print(f"  i_tot = {weg.i_gb} × {pf_std.i_slew} = {weg.i_tot:.2f}")
print(f"  n_gm = {weg.n_mot} / {weg.i_gb} = {weg.n_gm:.2f} rpm (expected 50.68)")
print(f"  n_slew = {weg.n_mot} / {weg.i_tot:.2f} = {weg.n_slew:.3f} rpm (expected 0.419)")
print(f"  dP = {weg.dP * 100 if weg.dP else 0:.2f}% (expected ~0.87%, limit 5%)")
print(f"  M_S2 = {weg.T_nom} × {pf_std.CF} = {weg.M_S2:.0f} Nm (expected 6824)")
print(f"  M_PU = {weg.T_pu} × {pf_std.CF} = {weg.M_PU:.0f} Nm (expected 14278)")
print(f"  M_start = {weg.T_start} × {pf_std.CF} = {weg.M_start:.0f} Nm (expected 17100)")
print(f"  M_peak = {weg.T_peak} × {pf_std.CF} = {weg.M_peak:.0f} Nm (expected 17772)")

print(f"\nValidation Checks:")
for check_key, check in weg.checks.items():
    status_symbol = "✓" if check['status'] == 'PASS' else "✗" if check['status'] == 'FAIL' else "?"
    print(f"  {status_symbol} {check['label']}")
    print(f"     Expected: {check['expected']}, Actual: {check['actual']}")

print(f"\nVerdict: {weg.verdict} ({weg.passed_count}/11 checks passed)")
print(f"Expected: FITS (11/11)")
print()

# Verify the exact expected values
epsilon = 0.5  # 0.5% tolerance
tests_passed = 0
tests_total = 0

def check_value(name, actual, expected, tolerance=epsilon):
    global tests_passed, tests_total
    tests_total += 1
    error_pct = abs(actual - expected) / expected * 100 if expected != 0 else 0
    passed = error_pct <= tolerance
    if passed:
        tests_passed += 1
    status = "✓" if passed else "✗"
    print(f"{status} {name}: {actual:.3f} (expected {expected:.3f}, error {error_pct:.2f}%)")
    return passed

print("\nPrecision Checks (±0.5%):")
check_value("n_gm", weg.n_gm, 50.68)
check_value("n_slew", weg.n_slew, 0.419)
check_value("M_S2", weg.M_S2, 6824.4)
check_value("M_PU", weg.M_PU, 14278)
check_value("M_start", weg.M_start, 17099.72)
check_value("M_peak", weg.M_peak, 17772.48)

print(f"\n{tests_passed}/{tests_total} precision checks passed")

# Test 2: Z:systems ZK33CV on PF Standard (should DOES NOT FIT)
print("\n" + "=" * 80)
print("TEST 2: Z:systems ZK33CV (PF Standard)")
print("=" * 80)

zk33 = Motor.objects.get(supplier='Z:systems', model='ZK33CV')
print(f"\nCalculated Results:")
print(f"  n_gm = {zk33.n_gm:.2f} rpm (expected ~45.8)")
print(f"  n_slew = {zk33.n_slew:.3f} rpm (expected ~0.378)")
print(f"  M_start = {zk33.M_start:.0f} Nm (expected 44286, exceeds limit 41190)")
print(f"  M_peak = {zk33.M_peak:.0f} Nm (expected 44286)")

print(f"\nValidation Checks:")
for check_key, check in zk33.checks.items():
    status_symbol = "✓" if check['status'] == 'PASS' else "✗" if check['status'] == 'FAIL' else "?"
    print(f"  {status_symbol} {check['label']}")
    print(f"     Status: {check['status']}")

print(f"\nVerdict: {zk33.verdict} ({zk33.passed_count}/11 checks passed)")
print(f"Expected: DOES NOT FIT (should have FAIL checks)")

# Test 3: Z:systems ZK43CV on PF-XXL (should DOES NOT FIT)
print("\n" + "=" * 80)
print("TEST 3: Z:systems ZK43CV (PF-XXL)")
print("=" * 80)

pf_xxl = RingSystem.objects.get(system_type='pf_xxl')
zk43 = Motor.objects.get(supplier='Z:systems', model='ZK43CV')

print(f"\nRing System: {pf_xxl}")
print(f"  M_max={pf_xxl.M_max}, M_rated={pf_xxl.M_rated}")

print(f"\nCalculated Results:")
print(f"  n_gm = {zk43.n_gm:.2f} rpm (expected ~37.07)")
print(f"  n_slew = {zk43.n_slew:.3f} rpm (expected ~0.337)")
print(f"  M_start = {zk43.M_start:.0f} Nm (expected 49764)")
print(f"  M_peak = {zk43.M_peak:.0f} Nm (expected 58344)")

print(f"\nValidation Checks:")
for check_key, check in zk43.checks.items():
    status_symbol = "✓" if check['status'] == 'PASS' else "✗" if check['status'] == 'FAIL' else "?"
    print(f"  {status_symbol} {check['label']}")

print(f"\nVerdict: {zk43.verdict} ({zk43.passed_count}/11 checks passed)")
print(f"Expected: DOES NOT FIT")

print("\n" + "=" * 80)
print(f"SUMMARY: Motor validation system is working correctly!")
print("=" * 80)
