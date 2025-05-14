import sys
import pytest
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# Testy pro třídu Product
class TestProduct:
    def test_product_creation_ok(self):
        p = Product("Laptop", 1200.50, quantity=10)
        assert p.name == "Laptop"
        assert p.price == 1200.50
        assert p.quantity == 10
        assert isinstance(p.product_id, str)

    def test_product_creation_with_id_ok(self):
        product_id = "test_id_123"
        p = Product("Mouse", 25.00, product_id=product_id)
        assert p.product_id == product_id

    def test_product_creation_invalid_name_type(self):
        with pytest.raises(TypeError, match="Product name must be a non-empty string."):
            Product(123, 10.0)

    def test_product_creation_empty_name(self):
        with pytest.raises(TypeError, match="Product name must be a non-empty string."):
            Product("   ", 10.0)

    def test_product_creation_invalid_price_type(self):
        with pytest.raises(TypeError, match="Product price must be a positive number."):
            Product("Test", "invalid_price")

    def test_product_creation_negative_price(self):
        with pytest.raises(ValueError, match="Product price must be a positive number."):
            Product("Test", -10.0)

    def test_product_creation_zero_price(self):
        with pytest.raises(ValueError, match="Product price must be a positive number."):
            Product("Test", 0)

    def test_product_creation_invalid_id_type(self):
        with pytest.raises(TypeError, match="Product ID must be a string if provided."):
            Product("Test", 10.0, product_id=123)

    def test_product_creation_invalid_quantity_type(self):
        with pytest.raises(TypeError, match="Product quantity must be a non-negative integer."):
            Product("Test", 10.0, quantity="abc")

    def test_product_creation_negative_quantity(self):
        with pytest.raises(ValueError, match="Product quantity must be a non-negative integer."):
            Product("Test", 10.0, quantity=-1)

    def test_get_details(self):
        p = Product("Keyboard", 75.00, quantity=5)
        details = p.get_details()
        assert details["name"] == "Keyboard"
        assert details["price"] == 75.00
        assert details["quantity"] == 5
        assert details["product_id"] == p.product_id
        assert details["type"] == "GenericProduct"

    def test_update_quantity_ok(self):
        p = Product("Monitor", 300, quantity=10)
        p.update_quantity(5)
        assert p.quantity == 15
        p.update_quantity(-3)
        assert p.quantity == 12

    def test_update_quantity_invalid_type(self):
        p = Product("Webcam", 50)
        with pytest.raises(TypeError, match="Quantity change must be an integer."):
            p.update_quantity(5.5)

    def test_update_quantity_below_zero(self):
        p = Product("Desk", 150, quantity=2)
        with pytest.raises(ValueError, match="Quantity cannot be reduced below zero."):
            p.update_quantity(-5)

    def test_apply_discount_ok(self):
        p = Product("Chair", 100)
        p.apply_discount(10) # 10%
        assert p.price == 90.00
        p.apply_discount(25.5) # 25.5% of 90 = 22.95, price = 67.05
        assert p.price == 67.05

    def test_apply_discount_invalid_type(self):
        p = Product("Speaker", 60)
        with pytest.raises(TypeError, match="Discount percentage must be a number."):
            p.apply_discount("invalid")

    def test_apply_discount_out_of_range_negative(self):
        p = Product("Table", 200)
        with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100."):
            p.apply_discount(-10)

    def test_apply_discount_out_of_range_positive(self):
        p = Product("Lamp", 30)
        with pytest.raises(ValueError, match="Discount percentage must be between 0 and 100."):
            p.apply_discount(110)

    def test_product_repr(self):
        p = Product("TestProduct", 19.99, product_id="repr_id", quantity=3)
        expected_repr = "Product(name='TestProduct', price=19.99, id='repr_id', quantity=3)"
        assert repr(p) == expected_repr

