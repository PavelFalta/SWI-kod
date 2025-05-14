import sys
sys.path.append("..")

import pytest
import uuid
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# --- Fixtures ---

@pytest.fixture
def product_data():
    """Provides basic data for a generic product."""
    return {"name": "Generic Item", "price": 19.99, "quantity": 10}

@pytest.fixture
def sample_product(product_data):
    """Provides a sample Product instance."""
    return Product(**product_data)

@pytest.fixture
def digital_product_data():
    """Provides data for a digital product."""
    return {
        "name": "Software License",
        "price": 49.99,
        "download_link": "https://example.com/license_key",
        "file_size_mb": 1.5
        # quantity defaults to 1 for DigitalProduct in its constructor
    }

@pytest.fixture
def sample_digital_product(digital_product_data):
    """Provides a sample DigitalProduct instance."""
    return DigitalProduct(**digital_product_data)

@pytest.fixture
def physical_product_data():
    """Provides data for a physical product."""
    return {
        "name": "Heavy Book",
        "price": 29.99,
        "weight_kg": 1.2,
        "shipping_dimensions": (25, 18, 4), # L, W, H in cm
        "quantity": 5
    }

@pytest.fixture
def sample_physical_product(physical_product_data):
    """Provides a sample PhysicalProduct instance."""
    return PhysicalProduct(**physical_product_data)

@pytest.fixture
def empty_inventory():
    """Provides an empty Inventory instance."""
    return Inventory()

@pytest.fixture
def inventory_with_products():
    """Provides an Inventory instance populated with various products."""
    inventory = Inventory()
    p1 = Product(name="Test Laptop", price=1200.00, quantity=5, product_id="prod_laptop_01")
    p2_data = {
        "name": "Test Software", "price": 199.99, 
        "download_link": "https://example.com/software", "file_size_mb": 500, 
        "product_id": "prod_software_01"
    }
    # DigitalProduct quantity defaults to 1 if not specified, but we can set it via add_product's initial_stock
    p2 = DigitalProduct(**p2_data)


    p3_data = {
        "name": "Test Chair", "price": 150.00, "weight_kg": 15, 
        "shipping_dimensions": (60,60,90), "product_id": "prod_chair_01"
    }
    p3 = PhysicalProduct(**p3_data)

    inventory.add_product(p1, initial_stock=p1.quantity)
    inventory.add_product(p2, initial_stock=2) # Explicitly set stock for digital product in inventory
    inventory.add_product(p3, initial_stock=p3.quantity)
    
    # Update p2 quantity to match initial_stock for consistency in later tests
    p2.quantity = 2 
    
    return inventory, p1, p2, p3

@pytest.fixture
def sample_order_data():
    """Provides basic data for an order."""
    return {"customer_id": "cust_789"}

@pytest.fixture
def sample_order(sample_order_data):
    """Provides a sample Order instance."""
    return Order(**sample_order_data)

# --- Test Classes ---

