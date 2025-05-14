import pytest
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct,
    Inventory, Order
)

# ---------- Product & Subclasses ----------

def test_product_creation_valid():
    p = Product("Test", 10.5, quantity=5)
    assert p.name == "Test"
    assert p.price == 10.5
    assert p.quantity == 5
    assert isinstance(p.product_id, str)

@pytest.mark.parametrize("name,price,quantity", [
    ("", 10, 1),
    (None, 10, 1),
    ("Test", -1, 1),
    ("Test", 0, 1),
    ("Test", 10, -1),
])
def test_product_creation_invalid(name, price, quantity):
    with pytest.raises((TypeError, ValueError)):
        Product(name, price, quantity=quantity)

def test_product_update_quantity():
    p = Product("Test", 10, quantity=2)
    p.update_quantity(3)
    assert p.quantity == 5
    p.update_quantity(-2)
    assert p.quantity == 3
    with pytest.raises(ValueError):
        p.update_quantity(-10)
    with pytest.raises(TypeError):
        p.update_quantity("abc")

def test_product_apply_discount():
    p = Product("Test", 100)
    p.apply_discount(10)
    assert p.price == 90.0
    with pytest.raises(ValueError):
        p.apply_discount(200)
    with pytest.raises(TypeError):
        p.apply_discount("abc")

def test_digital_product_creation_and_link():
    dp = DigitalProduct("Ebook", 20, "https://example.com/file", 5.5)
    assert dp.download_link.startswith("https://")
    assert dp.file_size_mb == 5.5
    new_link = dp.generate_new_download_link("https://newbase.com")
    assert new_link.startswith("https://newbase.com/")
    with pytest.raises(TypeError):
        DigitalProduct("Ebook", 20, "ftp://badlink", 5.5)
    with pytest.raises(ValueError):
        DigitalProduct("Ebook", 20, "https://good.com", -1)

def test_physical_product_creation_and_shipping():
    pp = PhysicalProduct("Box", 50, 2.5, (10, 20, 30))
    assert pp.weight_kg == 2.5
    assert pp.shipping_dimensions == (10, 20, 30)
    cost = pp.calculate_shipping_cost(10)
    assert isinstance(cost, float)
    with pytest.raises(ValueError):
        PhysicalProduct("Box", 50, -1, (10, 20, 30))
    with pytest.raises(TypeError):
        PhysicalProduct("Box", 50, 1, (10, 20))
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(-1)

# ---------- Inventory ----------

def test_inventory_add_and_get_product():
    inv = Inventory()
    p = Product("Test", 10)
    inv.add_product(p)
    assert inv.get_product(p.product_id) == p
    with pytest.raises(ValueError):
        inv.add_product(p)  # Duplicate
    with pytest.raises(TypeError):
        inv.add_product("not a product")

def test_inventory_remove_product():
    inv = Inventory()
    p = Product("Test", 10)
    inv.add_product(p)
    removed = inv.remove_product(p.product_id)
    assert removed == p
    with pytest.raises(KeyError):
        inv.remove_product(p.product_id)

def test_inventory_update_stock():
    inv = Inventory()
    p = Product("Test", 10, quantity=5)
    inv.add_product(p)
    inv.update_stock(p.product_id, -2)
    assert p.quantity == 3
    with pytest.raises(ValueError):
        inv.update_stock(p.product_id, -10)

def test_inventory_search_and_value():
    inv = Inventory()
    p1 = Product("Apple", 2, quantity=10)
    p2 = Product("Banana", 1, quantity=5)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.find_products_by_name("apple")
    assert p1 in results
    assert p2 not in results
    value = inv.get_total_inventory_value()
    assert value == 2*10 + 1*5

# ---------- Order ----------

def test_order_add_and_remove_item():
    inv = Inventory()
    p = Product("Test", 10, quantity=5)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 2, inventory=inv)
    assert order.items[p.product_id]["quantity"] == 2
    assert inv.get_product(p.product_id).quantity == 3
    order.remove_item(p.product_id, 1, inventory=inv)
    assert order.items[p.product_id]["quantity"] == 1
    assert inv.get_product(p.product_id).quantity == 4
    with pytest.raises(ValueError):
        order.remove_item(p.product_id, 10, inventory=inv)

def test_order_finalize_and_status():
    order = Order()
    p = Product("Test", 10)
    order.add_item(p, 1)
    order.finalize_order()
    assert order.status == "awaiting_payment"
    with pytest.raises(ValueError):
        empty_order = Order()
        empty_order.finalize_order()
    order.update_status("processing")
    assert order.status == "processing"
    with pytest.raises(ValueError):
        order.update_status("invalid_status")

def test_order_calculate_total_and_summary():
    order = Order()
    p1 = Product("A", 10)
    p2 = Product("B", 5)
    order.add_item(p1, 2)
    order.add_item(p2, 1)
    assert order.calculate_total() == 25
    summary = order.get_order_summary()
    assert summary["total_items"] == 3
    assert summary["total_cost"] == 25