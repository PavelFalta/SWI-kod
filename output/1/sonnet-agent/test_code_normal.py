import pytest
import uuid
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

class TestProduct:
    def test_product_initialization(self):
        product = Product("Test Product", 10.50, "prod-1", 5)
        assert product.name == "Test Product"
        assert product.price == 10.50
        assert product.product_id == "prod-1"
        assert product.quantity == 5

    def test_product_id_generation(self):
        product = Product("Test Product", 10.50)
        assert isinstance(product.product_id, str)
        assert len(product.product_id) > 0

    def test_product_invalid_name(self):
        with pytest.raises(TypeError):
            Product("", 10.50)
        with pytest.raises(TypeError):
            Product(123, 10.50)

    def test_product_invalid_price(self):
        with pytest.raises(ValueError):
            Product("Test Product", 0)
        with pytest.raises(ValueError):
            Product("Test Product", -10)
        with pytest.raises(ValueError):
            Product("Test Product", "10")

    def test_product_invalid_quantity(self):
        with pytest.raises(ValueError):
            Product("Test Product", 10, quantity=-1)

    def test_get_details(self):
        product = Product("Test Product", 10.50, "prod-1", 5)
        details = product.get_details()
        assert details["product_id"] == "prod-1"
        assert details["name"] == "Test Product"
        assert details["price"] == 10.50
        assert details["quantity"] == 5
        assert details["type"] == "GenericProduct"

    def test_update_quantity(self):
        product = Product("Test Product", 10.50, quantity=5)
        product.update_quantity(3)
        assert product.quantity == 8
        product.update_quantity(-2)
        assert product.quantity == 6

    def test_update_quantity_errors(self):
        product = Product("Test Product", 10.50, quantity=5)
        with pytest.raises(TypeError):
            product.update_quantity("3")
        with pytest.raises(ValueError):
            product.update_quantity(-6)

    def test_apply_discount(self):
        product = Product("Test Product", 100, quantity=5)
        product.apply_discount(10)
        assert product.price == 90.0
        product.apply_discount(50)
        assert product.price == 45.0

    def test_apply_discount_errors(self):
        product = Product("Test Product", 100)
        with pytest.raises(TypeError):
            product.apply_discount("10")
        with pytest.raises(ValueError):
            product.apply_discount(-10)
        with pytest.raises(ValueError):
            product.apply_discount(110)


class TestDigitalProduct:
    def test_digital_product_initialization(self):
        dp = DigitalProduct(
            "Digital Product", 
            19.99, 
            "https://example.com/download", 
            25.5,
            "dig-1"
        )
        assert dp.name == "Digital Product"
        assert dp.price == 19.99
        assert dp.product_id == "dig-1"
        assert dp.quantity == 1  # Default for digital products
        assert dp.download_link == "https://example.com/download"
        assert dp.file_size_mb == 25.5

    def test_invalid_download_link(self):
        with pytest.raises(TypeError):
            DigitalProduct("Digital Product", 19.99, "example.com", 25.5)
        with pytest.raises(TypeError):
            DigitalProduct("Digital Product", 19.99, 123, 25.5)

    def test_invalid_file_size(self):
        with pytest.raises(ValueError):
            DigitalProduct("Digital Product", 19.99, "https://example.com", 0)
        with pytest.raises(ValueError):
            DigitalProduct("Digital Product", 19.99, "https://example.com", -5)

    def test_get_details(self):
        dp = DigitalProduct(
            "Digital Product", 
            19.99, 
            "https://example.com/download", 
            25.5,
            "dig-1"
        )
        details = dp.get_details()
        assert details["product_id"] == "dig-1"
        assert details["name"] == "Digital Product"
        assert details["price"] == 19.99
        assert details["download_link"] == "https://example.com/download"
        assert details["file_size_mb"] == 25.5
        assert details["type"] == "DigitalProduct"

    def test_generate_new_download_link(self):
        dp = DigitalProduct(
            "Digital Product", 
            19.99, 
            "https://example.com/download", 
            25.5,
            "dig-1"
        )
        new_link = dp.generate_new_download_link("https://newexample.com")
        assert new_link.startswith("https://newexample.com/dig-1/download_")
        assert dp.download_link == new_link

    def test_generate_new_download_link_error(self):
        dp = DigitalProduct(
            "Digital Product", 
            19.99, 
            "https://example.com/download", 
            25.5
        )
        with pytest.raises(TypeError):
            dp.generate_new_download_link("")
        with pytest.raises(TypeError):
            dp.generate_new_download_link(123)


