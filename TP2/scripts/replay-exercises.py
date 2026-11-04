"""Replay A3 mutations and A4 TDD in a disposable copy, never in the delivered API."""

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT / "docs" / "exercises.json"


def replace_function(source, name, replacement):
    node = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == name)
    lines = source.splitlines(keepends=True)
    return "".join(lines[: node.lineno - 1]) + replacement + "\n\n" + "".join(lines[node.end_lineno :])


def run_tests(sandbox, labels):
    completed = subprocess.run(
        [sys.executable, "manage.py", "test", *labels, "--noinput"],
        cwd=sandbox,
        env={**os.environ, "PYTHONUTF8": "1"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    lines = (completed.stdout + completed.stderr).splitlines()
    return {
        "passed": completed.returncode == 0,
        "summary": [line for line in lines if line.startswith(("Ran ", "FAILED", "OK", "AssertionError:"))],
    }


def main():
    artifacts = PROJECT.parent / ".artifacts"
    artifacts.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tp2-exercises-", dir=artifacts) as temporary:
        sandbox = Path(temporary)
        for folder in ["orders", "config"]:
            shutil.copytree(PROJECT / folder, sandbox / folder, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(PROJECT / "manage.py", sandbox / "manage.py")
        utils_path = sandbox / "orders" / "utils.py"
        validators_path = sandbox / "orders" / "validators.py"
        original_utils = utils_path.read_text(encoding="utf-8")
        original_validators = validators_path.read_text(encoding="utf-8")

        mutations = []
        for name, target, original, changed, labels in [
            (
                "average: division replaced by multiplication",
                utils_path,
                original_utils,
                original_utils.replace("sum(numbers) / len(numbers)", "sum(numbers) * len(numbers)"),
                ["orders.test_utils.UtilityTests"],
            ),
            (
                "email: mandatory @ removed from the pattern",
                validators_path,
                original_validators,
                original_validators.replace(r"[^\s@]+@[^\s@]+", r"[^\s@]+[^\s@]+"),
                ["orders.test_validators.ValidatorTests"],
            ),
            (
                "capitalize: lower() removed",
                utils_path,
                original_utils,
                original_utils.replace("text[1:].lower()", "text[1:]"),
                ["orders.test_utils.UtilityTests"],
            ),
        ]:
            target.write_text(changed, encoding="utf-8")
            red = run_tests(sandbox, labels)
            target.write_text(original, encoding="utf-8")
            green = run_tests(sandbox, labels)
            if red["passed"] or not green["passed"]:
                raise RuntimeError(f"Unexpected mutation result: {name}")
            mutations.append({"mutation": name, "red": red, "restored": green})

        stub = 'def sort_students(students, sort_by, order="asc"):\n    raise NotImplementedError()'
        versions = [
            'return sorted(students, key=lambda student: student["grade"])',
            'return sorted(students, key=lambda student: student["grade"], reverse=order == "desc")',
            'return sorted(students, key=lambda student: student[sort_by], reverse=order == "desc")',
        ]
        tests = [
            "sort_grade_ascending",
            "sort_grade_descending",
            "sort_name_ascending",
            "sort_age_ascending",
            "sort_null",
            "sort_empty",
            "sort_without_mutating",
            "sort_ascending_by_default",
        ]
        implementation = stub
        labels = []
        tdd = []
        for index, name in enumerate(tests):
            labels.append(f"orders.test_utils.SortStudentsTests.test_should_{name}")
            utils_path.write_text(replace_function(original_utils, "sort_students", implementation), encoding="utf-8")
            before = run_tests(sandbox, labels)
            if not before["passed"]:
                if index < 3:
                    body = versions[index]
                elif name == "sort_null":
                    body = "if students is None:\n        return []\n    " + versions[2]
                else:
                    raise RuntimeError(f"Unexpected TDD failure: {name}")
                implementation = 'def sort_students(students, sort_by, order="asc"):\n    ' + body
                utils_path.write_text(
                    replace_function(original_utils, "sort_students", implementation), encoding="utf-8"
                )
            after = run_tests(sandbox, labels)
            if not after["passed"]:
                raise RuntimeError(f"TDD step remains red: {name}")
            tdd.append({"newTest": name, "before": before, "after": after})

        utils_path.write_text(original_utils, encoding="utf-8")
        final = run_tests(sandbox, ["orders.test_utils.SortStudentsTests"])
        if not final["passed"]:
            raise RuntimeError("The final refactored implementation failed")
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(
            json.dumps(
                {
                    "recordedAt": datetime.now(timezone.utc).isoformat(),
                    "scope": "Explicit replay in a disposable copy; not a claim about original commit chronology",
                    "a3": mutations,
                    "a4": tdd,
                    "finalRefactor": final,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"A3: 3 detected mutations; A4: 8 steps green. Report: {OUTPUT}")


if __name__ == "__main__":
    main()
