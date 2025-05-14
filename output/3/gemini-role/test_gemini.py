import sys
sys.path.append("..")

import pytest
import uuid
import re
from decimal import Decimal, ROUND_HALF_UP

# Assuming code_normal.py is in the same directory or accessible via PYTHONPATH
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# --- Helper Functions (if any, though pytest fixtures are preferred) ---

# --- Fixtures ---

@pytest.fixture
def basic_product_data():
    """Provides basic valid data for a Product."""
    return {"name": "Test Product", "price": 100.0, "quantity": 10}

@pytest.fixture
def product(basic_product_data):
    """A basic Product instance."""
    return Product(**basic_product_data)

@pytest.fixture
def digital_product_data(basic_product_data):
    """Provides valid data for a DigitalProduct."""
    data = basic_product_data.copy()
    data.update({
        "download_link": "https://example.com/download/item.zip",
        "file_size_mb": 50.5,
        "quantity": 1 # Digital products often default to 1 or are unique
    })
    return data

@pytest.fixture
def digital_product(digital_product_data):
    """A DigitalProduct instance."""
    return DigitalProduct(**digital_product_data)

@pytest.fixture
def physical_product_data(basic_product_data):
    """Provides valid data for a PhysicalProduct."""
    data = basic_product_data.copy()
    data.update({
        "weight_kg": 2.5,
        "shipping_dimensions": (30, 20, 10) # L, W, H in cm
    })
    return data

@pytest.fixture
def physical_product(physical_product_data):
    """A PhysicalProduct instance."""
    return PhysicalProduct(**physical_product_data)

@pytest.fixture
def empty_inventory():
    """An empty Inventory instance."""
    return Inventory()

@pytest.fixture
def inventory_with_products(empty_inventory, product, digital_product, physical_product):
    """An Inventory instance populated with various products."""
    inv = empty_inventory
    # Create distinct products for inventory
    p1 = Product(name="Laptop Pro", price=1200.00, quantity=5)
    p2 = DigitalProduct(name="OS License", price=150.00, download_link="https://example.com/os", file_size_mb=20.0)
    p3 = PhysicalProduct(name="Desk Chair", price=250.00, weight_kg=15, shipping_dimensions=(60,60,90), quantity=3)
    
    inv.add_product(p1)
    inv.add_product(p2) # quantity will be 1 (default for DigitalProduct)
    inv.add_product(p3)
    return inv

@pytest.fixture
def empty_order():
    """An empty Order instance."""
    return Order(customer_id="cust_test_123")


# --- Test Classes ---

