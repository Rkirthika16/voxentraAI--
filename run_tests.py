import sys
import traceback
import inspect
import unittest

def run_all_tests():
    modules = [
        "tests.test_ai_pipeline",
        "tests.test_database",
        "tests.test_api_complaints",
        "tests.test_webhooks",
        "tests.test_exotel_telephony",
    ]

    total = 0
    passed = 0
    failed = 0
    errors = []

    print("=" * 70)
    print("VOXENTRA AI - TEST SUITE EXECUTION")
    print("=" * 70)

    for mod_name in modules:
        try:
            mod = __import__(mod_name, fromlist=["*"])
        except Exception as e:
            print(f"[ERROR] Failed to import {mod_name}: {e}")
            traceback.print_exc()
            continue

        functions = [f for name, f in inspect.getmembers(mod, inspect.isfunction) if name.startswith("test_")]
        test_classes = [c for name, c in inspect.getmembers(mod, inspect.isclass) if issubclass(c, unittest.TestCase) and c is not unittest.TestCase]

        # Run module fixture if any
        if hasattr(mod, "setup_db"):
            try:
                mod.setup_db()
            except Exception:
                pass
        if hasattr(mod, "setup_database"):
            try:
                mod.setup_database()
            except Exception:
                pass

        print(f"\n--- Testing Module: {mod_name} ---")
        for fn in functions:
            total += 1
            try:
                fn()
                passed += 1
                print(f"  [PASS] {fn.__name__}")
            except Exception as ex:
                failed += 1
                errors.append((mod_name, fn.__name__, str(ex), traceback.format_exc()))
                print(f"  [FAIL] {fn.__name__}: {ex}")

        for tc_cls in test_classes:
            suite = unittest.TestLoader().loadTestsFromTestCase(tc_cls)
            for test in suite:
                total += 1
                res = unittest.TestResult()
                test.run(res)
                if res.wasSuccessful():
                    passed += 1
                    print(f"  [PASS] {tc_cls.__name__}.{test._testMethodName}")
                else:
                    failed += 1
                    err_msg = res.errors[0][1] if res.errors else (res.failures[0][1] if res.failures else "Unknown failure")
                    errors.append((mod_name, f"{tc_cls.__name__}.{test._testMethodName}", "Failed", err_msg))
                    print(f"  [FAIL] {tc_cls.__name__}.{test._testMethodName}")

    print("\n" + "=" * 70)
    print(f"SUMMARY: Total Tests: {total} | Passed: {passed} | Failed: {failed}")
    print("=" * 70)

    if errors:
        print("\nFAILURE DETAILS:")
        for mod, fn, err, tb in errors:
            print(f"\n{mod}.{fn}: {err}\n{tb}")
        sys.exit(1)
    else:
        print("\nALL TEST CASES PASSED SUCCESSFULLY!")
        sys.exit(0)

if __name__ == "__main__":
    run_all_tests()
