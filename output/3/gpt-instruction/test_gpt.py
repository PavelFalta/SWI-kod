import pytest
import uuid
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# ---------- Product ----------

def test_product_init_valid():
    # Arrange
    name = "Test"
    price = 10.5
    quantity = 3
    # Act
    p = Product(name, price, quantity=quantity)
    # Assert
    assert p.name == name
    assert p.price == price
    assert p.quantity == quantity
    assert isinstance(uuid.UUID(p.product_id), uuid.UUID)

@pytest.mark.parametrize("name", ["", "   ", None, 123])
def test_product_init_invalid_name(name):
    # Arrange-Act-Assert
    with pytest.raises(TypeError):
        Product(name, 10)

@pytest.mark.parametrize("price", [0, -1, "abc", None])
def test_product_init_invalid_price(price):
    with pytest.raises(ValueError):
        Product("Test", price)

@pytest.mark.parametrize("product_id", [123, 1.2, []])
def test_product_init_invalid_product_id(product_id):
    with pytest.raises(TypeError):
        Product("Test", 10, product_id=product_id)

@pytest.mark.parametrize("quantity", [-1, 1.2, "abc"])
def test_product_init_invalid_quantity(quantity):
    with pytest.raises(ValueError):
        Product("Test", 10, quantity=quantity)

def test_product_get_details():
    p = Product("A", 1.5, quantity=2)
    details = p.get_details()
    assert details["name"] == "A"
    assert details["price"] == 1.5
    assert details["quantity"] == 2
    assert details["type"] == "GenericProduct"

def test_product_update_quantity_valid():
    p = Product("A", 1.5, quantity=2)
    p.update_quantity(3)
    assert p.quantity == 5
    p.update_quantity(-2)
    assert p.quantity == 3

def test_product_update_quantity_invalid_type():
    p = Product("A", 1.5, quantity=2)
    with pytest.raises(TypeError):
        p.update_quantity("abc")

def test_product_update_quantity_below_zero():
    p = Product("A", 1.5, quantity=2)
    with pytest.raises(ValueError):
        p.update_quantity(-3)

def test_product_apply_discount_valid():
    p = Product("A", 100)
    p.apply_discount(10)
    assert p.price == 90.0

def test_product_apply_discount_invalid_type():
    p = Product("A", 100)
    with pytest.raises(TypeError):
        p.apply_discount("abc")

@pytest.mark.parametrize("discount", [-1, 101])
def test_product_apply_discount_invalid_value(discount):
    p = Product("A", 100)
    with pytest.raises(ValueError):
        p.apply_discount(discount)

# ---------- DigitalProduct ----------

def test_digital_product_init_valid():
    dp = DigitalProduct("D", 10, "https://example.com/file", 5.5)
    assert dp.download_link.startswith("https://")
    assert dp.file_size_mb == 5.5

@pytest.mark.parametrize("link", ["ftp://bad", "file.txt", "", None])
def test_digital_product_invalid_link(link):
    with pytest.raises(TypeError):
        DigitalProduct("D", 10, link, 5.5)

@pytest.mark.parametrize("size", [0, -1, "abc"])
def test_digital_product_invalid_size(size):
    with pytest.raises(ValueError):
        DigitalProduct("D", 10, "https://example.com", size)

def test_digital_product_get_details():
    dp = DigitalProduct("D", 10, "https://example.com", 5.5)
    details = dp.get_details()
    assert details["type"] == "DigitalProduct"
    assert details["file_size_mb"] == 5.5

def test_digital_product_generate_new_download_link():
    dp = DigitalProduct("D", 10, "https://example.com", 5.5)
    base_url = "https://new.com"
    new_link = dp.generate_new_download_link(base_url)
    assert new_link.startswith(base_url)
    assert dp.download_link == new_link

def test_digital_product_generate_new_download_link_invalid():
    dp = DigitalProduct("D", 10, "https://example.com", 5.5)
    with pytest.raises(TypeError):
        dp.generate_new_download_link("")

# ---------- PhysicalProduct ----------

def test_physical_product_init_valid():
    pp = PhysicalProduct("P", 20, 2.5, (10, 20, 30))
    assert pp.weight_kg == 2.5
    assert pp.shipping_dimensions == (10, 20, 30)

@pytest.mark.parametrize("weight", [0, -1, "abc"])
def test_physical_product_invalid_weight(weight):
    with pytest.raises(ValueError):
        PhysicalProduct("P", 20, weight, (10, 20, 30))

