"""
calculator/engine.py
Pure calculation engine — no Django dependencies.
All drivetrain sizing formulas for PF offshore crane slewing drives.

CHAIN:  MOTOR ──► [HELICAL BEVEL GEARBOX] ──► [WORM SLEW RING] ──► CRANE OUTPUT
         n_motor      i_gb / eta_gb              i_slew / eta_slew

Formula reference
F1   T_gm_start_MAX = T_crane_lim  / (i_slew x eta_slew)
F2   T_gm_nom_req   = T_crane_nom  / (i_slew x eta_slew)
F3   CF             = i_slew x eta_slew
F4   n_crane        = n_gm_out / i_slew
F5   M_Nenn         = T_gm_out_nom x CF
F6   Ma_Max         = T_gm_out_start x CF   (CRITICAL structural check)
F7   Mk_Max         = M_Nenn x Mk_Mn
F8   Mn_motor       = (P_kW x 9550) / n_motor
F9   i_gb           = n_motor / n_gm_out
F10  Ma_Mn_MAX      = T_gm_start_MAX / T_gm_out_nom
"""

from dataclasses import dataclass, field
from typing import Optional

CRANE_STANDARD_PF = 'standard_pf'
CRANE_PF_XXL      = 'pf_xxl'

CRANE_PARAMS = {
    CRANE_STANDARD_PF: {
        'i_slew':      121,
        'eta_slew':    0.40,
        'T_crane_lim': 41190,
        'T_crane_nom': 15360,
        'n_crane_min': 0.2,
        'n_crane_max': 1.0,
        'label':       'Standard PF',
    },
    CRANE_PF_XXL: {
        'i_slew':      150,
        'eta_slew':    0.40,
        'T_crane_lim': 62000,
        'T_crane_nom': 23400,
        'n_crane_min': 0.2,
        'n_crane_max': 1.0,
        'label':       'PF-XXL',
    },
}

ETA_GB_ASSUMED  = 0.90
SAFETY_FACTOR   = 1.34
TORQUE_CONSTANT = 9550

KNOWN_MOTORS = {
    'watt_075': {
        'label':            'Watt Drive EP2557M — 0.75 kW',
        'supplier':         'Watt Drive (WEG Group)',
        'crane_type':       CRANE_STANDARD_PF,
        'motor_power_kw':   0.75,
        'motor_speed_rpm':  1410,
        'duty_cycle':       'S2-12min',
        'i_gb':             27.82,
        'gm_out_speed_rpm': 51,
        'gm_out_nom_nm':    141,
        'gm_out_start_nm':  295,
        'gm_out_pullup_nm': 295,  # stated in datasheet
        'Mk_Mn':            3.40,
    },
    'watt_110': {
        'label':            'Watt Drive EP2557M — 1.1 kW',
        'supplier':         'Watt Drive (WEG Group)',
        'crane_type':       CRANE_STANDARD_PF,
        'motor_power_kw':   1.1,
        'motor_speed_rpm':  1365,
        'duty_cycle':       'S2-12min',
        'i_gb':             27.82,
        'gm_out_speed_rpm': 51,
        'gm_out_nom_nm':    141,
        'gm_out_start_nm':  295,
        'gm_out_pullup_nm': 295,  # stated in datasheet
        'Mk_Mn':            3.40,
    },
    'zsystems_v1': {
        'label':            'Z:systems ZK33CV DM90-4 TS P2 — V1',
        'supplier':         'Z:systems',
        'crane_type':       CRANE_STANDARD_PF,
        'motor_power_kw':   1.5,
        'motor_speed_rpm':  1415,
        'duty_cycle':       'S3-15%',
        'i_gb':             30.91,
        'gm_out_speed_rpm': 46,
        'gm_out_nom_nm':    315,
        'gm_out_start_nm':  915,
        'gm_out_pullup_nm': None,  # not stated — will estimate as 75% of starting torque
        'Mk_Mn':            3.40,
    },
    'zsystems_v2': {
        'label':            'Z:systems ZK43CV DM90-4 TS P2 — V2',
        'supplier':         'Z:systems',
        'crane_type':       CRANE_PF_XXL,
        'motor_power_kw':   1.5,
        'motor_speed_rpm':  1415,
        'duty_cycle':       'S3-15%',
        'i_gb':             38.17,
        'gm_out_speed_rpm': 37,
        'gm_out_nom_nm':    390,
        'gm_out_start_nm':  1130,
        'gm_out_pullup_nm': None,  # not stated — will estimate as 75% of starting torque
        'Mk_Mn':            3.40,
    },
}

