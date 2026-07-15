"""Core domain objects and checkout rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Iterable

from .exceptions import ValidationError


ZERO = Decimal("0")
ONE = Decimal("1")
CENT = Decimal("0.01")


class ProductCategory(str, Enum):
    ELECTRONICS = "電子"
    FOOD = "食品"
    DAILY_NECESSITIES = "日用品"
    ALCOHOL = "酒類"


PRODUCT_CATALOG: dict[str, ProductCategory] = {
    "ipad": ProductCategory.ELECTRONICS,
    "iphone": ProductCategory.ELECTRONICS,
    "顯示器": ProductCategory.ELECTRONICS,
    "筆記型電腦": ProductCategory.ELECTRONICS,
    "鍵盤": ProductCategory.ELECTRONICS,
    "麵包": ProductCategory.FOOD,
    "餅乾": ProductCategory.FOOD,
    "蛋糕": ProductCategory.FOOD,
    "牛肉": ProductCategory.FOOD,
    "魚": ProductCategory.FOOD,
    "蔬菜": ProductCategory.FOOD,
    "餐巾紙": ProductCategory.DAILY_NECESSITIES,
    "收納箱": ProductCategory.DAILY_NECESSITIES,
    "咖啡杯": ProductCategory.DAILY_NECESSITIES,
    "雨傘": ProductCategory.DAILY_NECESSITIES,
    "啤酒": ProductCategory.ALCOHOL,
    "白酒": ProductCategory.ALCOHOL,
    "伏特加": ProductCategory.ALCOHOL,
}


@dataclass(frozen=True)
class CartItem:
    name: str
    category: ProductCategory
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValidationError(f"商品「{self.name}」的數量必須大於 0")
        if not self.unit_price.is_finite() or self.unit_price < ZERO:
            raise ValidationError(f"商品「{self.name}」的單價必須是非負有限數字")

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class Promotion:
    effective_date: date
    discount_rate: Decimal
    category: ProductCategory

    def __post_init__(self) -> None:
        if (
            not self.discount_rate.is_finite()
            or self.discount_rate < ZERO
            or self.discount_rate > ONE
        ):
            raise ValidationError("促銷折扣必須介於 0 與 1 之間")


@dataclass(frozen=True)
class Coupon:
    expires_on: date
    threshold: Decimal
    discount_amount: Decimal

    def __post_init__(self) -> None:
        if not self.threshold.is_finite() or self.threshold < ZERO:
            raise ValidationError("優惠券門檻必須是非負有限數字")
        if not self.discount_amount.is_finite() or self.discount_amount < ZERO:
            raise ValidationError("優惠券折抵金額必須是非負有限數字")

    def can_apply(self, checkout_date: date, amount: Decimal) -> bool:
        """Expiry and threshold are inclusive (「滿」means greater than or equal)."""
        return checkout_date <= self.expires_on and amount >= self.threshold


@dataclass(frozen=True)
class CheckoutRequest:
    items: tuple[CartItem, ...]
    checkout_date: date
    promotions: tuple[Promotion, ...] = ()
    coupon: Coupon | None = None

    def __post_init__(self) -> None:
        if not self.items:
            raise ValidationError("購物車不可為空")


class CheckoutService:
    """Calculates payable totals without performing input/output."""

    def calculate(self, request: CheckoutRequest) -> Decimal:
        rates = self._active_discount_rates(
            request.promotions, request.checkout_date
        )
        amount = sum(
            (
                item.subtotal * rates.get(item.category, ONE)
                for item in request.items
            ),
            start=ZERO,
        )

        if request.coupon and request.coupon.can_apply(request.checkout_date, amount):
            amount = max(ZERO, amount - request.coupon.discount_amount)

        return amount.quantize(CENT, rounding=ROUND_HALF_UP)

    @staticmethod
    def _active_discount_rates(
        promotions: Iterable[Promotion], checkout_date: date
    ) -> dict[ProductCategory, Decimal]:
        rates: dict[ProductCategory, Decimal] = {}
        for promotion in promotions:
            if promotion.effective_date != checkout_date:
                continue
            if promotion.category in rates:
                raise ValidationError(
                    f"結算日的「{promotion.category.value}」品類有重複促銷"
                )
            rates[promotion.category] = promotion.discount_rate
        return rates