class TestPhysicalProduct:
    def test_physical_product_initialization(self):
        pp = PhysicalProduct(
            "Physical Product", 
            29.99, 
            2.5, 
            (30, 20, 10),
            "phys-1",
            15
        )
        assert pp.name == "Physical Product"
        assert pp.price == 29.99
        assert pp.product_id == "phys-1"
        assert pp.quantity == 15
        assert pp.weight_kg == 2.5
        assert pp.shipping_dimensions == (30, 20, 10)

    def test_invalid_weight(self):
        with pytest.raises(ValueError):
            PhysicalProduct("Physical Product", 29.99, 0, (30, 20, 10))
        with pytest.raises(ValueError):
            PhysicalProduct("Physical Product", 29.99, -2, (30, 20, 10))

    def test_invalid_dimensions(self):
        with pytest.raises(TypeError):
            PhysicalProduct("Physical Product", 29.99, 2.5, [30, 20, 10])
        with pytest.raises(TypeError):
            PhysicalProduct("Physical Product", 29.99, 2.5, (30, 20))
        with pytest.raises(TypeError):
            PhysicalProduct("Physical Product", 29.99, 2.5, (30, 20, -10))

    def test_get_details(self):
        pp = PhysicalProduct(
            "Physical Product", 
            29.99, 
            2.5, 
            (30, 20, 10),
            "phys-1"
        )
        details = pp.get_details()
        assert details["product_id"] == "phys-1"
        assert details["name"] == "Physical Product"
        assert details["price"] == 29.99
        assert details["weight_kg"] == 2.5
        assert details["shipping_dimensions_cm"] == (30, 20, 10)
        assert details["type"] == "PhysicalProduct"

    def test_calculate_shipping_cost(self):
        pp = PhysicalProduct(
            "Physical Product", 
            29.99, 
            2.5, 
            (30, 20, 10)
        )
        # Weight-based calculation: 2.5 kg * 5 = 12.5
        cost = pp.calculate_shipping_cost(5)
        assert cost == 12.5

        # Test volumetric calculation
        # (30 * 20 * 10) / 5000 = 1.2 kg, still less than actual weight
        cost = pp.calculate_shipping_cost(5, 5000)
        assert cost == 12.5

        # Volumetric weight is higher
        pp = PhysicalProduct("Large Light Item", 29.99, 0.5, (50, 40, 30))
        # (50 * 40 * 30) / 5000 = 12 kg > 0.5 kg
        cost = pp.calculate_shipping_cost(5, 5000)
        assert cost == 60.0

    def test_calculate_shipping_cost_errors(self):
        pp = PhysicalProduct("Physical Product", 29.99, 2.5, (30, 20, 10))
        with pytest.raises(ValueError):
            pp.calculate_shipping_cost(0)
        with pytest.raises(ValueError):
            pp.calculate_shipping_cost(-5)
        with pytest.raises(ValueError):
            pp.calculate_shipping_cost(5, 0)


