# validpeas

Small library to create structured validations.

Define validations in a structured way, so the result is also structured and easy to understand what went wrong.

While functional, still has a lot of room for improvement. No breaking changes will be introduced in the 0.x.x versions.


## Example

The example is a simple JSON validation. The JSON should have a field called "numbers" that is a list of integers. The list should have at least 6 elements and be in ascending order.

Just for the sake of the example, the validation is done in a very verbose way, with a lot of intermediate steps, so the result is also verbose and easy to understand.


### Validation definition


```python
from json import loads
from typing import Any
from itertools import pairwise

from validpeas import (
    ValidationResult,
    make_composite_processor,
    make_validator,
    processor_from_validator,
    human_text_result_report,
)


# ##################### Elemental validators ######################
# These validators are the basic building blocks, the ones that
# actually do the validation.


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


# ####################### Composite validators ########################
# These validators are composed of elemental validators, they provide
# structure to the validations in a logical way, and also dispatch
# and process the data for the elemental validators.


@make_composite_processor()
def all_list_items_are_integers(numbers: list[Any]) -> list[ValidationResult]:
    return list(map(is_integer, numbers))


@make_composite_processor()
def is_in_ascending_order(numbers: list[int]) -> list[ValidationResult]:
    return list(map(ascending_pair, pairwise(numbers)))


# Define a custom name for the main validator
@make_composite_processor("JSON with +6 numbers in ascending order")
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


# ####################### Run validations ########################
# Run the main validator with different samples of data and print


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

result_separator = "\n--------------------------------------------------\n\n"

result_reports = (
    (f"INPUT: {sample}\n\n" f"{human_text_result_report(main_validator(sample))}")
    for sample in samples
)

print(result_separator.join(result_reports))
```

### Output

```
INPUT: 5

❌ JSON with +6 numbers in ascending order
    ❌ is_string
    ⚠️ is_valid_json
    ⚠️ has_numbers_field
    ⚠️ is_list
    ⚠️ length_is_greater_than_5
    ⚠️ all_list_items_are_integers
    ⚠️ is_in_ascending_order

--------------------------------------------------

INPUT: gfdgsgfsggfds

❌ JSON with +6 numbers in ascending order
    ✅ is_string
    ❌ is_valid_json
    ⚠️ has_numbers_field
    ⚠️ is_list
    ⚠️ length_is_greater_than_5
    ⚠️ all_list_items_are_integers
    ⚠️ is_in_ascending_order

--------------------------------------------------

INPUT: {"asdf": [1, 2, 3, 5, 4]}

❌ JSON with +6 numbers in ascending order
    ✅ is_string
    ✅ is_valid_json
    ❌ has_numbers_field
    ⚠️ is_list
    ⚠️ length_is_greater_than_5
    ⚠️ all_list_items_are_integers
    ⚠️ is_in_ascending_order

--------------------------------------------------

INPUT: {"numbers": [1, 2, 3]}

❌ JSON with +6 numbers in ascending order
    ✅ is_string
    ✅ is_valid_json
    ✅ has_numbers_field
    ✅ is_list
    ❌ length_is_greater_than_5
    ✅ all_list_items_are_integers
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
    ✅ is_in_ascending_order
        ✅ ascending_pair
        ✅ ascending_pair

--------------------------------------------------

INPUT: {"numbers": [1, 2, 3, 4, 5, "a"]}

❌ JSON with +6 numbers in ascending order
    ✅ is_string
    ✅ is_valid_json
    ✅ has_numbers_field
    ✅ is_list
    ✅ length_is_greater_than_5
    ❌ all_list_items_are_integers
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ❌ is_integer
    ⚠️ is_in_ascending_order

--------------------------------------------------

INPUT: {"numbers": [1, 2, 3, "b"]}

❌ JSON with +6 numbers in ascending order
    ✅ is_string
    ✅ is_valid_json
    ✅ has_numbers_field
    ✅ is_list
    ❌ length_is_greater_than_5
    ❌ all_list_items_are_integers
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ❌ is_integer
    ⚠️ is_in_ascending_order

--------------------------------------------------

INPUT: {"numbers": [1, 2, 3, 4, 6, 5, 7, 8, 9, 10]}

❌ JSON with +6 numbers in ascending order
    ✅ is_string
    ✅ is_valid_json
    ✅ has_numbers_field
    ✅ is_list
    ✅ length_is_greater_than_5
    ✅ all_list_items_are_integers
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
    ❌ is_in_ascending_order
        ✅ ascending_pair
        ✅ ascending_pair
        ✅ ascending_pair
        ✅ ascending_pair
        ❌ ascending_pair
        ✅ ascending_pair
        ✅ ascending_pair
        ✅ ascending_pair
        ✅ ascending_pair

--------------------------------------------------

INPUT: {"numbers": [1, 2, 3, 4, 5, 6]}

✅ JSON with +6 numbers in ascending order
    ✅ is_string
    ✅ is_valid_json
    ✅ has_numbers_field
    ✅ is_list
    ✅ length_is_greater_than_5
    ✅ all_list_items_are_integers
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
        ✅ is_integer
    ✅ is_in_ascending_order
        ✅ ascending_pair
        ✅ ascending_pair
        ✅ ascending_pair
        ✅ ascending_pair
        ✅ ascending_pair
```