@pytest.mark.parametrize("dims", [
    (10, 20), (10, 20, 0), (10, 20, -1), (10, 20, "a"), "abc", None
])
def test_physical_product_invalid_dimensions(dims):
    with pytest.raises(TypeError):
        PhysicalProduct("P", 20, 2.5, dims)

def test_physical_product_get_details():
    pp = PhysicalProduct("P", 20, 2.5, (10, 20, 30))
    details = pp.get_details()
    assert details["type"] == "PhysicalProduct"
    assert details["weight_kg"] == 2.5

def test_physical_product_calculate_shipping_cost_valid():
    pp = PhysicalProduct("P", 20, 2.5, (10, 20, 30))
    cost = pp.calculate_shipping_cost(10)
    assert isinstance(cost, float)

@pytest.mark.parametrize("rate", [0, -1, "abc"])
def test_physical_product_calculate_shipping_cost_invalid_rate(rate):
    pp = PhysicalProduct("P", 20, 2.5, (10, 20, 30))
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(rate)

@pytest.mark.parametrize("factor", [0, -1, 1.5])
def test_physical_product_calculate_shipping_cost_invalid_factor(factor):
    pp = PhysicalProduct("P", 20, 2.5, (10, 20, 30))
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(10, volumetric_factor=factor)

# ---------- Inventory ----------

def test_inventory_add_and_get_product():
    inv = Inventory()
    p = Product("A", 1.5)
    inv.add_product(p)
    assert inv.get_product(p.product_id) == p

def test_inventory_add_product_duplicate():
    inv = Inventory()
    p = Product("A", 1.5)
    inv.add_product(p)
    with pytest.raises(ValueError):
        inv.add_product(p)

def test_inventory_add_product_invalid():
    inv = Inventory()
    with pytest.raises(TypeError):
        inv.add_product("not a product")

def test_inventory_add_product_with_initial_stock():
    inv = Inventory()
    p = Product("A", 1.5)
    inv.add_product(p, initial_stock=5)
    assert p.quantity == 5

def test_inventory_add_product_invalid_initial_stock():
    inv = Inventory()
    p = Product("A", 1.5)
    with pytest.raises(ValueError):
        inv.add_product(p, initial_stock=-1)

def test_inventory_remove_product():
    inv = Inventory()
    p = Product("A", 1.5)
    inv.add_product(p)
    removed = inv.remove_product(p.product_id)
    assert removed == p
    assert p.product_id not in inv.products

def test_inventory_remove_product_invalid_id():
    inv = Inventory()
    with pytest.raises(TypeError):
        inv.remove_product(123)
    with pytest.raises(KeyError):
        inv.remove_product("notfound")

def test_inventory_update_stock_valid():
    inv = Inventory()
    p = Product("A", 1.5, quantity=5)
    inv.add_product(p)
    inv.update_stock(p.product_id, -2)
    assert p.quantity == 3

def test_inventory_update_stock_invalid():
    inv = Inventory()
    p = Product("A", 1.5, quantity=1)
    inv.add_product(p)
    with pytest.raises(ValueError):
        inv.update_stock(p.product_id, -2)

def test_inventory_get_total_inventory_value():
    inv = Inventory()
    p1 = Product("A", 2, quantity=2)
    p2 = Product("B", 3, quantity=1)
    inv.add_product(p1)
    inv.add_product(p2)
    assert inv.get_total_inventory_value() == 7.0

def test_inventory_find_products_by_name():
    inv = Inventory()
    p1 = Product("Apple", 1)
    p2 = Product("Banana", 1)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.find_products_by_name("app")
    assert p1 in results
    assert p2 not in results

def test_inventory_find_products_by_name_case_sensitive():
    inv = Inventory()
    p1 = Product("Apple", 1)
    inv.add_product(p1)
    assert inv.find_products_by_name("App", case_sensitive=True)
    assert not inv.find_products_by_name("app", case_sensitive=True)

def test_inventory_find_products_by_name_invalid():
    inv = Inventory()
    with pytest.raises(TypeError):
        inv.find_products_by_name(123)

def test_inventory_get_products_in_price_range():
    inv = Inventory()
    p1 = Product("A", 2)
    p2 = Product("B", 5)
    inv.add_product(p1)
    inv.add_product(p2)
    results = inv.get_products_in_price_range(1, 3)
    assert p1 in results
    assert p2 not in results

