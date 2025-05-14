import sys
sys.path.append("..")
import pytest
import uuid
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# Fixtures
@pytest.fixture
def product_data():
    return {
        "name": "Test Product",
        "price": 19.99,
        "product_id": "test-123",
        "quantity": 10
    }

@pytest.fixture
def sample_product(product_data):
    return Product(**product_data)

@pytest.fixture
def digital_product_data():
    return {
        "name": "Test App",
        "price": 29.99,
        "download_link": "https://example.com/download",
        "file_size_mb": 100.0,
        "product_id": "digital-123",
        "quantity": 1
    }

@pytest.fixture
def sample_digital_product(digital_product_data):
    return DigitalProduct(**digital_product_data)

@pytest.fixture
def physical_product_data():
    return {
        "name": "Test Book",
        "price": 14.99,
        "weight_kg": 0.5,
        "shipping_dimensions": (20, 15, 3),
        "product_id": "physical-123",
        "quantity": 5
    }

@pytest.fixture
def sample_physical_product(physical_product_data):
    return PhysicalProduct(**physical_product_data)

@pytest.fixture
def sample_inventory():
    return Inventory()

@pytest.fixture
def populated_inventory(sample_product, sample_digital_product, sample_physical_product):
    inventory = Inventory()
    inventory.add_product(sample_product)
    inventory.add_product(sample_digital_product)
    inventory.add_product(sample_physical_product)
    return inventory

@pytest.fixture
def sample_order():
    return Order(order_id="order-123", customer_id="customer-123")


class TestProduct:
    def test_product_creation_ok(self, product_data):
        # Act
        product = Product(**product_data)
        
        # Assert
        assert product.name == product_data["name"]
        assert product.price == product_data["price"]
        assert product.product_id == product_data["product_id"]
        assert product.quantity == product_data["quantity"]
    
    def test_product_creation_auto_id(self):
        # Arrange
        data = {"name": "Auto ID Product", "price": 29.99}
        
        # Act
        product = Product(**data)
        
        # Assert
        assert isinstance(product.product_id, str)
        assert len(product.product_id) > 0
    
    @pytest.mark.parametrize("name", ["", None, 123])
    def test_product_invalid_name(self, name):
        # Act & Assert
        with pytest.raises(TypeError, match="Product name must be a non-empty string."):
            Product(name=name, price=10.0)
    
    @pytest.mark.parametrize("price", [0, -10, "ten"])
    def test_product_invalid_price(self, price):
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            Product(name="Test Product", price=price)
    
    def test_get_details(self, sample_product):
        # Act
        details = sample_product.get_details()
        
        # Assert
        assert details["product_id"] == sample_product.product_id
        assert details["name"] == sample_product.name
        assert details["price"] == sample_product.price
        assert details["quantity"] == sample_product.quantity
        assert details["type"] == "GenericProduct"
    
    def test_update_quantity(self, sample_product):
        # Arrange
        original_quantity = sample_product.quantity
        change = 5
        
        # Act
        sample_product.update_quantity(change)
        
        # Assert
        assert sample_product.quantity == original_quantity + change
    
    def test_update_quantity_negative(self, sample_product):
        # Arrange
        original_quantity = sample_product.quantity
        
        # Act
        sample_product.update_quantity(-5)
        
        # Assert
        assert sample_product.quantity == original_quantity - 5
    
    def test_update_quantity_below_zero(self, sample_product):
        # Act & Assert
        with pytest.raises(ValueError, match="Quantity cannot be reduced below zero."):
            sample_product.update_quantity(-100)
    
    def test_apply_discount(self, sample_product):
        # Arrange
        original_price = sample_product.price
        discount = 20
        
        # Act
        sample_product.apply_discount(discount)
        
        # Assert
        expected_price = round(original_price * 0.8, 2)
        assert sample_product.price == expected_price
    
    @pytest.mark.parametrize("discount", [-10, 101, "discount"])
    def test_apply_invalid_discount(self, discount, sample_product):
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            sample_product.apply_discount(discount)
    
    def test_product_repr(self, sample_product):
        # Act
        representation = repr(sample_product)
        
        # Assert
        expected = f"Product(name='{sample_product.name}', price={sample_product.price}, id='{sample_product.product_id}', quantity={sample_product.quantity})"
        assert representation == expected


