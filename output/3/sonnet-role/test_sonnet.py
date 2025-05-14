import sys
sys.path.append("..")

import pytest
import uuid
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order


# Fixtures
@pytest.fixture
def valid_product():
    return Product("Test Product", 19.99, quantity=10)

@pytest.fixture
def digital_product():
    return DigitalProduct("Digital Item", 29.99, "https://example.com/download", 250.5)

@pytest.fixture
def physical_product():
    return PhysicalProduct("Physical Item", 99.99, 2.5, (30, 20, 10), quantity=5)

@pytest.fixture
def inventory():
    inv = Inventory()
    return inv

@pytest.fixture
def populated_inventory():
    inv = Inventory()
    p1 = Product("Basic Item", 10.00, quantity=5)
    p2 = DigitalProduct("Digital Item", 19.99, "https://example.com/download", 100)
    p3 = PhysicalProduct("Physical Item", 29.99, 1.5, (25, 15, 10), quantity=3)
    inv.add_product(p1)
    inv.add_product(p2)
    inv.add_product(p3)
    return inv, [p1, p2, p3]

@pytest.fixture
def order():
    return Order(customer_id="cust123")


# Product Tests
class TestProduct:
    def test_product_initialization(self, valid_product):
        assert valid_product.name == "Test Product"
        assert valid_product.price == 19.99
        assert valid_product.quantity == 10
        assert isinstance(valid_product.product_id, str)

    @pytest.mark.parametrize("name, price, expected_error", [
        ("", 10.00, TypeError),
        (123, 10.00, TypeError),
        ("Product", -5.00, ValueError),
        ("Product", "10.00", ValueError),
        ("Product", 10.00, None)
    ])
    def test_product_validation(self, name, price, expected_error):
        if expected_error:
            with pytest.raises(expected_error):
                Product(name, price)
        else:
            product = Product(name, price)
            assert product.name == name
            assert product.price == price

    def test_update_quantity(self, valid_product):
        valid_product.update_quantity(5)
        assert valid_product.quantity == 15
        
        valid_product.update_quantity(-10)
        assert valid_product.quantity == 5
        
        with pytest.raises(ValueError):
            valid_product.update_quantity(-10)
            
        with pytest.raises(TypeError):
            valid_product.update_quantity("5")

    @pytest.mark.parametrize("discount, expected_price", [
        (10, 17.99),
        (0, 19.99),
        (100, 0.00)
    ])
    def test_apply_discount(self, valid_product, discount, expected_price):
        valid_product.apply_discount(discount)
        assert valid_product.price == expected_price

    def test_get_details(self, valid_product):
        details = valid_product.get_details()
        assert details["name"] == "Test Product"
        assert details["price"] == 19.99
        assert details["quantity"] == 10
        assert details["type"] == "GenericProduct"


# DigitalProduct Tests
class TestDigitalProduct:
    def test_digital_product_initialization(self, digital_product):
        assert digital_product.name == "Digital Item"
        assert digital_product.price == 29.99
        assert digital_product.download_link == "https://example.com/download"
        assert digital_product.file_size_mb == 250.5
        assert digital_product.quantity == 1

    def test_invalid_digital_product(self):
        with pytest.raises(TypeError):
            DigitalProduct("Test", 10.00, "invalid-link", 100)
            
        with pytest.raises(ValueError):
            DigitalProduct("Test", 10.00, "https://example.com", -5)

    def test_generate_new_download_link(self, digital_product):
        new_link = digital_product.generate_new_download_link("https://newsite.com")
        assert new_link.startswith("https://newsite.com/")
        assert digital_product.product_id in new_link

    def test_get_details(self, digital_product):
        details = digital_product.get_details()
        assert details["type"] == "DigitalProduct"
        assert details["download_link"] == "https://example.com/download"
        assert details["file_size_mb"] == 250.5


# PhysicalProduct Tests
class TestPhysicalProduct:
    def test_physical_product_initialization(self, physical_product):
        assert physical_product.name == "Physical Item"
        assert physical_product.price == 99.99
        assert physical_product.weight_kg == 2.5
        assert physical_product.shipping_dimensions == (30, 20, 10)
        assert physical_product.quantity == 5

    def test_invalid_physical_product(self):
        with pytest.raises(ValueError):
            PhysicalProduct("Test", 10.00, -1, (10, 10, 10))
            
        with pytest.raises(TypeError):
            PhysicalProduct("Test", 10.00, 1, [10, 10, 10])
            
        with pytest.raises(TypeError):
            PhysicalProduct("Test", 10.00, 1, (10, -5, 10))

    @pytest.mark.parametrize("rate, expected_cost", [
        (5, 12.5),
        (10, 25.0)
    ])
    def test_calculate_shipping_cost(self, physical_product, rate, expected_cost):
        cost = physical_product.calculate_shipping_cost(rate)
        assert cost == expected_cost
        
    def test_volumetric_weight(self):
        product = PhysicalProduct("Big Light Item", 10.00, 0.5, (100, 80, 60))
        cost = product.calculate_shipping_cost(5, 5000)
        volumetric_weight = (100 * 80 * 60) / 5000  # = 96
        expected = 96 * 5  # volumetric weight * rate
        assert cost == expected