class TestProduct:
    def test_product_creation_ok(self, product_data):
        product = Product(**product_data)
        assert product.name == product_data["name"]
        assert product.price == product_data["price"]
        assert product.quantity == product_data["quantity"]
        assert isinstance(product.product_id, str)

    def test_product_creation_default_id_quantity(self):
        product = Product(name="Default Test", price=10.0)
        assert product.quantity == 0
        assert isinstance(product.product_id, str)
        assert len(product.product_id) > 0

    def test_product_creation_with_specific_id(self):
        product_id = "custom_id_123"
        product = Product(name="Specific ID Test", price=5.0, product_id=product_id)
        assert product.product_id == product_id

    @pytest.mark.parametrize("name", [None, "", "   ", 123])
    def test_product_invalid_name(self, name, product_data):
        data = product_data.copy()
        data["name"] = name
        with pytest.raises(TypeError, match="Product name must be a non-empty string."):
            Product(**data)

    @pytest.mark.parametrize("price", [0, -10, "free"])
    def test_product_invalid_price(self, price, product_data):
        data = product_data.copy()
        data["price"] = price
        with pytest.raises((ValueError, TypeError)): # Catches both ValueError and TypeError
            Product(**data)

    def test_product_invalid_product_id_type(self, product_data):
        data = product_data.copy()
        data["product_id"] = 12345
        with pytest.raises(TypeError, match="Product ID must be a string if provided."):
            Product(**data)

    @pytest.mark.parametrize("quantity", [-1, "ten", 10.5])
    def test_product_invalid_quantity(self, quantity, product_data):
        data = product_data.copy()
        data["quantity"] = quantity
        with pytest.raises((ValueError, TypeError)):
            Product(**data)

    def test_product_get_details(self, sample_product):
        details = sample_product.get_details()
        assert details["product_id"] == sample_product.product_id
        assert details["name"] == sample_product.name
        assert details["price"] == sample_product.price
        assert details["quantity"] == sample_product.quantity
        assert details["type"] == "GenericProduct"

    def test_product_update_quantity_ok(self, sample_product):
        initial_quantity = sample_product.quantity
        sample_product.update_quantity(5)
        assert sample_product.quantity == initial_quantity + 5
        sample_product.update_quantity(-3)
        assert sample_product.quantity == initial_quantity + 2

    def test_product_update_quantity_invalid_type(self, sample_product):
        with pytest.raises(TypeError, match="Quantity change must be an integer."):
            sample_product.update_quantity("five")

    def test_product_update_quantity_below_zero(self, sample_product):
        with pytest.raises(ValueError, match="Quantity cannot be reduced below zero."):
            sample_product.update_quantity(-(sample_product.quantity + 1))

    def test_product_apply_discount_ok(self, sample_product):
        original_price = sample_product.price
        discount = 10  # 10%
        sample_product.apply_discount(discount)
        expected_price = round(original_price * (1 - discount / 100.0), 2)
        assert sample_product.price == expected_price

    @pytest.mark.parametrize("discount", ["ten", None])
    def test_product_apply_discount_invalid_percentage_type(self, sample_product, discount):
        with pytest.raises(TypeError, match="Discount percentage must be a number."):
            sample_product.apply_discount(discount)

    @pytest.mark.parametrize("discount", [-10, 101])
    def test_product_apply_discount_percentage_out_of_range(self, sample_product, discount):
        with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100."):
            sample_product.apply_discount(discount)

    def test_product_repr(self, sample_product):
        expected_repr = f"Product(name='{sample_product.name}', price={sample_product.price}, id='{sample_product.product_id}', quantity={sample_product.quantity})"
        assert repr(sample_product) == expected_repr