class TestPhysicalProduct:
    def test_physical_product_creation_ok(self, physical_product_data):
        # Act
        product = PhysicalProduct(**physical_product_data)
        
        # Assert
        assert product.name == physical_product_data["name"]
        assert product.price == physical_product_data["price"]
        assert product.weight_kg == physical_product_data["weight_kg"]
        assert product.shipping_dimensions == physical_product_data["shipping_dimensions"]
        assert product.product_id == physical_product_data["product_id"]
        assert product.quantity == physical_product_data["quantity"]
    
    @pytest.mark.parametrize("weight", [0, -1, "heavy"])
    def test_physical_product_invalid_weight(self, weight, physical_product_data):
        # Arrange
        data = physical_product_data.copy()
        data["weight_kg"] = weight
        
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            PhysicalProduct(**data)
    
    @pytest.mark.parametrize("dimensions", [(1, -1, 3), (1, 2), "small", (0, 1, 2)])
    def test_physical_product_invalid_dimensions(self, dimensions, physical_product_data):
        # Arrange
        data = physical_product_data.copy()
        data["shipping_dimensions"] = dimensions
        
        # Act & Assert
        with pytest.raises(TypeError):
            PhysicalProduct(**data)
    
    def test_physical_product_get_details(self, sample_physical_product):
        # Act
        details = sample_physical_product.get_details()
        
        # Assert
        assert details["product_id"] == sample_physical_product.product_id
        assert details["name"] == sample_physical_product.name
        assert details["weight_kg"] == sample_physical_product.weight_kg
        assert details["shipping_dimensions_cm"] == sample_physical_product.shipping_dimensions
        assert details["type"] == "PhysicalProduct"
    
    def test_calculate_shipping_cost(self, sample_physical_product):
        # Arrange
        rate_per_kg = 10.0
        
        # Act
        cost = sample_physical_product.calculate_shipping_cost(rate_per_kg)
        
        # Assert
        dimensions = sample_physical_product.shipping_dimensions
        volumetric_weight = (dimensions[0] * dimensions[1] * dimensions[2]) / 5000
        chargeable_weight = max(sample_physical_product.weight_kg, volumetric_weight)
        expected_cost = round(chargeable_weight * rate_per_kg, 2)
        assert cost == expected_cost
    
    @pytest.mark.parametrize("rate", [0, -5, "expensive"])
    def test_calculate_shipping_cost_invalid_rate(self, rate, sample_physical_product):
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            sample_physical_product.calculate_shipping_cost(rate)
    
    def test_physical_product_repr(self, sample_physical_product):
        # Act
        representation = repr(sample_physical_product)
        
        # Assert
        expected = f"PhysicalProduct(name='{sample_physical_product.name}', price={sample_physical_product.price}, id='{sample_physical_product.product_id}', weight={sample_physical_product.weight_kg}kg)"
        assert representation == expected


