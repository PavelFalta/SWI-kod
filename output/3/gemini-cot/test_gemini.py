import pytest
import uuid
import sys
sys.path.append("..")
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# Fixtures pro často používané produkty
@pytest.fixture
def generic_product():
    """Fixture for a generic product."""
    return Product(name="Test Book", price=19.99, quantity=10)

@pytest.fixture
def digital_product():
    """Fixture for a digital product."""
    return DigitalProduct(name="E-Book Alpha", price=9.99, 
                          download_link="http://example.com/ebook.pdf", 
                          file_size_mb=5.5)

@pytest.fixture
def physical_product():
    """Fixture for a physical product."""
    return PhysicalProduct(name="Laptop X", price=1200.00, weight_kg=2.5, 
                           shipping_dimensions=(40, 30, 5), quantity=3)

@pytest.fixture
def inventory_instance():
    """Fixture for an Inventory instance."""
    return Inventory()

@pytest.fixture
def order_instance():
    """Fixture for an Order instance."""
    return Order(customer_id="cust123")

class TestProduct:
    def test_product_creation_valid(self):
        """Test valid Product creation."""
        p = Product(name="Test Item", price=10.50, quantity=5)
        assert p.name == "Test Item"
        assert p.price == 10.50
        assert p.quantity == 5
        assert isinstance(uuid.UUID(p.product_id), uuid.UUID) # Check if product_id is a valid UUID

        product_id = "custom-id-123"
        p_custom_id = Product(name="Another Item", price=20.00, product_id=product_id)
        assert p_custom_id.product_id == product_id

    def test_product_creation_invalid_name(self):
        """Test Product creation with invalid name."""
        with pytest.raises(TypeError, match="Product name must be a non-empty string."):
            Product(name=123, price=10.00)
        with pytest.raises(TypeError, match="Product name must be a non-empty string."):
            Product(name="  ", price=10.00)

    def test_product_creation_invalid_price(self):
        """Test Product creation with invalid price."""
        with pytest.raises(ValueError, match="Product price must be a positive number."):
            Product(name="Test", price=-5)
        with pytest.raises(ValueError, match="Product price must be a positive number."):
            Product(name="Test", price=0)
        with pytest.raises(TypeError, match="Product price must be a positive number."):
            Product(name="Test", price="free")

    def test_product_creation_invalid_product_id(self):
        """Test Product creation with invalid product_id type."""
        with pytest.raises(TypeError, match="Product ID must be a string if provided."):
            Product(name="Test", price=10.00, product_id=123)

    def test_product_creation_invalid_quantity(self):
        """Test Product creation with invalid quantity."""
        with pytest.raises(ValueError, match="Product quantity must be a non-negative integer."):
            Product(name="Test", price=10.00, quantity=-1)
        with pytest.raises(TypeError, match="Product quantity must be a non-negative integer."):
            Product(name="Test", price=10.00, quantity="many")

    def test_get_details(self, generic_product):
        """Test get_details method."""
        details = generic_product.get_details()
        assert details["name"] == "Test Book"
        assert details["price"] == 19.99
        assert details["quantity"] == 10
        assert details["product_id"] == generic_product.product_id
        assert details["type"] == "GenericProduct"

    def test_update_quantity_valid(self, generic_product):
        """Test valid quantity updates."""
        generic_product.update_quantity(5)
        assert generic_product.quantity == 15
        generic_product.update_quantity(-10)
        assert generic_product.quantity == 5
        generic_product.update_quantity(-5)
        assert generic_product.quantity == 0

    def test_update_quantity_invalid(self, generic_product):
        """Test invalid quantity updates."""
        with pytest.raises(TypeError, match="Quantity change must be an integer."):
            generic_product.update_quantity("five")
        with pytest.raises(ValueError, match="Quantity cannot be reduced below zero."):
            generic_product.update_quantity(-100) # Current quantity is 10

    def test_apply_discount_valid(self, generic_product):
        """Test valid discount application."""
        # generic_product has price 19.99
        original_price = generic_product.price
        generic_product.apply_discount(10) # 10% discount
        assert generic_product.price == round(original_price * 0.9, 2)
        
        # Reset price for next test
        generic_product.price = 100.00
        generic_product.apply_discount(100) # 100% discount
        assert generic_product.price == 0.00

        generic_product.price = 50.00
        generic_product.apply_discount(0) # 0% discount
        assert generic_product.price == 50.00

    def test_apply_discount_invalid(self, generic_product):
        """Test invalid discount application."""
        with pytest.raises(TypeError, match="Discount percentage must be a number."):
            generic_product.apply_discount("ten")
        with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100."):
            generic_product.apply_discount(-10)
        with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100."):
            generic_product.apply_discount(101)

    def test_product_repr(self, generic_product):
        """Test Product __repr__ method."""
        expected_repr = f"Product(name='Test Book', price=19.99, id='{generic_product.product_id}', quantity=10)"
        assert repr(generic_product) == expected_repr