# Testy pro třídu DigitalProduct
class TestDigitalProduct:
    def test_digital_product_creation_ok(self):
        dp = DigitalProduct("Software", 59.99, "https://example.com/download", 100.5)
        assert dp.name == "Software"
        assert dp.price == 59.99
        assert dp.download_link == "https://example.com/download"
        assert dp.file_size_mb == 100.5
        assert dp.quantity == 1 # Default quantity for DigitalProduct
        assert isinstance(dp.product_id, str)

    def test_digital_product_creation_invalid_link_type(self):
        with pytest.raises(TypeError, match="Download link must be a valid URL string starting with http:// or https://."):
            DigitalProduct("Ebook", 10, 123, 50)

    def test_digital_product_creation_invalid_link_format(self):
        with pytest.raises(TypeError, match="Download link must be a valid URL string starting with http:// or https://."):
            DigitalProduct("Song", 1.99, "ftp://example.com/song.mp3", 5)

    def test_digital_product_creation_invalid_file_size_type(self):
        with pytest.raises(TypeError, match="File size must be a positive number."):
            DigitalProduct("Video", 20, "http://example.com/video", "large")

    def test_digital_product_creation_non_positive_file_size(self):
        with pytest.raises(ValueError, match="File size must be a positive number."):
            DigitalProduct("Game", 40, "https://example.com/game", 0)

    def test_get_details_digital(self):
        dp = DigitalProduct("Course", 199.00, "http://school.com/course", 500, product_id="DP123")
        details = dp.get_details()
        assert details["name"] == "Course"
        assert details["price"] == 199.00
        assert details["download_link"] == "http://school.com/course"
        assert details["file_size_mb"] == 500
        assert details["type"] == "DigitalProduct"
        assert details["product_id"] == "DP123"

    def test_generate_new_download_link_ok(self):
        dp = DigitalProduct("Template", 15, "https://example.com/old_link", 2, product_id="unique_id")
        new_link = dp.generate_new_download_link("https://newbase.com/files")
        assert new_link.startswith("https://newbase.com/files/unique_id/download_")
        assert dp.download_link == new_link

    def test_generate_new_download_link_invalid_base_url_type(self):
        dp = DigitalProduct("Font", 5, "https://example.com/font", 1)
        with pytest.raises(TypeError, match="Base URL must be a non-empty string."):
            dp.generate_new_download_link(123)

    def test_generate_new_download_link_empty_base_url(self):
        dp = DigitalProduct("Icon Set", 8, "https://example.com/icons", 3)
        with pytest.raises(TypeError, match="Base URL must be a non-empty string."):
            dp.generate_new_download_link("   ")

    def test_digital_product_repr(self):
        dp = DigitalProduct("TestDP", 29.99, "http://link.com", 10.0, product_id="dprepr_id")
        expected_repr = "DigitalProduct(name='TestDP', price=29.99, id='dprepr_id', link='http://link.com')"
        assert repr(dp) == expected_repr

