import pytest
import uuid

from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# ---------- Product ----------
def test_product_init_valid():
    p = Product("Test", 10.5, quantity=5)
    assert p.name == "Test"
    assert p.price == 10.5
    assert p.quantity == 5
    assert isinstance(p.product_id, str)

def test_product_init_invalid_types():
    with pytest.raises(TypeError):
        Product(123, 10.5)
    with pytest.raises(TypeError):
        Product("Test", "not-a-float")
    with pytest.raises(TypeError):
        Product("Test", 10.5, quantity="not-an-int")

def test_product_init_invalid_values():
    with pytest.raises(ValueError):
        Product("Test", -1)
    with pytest.raises(ValueError):
        Product("Test", 10.5, quantity=-5)

def test_product_get_details():
    p = Product("Test", 10.5, quantity=2)
    details = p.get_details()
    assert details["name"] == "Test"
    assert details["price"] == 10.5
    assert details["quantity"] == 2

def test_product_update_quantity_valid():
    p = Product("Test", 10.5, quantity=2)
    p.update_quantity(3)
    assert p.quantity == 5
    p.update_quantity(-2)
    assert p.quantity == 3

def test_product_update_quantity_invalid():
    p = Product("Test", 10.5, quantity=2)
    with pytest.raises(TypeError):
        p.update_quantity("not-an-int")
    with pytest.raises(ValueError):
        p.update_quantity(-5)  # would make quantity negative

def test_product_apply_discount_valid():
    p = Product("Test", 100)
    p.apply_discount(10)
    assert p.price == 90

def test_product_apply_discount_invalid():
    p = Product("Test", 100)
    with pytest.raises(TypeError):
        p.apply_discount("not-a-float")
    with pytest.raises(ValueError):
        p.apply_discount(-5)
    with pytest.raises(ValueError):
        p.apply_discount(150)

# ---------- DigitalProduct ----------
def test_digital_product_init_valid():
    dp = DigitalProduct("Ebook", 20, "http://link", 5.5)
    assert dp.download_link == "http://link"
    assert dp.file_size_mb == 5.5
    assert dp.quantity == 1

def test_digital_product_init_invalid():
    with pytest.raises(TypeError):
        DigitalProduct("Ebook", 20, 123, 5.5)
    with pytest.raises(TypeError):
        DigitalProduct("Ebook", 20, "http://link", "not-a-float")
    with pytest.raises(ValueError):
        DigitalProduct("Ebook", 20, "http://link", -1)

def test_digital_product_get_details():
    dp = DigitalProduct("Ebook", 20, "http://link", 5.5)
    details = dp.get_details()
    assert details["download_link"] == "http://link"
    assert details["file_size_mb"] == 5.5

def test_digital_product_generate_new_download_link():
    dp = DigitalProduct("Ebook", 20, "http://link", 5.5)
    base_url = "http://download.com/"
    new_link = dp.generate_new_download_link(base_url)
    assert new_link.startswith(base_url)
    assert new_link != dp.download_link

    with pytest.raises(TypeError):
        dp.generate_new_download_link(123)

# ---------- PhysicalProduct ----------
def test_physical_product_init_valid():
    pp = PhysicalProduct("Book", 30, 0.5, (20, 15, 2))
    assert pp.weight_kg == 0.5
    assert pp.shipping_dimensions == (20, 15, 2)

def test_physical_product_init_invalid():
    with pytest.raises(TypeError):
        PhysicalProduct("Book", 30, "not-a-float", (20, 15, 2))
    with pytest.raises(TypeError):
        PhysicalProduct("Book", 30, 0.5, "not-a-tuple")
    with pytest.raises(ValueError):
        PhysicalProduct("Book", 30, -1, (20, 15, 2))

def test_physical_product_get_details():
    pp = PhysicalProduct("Book", 30, 0.5, (20, 15, 2))
    details = pp.get_details()
    assert details["weight_kg"] == 0.5
    assert details["shipping_dimensions"] == (20, 15, 2)