class TestDigitalProduct: # User-provided example
    def test_digital_product_creation_ok(self, digital_product_data):
        # Arrange
        # digital_product_data is arranged
        
        # Act
        product = DigitalProduct(**digital_product_data)
        
        # Assert
        assert product.name == digital_product_data["name"]
        assert product.price == digital_product_data["price"]
        assert product.download_link == digital_product_data["download_link"]
        assert product.file_size_mb == digital_product_data["file_size_mb"]
        # DigitalProduct's __init__ sets quantity to 1 by default if not specified
        assert product.quantity == 1 
        assert isinstance(product.product_id, str)

    def test_digital_product_creation_default_quantity(self):
        # Arrange
        data = {"name": "Test App", "price": 9.99, "download_link": "https://example.com/app", "file_size_mb": 50.0}
        # Act
        product = DigitalProduct(**data)
        # Assert
        assert product.quantity == 1

    def test_digital_product_creation_with_quantity(self, digital_product_data):
        data = digital_product_data.copy()
        data["quantity"] = 5
        product = DigitalProduct(**data)
        assert product.quantity == 5

    @pytest.mark.parametrize("link", ["ftp://invalid.com", "example.com", 123])
    def test_digital_product_invalid_download_link(self, link, digital_product_data):
        # Arrange
        data = digital_product_data.copy()
        data["download_link"] = link
        
        # Act & Assert
        with pytest.raises(TypeError, match="Download link must be a valid URL string starting with http:// or https://."):
            DigitalProduct(**data)

    @pytest.mark.parametrize("size", [0, -10, "big"])
    def test_digital_product_invalid_file_size(self, size, digital_product_data):
        # Arrange
        data = digital_product_data.copy()
        data["file_size_mb"] = size
        
        # Act & Assert
        with pytest.raises((ValueError, TypeError)): # Catches ValueError for 0, -10 and TypeError for "big"
            DigitalProduct(**data)

    def test_digital_product_get_details(self, sample_digital_product):
        # Arrange
        # sample_digital_product is arranged
        
        # Act
        details = sample_digital_product.get_details()
        
        # Assert
        assert details["product_id"] == sample_digital_product.product_id
        assert details["name"] == sample_digital_product.name
        assert details["download_link"] == sample_digital_product.download_link
        assert details["file_size_mb"] == sample_digital_product.file_size_mb
        assert details["type"] == "DigitalProduct"
        assert details["quantity"] == sample_digital_product.quantity

    def test_generate_new_download_link(self, sample_digital_product):
        # Arrange
        base_url = "https://newstore.com/downloads"
        original_link = sample_digital_product.download_link
        
        # Act
        new_link = sample_digital_product.generate_new_download_link(base_url)
        
        # Assert
        assert new_link != original_link
        assert new_link.startswith(f"{base_url}/{sample_digital_product.product_id}/download_")
        assert sample_digital_product.download_link == new_link # Check if attribute is updated

    def test_generate_new_download_link_invalid_base_url(self, sample_digital_product):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Base URL must be a non-empty string."):
            sample_digital_product.generate_new_download_link("  ") # Empty or whitespace only

    def test_digital_product_repr(self, sample_digital_product):
        # Arrange
        # sample_digital_product is arranged
        
        # Act
        representation = repr(sample_digital_product)
        
        # Assert
        expected_repr = f"DigitalProduct(name='{sample_digital_product.name}', price={sample_digital_product.price}, id='{sample_digital_product.product_id}', link='{sample_digital_product.download_link}')"
        assert representation == expected_repr


class TestPhysicalProduct:
    def test_physical_product_creation_ok(self, physical_product_data):
        product = PhysicalProduct(**physical_product_data)
        assert product.name == physical_product_data["name"]
        assert product.price == physical_product_data["price"]
        assert product.weight_kg == physical_product_data["weight_kg"]
        assert product.shipping_dimensions == physical_product_data["shipping_dimensions"]
        assert product.quantity == physical_product_data["quantity"]
        assert isinstance(product.product_id, str)

    @pytest.mark.parametrize("weight", [0, -5.0, "light"])
    def test_physical_product_invalid_weight(self, weight, physical_product_data):
        data = physical_product_data.copy()
        data["weight_kg"] = weight
        with pytest.raises((ValueError, TypeError)):
            PhysicalProduct(**data)

    @pytest.mark.parametrize("dims", [
        (10, 20), "10x20x30", (10, 20, 0), (10, -5, 30), (10, "20", 30), None
    ])
    def test_physical_product_invalid_dimensions(self, dims, physical_product_data):
        data = physical_product_data.copy()
        data["shipping_dimensions"] = dims
        with pytest.raises(TypeError, match="Shipping dimensions must be a tuple of three positive numbers"):
            PhysicalProduct(**data)

    def test_physical_product_get_details(self, sample_physical_product):
        details = sample_physical_product.get_details()
        assert details["name"] == sample_physical_product.name
        assert details["weight_kg"] == sample_physical_product.weight_kg
        assert details["shipping_dimensions_cm"] == sample_physical_product.shipping_dimensions
        assert details["type"] == "PhysicalProduct"
        assert details["quantity"] == sample_physical_product.quantity

    def test_physical_product_calculate_shipping_cost_ok(self, sample_physical_product):
        cost = sample_physical_product.calculate_shipping_cost(rate_per_kg=5.0)
        # (25*18*4)/5000 = 0.36. Weight = 1.2. Chargeable = 1.2. Cost = 1.2 * 5.0 = 6.0
        assert cost == 6.00 

    def test_physical_product_calculate_shipping_cost_volumetric(self, sample_physical_product):
        # Make weight less than volumetric weight
        sample_physical_product.weight_kg = 0.1 
        cost = sample_physical_product.calculate_shipping_cost(rate_per_kg=10.0, volumetric_factor=6000)
        # (25*18*4)/6000 = 0.3. Weight = 0.1. Chargeable = 0.3. Cost = 0.3 * 10.0 = 3.0
        assert cost == 3.00

    @pytest.mark.parametrize("rate", [0, -2.5, "cheap"])
    def test_physical_product_calculate_shipping_cost_invalid_rate(self, sample_physical_product, rate):
        with pytest.raises((ValueError, TypeError)):
            sample_physical_product.calculate_shipping_cost(rate_per_kg=rate)
            
    @pytest.mark.parametrize("factor", [0, -2000, "standard"])
    def test_physical_product_calculate_shipping_cost_invalid_factor(self, sample_physical_product, factor):
        with pytest.raises((ValueError, TypeError)):
            sample_physical_product.calculate_shipping_cost(rate_per_kg=5, volumetric_factor=factor)


    def test_physical_product_repr(self, sample_physical_product):
        expected_repr = f"PhysicalProduct(name='{sample_physical_product.name}', price={sample_physical_product.price}, id='{sample_physical_product.product_id}', weight={sample_physical_product.weight_kg}kg)"
        assert repr(sample_physical_product) == expected_repr


