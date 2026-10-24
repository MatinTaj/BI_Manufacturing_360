"""Pure five-component monthly finished-goods valuation; no I/O or RNG."""
from material_valuation import nonnegative_decimal, cents, round_ratio, allocate_issue_cents

COMPONENT_COSTS = dict(material='purchase_material_cost_eur',
    inbound_freight='inbound_freight_cost_eur', labor='labor_cost_eur',
    energy='energy_cost_eur', overhead='manufacturing_overhead_eur')
COMPONENTS = tuple(COMPONENT_COSTS)
CAPITALIZED_COLUMNS = tuple(f'capitalized_{c}_cost_eur' for c in COMPONENTS)
LOSS_COLUMNS = tuple(f'{c}_production_loss_expense_eur' for c in COMPONENTS)
PRODUCTION_COLUMNS = ('purchase_material_cost_eur', 'inbound_freight_cost_eur',
                      *CAPITALIZED_COLUMNS, *LOSS_COLUMNS)
COGS_COLUMNS = tuple(f'{c}_cogs_eur' for c in COMPONENTS)
INVENTORY_COLUMNS = tuple(f'{movement}_{c}_value_eur'
    for movement in ('opening', 'production', 'closing') for c in COMPONENTS) + COGS_COLUMNS


def units(value):
    value = nonnegative_decimal(value)
    if value != value.to_integral_value():
        raise ValueError('Finished-goods units must be integers')
    return int(value)


def booked_cents(value):
    amount = cents(value)
    if abs(nonnegative_decimal(value) - nonnegative_decimal(amount)/100) > nonnegative_decimal('0.00000001'):
        raise ValueError('Component values must be booked cents')
    return amount


def component_cents(values):
    if set(values) != set(COMPONENTS):
        raise ValueError('All five manufacturing components required')
    return {c: booked_cents(values[c]) for c in COMPONENTS}


def value_finished_goods_month(opening_units, opening_values, good_units, production_values, shipped_units):
    opening_units, good_units, shipped_units = map(units, (opening_units, good_units, shipped_units))
    opening, production = component_cents(opening_values), component_cents(production_values)
    if (not opening_units and sum(opening.values())) or (not good_units and sum(production.values())):
        raise ValueError('Capitalized value without good inventory units')
    available_units = opening_units + good_units
    if shipped_units > available_units:
        raise ValueError('Shipments exceed available finished goods')
    available = {c: opening[c] + production[c] for c in COMPONENTS}
    cogs = {c: round_ratio(available[c] * shipped_units, available_units) for c in COMPONENTS}
    closing = {c: available[c] - cogs[c] for c in COMPONENTS}
    result = dict(opening_units=opening_units, good_production_units=good_units,
        shipped_units=shipped_units, closing_units=available_units-shipped_units,
        opening_value_eur=sum(opening.values())/100, production_value_eur=sum(production.values())/100,
        cogs_eur=sum(cogs.values())/100, closing_value_eur=sum(closing.values())/100,
        weighted_average_unit_cost_eur=round(sum(available.values())/100/available_units, 8) if available_units else 0.)
    for movement, values in (('opening', opening), ('production', production), ('closing', closing)):
        result.update({f'{movement}_{c}_value_eur': values[c]/100 for c in COMPONENTS})
    result.update({f'{c}_cogs_eur': cogs[c]/100 for c in COMPONENTS})
    return result


def allocate_sales_cogs(ledger, shipped_quantities):
    """Caller orders rows by stable sales_line_id (request order during generation)."""
    quantities = [units(q) for q in shipped_quantities]
    if sum(quantities) != units(ledger['shipped_units']):
        raise ValueError('Sales quantities do not match product/month shipments')
    pools = {c: booked_cents(ledger[f'{c}_cogs_eur']) for c in COMPONENTS}
    if booked_cents(ledger['cogs_eur']) != sum(pools.values()):
        raise ValueError('Aggregate COGS does not equal components')
    shares = {c: allocate_issue_cents(pools[c], quantities) for c in COMPONENTS}
    return [dict(cogs_eur=sum(shares[c][i] for c in COMPONENTS)/100,
                 **{f'{c}_cogs_eur': shares[c][i]/100 for c in COMPONENTS})
            for i in range(len(quantities))]
