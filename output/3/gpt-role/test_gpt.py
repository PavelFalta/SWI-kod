import pytest
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

import uuid

# ---------- FIXTURES ----------

@pytest.fixture
def product():
    return Product(name="Test Product", price=100.0, quantity=10)

@pytest.fixture
def digital_product():
    return DigitalProduct(
        name="E-Book", price=50.0, download_link="https://example.com/file", file_size_mb=5.5
    )

@pytest.fixture
def physical_product():
    return PhysicalProduct(
        name="Laptop", price=1500.0, weight_kg=2.5, shipping_dimensions=(30, 20, 5), quantity=5
    )

@pytest.fixture
def inventory(product, digital_product, physical_product):
    inv = Inventory()
    inv.add_product(product)
    inv.add_product(digital_product)
    inv.add_product(physical_product)
    return inv

@pytest.fixture
def order():
    return Order(customer_id="cust-123")

# ---------- PRODUCT TESTS ----------

@pytest.mark.parametrize("name, price, quantity", [
    ("Valid", 1.0, 0),
    ("Another", 99.99, 10),
])
def test_product_creation_valid(name, price, quantity):
    p = Product(name=name, price=price, quantity=quantity)
    assert p.name == name
    assert p.price == price
    assert p.quantity == quantity
    assert isinstance(uuid.UUID(p.product_id), uuid.UUID)

@pytest.mark.parametrize("name, price, quantity, exc", [
    ("", 10, 1, TypeError),
    (None, 10, 1, TypeError),
    ("Valid", -1, 1, ValueError),
    ("Valid", 0, 1, ValueError),
    ("Valid", 10, -1, ValueError),
])
def test_product_creation_invalid(name, price, quantity, exc):
    with pytest.raises(exc):
        Product(name=name, price=price, quantity=quantity)

def test_product_update_quantity(product):
    product.update_quantity(5)
    assert product.quantity == 15
    product.update_quantity(-10)
    assert product.quantity == 5

def test_product_update_quantity_invalid(product):
    with pytest.raises(TypeError):
        product.update_quantity("not-an-int")
    with pytest.raises(ValueError):
        product.update_quantity(-100)

@pytest.mark.parametrize("discount, expected", [
    (10, 90.0),
    (0, 100.0),
    (100, 0.0),
])
def test_product_apply_discount(product, discount, expected):
    product.apply_discount(discount)
    assert product.price == expected

@pytest.mark.parametrize("discount", [-1, 101])
def test_product_apply_discount_invalid(product, discount):
    with pytest.raises(ValueError):
        product.apply_discount(discount)

# ---------- DIGITAL PRODUCT TESTS ----------

def test_digital_product_creation_valid():
    dp = DigitalProduct(
        name="Music", price=10, download_link="http://example.com/track", file_size_mb=3.2
    )
    assert dp.download_link.startswith("http")
    assert dp.file_size_mb == 3.2

@pytest.mark.parametrize("link", ["ftp://bad", "notalink", "", None])
def test_digital_product_invalid_link(link):
    with pytest.raises(TypeError):
        DigitalProduct(
            name="Music", price=10, download_link=link, file_size_mb=1
        )

@pytest.mark.parametrize("size", [0, -1])
def test_digital_product_invalid_size(size):
    with pytest.raises(ValueError):
        DigitalProduct(
            name="Music", price=10, download_link="http://example.com", file_size_mb=size
        )

def test_digital_product_generate_new_download_link(digital_product):
    base_url = "https://newhost.com"
    new_link = digital_product.generate_new_download_link(base_url)
    assert new_link.startswith(base_url)
    assert digital_product.download_link == new_link

# ---------- PHYSICAL PRODUCT TESTS ----------

def test_physical_product_creation_valid():
    pp = PhysicalProduct(
        name="Box", price=20, weight_kg=1.5, shipping_dimensions=(10, 10, 10)
    )
    assert pp.weight_kg == 1.5
    assert pp.shipping_dimensions == (10, 10, 10)