class TestProduct:
    def test_product_creation_valid(self, basic_product_data):
        # Arrange
        name, price, quantity = basic_product_data["name"], basic_product_data["price"], basic_product_data["quantity"]
        
        # Act
        p = Product(name, price, quantity=quantity)
        
        # Assert
        assert p.name == name
        assert p.price == float(price)
        assert p.quantity == quantity
        assert isinstance(uuid.UUID(p.product_id, version=4), uuid.UUID)

    def test_product_creation_with_id(self):
        # Arrange
        custom_id = "custom_product_id_123"
        
        # Act
        p = Product("Test", 10.0, product_id=custom_id)
        
        # Assert
        assert p.product_id == custom_id

    @pytest.mark.parametrize(
        "name, price, quantity, product_id, error_type, error_msg_regex",
        [
            ("", 10.0, 5, None, TypeError, "Product name must be a non-empty string."),
            ("  ", 10.0, 5, None, TypeError, "Product name must be a non-empty string."),
            (123, 10.0, 5, None, TypeError, "Product name must be a non-empty string."),
            ("Valid Name", 0, 5, None, ValueError, "Product price must be a positive number."),
            ("Valid Name", -10, 5, None, ValueError, "Product price must be a positive number."),
            ("Valid Name", "invalid", 5, None, TypeError, "Product price must be a positive number."),
            ("Valid Name", 10.0, -1, None, ValueError, "Product quantity must be a non-negative integer."),
            ("Valid Name", 10.0, "invalid", None, ValueError, "Product quantity must be a non-negative integer."),
            ("Valid Name", 10.0, 5, 12345, TypeError, "Product ID must be a string if provided."),
        ]
    )
    def test_product_creation_invalid_inputs(self, name, price, quantity, product_id, error_type, error_msg_regex):
        # Arrange & Act & Assert
        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            Product(name, price, product_id=product_id, quantity=quantity)

    def test_get_details(self, product):
        # Arrange
        expected_details = {
            "product_id": product.product_id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity,
            "type": "GenericProduct"
        }
        # Act
        details = product.get_details()
        # Assert
        assert details == expected_details

    @pytest.mark.parametrize(
        "initial_qty, change, expected_qty",
        [
            (10, 5, 15),
            (10, -5, 5),
            (10, -10, 0),
        ]
    )
    def test_update_quantity_valid(self, product, initial_qty, change, expected_qty):
        # Arrange
        product.quantity = initial_qty
        # Act
        product.update_quantity(change)
        # Assert
        assert product.quantity == expected_qty

    @pytest.mark.parametrize(
        "change, error_type, error_msg_regex",
        [
            ("invalid", TypeError, "Quantity change must be an integer."),
            (-11, ValueError, "Quantity cannot be reduced below zero."), # Assuming initial quantity of 10
        ]
    )
    def test_update_quantity_invalid(self, product, change, error_type, error_msg_regex):
        # Arrange
        product.quantity = 10
        # Act & Assert
        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            product.update_quantity(change)
    
    @pytest.mark.parametrize(
        "initial_price, discount_percent, expected_price",
        [
            (100.0, 10, 90.0),
            (100.0, 0, 100.0),
            (100.0, 100, 0.0),
            (99.99, 10, 89.99), # Test rounding
            (33.33, 10, 30.0), # 33.33 * 0.1 = 3.333 -> 3.33. 33.33 - 3.33 = 30.00
        ]
    )
    def test_apply_discount_valid(self, product, initial_price, discount_percent, expected_price):
        # Arrange
        product.price = initial_price
        # Act
        product.apply_discount(discount_percent)
        # Assert
        assert product.price == pytest.approx(expected_price)

    @pytest.mark.parametrize(
        "discount, error_type, error_msg_regex",
        [
            ("invalid", TypeError, "Discount percentage must be a number."),
            (-10, ValueError, "Discount percentage must be between 0 and 100."),
            (110, ValueError, "Discount percentage must be between 0 and 100."),
        ]
    )
    def test_apply_discount_invalid(self, product, discount, error_type, error_msg_regex):
        # Act & Assert
        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            product.apply_discount(discount)

    def test_product_repr(self, product):
        # Arrange
        # Act
        representation = repr(product)
        # Assert
        assert product.name in representation
        assert str(product.price) in representation
        assert product.product_id in representation
        assert str(product.quantity) in representation
        assert "Product(" in representation


class TestDigitalProduct:
    def test_digital_product_creation_valid(self, digital_product_data):
        # Arrange
        # Act
        dp = DigitalProduct(**digital_product_data)
        # Assert
        assert dp.name == digital_product_data["name"]
        assert dp.price == float(digital_product_data["price"])
        assert dp.download_link == digital_product_data["download_link"]
        assert dp.file_size_mb == float(digital_product_data["file_size_mb"])
        assert dp.quantity == digital_product_data["quantity"] # Check quantity, default for DigitalProduct is 1
        assert isinstance(uuid.UUID(dp.product_id, version=4), uuid.UUID)

    def test_digital_product_creation_default_quantity(self, basic_product_data):
        # Arrange
        data = basic_product_data.copy()
        data.pop("quantity", None) # Remove quantity to test default
        data["download_link"] = "https://example.com/file"
        data["file_size_mb"] = 10.0
        # Act
        dp = DigitalProduct(**data)
        # Assert
        assert dp.quantity == 1

    @pytest.mark.parametrize(
        "link, size_mb, error_type, error_msg_regex",
        [
            ("ftp://invalid.com", 50.0, TypeError, "Download link must be a valid URL string starting with http:// or https://."),
            ("http://valid.com", 0, ValueError, "File size must be a positive number."),
            ("http://valid.com", -5.0, ValueError, "File size must be a positive number."),
            ("http://valid.com", "invalid_size", ValueError, "File size must be a positive number."), # This will be caught by float conversion first then the check
            (123, 50.0, TypeError, "Download link must be a valid URL string starting with http:// or https://."),
        ]
    )
    def test_digital_product_creation_invalid_specifics(self, basic_product_data, link, size_mb, error_type, error_msg_regex):
        # Arrange
        name = basic_product_data["name"]
        price = basic_product_data["price"]
        # Act & Assert
        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            DigitalProduct(name, price, download_link=link, file_size_mb=size_mb)

    def test_get_details_digital(self, digital_product):
        # Arrange
        # Act
        details = digital_product.get_details()
        # Assert
        assert details["type"] == "DigitalProduct"
        assert details["download_link"] == digital_product.download_link
        assert details["file_size_mb"] == digital_product.file_size_mb
        assert details["name"] == digital_product.name # Check inherited fields

    def test_generate_new_download_link(self, digital_product):
        # Arrange
        base_url = "https://newstore.com/downloads"
        old_link = digital_product.download_link
        # Act
        new_link = digital_product.generate_new_download_link(base_url)
        # Assert
        assert new_link != old_link
        assert new_link.startswith(f"{base_url.rstrip('/')}/{digital_product.product_id}/download_")
        assert digital_product.download_link == new_link

    def test_generate_new_download_link_invalid_base_url(self, digital_product):
        # Arrange
        # Act & Assert
        with pytest.raises(TypeError, match="Base URL must be a non-empty string."):
            digital_product.generate_new_download_link("  ")

    def test_digital_product_repr(self, digital_product):
        representation = repr(digital_product)
        assert "DigitalProduct(" in representation
        assert f"link='{digital_product.download_link}'" in representation


