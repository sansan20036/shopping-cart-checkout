import unittest
from decimal import Decimal

from shopping_cart.domain import CheckoutService, ProductCategory
from shopping_cart.exceptions import InputFormatError, ValidationError
from shopping_cart.parser import CheckoutInputParser


CASE_A = """\
2015.11.11|0.7|電子 // 促銷

1*ipad:2399.00
1*顯示器:1799.00
12*啤酒:25.00
5*麵包:9.00

2015.11.11
2016.3.2 1000 200
"""

CASE_B = """\
3*蔬菜:5.98
8*餐巾紙:3.20
2015.01.01
"""


class CheckoutInputParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = CheckoutInputParser()

    def test_case_a(self) -> None:
        request = self.parser.parse(CASE_A)

        self.assertEqual(4, len(request.items))
        self.assertEqual(ProductCategory.ELECTRONICS, request.items[0].category)
        self.assertEqual(
            Decimal("3083.60"), CheckoutService().calculate(request)
        )

    def test_case_b_compact_format(self) -> None:
        request = self.parser.parse(CASE_B)

        self.assertEqual(
            Decimal("43.54"), CheckoutService().calculate(request)
        )

    def test_accepts_spaces_around_item_separators(self) -> None:
        request = self.parser.parse("2 * 麵包 : 10.50\n2025.1.2")

        self.assertEqual(Decimal("21.00"), CheckoutService().calculate(request))

    def test_rejects_unknown_product(self) -> None:
        with self.assertRaisesRegex(InputFormatError, "產品目錄"):
            self.parser.parse("1*汽水:10\n2025.1.1")

    def test_rejects_invalid_calendar_date_with_line_number(self) -> None:
        with self.assertRaisesRegex(InputFormatError, "第 2 行"):
            self.parser.parse("1*麵包:10\n2025.2.30")

    def test_rejects_missing_checkout_date(self) -> None:
        with self.assertRaisesRegex(InputFormatError, "缺少結算日期"):
            self.parser.parse("1*麵包:10")

    def test_rejects_empty_cart(self) -> None:
        with self.assertRaisesRegex(ValidationError, "購物車不可為空"):
            self.parser.parse("2025.1.1")

    def test_rejects_more_than_one_coupon(self) -> None:
        text = "1*麵包:1000\n2025.1.1\n2025.2.1 100 10\n2025.3.1 200 20"

        with self.assertRaisesRegex(InputFormatError, "只能使用一張"):
            self.parser.parse(text)

    def test_rejects_non_positive_quantity(self) -> None:
        with self.assertRaisesRegex(ValidationError, "數量必須大於"):
            self.parser.parse("0*麵包:10\n2025.1.1")


if __name__ == "__main__":
    unittest.main()
