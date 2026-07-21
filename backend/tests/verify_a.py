import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models import (
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskUpdate,
)


def print_pass(check_name: str) -> None:
    print(f"PASS: {check_name}")


def print_fail(check_name: str, reason: str) -> None:
    print(f"FAIL: {check_name} — {reason}")


def expect_validation_error(
    check_name: str,
    action: Callable[[], Any],
    expected_field: str,
) -> None:
    """
    Pass only when Pydantic raises a ValidationError involving
    the field being tested.
    """
    try:
        action()
    except ValidationError as exc:
        error_fields = {
            str(error["loc"][-1])
            for error in exc.errors()
            if error.get("loc")
        }

        if expected_field in error_fields:
            print_pass(check_name)
        else:
            print_fail(
                check_name,
                f"validation failed, but not for '{expected_field}'. "
                f"Errors: {exc.errors()}",
            )
    except Exception as exc:
        print_fail(
            check_name,
            f"unexpected {type(exc).__name__}: {exc}",
        )
    else:
        print_fail(
            check_name,
            "the invalid value was accepted",
        )


def enum_value(value: Any) -> Any:
    """Return an enum's stored value, or the value itself."""
    return getattr(value, "value", value)


def run_verifications() -> None:
    # 1. Whitespace title rejected
    expect_validation_error(
        "whitespace title rejected",
        lambda: TaskCreate(title="   "),
        "title",
    )

    # 2. Empty title rejected
    expect_validation_error(
        "empty title rejected",
        lambda: TaskCreate(title=""),
        "title",
    )

    # 3. Title over 200 characters rejected
    expect_validation_error(
        "title over 200 chars rejected",
        lambda: TaskCreate(title="x" * 201),
        "title",
    )

    # 4. Defaults applied
    try:
        task = TaskCreate(title="Valid task")

        defaults_are_correct = (
            enum_value(task.status) == "ToDo"
            and enum_value(task.priority) == "Medium"
            and task.description == ""
        )

        if defaults_are_correct:
            print_pass(
                "defaults applied "
                "(ToDo, Medium, empty description)"
            )
        else:
            print_fail(
                "defaults applied "
                "(ToDo, Medium, empty description)",
                (
                    f"received status={task.status!r}, "
                    f"priority={task.priority!r}, "
                    f"description={task.description!r}"
                ),
            )
    except Exception as exc:
        print_fail(
            "defaults applied "
            "(ToDo, Medium, empty description)",
            f"{type(exc).__name__}: {exc}",
        )

    # 5. Extra field rejected on TaskCreate
    expect_validation_error(
        "extra field rejected on TaskCreate",
        lambda: TaskCreate.model_validate(
            {
                "title": "Valid task",
                "unexpected_field": "not allowed",
            }
        ),
        "unexpected_field",
    )

    # 6. id rejected on TaskCreate
    expect_validation_error(
        "id rejected on TaskCreate",
        lambda: TaskCreate.model_validate(
            {
                "title": "Valid task",
                "id": "manually-supplied-id",
            }
        ),
        "id",
    )

    # 7. created_at rejected on TaskUpdate
    expect_validation_error(
        "created_at rejected on TaskUpdate",
        lambda: TaskUpdate.model_validate(
            {
                "created_at": datetime.now(timezone.utc),
            }
        ),
        "created_at",
    )

    # 8. Invalid status rejected
    expect_validation_error(
        "invalid status rejected",
        lambda: TaskCreate.model_validate(
            {
                "title": "Valid task",
                "status": "InvalidStatus",
            }
        ),
        "status",
    )

    print("--- Part A verifications complete ---")


if __name__ == "__main__":
    run_verifications()