PHYSICAL_REQUIREMENTS = {
    'motor_type':             {'label': 'Motor type',                     'required': 'Squirrel cage asynchronous helical bevel gearmotor — marine execution',    'note': 'Must be helical bevel, NOT worm. Marine execution required.'},
    'frame_material':         {'label': 'Frame / housing material',        'required': 'Cast Iron (GJL / GG)',                                                     'note': 'Aluminium not acceptable for offshore C5H.'},
    'input_flange':           {'label': 'Input flange',                    'required': 'Round IEC — Ø165 mm bolt circle (IEC 90 B5)',                              'note': 'Direct mounting. Bolt circle diameter 165 mm.'},
    'output_flange':          {'label': 'Output flange',                   'required': 'Square IEC — Ø200 mm',                                                    'note': 'Gearbox output side. Adapter to Ø165 mm slewing drive input.'},
    'output_shaft':           {'label': 'Output shaft',                    'required': 'Ø32 k6 x 50 mm from flange surface — DIN 6885.1 keyway',                  'note': 'Tolerance k6. Length from flange surface.'},
    'cooling_method':         {'label': 'Cooling method',                  'required': 'IC410 TENV — totally enclosed non-ventilated, no shaft fan',               'note': 'IC411 fan-cooled NOT acceptable.'},
    'ip_rating':              {'label': 'IP protection class',             'required': 'IP66 minimum',                                                            'note': 'IP67/68 also acceptable. IP65 NOT sufficient.'},
    'insulation_class':       {'label': 'Insulation class',                'required': 'Class H (180 deg C)',                                                     'note': 'Required for -20 to +45 deg C ambient.'},
    'efficiency_class':       {'label': 'Motor efficiency class',          'required': 'IE2 or higher (IE3, IE4)',                                                'note': 'IE1 NOT acceptable.'},
    'duty_cycle':             {'label': 'Duty cycle',                      'required': 'S3-25% minimum',                                                          'note': 'S3-15% requires thermal confirmation at +45 deg C.'},
    'ambient_temp':           {'label': 'Ambient temperature range',       'required': '-20 deg C to +45 deg C (both limits must be met)',                        'note': 'Offshore wind platform operating range per PF-XXL requirements.'},
    'voltages':               {'label': 'Supply voltages / frequencies',   'required': '400V/50Hz, 400V/60Hz, 480V/60Hz, 690V/50Hz, 690V/60Hz (all 5)',          'note': 'Voltage tolerance +/-10%, frequency tolerance +/-1%.'},
    'standstill_heater':      {'label': 'Standstill heater',               'required': '24 VDC, approx 25 W — anti-condensation — must be included',              'note': 'Required for long offshore standby periods.'},
    'coating_standard':       {'label': 'Coating standard — main body',    'required': 'C5H per ISO 12944 / EN 12944-5',                                          'note': 'For offshore wind platform service.'},
    'surface_prep':           {'label': 'Surface preparation',             'required': 'ISO 8501-3 Level P3',                                                     'note': 'Required before primer.'},
    'coating_layers':         {'label': 'Coating layer system',            'required': 'Primer 2K + Intermediate 2K + Joint sealant + Topcoat 2K',                'note': 'Minimum 4-layer system.'},
    'coating_thickness':      {'label': 'Minimum total NDFT',              'required': '>= 320 um',                                                               'note': 'Verified per motor. Temp range: -40 to +120 deg C.'},
    'output_flange_coating':  {'label': 'Output flange coating (exception)','required': '1x primer only — no topcoat on mating flange surface',                   'note': 'Contact surface must stay primer-only.'},
    'paint_color':            {'label': 'Paint colour',                    'required': 'RAL 7035 Light Grey',                                                     'note': 'Gloss finish per Palfinger standard.'},
    'fasteners':              {'label': 'All fasteners',                   'required': 'Stainless steel A4',                                                      'note': 'Motor and gearbox fasteners both.'},
    'shaft_seal':             {'label': 'Shaft seal material',             'required': 'FPM (Viton) — preferred',                                                 'note': 'For -20 to +120 deg C and offshore chemical resistance.'},
    'nameplate':              {'label': 'Nameplate',                       'required': 'Stainless steel — mounted with stainless rivets or screws',                'note': 'Must include all voltage specs and certification marks.'},
}


