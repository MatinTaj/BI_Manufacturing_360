"""Fictional engineering/commercial assumptions; see docs/financial_model.md.

No values are estimated from realized profit or a target margin.
This module performs no I/O and consumes no random state on import.
"""
import hashlib
import numpy as np

ASSUMPTION_VERSION = "engineering-v1"
MONTHLY_ESCALATION = 0.0015
LABOR_RATE_RANGE_EUR = (32.0, 36.0)  # fully burdened shop-floor labor
ENERGY_TARIFF_RANGE_EUR = (0.16, 0.23)
OVERHEAD_RANGE_EUR = (22000.0, 28000.0)  # per line/month
SELLING_FIXED_EUR = 26000.0  # four commercial staff + office/customer service
ADMIN_FIXED_EUR = 38000.0  # six finance/HR/IT/management staff + services
SELLING_VARIABLE_RATE = 0.02  # commissions/commercial support, excludes freight

# Fictional domestic/regional consolidated truck transport, excluding unloading,
# plant handling, storage, outbound delivery and recoverable taxes.
INBOUND_FREIGHT_BASE_EUR_PER_KG = 0.12
INBOUND_FREIGHT_MONTHLY_ESCALATION = 0.0015
INBOUND_FREIGHT_VERSION = "inbound-v1"


def inbound_freight_rate(material_id, supplier_id, month_id, elapsed):
    """Stable freight variation without consuming the operational RNG stream."""
    validate_freight_assumptions()
    if int(elapsed) != elapsed or elapsed < 0:
        raise ValueError("Freight elapsed months must be nonnegative integers")
    def fraction(key):
        return int.from_bytes(hashlib.sha256(key.encode('utf-8')).digest()[:8], 'big') / (2**64 - 1)
    supplier = 0.90 + 0.20 * fraction(f"{INBOUND_FREIGHT_VERSION}|361|{supplier_id}")
    movement = 0.95 + 0.10 * fraction(f"{INBOUND_FREIGHT_VERSION}|361|{material_id}|{supplier_id}|{month_id}")
    return round(INBOUND_FREIGHT_BASE_EUR_PER_KG * supplier * movement *
                 (1 + INBOUND_FREIGHT_MONTHLY_ESCALATION * elapsed), 4)


def validate_freight_assumptions():
    values = (INBOUND_FREIGHT_BASE_EUR_PER_KG, INBOUND_FREIGHT_MONTHLY_ESCALATION)
    if not np.isfinite(values).all() or values[0] <= 0 or values[1] < 0:
        raise ValueError("Invalid inbound freight assumptions")


# Fictional external delivery of packed subassemblies, EUR per shipped unit.
# OEM/Tier 1 use consolidated industrial deliveries; aftermarket orders are smaller.
OUTBOUND_FREIGHT_RATES_EUR_PER_UNIT = {'OEM': 1.20, 'Tier 1': 1.50, 'Aftermarket': 2.20}
OUTBOUND_FREIGHT_VERSION = "outbound-v1"


def validate_outbound_freight_assumptions():
    if set(OUTBOUND_FREIGHT_RATES_EUR_PER_UNIT) != {'OEM', 'Tier 1', 'Aftermarket'}:
        raise ValueError('Outbound freight requires all three customer segments')
    values = list(OUTBOUND_FREIGHT_RATES_EUR_PER_UNIT.values())
    if not np.isfinite(values).all() or min(values) <= 0:
        raise ValueError('Outbound freight base rates must be finite and positive')


def outbound_freight_rate(segment, customer_id, month_id):
    """Stable +/-5% customer and +/-3% month variation without RNG draws."""
    validate_outbound_freight_assumptions()
    if segment not in OUTBOUND_FREIGHT_RATES_EUR_PER_UNIT:
        raise ValueError(f'Unknown outbound freight segment: {segment}')
    def fraction(key):
        return int.from_bytes(hashlib.sha256(key.encode('utf-8')).digest()[:8], 'big') / (2**64 - 1)
    customer = .95 + .10 * fraction(f'{OUTBOUND_FREIGHT_VERSION}|362|{segment}|{customer_id}')
    month = .97 + .06 * fraction(f'{OUTBOUND_FREIGHT_VERSION}|362|{segment}|{customer_id}|{month_id}')
    return round(OUTBOUND_FREIGHT_RATES_EUR_PER_UNIT[segment] * customer * month, 4)


