import pytest
import uuid
import sys
sys.path.append("..")
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# Helper function to generate a unique ID for testing if needed
def generate_test_id():
    return str(uuid.uuid4())

# Fixtures for Product
@pytest.fixture
def sample_product_data():
    return {"name": "Test Laptop", "price": 1200.00, "quantity": 10}

@pytest.fixture
def sample_product(sample_product_data):
    return Product(**sample_product_data)

@pytest.fixture
def digital_product_data():
    return {
        "name": "Test Software", 
        "price": 49.99, 
        "download_link": "http://example.com/download/software", 
        "file_size_mb": 100.0,
        "quantity": 1 # Digital products usually have quantity 1 unless managed differently
    }

@pytest.fixture
def sample_digital_product(digital_product_data):
    return DigitalProduct(**digital_product_data)

@pytest.fixture
def physical_product_data():
    return {
        "name": "Test Book", 
        "price": 19.99, 
        "weight_kg": 0.5, 
        "shipping_dimensions": (20, 15, 5), # cm
        "quantity": 50
    }

@pytest.fixture
def sample_physical_product(physical_product_data):
    return PhysicalProduct(**physical_product_data)

# Fixture for Inventory
@pytest.fixture
def empty_inventory():
    return Inventory()

@pytest.fixture
def populated_inventory(sample_product, sample_digital_product, sample_physical_product):
    inventory = Inventory()
    # Ensure products have distinct IDs for inventory addition
    sample_product.product_id = "prod_laptop_001"
    sample_digital_product.product_id = "prod_software_002"
    sample_physical_product.product_id = "prod_book_003"
    
    inventory.add_product(Product(name="Keyboard", price=75.00, product_id="prod_keyboard_004", quantity=25))
    inventory.add_product(sample_product, initial_stock=sample_product.quantity)
    inventory.add_product(sample_digital_product, initial_stock=sample_digital_product.quantity)
    inventory.add_product(sample_physical_product, initial_stock=sample_physical_product.quantity)
    return inventory

# Fixture for Order
@pytest.fixture
def sample_order():
    return Order(customer_id="cust_123")


class TestProduct:
    def test_product_creation_ok(self, sample_product_data):
        # Arrange
        name, price, quantity = sample_product_data["name"], sample_product_data["price"], sample_product_data["quantity"]
        
        # Act
        product = Product(name, price, quantity=quantity)
        
        # Assert
        assert product.name == name
        assert product.price == price
        assert product.quantity == quantity
        assert isinstance(product.product_id, str)

    def test_product_creation_with_id(self):
        # Arrange
        product_id = "custom_id_123"
        
        # Act
        product = Product("Test Item", 25.00, product_id=product_id)
        
        # Assert
        assert product.product_id == product_id

    @pytest.mark.parametrize("name", [None, "", "  ", 123])
    def test_product_creation_invalid_name(self, name):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Product name must be a non-empty string."):
            Product(name, 10.0)

    @pytest.mark.parametrize("price", [0, -10, "abc"])
    def test_product_creation_invalid_price(self, price):
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)): # Catches ValueError for price <= 0, TypeError for non-numeric
            Product("Valid Name", price)

    @pytest.mark.parametrize("quantity", [-1, "abc", 10.5])
    def test_product_creation_invalid_quantity(self, quantity):
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)): # Catches ValueError for <0, TypeError for non-int
            Product("Valid Name", 10.0, quantity=quantity)

    def test_product_creation_invalid_product_id_type(self):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Product ID must be a string if provided."):
            Product("Valid Name", 10.0, product_id=123)

    def test_get_details(self, sample_product):
        # Arrange
        # sample_product is already arranged
        
        # Act
        details = sample_product.get_details()
        
        # Assert
        assert details["product_id"] == sample_product.product_id
        assert details["name"] == sample_product.name
        assert details["price"] == sample_product.price
        assert details["quantity"] == sample_product.quantity
        assert details["type"] == "GenericProduct"

    def test_update_quantity_ok(self, sample_product):
        # Arrange
        initial_quantity = sample_product.quantity
        change = 5
        
        # Act
        sample_product.update_quantity(change)
        
        # Assert
        assert sample_product.quantity == initial_quantity + change

    def test_update_quantity_decrease_ok(self, sample_product):
        # Arrange
        sample_product.quantity = 10
        change = -3
        
        # Act
        sample_product.update_quantity(change)
        
        # Assert
        assert sample_product.quantity == 7

    def test_update_quantity_to_zero(self, sample_product):
        # Arrange
        sample_product.quantity = 5
        change = -5
        
        # Act
        sample_product.update_quantity(change)
        
        # Assert
        assert sample_product.quantity == 0
        
    def test_update_quantity_invalid_type(self, sample_product):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Quantity change must be an integer."):
            sample_product.update_quantity(5.5)

    def test_update_quantity_below_zero(self, sample_product):
        # Arrange
        sample_product.quantity = 2
        
        # Act & Assert
        with pytest.raises(ValueError, match="Quantity cannot be reduced below zero."):
            sample_product.update_quantity(-3)

    def test_apply_discount_ok(self, sample_product):
        # Arrange
        initial_price = sample_product.price # 1200.00
        discount = 10 # 10%
        
        # Act
        sample_product.apply_discount(discount)
        
        # Assert
        assert sample_product.price == round(initial_price * 0.9, 2) # 1080.00

    def test_apply_discount_float(self, sample_product):
        # Arrange
        sample_product.price = 100.00
        discount = 12.5 
        
        # Act
        sample_product.apply_discount(discount)
        
        # Assert
        assert sample_product.price == 87.50

    @pytest.mark.parametrize("discount", [-5, 101, "abc"])
    def test_apply_discount_invalid_value(self, sample_product, discount):
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)):
            sample_product.apply_discount(discount)
            
    def test_product_repr(self, sample_product):
        # Arrange
        # sample_product is arranged
        
        # Act
        representation = repr(sample_product)
        
        # Assert
        expected_repr = f"Product(name='{sample_product.name}', price={sample_product.price}, id='{sample_product.product_id}', quantity={sample_product.quantity})"
        assert representation == expected_repr


