import pytest
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# ----------- Product -----------
def test_product_init_and_get_details():
    p = Product("Test", 99.99, quantity=10)
    details = p.get_details()
    assert details["name"] == "Test"
    assert details["price"] == 99.99
    assert details["quantity"] == 10
    assert isinstance(details["product_id"], str)

def test_product_invalid_init():
    with pytest.raises(TypeError):
        Product(123, 10.0)
    with pytest.raises(TypeError):
        Product("Test", "not a float")
    with pytest.raises(ValueError):
        Product("Test", -1.0)
    with pytest.raises(ValueError):
        Product("Test", 10.0, quantity=-5)

def test_product_update_quantity():
    p = Product("Test", 10.0, quantity=5)
    p.update_quantity(3)
    assert p.get_details()["quantity"] == 8
    p.update_quantity(-2)
    assert p.get_details()["quantity"] == 6
    with pytest.raises(TypeError):
        p.update_quantity("not an int")
    with pytest.raises(ValueError):
        p.update_quantity(-100)  # would go negative

def test_product_apply_discount():
    p = Product("Test", 100.0)
    p.apply_discount(10)
    assert p.get_details()["price"] == 90.0
    with pytest.raises(TypeError):
        p.apply_discount("not a float")
    with pytest.raises(ValueError):
        p.apply_discount(-5)
    with pytest.raises(ValueError):
        p.apply_discount(150)

# ----------- DigitalProduct -----------
def test_digital_product_init_and_details():
    dp = DigitalProduct("Ebook", 20.0, "http://link", 5.5)
    details = dp.get_details()
    assert details["download_link"] == "http://link"
    assert details["file_size_mb"] == 5.5

def test_digital_product_generate_new_download_link():
    dp = DigitalProduct("Ebook", 20.0, "http://link", 5.5)
    link = dp.generate_new_download_link("http://baseurl/")
    assert link.startswith("http://baseurl/")
    with pytest.raises(TypeError):
        dp.generate_new_download_link(123)

# ----------- PhysicalProduct -----------
def test_physical_product_init_and_details():
    pp = PhysicalProduct("Book", 30.0, 0.5, (20, 15, 2))
    details = pp.get_details()
    assert details["weight_kg"] == 0.5
    assert details["shipping_dimensions"] == (20, 15, 2)

def test_physical_product_calculate_shipping_cost():
    pp = PhysicalProduct("Book", 30.0, 2.0, (20, 15, 10))
    cost = pp.calculate_shipping_cost(10.0)
    assert isinstance(cost, float)
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(-1.0)

# ----------- Inventory -----------
def test_inventory_add_and_get_product():
    inv = Inventory()
    p = Product("Test", 10.0)
    inv.add_product(p, initial_stock=5)
    fetched = inv.get_product(p.get_details()["product_id"])
    assert fetched.get_details()["name"] == "Test"
    assert inv.get_stock_level(p.get_details()["product_id"]) == 5

def test_inventory_remove_product():
    inv = Inventory()
    p = Product("Test", 10.0)
    inv.add_product(p)
    pid = p.get_details()["product_id"]
    removed = inv.remove_product(pid)
    assert removed is p
    with pytest.raises(KeyError):
        inv.remove_product(pid)

def test_inventory_update_stock():
    inv = Inventory()
    p = Product("Test", 10.0)
    inv.add_product(p, initial_stock=2)
    pid = p.get_details()["product_id"]
    inv.update_stock(pid, 3)
    assert inv.get_stock_level(pid) == 5
    with pytest.raises(ValueError):
        inv.update_stock(pid, -10)
    with pytest.raises(KeyError):
        inv.update_stock("nonexistent", 1)

def test_inventory_find_products_by_name():
    inv = Inventory()
    p1 = Product("Apple", 1.0)
    p2 = Product("Banana", 2.0)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.find_products_by_name("app")
    assert p1 in results
    assert p2 not in results
    results_cs = inv.find_products_by_name("App", case_sensitive=True)
    assert p1 in results_cs
    assert p2 not in results_cs
    with pytest.raises(TypeError):
        inv.find_products_by_name(123)

def test_inventory_get_products_in_price_range():
    inv = Inventory()
    p1 = Product("Cheap", 5.0)
    p2 = Product("Expensive", 100.0)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.get_products_in_price_range(1, 10)
    assert p1 in results
    assert p2 not in results
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(10, 1)

def test_inventory_total_value():
    inv = Inventory()
    p1 = Product("A", 10.0)
    p2 = Product("B", 20.0)
    inv.add_product(p1, initial_stock=2)
    inv.add_product(p2, initial_stock=1)
    assert inv.get_total_inventory_value() == 10.0*2 + 20.0*1

# ----------- Order -----------
def test_order_add_and_remove_item(monkeypatch):
    inv = Inventory()
    p = Product("Test", 10.0)
    inv.add_product(p, initial_stock=5)
    order = Order()
    order.add_item(p, 2, inventory=inv)
    assert order.calculate_total() == 20.0
    order.remove_item(p.get_details()["product_id"], 1, inventory=inv)
    assert order.calculate_total() == 10.0
    with pytest.raises(ValueError):
        order.remove_item(p.get_details()["product_id"], 10, inventory=inv)

def test_order_status_and_finalize():
    order = Order()
    order.update_status("processing")
    assert order.get_order_summary()["status"] == "processing"
    with pytest.raises(TypeError):
        order.update_status(123)
    with pytest.raises(ValueError):
        order.update_status("not_a_status")
    order.finalize_order()
    with pytest.raises(ValueError):
        order.finalize_order()

def test_order_repr():
    order = Order()
    assert "Order" in repr(order)