class TestInventory:
    def test_inventory_creation(self):
        # Act
        inventory = Inventory()
        
        # Assert
        assert inventory.products == {}
    
    def test_add_product(self, sample_inventory, sample_product):
        # Act
        sample_inventory.add_product(sample_product)
        
        # Assert
        assert sample_product.product_id in sample_inventory.products
        assert sample_inventory.products[sample_product.product_id] == sample_product
    
    def test_add_product_with_initial_stock(self, sample_inventory, sample_product):
        # Arrange
        initial_stock = 20
        
        # Act
        sample_inventory.add_product(sample_product, initial_stock)
        
        # Assert
        assert sample_inventory.products[sample_product.product_id].quantity == initial_stock
    
    def test_add_product_duplicate(self, sample_inventory, sample_product):
        # Arrange
        sample_inventory.add_product(sample_product)
        
        # Act & Assert
        with pytest.raises(ValueError):
            sample_inventory.add_product(sample_product)
    
    def test_remove_product(self, populated_inventory, sample_product):
        # Act
        removed = populated_inventory.remove_product(sample_product.product_id)
        
        # Assert
        assert removed == sample_product
        assert sample_product.product_id not in populated_inventory.products
    
    def test_remove_product_not_found(self, sample_inventory):
        # Act & Assert
        with pytest.raises(KeyError):
            sample_inventory.remove_product("nonexistent-id")
    
    def test_get_product(self, populated_inventory, sample_product):
        # Act
        product = populated_inventory.get_product(sample_product.product_id)
        
        # Assert
        assert product == sample_product
    
    def test_update_stock(self, populated_inventory, sample_product):
        # Arrange
        original_quantity = sample_product.quantity
        change = 5
        
        # Act
        populated_inventory.update_stock(sample_product.product_id, change)
        
        # Assert
        assert populated_inventory.get_product(sample_product.product_id).quantity == original_quantity + change
    
    def test_update_stock_below_zero(self, populated_inventory, sample_product):
        # Act & Assert
        with pytest.raises(ValueError):
            populated_inventory.update_stock(sample_product.product_id, -100)
    
    def test_get_total_inventory_value(self, populated_inventory):
        # Act
        total_value = populated_inventory.get_total_inventory_value()
        
        # Assert
        expected_value = sum(p.price * p.quantity for p in populated_inventory.products.values())
        assert total_value == round(expected_value, 2)
    
    def test_find_products_by_name(self, populated_inventory):
        # Act
        results = populated_inventory.find_products_by_name("Test")
        
        # Assert
        assert len(results) == 3  # All fixture products have "Test" in their name
    
    def test_find_products_by_name_case_sensitive(self, populated_inventory):
        # Act
        results = populated_inventory.find_products_by_name("test", case_sensitive=True)
        
        # Assert
        assert len(results) == 0
    
    def test_get_products_in_price_range(self, populated_inventory):
        # Act
        results = populated_inventory.get_products_in_price_range(15.0, 30.0)
        
        # Assert
        assert all(15.0 <= p.price <= 30.0 for p in results)
    
    def test_get_stock_level(self, populated_inventory, sample_product):
        # Act
        stock_level = populated_inventory.get_stock_level(sample_product.product_id)
        
        # Assert
        assert stock_level == sample_product.quantity