class TestDigitalProduct:
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
        assert product.quantity == digital_product_data["quantity"] # Should be 1 by default if not specified
        assert isinstance(product.product_id, str)

    def test_digital_product_creation_default_quantity(self):
        # Arrange
        data = {"name": "Test App", "price": 9.99, "download_link": "https://example.com/app", "file_size_mb": 50.0}
        # Act
        product = DigitalProduct(**data)
        # Assert
        assert product.quantity == 1


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
        with pytest.raises((ValueError, TypeError)):
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
            sample_digital_product.generate_new_download_link("")

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
        # Arrange
        # physical_product_data is arranged
        
        # Act
        product = PhysicalProduct(**physical_product_data)
        
        # Assert
        assert product.name == physical_product_data["name"]
        assert product.price == physical_product_data["price"]
        assert product.weight_kg == physical_product_data["weight_kg"]
        assert product.shipping_dimensions == physical_product_data["shipping_dimensions"]
        assert product.quantity == physical_product_data["quantity"]
        assert isinstance(product.product_id, str)

    @pytest.mark.parametrize("weight", [0, -5, "heavy"])
    def test_physical_product_invalid_weight(self, weight, physical_product_data):
        # Arrange
        data = physical_product_data.copy()
        data["weight_kg"] = weight
        
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            PhysicalProduct(**data)

    @pytest.mark.parametrize("dims", [(10, 20), (10, 20, 0), (10, 20, -5), "10x20x30", (10, "20", 30)])
    def test_physical_product_invalid_dimensions(self, dims, physical_product_data):
        # Arrange
        data = physical_product_data.copy()
        data["shipping_dimensions"] = dims
        
        # Act & Assert
        with pytest.raises(TypeError, match="Shipping dimensions must be a tuple of three positive numbers"):
            PhysicalProduct(**data)

    def test_physical_product_get_details(self, sample_physical_product):
        # Arrange
        # sample_physical_product is arranged
        
        # Act
        details = sample_physical_product.get_details()
        
        # Assert
        assert details["product_id"] == sample_physical_product.product_id
        assert details["name"] == sample_physical_product.name
        assert details["weight_kg"] == sample_physical_product.weight_kg
        assert details["shipping_dimensions_cm"] == sample_physical_product.shipping_dimensions
        assert details["type"] == "PhysicalProduct"
        assert details["quantity"] == sample_physical_product.quantity

    def test_calculate_shipping_cost_weight_based(self, sample_physical_product):
        # Arrange
        # weight_kg = 0.5, dimensions = (20,15,5) -> vol_weight = 20*15*5 / 5000 = 0.3 kg
        # Chargeable weight is 0.5 kg
        rate_per_kg = 10.0
        
        # Act
        cost = sample_physical_product.calculate_shipping_cost(rate_per_kg)
        
        # Assert
        assert cost == round(0.5 * rate_per_kg, 2) # 5.0

    def test_calculate_shipping_cost_volumetric_based(self, sample_physical_product):
        # Arrange
        sample_physical_product.weight_kg = 0.1 # Make actual weight less than volumetric
        # vol_weight = 20*15*5 / 5000 = 0.3 kg. Chargeable weight is 0.3 kg
        rate_per_kg = 10.0
        volumetric_factor = 5000
        
        # Act
        cost = sample_physical_product.calculate_shipping_cost(rate_per_kg, volumetric_factor)
        
        # Assert
        expected_vol_weight = (20*15*5)/volumetric_factor
        assert cost == round(expected_vol_weight * rate_per_kg, 2) # 3.0

    @pytest.mark.parametrize("rate", [0, -10, "abc"])
    def test_calculate_shipping_cost_invalid_rate(self, sample_physical_product, rate):
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)):
            sample_physical_product.calculate_shipping_cost(rate)

    @pytest.mark.parametrize("factor", [0, -10, "abc"])
    def test_calculate_shipping_cost_invalid_volumetric_factor(self, sample_physical_product, factor):
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)):
            sample_physical_product.calculate_shipping_cost(10.0, volumetric_factor=factor)

    def test_physical_product_repr(self, sample_physical_product):
        # Arrange
        # sample_physical_product is arranged
        
        # Act
        representation = repr(sample_physical_product)
        
        # Assert
        expected_repr = f"PhysicalProduct(name='{sample_physical_product.name}', price={sample_physical_product.price}, id='{sample_physical_product.product_id}', weight={sample_physical_product.weight_kg}kg)"
        assert representation == expected_repr

