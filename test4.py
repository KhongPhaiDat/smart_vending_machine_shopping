from decimal import Decimal

origin = {
    "bento": {
        "quantity": "Decimal('10')",
        "price": "Decimal('10000')",
        "cost": "Decimal('100000')",
    },
    "cupcake": {
        "quantity": "Decimal('10')",
        "price": "Decimal('10000')",
        "cost": "Decimal('100000')",
    },
    "dat": {
        "quantity": "Decimal('0')",
        "price": "Decimal('0')",
        "cost": "Decimal('100000')",
    },
}

data = "Decimal('10')"


def convert():
    convert_dt = int(data.split("'")[1])
    print(type(convert_dt))


def convert_decimal_to_int(value):
    if isinstance(value, dict):
        return {k: convert_decimal_to_int(v) for k, v in value.items()}
    if (
        isinstance(value, str)
        and value.startswith("Decimal('")
        and value.endswith("')")
    ):
        return int(Decimal(value.split("'")[1]))
    return value


def orgin_item_list_to_dict(origin_item_list):
    items = dict()
    for item_name, value in origin_item_list.items():
        items[item_name] = {
            "amount": int(Decimal(value["quantity"].split("'")[1])),
            "price": int(Decimal(value["price"].split("'")[1])),
        }

    print(items)


convert()