@dataclass
class DrivetrainResult:
    crane_type:             str   = ''
    crane_label:            str   = ''
    motor_power_kw:         float = 0.0
    motor_speed_rpm:        float = 0.0
    i_gb:                   float = 0.0
    gm_out_speed_rpm:       float = 0.0
    gm_out_nom_nm:          float = 0.0
    gm_out_start_nm:        float = 0.0
    Mk_Mn:                  float = 3.40
    eta_gb:                 float = ETA_GB_ASSUMED
    i_slew:                 float = 0.0
    eta_slew:               float = 0.0
    CF:                     float = 0.0
    T_crane_lim:            float = 0.0
    T_crane_nom:            float = 0.0
    n_crane_min:            float = 0.0
    n_crane_max:            float = 0.0
    T_gm_start_MAX:         float = 0.0
    T_gm_nom_required:      float = 0.0
    Ma_Mn_MAX:              float = 0.0
    n_gm_min:               float = 0.0
    n_gm_max:               float = 0.0
    Mn_motor:               float = 0.0
    Ma_motor:               float = 0.0
    n_crane:                float = 0.0
    M_Nenn:                 float = 0.0
    Ma_Max:                 float = 0.0
    Mk_Max:                 float = 0.0
    nom_utilisation_pct:    float = 0.0
    start_utilisation_pct:  float = 0.0
    Ma_Mn_actual:           float = 0.0
    M_gear_req:             Optional[float] = None
    gearbox_catalogue_min:  Optional[float] = None

    # Torque-speed curve points at gearbox output shaft
    gm_out_locked_rotor_nm: float = 0.0    # torque at 0 RPM (locked rotor = starting torque)
    gm_out_pullup_nm:       float = 0.0    # minimum torque during acceleration (~40% speed)
    gm_out_breakdown_nm:    float = 0.0    # peak torque before stall (Mk) (~80% speed)
    gm_out_nominal_nm:      float = 0.0    # torque at rated speed (= gm_out_nom_nm)

    # Crane-level equivalents of torque-speed curve points
    Ma_locked_rotor:        float = 0.0    # = existing Ma_Max
    Ma_pullup:              float = 0.0    # pullup torque at crane output
    Ma_breakdown:           float = 0.0    # = existing Mk_Max

    checks: dict = field(default_factory=dict)
    overall_pass: bool = True
    overall_status: str = 'PASS'