class TestInventory:
    def test_inventory_creation(self, empty_inventory):
        # Arrange & Act
        # empty_inventory is created
        
        # Assert
        assert empty_inventory.products == {}

    def test_add_product_ok(self, empty_inventory, sample_product):
        # Arrange
        inventory = empty_inventory
        
        # Act
        inventory.add_product(sample_product, initial_stock=5)
        
        # Assert
        assert sample_product.product_id in inventory.products
        assert inventory.products[sample_product.product_id] == sample_product
        assert inventory.get_product(sample_product.product_id).quantity == 5

    def test_add_product_no_initial_stock(self, empty_inventory, sample_product):
        # Arrange
        inventory = empty_inventory
        sample_product.quantity = 3 # Pre-set quantity
        
        # Act
        inventory.add_product(sample_product)
        
        # Assert
        assert sample_product.product_id in inventory.products
        assert inventory.get_product(sample_product.product_id).quantity == 3


    def test_add_product_invalid_type(self, empty_inventory):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Item to add must be an instance of Product."):
            empty_inventory.add_product("not a product")

    def test_add_product_duplicate_id(self, empty_inventory, sample_product):
        # Arrange
        empty_inventory.add_product(sample_product)
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Product with ID {sample_product.product_id} already exists in inventory."):
            empty_inventory.add_product(sample_product) # Adding same product again

    @pytest.mark.parametrize("stock", [-1, "abc", 5.5])
    def test_add_product_invalid_initial_stock(self, empty_inventory, sample_product, stock):
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)):
            empty_inventory.add_product(sample_product, initial_stock=stock)

    def test_remove_product_ok(self, populated_inventory, sample_product):
        # Arrange
        inventory = populated_inventory
        product_id_to_remove = sample_product.product_id # "prod_laptop_001"
        assert product_id_to_remove in inventory.products
        
        # Act
        removed_product = inventory.remove_product(product_id_to_remove)
        
        # Assert
        assert removed_product == sample_product
        assert product_id_to_remove not in inventory.products

    def test_remove_product_invalid_id_type(self, populated_inventory):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Product ID must be a string."):
            populated_inventory.remove_product(123)

    def test_remove_product_not_found(self, populated_inventory):
        # Arrange & Act & Assert
        with pytest.raises(KeyError, match="Product with ID non_existent_id not found in inventory."):
            populated_inventory.remove_product("non_existent_id")

    def test_get_product_ok(self, populated_inventory, sample_product):
        # Arrange
        inventory = populated_inventory
        product_id_to_get = sample_product.product_id
        
        # Act
        fetched_product = inventory.get_product(product_id_to_get)
        
        # Assert
        assert fetched_product == sample_product

    def test_get_product_invalid_id_type(self, populated_inventory):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Product ID must be a string."):
            populated_inventory.get_product(12345)

    def test_get_product_not_found(self, populated_inventory):
        # Arrange & Act & Assert
        with pytest.raises(KeyError, match="Product with ID non_existent_id not found in inventory."):
            populated_inventory.get_product("non_existent_id")

    def test_update_stock_increase(self, populated_inventory, sample_product):
        # Arrange
        inventory = populated_inventory
        product_id = sample_product.product_id
        initial_stock = inventory.get_product(product_id).quantity
        change = 5
        
        # Act
        inventory.update_stock(product_id, change)
        
        # Assert
        assert inventory.get_product(product_id).quantity == initial_stock + change

    def test_update_stock_decrease(self, populated_inventory, sample_product):
        # Arrange
        inventory = populated_inventory
        product_id = sample_product.product_id
        inventory.get_product(product_id).quantity = 10 # Ensure enough stock
        initial_stock = 10
        change = -3
        
        # Act
        inventory.update_stock(product_id, change)
        
        # Assert
        assert inventory.get_product(product_id).quantity == initial_stock + change


    def test_update_stock_product_not_found(self, populated_inventory):
        # Arrange & Act & Assert
        with pytest.raises(KeyError): # The get_product inside update_stock will raise this
            populated_inventory.update_stock("non_existent_id", 5)

    def test_update_stock_invalid_quantity_change(self, populated_inventory, sample_product):
        # Arrange
        inventory = populated_inventory
        product_id = sample_product.product_id
        inventory.get_product(product_id).quantity = 1 # Set stock to 1
        
        # Act & Assert
        with pytest.raises(ValueError, match="Stock update for .* failed: Quantity cannot be reduced below zero."):
            inventory.update_stock(product_id, -2) # Try to reduce by 2

    def test_update_stock_invalid_id_type(self, populated_inventory):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Product ID must be a string."):
            populated_inventory.update_stock(123, 5)

    def test_get_total_inventory_value_empty(self, empty_inventory):
        # Arrange & Act & Assert
        assert empty_inventory.get_total_inventory_value() == 0.0

    def test_get_total_inventory_value_populated(self, populated_inventory):
        # Arrange
        # populated_inventory fixture contains:
        # Keyboard: 75.00 * 25 = 1875
        # Laptop: 1200.00 * 10 = 12000
        # Software: 49.99 * 1 = 49.99
        # Book: 19.99 * 50 = 999.50
        # Total = 1875 + 12000 + 49.99 + 999.50 = 14924.49
        
        # Act
        total_value = populated_inventory.get_total_inventory_value()
        
        # Assert
        expected_value = sum(p.price * p.quantity for p in populated_inventory.products.values())
        assert total_value == round(expected_value, 2)
        assert total_value == 14924.49


    def test_find_products_by_name_found_case_insensitive(self, populated_inventory):
        # Arrange
        # Laptop (prod_laptop_001) and Test Laptop in sample_product fixture
        # Keyboard (prod_keyboard_004)
        
        # Act
        results = populated_inventory.find_products_by_name("laptop")
        
        # Assert
        assert len(results) == 1
        assert results[0].name == "Test Laptop"

    def test_find_products_by_name_found_case_sensitive(self, populated_inventory):
        # Arrange & Act
        results = populated_inventory.find_products_by_name("Laptop", case_sensitive=True)
        
        # Assert
        assert len(results) == 1
        assert results[0].name == "Test Laptop"

    def test_find_products_by_name_partial_match(self, populated_inventory):
         # Act
        results = populated_inventory.find_products_by_name("key") # Keyboard
        
        # Assert
        assert len(results) == 1
        assert results[0].name == "Keyboard"

    def test_find_products_by_name_multiple_matches(self, populated_inventory):
        # Arrange
        # Add another product with "Test"
        prod_test_game = Product("Test Game", 29.99, product_id="prod_game_005")
        populated_inventory.add_product(prod_test_game, 5)
        # Now we have "Test Laptop", "Test Software", "Test Book", "Test Game"
        
        # Act
        results = populated_inventory.find_products_by_name("Test")
        
        # Assert
        assert len(results) == 4 # Laptop, Software, Book, Game
        product_names = sorted([p.name for p in results])
        assert "Test Book" in product_names
        assert "Test Game" in product_names
        assert "Test Laptop" in product_names
        assert "Test Software" in product_names


    def test_find_products_by_name_no_match(self, populated_inventory):
        # Arrange & Act
        results = populated_inventory.find_products_by_name("nonexistent")
        
        # Assert
        assert len(results) == 0

    def test_find_products_by_name_invalid_term_type(self, populated_inventory):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Search term must be a string."):
            populated_inventory.find_products_by_name(123)

    def test_get_products_in_price_range_ok(self, populated_inventory):
        # Arrange
        # Keyboard: 75.00, Laptop: 1200.00, Software: 49.99, Book: 19.99
        min_price = 50.0
        max_price = 200.0
        
        # Act
        results = populated_inventory.get_products_in_price_range(min_price, max_price)
        
        # Assert
        assert len(results) == 1 # Only Keyboard (75.00)
        assert results[0].name == "Keyboard"

    def test_get_products_in_price_range_only_min(self, populated_inventory):
        # Arrange
        min_price = 1000.0
        
        # Act
        results = populated_inventory.get_products_in_price_range(min_price=min_price)
        
        # Assert
        assert len(results) == 1 # Only Laptop (1200.00)
        assert results[0].name == "Test Laptop"

    def test_get_products_in_price_range_only_max(self, populated_inventory):
        # Arrange
        max_price = 50.0
        
        # Act
        results = populated_inventory.get_products_in_price_range(max_price=max_price) # Software (49.99), Book (19.99)
        
        # Assert
        assert len(results) == 2
        names = sorted([p.name for p in results])
        assert "Test Book" in names
        assert "Test Software" in names


    def test_get_products_in_price_range_no_match(self, populated_inventory):
        # Arrange & Act
        results = populated_inventory.get_products_in_price_range(min_price=2000, max_price=3000)
        
        # Assert
        assert len(results) == 0

    @pytest.mark.parametrize("min_p, max_p", [(-1, 100), (100, 50), ("a", 100), (0, "b")])
    def test_get_products_in_price_range_invalid_prices(self, populated_inventory, min_p, max_p):
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)):
            populated_inventory.get_products_in_price_range(min_p, max_p)

    def test_get_stock_level_ok(self, populated_inventory, sample_product):
        # Arrange
        product_id = sample_product.product_id # Laptop, quantity 10
        
        # Act
        stock = populated_inventory.get_stock_level(product_id)
        
        # Assert
        assert stock == 10 # From populated_inventory fixture

    def test_get_stock_level_product_not_found(self, populated_inventory):
        # Arrange & Act & Assert
        with pytest.raises(KeyError):
            populated_inventory.get_stock_level("non_existent_id")

