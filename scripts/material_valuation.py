"""Pure monthly landed-material valuation. No file I/O or RNG state."""
from decimal import Decimal, ROUND_HALF_UP

COMPONENTS = ('purchase_material', 'inbound_freight')
RECEIPT_COLUMNS = ('purchase_unit_cost_eur', 'purchase_value_eur',
                   'inbound_freight_rate_eur_per_kg', 'inbound_freight_eur',
                   'landed_receipt_value_eur')
ISSUE_COLUMNS = ('issued_purchase_material_value_eur', 'issued_inbound_freight_eur',
                 'weighted_average_purchase_unit_cost_eur',
                 'weighted_average_inbound_freight_unit_cost_eur')
INVENTORY_COLUMNS = tuple(f'{movement}_{component}_value_eur'
                          for movement in ('opening', 'receipt', 'issued', 'closing')
                          for component in COMPONENTS) + ('landed_receipt_value_eur',
                          'weighted_average_purchase_unit_cost_eur',
                          'weighted_average_inbound_freight_unit_cost_eur')


def nonnegative_decimal(value):
    value = Decimal(str(value))
    if not value.is_finite() or value < 0:
        raise ValueError('Quantity, rate or value must be finite and nonnegative')
    return value


def cents(value):
    return int((nonnegative_decimal(value) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def mills(value):
    scaled = nonnegative_decimal(value) * 1000
    if scaled != scaled.to_integral_value():
        raise ValueError('Material kg must have at most three decimal places')
    return int(scaled)


def round_ratio(numerator, denominator):
    """Nonnegative integer ratio rounded half up without binary float error."""
    if denominator <= 0:
        if numerator == 0:
            return 0
        raise ValueError('Value without available material quantity')
    quotient, remainder = divmod(numerator, denominator)
    return quotient + int(2 * remainder >= denominator)


def allocate_issue_cents(total, quantities):
    """Largest remainder; caller supplies stable production_id order."""
    denominator = sum(quantities)
    if not denominator:
        if total:
            raise ValueError('Issue value without consumption')
        return [0] * len(quantities)
    shares = [total * q // denominator for q in quantities]
    order = sorted(range(len(quantities)), key=lambda i: (-(total * quantities[i] % denominator), i))
    for i in order[:total - sum(shares)]:
        shares[i] += 1
    return shares


def value_receipt(quantity_kg, purchase_unit_cost, freight_rate):
    quantity = mills(quantity_kg)
    purchase_unit_cost = nonnegative_decimal(purchase_unit_cost)
    freight_rate = nonnegative_decimal(freight_rate)
    kg = Decimal(quantity) / 1000
    purchase, freight = cents(kg * purchase_unit_cost), cents(kg * freight_rate)
    landed = purchase + freight
    return dict(purchase_unit_cost_eur=float(purchase_unit_cost), purchase_value_eur=purchase / 100,
                inbound_freight_rate_eur_per_kg=float(freight_rate), inbound_freight_eur=freight / 100,
                receipt_value_eur=purchase / 100, landed_receipt_value_eur=landed / 100,
                landed_unit_cost_eur=round(landed / 100 / (quantity / 1000), 8) if quantity else 0.)


def value_material_month(opening_kg, opening_purchase_eur, opening_freight_eur,
                         received_kg, receipt_purchase_eur, receipt_freight_eur,
                         consumed_quantities):
    """Return ledger and per-issue values; aggregate value is sum of components."""
    opening, received = mills(opening_kg), mills(received_kg)
    quantities = [mills(q) for q in consumed_quantities]
    available, used = opening + received, sum(quantities)
    if used > available:
        raise ValueError('Consumption exceeds available material')
    opening_values = [cents(opening_purchase_eur), cents(opening_freight_eur)]
    receipts = [cents(receipt_purchase_eur), cents(receipt_freight_eur)]
    if (not opening and sum(opening_values)) or (not received and sum(receipts)):
        raise ValueError('Material value without corresponding quantity')
    values = [o + r for o, r in zip(opening_values, receipts)]
    issued = [round_ratio(value * used, available) for value in values]
    closing = [value - issue for value, issue in zip(values, issued)]
    shares = [allocate_issue_cents(value, quantities) for value in issued]
    averages = [round(value / 100 / (available / 1000), 8) if available else 0. for value in values]
    landed_average = round(sum(values) / 100 / (available / 1000), 8) if available else 0.
    ledger = dict(opening_kg=opening/1000, received_kg=received/1000, consumed_kg=used/1000,
                  closing_kg=(available-used)/1000, opening_value_eur=sum(opening_values)/100,
                  receipt_value_eur=receipts[0]/100, issued_material_value_eur=sum(issued)/100,
                  closing_value_eur=sum(closing)/100, weighted_average_unit_cost_eur=landed_average)
    for movement, amounts in zip(('opening', 'receipt', 'issued', 'closing'),
                                  (opening_values, receipts, issued, closing)):
        ledger.update({f'{movement}_{component}_value_eur': amount/100
                       for component, amount in zip(COMPONENTS, amounts)})
    ledger.update(landed_receipt_value_eur=sum(receipts)/100,
                  weighted_average_purchase_unit_cost_eur=averages[0],
                  weighted_average_inbound_freight_unit_cost_eur=averages[1])
    issues = [dict(issued_material_value_eur=(shares[0][i]+shares[1][i])/100,
                   weighted_average_unit_cost_eur=landed_average,
                   issued_purchase_material_value_eur=shares[0][i]/100,
                   issued_inbound_freight_eur=shares[1][i]/100,
                   weighted_average_purchase_unit_cost_eur=averages[0],
                   weighted_average_inbound_freight_unit_cost_eur=averages[1])
              for i in range(len(quantities))]
    return ledger, issues