@pytest.mark.parametrize("weight", [0, -1])
def test_physical_product_invalid_weight(weight):
    with pytest.raises(ValueError):
        PhysicalProduct(
            name="Box", price=20, weight_kg=weight, shipping_dimensions=(10, 10, 10)
        )

@pytest.mark.parametrize("dims", [
    (10, 10),  # too short
    (10, 10, 0),  # zero
    (10, 10, -1),  # negative
    "notatuple",
    (10, "a", 10),
])
def test_physical_product_invalid_dimensions(dims):
    with pytest.raises(TypeError):
        PhysicalProduct(
            name="Box", price=20, weight_kg=1, shipping_dimensions=dims
        )

def test_physical_product_calculate_shipping_cost(physical_product):
    cost = physical_product.calculate_shipping_cost(rate_per_kg=100)
    assert cost > 0

@pytest.mark.parametrize("rate", [0, -1])
def test_physical_product_invalid_shipping_rate(physical_product, rate):
    with pytest.raises(ValueError):
        physical_product.calculate_shipping_cost(rate_per_kg=rate)

# ---------- INVENTORY TESTS ----------

def test_inventory_add_and_get_product(product):
    inv = Inventory()
    inv.add_product(product)
    assert inv.get_product(product.product_id) == product

def test_inventory_add_duplicate(product):
    inv = Inventory()
    inv.add_product(product)
    with pytest.raises(ValueError):
        inv.add_product(product)

def test_inventory_remove_product(product):
    inv = Inventory()
    inv.add_product(product)
    removed = inv.remove_product(product.product_id)
    assert removed == product
    with pytest.raises(KeyError):
        inv.get_product(product.product_id)

def test_inventory_update_stock(product):
    inv = Inventory()
    inv.add_product(product)
    inv.update_stock(product.product_id, 5)
    assert inv.get_product(product.product_id).quantity == 15

def test_inventory_find_products_by_name(inventory):
    results = inventory.find_products_by_name("test", case_sensitive=False)
    assert any("Test" in p.name for p in results)

def test_inventory_get_products_in_price_range(inventory):
    products = inventory.get_products_in_price_range(50, 2000)
    assert all(50 <= p.price <= 2000 for p in products)

# ---------- ORDER TESTS ----------

def test_order_add_and_remove_item(order, product, inventory):
    order.add_item(product, 2, inventory)
    assert order.items[product.product_id]["quantity"] == 2
    order.remove_item(product.product_id, 1, inventory)
    assert order.items[product.product_id]["quantity"] == 1

def test_order_add_item_insufficient_stock(product, inventory, order):
    with pytest.raises(ValueError):
        order.add_item(product, 1000, inventory)

def test_order_remove_item_too_many(order, product, inventory):
    order.add_item(product, 2, inventory)
    with pytest.raises(ValueError):
        order.remove_item(product.product_id, 3, inventory)

def test_order_finalize_and_status(order, product, inventory):
    order.add_item(product, 1, inventory)
    order.finalize_order()
    assert order._is_finalized
    assert order.status == "awaiting_payment"

@pytest.mark.parametrize("status", ["shipped", "delivered", "cancelled", "refunded"])
def test_order_update_status(order, product, inventory, status):
    order.add_item(product, 1, inventory)
    order.finalize_order()
    order.update_status(status)
    assert order.status == status

@pytest.mark.parametrize("bad_status", ["unknown", "processingg", 123])
def test_order_update_status_invalid(order, product, inventory, bad_status):
    order.add_item(product, 1, inventory)
    order.finalize_order()
    with pytest.raises((TypeError, ValueError)):
        order.update_status(bad_status)

def test_order_summary(order, product, inventory):
    order.add_item(product, 2, inventory)
    summary = order.get_order_summary()
    assert summary["total_items"] == 2
    assert summary["total_cost"] == 200.0

def test_order_finalize_empty(order):
    with pytest.raises(ValueError):
        order.finalize_order()