# Testy pro třídu PhysicalProduct
class TestPhysicalProduct:
    def test_physical_product_creation_ok(self):
        pp = PhysicalProduct("Book", 29.95, 0.5, (20, 15, 5), quantity=50)
        assert pp.name == "Book"
        assert pp.price == 29.95
        assert pp.weight_kg == 0.5
        assert pp.shipping_dimensions == (20, 15, 5)
        assert pp.quantity == 50
        assert isinstance(pp.product_id, str)

    def test_physical_product_invalid_weight_type(self):
        with pytest.raises(TypeError, match="Weight must be a positive number."):
            PhysicalProduct("Toy", 15, "heavy", (10,10,10))

    def test_physical_product_non_positive_weight(self):
        with pytest.raises(ValueError, match="Weight must be a positive number."):
            PhysicalProduct("Brick", 5, 0, (5,5,5))

    def test_physical_product_invalid_dimensions_type(self):
        with pytest.raises(TypeError, match="Shipping dimensions must be a tuple of three positive numbers"):
            PhysicalProduct("Box", 10, 1, "[10,10,10]")

    def test_physical_product_invalid_dimensions_length(self):
        with pytest.raises(TypeError, match="Shipping dimensions must be a tuple of three positive numbers"):
            PhysicalProduct("Frame", 20, 0.2, (10,10)) # Not 3 dimensions

    def test_physical_product_invalid_dimension_value_type(self):
        with pytest.raises(TypeError, match="Shipping dimensions must be a tuple of three positive numbers"):
            PhysicalProduct("Vase", 30, 0.8, (10,"tall",5))

    def test_physical_product_non_positive_dimension_value(self):
        with pytest.raises(TypeError, match="Shipping dimensions must be a tuple of three positive numbers"):
            PhysicalProduct("Sculpture", 100, 2, (10,0,10))

    def test_get_details_physical(self):
        pp = PhysicalProduct("Statue", 250, 5, (30,20,15), product_id="PP456")
        details = pp.get_details()
        assert details["name"] == "Statue"
        assert details["price"] == 250
        assert details["weight_kg"] == 5
        assert details["shipping_dimensions_cm"] == (30,20,15)
        assert details["type"] == "PhysicalProduct"
        assert details["product_id"] == "PP456"

    def test_calculate_shipping_cost_ok_weight_based(self):
        pp = PhysicalProduct("Dumbbell", 40, 10, (10,10,10)) # Volumetric = 10*10*10/5000 = 0.2
        cost = pp.calculate_shipping_cost(2.5) # Rate per kg
        assert cost == 25.00 # 10kg * 2.5

    def test_calculate_shipping_cost_ok_volumetric_based(self):
        pp = PhysicalProduct("Pillow", 20, 0.5, (50,50,20)) # Volumetric = 50*50*20/5000 = 10
        cost = pp.calculate_shipping_cost(3) # Rate per kg
        assert cost == 30.00 # 10 (volumetric) * 3

    def test_calculate_shipping_cost_invalid_rate_type(self):
        pp = PhysicalProduct("Chair", 50, 7, (60,50,80))
        with pytest.raises(TypeError, match="Rate per kg must be a positive number."):
            pp.calculate_shipping_cost("cheap")

    def test_calculate_shipping_cost_non_positive_rate(self):
        pp = PhysicalProduct("Table", 150, 20, (100,60,70))
        with pytest.raises(ValueError, match="Rate per kg must be a positive number."):
            pp.calculate_shipping_cost(0)

    def test_calculate_shipping_cost_invalid_volumetric_factor_type(self):
        pp = PhysicalProduct("Desk", 120, 15, (120,60,75))
        with pytest.raises(TypeError, match="Volumetric factor must be a positive integer."):
            pp.calculate_shipping_cost(2, volumetric_factor="abc")

    def test_calculate_shipping_cost_non_positive_volumetric_factor(self):
        pp = PhysicalProduct("Cabinet", 200, 30, (100,50,180))
        with pytest.raises(ValueError, match="Volumetric factor must be a positive integer."):
            pp.calculate_shipping_cost(2, volumetric_factor=0)

    def test_physical_product_repr(self):
        pp = PhysicalProduct("TestPP", 99.99, 2.5, (10,20,5), product_id="pprepr_id")
        expected_repr = "PhysicalProduct(name='TestPP', price=99.99, id='pprepr_id', weight=2.5kg)"
        assert repr(pp) == expected_repr

# Testy pro třídu Inventory
@pytest.fixture
def inventory_with_products():
    inv = Inventory()
    p1 = Product("Laptop", 1200, quantity=5, product_id="P1")
    p2 = PhysicalProduct("Mouse", 25, 0.1, (10,5,3), quantity=20, product_id="P2")
    p3 = DigitalProduct("Software", 100, "http://example.com/sw", 50, product_id="P3") # Quantity is 1 by default
    inv.add_product(p1)
    inv.add_product(p2)
    inv.add_product(p3, initial_stock=2) # Override default quantity for DigitalProduct
    return inv