def test_physical_product_calculate_shipping_cost():
    pp = PhysicalProduct("Book", 30, 2, (20, 15, 2))
    cost = pp.calculate_shipping_cost(10)
    assert isinstance(cost, float)
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(-1)

# ---------- Inventory ----------
def test_inventory_add_and_get_product():
    inv = Inventory()
    p = Product("Test", 10)
    inv.add_product(p, initial_stock=5)
    assert inv.get_product(p.product_id) == p
    assert inv.get_stock_level(p.product_id) == 5

def test_inventory_add_product_invalid():
    inv = Inventory()
    with pytest.raises(TypeError):
        inv.add_product("not-a-product")
    p = Product("Test", 10)
    with pytest.raises(ValueError):
        inv.add_product(p, initial_stock=-1)

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
    p = Product("Test", 10)
    inv.add_product(p, initial_stock=2)
    inv.update_stock(p.product_id, 3)
    assert inv.get_stock_level(p.product_id) == 5
    with pytest.raises(ValueError):
        inv.update_stock(p.product_id, -10)
    with pytest.raises(KeyError):
        inv.update_stock("nonexistent", 1)

def test_inventory_get_total_inventory_value():
    inv = Inventory()
    p1 = Product("A", 10, quantity=2)
    p2 = Product("B", 20, quantity=1)
    inv.add_product(p1, initial_stock=2)
    inv.add_product(p2, initial_stock=1)
    assert inv.get_total_inventory_value() == 10*2 + 20*1

def test_inventory_find_products_by_name():
    inv = Inventory()
    p1 = Product("Apple", 10)
    p2 = Product("Banana", 20)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.find_products_by_name("app")
    assert p1 in results
    assert p2 not in results
    results = inv.find_products_by_name("App", case_sensitive=True)
    assert p1 not in results

def test_inventory_get_products_in_price_range():
    inv = Inventory()
    p1 = Product("A", 10)
    p2 = Product("B", 20)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.get_products_in_price_range(15, 25)
    assert p2 in results
    assert p1 not in results
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(30, 10)

# ---------- Order ----------
def test_order_init_and_add_item():
    inv = Inventory()
    p = Product("Test", 10)
    inv.add_product(p, initial_stock=5)
    order = Order()
    order.add_item(p, 2, inventory=inv)
    summary = order.get_order_summary()
    assert summary["total_items"] == 2

def test_order_add_item_invalid():
    order = Order()
    with pytest.raises(TypeError):
        order.add_item("not-a-product", 1)
    p = Product("Test", 10)
    with pytest.raises(ValueError):
        order.add_item(p, -1)
    inv = Inventory()
    inv.add_product(p, initial_stock=1)
    with pytest.raises(ValueError):
        order.add_item(p, 2, inventory=inv)

def test_order_remove_item():
    inv = Inventory()
    p = Product("Test", 10)
    inv.add_product(p, initial_stock=5)
    order = Order()
    order.add_item(p, 3, inventory=inv)
    order.remove_item(p.product_id, 2, inventory=inv)
    summary = order.get_order_summary()
    assert summary["total_items"] == 1
    with pytest.raises(KeyError):
        order.remove_item("nonexistent", 1)

def test_order_calculate_total():
    inv = Inventory()
    p = Product("Test", 10)
    inv.add_product(p, initial_stock=5)
    order = Order()
    order.add_item(p, 2, inventory=inv)
    assert order.calculate_total() == 20

def test_order_update_status():
    order = Order()
    order.update_status("processing")
    assert order.status == "processing"
    with pytest.raises(ValueError):
        order.update_status("not-a-status")
    with pytest.raises(TypeError):
        order.update_status(123)

def test_order_finalize_order():
    order = Order()
    order.status = "pending"
    order.finalize_order()
    assert order.status == "processing" or order.status == "finalized"  # depending on implementation
    order.status = "cancelled"
    with pytest.raises(ValueError):
        order.finalize_order()