def drivetrain_sizing(
    crane_type,
    motor_power_kw,
    motor_speed_rpm,
    gm_out_speed_rpm,
    gm_out_nom_nm,
    gm_out_start_nm,
    Mk_Mn=3.40,
    i_gb=None,
    eta_gb=ETA_GB_ASSUMED,
    gm_out_pullup_nm: float = None,
):
    p = CRANE_PARAMS[crane_type]
    r = DrivetrainResult()

    r.crane_type        = crane_type
    r.crane_label       = p['label']
    r.motor_power_kw    = motor_power_kw
    r.motor_speed_rpm   = motor_speed_rpm
    r.gm_out_speed_rpm  = gm_out_speed_rpm
    r.gm_out_nom_nm     = gm_out_nom_nm
    r.gm_out_start_nm   = gm_out_start_nm
    r.Mk_Mn             = Mk_Mn
    r.eta_gb            = eta_gb

    r.i_gb = i_gb if i_gb else (motor_speed_rpm / gm_out_speed_rpm if gm_out_speed_rpm else 0)

    r.i_slew      = p['i_slew']
    r.eta_slew    = p['eta_slew']
    r.CF          = p['i_slew'] * p['eta_slew']
    r.T_crane_lim = p['T_crane_lim']
    r.T_crane_nom = p['T_crane_nom']
    r.n_crane_min = p['n_crane_min']
    r.n_crane_max = p['n_crane_max']

    r.T_gm_start_MAX    = r.T_crane_lim / r.CF if r.CF else 0
    r.T_gm_nom_required = r.T_crane_nom / r.CF if r.CF else 0
    r.Ma_Mn_MAX         = r.T_gm_start_MAX / gm_out_nom_nm if gm_out_nom_nm else 0
    r.n_gm_min          = r.n_crane_min * r.i_slew
    r.n_gm_max          = r.n_crane_max * r.i_slew

    r.Mn_motor     = (motor_power_kw * TORQUE_CONSTANT) / motor_speed_rpm if motor_speed_rpm else 0
    r.Ma_Mn_actual = gm_out_start_nm / gm_out_nom_nm if gm_out_nom_nm else 0
    r.Ma_motor     = r.Mn_motor * r.Ma_Mn_actual

    r.n_crane = gm_out_speed_rpm / r.i_slew if r.i_slew else 0
    r.M_Nenn  = gm_out_nom_nm   * r.CF
    r.Ma_Max  = gm_out_start_nm * r.CF
    r.Mk_Max  = r.M_Nenn        * Mk_Mn

    r.nom_utilisation_pct   = (r.M_Nenn / r.T_crane_lim * 100) if r.T_crane_lim else 0
    r.start_utilisation_pct = (r.Ma_Max / r.T_crane_lim * 100) if r.T_crane_lim else 0

    # Torque-speed curve points at gearbox output shaft
    # These use the Ma/Mn and Mk/Mn factors from the supplier datasheet
    r.gm_out_locked_rotor_nm = gm_out_start_nm                    # = Anlaufdrehmoment (at 0 RPM)
    r.gm_out_pullup_nm       = gm_out_pullup_nm if gm_out_pullup_nm is not None else gm_out_start_nm * 0.75  # estimated or explicit
    r.gm_out_breakdown_nm    = gm_out_nom_nm * Mk_Mn              # = Mk (peak before stall)
    r.gm_out_nominal_nm      = gm_out_nom_nm                      # at rated speed (already stored)

    # Crane-level equivalents of torque-speed curve points
    r.Ma_locked_rotor = r.gm_out_locked_rotor_nm * r.CF          # = existing Ma_Max
    r.Ma_pullup       = r.gm_out_pullup_nm       * r.CF
    r.Ma_breakdown    = r.gm_out_breakdown_nm    * r.CF          # = existing Mk_Max

    M2_nom = r.T_gm_nom_required
    r.M_gear_req          = M2_nom * SAFETY_FACTOR
    r.gearbox_catalogue_min = r.M_gear_req

    r.checks        = _run_checks(r)
    fails           = [k for k, v in r.checks.items() if v['status'] == 'FAIL']
    reviews         = [k for k, v in r.checks.items() if v['status'] == 'REVIEW']
    r.overall_pass  = len(fails) == 0
    r.overall_status = 'FAIL' if fails else ('REVIEW' if reviews else 'PASS')

    return r