class TestPhysicalProduct:
    def test_physical_product_creation_valid(self, physical_product_data):
        # Arrange
        # Act
        pp = PhysicalProduct(**physical_product_data)
        # Assert
        assert pp.name == physical_product_data["name"]
        assert pp.weight_kg == float(physical_product_data["weight_kg"])
        assert pp.shipping_dimensions == physical_product_data["shipping_dimensions"]
        assert pp.quantity == physical_product_data["quantity"]

    @pytest.mark.parametrize(
        "weight, dims, error_type, error_msg_regex",
        [
            (0, (1,1,1), ValueError, "Weight must be a positive number."),
            (-1.0, (1,1,1), ValueError, "Weight must be a positive number."),
            ("invalid", (1,1,1), ValueError, "Weight must be a positive number."),
            (1.0, (1,1), TypeError, "Shipping dimensions must be a tuple of three positive numbers"), # Wrong length
            (1.0, (1,1,0), TypeError, "Shipping dimensions must be a tuple of three positive numbers"), # Non-positive dim
            (1.0, (1,1,"a"), TypeError, "Shipping dimensions must be a tuple of three positive numbers"), # Non-numeric dim
            (1.0, "invalid", TypeError, "Shipping dimensions must be a tuple of three positive numbers"), # Not a tuple
        ]
    )
    def test_physical_product_creation_invalid_specifics(self, basic_product_data, weight, dims, error_type, error_msg_regex):
        # Arrange
        name = basic_product_data["name"]
        price = basic_product_data["price"]
        # Act & Assert
        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            PhysicalProduct(name, price, weight_kg=weight, shipping_dimensions=dims)
    
    def test_get_details_physical(self, physical_product):
        # Arrange
        # Act
        details = physical_product.get_details()
        # Assert
        assert details["type"] == "PhysicalProduct"
        assert details["weight_kg"] == physical_product.weight_kg
        assert details["shipping_dimensions_cm"] == physical_product.shipping_dimensions

    @pytest.mark.parametrize(
        "weight, dims, rate_per_kg, volumetric_factor, expected_cost",
        [
            (2.5, (30,20,10), 5.0, 5000, 12.5), # Actual weight: 2.5kg, Volumetric: (30*20*10)/5000 = 1.2kg. Chargeable: 2.5kg. Cost: 2.5 * 5 = 12.5
            (1.0, (50,40,30), 5.0, 5000, 60.0), # Actual weight: 1.0kg, Volumetric: (50*40*30)/5000 = 12kg. Chargeable: 12kg. Cost: 12 * 5 = 60.0
            (10.0, (10,10,10), 2.5, 6000, 25.0) # Actual: 10kg, Volumetric: 1000/6000 = 0.166..kg. Chargeable: 10kg. Cost: 10 * 2.5 = 25.0
        ]
    )
    def test_calculate_shipping_cost_valid(self, physical_product, weight, dims, rate_per_kg, volumetric_factor, expected_cost):
        # Arrange
        physical_product.weight_kg = weight
        physical_product.shipping_dimensions = dims
        # Act
        cost = physical_product.calculate_shipping_cost(rate_per_kg, volumetric_factor)
        # Assert
        assert cost == pytest.approx(expected_cost)

    @pytest.mark.parametrize(
        "rate, factor, error_type, error_msg_regex",
        [
            (0, 5000, ValueError, "Rate per kg must be a positive number."),
            (-5, 5000, ValueError, "Rate per kg must be a positive number."),
            ("invalid", 5000, ValueError, "Rate per kg must be a positive number."),
            (5, 0, ValueError, "Volumetric factor must be a positive integer."),
            (5, -5000, ValueError, "Volumetric factor must be a positive integer."),
            (5, "invalid", ValueError, "Volumetric factor must be a positive integer."),
        ]
    )
    def test_calculate_shipping_cost_invalid_params(self, physical_product, rate, factor, error_type, error_msg_regex):
        # Act & Assert
        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            physical_product.calculate_shipping_cost(rate, factor)

    def test_physical_product_repr(self, physical_product):
        representation = repr(physical_product)
        assert "PhysicalProduct(" in representation
        assert f"weight={physical_product.weight_kg}kg" in representation