# Inventory Tests
class TestInventory:
    def test_add_product(self, inventory, valid_product):
        inventory.add_product(valid_product)
        assert valid_product.product_id in inventory.products
        assert inventory.products[valid_product.product_id] is valid_product

    def test_add_existing_product(self, inventory, valid_product):
        inventory.add_product(valid_product)
        with pytest.raises(ValueError):
            inventory.add_product(valid_product)

    def test_add_with_initial_stock(self, inventory, valid_product):
        valid_product.quantity = 0
        inventory.add_product(valid_product, initial_stock=15)
        assert valid_product.quantity == 15

    def test_remove_product(self, populated_inventory):
        inventory, products = populated_inventory
        product = inventory.remove_product(products[0].product_id)
        assert product is products[0]
        assert products[0].product_id not in inventory.products

    def test_get_product(self, populated_inventory):
        inventory, products = populated_inventory
        product = inventory.get_product(products[1].product_id)
        assert product is products[1]

    def test_update_stock(self, populated_inventory):
        inventory, products = populated_inventory
        initial_qty = products[0].quantity
        inventory.update_stock(products[0].product_id, 5)
        assert products[0].quantity == initial_qty + 5
        
        with pytest.raises(ValueError):
            inventory.update_stock(products[0].product_id, -100)

    def test_get_total_inventory_value(self, populated_inventory):
        inventory, products = populated_inventory
        expected_value = sum(p.price * p.quantity for p in products)
        assert inventory.get_total_inventory_value() == round(expected_value, 2)

    def test_find_products_by_name(self, populated_inventory):
        inventory, products = populated_inventory
        results = inventory.find_products_by_name("item")
        assert len(results) == 3
        
        results = inventory.find_products_by_name("DIGITAL", case_sensitive=False)
        assert len(results) == 1
        assert results[0] is products[1]

    def test_get_products_in_price_range(self, populated_inventory):
        inventory, products = populated_inventory
        results = inventory.get_products_in_price_range(15, 25)
        assert len(results) == 1
        assert results[0] is products[1]


# Order Tests
class TestOrder:
    def test_order_initialization(self, order):
        assert order.customer_id == "cust123"
        assert isinstance(order.order_id, str)
        assert order.status == "pending"
        assert not order._is_finalized
        assert len(order.items) == 0

    def test_add_item_without_inventory(self, order, valid_product):
        order.add_item(valid_product, 2)
        assert valid_product.product_id in order.items
        assert order.items[valid_product.product_id]["quantity"] == 2
        assert order.items[valid_product.product_id]["price_at_purchase"] == valid_product.price

    def test_add_item_with_inventory(self, order, populated_inventory):
        inventory, products = populated_inventory
        initial_qty = products[0].quantity
        order.add_item(products[0], 2, inventory)
        assert products[0].product_id in order.items
        assert order.items[products[0].product_id]["quantity"] == 2
        assert products[0].quantity == initial_qty - 2

    def test_add_item_insufficient_stock(self, order, populated_inventory):
        inventory, products = populated_inventory
        with pytest.raises(ValueError):
            order.add_item(products[0], 100, inventory)

    def test_remove_item(self, order, valid_product):
        order.add_item(valid_product, 5)
        order.remove_item(valid_product.product_id, 2)
        assert order.items[valid_product.product_id]["quantity"] == 3
        
        order.remove_item(valid_product.product_id, 3)
        assert valid_product.product_id not in order.items

    def test_remove_item_with_inventory(self, order, populated_inventory):
        inventory, products = populated_inventory
        initial_qty = products[0].quantity
        order.add_item(products[0], 2, inventory)
        order.remove_item(products[0].product_id, 1, inventory)
        assert products[0].quantity == initial_qty - 1

    def test_calculate_total(self, order, valid_product, digital_product):
        order.add_item(valid_product, 2)
        order.add_item(digital_product, 1)
        expected_total = (valid_product.price * 2) + digital_product.price
        assert order.calculate_total() == round(expected_total, 2)

    @pytest.mark.parametrize("status, should_raise", [
        ("pending", False),
        ("awaiting_payment", False),
        ("processing", False),
        ("shipped", False),
        ("delivered", False),
        ("cancelled", False),
        ("refunded", False),
        ("invalid_status", True)
    ])
    def test_update_status(self, order, status, should_raise):
        if should_raise:
            with pytest.raises(ValueError):
                order.update_status(status)
        else:
            order.update_status(status)
            assert order.status == status

    def test_status_transitions(self, order):
        order.update_status("cancelled")
        with pytest.raises(ValueError):
            order.update_status("processing")
            
        new_order = Order()
        new_order.update_status("delivered")
        with pytest.raises(ValueError):
            new_order.update_status("processing")

    def test_get_order_summary(self, order, valid_product, digital_product):
        order.add_item(valid_product, 2)
        order.add_item(digital_product, 1)
        summary = order.get_order_summary()
        assert summary["total_items"] == 3
        assert len(summary["items"]) == 2
        assert summary["total_cost"] == order.calculate_total()

    def test_finalize_order(self, order, valid_product):
        order.add_item(valid_product, 1)
        order.finalize_order()
        assert order._is_finalized
        assert order.status == "awaiting_payment"
        
        with pytest.raises(RuntimeError):
            order.add_item(valid_product, 1)