def _run_checks(r):
    checks = {}

    n = r.n_crane
    checks['speed'] = {
        'label':   'Crane output speed',
        'status':  'PASS' if r.n_crane_min <= n <= r.n_crane_max else 'FAIL',
        'message': f'{n:.3f} RPM — {"within" if r.n_crane_min <= n <= r.n_crane_max else "outside"} {r.n_crane_min}–{r.n_crane_max} RPM range',
        'margin':  None,
    }

    utilisation_pct = r.nom_utilisation_pct
    if utilisation_pct > 100:
        nom_status = 'FAIL'
        nom_msg = f'{r.M_Nenn:,.0f} Nm EXCEEDS ring nominal limit {r.T_crane_nom:,.0f} Nm'
    elif utilisation_pct > 90:
        nom_status = 'REVIEW'
        nom_msg = f'{r.M_Nenn:,.0f} Nm — {utilisation_pct:.1f}% of ring capacity (tight margin)'
    else:
        nom_status = 'PASS'
        nom_msg = f'{r.M_Nenn:,.0f} Nm — {utilisation_pct:.1f}% of ring capacity'
    checks['nom_torque_utilisation'] = {
        'label':   'Nominal torque utilisation',
        'status':  nom_status,
        'message': nom_msg,
        'margin':  r.T_crane_nom - r.M_Nenn,
    }

    nom_margin_pct = (1 - r.M_Nenn / r.T_crane_lim) * 100
    checks['nom_torque_limit'] = {
        'label':   'Nominal torque — below structural limit',
        'status':  'PASS' if nom_margin_pct > 10 else ('REVIEW' if nom_margin_pct >= 0 else 'FAIL'),
        'message': f'{r.M_Nenn:,.0f} Nm vs limit {r.T_crane_lim:,.0f} Nm ({nom_margin_pct:.1f}% margin)',
        'margin':  r.T_crane_lim - r.M_Nenn,
    }

    start_margin     = r.T_crane_lim - r.Ma_Max
    start_margin_pct = start_margin / r.T_crane_lim * 100
    if start_margin >= 0:
        st_status = 'PASS'
        st_msg    = f'{r.Ma_Max:,.0f} Nm vs limit {r.T_crane_lim:,.0f} Nm (margin: {start_margin:,.0f} Nm / {start_margin_pct:.1f}%)'
        st_action = ''
    else:
        st_status = 'FAIL'
        over_by   = abs(start_margin)
        over_pct  = over_by / r.T_crane_lim * 100
        st_msg    = f'{r.Ma_Max:,.0f} Nm EXCEEDS limit {r.T_crane_lim:,.0f} Nm by {over_by:,.0f} Nm ({over_pct:.1f}%)'
        st_action = (f'Action required: specify Ma/Mn <= {r.Ma_Mn_MAX:.2f} to supplier, '
                     f'or mandate VFD soft-start capping output starting torque at <= {r.T_gm_start_MAX:,.0f} Nm.')
    checks['start_torque'] = {
        'label':   'Starting torque — structural safety (CRITICAL)',
        'status':  st_status,
        'message': st_msg,
        'action':  st_action,
        'margin':  start_margin,
    }

    checks['ma_mn_ratio'] = {
        'label':   'Ma/Mn starting factor',
        'status':  'PASS' if r.Ma_Mn_actual <= r.Ma_Mn_MAX else 'FAIL',
        'message': (f'Actual {r.Ma_Mn_actual:.2f} <= limit {r.Ma_Mn_MAX:.2f}'
                    if r.Ma_Mn_actual <= r.Ma_Mn_MAX
                    else f'Actual {r.Ma_Mn_actual:.2f} EXCEEDS limit {r.Ma_Mn_MAX:.2f}'),
        'margin':  r.Ma_Mn_MAX - r.Ma_Mn_actual,
    }

    n_out = r.gm_out_speed_rpm
    checks['gm_speed'] = {
        'label':   'GM output speed within window',
        'status':  'PASS' if r.n_gm_min <= n_out <= r.n_gm_max else 'REVIEW',
        'message': f'{n_out} RPM — window is {r.n_gm_min:.0f}–{r.n_gm_max:.0f} RPM',
        'margin':  None,
    }

    gm_start = r.gm_out_start_nm
    gm_limit = r.T_gm_start_MAX
    gm_margin = gm_limit - gm_start
    checks['gm_start_torque'] = {
        'label':   'GM output starting torque vs limit (supplier interface check)',
        'status':  'PASS' if gm_start <= gm_limit else 'FAIL',
        'message': (
            f'Supplier states {gm_start:,.0f} Nm — limit at GM output shaft is '
            f'{gm_limit:,.0f} Nm (= {r.T_crane_lim:,.0f} / {r.CF}) — '
            f'{"margin " + f"{gm_margin:,.0f} Nm" if gm_margin >= 0 else f"OVER by {abs(gm_margin):,.0f} Nm"}'
        ),
        'action': (
            '' if gm_start <= gm_limit else
            f'Require soft-start OR specify Ma/Mn <= {r.Ma_Mn_MAX:.2f} to supplier'
        ),
        'margin': gm_margin,
    }

    return checks


