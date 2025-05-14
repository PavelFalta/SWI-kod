import sys
sys.path.append("..")
import uuid
import pytest
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# Product Tests
class TestProduct:
    def test_init_valid(self):
        # Arrange
        name = "Test Product"
        price = 10.99
        
        # Act
        product = Product(name, price)
        
        # Assert
        assert product.name == name
        assert product.price == price
        assert isinstance(product.product_id, str)
        assert product.quantity == 0

    def test_init_with_all_parameters(self):
        # Arrange
        name = "Test Product"
        price = 10.99
        product_id = "test123"
        quantity = 5
        
        # Act
        product = Product(name, price, product_id, quantity)
        
        # Assert
        assert product.name == name
        assert product.price == price
        assert product.product_id == product_id
        assert product.quantity == quantity

    def test_init_invalid_name(self):
        # Arrange/Act/Assert
        with pytest.raises(TypeError):
            Product("", 10.99)
        with pytest.raises(TypeError):
            Product(123, 10.99)

    def test_init_invalid_price(self):
        # Arrange/Act/Assert
        with pytest.raises(ValueError):
            Product("Test", 0)
        with pytest.raises(ValueError):
            Product("Test", -10)
        with pytest.raises(ValueError):
            Product("Test", "not a price")

    def test_init_invalid_product_id(self):
        # Arrange/Act/Assert
        with pytest.raises(TypeError):
            Product("Test", 10.99, 123)

    def test_init_invalid_quantity(self):
        # Arrange/Act/Assert
        with pytest.raises(ValueError):
            Product("Test", 10.99, "test123", -1)
        with pytest.raises(ValueError):
            Product("Test", 10.99, "test123", "not a quantity")

    def test_get_details(self):
        # Arrange
        product = Product("Test Product", 10.99, "test123", 5)
        
        # Act
        details = product.get_details()
        
        # Assert
        assert details == {
            "product_id": "test123",
            "name": "Test Product",
            "price": 10.99,
            "quantity": 5,
            "type": "GenericProduct"
        }

    def test_update_quantity_increase(self):
        # Arrange
        product = Product("Test", 10.99, quantity=5)
        
        # Act
        product.update_quantity(3)
        
        # Assert
        assert product.quantity == 8

    def test_update_quantity_decrease(self):
        # Arrange
        product = Product("Test", 10.99, quantity=5)
        
        # Act
        product.update_quantity(-3)
        
        # Assert
        assert product.quantity == 2

    def test_update_quantity_to_zero(self):
        # Arrange
        product = Product("Test", 10.99, quantity=5)
        
        # Act
        product.update_quantity(-5)
        
        # Assert
        assert product.quantity == 0

    def test_update_quantity_invalid_change(self):
        # Arrange
        product = Product("Test", 10.99, quantity=5)
        
        # Act/Assert
        with pytest.raises(TypeError):
            product.update_quantity("3")

    def test_update_quantity_below_zero(self):
        # Arrange
        product = Product("Test", 10.99, quantity=5)
        
        # Act/Assert
        with pytest.raises(ValueError):
            product.update_quantity(-6)

    def test_apply_discount(self):
        # Arrange
        product = Product("Test", 100.00)
        
        # Act
        product.apply_discount(20)
        
        # Assert
        assert product.price == 80.00

    def test_apply_discount_zero(self):
        # Arrange
        product = Product("Test", 100.00)
        
        # Act
        product.apply_discount(0)
        
        # Assert
        assert product.price == 100.00

    def test_apply_discount_full(self):
        # Arrange
        product = Product("Test", 100.00)
        
        # Act
        product.apply_discount(100)
        
        # Assert
        assert product.price == 0.00

    def test_apply_discount_invalid_percentage(self):
        # Arrange
        product = Product("Test", 100.00)
        
        # Act/Assert
        with pytest.raises(TypeError):
            product.apply_discount("20")
        with pytest.raises(ValueError):
            product.apply_discount(-10)
        with pytest.raises(ValueError):
            product.apply_discount(110)