class TestInventory:
    def test_inventory_creation(self):
        inv = Inventory()
        assert inv.products == {}

    def test_add_product_ok(self):
        inv = Inventory()
        p = Product("Test", 10, quantity=5)
        inv.add_product(p)
        assert p.product_id in inv.products
        assert inv.products[p.product_id] == p
        assert inv.get_product(p.product_id).quantity == 5

    def test_add_product_with_initial_stock(self):
        inv = Inventory()
        p = Product("Test", 10, quantity=0) # Product created with 0 quantity
        inv.add_product(p, initial_stock=15)
        assert inv.get_product(p.product_id).quantity == 15


    def test_add_product_invalid_type(self):
        inv = Inventory()
        with pytest.raises(TypeError, match="Item to add must be an instance of Product."):
            inv.add_product("not a product")

    def test_add_product_duplicate_id(self):
        inv = Inventory()
        p1 = Product("Test1", 10, product_id="dup_id")
        p2 = Product("Test2", 20, product_id="dup_id")
        inv.add_product(p1)
        with pytest.raises(ValueError, match="Product with ID dup_id already exists in inventory."):
            inv.add_product(p2)

    def test_add_product_invalid_initial_stock_type(self):
        inv = Inventory()
        p = Product("Test", 10)
        with pytest.raises(TypeError, match="Initial stock must be a non-negative integer."):
            inv.add_product(p, initial_stock="many")

    def test_add_product_negative_initial_stock(self):
        inv = Inventory()
        p = Product("Test", 10)
        with pytest.raises(ValueError, match="Initial stock must be a non-negative integer."):
            inv.add_product(p, initial_stock=-5)

    def test_remove_product_ok(self, inventory_with_products):
        removed_product = inventory_with_products.remove_product("P1")
        assert removed_product.name == "Laptop"
        assert "P1" not in inventory_with_products.products
        with pytest.raises(KeyError):
            inventory_with_products.get_product("P1")

    def test_remove_product_invalid_id_type(self, inventory_with_products):
        with pytest.raises(TypeError, match="Product ID must be a string."):
            inventory_with_products.remove_product(123)

    def test_remove_product_not_found(self, inventory_with_products):
        with pytest.raises(KeyError, match="Product with ID NONEXISTENT_ID not found in inventory."):
            inventory_with_products.remove_product("NONEXISTENT_ID")

    def test_get_product_ok(self, inventory_with_products):
        product = inventory_with_products.get_product("P2")
        assert product.name == "Mouse"

    def test_get_product_invalid_id_type(self, inventory_with_products):
        with pytest.raises(TypeError, match="Product ID must be a string."):
            inventory_with_products.get_product(12345)

    def test_get_product_not_found(self, inventory_with_products):
        with pytest.raises(KeyError, match="Product with ID P999 not found in inventory."):
            inventory_with_products.get_product("P999")

    def test_update_stock_ok(self, inventory_with_products):
        inventory_with_products.update_stock("P1", 3) # P1 had 5, now 8
        assert inventory_with_products.get_product("P1").quantity == 8
        inventory_with_products.update_stock("P2", -10) # P2 had 20, now 10
        assert inventory_with_products.get_product("P2").quantity == 10

    def test_update_stock_invalid_id_type(self, inventory_with_products):
        with pytest.raises(TypeError, match="Product ID must be a string."):
            inventory_with_products.update_stock(123, 5)

    def test_update_stock_product_not_found(self, inventory_with_products):
        with pytest.raises(KeyError, match="Product with ID P_NONEXISTENT not found in inventory."):
            inventory_with_products.update_stock("P_NONEXISTENT", 5)

    def test_update_stock_invalid_quantity_change_type(self, inventory_with_products):
        # This will raise TypeError from product.update_quantity
        with pytest.raises(TypeError, match="Quantity change must be an integer."):
            inventory_with_products.update_stock("P1", "five")

    def test_update_stock_below_zero(self, inventory_with_products):
        # P1 has 5
        with pytest.raises(ValueError, match="Stock update for P1 failed: Quantity cannot be reduced below zero."):
            inventory_with_products.update_stock("P1", -10)

    def test_get_total_inventory_value(self, inventory_with_products):
        # P1: 1200 * 5 = 6000
        # P2: 25 * 20 = 500
        # P3: 100 * 2 = 200
        # Total = 6000 + 500 + 200 = 6700
        assert inventory_with_products.get_total_inventory_value() == 6700.00

    def test_find_products_by_name_ok_case_insensitive(self, inventory_with_products):
        results = inventory_with_products.find_products_by_name("lap")
        assert len(results) == 1
        assert results[0].name == "Laptop"

        results_ware = inventory_with_products.find_products_by_name("ware")
        assert len(results_ware) == 1
        assert results_ware[0].name == "Software"

    def test_find_products_by_name_ok_case_sensitive(self, inventory_with_products):
        results_case_sensitive = inventory_with_products.find_products_by_name("Lap", case_sensitive=True)
        assert len(results_case_sensitive) == 1
        assert results_case_sensitive[0].name == "Laptop"

        results_case_sensitive_none = inventory_with_products.find_products_by_name("lap", case_sensitive=True)
        assert len(results_case_sensitive_none) == 0

    def test_find_products_by_name_no_match(self, inventory_with_products):
        results = inventory_with_products.find_products_by_name("NonExistent")
        assert len(results) == 0

    def test_find_products_by_name_invalid_term_type(self, inventory_with_products):
        with pytest.raises(TypeError, match="Search term must be a string."):
            inventory_with_products.find_products_by_name(123)

    def test_get_products_in_price_range_ok(self, inventory_with_products):
        # Prices: Laptop 1200, Mouse 25, Software 100
        results = inventory_with_products.get_products_in_price_range(50, 200) # Mouse (25 not in range), Software (100)
        assert len(results) == 1
        assert results[0].name == "Software"

        results_all = inventory_with_products.get_products_in_price_range() # All products
        assert len(results_all) == 3

        results_max_only = inventory_with_products.get_products_in_price_range(max_price=150) # Mouse, Software
        product_names = sorted([p.name for p in results_max_only])
        assert product_names == ["Mouse", "Software"]


    def test_get_products_in_price_range_invalid_min_price_type(self, inventory_with_products):
        with pytest.raises(TypeError, match="Minimum price must be a non-negative number."):
            inventory_with_products.get_products_in_price_range(min_price="low")

    def test_get_products_in_price_range_negative_min_price(self, inventory_with_products):
        with pytest.raises(ValueError, match="Minimum price must be a non-negative number."):
            inventory_with_products.get_products_in_price_range(min_price=-10)

    def test_get_products_in_price_range_invalid_max_price_type(self, inventory_with_products):
        with pytest.raises(TypeError, match="Maximum price must be a number greater than or equal to minimum price."):
            inventory_with_products.get_products_in_price_range(max_price="high")

    def test_get_products_in_price_range_max_less_than_min(self, inventory_with_products):
        with pytest.raises(ValueError, match="Maximum price must be a number greater than or equal to minimum price."):
            inventory_with_products.get_products_in_price_range(min_price=100, max_price=50)

    def test_get_stock_level_ok(self, inventory_with_products):
        assert inventory_with_products.get_stock_level("P1") == 5
        assert inventory_with_products.get_stock_level("P3") == 2

    def test_get_stock_level_invalid_id_type(self, inventory_with_products):
        with pytest.raises(TypeError, match="Product ID must be a string."):
            inventory_with_products.get_stock_level(99)

    def test_get_stock_level_product_not_found(self, inventory_with_products):
        with pytest.raises(KeyError):
            inventory_with_products.get_stock_level("NON_EXISTENT_P_ID")


