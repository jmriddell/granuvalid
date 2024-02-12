# validpeas
Small library to create structured validations


## Example

```python
# Elemental validators


@processor_from_validator
@make_validator()
def is_string(data: Any) -> bool:
    return isinstance(data, str)


@processor_from_validator
@make_validator()
def is_valid_json(json_string: str) -> bool:
    try:
        loads(json_string)
        return True
    except ValueError:
        return False


@processor_from_validator
@make_validator()
def has_numbers_field(data: dict) -> bool:
    return "numbers" in data


@processor_from_validator
@make_validator()
def is_list(data: Any) -> bool:
    return isinstance(data, list)


@processor_from_validator
@make_validator()
def is_integer(data: Any) -> bool:
    return isinstance(data, int)


@processor_from_validator
@make_validator()
def length_is_greater_than_5(data: list) -> bool:
    return len(data) > 5


@processor_from_validator
@make_validator()
def ascending_pair(numbers: tuple[int, int]) -> bool:
    return numbers[0] < numbers[1]


# Composite validators


@make_composite_processor()
def all_list_items_are_integers(numbers: list[Any]) -> list[ValidationResult]:
    return list(map(is_integer, numbers))


@make_composite_processor()
def is_in_ascending_order(numbers: list[int]) -> list[ValidationResult]:
    return list(map(ascending_pair, pairwise(numbers)))


@make_composite_processor()
def main_validator(data: Any) -> list[ValidationResult]:
    is_string_result = is_string(data)

    is_valid_json_result = is_valid_json(data, dependencies=[is_string_result])

    json_data = loads(data) if is_valid_json_result.passed else None

    has_numbers_field_result = has_numbers_field(
        json_data, dependencies=[is_valid_json_result]
    )

    numbers = json_data["numbers"] if has_numbers_field_result.passed else None

    is_list_result = is_list(numbers, dependencies=[has_numbers_field_result])

    length_is_greater_than_5_result = length_is_greater_than_5(
        numbers, dependencies=[is_list_result]
    )
    all_list_items_are_integers_result = all_list_items_are_integers(
        numbers, dependencies=[is_list_result]
    )

    is_in_ascending_order_result = is_in_ascending_order(
        numbers, dependencies=[all_list_items_are_integers_result]
    )

    return [
        is_string_result,
        is_valid_json_result,
        has_numbers_field_result,
        is_list_result,
        length_is_greater_than_5_result,
        all_list_items_are_integers_result,
        is_in_ascending_order_result,
    ]


samples = [
    5,
    "gfdgsgfsggfds",
    '{"asdf": [1, 2, 3, 5, 4]}',
    '{"numbers": [1, 2, 3]}',
    '{"numbers": [1, 2, 3, 4, 5, "a"]}',
    '{"numbers": [1, 2, 3, "b"]}',
    '{"numbers": [1, 2, 3, 4, 6, 5, 7, 8, 9, 10]}',
    '{"numbers": [1, 2, 3, 4, 5, 6]}',
]

for sample in samples:
    result = main_validator(sample)
    print(human_text_result_report(result))
    print()
```