class TestInventory:
    @pytest.fixture
    def sample_inventory(self):
        inventory = Inventory()
        product1 = Product("Test Product 1", 10.50, "prod-1", 10)
        product2 = PhysicalProduct("Test Product 2", 20.00, 1.5, (20, 15, 10), "prod-2", 5)
        product3 = DigitalProduct("Test Product 3", 15.99, "https://example.com/download", 50, "prod-3")
        
        inventory.add_product(product1)
        inventory.add_product(product2)
        inventory.add_product(product3)
        
        return inventory, [product1, product2, product3]

    def test_add_product(self, sample_inventory):
        inventory, products = sample_inventory
        assert len(inventory.products) == 3
        assert "prod-1" in inventory.products
        assert "prod-2" in inventory.products
        assert "prod-3" in inventory.products

    def test_add_product_with_initial_stock(self):
        inventory = Inventory()
        product = Product("Test Product", 10.50, "prod-1")
        inventory.add_product(product, 20)
        assert product.quantity == 20

    def test_add_existing_product(self, sample_inventory):
        inventory, products = sample_inventory
        duplicate_product = Product("Duplicate", 10.50, "prod-1")
        with pytest.raises(ValueError):
            inventory.add_product(duplicate_product)

    def test_add_invalid_product(self):
        inventory = Inventory()
        with pytest.raises(TypeError):
            inventory.add_product("Not a product")

    def test_remove_product(self, sample_inventory):
        inventory, products = sample_inventory
        removed = inventory.remove_product("prod-1")
        assert removed is products[0]
        assert "prod-1" not in inventory.products
        assert len(inventory.products) == 2

    def test_remove_nonexistent_product(self, sample_inventory):
        inventory, _ = sample_inventory
        with pytest.raises(KeyError):
            inventory.remove_product("nonexistent-id")

    def test_get_product(self, sample_inventory):
        inventory, products = sample_inventory
        product = inventory.get_product("prod-2")
        assert product is products[1]

    def test_get_nonexistent_product(self, sample_inventory):
        inventory, _ = sample_inventory
        with pytest.raises(KeyError):
            inventory.get_product("nonexistent-id")

    def test_update_stock(self, sample_inventory):
        inventory, products = sample_inventory
        inventory.update_stock("prod-1", 5)
        assert products[0].quantity == 15
        inventory.update_stock("prod-1", -3)
        assert products[0].quantity == 12

    def test_update_stock_below_zero(self, sample_inventory):
        inventory, _ = sample_inventory
        with pytest.raises(ValueError):
            inventory.update_stock("prod-1", -20)

    def test_get_total_inventory_value(self, sample_inventory):
        inventory, products = sample_inventory
        # prod-1: 10.50 * 10 = 105.00
        # prod-2: 20.00 * 5 = 100.00
        # prod-3: 15.99 * 1 = 15.99
        expected_value = 105.00 + 100.00 + 15.99
        assert inventory.get_total_inventory_value() == round(expected_value, 2)

    def test_find_products_by_name(self, sample_inventory):
        inventory, products = sample_inventory
        results = inventory.find_products_by_name("Test")
        assert len(results) == 3
        
        results = inventory.find_products_by_name("Product 2")
        assert len(results) == 1
        assert results[0] is products[1]

    def test_find_products_case_sensitive(self, sample_inventory):
        inventory, _ = sample_inventory
        results = inventory.find_products_by_name("test", case_sensitive=False)
        assert len(results) == 3
        
        results = inventory.find_products_by_name("test", case_sensitive=True)
        assert len(results) == 0

    def test_get_products_in_price_range(self, sample_inventory):
        inventory, products = sample_inventory
        results = inventory.get_products_in_price_range(15, 25)
        assert len(results) == 2
        assert products[1] in results
        assert products[2] in results

    def test_get_stock_level(self, sample_inventory):
        inventory, products = sample_inventory
        level = inventory.get_stock_level("prod-1")
        assert level == 10


