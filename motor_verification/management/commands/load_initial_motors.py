from django.core.management.base import BaseCommand
from motor_verification.models import MotorSupplier


class Command(BaseCommand):
    help = (
        "Load the four pre-evaluated motor options into the database. "
        "Safe to re-run — existing records with the same motor_model "
        "are skipped."
    )

    def handle(self, *args, **options):
        motors = self._get_motor_data()
        created = 0
        skipped = 0
        for data in motors:
            obj, new = MotorSupplier.objects.get_or_create(
                motor_model=data["motor_model"],
                defaults=data,
            )
            if new:
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(f" Created: {obj.motor_model}")
                )
            else:
                skipped += 1
                self.stdout.write(
                    f" Skipped (already exists): {obj.motor_model}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {created} created, {skipped} skipped."
            )
        )

    # ──────────────────────────────────────────────────────
    def _get_motor_data(self):
        return [
            self._keb_dm90sd4(),
            self._keb_dm90lb4(),
            self._weg_ep2557m(),
            self._transtecno_itb423(),
        ]

    # ════════════════════════════════════════════════════════
    # MOTOR 1 — KEB K43A DM90SD4 (1.1 kW)
    # ════════════════════════════════════════════════════════
    def _keb_dm90sd4(self):
        return {
            # ── IDENTIFICATION ────────────────────────────
            "supplier_name": "KEB",
            "motor_model": "KEB K43A DM90SD4 (1.1 kW)",
            "datasheet_source": (
                "ct_gm-2023_de.pdf — KEB gearmotor catalogue "
                "tables pp. 54–55; motor table p. 94"
            ),
            "notes": (
                "OVERALL RESULT: CONDITIONAL — passes all calculated "
                "performance checks; several non-standard executions must "
                "be ordered as options or confirmed with KEB before purchase. "
                "Key items to confirm with KEB:\n"
                " 1. IP66 protection (catalogue lists IP65; IP66 is an option "
                "— confirm availability on K43A housing)\n"
                " 2. TENV / IC410 unventilated execution (catalogue standard "
                "is TEFC / IC411 with shaft fan; unventilated version must be "
                "ordered as special execution)\n"
                " 3. C5H corrosion protection paint system per EN 12944-5 "
                "(catalogue standard finish differs; C5H must be specified "
                "as a surface protection option)\n"
                " 4. RAL7035 colour (catalogue standard is RAL7031 dark grey; "
                "RAL7035 light grey must be specified)\n"
                " 5. Output flange IEC 200 square, hole circle Ø165 mm, "
                "4×Ø11 mm (non-standard; must be ordered as custom flange)\n"
                " 6. Output shaft Ø32 k6 × 50 mm length (non-standard; "
                "confirm against K43A catalogue shaft options)\n"
                " 7. Left-side input flange: square IEC 150, Ø165 bolt "
                "circle, 4×Ø12 through-holes, R15 corners, Ø32 F8 bore, "
                "10 H9 keyway (non-standard; must be specified)\n"
                " 8. Supply voltages 400 / 480 / 690 V and frequency "
                "50 / 60 Hz (catalogue extract is 400 V / 50 Hz basis; "
                "dual-voltage D/Y winding and 60 Hz rating to confirm)\n"
                " 9. D/Y winding connection (confirm 400 V Delta / "
                "690 V Star)\n"
                " 10. Anti-condensation heater ~25 W, 24 V DC "
                "(not standard in catalogue; must be ordered as option)\n"
                " 11. Heater terminal blocks inside terminal box\n"
                " 12. Terminal box orientation: mounted vertically downward "
                "on NDE side, cable entry pointing downward\n"
                " 13. Mounting position: confirm exact designation\n"
                " 14. CE marking + EN 10204 Type 3.1 material certificate "
                "(supplier to provide both)\n"
                " 15. Duty cycle S3-25%: confirm thermal suitability "
                "of the selected motor frame at S3-25% with TENV execution\n"
                " 16. Total gearmotor weight (motor alone ~24 kg; "
                "confirm combined weight)"
            ),
            # ── GEAR DATA ──────────────────────────────────
            "gear_series": "Helical bevel geared motor K43A",
            "gearmotor_output_speed_rpm": 33.0,
            "gearmotor_output_torque_nm": 315.0,
            "gearbox_internal_ratio": 43.37,
            "max_permissible_input_speed_rpm": 1445.0,
            "mounting_position": "Supplier to confirm exact mounting position",
            "output_flange_description": (
                "IEC 200 square flange, hole circle Ø165 mm, 4×Ø11 mm holes "
                "— not confirmed against catalogue; must be specified as "
                "custom option when ordering"
            ),
            "output_shaft_description": (
                "Ø32 k6 × 50 mm — not confirmed against K43A catalogue "
                "shaft options; must be specified when ordering"
            ),
            "keyway_standard": "DIN 6885-1 — supplier to confirm",
            "painting_system": (
                "C5H per EN 12944-5 — must be specified as option; "
                "catalogue standard protection differs"
            ),
            "colour_ral": (
                "RAL7035 — must be specified; catalogue standard is RAL7031"
            ),
            # ── INPUT SIDE ─────────────────────────────────
            "input_flange_description": (
                "Left input flange: square IEC 150; Ø165 bolt circle; "
                "4×Ø12 through-holes; R15 corner radius; Ø32 F8 bore; "
                "10 H9 keyway — not confirmed against catalogue; "
                "must be specified as custom option"
            ),
            # ── MOTOR DATA ─────────────────────────────────
            "housing_material": "Cast iron — not stated in extracted catalogue data; to confirm",
            "duty_cycle": "S3-25% required; catalogue motor data is 50 Hz S1 base; thermal suitability at S3-25% with TENV execution to confirm with KEB",
            "efficiency_class": "IE3",
            "motor_rated_power_kw": 1.1,
            "motor_rated_speed_rpm": 1445.0,
            "supply_voltage_v": "400 V confirmed in catalogue; 480 V and 690 V to confirm with KEB",
            "supply_frequency_hz": "50 Hz confirmed; 60 Hz to confirm with KEB",
            "winding_connection": "D/Y — supplier to confirm 400 V Delta / 690 V Star",
            "protection_class": "IP65 shown in catalogue; IP66 to confirm as option with KEB",
            "terminal_box_position": "Supplier to confirm: mounted vertically downward on NDE side with downward cable entry",
            "cable_entries": "M25×1.5 and M16×1.5 — supplier to confirm entries and blind-plug supply",
            # ── FURTHER EXECUTIONS ────────────────────────
            "cooling_method": (
                "TEFC (IC411) in standard catalogue; TENV / IC410 "
                "unventilated execution required — must be ordered as "
                "special execution; confirm availability with KEB"
            ),
            "heater_spec": "~25 W, 24 V DC — not in standard catalogue; must be ordered as option",
            "total_weight_kg": None,
            # ── GENERAL ────────────────────────────────────
            "certifications": "CE mandatory — supplier to provide; EN 10204 Type 3.1 material certificate required",
            "temperature_range": "-20°C to +50°C — supplier to confirm",
            "corrosivity_category": "C5H per DIN EN ISO 12944-5 — must be specified; catalogue standard differs",
            "rotation": "CW and CCW — supplier to confirm",
            "starting_method": "Direct-on-line start (catalogue shows Ma/Mn starting torque data)",
            "heater_terminal_blocks": "Supplier to provide two dedicated heater terminal blocks inside motor terminal box",
            "gearbox_structural_capacity_nm": 756.0,
        }

    # ════════════════════════════════════════════════════════
    # MOTOR 2 — KEB K43A DM90LB4 (1.5 kW)
    # ════════════════════════════════════════════════════════
    def _keb_dm90lb4(self):
        return {
            "supplier_name": "KEB",
            "motor_model": "KEB K43A DM90LB4 (1.5 kW)",
            "datasheet_source": (
                "ct_gm-2023_de.pdf — KEB gearmotor catalogue "
                "tables pp. 54–55; motor table p. 94"
            ),
            "notes": (
                "OVERALL RESULT: CONDITIONAL — passes all calculated "
                "performance checks; same non-standard executions as the "
                "DM90SD4 must be confirmed with KEB. "
                "This is the 1.5 kW variant of the same K43A gearbox frame. "
                "The larger motor frame (90L vs 90S) and lower ratio (33.43 "
                "vs 43.37) push the output speed to the top of the "
                "acceptance window (44.0 rpm = 0.40 rpm crane speed). "
                "There is no margin above 0.40 rpm — this motor produces "
                "exactly the maximum acceptable crane speed at rated motor "
                "speed. Any slight motor overspeed (e.g. at light load) "
                "would exceed the limit."
            ),
            "gear_series": "Helical bevel geared motor K43A",
            "gearmotor_output_speed_rpm": 44.0,
            "gearmotor_output_torque_nm": 330.0,
            "gearbox_internal_ratio": 33.43,
            "max_permissible_input_speed_rpm": 1455.0,
            "mounting_position": "Supplier to confirm exact mounting position",
            "output_flange_description": (
                "IEC 200 square flange, hole circle Ø165 mm, 4×Ø11 mm holes "
                "— not confirmed against catalogue; must be specified as "
                "custom option when ordering"
            ),
            "output_shaft_description": (
                "Ø32 k6 × 50 mm — not confirmed against K43A catalogue "
                "shaft options; must be specified when ordering"
            ),
            "keyway_standard": "DIN 6885-1 — supplier to confirm",
            "painting_system": (
                "C5H per EN 12944-5 — must be specified as option; "
                "catalogue standard protection differs"
            ),
            "colour_ral": "RAL7035 — must be specified; catalogue standard is RAL7031",
            "input_flange_description": (
                "Left input flange: square IEC 150; Ø165 bolt circle; "
                "4×Ø12 through-holes; R15 corner radius; Ø32 F8 bore; "
                "10 H9 keyway — not confirmed against catalogue; "
                "must be specified as custom option"
            ),
            "housing_material": "Cast iron — not stated in extracted catalogue data; to confirm",
            "duty_cycle": "S3-25% required; catalogue motor data is 50 Hz S1 base; thermal suitability at S3-25% with TENV execution to confirm with KEB",
            "efficiency_class": "IE3",
            "motor_rated_power_kw": 1.5,
            "motor_rated_speed_rpm": 1455.0,
            "supply_voltage_v": "400 V confirmed in catalogue; 480 V and 690 V to confirm with KEB",
            "supply_frequency_hz": "50 Hz confirmed; 60 Hz to confirm with KEB",
            "winding_connection": "D/Y — supplier to confirm 400 V Delta / 690 V Star",
            "protection_class": "IP65 shown in catalogue; IP66 to confirm as option with KEB",
            "terminal_box_position": "Supplier to confirm: mounted vertically downward on NDE side with downward cable entry",
            "cable_entries": "M25×1.5 and M16×1.5 — supplier to confirm entries and blind-plug supply",
            "cooling_method": (
                "TEFC (IC411) in standard catalogue; TENV / IC410 "
                "unventilated execution required — confirm availability "
                "with KEB on 90L frame"
            ),
            "heater_spec": "~25 W, 24 V DC — not in standard catalogue; must be ordered as option",
            "total_weight_kg": None,
            "certifications": "CE mandatory — supplier to provide; EN 10204 Type 3.1 material certificate required",
            "temperature_range": "-20°C to +50°C — supplier to confirm",
            "corrosivity_category": "C5H per DIN EN ISO 12944-5 — must be specified; catalogue standard differs",
            "rotation": "CW and CCW — supplier to confirm",
            "starting_method": "Direct-on-line start (catalogue shows Ma/Mn data)",
            "heater_terminal_blocks": "Supplier to provide two dedicated heater terminal blocks inside motor terminal box",
            "gearbox_structural_capacity_nm": 759.0,
        }

    # ════════════════════════════════════════════════════════
    # MOTOR 3 — WEG EP2557M (reference)
    # ════════════════════════════════════════════════════════
    def _weg_ep2557m(self):
        return {
            "supplier_name": "WEG",
            "motor_model": "WEG EP2557M (reference — does not fit)",
            "datasheet_source": "INF_EP-2557M_A.pdf — WEG reference gearmotor datasheet",
            "notes": (
                "OVERALL RESULT: DOES NOT FIT — three hard engineering FAILs.\n\n"
                "This is a REFERENCE unit only, evaluated to understand "
                "the WEG product range and why it cannot be used.\n\n"
                "FAIL 1 — Gearbox ratio 27.82 is BELOW the minimum 31.59.\n"
                " Minimum ratio = 1390 rpm (minimum motor speed) "
                "÷ 44 rpm (maximum gearmotor output speed) = 31.59.\n"
                " WEG ratio 27.82 < 31.59 minimum → the gearmotor spins "
                "faster than the maximum allowed output speed at any motor "
                "speed in the accepted band.\n\n"
                "FAIL 2 — Gearmotor output speed 51 rpm EXCEEDS the 44 rpm "
                "maximum.\n"
                " At rated motor speed 1410 rpm with ratio 27.82: "
                "output = 1410 ÷ 27.82 = 50.7 rpm ≈ 51 rpm.\n"
                " Crane speed = 51 ÷ 110 = 0.464 rpm > 0.40 rpm limit.\n\n"
                "FAIL 3 — Gearbox output torque 141 Nm is BELOW the 169.1 Nm "
                "minimum.\n"
                " Required: 30% × 62 000 Nm ÷ 110 = 169.1 Nm.\n"
                " WEG delivers 141 Nm — 16% below the minimum.\n"
                " Structural capacity is also only 141 Nm, far below "
                "the 563.6 Nm structural requirement."
            ),
            "gear_series": "Helical bevel geared motors",
            "gearmotor_output_speed_rpm": 51.0,
            "gearmotor_output_torque_nm": 141.0,
            "gearbox_internal_ratio": 27.82,
            "max_permissible_input_speed_rpm": 1410.0,
            "mounting_position": "H522 (WEG designation)",
            "output_flange_description": "IEC 200 square Ø200 mm (confirmed in datasheet)",
            "output_shaft_description": "Ø32 k6 × 50 mm from flange surface (confirmed)",
            "keyway_standard": "DIN 6885-1 (confirmed)",
            "painting_system": "C5H confirmed in datasheet",
            "colour_ral": "RAL7035 Light Grey (confirmed)",
            "input_flange_description": (
                "Round IEC Ø160 mm — square IEC 150 flange (Ø165; 4×Ø12; "
                "Ø32 F8) is required but not confirmed for this model"
            ),
            "housing_material": "Cast iron",
            "duty_cycle": "S2-12 min (not S3-25% as required — CHECK with WEG for S3-25% availability)",
            "efficiency_class": "Not stated in WEG reference datasheet",
            "motor_rated_power_kw": 1.1,
            "motor_rated_speed_rpm": 1410.0,
            "supply_voltage_v": "400 / 690 V",
            "supply_frequency_hz": "50 Hz (60 Hz not stated in reference)",
            "winding_connection": "Delta / Star (400 V Δ / 690 V Y confirmed)",
            "protection_class": "IP66 (confirmed)",
            "terminal_box_position": "Side 4 cable entry III (from datasheet)",
            "cable_entries": "1× M16×1.5 and 1× M25×1.5 (confirmed)",
            "cooling_method": "Unventilated without shaft fan (confirmed in datasheet)",
            "heater_spec": "~25 W, 24 V DC (confirmed)",
            "total_weight_kg": 45.0,
            "certifications": "CE confirmed; UL/CSA confirmed; UKCA confirmed; EN 2.2 batch certificate provided",
            "temperature_range": "-40°C to +120°C (confirmed — exceeds requirement)",
            "corrosivity_category": "C5H confirmed",
            "rotation": "CW and CCW — not explicitly stated in datasheet; to confirm",
            "starting_method": "Direct-on-line start (DOL jog / rotate crane)",
            "heater_terminal_blocks": "Connected to WEG clamping system (confirmed)",
            "gearbox_structural_capacity_nm": 141.0,
        }

    # ════════════════════════════════════════════════════════
    # MOTOR 4 — Transtecno ITB 423 F200D 28.22 (1.1 kW)
    # ════════════════════════════════════════════════════════
    def _transtecno_itb423(self):
        return {
            "supplier_name": "Transtecno",
            "motor_model": "Transtecno ITB 423 F200D 28.22 — 1.1 kW TENV IP66 UL/CSA",
            "datasheet_source": (
                "AF.00045419 (Transtecno approval drawing, 10/06/2026) "
                "+ Palfinger datasheet D86141 "
                "(ITB 42_3 F200 D 28.22 D40 90B14 SZDX M2)"
            ),
            "notes": (
                "OVERALL RESULT: DOES NOT FIT — two hard engineering FAILs "
                "(ratio and speed) that are structural to this unit's design. "
                "A higher-ratio variant is needed.\n\n"
                "FAIL 1 — Gearbox internal ratio 28.22 is BELOW the minimum "
                "31.59.\n"
                " Minimum ratio = 1390 rpm ÷ 44 rpm = 31.59.\n"
                " Transtecno ratio 28.22 < 31.59 → gearmotor runs too fast "
                "at any motor speed in the 1390–1465 rpm band.\n\n"
                "FAIL 2 — Gearmotor output speed 49.61 rpm EXCEEDS the "
                "44 rpm maximum.\n"
                " At rated motor speed 1400 rpm with ratio 28.22: "
                "output = 1400 ÷ 28.22 = 49.6 rpm.\n"
                " Crane speed = 49.6 ÷ 110 = 0.451 rpm > 0.40 rpm limit."
            ),
            "gear_series": "Helical bevel geared motor ITB 423 (Transtecno)",
            "gearmotor_output_speed_rpm": 49.61,
            "gearmotor_output_torque_nm": 199.05,
            "gearbox_internal_ratio": 28.22,
            "max_permissible_input_speed_rpm": 1400.0,
            "mounting_position": "M2 (per Palfinger datasheet D86141); exact position to confirm",
            "output_flange_description": (
                "IEC F200D (Ø200 mm); Ø165 bolt circle; 4×Ø11 mm holes "
                "(confirmed per approval drawing AF.00045419)"
            ),
            "output_shaft_description": "Ø32 k6 × 50 mm hardened steel special output shaft (confirmed per AF.00045419)",
            "keyway_standard": "DIN 6885-1 — Key A 10×8×40 confirmed in drawing AF.00045419",
            "painting_system": (
                "C5M RAL7035 specified in drawing AF.00045419. "
                "Note: C5M is the marine/offshore category; the requirement "
                "is C5H (industrial coast/offshore). Confirm equivalence "
                "or request C5H specification from Transtecno."
            ),
            "colour_ral": "RAL7035 (confirmed in drawing AF.00045419)",
            "input_flange_description": (
                "B14 IEC round flange Ø160 mm (from Palfinger datasheet "
                "D86141: '90B14'). "
                "Requirement is square IEC 150: Ø165 bolt circle; "
                "4×Ø12 through-holes; R15 corners; Ø32 F8 bore; "
                "10 H9 keyway. Square flange not confirmed — CHECK."
            ),
            "housing_material": "Cast iron (confirmed in drawing notes AF.00045419)",
            "duty_cycle": "S3-25% to confirm; TENV execution is suitable for intermittent duty; thermal confirmation from Transtecno required",
            "efficiency_class": "IE class not stated in AF.00045419 or Palfinger D86141; UL/CSA T1 temperature class confirmed; IE2 or IE3 to confirm with Transtecno",
            "motor_rated_power_kw": 1.1,
            "motor_rated_speed_rpm": 1400.0,
            "supply_voltage_v": "400 / 480 / 690 V (per model nameplate in AF.00045419)",
            "supply_frequency_hz": "50/60 Hz — 50 Hz confirmed via Palfinger D86141; 60 Hz to confirm",
            "winding_connection": "Delta/Star — 400 V Delta / 690 V Star assumed from dual-voltage model; to confirm explicitly with Transtecno",
            "protection_class": "IP66 (confirmed in model designation AF.00045419: 'IP66')",
            "terminal_box_position": "Terminal box position to confirm with Transtecno; downward NDE-side cable entry required per specification",
            "cable_entries": "Double cable glands confirmed in drawing notes AF.00045419; M25×1.5 and M16×1.5 thread sizes to confirm",
            "cooling_method": "TENV / IC410 unventilated — confirmed in model designation (T1C90S4 TENV) and drawing notes AF.00045419",
            "heater_spec": "~25 W, 24 V DC heater included (confirmed in drawing notes AF.00045419: 'cast iron motor with heater 24V DC')",
            "total_weight_kg": None,
            "certifications": (
                "UL/CSA T1 confirmed (model designation AF.00045419). "
                "CE marking mandatory — not explicitly stated in available "
                "documents; to confirm with Transtecno. "
                "EN 10204 Type 3.1 material certificate required — to "
                "confirm. UKCA not stated."
            ),
            "temperature_range": "T1 UL/CSA temperature class confirmed; operating range -20°C to +50°C to confirm with Transtecno",
            "corrosivity_category": "C5M specified in drawing AF.00045419; C5H corrosivity equivalence to confirm (see painting notes above)",
            "rotation": "CW and CCW compatible (M2 mounting; ITB series design) — to confirm with Transtecno",
            "starting_method": "Direct-on-line start (T1C90S4 motor design — suitable for DOL)",
            "heater_terminal_blocks": "24 V DC heater included per drawing; two dedicated terminal blocks inside terminal box to confirm",
            "gearbox_structural_capacity_nm": 796.2,
        }
