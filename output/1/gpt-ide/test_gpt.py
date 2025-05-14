import pytest
import uuid
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# ---------- Product ----------
def test_product_creation_and_details():
    p = Product("Test", 10.5, quantity=3)
    assert p.name == "Test"
    assert p.price == 10.5
    assert p.quantity == 3
    details = p.get_details()
    assert details["name"] == "Test"
    assert details["type"] == "GenericProduct"

def test_product_invalid_name():
    with pytest.raises(TypeError):
        Product("", 10)
    with pytest.raises(TypeError):
        Product(123, 10)

def test_product_invalid_price():
    with pytest.raises(ValueError):
        Product("A", 0)
    with pytest.raises(ValueError):
        Product("A", -1)

def test_product_update_quantity():
    p = Product("A", 10, quantity=2)
    p.update_quantity(3)
    assert p.quantity == 5
    p.update_quantity(-2)
    assert p.quantity == 3
    with pytest.raises(ValueError):
        p.update_quantity(-10)
    with pytest.raises(TypeError):
        p.update_quantity("bad")

def test_product_apply_discount():
    p = Product("A", 100)
    p.apply_discount(10)
    assert p.price == 90
    p.apply_discount(50)
    assert p.price == 45
    with pytest.raises(ValueError):
        p.apply_discount(-1)
    with pytest.raises(ValueError):
        p.apply_discount(101)
    with pytest.raises(TypeError):
        p.apply_discount("bad")

# ---------- DigitalProduct ----------
def test_digital_product_creation_and_details():
    dp = DigitalProduct("Ebook", 20, "https://example.com/file", 5.5)
    assert dp.download_link.startswith("https://")
    assert dp.file_size_mb == 5.5
    details = dp.get_details()
    assert details["type"] == "DigitalProduct"

def test_digital_product_invalid_link_and_size():
    with pytest.raises(TypeError):
        DigitalProduct("Ebook", 20, "ftp://bad", 5)
    with pytest.raises(ValueError):
        DigitalProduct("Ebook", 20, "https://good", 0)

def test_digital_product_generate_new_link():
    dp = DigitalProduct("Ebook", 20, "https://example.com/file", 5.5)
    old_link = dp.download_link
    new_link = dp.generate_new_download_link("https://newbase.com")
    assert new_link != old_link
    assert new_link.startswith("https://newbase.com/")
    with pytest.raises(TypeError):
        dp.generate_new_download_link("")

# ---------- PhysicalProduct ----------
def test_physical_product_creation_and_details():
    pp = PhysicalProduct("Book", 30, 0.5, (20, 15, 2))
    assert pp.weight_kg == 0.5
    assert pp.shipping_dimensions == (20, 15, 2)
    details = pp.get_details()
    assert details["type"] == "PhysicalProduct"

def test_physical_product_invalid_weight_and_dimensions():
    with pytest.raises(ValueError):
        PhysicalProduct("Book", 30, 0, (20, 15, 2))
    with pytest.raises(TypeError):
        PhysicalProduct("Book", 30, 1, (20, 15))
    with pytest.raises(TypeError):
        PhysicalProduct("Book", 30, 1, (20, 15, -1))

def test_physical_product_shipping_cost():
    pp = PhysicalProduct("Book", 30, 2, (20, 15, 10))
    cost = pp.calculate_shipping_cost(10)
    assert isinstance(cost, float)
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(0)
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(10, 0)

# ---------- Inventory ----------
def test_inventory_add_and_get_product():
    inv = Inventory()
    p = Product("A", 10)
    inv.add_product(p)
    assert inv.get_product(p.product_id) is p
    assert inv.get_stock_level(p.product_id) == p.quantity

def test_inventory_add_duplicate():
    inv = Inventory()
    p = Product("A", 10)
    inv.add_product(p)
    with pytest.raises(ValueError):
        inv.add_product(p)

def test_inventory_remove_product():
    inv = Inventory()
    p = Product("A", 10)
    inv.add_product(p)
    removed = inv.remove_product(p.product_id)
    assert removed is p
    with pytest.raises(KeyError):
        inv.remove_product(p.product_id)

def test_inventory_update_stock():
    inv = Inventory()
    p = Product("A", 10, quantity=5)
    inv.add_product(p)
    inv.update_stock(p.product_id, -2)
    assert p.quantity == 3
    with pytest.raises(ValueError):
        inv.update_stock(p.product_id, -10)

def test_inventory_find_products_by_name():
    inv = Inventory()
    p1 = Product("Apple", 10)
    p2 = Product("Banana", 5)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.find_products_by_name("app")
    assert p1 in results
    assert p2 not in results

def test_inventory_price_range():
    inv = Inventory()
    p1 = Product("A", 10)
    p2 = Product("B", 20)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.get_products_in_price_range(15, 25)
    assert p2 in results
    assert p1 not in results

def test_inventory_total_value():
    inv = Inventory()
    p1 = Product("A", 10, quantity=2)
    p2 = Product("B", 5, quantity=3)
    inv.add_product(p1)
    inv.add_product(p2)
    assert inv.get_total_inventory_value() == 2*10 + 3*5

# ---------- Order ----------
def test_order_add_and_remove_item():
    inv = Inventory()
    p = Product("A", 10, quantity=5)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 2, inventory=inv)
    assert order.items[p.product_id]["quantity"] == 2
    assert inv.get_stock_level(p.product_id) == 3
    order.remove_item(p.product_id, 1, inventory=inv)
    assert order.items[p.product_id]["quantity"] == 1
    assert inv.get_stock_level(p.product_id) == 4

def test_order_add_item_not_enough_stock():
    inv = Inventory()
    p = Product("A", 10, quantity=1)
    inv.add_product(p)
    order = Order()
    with pytest.raises(ValueError):
        order.add_item(p, 2, inventory=inv)

def test_order_remove_item_too_many():
    inv = Inventory()
    p = Product("A", 10, quantity=5)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 2, inventory=inv)
    with pytest.raises(ValueError):
        order.remove_item(p.product_id, 3, inventory=inv)

def test_order_status_and_finalize():
    order = Order()
    p = Product("A", 10)
    order.add_item(p, 1)
    order.finalize_order()
    assert order.status == "awaiting_payment"
    order.update_status("processing")
    assert order.status == "processing"
    order.update_status("shipped")
    assert order.status == "shipped"
    with pytest.raises(ValueError):
        order.update_status("pending")
    with pytest.raises(ValueError):
        order.update_status("badstatus")

def test_order_empty_finalize():
    order = Order()
    with pytest.raises(ValueError):
        order.finalize_order()

def test_order_summary_and_total():
    order = Order()
    p = Product("A", 10)
    order.add_item(p, 2)
    summary = order.get_order_summary()
    assert summary["total_items"] == 2
    assert summary["total_cost"] == 20
    assert summary["items"][0]["name"] == "A"