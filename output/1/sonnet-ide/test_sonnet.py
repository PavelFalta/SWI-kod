import pytest
import uuid
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# Product Tests
class TestProduct:
    def test_valid_initialization(self):
        product = Product("Test Product", 19.99, quantity=5)
        assert product.name == "Test Product"
        assert product.price == 19.99
        assert product.quantity == 5
        assert isinstance(product.product_id, str)

    def test_invalid_name(self):
        with pytest.raises(TypeError):
            Product("", 19.99)
        with pytest.raises(TypeError):
            Product(None, 19.99)

    def test_invalid_price(self):
        with pytest.raises(ValueError):
            Product("Test", -10)
        with pytest.raises(ValueError):
            Product("Test", 0)

    def test_invalid_quantity(self):
        with pytest.raises(ValueError):
            Product("Test", 19.99, quantity=-1)

    def test_get_details(self):
        product = Product("Test Product", 19.99, "test123", 5)
        details = product.get_details()
        assert details["name"] == "Test Product"
        assert details["price"] == 19.99
        assert details["product_id"] == "test123"
        assert details["quantity"] == 5
        assert details["type"] == "GenericProduct"

    def test_update_quantity(self):
        product = Product("Test", 19.99, quantity=5)
        product.update_quantity(3)
        assert product.quantity == 8
        product.update_quantity(-3)
        assert product.quantity == 5
        
        with pytest.raises(ValueError):
            product.update_quantity(-10)
        
        with pytest.raises(TypeError):
            product.update_quantity("3")

    def test_apply_discount(self):
        product = Product("Test", 100.00)
        product.apply_discount(20)
        assert product.price == 80.00
        
        with pytest.raises(ValueError):
            product.apply_discount(101)
        
        with pytest.raises(TypeError):
            product.apply_discount("20")

# DigitalProduct Tests
class TestDigitalProduct:
    def test_valid_initialization(self):
        product = DigitalProduct("Digital Test", 29.99, "https://example.com/download", 150.5)
        assert product.name == "Digital Test"
        assert product.price == 29.99
        assert product.download_link == "https://example.com/download"
        assert product.file_size_mb == 150.5
        assert product.quantity == 1  # Default for digital products

    def test_invalid_download_link(self):
        with pytest.raises(TypeError):
            DigitalProduct("Digital Test", 29.99, "invalid-link", 150.5)

    def test_invalid_file_size(self):
        with pytest.raises(ValueError):
            DigitalProduct("Digital Test", 29.99, "https://example.com", -10)

    def test_get_details(self):
        product = DigitalProduct("Digital Test", 29.99, "https://example.com/download", 150.5)
        details = product.get_details()
        assert details["name"] == "Digital Test"
        assert details["price"] == 29.99
        assert details["download_link"] == "https://example.com/download"
        assert details["file_size_mb"] == 150.5
        assert details["type"] == "DigitalProduct"

    def test_generate_new_download_link(self):
        product = DigitalProduct("Digital Test", 29.99, "https://example.com/download", 150.5)
        new_link = product.generate_new_download_link("https://newdomain.com")
        assert new_link.startswith("https://newdomain.com/")
        assert product.product_id in new_link