class TestOrder:
    def test_order_creation_ok(self):
        # Arrange
        customer_id = "cust_789"
        
        # Act
        order = Order(customer_id=customer_id)
        
        # Assert
        assert isinstance(order.order_id, str)
        assert order.customer_id == customer_id
        assert order.items == {}
        assert order.status == "pending"
        assert not order._is_finalized

    def test_order_creation_with_order_id(self):
        # Arrange
        order_id = "order_abc_123"
        
        # Act
        order = Order(order_id=order_id)
        
        # Assert
        assert order.order_id == order_id

    @pytest.mark.parametrize("order_id", [123, True])
    def test_order_creation_invalid_order_id_type(self, order_id):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Order ID must be a string if provided."):
            Order(order_id=order_id)
            
    @pytest.mark.parametrize("customer_id", [123, True])
    def test_order_creation_invalid_customer_id_type(self, customer_id):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Customer ID must be a string if provided."):
            Order(customer_id=customer_id)

    def test_add_item_ok_no_inventory(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        product = sample_product
        quantity = 2
        
        # Act
        order.add_item(product, quantity)
        
        # Assert
        assert product.product_id in order.items
        item_data = order.items[product.product_id]
        assert item_data["quantity"] == quantity
        assert item_data["price_at_purchase"] == product.price
        assert item_data["product_snapshot"]["name"] == product.name

    def test_add_item_ok_with_inventory(self, sample_order, sample_product, empty_inventory):
        # Arrange
        order = sample_order
        inventory = empty_inventory
        product = sample_product
        product.quantity = 10 # Set product's own quantity, not directly used by add_item logic
        inventory.add_product(product, initial_stock=5) # Add to inventory with stock
        quantity_to_add = 3
        initial_inv_stock = inventory.get_stock_level(product.product_id)
        
        # Act
        order.add_item(product, quantity_to_add, inventory=inventory)
        
        # Assert
        assert product.product_id in order.items
        assert order.items[product.product_id]["quantity"] == quantity_to_add
        assert inventory.get_stock_level(product.product_id) == initial_inv_stock - quantity_to_add

    def test_add_item_existing_increases_quantity(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        product = sample_product
        order.add_item(product, 2) # Add first time
        
        # Act
        order.add_item(product, 3) # Add same product again
        
        # Assert
        assert order.items[product.product_id]["quantity"] == 5

    def test_add_item_finalized_order(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        order.finalize_order() # Finalizes and sets status to awaiting_payment
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Cannot add items to a finalized order."):
            order.add_item(sample_product, 1)

    def test_add_item_invalid_product_type(self, sample_order):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Item to add must be an instance of Product."):
            sample_order.add_item("not_a_product", 1)

    @pytest.mark.parametrize("quantity", [0, -1, "many"])
    def test_add_item_invalid_quantity(self, sample_order, sample_product, quantity):
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)):
            sample_order.add_item(sample_product, quantity)

    def test_add_item_not_enough_stock_in_inventory(self, sample_order, sample_product, empty_inventory):
        # Arrange
        order = sample_order
        inventory = empty_inventory
        inventory.add_product(sample_product, initial_stock=1)
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Not enough stock for {sample_product.name}"):
            order.add_item(sample_product, 2, inventory=inventory)

    def test_add_item_product_not_in_inventory(self, sample_order, sample_product, empty_inventory):
        # Arrange
        order = sample_order
        inventory = empty_inventory # sample_product is not in this empty_inventory
        
        # Act & Assert
        with pytest.raises(KeyError): # get_product will raise KeyError
            order.add_item(sample_product, 1, inventory=inventory)

    def test_add_item_invalid_inventory_type(self, sample_order, sample_product):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Inventory must be an Inventory instance."):
            sample_order.add_item(sample_product, 1, inventory="not_inventory")


    def test_remove_item_ok_partial(self, sample_order, sample_product, empty_inventory):
        # Arrange
        order = sample_order
        inventory = empty_inventory
        inventory.add_product(sample_product, initial_stock=10) # Stock for restocking
        order.add_item(sample_product, 5) # No inventory check for add_item here
        initial_inv_stock = inventory.get_stock_level(sample_product.product_id)
        
        # Act
        order.remove_item(sample_product.product_id, 2, inventory=inventory)
        
        # Assert
        assert order.items[sample_product.product_id]["quantity"] == 3
        assert inventory.get_stock_level(sample_product.product_id) == initial_inv_stock + 2

    def test_remove_item_ok_full(self, sample_order, sample_product, empty_inventory):
        # Arrange
        order = sample_order
        inventory = empty_inventory
        inventory.add_product(sample_product, initial_stock=10)
        order.add_item(sample_product, 3) # No inv check for add
        initial_inv_stock = inventory.get_stock_level(sample_product.product_id)


        # Act
        order.remove_item(sample_product.product_id, 3, inventory=inventory)
        
        # Assert
        assert sample_product.product_id not in order.items
        assert inventory.get_stock_level(sample_product.product_id) == initial_inv_stock + 3

    def test_remove_item_no_inventory_restock(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        order.add_item(sample_product, 5)
        
        # Act
        order.remove_item(sample_product.product_id, 2) # No inventory specified
        
        # Assert
        assert order.items[sample_product.product_id]["quantity"] == 3

    @pytest.mark.parametrize("status", ["shipped", "delivered", "cancelled", "refunded"])
    def test_remove_item_finalized_order_disallowed_status(self, sample_order, sample_product, status):
        # Arrange
        order = sample_order
        order.add_item(sample_product, 1)
        order.status = status # Manually set status that finalizes
        order._is_finalized = True
        
        # Act & Assert
        with pytest.raises(RuntimeError, match=f"Cannot remove items from an order with status '{status}'."):
            order.remove_item(sample_product.product_id, 1)

    @pytest.mark.parametrize("status", ["pending", "awaiting_payment"])
    def test_remove_item_finalized_order_allowed_status(self, sample_order, sample_product, status):
        # Arrange
        order = sample_order
        order.add_item(sample_product, 2)
        order.status = status 
        order._is_finalized = True # E.g. after finalize_order() then status changes
        
        # Act
        order.remove_item(sample_product.product_id, 1)
        
        # Assert
        assert order.items[sample_product.product_id]["quantity"] == 1


    def test_remove_item_invalid_product_id_type(self, sample_order):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="Product ID must be a string."):
            sample_order.remove_item(123, 1)

    @pytest.mark.parametrize("quantity", [0, -1, "some"])
    def test_remove_item_invalid_quantity_to_remove(self, sample_order, sample_product, quantity):
        # Arrange
        order = sample_order
        order.add_item(sample_product, 5)
        
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            sample_order.remove_item(sample_product.product_id, quantity)

    def test_remove_item_product_not_in_order(self, sample_order):
        # Arrange & Act & Assert
        with pytest.raises(KeyError, match="Product with ID non_existent_id not found in order."):
            sample_order.remove_item("non_existent_id", 1)

    def test_remove_item_too_many_to_remove(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        order.add_item(sample_product, 2)
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Cannot remove 3 units of {sample_product.product_id}"):
            sample_order.remove_item(sample_product.product_id, 3)

    def test_remove_item_product_not_in_inventory_for_restock(self, sample_order, sample_product, empty_inventory):
        # Arrange
        order = sample_order
        inventory = empty_inventory # Product not in this inventory
        order.add_item(sample_product, 1) # Add to order

        # Act & Assert
        # The code currently tries to update_stock which calls get_product, this would raise KeyError from Inventory
        # which then is caught and reraised as RuntimeError in Order.remove_item
        with pytest.raises(RuntimeError, match=f"Product {sample_product.product_id} not found in inventory for restocking."):
           order.remove_item(sample_product.product_id, 1, inventory=inventory)


    def test_calculate_total_empty_order(self, sample_order):
        # Arrange & Act & Assert
        assert sample_order.calculate_total() == 0.0

    def test_calculate_total_one_item(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        product = sample_product # price 1200.00
        order.add_item(product, 2)
        
        # Act
        total = order.calculate_total()
        
        # Assert
        assert total == round(product.price * 2, 2) # 2400.00

    def test_calculate_total_multiple_items(self, sample_order, sample_product, sample_digital_product):
        # Arrange
        order = sample_order
        # sample_product: price 1200.00
        # sample_digital_product: price 49.99
        order.add_item(sample_product, 1)
        order.add_item(sample_digital_product, 3)
        
        # Act
        total = order.calculate_total()
        
        # Assert
        expected_total = round(sample_product.price * 1 + sample_digital_product.price * 3, 2) # 1200 + 149.97 = 1349.97
        assert total == expected_total

    def test_calculate_total_price_at_purchase_used(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        original_price = sample_product.price
        order.add_item(sample_product, 1)
        
        # Act: Change product price AFTER adding to order
        sample_product.price = 100.00 
        total = order.calculate_total()
        
        # Assert: Total should use price at time of purchase
        assert total == original_price

    def test_update_status_ok(self, sample_order):
        # Arrange
        order = sample_order
        new_status = "processing"
        
        # Act
        order.update_status(new_status)
        
        # Assert
        assert order.status == new_status
        assert not order._is_finalized # processing does not finalize

    @pytest.mark.parametrize("status", ["shipped", "delivered", "cancelled", "refunded"])
    def test_update_status_finalizes_order(self, sample_order, status):
        # Arrange
        order = sample_order
        # Act
        order.update_status(status)
        # Assert
        assert order.status == status
        assert order._is_finalized

    def test_update_status_invalid_type(self, sample_order):
        # Arrange & Act & Assert
        with pytest.raises(TypeError, match="New status must be a string."):
            sample_order.update_status(123)

    def test_update_status_invalid_value(self, sample_order):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invalid order status 'unknown_status'."):
            sample_order.update_status("unknown_status")

    def test_update_status_from_delivered_to_refunded_ok(self, sample_order):
        # Arrange
        order = sample_order
        order.status = "delivered"
        order._is_finalized = True
        
        # Act
        order.update_status("refunded")
        
        # Assert
        assert order.status == "refunded"

    def test_update_status_from_delivered_to_pending_fail(self, sample_order):
        # Arrange
        order = sample_order
        order.status = "delivered"
        order._is_finalized = True

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot change status from 'delivered' to 'pending'."):
            sample_order.update_status("pending")

    def test_update_status_from_cancelled_fail(self, sample_order):
        # Arrange
        order = sample_order
        order.status = "cancelled"
        order._is_finalized = True
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot change status of a 'cancelled' order."):
            sample_order.update_status("pending")

    def test_get_order_summary(self, sample_order, sample_product, sample_digital_product):
        # Arrange
        order = sample_order
        order.customer_id = "cust_summary_test"
        # sample_product: price 1200.00, name "Test Laptop"
        # sample_digital_product: price 49.99, name "Test Software"
        order.add_item(sample_product, 1)
        order.add_item(sample_digital_product, 2)
        
        # Act
        summary = order.get_order_summary()
        
        # Assert
        assert summary["order_id"] == order.order_id
        assert summary["customer_id"] == "cust_summary_test"
        assert summary["status"] == "pending"
        assert summary["total_items"] == 3 # 1 + 2
        assert summary["total_cost"] == round(1200.00 + (49.99 * 2), 2) # 1200 + 99.98 = 1299.98
        
        assert len(summary["items"]) == 2
        item_ids = [item["product_id"] for item in summary["items"]]
        assert sample_product.product_id in item_ids
        assert sample_digital_product.product_id in item_ids

        for item_summary in summary["items"]:
            if item_summary["product_id"] == sample_product.product_id:
                assert item_summary["name"] == sample_product.name
                assert item_summary["quantity"] == 1
                assert item_summary["unit_price"] == sample_product.price
                assert item_summary["subtotal"] == round(sample_product.price * 1, 2)
            elif item_summary["product_id"] == sample_digital_product.product_id:
                assert item_summary["name"] == sample_digital_product.name
                assert item_summary["quantity"] == 2
                assert item_summary["unit_price"] == sample_digital_product.price
                assert item_summary["subtotal"] == round(sample_digital_product.price * 2, 2)

    def test_finalize_order_ok(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        order.add_item(sample_product, 1) # Add an item so it's not empty
        assert order.status == "pending"
        assert not order._is_finalized
        
        # Act
        order.finalize_order()
        
        # Assert
        assert order._is_finalized
        assert order.status == "awaiting_payment"

    def test_finalize_order_empty(self, sample_order):
        # Arrange
        # sample_order is empty by default
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot finalize an empty order."):
            sample_order.finalize_order()

    def test_finalize_order_already_not_pending_status(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        order.add_item(sample_product, 1)
        order.update_status("processing") # Status is not 'pending'
        
        # Act
        order.finalize_order()
        
        # Assert
        assert order._is_finalized # Still finalizes
        assert order.status == "processing" # Status remains unchanged if not 'pending'

    def test_order_repr(self, sample_order, sample_product):
        # Arrange
        order = sample_order
        order.add_item(sample_product, 2) # Price 1200, total 2400
        
        # Act
        representation = repr(order)
        
        # Assert
        expected_repr = f"Order(id='{order.order_id}', status='pending', items=1, total={2400.00})"
        assert representation == expected_repr