# price EUR, hours/attempt, kWh/attempt, kg/attempt by stable material ID.
# These are process-input BOMs, before separately generated extra process waste.
FAMILIES = {
    "Brake Assembly": dict(price=65.0, hours=0.55, kwh=8.0,
                          bom={"M001": 4.0, "M004": 3.0, "M005": 0.2, "M006": 0.15}),
    "Steering Bracket": dict(price=44.0, hours=0.40, kwh=5.0,
                            bom={"M001": 2.8, "M007": 0.35, "M005": 0.08}),
    "Engine Mount": dict(price=52.0, hours=0.45, kwh=6.0,
                         bom={"M001": 3.2, "M002": 0.7, "M006": 0.6}),
    "Suspension Link": dict(price=57.0, hours=0.50, kwh=7.0,
                            bom={"M001": 3.8, "M006": 0.25, "M007": 0.2}),
    "Transmission Housing": dict(price=88.0, hours=0.80, kwh=12.0,
                                 bom={"M002": 5.5, "M001": 0.4, "M005": 0.1}),
}
# Size/complexity variants are explicitly paired with engineering activity.
# Commercial multipliers are independent inputs, not cost-plus calculations.
VARIANT_SIZE = (0.85, 0.95, 1.05, 1.15)
VARIANT_PRICE = (0.90, 0.97, 1.04, 1.11)
LINE_FIXED_ACTIVITY = {
    "L01": (120.0, 2400.0),
    "L02": (135.0, 2800.0),
    "L03": (150.0, 3200.0),
}
PRODUCT_DRIVERS = ("standard_labor_hours_per_attempt", "standard_energy_kwh_per_attempt")
LINE_DRIVERS = ("support_labor_hours_per_month", "base_energy_kwh_per_month")


def validate_economic_assumptions():
    """Fail before export for invalid settings; profitability is not a constraint."""
    for name, bounds in (("labor rate", LABOR_RATE_RANGE_EUR),
                         ("energy tariff", ENERGY_TARIFF_RANGE_EUR),
                         ("overhead", OVERHEAD_RANGE_EUR)):
        if len(bounds) != 2 or not np.isfinite(bounds).all() or not 0 < bounds[0] <= bounds[1]:
            raise ValueError(f"Invalid {name} bounds")
    values = (SELLING_FIXED_EUR, ADMIN_FIXED_EUR, MONTHLY_ESCALATION, SELLING_VARIABLE_RATE)
    if not np.isfinite(values).all() or min(values) < 0 or SELLING_VARIABLE_RATE > 1:
        raise ValueError("Invalid operating expense/escalation assumptions")
    for factors in (VARIANT_SIZE, VARIANT_PRICE):
        if len(factors) != 4 or not np.isfinite(factors).all() or min(factors) <= 0:
            raise ValueError("Four finite positive variant factors required")
    if len(FAMILIES) != 5 or set(LINE_FIXED_ACTIVITY) != {"L01", "L02", "L03"}:
        raise ValueError("Stable five-family/three-line catalog required")
    for family in FAMILIES.values():
        values = [family['price'], family['hours'], family['kwh'], *family['bom'].values()]
        if not family['bom'] or not np.isfinite(values).all() or min(values) <= 0:
            raise ValueError("Invalid family engineering/commercial assumptions")
    for values in LINE_FIXED_ACTIVITY.values():
        if len(values) != 2 or not np.isfinite(values).all() or min(values) <= 0:
            raise ValueError("Invalid fixed line activity")


def validate_activity_masters(products, lines):
    """Reject legacy/mixed schemas explicitly; never silently invent drivers."""
    for frame, columns, key in ((products, PRODUCT_DRIVERS, "product_id"),
                                (lines, LINE_DRIVERS, "line_id")):
        missing = set(columns) - set(frame.columns)
        if missing:
            raise ValueError(f"Missing economic drivers {sorted(missing)}; existing CSVs are legacy. "
                             "A coordinated regeneration is required before using new financial logic.")
        values = frame[list(columns)].to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values <= 0).any():
            raise ValueError(f"{key}: drivers must be finite and positive")
        if frame[key].isna().any() or frame[key].duplicated().any():
            raise ValueError(f"{key}: missing/duplicate key")
    if not products.line_id.isin(lines.line_id).all():
        raise ValueError("Product line has no fixed activity drivers")


def line_activity(batch, line):
    """Aggregate product requirements, preserving separately visible fixed activity."""
    production_hours = round(float((batch.attempted_units * batch.standard_labor_hours_per_attempt).sum()), 2)
    activity_kwh = round(float((batch.attempted_units * batch.standard_energy_kwh_per_attempt).sum()), 2)
    support = float(line.support_labor_hours_per_month)
    base = float(line.base_energy_kwh_per_month)
    return dict(production_labor_hours=production_hours, support_labor_hours=support,
                labor_hours=round(production_hours + support, 2),
                activity_energy_kwh=activity_kwh, base_energy_kwh=base,
                energy_kwh=round(activity_kwh + base, 2))