def check_physical_compliance(spec_data):
    results = {}

    def _check(key, label, test_fn, required_str, note=''):
        val = spec_data.get(key)
        if val is None or val == '':
            results[key] = {'label': label, 'status': 'PENDING',
                            'message': 'Not provided — supplier input required',
                            'required': required_str, 'note': note}
        else:
            try:
                passed = test_fn(val)
            except Exception:
                passed = False
            results[key] = {
                'label': label,
                'status': 'PASS' if passed else 'FAIL',
                'message': f'Stated: "{val}"' + ('' if passed else f' — required: {required_str}'),
                'required': required_str, 'note': note, 'value': val,
            }

    _check('motor_type',           'Motor type',                     lambda v: 'helical bevel' in str(v).lower(),                    'Squirrel cage async helical bevel gearmotor marine execution')
    _check('frame_material',       'Frame material',                 lambda v: any(x in str(v).lower() for x in ('cast','gjl','gg')), 'Cast Iron (GJL / GG)')
    _check('input_flange_mm',      'Input flange diameter (mm)',     lambda v: float(v) in (160, 165),                               'Ø160 mm or Ø165 mm (IEC 90 B5)')
    _check('output_flange_type',   'Output flange type',             lambda v: 'square' in str(v).lower() or '200' in str(v),        'Square IEC Ø200 mm')
    _check('output_shaft_mm',      'Output shaft diameter (mm)',     lambda v: float(v) == 32,                                       'Ø32 mm (k6 tolerance)')
    _check('cooling_method',       'Cooling method',                 lambda v: 'ic410' in str(v).lower() or 'tenv' in str(v).lower(),'IC410 TENV — unventilated, no shaft fan')
    _check('ip_rating',            'IP protection class',            lambda v: str(v).upper() in ('IP66','IP67','IP68'),             'IP66 minimum')
    _check('insulation_class',     'Insulation class',               lambda v: str(v).upper() in ('H','CLASS H'),                    'Class H')
    _check('efficiency_class',     'Efficiency class',               lambda v: str(v).upper() in ('IE2','IE3','IE4'),                'IE2 or higher')
    _check('duty_cycle',           'Duty cycle',                     lambda v: any(x in str(v).upper() for x in ('S3-25','S3-40','S3-60','S1')), 'S3-25% minimum')
    _check('ambient_temp_min_c',   'Ambient temp minimum (deg C)',   lambda v: float(v) <= -20,                                      '<= -20 deg C')
    _check('ambient_temp_max_c',   'Ambient temp maximum (deg C)',   lambda v: float(v) >= 45,                                       '>= +45 deg C')
    _check('voltage_400_50',       '400V / 50Hz',                   lambda v: str(v).upper() in ('YES','CONFIRMED','TRUE','1'),      'Confirmed')
    _check('voltage_400_60',       '400V / 60Hz',                   lambda v: str(v).upper() in ('YES','CONFIRMED','TRUE','1'),      'Confirmed')
    _check('voltage_480_60',       '480V / 60Hz',                   lambda v: str(v).upper() in ('YES','CONFIRMED','TRUE','1'),      'Confirmed')
    _check('voltage_690_50',       '690V / 50Hz',                   lambda v: str(v).upper() in ('YES','CONFIRMED','TRUE','1'),      'Confirmed')
    _check('voltage_690_60',       '690V / 60Hz',                   lambda v: str(v).upper() in ('YES','CONFIRMED','TRUE','1'),      'Confirmed')
    _check('heater_voltage_vdc',   'Standstill heater (VDC)',        lambda v: float(v) == 24,                                       '24 VDC')
    _check('coating_standard',     'Coating standard',               lambda v: 'c5h' in str(v).lower(),                             'C5H per ISO 12944 / EN 12944-5')
    _check('surface_prep',         'Surface preparation',            lambda v: 'p3' in str(v).lower(),                              'ISO 8501-3 Level P3')
    _check('coating_ndft_um',      'Coating NDFT (um)',              lambda v: float(v) >= 320,                                      '>= 320 um')
    _check('paint_color',          'Paint colour',                   lambda v: '7035' in str(v),                                    'RAL 7035 Light Grey')
    _check('output_flange_coating','Output flange coating',          lambda v: 'primer' in str(v).lower(),                          '1x primer only — no topcoat on mating surface')
    _check('fasteners',            'Fasteners',                      lambda v: 'a4' in str(v).lower() or 'stainless' in str(v).lower(), 'Stainless steel A4')
    _check('shaft_seal',           'Shaft seal material',            lambda v: 'fpm' in str(v).lower() or 'viton' in str(v).lower(),'FPM / Viton')

    return results


def size_known_motor(motor_key):
    m = KNOWN_MOTORS[motor_key]
    return drivetrain_sizing(
        crane_type        = m['crane_type'],
        motor_power_kw    = m['motor_power_kw'],
        motor_speed_rpm   = m['motor_speed_rpm'],
        gm_out_speed_rpm  = m['gm_out_speed_rpm'],
        gm_out_nom_nm     = m['gm_out_nom_nm'],
        gm_out_start_nm   = m['gm_out_start_nm'],
        Mk_Mn             = m.get('Mk_Mn', 3.40),
        i_gb              = m['i_gb'],
        gm_out_pullup_nm  = m.get('gm_out_pullup_nm'),
    )