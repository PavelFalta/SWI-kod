import pytest
import uuid

from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# ---------- Product ----------
def test_product_init_and_get_details():
    p = Product("Book", 199.0, quantity=10)
    details = p.get_details()
    assert details["name"] == "Book"
    assert details["price"] == 199.0
    assert details["quantity"] == 10
    assert isinstance(details["product_id"], str)

def test_product_invalid_init():
    with pytest.raises(TypeError):
        Product(123, 100)
    with pytest.raises(TypeError):
        Product("Book", "not-a-float")
    with pytest.raises(ValueError):
        Product("Book", -10)

def test_product_update_quantity():
    p = Product("Pen", 10, quantity=5)
    p.update_quantity(3)
    assert p.get_details()["quantity"] == 8
    p.update_quantity(-2)
    assert p.get_details()["quantity"] == 6

def test_product_update_quantity_invalid():
    p = Product("Pen", 10, quantity=5)
    with pytest.raises(TypeError):
        p.update_quantity("abc")
    with pytest.raises(ValueError):
        p.update_quantity(-10)  # negative stock

def test_product_apply_discount():
    p = Product("Pen", 100)
    p.apply_discount(10)
    assert p.get_details()["price"] == 90
    p.apply_discount(50)
    assert p.get_details()["price"] == 45

def test_product_apply_discount_invalid():
    p = Product("Pen", 100)
    with pytest.raises(TypeError):
        p.apply_discount("abc")
    with pytest.raises(ValueError):
        p.apply_discount(-5)
    with pytest.raises(ValueError):
        p.apply_discount(150)

# ---------- DigitalProduct ----------
def test_digital_product_init_and_get_details():
    dp = DigitalProduct("Ebook", 50, "http://link", 5.5)
    details = dp.get_details()
    assert details["name"] == "Ebook"
    assert details["download_link"] == "http://link"
    assert details["file_size_mb"] == 5.5

def test_digital_product_invalid_init():
    with pytest.raises(TypeError):
        DigitalProduct("Ebook", 50, 123, 5.5)
    with pytest.raises(TypeError):
        DigitalProduct("Ebook", 50, "http://link", "big")
    with pytest.raises(ValueError):
        DigitalProduct("Ebook", 50, "http://link", -1)

def test_generate_new_download_link():
    dp = DigitalProduct("Ebook", 50, "http://link", 5.5)
    base_url = "http://download.com/"
    link = dp.generate_new_download_link(base_url)
    assert link.startswith(base_url)
    assert isinstance(link, str)
    with pytest.raises(TypeError):
        dp.generate_new_download_link(123)

# ---------- PhysicalProduct ----------
def test_physical_product_init_and_get_details():
    pp = PhysicalProduct("Table", 1000, 10.0, (2, 1, 0.5))
    details = pp.get_details()
    assert details["name"] == "Table"
    assert details["weight_kg"] == 10.0
    assert details["shipping_dimensions"] == (2, 1, 0.5)

def test_physical_product_invalid_init():
    with pytest.raises(TypeError):
        PhysicalProduct("Table", 1000, "heavy", (2, 1, 0.5))
    with pytest.raises(TypeError):
        PhysicalProduct("Table", 1000, 10, "not-a-tuple")
    with pytest.raises(ValueError):
        PhysicalProduct("Table", 1000, -1, (2, 1, 0.5))

def test_physical_product_calculate_shipping_cost():
    pp = PhysicalProduct("Table", 1000, 10.0, (2, 1, 0.5))
    cost = pp.calculate_shipping_cost(100)
    assert cost > 0
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(-10)

# ---------- Inventory ----------
def test_inventory_add_and_get_product():
    inv = Inventory()
    p = Product("Book", 100, quantity=5)
    inv.add_product(p)
    fetched = inv.get_product(p.get_details()["product_id"])
    assert fetched.get_details()["name"] == "Book"

