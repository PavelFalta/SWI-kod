import pytest
import uuid

from code_normal import (  # Změň na své jméno souboru/modulu
    Product,
    DigitalProduct,
    PhysicalProduct,
    Inventory,
    Order
)

# -------- Product Base --------

def test_product_init_and_get_details():
    p = Product(name="Book", price=129.99, quantity=10)
    details = p.get_details()
    assert details["name"] == "Book"
    assert details["price"] == 129.99
    assert details["quantity"] == 10
    assert isinstance(details["product_id"], str)

def test_product_invalid_types():
    with pytest.raises(TypeError):
        Product(name=123, price=10.0)
    with pytest.raises(TypeError):
        Product(name="x", price="9.99")
    with pytest.raises(ValueError):
        Product(name="x", price=10, quantity=-4)

def test_product_update_quantity():
    p = Product("Pen", 15.0, quantity=3)
    p.update_quantity(2)
    assert p.get_details()["quantity"] == 5
    p.update_quantity(-1)
    assert p.get_details()["quantity"] == 4
    with pytest.raises(TypeError):
        p.update_quantity("ten")
    with pytest.raises(ValueError):
        p.update_quantity(-100)  # negativní stav

def test_product_apply_discount():
    p = Product("Pencil", 20.0)
    p.apply_discount(10)
    assert round(p.get_details()["price"], 2) == 18.00
    with pytest.raises(TypeError):
        p.apply_discount("10")
    with pytest.raises(ValueError):
        p.apply_discount(-5)

# -------- DigitalProduct --------

def test_digital_product_init_and_details():
    dp = DigitalProduct("E-book", 49.0, "https://url", 5.7)
    details = dp.get_details()
    assert details["download_link"].startswith("http")
    assert details["file_size_mb"] == 5.7

def test_digital_product_invalid_types():
    with pytest.raises(TypeError):
        DigitalProduct("E-book", 39.0, 123, 1.1)
    with pytest.raises(TypeError):
        DigitalProduct("E-book", 39.0, "xxx", "1.5")

def test_digital_product_generate_new_link():
    dp = DigitalProduct("E-book", 12.0, "x", 1.0)
    new_link = dp.generate_new_download_link("https://baseurl.com")
    assert new_link.startswith("https://baseurl.com/")
    # Ensure it's a uuid or at least unique:
    uuid_part = new_link.split("/")[-1]
    uuid.UUID(uuid_part)  # Should not error

    with pytest.raises(TypeError):
        dp.generate_new_download_link(1234)

# -------- PhysicalProduct --------

def test_physical_product_init_and_details():
    pp = PhysicalProduct("Mug", 79.0, 0.35, (10,10,10), quantity=5)
    d = pp.get_details()
    assert d["weight_kg"] == 0.35
    assert d["shipping_dimensions"] == (10, 10, 10)

def test_physical_product_invalid_types():
    with pytest.raises(TypeError):
        PhysicalProduct("Shirt", 99.0, "0.5", (30, 40, 3))
    with pytest.raises(TypeError):
        PhysicalProduct("Shirt", 99.0, 0.5, "30x40x3")
    with pytest.raises(ValueError):
        PhysicalProduct("Shirt", 99.0, -1, (1,1,1))

def test_physical_product_calculate_shipping_cost():
    pp = PhysicalProduct("Vase", 200, 2.0, (40,20,10))
    cost = pp.calculate_shipping_cost(100)
    assert cost > 0
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(-1)

# -------- Inventory --------

@pytest.fixture
def basic_inventory():
    inv = Inventory()
    prod1 = Product("Notebook", 90, quantity=4)
    prod2 = Product("Pen", 9.5, quantity=10)
    inv.add_product(prod1)
    inv.add_product(prod2)
    return inv, prod1, prod2

def test_inventory_add_and_get_product(basic_inventory):
    inv, prod1, _ = basic_inventory
    fetched = inv.get_product(prod1.get_details()["product_id"])
    assert fetched is prod1

def test_inventory_add_invalid():
    inv = Inventory()
    with pytest.raises(TypeError):
        inv.add_product("abc")

def test_inventory_remove_product(basic_inventory):
    inv, prod1, _ = basic_inventory
    inv.remove_product(prod1.get_details()["product_id"])
    with pytest.raises(KeyError):
        inv.get_product(prod1.get_details()["product_id"])

def test_inventory_update_and_get_stock(basic_inventory):
    inv, prod1, _ = basic_inventory
    pid = prod1.get_details()["product_id"]
    inv.update_stock(pid, 3)
    assert inv.get_stock_level(pid) == 7
    inv.update_stock(pid, -2)
    assert inv.get_stock_level(pid) == 5
    with pytest.raises(ValueError):
        inv.update_stock(pid, -100)
    with pytest.raises(KeyError):
        inv.update_stock("nonexistent", 2)

def test_inventory_total_value(basic_inventory):
    inv, _, _ = basic_inventory
    val = inv.get_total_inventory_value()
    assert isinstance(val, float)
    assert val > 0

def test_inventory_find_by_name(basic_inventory):
    inv, _, _ = basic_inventory
    results = inv.find_products_by_name("Note")
    assert results
    assert "Note" in results[0].get_details()["name"]
    results2 = inv.find_products_by_name("pen", case_sensitive=False)
    assert results2
    with pytest.raises(TypeError):
        inv.find_products_by_name(1234)

def test_inventory_get_products_in_price_range(basic_inventory):
    inv, _, _ = basic_inventory
    results = inv.get_products_in_price_range(5, 100)
    assert all(5 <= prod.get_details()["price"] <= 100 for prod in results)
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(100, 5)

# -------- Order --------

def test_order_create_and_add_item(basic_inventory):
    inv, prod, _ = basic_inventory
    order = Order()
    order.add_item(prod, 2, inventory=inv)
    summary = order.get_order_summary()
    assert summary["total_items"] == 2
    assert summary["status"] == "pending"
    assert summary["order_id"]

def test_order_add_item_invalid(basic_inventory):
    inv, prod, _ = basic_inventory
    order = Order()
    with pytest.raises(TypeError):
        order.add_item("not a product", 3)
    with pytest.raises(TypeError):
        order.add_item(prod, "3")
    with pytest.raises(ValueError):
        order.add_item(prod, -1)
    with pytest.raises(KeyError):
        order.add_item(Product("Ghost", 1), 1, inventory=inv)

def test_order_remove_item_and_calculate(basic_inventory):
    inv, prod, _ = basic_inventory
    order = Order()
    order.add_item(prod, 3, inventory=inv)
    order.remove_item(prod.get_details()["product_id"], 2, inventory=inv)
    summary = order.get_order_summary()
    assert summary["total_items"] == 1

    with pytest.raises(ValueError):
        order.remove_item(prod.get_details()["product_id"], 100, inventory=inv)
    with pytest.raises(KeyError):
        order.remove_item("nonexistent", 1, inventory=inv)

def test_order_status_and_finalize():
    order = Order()
    order.update_status("processing")
    assert order.get_order_summary()["status"] == "processing"
    with pytest.raises(TypeError):
        order.update_status(123)
    with pytest.raises(ValueError):
        order.update_status("invalid_status")

    # Finalize should only be called once
    order.finalize_order()
    with pytest.raises(ValueError):
        order.finalize_order()

def test_order_repr():
    order = Order()
    assert "Order(" in repr(order)

# ---------- END OF TESTS -----------