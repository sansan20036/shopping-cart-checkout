"""Parser for the line-oriented interview-question input format."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from .domain import (
    PRODUCT_CATALOG,
    CartItem,
    CheckoutRequest,
    Coupon,
    ProductCategory,
    Promotion,
)
from .exceptions import InputFormatError


_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
_ITEM_PATTERN = re.compile(
    rf"^(?P<quantity>[+-]?\d+)\s*\*\s*(?P<name>[^:]+?)\s*:\s*(?P<price>{_NUMBER})$"
)
_DATE_PATTERN = re.compile(r"^\d{4}\.\d{1,2}\.\d{1,2}$")


class CheckoutInputParser:
    """Converts input text to a validated checkout request.

    Lines are identified by their documented syntax. This supports both the
    blank-line-separated format in Case A and the compact format in Case B.
    Text following ``//`` is treated as a comment.
    """

    def parse(self, text: str) -> CheckoutRequest:
        promotions: list[Promotion] = []
        items: list[CartItem] = []
        checkout_date: date | None = None
        coupon: Coupon | None = None

        for line_number, raw_line in enumerate(text.splitlines(), start=1):
            line = raw_line.split("//", maxsplit=1)[0].strip()
            if not line:
                continue

            try:
                if "|" in line:
                    promotions.append(self._parse_promotion(line))
                elif "*" in line or ":" in line:
                    items.append(self._parse_item(line))
                elif _DATE_PATTERN.fullmatch(line):
                    if checkout_date is not None:
                        raise InputFormatError("只能有一個結算日期")
                    checkout_date = self._parse_date(line, "結算日期")
                else:
                    if coupon is not None:
                        raise InputFormatError("每次結算只能使用一張優惠券")
                    coupon = self._parse_coupon(line)
            except InputFormatError as exc:
                raise InputFormatError(f"第 {line_number} 行：{exc}") from exc

        if checkout_date is None:
            raise InputFormatError("缺少結算日期")

        return CheckoutRequest(
            items=tuple(items),
            checkout_date=checkout_date,
            promotions=tuple(promotions),
            coupon=coupon,
        )

    def _parse_promotion(self, line: str) -> Promotion:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 3:
            raise InputFormatError("促銷格式應為 日期|折扣|產品品類")

        date_text, rate_text, category_text = parts
        try:
            category = ProductCategory(category_text)
        except ValueError as exc:
            raise InputFormatError(f"未知的產品品類「{category_text}」") from exc

        return Promotion(
            effective_date=self._parse_date(date_text, "促銷日期"),
            discount_rate=self._parse_decimal(rate_text, "促銷折扣"),
            category=category,
        )

    def _parse_item(self, line: str) -> CartItem:
        match = _ITEM_PATTERN.fullmatch(line)
        if match is None:
            raise InputFormatError("商品格式應為 數量*商品:單價")

        name = match.group("name").strip()
        category = PRODUCT_CATALOG.get(name)
        if category is None:
            raise InputFormatError(f"產品目錄中沒有商品「{name}」")

        return CartItem(
            name=name,
            category=category,
            quantity=int(match.group("quantity")),
            unit_price=self._parse_decimal(match.group("price"), "商品單價"),
        )

    def _parse_coupon(self, line: str) -> Coupon:
        parts = line.split()
        if len(parts) != 3:
            raise InputFormatError("優惠券格式應為 到期日 門檻 折抵金額")

        expires_text, threshold_text, discount_text = parts
        return Coupon(
            expires_on=self._parse_date(expires_text, "優惠券到期日"),
            threshold=self._parse_decimal(threshold_text, "優惠券門檻"),
            discount_amount=self._parse_decimal(discount_text, "優惠券折抵金額"),
        )

    @staticmethod
    def _parse_date(value: str, label: str) -> date:
        try:
            return datetime.strptime(value, "%Y.%m.%d").date()
        except ValueError as exc:
            raise InputFormatError(f"{label}「{value}」不是有效的 YYYY.M.D 日期") from exc

    @staticmethod
    def _parse_decimal(value: str, label: str) -> Decimal:
        try:
            result = Decimal(value)
        except InvalidOperation as exc:
            raise InputFormatError(f"{label}「{value}」不是有效數字") from exc
        if not result.is_finite():
            raise InputFormatError(f"{label}必須是有限數字")
        return result
