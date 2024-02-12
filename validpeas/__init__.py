from pydantic import BaseModel
from typing import Any, Callable, Protocol
from json import loads, dumps
from itertools import pairwise


ValidatorFunc = Callable[[Any], bool]


class ValidationResult(BaseModel):
    validator_name: str
    passed: bool
    sub_results: list["ValidationResult"] | None = None
    dependencies: list["ValidationResult"] | None = None


class ProcessorFunc(Protocol):
    @staticmethod
    def __call__(
        data: Any, dependencies: list[ValidationResult] = []
    ) -> ValidationResult: ...


CompositeValidatorFunc = Callable[[Any], list[ValidationResult]]


class Validator(BaseModel):
    name: str
    func: ValidatorFunc


def make_validator(
    name: str | None = None,
) -> Callable[[ValidatorFunc], Validator]:
    def decorator(func: ValidatorFunc) -> Validator:
        name_ = func.__name__ if name is None else name
        return Validator(name=name_, func=func)

    return decorator


def all_passed(results: list[ValidationResult]) -> bool:
    return all(result.passed for result in results)


def processor_from_validator(validator: Validator) -> ProcessorFunc:
    def processor(data, dependencies: list[ValidationResult] = []) -> ValidationResult:
        return ValidationResult(
            validator_name=validator.name,
            passed=all_passed(dependencies) and validator.func(data),
            dependencies=dependencies,
        )

    return processor


########## Simplified Results ##########


def simplify_result(result: ValidationResult) -> dict:
    """Make a simpler and more readable structure from a ValidationResult model.

    The simplified structure is roughly the same but with the following changes:
    - The 'validator_name' key is replaced by 'validation'.
    - The 'sub_results' key is replaced by 'failed_sub_validations'.
    - In the 'failed_sub_validations' are listed only the failed sub validations.
    - The 'failed_sub_validations' key is removed if there's none.
    - The 'dependencies' key is renamed to 'failed_dependencies'.
    - The 'failed_dependencies' key is removed if there's none.
    - The 'failed_dependencies' contain only the immediate failed dependencies,
      no dependency nesting.
    - The 'failed_dependencies' now is a list of strings.
    """
    simplified = {
        "validation": result.validator_name,
        "passed": result.passed,
    }
    if result.sub_results:
        failed_sub_validations = [
            simplify_result(sub_result)
            for sub_result in result.sub_results
            if not sub_result.passed
        ]
        if len(failed_sub_validations) > 0:
            simplified["failed_sub_validations"] = failed_sub_validations
    if result.dependencies:
        failed_dependencies = [
            dependency.validator_name
            for dependency in result.dependencies
            if not dependency.passed
        ]
        if len(failed_dependencies) > 0:
            simplified["failed_dependencies"] = failed_dependencies
    return simplified


class FriendlierResult(BaseModel):
    validation: str
    passed: bool
    sub_validations: list["FriendlierResult"] | None = None
    dependencies: list[str] | None = None

    @classmethod
    def from_result(cls, result: ValidationResult) -> "FriendlierResult":
        return cls(
            validation=result.validator_name,
            passed=result.passed,
            sub_validations=(
                [cls.from_result(sub_result) for sub_result in result.sub_results]
                if result.sub_results
                else None
            ),
            dependencies=(
                [dependency.validator_name for dependency in result.dependencies]
                if result.dependencies
                else None
            ),
        )

    def model_dump(self, *args, **kwargs) -> dict:
        return super().model_dump(*args, **kwargs, exclude_none=True)


def remove_sub_validators_with_failed_dependencies(
    result: ValidationResult,
) -> ValidationResult:
    """Remove the sub_results with failed dependencies from a ValidationResult model."""
    if result.sub_results:
        sub_results = [
            remove_sub_validators_with_failed_dependencies(sub_result)
            for sub_result in result.sub_results
            if sub_result.passed or not sub_result.dependencies
        ]
    return ValidationResult(
        validator_name=result.validator_name,
        passed=result.passed,
        sub_results=sub_results,
        dependencies=result.dependencies,
    )


def human_text_result_report(
    result: ValidationResult, indentation_level=0, indentation="    "
) -> str:
    """Make a human readable text report from a ValidationResult model.

    The report is a string with the following structure:

    [icon] validation_name
        [icon] sub_validation_1
        [icon] sub_validation_2
            [icon] sub_sub_validation_1

    Icons:
        ✅ Is for passed
        ❌ Is for failed
        ⚠️ Is for has failed dependencies

    """
    indentation_ = indentation * indentation_level
    dependencies = result.dependencies or []
    sub_results = result.sub_results or []
    icon = "✅" if result.passed else "❌" if all_passed(dependencies) else "⚠️"
    intem_head = f"{indentation_}{icon} {result.validator_name}\n"

    def sub_report(sub_result: ValidationResult) -> str:
        return human_text_result_report(sub_result, indentation_level + 1, indentation)

    sub_reports = "".join(map(sub_report, sub_results))
    return intem_head + sub_reports