class TestDigitalProduct:
    def test_digital_product_creation_valid(self):
        """Test valid DigitalProduct creation."""
        dp = DigitalProduct(name="Software Suite", price=99.99, 
                            download_link="https://example.com/soft.zip", 
                            file_size_mb=150.5)
        assert dp.name == "Software Suite"
        assert dp.price == 99.99
        assert dp.download_link == "https://example.com/soft.zip"
        assert dp.file_size_mb == 150.5
        assert dp.quantity == 1 # Default quantity for DigitalProduct

        dp_with_quantity = DigitalProduct(name="Song", price=0.99, 
                                          download_link="http://t.co/song.mp3", 
                                          file_size_mb=3.0, quantity=0) # Explicitly 0
        assert dp_with_quantity.quantity == 0


    def test_digital_product_creation_invalid_link(self):
        """Test DigitalProduct creation with invalid download link."""
        with pytest.raises(TypeError, match="Download link must be a valid URL string starting with http:// or https://."):
            DigitalProduct(name="Test", price=10, download_link="ftp://example.com", file_size_mb=10)
        with pytest.raises(TypeError, match="Download link must be a valid URL string starting with http:// or https://."):
            DigitalProduct(name="Test", price=10, download_link=123, file_size_mb=10)

    def test_digital_product_creation_invalid_filesize(self):
        """Test DigitalProduct creation with invalid file size."""
        with pytest.raises(ValueError, match="File size must be a positive number."):
            DigitalProduct(name="Test", price=10, download_link="http://e.com", file_size_mb=-5)
        with pytest.raises(ValueError, match="File size must be a positive number."):
            DigitalProduct(name="Test", price=10, download_link="http://e.com", file_size_mb=0)
        with pytest.raises(TypeError, match="File size must be a positive number."):
            DigitalProduct(name="Test", price=10, download_link="http://e.com", file_size_mb="large")

    def test_digital_get_details(self, digital_product):
        """Test get_details method for DigitalProduct."""
        details = digital_product.get_details()
        assert details["name"] == "E-Book Alpha"
        assert details["price"] == 9.99
        assert details["download_link"] == "http://example.com/ebook.pdf"
        assert details["file_size_mb"] == 5.5
        assert details["type"] == "DigitalProduct"
        assert "quantity" in details # from base class

    def test_generate_new_download_link(self, digital_product):
        """Test generating a new download link."""
        old_link = digital_product.download_link
        new_link = digital_product.generate_new_download_link("https://newbase.com/downloads")
        assert new_link != old_link
        assert new_link.startswith("https://newbase.com/downloads/")
        assert digital_product.product_id in new_link
        assert "download_" in new_link
        assert digital_product.download_link == new_link

    def test_generate_new_download_link_invalid_base_url(self, digital_product):
        """Test generating new link with invalid base URL."""
        with pytest.raises(TypeError, match="Base URL must be a non-empty string."):
            digital_product.generate_new_download_link("  ")
        with pytest.raises(TypeError, match="Base URL must be a non-empty string."):
            digital_product.generate_new_download_link(123)
            
    def test_digital_product_repr(self, digital_product):
        """Test DigitalProduct __repr__ method."""
        expected_repr = f"DigitalProduct(name='E-Book Alpha', price=9.99, id='{digital_product.product_id}', link='http://example.com/ebook.pdf')"
        assert repr(digital_product) == expected_repr