class TestOrder:
    def test_order_creation(self):
        # Act
        order = Order(order_id="test-order", customer_id="test-customer")
        
        # Assert
        assert order.order_id == "test-order"
        assert order.customer_id == "test-customer"
        assert order.items == {}
        assert order.status == "pending"
        assert order._is_finalized is False
    
    def test_order_creation_auto_id(self):
        # Act
        order = Order()
        
        # Assert
        assert isinstance(order.order_id, str)
        assert len(order.order_id) > 0
    
    def test_add_item(self, sample_order, sample_product):
        # Act
        sample_order.add_item(sample_product, 2)
        
        # Assert
        assert sample_product.product_id in sample_order.items
        assert sample_order.items[sample_product.product_id]["quantity"] == 2
        assert sample_order.items[sample_product.product_id]["price_at_purchase"] == sample_product.price
    
    def test_add_item_with_inventory(self, sample_order, sample_product, populated_inventory):
        # Arrange
        original_quantity = sample_product.quantity
        quantity_to_add = 2
        
        # Act
        sample_order.add_item(sample_product, quantity_to_add, populated_inventory)
        
        # Assert
        assert sample_order.items[sample_product.product_id]["quantity"] == quantity_to_add
        assert populated_inventory.get_product(sample_product.product_id).quantity == original_quantity - quantity_to_add
    
    def test_add_item_insufficient_stock(self, sample_order, sample_product, populated_inventory):
        # Act & Assert
        with pytest.raises(ValueError):
            sample_order.add_item(sample_product, 100, populated_inventory)
    
    def test_add_item_to_finalized_order(self, sample_order, sample_product):
        # Arrange
        sample_order._is_finalized = True
        
        # Act & Assert
        with pytest.raises(RuntimeError):
            sample_order.add_item(sample_product, 1)
    
    def test_remove_item(self, sample_order, sample_product):
        # Arrange
        sample_order.add_item(sample_product, 3)
        
        # Act
        sample_order.remove_item(sample_product.product_id, 2)
        
        # Assert
        assert sample_order.items[sample_product.product_id]["quantity"] == 1
    
    def test_remove_item_complete(self, sample_order, sample_product):
        # Arrange
        sample_order.add_item(sample_product, 2)
        
        # Act
        sample_order.remove_item(sample_product.product_id, 2)
        
        # Assert
        assert sample_product.product_id not in sample_order.items
    
    def test_remove_item_with_inventory(self, sample_order, sample_product, populated_inventory):
        # Arrange
        original_quantity = populated_inventory.get_product(sample_product.product_id).quantity
        sample_order.add_item(sample_product, 2, populated_inventory)
        
        # Act
        sample_order.remove_item(sample_product.product_id, 1, populated_inventory)
        
        # Assert
        assert sample_order.items[sample_product.product_id]["quantity"] == 1
        assert populated_inventory.get_product(sample_product.product_id).quantity == original_quantity - 1
    
    def test_remove_item_too_many(self, sample_order, sample_product):
        # Arrange
        sample_order.add_item(sample_product, 1)
        
        # Act & Assert
        with pytest.raises(ValueError):
            sample_order.remove_item(sample_product.product_id, 2)
    
    def test_calculate_total(self, sample_order, sample_product, sample_digital_product):
        # Arrange
        sample_order.add_item(sample_product, 2)
        sample_order.add_item(sample_digital_product, 1)
        
        # Act
        total = sample_order.calculate_total()
        
        # Assert
        expected_total = (sample_product.price * 2) + sample_digital_product.price
        assert total == round(expected_total, 2)
    
    def test_update_status(self, sample_order):
        # Act
        sample_order.update_status("processing")
        
        # Assert
        assert sample_order.status == "processing"
        assert sample_order._is_finalized is False
    
    def test_update_status_finalizes_order(self, sample_order):
        # Act
        sample_order.update_status("shipped")
        
        # Assert
        assert sample_order.status == "shipped"
        assert sample_order._is_finalized is True
    
    def test_update_status_invalid(self, sample_order):
        # Act & Assert
        with pytest.raises(ValueError):
            sample_order.update_status("packed")
    
    def test_update_status_from_delivered(self, sample_order):
        # Arrange
        sample_order.update_status("delivered")
        
        # Act & Assert
        with pytest.raises(ValueError):
            sample_order.update_status("processing")
        
        # Should allow refunded
        sample_order.update_status("refunded")
        assert sample_order.status == "refunded"
    
    def test_get_order_summary(self, sample_order, sample_product, sample_digital_product):
        # Arrange
        sample_order.add_item(sample_product, 2)
        sample_order.add_item(sample_digital_product, 1)
        
        # Act
        summary = sample_order.get_order_summary()
        
        # Assert
        assert summary["order_id"] == sample_order.order_id
        assert summary["customer_id"] == sample_order.customer_id
        assert summary["status"] == sample_order.status
        assert summary["total_items"] == 3
        assert summary["total_cost"] == sample_order.calculate_total()
        assert len(summary["items"]) == 2
    
    def test_finalize_order(self, sample_order, sample_product):
        # Arrange
        sample_order.add_item(sample_product, 1)
        
        # Act
        sample_order.finalize_order()
        
        # Assert
        assert sample_order._is_finalized is True
        assert sample_order.status == "awaiting_payment"
    
    def test_finalize_empty_order(self, sample_order):
        # Act & Assert
        with pytest.raises(ValueError):
            sample_order.finalize_order()
    
    def test_order_repr(self, sample_order, sample_product):
        # Arrange
        sample_order.add_item(sample_product, 2)
        
        # Act
        representation = repr(sample_order)
        
        # Assert
        expected = f"Order(id='{sample_order.order_id}', status='{sample_order.status}', items={len(sample_order.items)}, total={sample_order.calculate_total()})"
        assert representation == expected