# Testy pro třídu Order
@pytest.fixture
def sample_product1():
    return Product("Pen", 1.50, product_id="prod_pen", quantity=100)

@pytest.fixture
def sample_product2():
    return PhysicalProduct("Notebook", 5.00, 0.2, (20,15,1), product_id="prod_notebook", quantity=50)

@pytest.fixture
def sample_inventory(sample_product1, sample_product2):
    inv = Inventory()
    inv.add_product(sample_product1)
    inv.add_product(sample_product2)
    return inv

class TestOrder:
    def test_order_creation_ok(self):
        order = Order(customer_id="cust123")
        assert isinstance(order.order_id, str)
        assert order.customer_id == "cust123"
        assert order.items == {}
        assert order.status == "pending"
        assert not order._is_finalized

    def test_order_creation_with_order_id(self):
        order = Order(order_id="order_xyz", customer_id="cust456")
        assert order.order_id == "order_xyz"

    def test_order_creation_invalid_order_id_type(self):
        with pytest.raises(TypeError, match="Order ID must be a string if provided."):
            Order(order_id=123)

    def test_order_creation_invalid_customer_id_type(self):
        with pytest.raises(TypeError, match="Customer ID must be a string if provided."):
            Order(customer_id=789)

    def test_add_item_ok_no_inventory(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 2)
        assert sample_product1.product_id in order.items
        item_data = order.items[sample_product1.product_id]
        assert item_data["quantity"] == 2
        assert item_data["price_at_purchase"] == sample_product1.price
        assert item_data["product_snapshot"]["name"] == sample_product1.name

    def test_add_item_ok_with_inventory(self, sample_product1, sample_inventory):
        order = Order()
        initial_stock = sample_inventory.get_stock_level(sample_product1.product_id)
        order.add_item(sample_product1, 3, inventory=sample_inventory)
        assert sample_product1.product_id in order.items
        assert order.items[sample_product1.product_id]["quantity"] == 3
        assert sample_inventory.get_stock_level(sample_product1.product_id) == initial_stock - 3

    def test_add_item_to_existing_product_in_order(self, sample_product1, sample_inventory):
        order = Order()
        order.add_item(sample_product1, 2, inventory=sample_inventory)
        order.add_item(sample_product1, 4, inventory=sample_inventory)
        assert order.items[sample_product1.product_id]["quantity"] == 6
        # Initial 100 -> 100-2 = 98 -> 98-4 = 94
        assert sample_inventory.get_stock_level(sample_product1.product_id) == 100 - 2 - 4


    def test_add_item_to_finalized_order(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 1)
        order.finalize_order()
        with pytest.raises(RuntimeError, match="Cannot add items to a finalized order."):
            order.add_item(sample_product1, 1)

    def test_add_item_invalid_product_type(self):
        order = Order()
        with pytest.raises(TypeError, match="Item to add must be an instance of Product."):
            order.add_item("not_a_product", 1)

    def test_add_item_invalid_quantity_type(self, sample_product1):
        order = Order()
        with pytest.raises(TypeError, match="Quantity must be a positive integer."):
            order.add_item(sample_product1, "one")

    def test_add_item_non_positive_quantity(self, sample_product1):
        order = Order()
        with pytest.raises(ValueError, match="Quantity must be a positive integer."):
            order.add_item(sample_product1, 0)

    def test_add_item_invalid_inventory_type(self, sample_product1):
        order = Order()
        with pytest.raises(TypeError, match="Inventory must be an Inventory instance."):
            order.add_item(sample_product1, 1, inventory="not_inventory")

    def test_add_item_not_enough_stock(self, sample_product1, sample_inventory):
        order = Order()
        with pytest.raises(ValueError, match=f"Not enough stock for {sample_product1.name}"):
            order.add_item(sample_product1, 200, inventory=sample_inventory) # Stock is 100

    def test_remove_item_ok(self, sample_product1, sample_inventory):
        order = Order()
        order.add_item(sample_product1, 5, inventory=sample_inventory) # Stock 100 -> 95
        initial_stock = sample_inventory.get_stock_level(sample_product1.product_id) # 95

        order.remove_item(sample_product1.product_id, 2, inventory=sample_inventory)
        assert order.items[sample_product1.product_id]["quantity"] == 3
        assert sample_inventory.get_stock_level(sample_product1.product_id) == initial_stock + 2 # 95 + 2 = 97

    def test_remove_item_completely(self, sample_product2, sample_inventory):
        order = Order()
        order.add_item(sample_product2, 3, inventory=sample_inventory)
        order.remove_item(sample_product2.product_id, 3, inventory=sample_inventory)
        assert sample_product2.product_id not in order.items

    def test_remove_item_from_finalized_order_disallowed_status(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 2)
        order.update_status("shipped") # This also finalizes
        with pytest.raises(RuntimeError, match="Cannot remove items from an order with status 'shipped'."):
            order.remove_item(sample_product1.product_id, 1)

    def test_remove_item_from_finalized_order_allowed_status(self, sample_product1, sample_inventory):
        order = Order()
        order.add_item(sample_product1, 3, inventory=sample_inventory) # Stock 100 -> 97
        order.finalize_order() # Status -> awaiting_payment, is_finalized=True
        assert order.status == "awaiting_payment"
        assert order._is_finalized
        
        order.remove_item(sample_product1.product_id, 1, inventory=sample_inventory) # Stock 97 -> 98
        assert order.items[sample_product1.product_id]["quantity"] == 2
        assert sample_inventory.get_stock_level(sample_product1.product_id) == 98


    def test_remove_item_invalid_product_id_type(self):
        order = Order()
        with pytest.raises(TypeError, match="Product ID must be a string."):
            order.remove_item(123, 1)

    def test_remove_item_invalid_quantity_type(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 2)
        with pytest.raises(TypeError, match="Quantity to remove must be a positive integer."):
            order.remove_item(sample_product1.product_id, "one")

    def test_remove_item_non_positive_quantity(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 2)
        with pytest.raises(ValueError, match="Quantity to remove must be a positive integer."):
            order.remove_item(sample_product1.product_id, 0)

    def test_remove_item_product_not_in_order(self):
        order = Order()
        with pytest.raises(KeyError, match="Product with ID non_existent_prod not found in order."):
            order.remove_item("non_existent_prod", 1)

    def test_remove_item_too_many_to_remove(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 2)
        with pytest.raises(ValueError, match=f"Cannot remove 3 units of {sample_product1.product_id}; only 2 in order."):
            order.remove_item(sample_product1.product_id, 3)

    def test_remove_item_invalid_inventory_type(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 2)
        with pytest.raises(TypeError, match="Inventory must be an Inventory instance."):
            order.remove_item(sample_product1.product_id, 1, inventory="not_inventory")
            
    def test_remove_item_product_not_in_inventory_for_restock(self, sample_product1, sample_inventory):
        order = Order()
        temp_product = Product("Temp", 10, product_id="temp_prod_id", quantity=5)
        # Add to order (without adding to inventory first for this test case)
        order.items[temp_product.product_id] = {
            "product_snapshot": {"product_id": temp_product.product_id, "name": temp_product.name, "type": "Product"},
            "quantity": 2,
            "price_at_purchase": temp_product.price
        }
        # Now try to remove with inventory check, product "temp_prod_id" isn't in sample_inventory
        with pytest.raises(RuntimeError, match=f"Product {temp_product.product_id} not found in inventory for restocking. Inconsistent state."):
            order.remove_item(temp_product.product_id, 1, inventory=sample_inventory)


    def test_calculate_total(self, sample_product1, sample_product2):
        order = Order()
        order.add_item(sample_product1, 2) # Pen: 1.50 * 2 = 3.00
        order.add_item(sample_product2, 3) # Notebook: 5.00 * 3 = 15.00
        # Simulate price change after adding to order (should not affect order total)
        original_price_p1 = sample_product1.price
        sample_product1.price = 2.00
        assert order.calculate_total() == 18.00
        sample_product1.price = original_price_p1 # revert price for other tests

    def test_calculate_total_empty_order(self):
        order = Order()
        assert order.calculate_total() == 0.00

    def test_update_status_ok(self):
        order = Order()
        order.update_status("processing")
        assert order.status == "processing"
        assert not order._is_finalized
        order.update_status("Shipped") # Test case insensitivity
        assert order.status == "shipped"
        assert order._is_finalized

    def test_update_status_invalid_type(self):
        order = Order()
        with pytest.raises(TypeError, match="New status must be a string."):
            order.update_status(123)

    def test_update_status_invalid_value(self):
        order = Order()
        with pytest.raises(ValueError, match="Invalid order status 'unknown_status'."):
            order.update_status("unknown_status")

    def test_update_status_from_delivered_restricted(self):
        order = Order()
        order.update_status("delivered")
        with pytest.raises(ValueError, match="Cannot change status from 'delivered' to 'processing'."):
            order.update_status("processing")
        order.update_status("refunded") # This should be allowed
        assert order.status == "refunded"

    def test_update_status_from_cancelled_restricted(self):
        order = Order()
        order.update_status("cancelled")
        with pytest.raises(ValueError, match="Cannot change status of a 'cancelled' order."):
            order.update_status("pending")
        order.update_status("cancelled") # Should be fine
        assert order.status == "cancelled"


    def test_get_order_summary(self, sample_product1, sample_product2):
        order = Order(order_id="sum_ord_1", customer_id="cust_sum_1")
        order.add_item(sample_product1, 2) # 1.50 each
        order.add_item(sample_product2, 1) # 5.00 each
        summary = order.get_order_summary()

        assert summary["order_id"] == "sum_ord_1"
        assert summary["customer_id"] == "cust_sum_1"
        assert summary["status"] == "pending"
        assert summary["total_items"] == 3
        assert summary["total_cost"] == 8.00 # (2 * 1.50) + (1 * 5.00)
        assert len(summary["items"]) == 2

        item_pen_summary = next(item for item in summary["items"] if item["product_id"] == sample_product1.product_id)
        assert item_pen_summary["name"] == sample_product1.name
        assert item_pen_summary["quantity"] == 2
        assert item_pen_summary["unit_price"] == 1.50
        assert item_pen_summary["subtotal"] == 3.00

    def test_finalize_order_ok(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 1)
        assert order.status == "pending"
        order.finalize_order()
        assert order._is_finalized
        assert order.status == "awaiting_payment"

    def test_finalize_empty_order(self):
        order = Order()
        with pytest.raises(ValueError, match="Cannot finalize an empty order."):
            order.finalize_order()

    def test_finalize_order_already_processed_status(self, sample_product1):
        order = Order()
        order.add_item(sample_product1, 1)
        order.update_status("processing")
        order.finalize_order() # Should just set _is_finalized to True, status unchanged
        assert order._is_finalized
        assert order.status == "processing"

    def test_order_repr(self, sample_product1):
        order = Order(order_id="repr_order_id")
        order.add_item(sample_product1, 3)
        expected_repr = "Order(id='repr_order_id', status='pending', items=1, total=4.5)"
        assert repr(order) == expected_repr