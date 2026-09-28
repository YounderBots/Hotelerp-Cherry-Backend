"""Validation rules for restaurant combo/package deals.

These are pure request-model checks, so they need no MySQL instance. The HTTP
suite exercises the live endpoint; this suite keeps the business constraints
from regressing when the UI is changed.
"""
import pytest
from pydantic import ValidationError

from resources.menuController import ComboIn, ComboItemIn, ComboUpdate


def item(menu_id: int = 1, quantity: int = 1):
    return {"menu_id": menu_id, "quantity": quantity}


def test_combo_item_quantity_must_be_positive():
    with pytest.raises(ValidationError, match="quantity must be at least 1"):
        ComboItemIn(menu_id=1, quantity=0)


def test_combo_price_must_be_positive():
    with pytest.raises(ValidationError, match="combo_price must be greater than zero"):
        ComboIn(
            combo_name="Breakfast",
            combo_price=0,
            items=[item()],
        )


def test_combo_dates_must_be_ordered():
    with pytest.raises(ValidationError, match="valid_to must be on or after valid_from"):
        ComboIn(
            combo_name="Breakfast",
            combo_price=250,
            valid_from="2026-10-10T00:00:00",
            valid_to="2026-10-09T00:00:00",
            items=[item()],
        )


def test_partial_combo_update_keeps_positive_price_rule():
    with pytest.raises(ValidationError, match="combo_price must be greater than zero"):
        ComboUpdate(combo_price=-1)