# DigitalProduct Tests
class TestDigitalProduct:
    def test_init_valid(self):
        # Arrange
        name = "Digital Product"
        price = 19.99
        download_link = "https://example.com/download"
        file_size_mb = 50.5
        
        # Act
        product = DigitalProduct(name, price, download_link, file_size_mb)
        
        # Assert
        assert product.name == name
        assert product.price == price
        assert product.download_link == download_link
        assert product.file_size_mb == file_size_mb
        assert product.quantity == 1  # Default for digital products

    def test_init_invalid_download_link(self):
        # Arrange/Act/Assert
        with pytest.raises(TypeError):
            DigitalProduct("Test", 19.99, "invalid-url", 50)
        with pytest.raises(TypeError):
            DigitalProduct("Test", 19.99, 123, 50)

    def test_init_invalid_file_size(self):
        # Arrange/Act/Assert
        with pytest.raises(ValueError):
            DigitalProduct("Test", 19.99, "https://example.com", 0)
        with pytest.raises(ValueError):
            DigitalProduct("Test", 19.99, "https://example.com", -10)
        with pytest.raises(ValueError):
            DigitalProduct("Test", 19.99, "https://example.com", "not a size")

    def test_get_details(self):
        # Arrange
        product = DigitalProduct("Digital Product", 19.99, "https://example.com", 50.5, "digital123")
        
        # Act
        details = product.get_details()
        
        # Assert
        assert details["name"] == "Digital Product"
        assert details["price"] == 19.99
        assert details["product_id"] == "digital123"
        assert details["download_link"] == "https://example.com"
        assert details["file_size_mb"] == 50.5
        assert details["type"] == "DigitalProduct"

    def test_generate_new_download_link(self):
        # Arrange
        product = DigitalProduct("Test", 19.99, "https://example.com/old", 50)
        base_url = "https://example.com/downloads"
        
        # Act
        new_link = product.generate_new_download_link(base_url)
        
        # Assert
        assert new_link.startswith(f"{base_url}/{product.product_id}/download_")
        assert product.download_link == new_link

    def test_generate_new_download_link_invalid_base_url(self):
        # Arrange
        product = DigitalProduct("Test", 19.99, "https://example.com/old", 50)
        
        # Act/Assert
        with pytest.raises(TypeError):
            product.generate_new_download_link("")
        with pytest.raises(TypeError):
            product.generate_new_download_link(123)

# PhysicalProduct Tests
class TestPhysicalProduct:
    def test_init_valid(self):
        # Arrange
        name = "Physical Product"
        price = 29.99
        weight_kg = 1.5
        dimensions = (30, 20, 10)
        
        # Act
        product = PhysicalProduct(name, price, weight_kg, dimensions)
        
        # Assert
        assert product.name == name
        assert product.price == price
        assert product.weight_kg == weight_kg
        assert product.shipping_dimensions == dimensions
        assert product.quantity == 0

    def test_init_invalid_weight(self):
        # Arrange/Act/Assert
        with pytest.raises(ValueError):
            PhysicalProduct("Test", 29.99, 0, (10, 10, 10))
        with pytest.raises(ValueError):
            PhysicalProduct("Test", 29.99, -1, (10, 10, 10))
        with pytest.raises(ValueError):
            PhysicalProduct("Test", 29.99, "not a weight", (10, 10, 10))

    def test_init_invalid_dimensions(self):
        # Arrange/Act/Assert
        with pytest.raises(TypeError):
            PhysicalProduct("Test", 29.99, 1.5, [10, 10, 10])  # List instead of tuple
        with pytest.raises(TypeError):
            PhysicalProduct("Test", 29.99, 1.5, (10, 10))  # Not 3D
        with pytest.raises(TypeError):
            PhysicalProduct("Test", 29.99, 1.5, (0, 10, 10))  # Zero dimension
        with pytest.raises(TypeError):
            PhysicalProduct("Test", 29.99, 1.5, (10, -1, 10))  # Negative dimension

    def test_get_details(self):
        # Arrange
        product = PhysicalProduct("Physical Product", 29.99, 1.5, (30, 20, 10), "physical123")
        
        # Act
        details = product.get_details()
        
        # Assert
        assert details["name"] == "Physical Product"
        assert details["price"] == 29.99
        assert details["product_id"] == "physical123"
        assert details["weight_kg"] == 1.5
        assert details["shipping_dimensions_cm"] == (30, 20, 10)
        assert details["type"] == "PhysicalProduct"

    def test_calculate_shipping_cost_weight_based(self):
        # Arrange
        product = PhysicalProduct("Test", 29.99, 5.0, (10, 10, 10))
        rate_per_kg = 2.5
        
        # Act
        cost = product.calculate_shipping_cost(rate_per_kg)
        
        # Assert
        assert cost == 12.5  # 5.0 kg * 2.5

    def test_calculate_shipping_cost_volumetric(self):
        # Arrange
        product = PhysicalProduct("Test", 29.99, 1.0, (50, 40, 30))
        rate_per_kg = 2.5
        
        # Act
        # Volumetric weight: (50*40*30)/5000 = 12 kg, which is > 1.0 kg
        cost = product.calculate_shipping_cost(rate_per_kg)
        
        # Assert
        assert cost == 30.0  # 12 kg * 2.5

    def test_calculate_shipping_cost_invalid_rate(self):
        # Arrange
        product = PhysicalProduct("Test", 29.99, 1.5, (30, 20, 10))
        
        # Act/Assert
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(0)
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(-1)
        with pytest.raises(ValueError):
            product.calculate_shipping_cost("not a rate")

    def test_calculate_shipping_cost_invalid_volumetric_factor(self):
        # Arrange
        product = PhysicalProduct("Test", 29.99, 1.5, (30, 20, 10))
        
        # Act/Assert
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(2.5, 0)
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(2.5, -1)
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(2.5, "not a factor")

