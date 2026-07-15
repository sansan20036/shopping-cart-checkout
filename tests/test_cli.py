import io
import unittest

from shopping_cart.cli import main


class CommandLineInterfaceTest(unittest.TestCase):
    def test_prints_total_for_valid_standard_input(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = main(
            [],
            stdin=io.StringIO("1*麵包:10\n2025.1.1\n"),
            stdout=stdout,
            stderr=stderr,
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("10.00\n", stdout.getvalue())
        self.assertEqual("", stderr.getvalue())

    def test_reports_friendly_error_and_nonzero_exit_code(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = main(
            [], stdin=io.StringIO("invalid"), stdout=stdout, stderr=stderr
        )

        self.assertEqual(2, exit_code)
        self.assertEqual("", stdout.getvalue())
        self.assertIn("錯誤：", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