class TestPhysicalProduct:
    def test_physical_product_creation_valid(self):
        """Test valid PhysicalProduct creation."""
        pp = PhysicalProduct(name="Chair", price=75.00, weight_kg=5.2, 
                             shipping_dimensions=(50, 50, 80), quantity=2)
        assert pp.name == "Chair"
        assert pp.price == 75.00
        assert pp.weight_kg == 5.2
        assert pp.shipping_dimensions == (50, 50, 80)
        assert pp.quantity == 2

    def test_physical_product_creation_invalid_weight(self):
        """Test PhysicalProduct creation with invalid weight."""
        with pytest.raises(ValueError, match="Weight must be a positive number."):
            PhysicalProduct(name="Test", price=10, weight_kg=-1, shipping_dimensions=(1,1,1))
        with pytest.raises(ValueError, match="Weight must be a positive number."):
            PhysicalProduct(name="Test", price=10, weight_kg=0, shipping_dimensions=(1,1,1))
        with pytest.raises(TypeError, match="Weight must be a positive number."):
            PhysicalProduct(name="Test", price=10, weight_kg="heavy", shipping_dimensions=(1,1,1))

    def test_physical_product_creation_invalid_dimensions(self):
        """Test PhysicalProduct creation with invalid shipping dimensions."""
        match_msg = "Shipping dimensions must be a tuple of three positive numbers (length, width, height)."
        with pytest.raises(TypeError, match=match_msg):
            PhysicalProduct(name="Test", price=10, weight_kg=1, shipping_dimensions=[1,1,1]) # Not a tuple
        with pytest.raises(TypeError, match=match_msg):
            PhysicalProduct(name="Test", price=10, weight_kg=1, shipping_dimensions=(1,1)) # Not 3 elements
        with pytest.raises(TypeError, match=match_msg):
            PhysicalProduct(name="Test", price=10, weight_kg=1, shipping_dimensions=(1,1,"one")) # Invalid type in tuple
        with pytest.raises(TypeError, match=match_msg):
            PhysicalProduct(name="Test", price=10, weight_kg=1, shipping_dimensions=(1,1,0)) # Non-positive dimension
        with pytest.raises(TypeError, match=match_msg):
            PhysicalProduct(name="Test", price=10, weight_kg=1, shipping_dimensions=(1,1,-1)) # Non-positive dimension

    def test_physical_get_details(self, physical_product):
        """Test get_details method for PhysicalProduct."""
        details = physical_product.get_details()
        assert details["name"] == "Laptop X"
        assert details["price"] == 1200.00
        assert details["weight_kg"] == 2.5
        assert details["shipping_dimensions_cm"] == (40, 30, 5)
        assert details["type"] == "PhysicalProduct"
        assert "quantity" in details # from base class

    def test_calculate_shipping_cost(self, physical_product):
        """Test shipping cost calculation."""
        # Laptop X: weight=2.5kg, dims=(40,30,5)
        # Volumetric weight = (40*30*5)/5000 = 6000/5000 = 1.2 kg
        # Chargeable weight is max(2.5, 1.2) = 2.5 kg
        cost = physical_product.calculate_shipping_cost(rate_per_kg=10) # 2.5 * 10 = 25
        assert cost == 25.00

        # Change weight to be less than volumetric
        physical_product.weight_kg = 1.0
        # Volumetric weight is 1.2 kg. Chargeable is max(1.0, 1.2) = 1.2 kg
        cost_volumetric = physical_product.calculate_shipping_cost(rate_per_kg=10) # 1.2 * 10 = 12
        assert cost_volumetric == 12.00
        
        # Test with different volumetric factor
        physical_product.weight_kg = 2.5 # Reset weight
        # Volumetric weight = (40*30*5)/6000 = 1 kg
        # Chargeable weight is max(2.5, 1) = 2.5 kg
        cost_custom_factor = physical_product.calculate_shipping_cost(rate_per_kg=10, volumetric_factor=6000)
        assert cost_custom_factor == 25.00

    def test_calculate_shipping_cost_invalid_inputs(self, physical_product):
        """Test shipping cost calculation with invalid inputs."""
        with pytest.raises(ValueError, match="Rate per kg must be a positive number."):
            physical_product.calculate_shipping_cost(rate_per_kg=0)
        with pytest.raises(ValueError, match="Rate per kg must be a positive number."):
            physical_product.calculate_shipping_cost(rate_per_kg=-5)
        with pytest.raises(TypeError, match="Rate per kg must be a positive number."):
            physical_product.calculate_shipping_cost(rate_per_kg="ten")
        
        with pytest.raises(ValueError, match="Volumetric factor must be a positive integer."):
            physical_product.calculate_shipping_cost(rate_per_kg=10, volumetric_factor=0)
        with pytest.raises(ValueError, match="Volumetric factor must be a positive integer."):
            physical_product.calculate_shipping_cost(rate_per_kg=10, volumetric_factor=-100)
        with pytest.raises(TypeError, match="Volumetric factor must be a positive integer."):
            physical_product.calculate_shipping_cost(rate_per_kg=10, volumetric_factor=5000.5)

    def test_physical_product_repr(self, physical_product):
        """Test PhysicalProduct __repr__ method."""
        expected_repr = f"PhysicalProduct(name='Laptop X', price=1200.00, id='{physical_product.product_id}', weight=2.5kg)"
        assert repr(physical_product) == expected_repr

