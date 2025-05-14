import pytest
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# ---------- Product ----------
def test_product_init_valid():
    p = Product("Book", 10.5, quantity=5)
    assert p.name == "Book"
    assert p.price == 10.5
    assert p.quantity == 5
    assert isinstance(p.product_id, str)

def test_product_init_invalid():
    with pytest.raises(TypeError):
        Product("", 10)
    with pytest.raises(ValueError):
        Product("Book", -1)
    with pytest.raises(TypeError):
        Product("Book", 10, product_id=123)
    with pytest.raises(ValueError):
        Product("Book", 10, quantity=-2)

def test_product_update_quantity():
    p = Product("Pen", 2, quantity=3)
    p.update_quantity(2)
    assert p.quantity == 5
    p.update_quantity(-3)
    assert p.quantity == 2
    with pytest.raises(TypeError):
        p.update_quantity(1.5)
    with pytest.raises(ValueError):
        p.update_quantity(-10)

def test_product_apply_discount():
    p = Product("Notebook", 100)
    p.apply_discount(10)
    assert p.price == 90.0
    with pytest.raises(TypeError):
        p.apply_discount("20")
    with pytest.raises(ValueError):
        p.apply_discount(-5)
    with pytest.raises(ValueError):
        p.apply_discount(150)

def test_product_get_details():
    p = Product("Chair", 50, quantity=2)
    details = p.get_details()
    assert details["name"] == "Chair"
    assert details["type"] == "GenericProduct"

# ---------- DigitalProduct ----------
def test_digital_product_init_valid():
    dp = DigitalProduct("Ebook", 15, "https://example.com/ebook", 5.5)
    assert dp.download_link.startswith("https://")
    assert dp.file_size_mb == 5.5

def test_digital_product_init_invalid():
    with pytest.raises(TypeError):
        DigitalProduct("Ebook", 15, "ftp://badlink", 5)
    with pytest.raises(ValueError):
        DigitalProduct("Ebook", 15, "https://good.com", 0)

def test_digital_product_generate_new_download_link():
    dp = DigitalProduct("Ebook", 15, "https://example.com/ebook", 5.5)
    old_link = dp.download_link
    new_link = dp.generate_new_download_link("https://newbase.com")
    assert new_link != old_link
    assert new_link.startswith("https://newbase.com/")
    with pytest.raises(TypeError):
        dp.generate_new_download_link(123)

def test_digital_product_get_details():
    dp = DigitalProduct("Ebook", 15, "https://example.com/ebook", 5.5)
    details = dp.get_details()
    assert details["type"] == "DigitalProduct"
    assert details["file_size_mb"] == 5.5

# ---------- PhysicalProduct ----------
def test_physical_product_init_valid():
    pp = PhysicalProduct("Box", 20, 2.5, (10, 20, 30))
    assert pp.weight_kg == 2.5
    assert pp.shipping_dimensions == (10, 20, 30)

def test_physical_product_init_invalid():
    with pytest.raises(ValueError):
        PhysicalProduct("Box", 20, 0, (10, 20, 30))
    with pytest.raises(TypeError):
        PhysicalProduct("Box", 20, 2, (10, 20))
    with pytest.raises(TypeError):
        PhysicalProduct("Box", 20, 2, (10, -5, 30))

def test_physical_product_calculate_shipping_cost():
    pp = PhysicalProduct("Box", 20, 2, (10, 20, 30))
    cost = pp.calculate_shipping_cost(10)
    assert isinstance(cost, float)
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(-1)
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(10, volumetric_factor=0)

def test_physical_product_get_details():
    pp = PhysicalProduct("Box", 20, 2, (10, 20, 30))
    details = pp.get_details()
    assert details["type"] == "PhysicalProduct"
    assert details["weight_kg"] == 2

# ---------- Inventory ----------
def test_inventory_add_and_get_product():
    inv = Inventory()
    p = Product("Book", 10)
    inv.add_product(p)
    assert inv.get_product(p.product_id) is p
    with pytest.raises(ValueError):
        inv.add_product(p)
    with pytest.raises(TypeError):
        inv.add_product("not a product")

