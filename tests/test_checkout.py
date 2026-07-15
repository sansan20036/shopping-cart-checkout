import unittest
from datetime import date
from decimal import Decimal

from shopping_cart.domain import (
    CartItem,
    CheckoutRequest,
    CheckoutService,
    Coupon,
    ProductCategory,
    Promotion,
)
from shopping_cart.exceptions import ValidationError


class CheckoutServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = CheckoutService()
        self.checkout_date = date(2015, 11, 11)

    def item(
        self,
        price: str,
        *,
        quantity: int = 1,
        category: ProductCategory = ProductCategory.FOOD,
    ) -> CartItem:
        return CartItem("測試商品", category, quantity, Decimal(price))

    def test_applies_multiple_category_promotions(self) -> None:
        request = CheckoutRequest(
            items=(
                self.item("100", category=ProductCategory.FOOD),
                self.item("200", category=ProductCategory.ELECTRONICS),
                self.item("50", category=ProductCategory.ALCOHOL),
            ),
            checkout_date=self.checkout_date,
            promotions=(
                Promotion(
                    self.checkout_date, Decimal("0.8"), ProductCategory.FOOD
                ),
                Promotion(
                    self.checkout_date,
                    Decimal("0.5"),
                    ProductCategory.ELECTRONICS,
                ),
            ),
        )

        self.assertEqual(Decimal("230.00"), self.service.calculate(request))

    def test_ignores_promotion_from_another_date(self) -> None:
        request = CheckoutRequest(
            items=(self.item("100"),),
            checkout_date=self.checkout_date,
            promotions=(
                Promotion(date(2015, 11, 10), Decimal("0.5"), ProductCategory.FOOD),
            ),
        )

        self.assertEqual(Decimal("100.00"), self.service.calculate(request))

    def test_coupon_threshold_uses_total_after_promotions(self) -> None:
        request = CheckoutRequest(
            items=(self.item("1000"),),
            checkout_date=self.checkout_date,
            promotions=(
                Promotion(self.checkout_date, Decimal("0.5"), ProductCategory.FOOD),
            ),
            coupon=Coupon(self.checkout_date, Decimal("1000"), Decimal("200")),
        )

        self.assertEqual(Decimal("500.00"), self.service.calculate(request))

    def test_coupon_applies_on_threshold_and_expiry_boundaries(self) -> None:
        request = CheckoutRequest(
            items=(self.item("1000"),),
            checkout_date=self.checkout_date,
            coupon=Coupon(self.checkout_date, Decimal("1000"), Decimal("200")),
        )

        self.assertEqual(Decimal("800.00"), self.service.calculate(request))

    def test_expired_coupon_is_ignored(self) -> None:
        request = CheckoutRequest(
            items=(self.item("1000"),),
            checkout_date=self.checkout_date,
            coupon=Coupon(date(2015, 11, 10), Decimal("1000"), Decimal("200")),
        )

        self.assertEqual(Decimal("1000.00"), self.service.calculate(request))

    def test_total_never_becomes_negative(self) -> None:
        request = CheckoutRequest(
            items=(self.item("10"),),
            checkout_date=self.checkout_date,
            coupon=Coupon(self.checkout_date, Decimal("0"), Decimal("20")),
        )

        self.assertEqual(Decimal("0.00"), self.service.calculate(request))

    def test_rounds_half_up_only_at_final_total(self) -> None:
        request = CheckoutRequest(
            items=(self.item("1.005"),), checkout_date=self.checkout_date
        )

        self.assertEqual(Decimal("1.01"), self.service.calculate(request))

    def test_rejects_duplicate_active_promotion_for_category(self) -> None:
        promotion = Promotion(
            self.checkout_date, Decimal("0.8"), ProductCategory.FOOD
        )
        request = CheckoutRequest(
            items=(self.item("100"),),
            checkout_date=self.checkout_date,
            promotions=(promotion, promotion),
        )

        with self.assertRaisesRegex(ValidationError, "重複促銷"):
            self.service.calculate(request)

    def test_rejects_invalid_domain_values(self) -> None:
        with self.assertRaises(ValidationError):
            self.item("10", quantity=0)
        with self.assertRaises(ValidationError):
            self.item("-0.01")
        with self.assertRaises(ValidationError):
            Promotion(self.checkout_date, Decimal("1.1"), ProductCategory.FOOD)


if __name__ == "__main__":
    unittest.main()