class TestInventory:
    def test_inventory_creation(self, inventory_instance):
        """Test Inventory creation."""
        assert isinstance(inventory_instance.products, dict)
        assert len(inventory_instance.products) == 0

    def test_add_product_valid(self, inventory_instance, generic_product, digital_product):
        """Test adding valid products to inventory."""
        inventory_instance.add_product(generic_product)
        assert generic_product.product_id in inventory_instance.products
        assert inventory_instance.products[generic_product.product_id] == generic_product
        assert generic_product.quantity == 10 # Original quantity

        inventory_instance.add_product(digital_product, initial_stock=5)
        assert digital_product.product_id in inventory_instance.products
        assert digital_product.quantity == 5 # Overridden by initial_stock

    def test_add_product_duplicate(self, inventory_instance, generic_product):
        """Test adding a duplicate product ID."""
        inventory_instance.add_product(generic_product)
        with pytest.raises(ValueError, match=f"Product with ID {generic_product.product_id} already exists in inventory."):
            inventory_instance.add_product(generic_product) # Add same product again

        # Create a new product with the same ID
        product_with_same_id = Product("Cloned Product", 5.0, product_id=generic_product.product_id)
        with pytest.raises(ValueError, match=f"Product with ID {generic_product.product_id} already exists in inventory."):
            inventory_instance.add_product(product_with_same_id)


    def test_add_product_invalid_type(self, inventory_instance):
        """Test adding an invalid item type to inventory."""
        with pytest.raises(TypeError, match="Item to add must be an instance of Product."):
            inventory_instance.add_product("not a product")

    def test_add_product_invalid_initial_stock(self, inventory_instance, generic_product):
        """Test adding product with invalid initial stock."""
        temp_product = Product("Temp", 1)
        with pytest.raises(ValueError, match="Initial stock must be a non-negative integer."):
            inventory_instance.add_product(temp_product, initial_stock=-1)
        with pytest.raises(TypeError, match="Initial stock must be a non-negative integer."):
            inventory_instance.add_product(temp_product, initial_stock="many")


    def test_remove_product_valid(self, inventory_instance, generic_product):
        """Test removing an existing product."""
        inventory_instance.add_product(generic_product)
        removed_product = inventory_instance.remove_product(generic_product.product_id)
        assert removed_product == generic_product
        assert generic_product.product_id not in inventory_instance.products

    def test_remove_product_non_existent(self, inventory_instance):
        """Test removing a non-existent product."""
        with pytest.raises(KeyError, match="Product with ID non-existent-id not found in inventory."):
            inventory_instance.remove_product("non-existent-id")

    def test_remove_product_invalid_id_type(self, inventory_instance):
        """Test removing product with invalid ID type."""
        with pytest.raises(TypeError, match="Product ID must be a string."):
            inventory_instance.remove_product(123)

    def test_get_product_valid(self, inventory_instance, generic_product):
        """Test retrieving an existing product."""
        inventory_instance.add_product(generic_product)
        retrieved_product = inventory_instance.get_product(generic_product.product_id)
        assert retrieved_product == generic_product

    def test_get_product_non_existent(self, inventory_instance):
        """Test retrieving a non-existent product."""
        with pytest.raises(KeyError, match="Product with ID non-existent-id not found in inventory."):
            inventory_instance.get_product("non-existent-id")

    def test_get_product_invalid_id_type(self, inventory_instance):
        """Test retrieving product with invalid ID type."""
        with pytest.raises(TypeError, match="Product ID must be a string."):
            inventory_instance.get_product(12345)


    def test_update_stock_valid(self, inventory_instance, generic_product):
        """Test valid stock updates."""
        # generic_product.quantity is 10
        inventory_instance.add_product(generic_product)
        inventory_instance.update_stock(generic_product.product_id, 5)
        assert generic_product.quantity == 15
        inventory_instance.update_stock(generic_product.product_id, -10)
        assert generic_product.quantity == 5
        inventory_instance.update_stock(generic_product.product_id, -5)
        assert generic_product.quantity == 0

    def test_update_stock_invalid(self, inventory_instance, generic_product):
        """Test invalid stock updates."""
        inventory_instance.add_product(generic_product) # quantity is 10
        
        with pytest.raises(ValueError, match=f"Stock update for {generic_product.product_id} failed: Quantity cannot be reduced below zero."):
            inventory_instance.update_stock(generic_product.product_id, -100)
        
        with pytest.raises(KeyError, match="Product with ID non-existent-id not found in inventory."):
            inventory_instance.update_stock("non-existent-id", 5)

        with pytest.raises(TypeError, match="Product ID must be a string."):
            inventory_instance.update_stock(123, 5)
        
        # Relies on Product.update_quantity's TypeError for quantity_change
        with pytest.raises(TypeError, match="Quantity change must be an integer."):
            inventory_instance.update_stock(generic_product.product_id, "five")

    def test_get_total_inventory_value(self, inventory_instance, generic_product, digital_product):
        """Test calculating total inventory value."""
        assert inventory_instance.get_total_inventory_value() == 0.00

        # generic_product: price=19.99, quantity=10 => value = 199.90
        # digital_product: price=9.99, quantity=1 (default) => value = 9.99
        inventory_instance.add_product(generic_product)
        inventory_instance.add_product(digital_product, initial_stock=2) # price 9.99, quantity 2 => value 19.98
        
        # generic_product.quantity is 10, price 19.99
        # digital_product.quantity is 2, price 9.99
        expected_value = (19.99 * 10) + (9.99 * 2)
        assert inventory_instance.get_total_inventory_value() == round(expected_value, 2)

    def test_find_products_by_name(self, inventory_instance):
        """Test finding products by name."""
        p1 = Product(name="Apple iPhone 13", price=799)
        p2 = Product(name="Apple MacBook Pro", price=1299)
        p3 = Product(name="Samsung Galaxy S21", price=699)
        p4 = Product(name="iPhone Case", price=20) # Different case for "iPhone"
        inventory_instance.add_product(p1)
        inventory_instance.add_product(p2)
        inventory_instance.add_product(p3)
        inventory_instance.add_product(p4)

        results_apple = inventory_instance.find_products_by_name("Apple")
        assert len(results_apple) == 2
        assert p1 in results_apple and p2 in results_apple

        results_iphone_cs = inventory_instance.find_products_by_name("iPhone", case_sensitive=True)
        assert len(results_iphone_cs) == 2 # "iPhone 13", "iPhone Case"
        assert p1 in results_iphone_cs
        assert p4 in results_iphone_cs

        results_iphone_ci = inventory_instance.find_products_by_name("iphone", case_sensitive=False)
        assert len(results_iphone_ci) == 2
        assert p1 in results_iphone_ci and p4 in results_iphone_ci
        
        results_iphone_ci_from_p1 = inventory_instance.find_products_by_name("IPHONE", case_sensitive=False)
        assert len(results_iphone_ci_from_p1) == 2

        results_galaxy = inventory_instance.find_products_by_name("Galaxy")
        assert results_galaxy == [p3]

        results_none = inventory_instance.find_products_by_name("Nokia")
        assert len(results_none) == 0

        with pytest.raises(TypeError, match="Search term must be a string."):
            inventory_instance.find_products_by_name(123)

    def test_get_products_in_price_range(self, inventory_instance):
        """Test getting products within a price range."""
        p1 = Product(name="P1", price=10)
        p2 = Product(name="P2", price=20)
        p3 = Product(name="P3", price=30)
        p4 = Product(name="P4", price=20) # Same price as P2
        inventory_instance.add_product(p1)
        inventory_instance.add_product(p2)
        inventory_instance.add_product(p3)
        inventory_instance.add_product(p4)

        # Range includes P1, P2, P4
        results = inventory_instance.get_products_in_price_range(min_price=5, max_price=25)
        assert len(results) == 3
        assert p1 in results and p2 in results and p4 in results
        
        # Exact match
        results_exact = inventory_instance.get_products_in_price_range(min_price=20, max_price=20)
        assert len(results_exact) == 2
        assert p2 in results_exact and p4 in results_exact

        # Open min range
        results_open_min = inventory_instance.get_products_in_price_range(max_price=15)
        assert results_open_min == [p1]

        # Open max range
        results_open_max = inventory_instance.get_products_in_price_range(min_price=25)
        assert results_open_max == [p3]

        # No products in range
        results_none = inventory_instance.get_products_in_price_range(min_price=100, max_price=200)
        assert len(results_none) == 0

        with pytest.raises(ValueError, match="Minimum price must be a non-negative number."):
            inventory_instance.get_products_in_price_range(min_price=-5)
        with pytest.raises(TypeError, match="Minimum price must be a non-negative number."):
            inventory_instance.get_products_in_price_range(min_price="free")
            
        with pytest.raises(ValueError, match="Maximum price must be a number greater than or equal to minimum price."):
            inventory_instance.get_products_in_price_range(min_price=20, max_price=10)
        with pytest.raises(TypeError, match="Maximum price must be a number greater than or equal to minimum price."):
            inventory_instance.get_products_in_price_range(max_price="expensive")


    def test_get_stock_level(self, inventory_instance, generic_product):
        """Test getting stock level for a product."""
        generic_product.quantity = 7 # Set specific quantity
        inventory_instance.add_product(generic_product)
        assert inventory_instance.get_stock_level(generic_product.product_id) == 7

        with pytest.raises(KeyError):
            inventory_instance.get_stock_level("non-existent-id")
        with pytest.raises(TypeError):
            inventory_instance.get_stock_level(123)