class TestInventory:
    def test_inventory_creation(self, empty_inventory):
        assert isinstance(empty_inventory.products, dict)
        assert len(empty_inventory.products) == 0

    def test_inventory_add_product_ok(self, empty_inventory, sample_product):
        empty_inventory.add_product(sample_product)
        assert sample_product.product_id in empty_inventory.products
        assert empty_inventory.products[sample_product.product_id] == sample_product

    def test_inventory_add_product_with_initial_stock(self, empty_inventory, sample_product):
        stock_level = 50
        # Product's initial quantity might be different
        original_product_quantity = sample_product.quantity
        empty_inventory.add_product(sample_product, initial_stock=stock_level)
        assert sample_product.product_id in empty_inventory.products
        assert empty_inventory.get_product(sample_product.product_id).quantity == stock_level
        # Reset for other tests if sample_product is reused
        sample_product.quantity = original_product_quantity


    def test_inventory_add_product_invalid_type(self, empty_inventory):
        with pytest.raises(TypeError, match="Item to add must be an instance of Product."):
            empty_inventory.add_product("not_a_product")

    def test_inventory_add_product_duplicate_id(self, empty_inventory, sample_product):
        empty_inventory.add_product(sample_product)
        product_copy = Product(name=sample_product.name, price=sample_product.price, product_id=sample_product.product_id)
        with pytest.raises(ValueError, match=f"Product with ID {sample_product.product_id} already exists"):
            empty_inventory.add_product(product_copy)

    @pytest.mark.parametrize("stock", [-5, "many"])
    def test_inventory_add_product_invalid_initial_stock(self, empty_inventory, sample_product, stock):
        with pytest.raises((ValueError, TypeError)): # ValueError for -5, TypeError for "many"
            empty_inventory.add_product(sample_product, initial_stock=stock)

    def test_inventory_remove_product_ok(self, inventory_with_products):
        inv, p1, _, _ = inventory_with_products
        removed_product = inv.remove_product(p1.product_id)
        assert p1.product_id not in inv.products
        assert removed_product == p1

    def test_inventory_remove_product_invalid_id_type(self, empty_inventory):
        with pytest.raises(TypeError, match="Product ID must be a string."):
            empty_inventory.remove_product(123)

    def test_inventory_remove_product_not_found(self, empty_inventory):
        with pytest.raises(KeyError, match="Product with ID non_existent_id not found"):
            empty_inventory.remove_product("non_existent_id")

    def test_inventory_get_product_ok(self, inventory_with_products):
        inv, p1, _, _ = inventory_with_products
        product = inv.get_product(p1.product_id)
        assert product == p1

    def test_inventory_update_stock_ok(self, inventory_with_products):
        inv, p1, _, _ = inventory_with_products
        initial_stock = p1.quantity
        inv.update_stock(p1.product_id, 5)
        assert inv.get_product(p1.product_id).quantity == initial_stock + 5
        inv.update_stock(p1.product_id, -3)
        assert inv.get_product(p1.product_id).quantity == initial_stock + 2

    def test_inventory_update_stock_product_not_found(self, empty_inventory):
        with pytest.raises(KeyError): # Product not found
            empty_inventory.update_stock("non_existent_id", 5)
    
    def test_inventory_update_stock_insufficient(self, inventory_with_products):
        inv, p1, _, _ = inventory_with_products
        with pytest.raises(ValueError, match="Stock update for .* failed: Quantity cannot be reduced below zero."):
            inv.update_stock(p1.product_id, -(p1.quantity + 10))

    def test_inventory_get_total_value_empty(self, empty_inventory):
        assert empty_inventory.get_total_inventory_value() == 0.0

    def test_inventory_get_total_value_populated(self, inventory_with_products):
        inv, p1, p2, p3 = inventory_with_products
        expected_value = (p1.price * p1.quantity) + \
                         (p2.price * p2.quantity) + \
                         (p3.price * p3.quantity)
        assert inv.get_total_inventory_value() == round(expected_value, 2)

    def test_inventory_find_products_by_name(self, inventory_with_products):
        inv, p1, p2, p3 = inventory_with_products # p1="Test Laptop", p2="Test Software", p3="Test Chair"
        results_laptop = inv.find_products_by_name("Laptop")
        assert len(results_laptop) == 1
        assert results_laptop[0] == p1

        results_test_case_insensitive = inv.find_products_by_name("test", case_sensitive=False)
        assert len(results_test_case_insensitive) == 3 # All contain "Test"

        results_test_case_sensitive = inv.find_products_by_name("Test", case_sensitive=True)
        assert len(results_test_case_sensitive) == 3

        results_soft = inv.find_products_by_name("Soft", case_sensitive=False)
        assert len(results_soft) == 1
        assert results_soft[0] == p2
        
        results_no_match = inv.find_products_by_name("XYZ")
        assert len(results_no_match) == 0

    def test_inventory_get_products_in_price_range(self, inventory_with_products):
        inv, p1, p2, p3 = inventory_with_products # Prices: p1=1200, p2=199.99, p3=150
        
        results = inv.get_products_in_price_range(min_price=100, max_price=200)
        assert len(results) == 2 # p2 and p3
        assert p2 in results
        assert p3 in results

        results_high_price = inv.get_products_in_price_range(min_price=1000)
        assert len(results_high_price) == 1
        assert p1 in results_high_price
        
        results_all = inv.get_products_in_price_range() # Default full range
        assert len(results_all) == 3


    @pytest.mark.parametrize("min_p, max_p", [(-1, 100), (100, 50), ("low", 100)])
    def test_inventory_get_products_in_price_range_invalid_prices(self, inventory_with_products, min_p, max_p):
        inv, _, _, _ = inventory_with_products
        with pytest.raises((ValueError, TypeError)):
             inv.get_products_in_price_range(min_price=min_p, max_price=max_p)

    def test_inventory_get_stock_level_ok(self, inventory_with_products):
        inv, p1, _, _ = inventory_with_products
        assert inv.get_stock_level(p1.product_id) == p1.quantity


