import unittest

def run_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests", pattern="test_*.py")
    test_runner = unittest.TextTestRunner()
    return test_runner.run(test_suite)

# only execute if we are the script being directly executed
if __name__ == "__main__":
    test_results = run_tests()

    # Check if any test failed
    if test_results.failures or test_results.errors:
        print("Some tests failed. Check the test output for details.")
    else:
        print("All tests passed successfully.")