# PhysicalProduct Tests
class TestPhysicalProduct:
    def test_valid_initialization(self):
        product = PhysicalProduct("Physical Test", 49.99, 2.5, (30, 20, 10), quantity=2)
        assert product.name == "Physical Test"
        assert product.price == 49.99
        assert product.weight_kg == 2.5
        assert product.shipping_dimensions == (30, 20, 10)
        assert product.quantity == 2

    def test_invalid_weight(self):
        with pytest.raises(ValueError):
            PhysicalProduct("Physical Test", 49.99, -1, (30, 20, 10))

    def test_invalid_dimensions(self):
        with pytest.raises(TypeError):
            PhysicalProduct("Physical Test", 49.99, 2.5, (30, -20, 10))
        with pytest.raises(TypeError):
            PhysicalProduct("Physical Test", 49.99, 2.5, [30, 20, 10])
        with pytest.raises(TypeError):
            PhysicalProduct("Physical Test", 49.99, 2.5, (30, 20))

    def test_get_details(self):
        product = PhysicalProduct("Physical Test", 49.99, 2.5, (30, 20, 10))
        details = product.get_details()
        assert details["name"] == "Physical Test"
        assert details["price"] == 49.99
        assert details["weight_kg"] == 2.5
        assert details["shipping_dimensions_cm"] == (30, 20, 10)
        assert details["type"] == "PhysicalProduct"

    def test_calculate_shipping_cost(self):
        product = PhysicalProduct("Physical Test", 49.99, 2.5, (30, 20, 10))
        cost = product.calculate_shipping_cost(5.0)
        assert isinstance(cost, float)
        assert cost > 0
        
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(-1)

# Inventory Tests
class TestInventory:
    @pytest.fixture
    def sample_inventory(self):
        inventory = Inventory()
        product1 = Product("Test Product 1", 19.99, quantity=5)
        product2 = DigitalProduct("Digital Test", 29.99, "https://example.com/download", 150.5)
        product3 = PhysicalProduct("Physical Test", 49.99, 2.5, (30, 20, 10), quantity=8)
        
        inventory.add_product(product1)
        inventory.add_product(product2)
        inventory.add_product(product3)
        
        return inventory, product1, product2, product3

    def test_add_product(self, sample_inventory):
        inventory, p1, p2, p3 = sample_inventory
        assert len(inventory.products) == 3
        assert p1.product_id in inventory.products
        
        with pytest.raises(TypeError):
            inventory.add_product("not a product")
            
        with pytest.raises(ValueError):
            inventory.add_product(p1)  # Adding existing product

    def test_remove_product(self, sample_inventory):
        inventory, p1, p2, p3 = sample_inventory
        removed = inventory.remove_product(p1.product_id)
        assert removed == p1
        assert len(inventory.products) == 2
        assert p1.product_id not in inventory.products
        
        with pytest.raises(KeyError):
            inventory.remove_product("non-existent-id")

    def test_get_product(self, sample_inventory):
        inventory, p1, p2, p3 = sample_inventory
        retrieved = inventory.get_product(p1.product_id)
        assert retrieved == p1
        
        with pytest.raises(KeyError):
            inventory.get_product("non-existent-id")

    def test_update_stock(self, sample_inventory):
        inventory, p1, p2, p3 = sample_inventory
        initial_quantity = p1.quantity
        inventory.update_stock(p1.product_id, 5)
        assert p1.quantity == initial_quantity + 5
        
        with pytest.raises(ValueError):
            inventory.update_stock(p1.product_id, -100)  # More than available

    def test_get_total_inventory_value(self, sample_inventory):
        inventory, p1, p2, p3 = sample_inventory
        expected_value = (p1.price * p1.quantity) + (p2.price * p2.quantity) + (p3.price * p3.quantity)
        assert inventory.get_total_inventory_value() == round(expected_value, 2)

    def test_find_products_by_name(self, sample_inventory):
        inventory, p1, p2, p3 = sample_inventory
        results = inventory.find_products_by_name("Test")
        assert len(results) == 3
        
        results = inventory.find_products_by_name("Digital")
        assert len(results) == 1
        assert results[0] == p2

    def test_get_products_in_price_range(self, sample_inventory):
        inventory, p1, p2, p3 = sample_inventory
        results = inventory.get_products_in_price_range(20, 40)
        assert len(results) == 1
        assert results[0] == p2
        
        results = inventory.get_products_in_price_range(10, 100)
        assert len(results) == 3

    def test_get_stock_level(self, sample_inventory):
        inventory, p1, p2, p3 = sample_inventory
        assert inventory.get_stock_level(p1.product_id) == p1.quantity
        
        with pytest.raises(KeyError):
            inventory.get_stock_level("non-existent-id")