def test_inventory_remove_product():
    inv = Inventory()
    p = Product("Book", 10)
    inv.add_product(p)
    removed = inv.remove_product(p.product_id)
    assert removed is p
    with pytest.raises(KeyError):
        inv.remove_product(p.product_id)

def test_inventory_update_stock():
    inv = Inventory()
    p = Product("Book", 10, quantity=5)
    inv.add_product(p)
    inv.update_stock(p.product_id, -2)
    assert p.quantity == 3
    with pytest.raises(ValueError):
        inv.update_stock(p.product_id, -10)
    with pytest.raises(KeyError):
        inv.update_stock("badid", 1)

def test_inventory_total_value():
    inv = Inventory()
    p1 = Product("A", 10, quantity=2)
    p2 = Product("B", 5, quantity=3)
    inv.add_product(p1)
    inv.add_product(p2)
    assert inv.get_total_inventory_value() == 2*10 + 3*5

def test_inventory_find_products_by_name():
    inv = Inventory()
    p1 = Product("Red Book", 10)
    p2 = Product("Blue Book", 12)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.find_products_by_name("book")
    assert len(results) == 2
    results_cs = inv.find_products_by_name("Book", case_sensitive=True)
    assert len(results_cs) == 2
    with pytest.raises(TypeError):
        inv.find_products_by_name(123)

def test_inventory_get_products_in_price_range():
    inv = Inventory()
    p1 = Product("A", 10)
    p2 = Product("B", 20)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.get_products_in_price_range(5, 15)
    assert p1 in results and p2 not in results
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(-1, 10)
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(10, 5)

def test_inventory_get_stock_level():
    inv = Inventory()
    p = Product("Book", 10, quantity=7)
    inv.add_product(p)
    assert inv.get_stock_level(p.product_id) == 7

# ---------- Order ----------
def test_order_add_and_remove_item():
    inv = Inventory()
    p = Product("Book", 10, quantity=5)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 2, inventory=inv)
    assert order.items[p.product_id]["quantity"] == 2
    assert p.quantity == 3
    order.remove_item(p.product_id, 1, inventory=inv)
    assert order.items[p.product_id]["quantity"] == 1
    assert p.quantity == 4
    order.remove_item(p.product_id, 1, inventory=inv)
    assert p.product_id not in order.items
    assert p.quantity == 5
    with pytest.raises(KeyError):
        order.remove_item(p.product_id, 1, inventory=inv)

def test_order_add_item_invalid():
    order = Order()
    with pytest.raises(TypeError):
        order.add_item("not a product", 1)
    p = Product("Book", 10)
    with pytest.raises(ValueError):
        order.add_item(p, 0)

def test_order_add_item_not_enough_stock():
    inv = Inventory()
    p = Product("Book", 10, quantity=1)
    inv.add_product(p)
    order = Order()
    with pytest.raises(ValueError):
        order.add_item(p, 2, inventory=inv)

def test_order_status_and_finalize():
    order = Order()
    p = Product("Book", 10)
    order.add_item(p, 1)
    order.finalize_order()
    assert order.status == "awaiting_payment"
    with pytest.raises(ValueError):
        empty_order = Order()
        empty_order.finalize_order()
    order.update_status("processing")
    assert order.status == "processing"
    with pytest.raises(ValueError):
        order.update_status("not_a_status")
    order.update_status("shipped")
    assert order.status == "shipped"
    with pytest.raises(ValueError):
        order.update_status("pending")

def test_order_get_order_summary():
    order = Order(customer_id="cust1")
    p = Product("Book", 10)
    order.add_item(p, 2)
    summary = order.get_order_summary()
    assert summary["customer_id"] == "cust1"
    assert summary["total_items"] == 2
    assert summary["total_cost"] == 20
    assert summary["items"][0]["name"] == "Book" 