# Inventory Tests
class TestInventory:
    def test_init(self):
        # Arrange/Act
        inventory = Inventory()
        
        # Assert
        assert inventory.products == {}

    def test_add_product(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99)
        
        # Act
        inventory.add_product(product)
        
        # Assert
        assert product.product_id in inventory.products
        assert inventory.products[product.product_id] == product

    def test_add_product_with_initial_stock(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99)
        
        # Act
        inventory.add_product(product, 5)
        
        # Assert
        assert product.quantity == 5

    def test_add_product_duplicate(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99)
        inventory.add_product(product)
        
        # Act/Assert
        with pytest.raises(ValueError):
            inventory.add_product(product)

    def test_add_product_invalid(self):
        # Arrange
        inventory = Inventory()
        
        # Act/Assert
        with pytest.raises(TypeError):
            inventory.add_product("not a product")
        with pytest.raises(ValueError):
            inventory.add_product(Product("Test", 10.99), -1)

    def test_remove_product(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99)
        inventory.add_product(product)
        
        # Act
        removed = inventory.remove_product(product.product_id)
        
        # Assert
        assert removed == product
        assert product.product_id not in inventory.products

    def test_remove_product_not_found(self):
        # Arrange
        inventory = Inventory()
        
        # Act/Assert
        with pytest.raises(KeyError):
            inventory.remove_product("nonexistent")
        with pytest.raises(TypeError):
            inventory.remove_product(123)

    def test_get_product(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99)
        inventory.add_product(product)
        
        # Act
        retrieved = inventory.get_product(product.product_id)
        
        # Assert
        assert retrieved == product

    def test_get_product_not_found(self):
        # Arrange
        inventory = Inventory()
        
        # Act/Assert
        with pytest.raises(KeyError):
            inventory.get_product("nonexistent")
        with pytest.raises(TypeError):
            inventory.get_product(123)

    def test_update_stock(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99, quantity=5)
        inventory.add_product(product)
        
        # Act
        inventory.update_stock(product.product_id, 3)
        
        # Assert
        assert product.quantity == 8

    def test_update_stock_decrease(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99, quantity=5)
        inventory.add_product(product)
        
        # Act
        inventory.update_stock(product.product_id, -3)
        
        # Assert
        assert product.quantity == 2

    def test_update_stock_below_zero(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99, quantity=5)
        inventory.add_product(product)
        
        # Act/Assert
        with pytest.raises(ValueError):
            inventory.update_stock(product.product_id, -6)

    def test_get_total_inventory_value(self):
        # Arrange
        inventory = Inventory()
        inventory.add_product(Product("Product 1", 10.00, quantity=5))
        inventory.add_product(Product("Product 2", 20.00, quantity=3))
        
        # Act
        total_value = inventory.get_total_inventory_value()
        
        # Assert
        assert total_value == 110.00  # 5*10 + 3*20

    def test_find_products_by_name(self):
        # Arrange
        inventory = Inventory()
        p1 = Product("Apple iPhone", 999.99)
        p2 = Product("Samsung Galaxy", 899.99)
        p3 = Product("Apple Watch", 399.99)
        inventory.add_product(p1)
        inventory.add_product(p2)
        inventory.add_product(p3)
        
        # Act
        results = inventory.find_products_by_name("Apple")
        
        # Assert
        assert len(results) == 2
        assert p1 in results
        assert p3 in results

    def test_find_products_by_name_case_sensitive(self):
        # Arrange
        inventory = Inventory()
        p1 = Product("Apple iPhone", 999.99)
        p2 = Product("apple watch", 399.99)
        inventory.add_product(p1)
        inventory.add_product(p2)
        
        # Act
        results = inventory.find_products_by_name("Apple", case_sensitive=True)
        
        # Assert
        assert len(results) == 1
        assert p1 in results

    def test_get_products_in_price_range(self):
        # Arrange
        inventory = Inventory()
        p1 = Product("Product 1", 50.00)
        p2 = Product("Product 2", 100.00)
        p3 = Product("Product 3", 150.00)
        inventory.add_product(p1)
        inventory.add_product(p2)
        inventory.add_product(p3)
        
        # Act
        results = inventory.get_products_in_price_range(75, 125)
        
        # Assert
        assert len(results) == 1
        assert p2 in results

    def test_get_products_in_price_range_invalid(self):
        # Arrange
        inventory = Inventory()
        
        # Act/Assert
        with pytest.raises(ValueError):
            inventory.get_products_in_price_range(-10, 100)
        with pytest.raises(ValueError):
            inventory.get_products_in_price_range(100, 50)

    def test_get_stock_level(self):
        # Arrange
        inventory = Inventory()
        product = Product("Test Product", 10.99, quantity=5)
        inventory.add_product(product)
        
        # Act
        stock = inventory.get_stock_level(product.product_id)
        
        # Assert
        assert stock == 5

