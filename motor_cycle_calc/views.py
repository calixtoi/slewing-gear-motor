import math
from django.views.generic import TemplateView
from cover.models import DesignParameters


def ceiling_to_step(value, step):
    """Round value UP to the nearest multiple of step."""
    return math.ceil(value / step) * step


class MotorCycleCalcView(TemplateView):
    template_name = "motor_cycle_calc/calc.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        d = DesignParameters.objects.get(pk=1)

        # ────────────────────────────────────────────────────
        # FIXED CONSTANTS (not user-editable; engineering basis)
        # ────────────────────────────────────────────────────
        MOTOR_SPEED_MIN_RPM = 1390.0  # lower bound, 4-pole 50 Hz loaded
        MOTOR_SPEED_MAX_RPM = 1465.0  # upper bound, 4-pole 50 Hz loaded
        GEARBOX_EFFICIENCY = 0.90  # helical bevel gearbox efficiency
        POWER_TORQUE_CONSTANT = 9550.0  # kW = Nm × rpm ÷ 9550
        POWER_STEP_KW = 0.25  # IEC standard motor power series step
        DUTY_FRACTION = 0.25  # S3-25% → 25% of cycle time running

        # ────────────────────────────────────────────────────
        # STEP 0 — GOVERNING INPUTS
        # All values read from DesignParameters (Cover sheet).
        # ────────────────────────────────────────────────────
        T_peak_kNm = d.crane_peak_torque_substation_kNm  # 62 kNm
        T_peak_Nm = T_peak_kNm * 1000  # 62 000 Nm
        i_slew = d.slewing_ring_ratio_pm401  # 110
        share = d.motor_torque_share_fraction  # 0.30
        n_crane_min = d.crane_min_slewing_speed_rpm  # 0.20 rpm
        n_crane_max = d.crane_max_slewing_speed_rpm  # 0.40 rpm

        # ────────────────────────────────────────────────────
        # STEP 1 — CRANE SLEWING SPEED WINDOW
        # ────────────────────────────────────────────────────
        crane_speed_window = {
            "min_rpm": n_crane_min,
            "max_rpm": n_crane_max,
            "why": (
                "The minimum (0.20 rpm) is the lowest speed at which "
                "electrical slewing is practically useful. "
                "The maximum (0.40 rpm) is imposed by the crane tip "
                "velocity limit stated in design brief section 5. "
                "Exceeding 0.40 rpm risks unsafe tip speeds at the "
                "maximum crane radius."
            ),
        }

        # ────────────────────────────────────────────────────
        # STEP 2 — GEARMOTOR OUTPUT SPEED RANGE
        # ────────────────────────────────────────────────────
        n_gm_out_min = n_crane_min * i_slew  # 22.0 rpm
        n_gm_out_max = n_crane_max * i_slew  # 44.0 rpm
        gearmotor_speed = {
            "formula": "n_gearmotor = n_crane × i_slewing_ring",
            "min_rpm": n_gm_out_min,
            "max_rpm": n_gm_out_max,
            "derivation_min": f"{n_crane_min} rpm × {i_slew} = {n_gm_out_min:.1f} rpm",
            "derivation_max": f"{n_crane_max} rpm × {i_slew} = {n_gm_out_max:.1f} rpm",
            "why": (
                f"The slewing ring ratio of {i_slew}:1 (source: TGB "
                f"P26-04) means the gearmotor output shaft makes "
                f"{i_slew} revolutions for every one crane revolution. "
                f"To keep the crane between {n_crane_min} and "
                f"{n_crane_max} rpm, the gearmotor output must be "
                f"between {n_gm_out_min:.0f} and {n_gm_out_max:.0f} rpm. "
                f"A supplier gearmotor with output speed outside this "
                f"band will either spin the crane too slowly (below "
                f"{n_gm_out_min:.0f} rpm) or overspeed the crane tip "
                f"(above {n_gm_out_max:.0f} rpm)."
            ),
        }

        # ────────────────────────────────────────────────────
        # STEP 3 — GEARBOX INTERNAL RATIO RANGE
        # ────────────────────────────────────────────────────
        i_gb_min = MOTOR_SPEED_MIN_RPM / n_gm_out_max  # 1390 ÷ 44 = 31.59
        i_gb_max = MOTOR_SPEED_MAX_RPM / n_gm_out_min  # 1465 ÷ 22 = 66.59
        gearbox_ratio = {
            "formula_min": "i_gb_min = n_motor_min ÷ n_gearmotor_output_max",
            "formula_max": "i_gb_max = n_motor_max ÷ n_gearmotor_output_min",
            "min": i_gb_min,
            "max": i_gb_max,
            "derivation_min": (
                f"{MOTOR_SPEED_MIN_RPM:.0f} rpm ÷ {n_gm_out_max:.1f} rpm "
                f"= {i_gb_min:.2f}"
            ),
            "derivation_max": (
                f"{MOTOR_SPEED_MAX_RPM:.0f} rpm ÷ {n_gm_out_min:.1f} rpm "
                f"= {i_gb_max:.2f}"
            ),
            "why_motor_speed": (
                f"A 4-pole induction motor at 50 Hz has synchronous speed "
                f"1500 rpm. Under rated load, slip reduces this to "
                f"{MOTOR_SPEED_MIN_RPM:.0f}–{MOTOR_SPEED_MAX_RPM:.0f} rpm. "
                f"These are the extremes of the nameplate rated-speed band "
                f"for standard commercial motors in the 0.75–1.5 kW class "
                f"at 50 Hz."
            ),
            "why_bounds": (
                f"The MINIMUM ratio ({i_gb_min:.2f}) ensures that even when "
                f"the motor is at its slowest rated speed "
                f"({MOTOR_SPEED_MIN_RPM:.0f} rpm), the gearmotor output "
                f"does not exceed {n_gm_out_max:.0f} rpm (= 0.40 rpm crane "
                f"speed). "
                f"The MAXIMUM ratio ({i_gb_max:.2f}) ensures that even when "
                f"the motor is at its fastest rated speed "
                f"({MOTOR_SPEED_MAX_RPM:.0f} rpm), the gearmotor output "
                f"is at least {n_gm_out_min:.0f} rpm (= 0.20 rpm crane "
                f"speed). "
                f"Any ratio outside {i_gb_min:.2f}–{i_gb_max:.2f} means "
                f"that at some point within the motor's normal speed band, "
                f"the crane will operate outside its permitted speed window."
            ),
            "fail_example": (
                f"Example of a FAIL: ratio 28.22 (Transtecno ITB 423). "
                f"At rated motor speed 1400 rpm: gearmotor output = "
                f"1400 ÷ 28.22 = 49.6 rpm. "
                f"Crane speed = 49.6 ÷ {i_slew:.0f} = 0.451 rpm. "
                f"This exceeds the 0.40 rpm limit → FAIL."
            ),
        }

        # ────────────────────────────────────────────────────
        # STEP 4 — MOTOR RATED SPEED RANGE
        # ────────────────────────────────────────────────────
        motor_speed = {
            "min_rpm": MOTOR_SPEED_MIN_RPM,
            "max_rpm": MOTOR_SPEED_MAX_RPM,
            "why_poles": (
                "A 4-pole motor is the natural choice because the required "
                "output speed (22–44 rpm) combined with practical gearbox "
                "ratios (32–67) points to a motor speed of roughly "
                "1400–1450 rpm. This band matches the 4-pole IEC motor "
                "family exactly. A 2-pole motor (≈ 2900 rpm) would need a "
                "ratio of 66–132, which is commercially unusual for this "
                "torque class. A 6-pole motor (≈ 950 rpm) would need a "
                "ratio of 22–43, giving too little ratio margin."
            ),
            "why_range": (
                f"Synchronous speed of a 4-pole motor at 50 Hz: "
                f"120 × 50 Hz ÷ 4 poles = 1500 rpm. "
                f"Under rated load, slip reduces speed by 2–7%, giving "
                f"approximately {MOTOR_SPEED_MIN_RPM:.0f}–"
                f"{MOTOR_SPEED_MAX_RPM:.0f} rpm. "
                f"This is the commercial nameplate-speed band used for "
                f"gearbox ratio selection."
            ),
        }

        # ────────────────────────────────────────────────────
        # STEP 5 — TORQUE CHAIN
        # ────────────────────────────────────────────────────
        T_share_Nm = share * T_peak_Nm  # 18 600 Nm
        M_gm_req = T_share_Nm / i_slew  # 169.09 Nm
        M_gm_peak = T_peak_Nm / i_slew  # 563.64 Nm
        torque_chain = {
            "peak_torque_kNm": T_peak_kNm,
            "peak_torque_Nm": T_peak_Nm,
            "share_fraction": share,
            "share_percent": share * 100,
            "T_share_Nm": T_share_Nm,
            "derivation_T_share": (
                f"{share} × {T_peak_kNm:.0f} kNm × 1000 "
                f"= {T_share_Nm:,.0f} Nm"
            ),
            "M_gm_req": M_gm_req,
            "derivation_M_gm": (
                f"{T_share_Nm:,.0f} Nm ÷ {i_slew:.0f} "
                f"= {M_gm_req:.1f} Nm"
            ),
            "M_gm_peak": M_gm_peak,
            "derivation_M_peak": (
                f"{T_peak_Nm:,.0f} Nm ÷ {i_slew:.0f} "
                f"= {M_gm_peak:.1f} Nm"
            ),
            "why_30_percent": (
                "The PF200 crane (existing product) has proven reliable with "
                "a motor covering 35% of a 42 kNm peak slewing torque. "
                "The design rule for PM401 sets the motor share at a "
                "minimum of 30% of the worst-case peak (62 kNm, Substation "
                "operation). This is conservative relative to PF200 practice "
                "because the PM401 worst-case peak is 48% higher than PF200. "
                "Peak torques occur only during extreme dynamic events such "
                "as maximum platform acceleration. In steady slewing, the "
                "motor torque demand is substantially lower than the "
                "structural peak."
            ),
            "why_structural": (
                f"The 563.6 Nm structural requirement applies to the "
                f"gearmotor housing, output shaft, and gearbox internals. "
                f"During emergency braking or crane blockage, 100% of the "
                f"{T_peak_kNm:.0f} kNm structural peak may be transmitted "
                f"through the gearmotor. The gearbox must withstand this "
                f"without permanent deformation, even though it only needs "
                f"to deliver {M_gm_req:.1f} Nm continuously in operation."
            ),
        }

        # ────────────────────────────────────────────────────
        # STEP 6 — MOTOR RATED POWER RANGE
        # ────────────────────────────────────────────────────
        P_required_kW = (
            M_gm_req
            * n_gm_out_max
            / POWER_TORQUE_CONSTANT
            / GEARBOX_EFFICIENCY
        )
        P_selected_kW = ceiling_to_step(P_required_kW, POWER_STEP_KW)
        P_range_min = 1.00  # adopted minimum (kW)
        P_range_max = 1.50  # adopted maximum (kW)
        motor_power = {
            "formula": (
                "P_required = M_gm_required × n_gearmotor_output_max "
                "÷ 9550 ÷ η_gearbox"
            ),
            "P_required_kW": P_required_kW,
            "P_selected_kW": P_selected_kW,
            "P_range_min": P_range_min,
            "P_range_max": P_range_max,
            "derivation": (
                f"{M_gm_req:.2f} Nm × {n_gm_out_max:.0f} rpm "
                f"÷ {POWER_TORQUE_CONSTANT:.0f} "
                f"÷ {GEARBOX_EFFICIENCY:.2f} "
                f"= {P_required_kW:.3f} kW"
            ),
            "why_max_speed": (
                f"The calculation uses the MAXIMUM gearmotor output speed "
                f"({n_gm_out_max:.0f} rpm) because this gives the highest "
                f"power demand. At lower speeds the same torque requires "
                f"less power. Sizing for the maximum-speed point guarantees "
                f"the motor is not under-powered anywhere in the operating "
                f"window."
            ),
            "why_9550": (
                "9550 is the conversion constant between the mechanical "
                "units used in this calculation. It is derived from: "
                "Power (kilowatts) = Torque (Newton-metres) × Angular "
                "velocity (radians per second) ÷ 1000. Since angular "
                "velocity in rad/s = rpm × 2π ÷ 60, the constant becomes "
                "1000 ÷ (2π ÷ 60) = 60 000 ÷ (2π) ≈ 9549.3, rounded to "
                "9550 in engineering practice."
            ),
            "why_efficiency": (
                f"A helical bevel gearbox converts approximately "
                f"{GEARBOX_EFFICIENCY*100:.0f}% of the motor input power "
                f"into useful output power; the remaining "
                f"{(1-GEARBOX_EFFICIENCY)*100:.0f}% is lost as heat through "
                f"gear meshing and bearing friction. Dividing by "
                f"{GEARBOX_EFFICIENCY:.2f} scales the required output power "
                f"up to the required motor input power. This is a "
                f"conservative engineering estimate consistent with typical "
                f"catalogue values for this gear type."
            ),
            "why_range": (
                f"Required power = {P_required_kW:.3f} kW. "
                f"Rounded up to next 0.25 kW step = {P_selected_kW:.2f} kW. "
                f"Adopted acceptance range: {P_range_min:.2f}–"
                f"{P_range_max:.2f} kW. "
                f"The lower bound ({P_range_min:.2f} kW) is the minimum "
                f"standard IEC rating that covers the calculated requirement. "
                f"The upper bound ({P_range_max:.2f} kW) is one IEC step "
                f"above the lower bound, accepted to allow a thermal margin "
                f"without the motor being unnecessarily heavy or costly. "
                f"Motors above {P_range_max:.2f} kW are oversized for this "
                f"application."
            ),
        }

        # ────────────────────────────────────────────────────
        # STEP 7 — MOTOR RATED TORQUE RANGE
        # ────────────────────────────────────────────────────
        T_motor_min = POWER_TORQUE_CONSTANT * 0.75 / MOTOR_SPEED_MAX_RPM
        T_motor_max = POWER_TORQUE_CONSTANT * 1.50 / MOTOR_SPEED_MIN_RPM
        motor_torque = {
            "formula": (
                "Motor rated torque = 9550 × Motor rated power (kW) "
                "÷ Motor rated speed (rpm)"
            ),
            "min_Nm": T_motor_min,
            "max_Nm": T_motor_max,
            "derivation_min": (
                f"9550 × 0.75 kW ÷ {MOTOR_SPEED_MAX_RPM:.0f} rpm "
                f"= {T_motor_min:.2f} Nm"
            ),
            "derivation_max": (
                f"9550 × 1.50 kW ÷ {MOTOR_SPEED_MIN_RPM:.0f} rpm "
                f"= {T_motor_max:.2f} Nm"
            ),
            "why": (
                "This range is a verification envelope, not a primary "
                "design requirement. It is derived by applying the "
                "power-torque-speed formula across the full accepted power "
                "range (0.75–1.50 kW) and speed range "
                f"({MOTOR_SPEED_MIN_RPM:.0f}–{MOTOR_SPEED_MAX_RPM:.0f} rpm). "
                "A motor whose computed rated torque falls outside "
                f"{T_motor_min:.2f}–{T_motor_max:.2f} Nm is either too "
                "weak (below minimum) or so heavily torque-biased that it "
                "would likely be under-speed and fail the gearbox ratio "
                "check as well."
            ),
        }

        # ────────────────────────────────────────────────────
        # STEP 8 — CRANE SLEWING SPEED (SUPPLIER BACK-CHECK)
        # ────────────────────────────────────────────────────
        crane_speed_check = {
            "formula": (
                "Crane slewing speed = "
                "Gearmotor output speed ÷ Slewing ring gear ratio"
            ),
            "min_rpm": n_crane_min,
            "max_rpm": n_crane_max,
            "why": (
                "This is the most direct verification: it converts the "
                "supplier's gearmotor output speed back into crane speed "
                "using the actual slewing ring ratio. Passing the gearbox "
                "ratio range check in Step 3 is necessary but not always "
                "sufficient — this step confirms the final crane speed "
                "with the actual supplier motor speed substituted in. "
                "A supplier whose gearbox ratio is within 31.59–66.59 but "
                "whose motor speed at rated load falls outside 1390–1465 rpm "
                "could still fail this check."
            ),
        }

        # ────────────────────────────────────────────────────
        # STEP 9 — DUTY CYCLE (THERMAL CHECK ONLY)
        # ────────────────────────────────────────────────────
        P_thermal_kW = P_required_kW * math.sqrt(DUTY_FRACTION)
        P_thermal_selected = ceiling_to_step(P_thermal_kW, POWER_STEP_KW)
        duty_cycle = {
            "duty_class": "S3-25%",
            "duty_fraction": DUTY_FRACTION,
            "P_operating_kW": P_required_kW,
            "P_thermal_kW": P_thermal_kW,
            "P_thermal_selected": P_thermal_selected,
            "derivation": (
                f"{P_required_kW:.3f} kW × √{DUTY_FRACTION:.2f} "
                f"= {P_required_kW:.3f} × {math.sqrt(DUTY_FRACTION):.3f} "
                f"= {P_thermal_kW:.3f} kW → select {P_thermal_selected:.2f} kW"
            ),
            "why_sqrt": (
                "Motor heating is governed by the root-mean-square (RMS) "
                "current over the operating cycle. Since current squared is "
                "proportional to power, the RMS power is the operating "
                "power multiplied by the square root of the duty fraction. "
                "At S3-25%, duty fraction = 0.25, √0.25 = 0.500. "
                "This halves the effective thermal power demand relative "
                "to continuous S1 operation. The mechanical torque "
                "requirement is unaffected by duty class — it must be met "
                "at the instant of operation regardless of how often "
                "the motor runs."
            ),
        }

        # ────────────────────────────────────────────────────
        # BUILD COMPLETE CONTEXT
        # ────────────────────────────────────────────────────
        ctx.update({
            "design": d,
            "crane_speed": crane_speed_window,
            "gearmotor_speed": gearmotor_speed,
            "gearbox_ratio": gearbox_ratio,
            "motor_speed": motor_speed,
            "torque_chain": torque_chain,
            "motor_power": motor_power,
            "motor_torque": motor_torque,
            "crane_speed_check": crane_speed_check,
            "duty_cycle": duty_cycle,
            "MOTOR_SPEED_MIN": MOTOR_SPEED_MIN_RPM,
            "MOTOR_SPEED_MAX": MOTOR_SPEED_MAX_RPM,
            "GEARBOX_EFF": GEARBOX_EFFICIENCY,
            "K": POWER_TORQUE_CONSTANT,
        })
        return ctx