class TestOrder:
    @pytest.fixture
    def product1(self):
        return Product(name="Product A", price=10.00, quantity=100, product_id="prod_A")

    @pytest.fixture
    def product2(self):
        return Product(name="Product B", price=25.50, quantity=50, product_id="prod_B")

    @pytest.fixture
    def populated_inventory(self, inventory_instance, product1, product2):
        inventory_instance.add_product(product1)
        inventory_instance.add_product(product2)
        return inventory_instance

    def test_order_creation(self):
        """Test Order creation."""
        order = Order(customer_id="cust123")
        assert isinstance(uuid.UUID(order.order_id), uuid.UUID)
        assert order.customer_id == "cust123"
        assert order.items == {}
        assert order.status == "pending"
        assert not order._is_finalized

        order_custom_id = Order(order_id="order-xyz", customer_id="cust456")
        assert order_custom_id.order_id == "order-xyz"

    def test_order_creation_invalid_ids(self):
        """Test Order creation with invalid ID types."""
        with pytest.raises(TypeError, match="Order ID must be a string if provided."):
            Order(order_id=123)
        with pytest.raises(TypeError, match="Customer ID must be a string if provided."):
            Order(customer_id=456)

    def test_add_item_no_inventory(self, order_instance, product1):
        """Test adding item to order without inventory check."""
        order_instance.add_item(product1, 2)
        assert "prod_A" in order_instance.items
        assert order_instance.items["prod_A"]["quantity"] == 2
        assert order_instance.items["prod_A"]["price_at_purchase"] == 10.00
        assert order_instance.items["prod_A"]["product_snapshot"]["name"] == "Product A"

        order_instance.add_item(product1, 3) # Add more of the same item
        assert order_instance.items["prod_A"]["quantity"] == 5

    def test_add_item_with_inventory_sufficient_stock(self, order_instance, product1, populated_inventory):
        """Test adding item with inventory check (sufficient stock)."""
        initial_stock_p1 = populated_inventory.get_stock_level(product1.product_id) # 100
        
        order_instance.add_item(product1, 5, inventory=populated_inventory)
        assert "prod_A" in order_instance.items
        assert order_instance.items["prod_A"]["quantity"] == 5
        assert populated_inventory.get_stock_level(product1.product_id) == initial_stock_p1 - 5

    def test_add_item_with_inventory_insufficient_stock(self, order_instance, product1, populated_inventory):
        """Test adding item with inventory check (insufficient stock)."""
        with pytest.raises(ValueError, match=f"Not enough stock for Product A \(ID: prod_A\). Requested: 200, Available: 100"):
            order_instance.add_item(product1, 200, inventory=populated_inventory)
        assert "prod_A" not in order_instance.items # Item should not be added
        assert populated_inventory.get_stock_level(product1.product_id) == 100 # Stock unchanged

    def test_add_item_to_finalized_order(self, order_instance, product1):
        """Test adding item to a finalized order."""
        order_instance.add_item(product1, 1)
        order_instance.finalize_order()
        with pytest.raises(RuntimeError, match="Cannot add items to a finalized order."):
            order_instance.add_item(product1, 1)

    def test_add_item_invalid_inputs(self, order_instance, product1, populated_inventory):
        """Test adding item with invalid inputs."""
        with pytest.raises(TypeError, match="Item to add must be an instance of Product."):
            order_instance.add_item("not a product", 1)
        with pytest.raises(ValueError, match="Quantity must be a positive integer."):
            order_instance.add_item(product1, 0)
        with pytest.raises(ValueError, match="Quantity must be a positive integer."):
            order_instance.add_item(product1, -1)
        with pytest.raises(TypeError, match="Quantity must be a positive integer."):
            order_instance.add_item(product1, "one")
        with pytest.raises(TypeError, match="Inventory must be an Inventory instance."):
            order_instance.add_item(product1, 1, inventory="not inventory")
        with pytest.raises(KeyError): # Product not in inventory
            p_not_in_inv = Product("NotInInv", 1)
            order_instance.add_item(p_not_in_inv, 1, inventory=populated_inventory)


    def test_remove_item_no_inventory(self, order_instance, product1):
        """Test removing item from order without inventory interaction."""
        order_instance.add_item(product1, 5)
        order_instance.remove_item(product1.product_id, 2)
        assert order_instance.items[product1.product_id]["quantity"] == 3

        order_instance.remove_item(product1.product_id, 3) # Remove all remaining
        assert product1.product_id not in order_instance.items

    def test_remove_item_with_inventory(self, order_instance, product1, populated_inventory):
        """Test removing item with inventory restocking."""
        initial_stock_p1 = populated_inventory.get_stock_level(product1.product_id) # 100
        order_instance.add_item(product1, 10, inventory=populated_inventory)
        assert populated_inventory.get_stock_level(product1.product_id) == initial_stock_p1 - 10 # 90

        order_instance.remove_item(product1.product_id, 3, inventory=populated_inventory)
        assert order_instance.items[product1.product_id]["quantity"] == 7
        assert populated_inventory.get_stock_level(product1.product_id) == initial_stock_p1 - 10 + 3 # 93

        order_instance.remove_item(product1.product_id, 7, inventory=populated_inventory) # Remove all
        assert product1.product_id not in order_instance.items
        assert populated_inventory.get_stock_level(product1.product_id) == initial_stock_p1 # Back to 100

    def test_remove_item_from_finalized_order(self, order_instance, product1, populated_inventory):
        """Test removing item from finalized orders with different statuses."""
        order_instance.add_item(product1, 5, inventory=populated_inventory)
        
        # Status: pending (allowed)
        order_instance.finalize_order() # status becomes awaiting_payment if pending
        order_instance.status = "pending" # Manually set back for testing this specific case if needed, or test awaiting_payment
        order_instance._is_finalized = False # Temporarily allow modification as if it was not fully finalized for status 'pending' removal test
        order_instance.remove_item(product1.product_id, 1, inventory=populated_inventory)
        assert order_instance.items[product1.product_id]["quantity"] == 4
        order_instance._is_finalized = True # Re-finalize after modification

        # Status: awaiting_payment (allowed)
        order_instance.status = "awaiting_payment"
        order_instance.remove_item(product1.product_id, 1, inventory=populated_inventory)
        assert order_instance.items[product1.product_id]["quantity"] == 3
        
        # Status: shipped (not allowed)
        order_instance.update_status("shipped") # This also sets _is_finalized = True
        with pytest.raises(RuntimeError, match="Cannot remove items from an order with status 'shipped'."):
            order_instance.remove_item(product1.product_id, 1, inventory=populated_inventory)

    def test_remove_item_invalid_inputs_or_state(self, order_instance, product1, populated_inventory):
        """Test removing item with various invalid conditions."""
        order_instance.add_item(product1, 3, inventory=populated_inventory)

        with pytest.raises(TypeError, match="Product ID must be a string."):
            order_instance.remove_item(123, 1)
        with pytest.raises(ValueError, match="Quantity to remove must be a positive integer."):
            order_instance.remove_item(product1.product_id, 0)
        with pytest.raises(ValueError, match="Quantity to remove must be a positive integer."):
            order_instance.remove_item(product1.product_id, -1)
        with pytest.raises(TypeError, match="Quantity to remove must be a positive integer."):
            order_instance.remove_item(product1.product_id, "one")
        
        with pytest.raises(KeyError, match="Product with ID non-existent-prod not found in order."):
            order_instance.remove_item("non-existent-prod", 1)

        with pytest.raises(ValueError, match=f"Cannot remove 5 units of {product1.product_id}; only 3 in order."):
            order_instance.remove_item(product1.product_id, 5)

        with pytest.raises(TypeError, match="Inventory must be an Inventory instance."):
            order_instance.remove_item(product1.product_id, 1, inventory="not inventory")

        # Simulate product removed from inventory after being added to order, then try to restock
        prod_temp_id = "temp_prod_for_removal_test"
        prod_temp = Product("Temp Prod", 1.0, product_id=prod_temp_id, quantity=10)
        populated_inventory.add_product(prod_temp)
        order_instance.add_item(prod_temp, 1, inventory=populated_inventory)
        populated_inventory.remove_product(prod_temp_id) # Remove from inventory
        
        # This should ideally be caught by Inventory.update_stock raising KeyError,
        # but Order wraps it in RuntimeError.
        # The current code_normal.py:Inventory.update_stock first calls get_product, which would fail.
        # The product.update_quantity would be the source of error if product itself was directly manipulated.
        # Here, the inventory.update_stock(product_id, quantity_change) will fail at get_product(product_id).
        with pytest.raises(RuntimeError, match=f"Product {prod_temp_id} not found in inventory for restocking. Inconsistent state."):
             order_instance.remove_item(prod_temp_id, 1, inventory=populated_inventory)


    def test_calculate_total(self, order_instance, product1, product2):
        """Test order total calculation."""
        assert order_instance.calculate_total() == 0.00

        order_instance.add_item(product1, 2) # 2 * 10.00 = 20.00
        order_instance.add_item(product2, 1) # 1 * 25.50 = 25.50
        assert order_instance.calculate_total() == 45.50

        # Change product price AFTER adding to order - total should not change
        product1.price = 5.00 
        assert order_instance.calculate_total() == 45.50 

    def test_update_status_valid(self, order_instance):
        """Test valid order status updates."""
        order_instance.update_status("processing")
        assert order_instance.status == "processing"
        assert not order_instance._is_finalized

        order_instance.update_status("shipped")
        assert order_instance.status == "shipped"
        assert order_instance._is_finalized

        # Reset finalized for next test
        order_instance._is_finalized = False 
        order_instance.update_status("delivered")
        assert order_instance.status == "delivered"
        assert order_instance._is_finalized
        
        # Can update from delivered to refunded
        order_instance.update_status("refunded")
        assert order_instance.status == "refunded"
        assert order_instance._is_finalized

    def test_update_status_invalid(self, order_instance):
        """Test invalid order status updates."""
        with pytest.raises(TypeError, match="New status must be a string."):
            order_instance.update_status(123)
        with pytest.raises(ValueError, match="Invalid order status 'unknown'."):
            order_instance.update_status("unknown")

        order_instance.update_status("delivered")
        with pytest.raises(ValueError, match="Cannot change status from 'delivered' to 'processing'."):
            order_instance.update_status("processing")
        # Can update from delivered to delivered or refunded
        order_instance.update_status("delivered") # no change, allowed
        assert order_instance.status == "delivered"

        order_instance.update_status("cancelled")
        with pytest.raises(ValueError, match="Cannot change status of a 'cancelled' order."):
            order_instance.update_status("pending")
        order_instance.update_status("cancelled") # no change, allowed
        assert order_instance.status == "cancelled"


    def test_get_order_summary(self, order_instance, product1, product2):
        """Test getting order summary."""
        order_instance.customer_id = "cust789"
        order_instance.add_item(product1, 3) # 3 * 10.00 = 30.00
        order_instance.add_item(product2, 1) # 1 * 25.50 = 25.50
        order_instance.update_status("processing")

        summary = order_instance.get_order_summary()
        
        assert summary["order_id"] == order_instance.order_id
        assert summary["customer_id"] == "cust789"
        assert summary["status"] == "processing"
        assert summary["total_items"] == 4
        assert summary["total_cost"] == 55.50
        assert len(summary["items"]) == 2
        
        item_a_summary = next(item for item in summary["items"] if item["product_id"] == "prod_A")
        item_b_summary = next(item for item in summary["items"] if item["product_id"] == "prod_B")

        assert item_a_summary["name"] == "Product A"
        assert item_a_summary["quantity"] == 3
        assert item_a_summary["unit_price"] == 10.00
        assert item_a_summary["subtotal"] == 30.00
        
        assert item_b_summary["name"] == "Product B"
        assert item_b_summary["quantity"] == 1
        assert item_b_summary["unit_price"] == 25.50
        assert item_b_summary["subtotal"] == 25.50

    def test_finalize_order(self, order_instance, product1):
        """Test finalizing an order."""
        # Test finalizing an empty order
        with pytest.raises(ValueError, match="Cannot finalize an empty order."):
            order_instance.finalize_order()

        order_instance.add_item(product1, 1)
        assert order_instance.status == "pending"
        assert not order_instance._is_finalized
        
        order_instance.finalize_order()
        assert order_instance.status == "awaiting_payment"
        assert order_instance._is_finalized

        # Test finalizing an order not in "pending" status
        order_instance.status = "processing" # Already past 'pending'
        order_instance.finalize_order() # Should still set _is_finalized, status should remain 'processing'
        assert order_instance.status == "processing"
        assert order_instance._is_finalized

    def test_order_repr(self, order_instance, product1):
        """Test Order __repr__ method."""
        order_instance.add_item(product1, 2) # Total 20.00
        expected_repr = f"Order(id='{order_instance.order_id}', status='pending', items=1, total=20.0)"
        assert repr(order_instance) == expected_repr