def test_inventory_get_products_in_price_range_invalid():
    inv = Inventory()
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(-1, 10)
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(10, 5)

def test_inventory_get_stock_level():
    inv = Inventory()
    p = Product("A", 1, quantity=7)
    inv.add_product(p)
    assert inv.get_stock_level(p.product_id) == 7

# ---------- Order ----------

def test_order_init_valid():
    o = Order()
    assert o.status == "pending"
    assert o.items == {}

def test_order_init_invalid_ids():
    with pytest.raises(TypeError):
        Order(order_id=123)
    with pytest.raises(TypeError):
        Order(customer_id=123)

def test_order_add_item_valid():
    inv = Inventory()
    p = Product("A", 10, quantity=5)
    inv.add_product(p)
    o = Order()
    o.add_item(p, 2, inventory=inv)
    assert o.items[p.product_id]["quantity"] == 2
    assert p.quantity == 3

def test_order_add_item_invalid():
    o = Order()
    with pytest.raises(TypeError):
        o.add_item("not a product", 1)
    p = Product("A", 10)
    with pytest.raises(ValueError):
        o.add_item(p, 0)
    with pytest.raises(ValueError):
        o.add_item(p, -1)

def test_order_add_item_not_enough_stock():
    inv = Inventory()
    p = Product("A", 10, quantity=1)
    inv.add_product(p)
    o = Order()
    with pytest.raises(ValueError):
        o.add_item(p, 2, inventory=inv)

def test_order_add_item_to_finalized():
    o = Order()
    o._is_finalized = True
    p = Product("A", 10)
    with pytest.raises(RuntimeError):
        o.add_item(p, 1)

def test_order_remove_item_valid():
    inv = Inventory()
    p = Product("A", 10, quantity=5)
    inv.add_product(p)
    o = Order()
    o.add_item(p, 2, inventory=inv)
    o.remove_item(p.product_id, 1, inventory=inv)
    assert o.items[p.product_id]["quantity"] == 1
    assert p.quantity == 4

def test_order_remove_item_invalid():
    o = Order()
    with pytest.raises(TypeError):
        o.remove_item(123, 1)
    with pytest.raises(ValueError):
        o.remove_item("id", 0)
    with pytest.raises(ValueError):
        o.remove_item("id", -1)
    with pytest.raises(KeyError):
        o.remove_item("notfound", 1)

def test_order_remove_item_too_many():
    o = Order()
    p = Product("A", 10)
    o.add_item(p, 1)
    with pytest.raises(ValueError):
        o.remove_item(p.product_id, 2)

def test_order_remove_item_finalized_status():
    o = Order()
    p = Product("A", 10)
    o.add_item(p, 1)
    o._is_finalized = True
    o.status = "shipped"
    with pytest.raises(RuntimeError):
        o.remove_item(p.product_id, 1)

def test_order_calculate_total():
    o = Order()
    p = Product("A", 10)
    o.add_item(p, 2)
    assert o.calculate_total() == 20

def test_order_update_status_valid():
    o = Order()
    o.update_status("processing")
    assert o.status == "processing"

def test_order_update_status_invalid_type():
    o = Order()
    with pytest.raises(TypeError):
        o.update_status(123)

def test_order_update_status_invalid_value():
    o = Order()
    with pytest.raises(ValueError):
        o.update_status("not_a_status")

def test_order_update_status_delivered():
    o = Order()
    o.status = "delivered"
    with pytest.raises(ValueError):
        o.update_status("processing")

def test_order_update_status_cancelled():
    o = Order()
    o.status = "cancelled"
    with pytest.raises(ValueError):
        o.update_status("pending")

def test_order_get_order_summary():
    o = Order(customer_id="cust1")
    p = Product("A", 10)
    o.add_item(p, 2)
    summary = o.get_order_summary()
    assert summary["customer_id"] == "cust1"
    assert summary["total_items"] == 2
    assert summary["total_cost"] == 20

def test_order_finalize_order_valid():
    o = Order()
    p = Product("A", 10)
    o.add_item(p, 1)
    o.finalize_order()
    assert o._is_finalized
    assert o.status == "awaiting_payment"

def test_order_finalize_order_empty():
    o = Order()
    with pytest.raises(ValueError):
        o.finalize_order()