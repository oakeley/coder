#!/usr/bin/env python3
"""
Test Runner Script

This script runs all unit tests for the Code Assistant project
and provides a summary of test results.
"""

import unittest
import sys


def run_all_tests():
    """
    Discover and run all unit tests in the project.

    Returns:
        Boolean indicating whether all tests passed
    """
    # Create a test loader
    loader = unittest.TestLoader()

    # Discover all tests matching the pattern "test_*.py"
    suite = loader.discover(".", pattern="test_*.py")

    # Create a test runner with verbosity level 2
    runner = unittest.TextTestRunner(verbosity=2)

    # Run the tests
    result = runner.run(suite)

    # Return True if all tests passed
    return result.wasSuccessful()


def main():
    """
    Main entry point for the test runner.
    """
    print("=" * 70)
    print("Code Assistant - Unit Test Runner")
    print("=" * 70)
    print()

    # Run all tests
    success = run_all_tests()

    # Print summary
    print()
    print("=" * 70)
    if success:
        print("All tests passed successfully!")
    else:
        print("Some tests failed. Please review the output above.")
    print("=" * 70)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