def test_inventory_add_product_invalid():
    inv = Inventory()
    with pytest.raises(TypeError):
        inv.add_product("not-a-product")
    p = Product("Book", 100)
    with pytest.raises(ValueError):
        inv.add_product(p, initial_stock=-5)

def test_inventory_remove_product():
    inv = Inventory()
    p = Product("Book", 100)
    inv.add_product(p)
    pid = p.get_details()["product_id"]
    removed = inv.remove_product(pid)
    assert removed.get_details()["name"] == "Book"
    with pytest.raises(KeyError):
        inv.remove_product(pid)

def test_inventory_update_stock():
    inv = Inventory()
    p = Product("Book", 100, quantity=5)
    inv.add_product(p)
    pid = p.get_details()["product_id"]
    inv.update_stock(pid, 5)
    assert inv.get_stock_level(pid) == 10
    with pytest.raises(ValueError):
        inv.update_stock(pid, -100)
    with pytest.raises(KeyError):
        inv.update_stock("nonexistent", 1)

def test_inventory_total_value():
    inv = Inventory()
    p1 = Product("Book", 100, quantity=2)
    p2 = Product("Pen", 10, quantity=10)
    inv.add_product(p1)
    inv.add_product(p2)
    assert inv.get_total_inventory_value() == 100*2 + 10*10

def test_inventory_find_products_by_name():
    inv = Inventory()
    p1 = Product("Book", 100)
    p2 = Product("Notebook", 50)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.find_products_by_name("book")
    assert len(results) == 2
    results_cs = inv.find_products_by_name("Book", case_sensitive=True)
    assert len(results_cs) == 1
    with pytest.raises(TypeError):
        inv.find_products_by_name(123)

def test_inventory_get_products_in_price_range():
    inv = Inventory()
    p1 = Product("Book", 100)
    p2 = Product("Pen", 10)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.get_products_in_price_range(50, 150)
    assert p1 in results
    assert p2 not in results
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(200, 100)

def test_inventory_get_stock_level():
    inv = Inventory()
    p = Product("Book", 100, quantity=5)
    inv.add_product(p)
    pid = p.get_details()["product_id"]
    assert inv.get_stock_level(pid) == 5
    with pytest.raises(KeyError):
        inv.get_stock_level("nonexistent")
    with pytest.raises(TypeError):
        inv.get_stock_level(123)

# ---------- Order ----------
def test_order_init_and_add_item():
    inv = Inventory()
    p = Product("Book", 100, quantity=10)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 2, inventory=inv)
    summary = order.get_order_summary()
    assert summary["total"] == 200
    assert summary["status"] == "pending"

def test_order_add_item_invalid():
    inv = Inventory()
    p = Product("Book", 100, quantity=1)
    inv.add_product(p)
    order = Order()
    with pytest.raises(ValueError):
        order.add_item(p, 0, inventory=inv)
    with pytest.raises(TypeError):
        order.add_item("not-a-product", 1, inventory=inv)
    with pytest.raises(KeyError):
        order.add_item(p, 2, inventory=inv)  # not enough stock

def test_order_remove_item():
    inv = Inventory()
    p = Product("Book", 100, quantity=5)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 3, inventory=inv)
    order.remove_item(p.get_details()["product_id"], 2, inventory=inv)
    summary = order.get_order_summary()
    assert summary["items"][0]["quantity"] == 1
    with pytest.raises(ValueError):
        order.remove_item(p.get_details()["product_id"], 5, inventory=inv)

def test_order_update_status():
    order = Order()
    order.update_status("processing")
    assert order.get_order_summary()["status"] == "processing"
    with pytest.raises(ValueError):
        order.update_status("unknown")
    with pytest.raises(TypeError):
        order.update_status(123)

def test_order_finalize():
    order = Order()
    order.finalize_order()
    with pytest.raises(ValueError):
        order.finalize_order()  # Already finalized

def test_order_repr():
    order = Order()
    assert "Order" in repr(order)