# Order Tests
class TestOrder:
    @pytest.fixture
    def sample_order_with_inventory(self):
        inventory = Inventory()
        product1 = Product("Test Product 1", 19.99, quantity=5)
        product2 = DigitalProduct("Digital Test", 29.99, "https://example.com/download", 150.5)
        product3 = PhysicalProduct("Physical Test", 49.99, 2.5, (30, 20, 10), quantity=8)
        
        inventory.add_product(product1)
        inventory.add_product(product2)
        inventory.add_product(product3)
        
        order = Order("test_order", "customer123")
        
        return order, inventory, product1, product2, product3

    def test_initialization(self):
        order = Order()
        assert order.status == "pending"
        assert not order._is_finalized
        assert isinstance(order.order_id, str)
        
        order = Order("custom_id", "customer123")
        assert order.order_id == "custom_id"
        assert order.customer_id == "customer123"

    def test_add_item(self, sample_order_with_inventory):
        order, inventory, p1, p2, p3 = sample_order_with_inventory
        order.add_item(p1, 2, inventory)
        assert p1.product_id in order.items
        assert order.items[p1.product_id]["quantity"] == 2
        assert inventory.get_stock_level(p1.product_id) == 3  # Initial 5 - 2
        
        order.add_item(p1, 1, inventory)  # Add more of same product
        assert order.items[p1.product_id]["quantity"] == 3
        assert inventory.get_stock_level(p1.product_id) == 2  # 3 - 1
        
        with pytest.raises(ValueError):
            order.add_item(p1, 10, inventory)  # Not enough stock

    def test_remove_item(self, sample_order_with_inventory):
        order, inventory, p1, p2, p3 = sample_order_with_inventory
        order.add_item(p1, 2, inventory)
        initial_inventory = inventory.get_stock_level(p1.product_id)
        
        order.remove_item(p1.product_id, 1, inventory)
        assert order.items[p1.product_id]["quantity"] == 1
        assert inventory.get_stock_level(p1.product_id) == initial_inventory + 1
        
        order.remove_item(p1.product_id, 1, inventory)  # Remove last item
        assert p1.product_id not in order.items
        
        with pytest.raises(KeyError):
            order.remove_item("non-existent-id", 1)

    def test_calculate_total(self, sample_order_with_inventory):
        order, inventory, p1, p2, p3 = sample_order_with_inventory
        order.add_item(p1, 2)
        order.add_item(p2, 1)
        expected_total = (p1.price * 2) + (p2.price * 1)
        assert order.calculate_total() == round(expected_total, 2)

    def test_update_status(self):
        order = Order()
        order.update_status("processing")
        assert order.status == "processing"
        
        with pytest.raises(ValueError):
            order.update_status("invalid_status")
        
        order.update_status("delivered")
        assert order.status == "delivered"
        assert order._is_finalized
        
        with pytest.raises(ValueError):
            order.update_status("processing")  # Can't go back from delivered

    def test_get_order_summary(self, sample_order_with_inventory):
        order, inventory, p1, p2, p3 = sample_order_with_inventory
        order.add_item(p1, 2)
        order.add_item(p2, 1)
        
        summary = order.get_order_summary()
        assert summary["order_id"] == order.order_id
        assert summary["total_items"] == 3
        assert summary["total_cost"] == order.calculate_total()
        assert len(summary["items"]) == 2

    def test_finalize_order(self, sample_order_with_inventory):
        order, inventory, p1, p2, p3 = sample_order_with_inventory
        
        with pytest.raises(ValueError):
            order.finalize_order()  # Empty order
            
        order.add_item(p1, 1)
        order.finalize_order()
        assert order._is_finalized
        assert order.status == "awaiting_payment"
        
        with pytest.raises(RuntimeError):
            order.add_item(p2, 1)  # Can't add to finalized order