class TestInventory:
    def test_inventory_initialization(self, empty_inventory):
        # Assert
        assert empty_inventory.products == {}

    def test_add_product_new(self, empty_inventory, product):
        # Arrange
        # Act
        empty_inventory.add_product(product, initial_stock=5)
        # Assert
        assert product.product_id in empty_inventory.products
        assert empty_inventory.products[product.product_id] == product
        assert empty_inventory.get_stock_level(product.product_id) == 5
        assert product.quantity == 5 # Product's quantity should be updated

    def test_add_product_uses_product_quantity_if_initial_stock_none(self, empty_inventory, product):
        # Arrange
        product.quantity = 7
        # Act
        empty_inventory.add_product(product)
        # Assert
        assert product.product_id in empty_inventory.products
        assert empty_inventory.get_stock_level(product.product_id) == 7

    def test_add_product_type_error(self, empty_inventory):
        # Act & Assert
        with pytest.raises(TypeError, match="Item to add must be an instance of Product."):
            empty_inventory.add_product("not a product")

    def test_add_product_duplicate_id_error(self, empty_inventory, product):
        # Arrange
        empty_inventory.add_product(product)
        # Act & Assert
        with pytest.raises(ValueError, match=f"Product with ID {product.product_id} already exists in inventory."):
            empty_inventory.add_product(product) # Adding same product instance

    def test_add_product_invalid_initial_stock(self, empty_inventory, product):
        # Act & Assert
        with pytest.raises(ValueError, match="Initial stock must be a non-negative integer."):
            empty_inventory.add_product(product, initial_stock=-1)

    def test_remove_product_existing(self, inventory_with_products, product):
        # Arrange
        # Need a product that's actually in inventory_with_products fixture
        p_to_remove = inventory_with_products.find_products_by_name("Laptop Pro")[0]
        pid_to_remove = p_to_remove.product_id
        
        # Act
        removed_product = inventory_with_products.remove_product(pid_to_remove)
        # Assert
        assert removed_product == p_to_remove
        assert pid_to_remove not in inventory_with_products.products

    def test_remove_product_non_existent_id(self, empty_inventory):
        # Act & Assert
        with pytest.raises(KeyError, match="Product with ID non_existent_id not found in inventory."):
            empty_inventory.remove_product("non_existent_id")

    def test_remove_product_invalid_id_type(self, empty_inventory):
        # Act & Assert
        with pytest.raises(TypeError, match="Product ID must be a string."):
            empty_inventory.remove_product(123)

    def test_get_product_existing(self, inventory_with_products):
        # Arrange
        p_expected = inventory_with_products.find_products_by_name("OS License")[0]
        pid_to_get = p_expected.product_id
        # Act
        retrieved_product = inventory_with_products.get_product(pid_to_get)
        # Assert
        assert retrieved_product == p_expected

    def test_get_product_non_existent_id(self, empty_inventory):
        # Act & Assert
        with pytest.raises(KeyError, match="Product with ID non_existent_id not found in inventory."):
            empty_inventory.get_product("non_existent_id")

    def test_update_stock_valid(self, inventory_with_products):
        # Arrange
        p_to_update = inventory_with_products.find_products_by_name("Laptop Pro")[0]
        pid = p_to_update.product_id
        initial_stock = p_to_update.quantity
        
        # Act: Increase stock
        inventory_with_products.update_stock(pid, 3)
        # Assert
        assert inventory_with_products.get_stock_level(pid) == initial_stock + 3

        # Act: Decrease stock
        inventory_with_products.update_stock(pid, -2)
        # Assert
        assert inventory_with_products.get_stock_level(pid) == initial_stock + 3 - 2

    def test_update_stock_insufficient(self, inventory_with_products):
        # Arrange
        p_to_update = inventory_with_products.find_products_by_name("Desk Chair")[0] # Has 3
        pid = p_to_update.product_id
        # Act & Assert
        with pytest.raises(ValueError, match=f"Stock update for {pid} failed: Quantity cannot be reduced below zero."):
            inventory_with_products.update_stock(pid, -10) # Initial stock is 3

    def test_get_total_inventory_value(self, empty_inventory, product, digital_product):
        # Arrange
        assert empty_inventory.get_total_inventory_value() == 0.0

        p1 = Product("Item A", 10.0, quantity=3) # Value 30
        p2 = DigitalProduct("Item B", 25.0, download_link="http://a.b/c", file_size_mb=1, quantity=2) # Value 50, DigitalProduct default quantity is 1, but explicit here.
        
        empty_inventory.add_product(p1)
        empty_inventory.add_product(p2)

        # Act
        total_value = empty_inventory.get_total_inventory_value()
        # Assert
        assert total_value == pytest.approx(10.0 * 3 + 25.0 * 2) # 30 + 50 = 80

    def test_find_products_by_name(self, inventory_with_products):
        # Arrange
        # inventory_with_products has: "Laptop Pro", "OS License", "Desk Chair"
        
        # Act & Assert (Case-insensitive default)
        results = inventory_with_products.find_products_by_name("laptop")
        assert len(results) == 1
        assert results[0].name == "Laptop Pro"

        results = inventory_with_products.find_products_by_name("os lIcEnSe")
        assert len(results) == 1
        assert results[0].name == "OS License"

        # Act & Assert (Case-sensitive)
        results = inventory_with_products.find_products_by_name("laptop", case_sensitive=True)
        assert len(results) == 0 
        results = inventory_with_products.find_products_by_name("Laptop", case_sensitive=True)
        assert len(results) == 1

        # Act & Assert (Partial match)
        results = inventory_with_products.find_products_by_name("pro")
        assert len(results) == 1
        assert results[0].name == "Laptop Pro"

        # Act & Assert (No match)
        results = inventory_with_products.find_products_by_name("nonexistent")
        assert len(results) == 0
        
        # Act & Assert (Empty search term returns all)
        all_products = list(inventory_with_products.products.values())
        results = inventory_with_products.find_products_by_name("")
        assert len(results) == len(all_products)
        assert set(results) == set(all_products)


    def test_find_products_by_name_type_error(self, empty_inventory):
        with pytest.raises(TypeError, match="Search term must be a string."):
            empty_inventory.find_products_by_name(123)

    def test_get_products_in_price_range(self, inventory_with_products):
        # Laptop Pro: 1200, OS License: 150, Desk Chair: 250
        # Act & Assert
        results = inventory_with_products.get_products_in_price_range(min_price=200, max_price=1000)
        assert len(results) == 1
        assert results[0].name == "Desk Chair"

        results = inventory_with_products.get_products_in_price_range(max_price=200) # min_price defaults to 0
        assert len(results) == 1
        assert results[0].name == "OS License"

        results = inventory_with_products.get_products_in_price_range(min_price=500) # max_price defaults to inf
        assert len(results) == 1
        assert results[0].name == "Laptop Pro"

        results = inventory_with_products.get_products_in_price_range() # All products
        assert len(results) == 3
        
        results = inventory_with_products.get_products_in_price_range(min_price=150, max_price=250) # Boundary inclusive
        product_names = sorted([p.name for p in results])
        assert product_names == sorted(["OS License", "Desk Chair"])


    @pytest.mark.parametrize(
        "min_p, max_p, error_type, error_msg_regex",
        [
            (-1, 100, ValueError, "Minimum price must be a non-negative number."),
            ("invalid", 100, ValueError, "Minimum price must be a non-negative number."),
            (100, 50, ValueError, "Maximum price must be a number greater than or equal to minimum price."),
            (100, "invalid", ValueError, "Maximum price must be a number greater than or equal to minimum price."),
        ]
    )
    def test_get_products_in_price_range_invalid(self, empty_inventory, min_p, max_p, error_type, error_msg_regex):
        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            empty_inventory.get_products_in_price_range(min_price=min_p, max_price=max_p)