# Order Tests
class TestOrder:
    def test_init(self):
        # Arrange/Act
        order = Order()
        
        # Assert
        assert isinstance(order.order_id, str)
        assert order.customer_id is None
        assert order.items == {}
        assert order.status == "pending"
        assert order._is_finalized is False

    def test_init_with_ids(self):
        # Arrange
        order_id = "order123"
        customer_id = "customer456"
        
        # Act
        order = Order(order_id, customer_id)
        
        # Assert
        assert order.order_id == order_id
        assert order.customer_id == customer_id

    def test_add_item(self):
        # Arrange
        order = Order()
        product = Product("Test Product", 10.99)
        
        # Act
        order.add_item(product, 3)
        
        # Assert
        assert product.product_id in order.items
        assert order.items[product.product_id]["quantity"] == 3
        assert order.items[product.product_id]["price_at_purchase"] == 10.99

    def test_add_item_with_inventory(self):
        # Arrange
        order = Order()
        inventory = Inventory()
        product = Product("Test Product", 10.99, quantity=5)
        inventory.add_product(product)
        
        # Act
        order.add_item(product, 3, inventory)
        
        # Assert
        assert product.product_id in order.items
        assert order.items[product.product_id]["quantity"] == 3
        assert inventory.get_stock_level(product.product_id) == 2

    def test_add_item_insufficient_stock(self):
        # Arrange
        order = Order()
        inventory = Inventory()
        product = Product("Test Product", 10.99, quantity=2)
        inventory.add_product(product)
        
        # Act/Assert
        with pytest.raises(ValueError):
            order.add_item(product, 3, inventory)

    def test_add_item_to_finalized_order(self):
        # Arrange
        order = Order()
        product = Product("Test Product", 10.99)
        order._is_finalized = True
        
        # Act/Assert
        with pytest.raises(RuntimeError):
            order.add_item(product, 1)

    def test_remove_item(self):
        # Arrange
        order = Order()
        product = Product("Test Product", 10.99)
        order.add_item(product, 3)
        
        # Act
        order.remove_item(product.product_id, 2)
        
        # Assert
        assert order.items[product.product_id]["quantity"] == 1

    def test_remove_item_with_inventory(self):
        # Arrange
        order = Order()
        inventory = Inventory()
        product = Product("Test Product", 10.99, quantity=5)
        inventory.add_product(product)
        order.add_item(product, 3, inventory)
        
        # Act
        order.remove_item(product.product_id, 2, inventory)
        
        # Assert
        assert order.items[product.product_id]["quantity"] == 1
        assert inventory.get_stock_level(product.product_id) == 4  # 5-3+2

    def test_remove_item_entirely(self):
        # Arrange
        order = Order()
        product = Product("Test Product", 10.99)
        order.add_item(product, 3)
        
        # Act
        order.remove_item(product.product_id, 3)
        
        # Assert
        assert product.product_id not in order.items

    def test_remove_item_errors(self):
        # Arrange
        order = Order()
        product = Product("Test Product", 10.99)
        order.add_item(product, 3)
        
        # Act/Assert
        with pytest.raises(ValueError):
            order.remove_item(product.product_id, 4)  # More than in order
        with pytest.raises(ValueError):
            order.remove_item(product.product_id, 0)  # Zero quantity
        with pytest.raises(KeyError):
            order.remove_item("nonexistent", 1)  # Product not in order

    def test_remove_item_from_finalized_order(self):
        # Arrange
        order = Order()
        product = Product("Test Product", 10.99)
        order.add_item(product, 3)
        order._is_finalized = True
        order.status = "shipped"
        
        # Act/Assert
        with pytest.raises(RuntimeError):
            order.remove_item(product.product_id, 1)

    def test_calculate_total(self):
        # Arrange
        order = Order()
        p1 = Product("Product 1", 10.00)
        p2 = Product("Product 2", 20.00)
        order.add_item(p1, 2)
        order.add_item(p2, 1)
        
        # Act
        total = order.calculate_total()
        
        # Assert
        assert total == 40.00  # 2*10 + 1*20

    def test_update_status_valid(self):
        # Arrange
        order = Order()
        
        # Act
        order.update_status("processing")
        
        # Assert
        assert order.status == "processing"
        assert not order._is_finalized

    def test_update_status_finalized(self):
        # Arrange
        order = Order()
        
        # Act
        order.update_status("shipped")
        
        # Assert
        assert order.status == "shipped"
        assert order._is_finalized

    def test_update_status_invalid(self):
        # Arrange
        order = Order()
        
        # Act/Assert
        with pytest.raises(ValueError):
            order.update_status("invalid_status")
        with pytest.raises(TypeError):
            order.update_status(123)

    def test_update_status_from_delivered(self):
        # Arrange
        order = Order()
        order.status = "delivered"
        
        # Act/Assert
        with pytest.raises(ValueError):
            order.update_status("processing")
        
        # Valid change
        order.update_status("refunded")
        assert order.status == "refunded"

    def test_update_status_from_cancelled(self):
        # Arrange
        order = Order()
        order.status = "cancelled"
        
        # Act/Assert
        with pytest.raises(ValueError):
            order.update_status("processing")

    def test_get_order_summary(self):
        # Arrange
        order = Order("order123", "customer456")
        p1 = Product("Product 1", 10.00)
        p2 = Product("Product 2", 20.00)
        order.add_item(p1, 2)
        order.add_item(p2, 1)
        
        # Act
        summary = order.get_order_summary()
        
        # Assert
        assert summary["order_id"] == "order123"
        assert summary["customer_id"] == "customer456"
        assert summary["status"] == "pending"
        assert summary["total_items"] == 3
        assert summary["total_cost"] == 40.00
        assert len(summary["items"]) == 2

    def test_finalize_order(self):
        # Arrange
        order = Order()
        product = Product("Test Product", 10.99)
        order.add_item(product, 1)
        
        # Act
        order.finalize_order()
        
        # Assert
        assert order._is_finalized is True
        assert order.status == "awaiting_payment"

    def test_finalize_empty_order(self):
        # Arrange
        order = Order()
        
        # Act/Assert
        with pytest.raises(ValueError):
            order.finalize_order()