class TestOrder:
    @pytest.fixture
    def sample_inventory(self):
        inventory = Inventory()
        product1 = Product("Test Product 1", 10.50, "prod-1", 10)
        product2 = PhysicalProduct("Test Product 2", 20.00, 1.5, (20, 15, 10), "prod-2", 5)
        product3 = DigitalProduct("Test Product 3", 15.99, "https://example.com/download", 50, "prod-3")
        
        inventory.add_product(product1)
        inventory.add_product(product2)
        inventory.add_product(product3)
        
        return inventory, [product1, product2, product3]

    def test_order_initialization(self):
        order = Order("order-1", "cust-1")
        assert order.order_id == "order-1"
        assert order.customer_id == "cust-1"
        assert order.items == {}
        assert order.status == "pending"
        assert order._is_finalized is False

    def test_order_id_generation(self):
        order = Order()
        assert isinstance(order.order_id, str)
        assert len(order.order_id) > 0

    def test_add_item(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        order.add_item(products[0], 2)
        assert "prod-1" in order.items
        assert order.items["prod-1"]["quantity"] == 2
        assert order.items["prod-1"]["price_at_purchase"] == 10.50

    def test_add_item_with_inventory(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        initial_quantity = products[0].quantity
        order.add_item(products[0], 2, inventory)
        assert "prod-1" in order.items
        assert order.items["prod-1"]["quantity"] == 2
        assert products[0].quantity == initial_quantity - 2

    def test_add_item_insufficient_stock(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        with pytest.raises(ValueError):
            order.add_item(products[0], 20, inventory)

    def test_add_item_to_finalized_order(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        order.add_item(products[0], 2)
        order.finalize_order()
        
        with pytest.raises(RuntimeError):
            order.add_item(products[1], 1)

    def test_remove_item(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        order.add_item(products[0], 5)
        order.remove_item("prod-1", 2)
        assert order.items["prod-1"]["quantity"] == 3
        
        order.remove_item("prod-1", 3)
        assert "prod-1" not in order.items

    def test_remove_item_with_inventory(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        initial_quantity = products[0].quantity
        order.add_item(products[0], 5, inventory)
        order.remove_item("prod-1", 2, inventory)
        assert products[0].quantity == initial_quantity - 3

    def test_remove_nonexistent_item(self):
        order = Order("order-1", "cust-1")
        with pytest.raises(KeyError):
            order.remove_item("nonexistent-id", 1)

    def test_remove_too_many_items(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        order.add_item(products[0], 2)
        with pytest.raises(ValueError):
            order.remove_item("prod-1", 3)

    def test_calculate_total(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        order.add_item(products[0], 2)  # 2 * 10.50 = 21.00
        order.add_item(products[1], 1)  # 1 * 20.00 = 20.00
        
        assert order.calculate_total() == 41.00

    def test_update_status(self):
        order = Order("order-1", "cust-1")
        
        order.update_status("awaiting_payment")
        assert order.status == "awaiting_payment"
        assert not order._is_finalized
        
        order.update_status("shipped")
        assert order.status == "shipped"
        assert order._is_finalized

    def test_update_status_invalid(self):
        order = Order("order-1", "cust-1")
        
        with pytest.raises(ValueError):
            order.update_status("invalid_status")

    def test_update_status_restrictions(self):
        order = Order("order-1", "cust-1")
        
        order.update_status("delivered")
        with pytest.raises(ValueError):
            order.update_status("processing")
            
        order = Order("order-1", "cust-1")
        order.update_status("cancelled")
        with pytest.raises(ValueError):
            order.update_status("delivered")

    def test_get_order_summary(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        order.add_item(products[0], 2)
        order.add_item(products[1], 1)
        
        summary = order.get_order_summary()
        assert summary["order_id"] == "order-1"
        assert summary["customer_id"] == "cust-1"
        assert summary["status"] == "pending"
        assert summary["total_items"] == 3
        assert summary["total_cost"] == 41.00
        assert len(summary["items"]) == 2

    def test_finalize_order(self, sample_inventory):
        inventory, products = sample_inventory
        order = Order("order-1", "cust-1")
        
        order.add_item(products[0], 2)
        order.finalize_order()
        
        assert order._is_finalized
        assert order.status == "awaiting_payment"

    def test_finalize_empty_order(self):
        order = Order("order-1", "cust-1")
        
        with pytest.raises(ValueError):
            order.finalize_order() 