class TestOrder:
    def test_order_creation_ok(self):
        order = Order()
        assert isinstance(order.order_id, str)
        assert order.customer_id is None
        assert order.status == "pending"
        assert not order._is_finalized

    def test_order_creation_with_ids(self, sample_order_data):
        order_id = "order_abc"
        order = Order(order_id=order_id, customer_id=sample_order_data["customer_id"])
        assert order.order_id == order_id
        assert order.customer_id == sample_order_data["customer_id"]

    @pytest.mark.parametrize("order_id, customer_id", [(123, "cust"), ("order", 456)])
    def test_order_creation_invalid_ids(self, order_id, customer_id):
        with pytest.raises(TypeError):
            Order(order_id=order_id, customer_id=customer_id)

    def test_order_add_item_ok(self, sample_order, sample_product):
        sample_order.add_item(sample_product, 2)
        assert sample_product.product_id in sample_order.items
        item_info = sample_order.items[sample_product.product_id]
        assert item_info["quantity"] == 2
        assert item_info["price_at_purchase"] == sample_product.price
        assert item_info["product_snapshot"]["name"] == sample_product.name

    def test_order_add_item_existing(self, sample_order, sample_product):
        sample_order.add_item(sample_product, 1)
        sample_order.add_item(sample_product, 3)
        assert sample_order.items[sample_product.product_id]["quantity"] == 4

    def test_order_add_item_with_inventory_check_ok(self, sample_order, inventory_with_products):
        inv, p1, _, _ = inventory_with_products # p1 has quantity 5
        original_inv_qty = inv.get_stock_level(p1.product_id)
        
        sample_order.add_item(p1, 2, inventory=inv)
        assert p1.product_id in sample_order.items
        assert sample_order.items[p1.product_id]["quantity"] == 2
        assert inv.get_stock_level(p1.product_id) == original_inv_qty - 2

    def test_order_add_item_with_inventory_check_insufficient_stock(self, sample_order, inventory_with_products):
        inv, p1, _, _ = inventory_with_products # p1 has quantity 5
        with pytest.raises(ValueError, match="Not enough stock"):
            sample_order.add_item(p1, 10, inventory=inv)

    def test_order_add_item_to_finalized_order(self, sample_order, sample_product):
        sample_order.finalize_order() # finalize_order needs items, so add one first
        # sample_order.add_item(sample_product, 1) # Add item before finalizing
        # sample_order.finalize_order() # Now finalize
        # Correcting: finalize_order raises error if empty, so need an item
        prod_for_finalize = Product("Temp", 1.0)
        sample_order.add_item(prod_for_finalize, 1)
        sample_order.finalize_order()

        with pytest.raises(RuntimeError, match="Cannot add items to a finalized order."):
            sample_order.add_item(sample_product, 1)

    def test_order_remove_item_ok(self, sample_order, sample_product):
        sample_order.add_item(sample_product, 5)
        sample_order.remove_item(sample_product.product_id, 2)
        assert sample_order.items[sample_product.product_id]["quantity"] == 3

    def test_order_remove_item_all_quantity(self, sample_order, sample_product):
        sample_order.add_item(sample_product, 2)
        sample_order.remove_item(sample_product.product_id, 2)
        assert sample_product.product_id not in sample_order.items

    def test_order_remove_item_with_inventory_restock(self, sample_order, inventory_with_products):
        inv, p1, _, _ = inventory_with_products
        initial_inv_qty = inv.get_stock_level(p1.product_id)
        
        sample_order.add_item(p1, 3, inventory=inv) # Stock becomes initial_inv_qty - 3
        assert inv.get_stock_level(p1.product_id) == initial_inv_qty - 3
        
        sample_order.remove_item(p1.product_id, 1, inventory=inv) # Stock becomes initial_inv_qty - 3 + 1
        assert sample_order.items[p1.product_id]["quantity"] == 2
        assert inv.get_stock_level(p1.product_id) == initial_inv_qty - 2


    def test_order_remove_item_from_finalized_order_disallowed(self, sample_order, sample_product):
        # Order needs an item to be finalized
        temp_prod = Product("Finalize Item", 10.0, quantity=1)
        sample_order.add_item(temp_prod, 1)
        sample_order.finalize_order() # status becomes "awaiting_payment"
        sample_order.update_status("shipped")
        
        with pytest.raises(RuntimeError, match="Cannot remove items from an order with status 'shipped'."):
            sample_order.remove_item(temp_prod.product_id, 1)


    def test_order_calculate_total_empty(self, sample_order):
        assert sample_order.calculate_total() == 0.0

    def test_order_calculate_total_with_items(self, sample_order, sample_product):
        p2 = Product("Another Item", 10.00, quantity=3)
        sample_order.add_item(sample_product, 2) # sample_product price 19.99
        sample_order.add_item(p2, 1) # p2 price 10.00
        expected_total = (19.99 * 2) + (10.00 * 1)
        assert sample_order.calculate_total() == round(expected_total, 2)

    @pytest.mark.parametrize("status", ["processing", "shipped", "delivered", "cancelled", "refunded"])
    def test_order_update_status_ok_and_finalizes(self, sample_order, status, sample_product):
        # Add item to allow finalization implicitly
        sample_order.add_item(sample_product, 1)
        sample_order.update_status(status)
        assert sample_order.status == status
        if status in ["shipped", "delivered", "cancelled", "refunded"]:
            assert sample_order._is_finalized

    def test_order_update_status_invalid_value(self, sample_order):
        with pytest.raises(ValueError, match="Invalid order status 'unknown_status'"):
            sample_order.update_status("unknown_status")

    def test_order_update_status_invalid_transition_delivered(self, sample_order, sample_product):
        sample_order.add_item(sample_product, 1) # Add item
        sample_order.update_status("delivered")
        with pytest.raises(ValueError, match="Cannot change status from 'delivered' to 'processing'"):
            sample_order.update_status("processing")
        sample_order.update_status("refunded") # This should be allowed
        assert sample_order.status == "refunded"

    def test_order_update_status_invalid_transition_cancelled(self, sample_order, sample_product):
        sample_order.add_item(sample_product, 1) # Add item
        sample_order.update_status("cancelled")
        with pytest.raises(ValueError, match="Cannot change status of a 'cancelled' order."):
            sample_order.update_status("pending")

    def test_order_finalize_order_ok(self, sample_order, sample_product):
        sample_order.add_item(sample_product, 1) # Add an item first
        assert not sample_order._is_finalized
        assert sample_order.status == "pending"
        sample_order.finalize_order()
        assert sample_order._is_finalized
        assert sample_order.status == "awaiting_payment"

    def test_order_finalize_order_empty(self, sample_order):
        with pytest.raises(ValueError, match="Cannot finalize an empty order."):
            sample_order.finalize_order()
            
    def test_order_get_order_summary(self, sample_order, sample_product):
        p2 = Product(name="Item B", price=5.50)
        sample_order.add_item(sample_product, 2) # 19.99 each
        sample_order.add_item(p2, 3) # 5.50 each
        sample_order.customer_id = "cust_summary_123"
        sample_order.update_status("processing")

        summary = sample_order.get_order_summary()

        assert summary["order_id"] == sample_order.order_id
        assert summary["customer_id"] == "cust_summary_123"
        assert summary["status"] == "processing"
        assert summary["total_items"] == 5
        expected_total = round((19.99 * 2) + (5.50 * 3), 2)
        assert summary["total_cost"] == expected_total
        assert len(summary["items"]) == 2
        
        item1_summary = next(item for item in summary["items"] if item["product_id"] == sample_product.product_id)
        assert item1_summary["name"] == sample_product.name
        assert item1_summary["quantity"] == 2
        assert item1_summary["unit_price"] == sample_product.price
        assert item1_summary["subtotal"] == round(sample_product.price * 2, 2)

    def test_order_repr(self, sample_order, sample_product):
        sample_order.add_item(sample_product, 1)
        expected_repr = f"Order(id='{sample_order.order_id}', status='{sample_order.status}', items=1, total={sample_order.calculate_total()})"
        assert repr(sample_order) == expected_repr