class TestOrder:
    def test_order_creation_valid(self):
        # Arrange
        customer_id = "cust456"
        order_id = "order_abc"
        # Act
        order = Order(order_id=order_id, customer_id=customer_id)
        # Assert
        assert order.order_id == order_id
        assert order.customer_id == customer_id
        assert order.status == "pending"
        assert not order._is_finalized
        assert order.items == {}

    def test_order_creation_default_id(self):
        # Arrange & Act
        order = Order()
        # Assert
        assert isinstance(uuid.UUID(order.order_id, version=4), uuid.UUID)
        assert order.customer_id is None

    @pytest.mark.parametrize("order_id, customer_id, error_type, error_msg_regex", [
        (123, "cust", TypeError, "Order ID must be a string if provided."),
        ("ord", 456, TypeError, "Customer ID must be a string if provided."),
    ])
    def test_order_creation_invalid_ids(self, order_id, customer_id, error_type, error_msg_regex):
        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            Order(order_id=order_id, customer_id=customer_id)

    def test_add_item_new_no_inventory(self, empty_order, product):
        # Arrange
        product.price = 25.0 # Set price for test
        # Act
        empty_order.add_item(product, quantity=2)
        # Assert
        assert len(empty_order.items) == 1
        item_data = empty_order.items[product.product_id]
        assert item_data["quantity"] == 2
        assert item_data["price_at_purchase"] == 25.0
        assert item_data["product_snapshot"]["name"] == product.name
        assert item_data["product_snapshot"]["type"] == "Product" # Class name

    def test_add_item_existing_no_inventory(self, empty_order, product):
        # Arrange
        product.price = 25.0
        empty_order.add_item(product, quantity=1)
        # Act
        empty_order.add_item(product, quantity=2) # Add more of the same
        # Assert
        assert empty_order.items[product.product_id]["quantity"] == 3

    def test_add_item_with_inventory_sufficient_stock(self, empty_order, inventory_with_products):
        # Arrange
        p_from_inv = inventory_with_products.find_products_by_name("Laptop Pro")[0] # Stock 5
        initial_inv_stock = p_from_inv.quantity
        # Act
        empty_order.add_item(p_from_inv, quantity=2, inventory=inventory_with_products)
        # Assert
        assert empty_order.items[p_from_inv.product_id]["quantity"] == 2
        assert inventory_with_products.get_stock_level(p_from_inv.product_id) == initial_inv_stock - 2
    
    def test_add_item_with_inventory_insufficient_stock(self, empty_order, inventory_with_products):
        # Arrange
        p_from_inv = inventory_with_products.find_products_by_name("Desk Chair")[0] # Stock 3
        # Act & Assert
        with pytest.raises(ValueError, match=f"Not enough stock for {p_from_inv.name}.*Requested: 5, Available: 3"):
            empty_order.add_item(p_from_inv, quantity=5, inventory=inventory_with_products)

    def test_add_item_finalized_order(self, empty_order, product):
        # Arrange
        empty_order.finalize_order() # Finalizes, sets status to awaiting_payment
        # Act & Assert
        with pytest.raises(RuntimeError, match="Cannot add items to a finalized order."):
            empty_order.add_item(product, 1)

    @pytest.mark.parametrize("item, quantity, inventory, error_type, error_msg_regex", [
        ("not a product", 1, None, TypeError, "Item to add must be an instance of Product."),
        (Product("temp",1), 0, None, ValueError, "Quantity must be a positive integer."),
        (Product("temp",1), -1, None, ValueError, "Quantity must be a positive integer."),
        (Product("temp",1), 1, "not inventory", TypeError, "Inventory must be an Inventory instance."),
    ])
    def test_add_item_invalid_inputs(self, empty_order, item, quantity, inventory, error_type, error_msg_regex):
        # Create a fresh product for parameterization as product fixture can't be used directly in parametrize
        if isinstance(item, str) and item == "not a product":
            pass # Use the string directly
        elif isinstance(item, Product) and inventory == "not inventory":
            # For this specific case, ensure product is in a dummy inventory for other checks to pass first
            dummy_inv = Inventory()
            dummy_inv.add_product(item, initial_stock=5)
        elif isinstance(item, Product):
             # For quantity checks, product is fine as is
             pass

        with pytest.raises(error_type, match=re.escape(error_msg_regex)):
            empty_order.add_item(item, quantity, inventory=inventory)

    def test_remove_item_partial_no_inventory(self, empty_order, product):
        # Arrange
        empty_order.add_item(product, quantity=5)
        # Act
        empty_order.remove_item(product.product_id, quantity_to_remove=2)
        # Assert
        assert empty_order.items[product.product_id]["quantity"] == 3

    def test_remove_item_full_no_inventory(self, empty_order, product):
        # Arrange
        empty_order.add_item(product, quantity=2)
        # Act
        empty_order.remove_item(product.product_id, quantity_to_remove=2)
        # Assert
        assert product.product_id not in empty_order.items

    def test_remove_item_with_inventory_restock(self, empty_order, inventory_with_products):
        # Arrange
        p_from_inv = inventory_with_products.find_products_by_name("Laptop Pro")[0] # Stock 5
        empty_order.add_item(p_from_inv, quantity=3, inventory=inventory_with_products) # Stock becomes 2
        current_inv_stock = inventory_with_products.get_stock_level(p_from_inv.product_id) # Should be 2
        
        # Act
        empty_order.remove_item(p_from_inv.product_id, quantity_to_remove=1, inventory=inventory_with_products)
        # Assert
        assert empty_order.items[p_from_inv.product_id]["quantity"] == 2
        assert inventory_with_products.get_stock_level(p_from_inv.product_id) == current_inv_stock + 1 # Should be 3

    def test_remove_item_finalized_order_disallowed_status(self, empty_order, product):
        empty_order.add_item(product, 1)
        empty_order.update_status("shipped") # This finalizes the order
        with pytest.raises(RuntimeError, match="Cannot remove items from an order with status 'shipped'."):
            empty_order.remove_item(product.product_id, 1)

    def test_remove_item_finalized_order_allowed_status(self, empty_order, product):
        empty_order.add_item(product, 1)
        empty_order.update_status("pending") # Not finalized yet
        empty_order._is_finalized = True # Manually set for test scenario
        # Act & Assert: Should pass for "pending" even if _is_finalized is true by some logic
        empty_order.remove_item(product.product_id, 1)
        assert product.product_id not in empty_order.items

    @pytest.mark.parametrize("product_id, quantity, inventory, error_type, error_msg_regex_part", [
        (123, 1, None, TypeError, "Product ID must be a string."),
        ("pid", 0, None, ValueError, "Quantity to remove must be a positive integer."),
        ("pid", -1, None, ValueError, "Quantity to remove must be a positive integer."),
        ("non_existent_pid", 1, None, KeyError, "Product with ID non_existent_pid not found in order."),
        # ValueError for removing too many is tested below.
        # TypeError for inventory is tested below.
    ])
    def test_remove_item_invalid_inputs(self, empty_order, product, product_id, quantity, inventory, error_type, error_msg_regex_part):
        empty_order.add_item(product, 2) # Add a known product
        test_pid = product.product_id if product_id == "pid" else product_id

        with pytest.raises(error_type, match=re.escape(error_msg_regex_part)):
            empty_order.remove_item(test_pid, quantity, inventory=inventory)

    def test_remove_item_too_many(self, empty_order, product):
        empty_order.add_item(product, 2)
        with pytest.raises(ValueError, match=f"Cannot remove 3 units of {product.product_id}; only 2 in order."):
            empty_order.remove_item(product.product_id, 3)
            
    def test_remove_item_inventory_type_error(self, empty_order, product):
        empty_order.add_item(product, 1)
        with pytest.raises(TypeError, match="Inventory must be an Inventory instance."):
            empty_order.remove_item(product.product_id, 1, inventory="not_inventory")

    def test_remove_item_inventory_restock_product_not_found_error(self, empty_order, product, inventory_with_products):
        # This tests the specific RuntimeError if a product exists in order,
        # inventory object is passed, but the product is somehow GONE from inventory
        # when trying to restock.
        
        # Add product to order from inventory (reducing its stock)
        p_original = inventory_with_products.find_products_by_name("Laptop Pro")[0]
        empty_order.add_item(p_original, 1, inventory_with_products)
        
        # Now, remove it from inventory directly (simulating an inconsistent state)
        inventory_with_products.remove_product(p_original.product_id)
        
        with pytest.raises(RuntimeError, match=f"Product {p_original.product_id} not found in inventory for restocking. Inconsistent state."):
            empty_order.remove_item(p_original.product_id, 1, inventory=inventory_with_products)


    def test_calculate_total(self, empty_order, product):
        # Arrange
        assert empty_order.calculate_total() == 0.0

        p1 = Product("A", 10.50)
        p2 = Product("B", 5.25)
        empty_order.add_item(p1, 2) # 2 * 10.50 = 21.00
        empty_order.add_item(p2, 3) # 3 * 5.25 = 15.75
        
        # Act
        total = empty_order.calculate_total()
        # Assert
        assert total == pytest.approx(21.00 + 15.75)

    def test_calculate_total_uses_price_at_purchase(self, empty_order, product):
        # Arrange
        product.price = 50.0
        empty_order.add_item(product, 1) # Price at purchase is 50.0

        product.price = 60.0 # Change product price *after* adding to order
        
        # Act
        total = empty_order.calculate_total()
        # Assert
        assert total == pytest.approx(50.0) # Should use the 50.0 price

    @pytest.mark.parametrize("new_status, expected_finalized_state_after", [
        ("processing", False),
        ("shipped", True),
        ("delivered", True),
        ("cancelled", True),
        ("refunded", True),
        ("awaiting_payment", False),
    ])
    def test_update_status_valid_transitions_and_finalization(self, empty_order, new_status, expected_finalized_state_after):
        # Arrange
        initial_status = empty_order.status # pending
        # Act
        empty_order.update_status(new_status)
        # Assert
        assert empty_order.status == new_status
        assert empty_order._is_finalized == expected_finalized_state_after

    @pytest.mark.parametrize("current_status, new_status, error_type, error_msg_regex_part", [
        ("pending", "invalid_status", ValueError, "Invalid order status 'invalid_status'."),
        ("delivered", "processing", ValueError, "Cannot change status from 'delivered' to 'processing'."),
        ("cancelled", "pending", ValueError, "Cannot change status of a 'cancelled' order."),
        ("pending", 123, TypeError, "New status must be a string."),
    ])
    def test_update_status_invalid_transitions(self, empty_order, current_status, new_status, error_type, error_msg_regex_part):
        empty_order.status = current_status # Set initial state for test
        if current_status in ["delivered", "cancelled"]: # these statuses also set _is_finalized
             empty_order._is_finalized = True
        
        with pytest.raises(error_type, match=error_msg_regex_part):
            empty_order.update_status(new_status)

    def test_get_order_summary(self, empty_order, product):
        # Arrange
        p1 = Product("Item X", 100.00)
        p2 = Product("Item Y", 25.50)
        empty_order.customer_id = "cust_summary"
        empty_order.add_item(p1, 2)
        empty_order.add_item(p2, 1)
        empty_order.update_status("processing")

        # Act
        summary = empty_order.get_order_summary()

        # Assert
        assert summary["order_id"] == empty_order.order_id
        assert summary["customer_id"] == "cust_summary"
        assert summary["status"] == "processing"
        assert summary["total_items"] == 3 # 2 of p1, 1 of p2
        assert summary["total_cost"] == pytest.approx(100.00 * 2 + 25.50 * 1)
        
        assert len(summary["items"]) == 2
        item_summary_p1 = next(item for item in summary["items"] if item["product_id"] == p1.product_id)
        assert item_summary_p1["name"] == p1.name
        assert item_summary_p1["quantity"] == 2
        assert item_summary_p1["unit_price"] == 100.00
        assert item_summary_p1["subtotal"] == pytest.approx(200.00)

    def test_finalize_order_pending_to_awaiting_payment(self, empty_order, product):
        # Arrange
        empty_order.add_item(product, 1)
        assert empty_order.status == "pending"
        assert not empty_order._is_finalized
        # Act
        empty_order.finalize_order()
        # Assert
        assert empty_order.status == "awaiting_payment"
        assert empty_order._is_finalized

    def test_finalize_order_already_processing(self, empty_order, product):
        # Arrange
        empty_order.add_item(product, 1)
        empty_order.update_status("processing")
        assert not empty_order._is_finalized # update_status to 'processing' doesn't finalize
        # Act
        empty_order.finalize_order()
        # Assert
        assert empty_order.status == "processing" # Status should not change from processing
        assert empty_order._is_finalized

    def test_finalize_order_empty_order(self, empty_order):
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot finalize an empty order."):
            empty_order.finalize_order()

    def test_order_repr(self, empty_order, product):
        # Arrange
        empty_order.add_item(product, 1)
        representation = repr(empty_order)
        # Assert
        assert "Order(" in representation
        assert f"id='{empty_order.order_id}'" in representation
        assert f"status='{empty_order.status}'" in representation
        assert f"items={len(empty_order.items)}" in representation
        assert f"total={empty_order.calculate_total()}" in representation
