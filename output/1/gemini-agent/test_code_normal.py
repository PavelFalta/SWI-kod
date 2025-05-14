'''
Unit tests for code_normal.py using pytest.
'''
import pytest
import uuid
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# Fixtures (if any become necessary)
@pytest.fixture
def sample_product():
    return Product(name="Test Book", price=29.99, quantity=10)

@pytest.fixture
def sample_digital_product():
    return DigitalProduct(name="Test Software", price=99.99, download_link="http://example.com/download", file_size_mb=500)

@pytest.fixture
def sample_physical_product():
    return PhysicalProduct(name="Test Laptop", price=1200.00, weight_kg=2.5, shipping_dimensions=(40, 30, 5), quantity=5)

@pytest.fixture
def empty_inventory():
    return Inventory()

@pytest.fixture
def inventory_with_products(sample_product, sample_digital_product, sample_physical_product):
    inventory = Inventory()
    # Create unique instances for inventory to avoid shared state issues if fixtures are modified
    p1 = Product(name="Book Alpha", price=10.0, product_id="p1", quantity=5)
    p2 = DigitalProduct(name="Software Beta", price=50.0, product_id="dp1", download_link="http://d.com/s", file_size_mb=100, quantity=2)
    p3 = PhysicalProduct(name="Widget Gamma", price=25.0, product_id="pp1", weight_kg=1, shipping_dimensions=(10,10,10), quantity=3)
    inventory.add_product(p1)
    inventory.add_product(p2)
    inventory.add_product(p3)
    return inventory

@pytest.fixture
def empty_order():
    return Order(order_id="order123", customer_id="cust456")


# Tests for Product class
class TestProduct:
    def test_product_creation_valid(self):
        p = Product(name="Laptop", price=1200.99, product_id="sku123", quantity=10)
        assert p.name == "Laptop"
        assert p.price == 1200.99
        assert p.product_id == "sku123"
        assert p.quantity == 10

    def test_product_creation_default_id_and_quantity(self):
        p = Product(name="Mouse", price=25.00)
        assert p.name == "Mouse"
        assert p.price == 25.00
        assert isinstance(p.product_id, str) and len(p.product_id) > 0
        assert p.quantity == 0

    @pytest.mark.parametrize("invalid_name", [123, None, "", "   "])
    def test_product_creation_invalid_name(self, invalid_name):
        with pytest.raises(TypeError if not isinstance(invalid_name, str) or invalid_name is None else ValueError):
            Product(name=invalid_name, price=10.0)

    @pytest.mark.parametrize("invalid_price", ["abc", None, 0, -10.0])
    def test_product_creation_invalid_price(self, invalid_price):
        with pytest.raises(TypeError if not isinstance(invalid_price, (int, float)) or invalid_price is None else ValueError):
            Product(name="Test", price=invalid_price)

    def test_product_creation_invalid_product_id_type(self):
        with pytest.raises(TypeError):
            Product(name="Test", price=10.0, product_id=123)

    @pytest.mark.parametrize("invalid_quantity", ["abc", None, -1])
    def test_product_creation_invalid_quantity(self, invalid_quantity):
        with pytest.raises(TypeError if not isinstance(invalid_quantity, int) or invalid_quantity is None else ValueError):
            Product(name="Test", price=10.0, quantity=invalid_quantity)

    def test_get_details(self, sample_product):
        details = sample_product.get_details()
        assert details["product_id"] == sample_product.product_id
        assert details["name"] == "Test Book"
        assert details["price"] == 29.99
        assert details["quantity"] == 10
        assert details["type"] == "GenericProduct"

    def test_update_quantity_valid_increase(self, sample_product):
        sample_product.update_quantity(5)
        assert sample_product.quantity == 15

    def test_update_quantity_valid_decrease(self, sample_product):
        sample_product.update_quantity(-5)
        assert sample_product.quantity == 5

    def test_update_quantity_invalid_type(self, sample_product):
        with pytest.raises(TypeError):
            sample_product.update_quantity("abc")

    def test_update_quantity_below_zero(self, sample_product):
        with pytest.raises(ValueError):
            sample_product.update_quantity(-100)

    def test_apply_discount_valid(self, sample_product):
        original_price = sample_product.price
        sample_product.apply_discount(10) # 10% discount
        assert sample_product.price == round(original_price * 0.9, 2)

    def test_apply_discount_zero(self, sample_product):
        original_price = sample_product.price
        sample_product.apply_discount(0)
        assert sample_product.price == original_price
    
    def test_apply_discount_hundred(self, sample_product):
        sample_product.apply_discount(100)
        assert sample_product.price == 0.0

    @pytest.mark.parametrize("invalid_discount", ["abc", None])
    def test_apply_discount_invalid_type(self, sample_product, invalid_discount):
        with pytest.raises(TypeError):
            sample_product.apply_discount(invalid_discount)

    @pytest.mark.parametrize("invalid_discount_value", [-10, 101])
    def test_apply_discount_invalid_range(self, sample_product, invalid_discount_value):
        with pytest.raises(ValueError):
            sample_product.apply_discount(invalid_discount_value)

    def test_product_repr(self, sample_product):
        expected_repr = f"Product(name='{sample_product.name}', price={sample_product.price}, id='{sample_product.product_id}', quantity={sample_product.quantity})"
        assert repr(sample_product) == expected_repr


# Tests for DigitalProduct class
class TestDigitalProduct:
    def test_digital_product_creation_valid(self):
        dp = DigitalProduct(name="Ebook", price=15.99, download_link="https://example.com/ebook.pdf", file_size_mb=5)
        assert dp.name == "Ebook"
        assert dp.price == 15.99
        assert dp.download_link == "https://example.com/ebook.pdf"
        assert dp.file_size_mb == 5.0
        assert dp.quantity == 1 # Default quantity for DigitalProduct
        assert isinstance(dp.product_id, str)

    @pytest.mark.parametrize("invalid_link", [123, None, "example.com"])
    def test_digital_product_creation_invalid_link(self, invalid_link):
        with pytest.raises(TypeError):
            DigitalProduct(name="Test", price=10.0, download_link=invalid_link, file_size_mb=10)

    @pytest.mark.parametrize("invalid_size", ["abc", None, 0, -5.0])
    def test_digital_product_creation_invalid_file_size(self, invalid_size):
        with pytest.raises(TypeError if not isinstance(invalid_size, (int, float)) or invalid_size is None else ValueError):
            DigitalProduct(name="Test", price=10.0, download_link="http://valid.com", file_size_mb=invalid_size)

    def test_digital_product_get_details(self, sample_digital_product):
        details = sample_digital_product.get_details()
        assert details["name"] == "Test Software"
        assert details["price"] == 99.99
        assert details["download_link"] == "http://example.com/download"
        assert details["file_size_mb"] == 500
        assert details["type"] == "DigitalProduct"
        assert "quantity" in details # Inherited from Product

    def test_generate_new_download_link_valid(self, sample_digital_product):
        old_link = sample_digital_product.download_link
        base_url = "https://newbase.com/downloads"
        new_link = sample_digital_product.generate_new_download_link(base_url)
        assert new_link != old_link
        assert new_link.startswith(base_url)
        assert sample_digital_product.product_id in new_link
        assert sample_digital_product.download_link == new_link

    @pytest.mark.parametrize("invalid_base_url", [123, None, "  "])
    def test_generate_new_download_link_invalid_base_url(self, sample_digital_product, invalid_base_url):
        with pytest.raises(TypeError):
            sample_digital_product.generate_new_download_link(invalid_base_url)

    def test_digital_product_repr(self, sample_digital_product):
        expected_repr = f"DigitalProduct(name='{sample_digital_product.name}', price={sample_digital_product.price}, id='{sample_digital_product.product_id}', link='{sample_digital_product.download_link}')"
        assert repr(sample_digital_product) == expected_repr

# Tests for PhysicalProduct class
class TestPhysicalProduct:
    def test_physical_product_creation_valid(self):
        pp = PhysicalProduct(name="Chair", price=89.50, weight_kg=15, shipping_dimensions=(50, 50, 90), quantity=3)
        assert pp.name == "Chair"
        assert pp.price == 89.50
        assert pp.weight_kg == 15.0
        assert pp.shipping_dimensions == (50, 50, 90)
        assert pp.quantity == 3
        assert isinstance(pp.product_id, str)

    @pytest.mark.parametrize("invalid_weight", ["abc", None, 0, -2.0])
    def test_physical_product_creation_invalid_weight(self, invalid_weight):
        with pytest.raises(TypeError if not isinstance(invalid_weight, (int,float)) or invalid_weight is None else ValueError):
            PhysicalProduct(name="Test", price=10.0, weight_kg=invalid_weight, shipping_dimensions=(1,1,1))

    @pytest.mark.parametrize("invalid_dims", [
        "abc", None, (1,2), (1,2,3,4), (1,2,"a"), (1,0,1), (-1,1,1)
    ])
    def test_physical_product_creation_invalid_dimensions(self, invalid_dims):
        with pytest.raises(TypeError):
            PhysicalProduct(name="Test", price=10.0, weight_kg=1.0, shipping_dimensions=invalid_dims)
    
    def test_physical_product_get_details(self, sample_physical_product):
        details = sample_physical_product.get_details()
        assert details["name"] == "Test Laptop"
        assert details["price"] == 1200.00
        assert details["weight_kg"] == 2.5
        assert details["shipping_dimensions_cm"] == (40, 30, 5)
        assert details["type"] == "PhysicalProduct"
        assert "quantity" in details

    def test_calculate_shipping_cost_weight_based(self, sample_physical_product):
        # weight_kg = 2.5, shipping_dimensions=(40, 30, 5)
        # Volumetric weight = (40*30*5)/5000 = 6000/5000 = 1.2
        # Chargeable weight = max(2.5, 1.2) = 2.5
        cost = sample_physical_product.calculate_shipping_cost(rate_per_kg=10)
        assert cost == 25.00 # 2.5 * 10

    def test_calculate_shipping_cost_volumetric_based(self):
        pp = PhysicalProduct(name="Feather Pillow", price=30, weight_kg=0.5, shipping_dimensions=(60, 40, 20)) # vol weight = 9.6
        # Volumetric weight = (60*40*20)/5000 = 48000/5000 = 9.6
        # Chargeable weight = max(0.5, 9.6) = 9.6
        cost = pp.calculate_shipping_cost(rate_per_kg=5, volumetric_factor=5000)
        assert cost == 48.00 # 9.6 * 5

    @pytest.mark.parametrize("invalid_rate", ["abc", None, 0, -10])
    def test_calculate_shipping_cost_invalid_rate(self, sample_physical_product, invalid_rate):
        with pytest.raises(TypeError if not isinstance(invalid_rate, (int,float)) or invalid_rate is None else ValueError):
            sample_physical_product.calculate_shipping_cost(rate_per_kg=invalid_rate)

    @pytest.mark.parametrize("invalid_factor", ["abc", None, 0, -5000])
    def test_calculate_shipping_cost_invalid_volumetric_factor(self, sample_physical_product, invalid_factor):
        with pytest.raises(TypeError if not isinstance(invalid_factor, int) or invalid_factor is None else ValueError):
            sample_physical_product.calculate_shipping_cost(rate_per_kg=10, volumetric_factor=invalid_factor)

    def test_physical_product_repr(self, sample_physical_product):
        expected_repr = f"PhysicalProduct(name='{sample_physical_product.name}', price={sample_physical_product.price}, id='{sample_physical_product.product_id}', weight={sample_physical_product.weight_kg}kg)"
        assert repr(sample_physical_product) == expected_repr

# Tests for Inventory class
class TestInventory:
    def test_inventory_add_product_valid(self, empty_inventory, sample_product):
        empty_inventory.add_product(sample_product)
        assert empty_inventory.get_product(sample_product.product_id) == sample_product
        assert sample_product.quantity == 10 # Original quantity

    def test_inventory_add_product_with_initial_stock(self, empty_inventory):
        p = Product("Temp", 1.0)
        empty_inventory.add_product(p, initial_stock=50)
        assert empty_inventory.get_product(p.product_id).quantity == 50

    def test_inventory_add_product_invalid_type(self, empty_inventory):
        with pytest.raises(TypeError):
            empty_inventory.add_product("not a product")

    def test_inventory_add_product_duplicate_id(self, empty_inventory, sample_product):
        empty_inventory.add_product(sample_product)
        with pytest.raises(ValueError, match=f"Product with ID {sample_product.product_id} already exists"):
            p_copy = Product(name="Copy", price=1, product_id=sample_product.product_id)
            empty_inventory.add_product(p_copy)

    @pytest.mark.parametrize("invalid_stock", ["abc", -1, None]) # None tests TypeError
    def test_inventory_add_product_invalid_initial_stock(self, empty_inventory, sample_product, invalid_stock):
        # Ensure product has a unique ID for this test to avoid conflicts
        p_unique = Product(name="Unique Prod", price=10.0, product_id=str(uuid.uuid4()))
        with pytest.raises(ValueError if isinstance(invalid_stock, int) else TypeError):
            empty_inventory.add_product(p_unique, initial_stock=invalid_stock)

    def test_inventory_remove_product_valid(self, inventory_with_products):
        removed_product = inventory_with_products.remove_product("p1")
        assert removed_product.name == "Book Alpha"
        with pytest.raises(KeyError):
            inventory_with_products.get_product("p1")

    def test_inventory_remove_product_invalid_id_type(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.remove_product(123)

    def test_inventory_remove_product_not_found(self, inventory_with_products):
        with pytest.raises(KeyError):
            inventory_with_products.remove_product("nonexistent_id")

    def test_inventory_get_product_valid(self, inventory_with_products):
        product = inventory_with_products.get_product("dp1")
        assert product.name == "Software Beta"

    def test_inventory_get_product_invalid_id_type(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.get_product(True)

    def test_inventory_get_product_not_found(self, inventory_with_products):
        with pytest.raises(KeyError):
            inventory_with_products.get_product("nonexistent_id")

    def test_inventory_update_stock_valid_increase(self, inventory_with_products):
        inventory_with_products.update_stock("p1", 5)
        assert inventory_with_products.get_product("p1").quantity == 10

    def test_inventory_update_stock_valid_decrease(self, inventory_with_products):
        inventory_with_products.update_stock("pp1", -2)
        assert inventory_with_products.get_product("pp1").quantity == 1

    def test_inventory_update_stock_invalid_id_type(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.update_stock(123, 5)

    def test_inventory_update_stock_product_not_found(self, inventory_with_products):
        with pytest.raises(KeyError):
            inventory_with_products.update_stock("nonexistent_id", 5)

    def test_inventory_update_stock_invalid_quantity_type(self, inventory_with_products):
        # Product.update_quantity raises TypeError for invalid quantity type
        with pytest.raises(TypeError):
            inventory_with_products.update_stock("p1", "abc")

    def test_inventory_update_stock_below_zero(self, inventory_with_products):
        # Product.update_quantity raises ValueError if quantity goes below zero
        # Original quantity of p1 is 5. Trying to decrease by 100.
        with pytest.raises(ValueError, match="Stock update for p1 failed: Quantity cannot be reduced below zero."):
            inventory_with_products.update_stock("p1", -100)

    def test_inventory_get_total_inventory_value_empty(self, empty_inventory):
        assert empty_inventory.get_total_inventory_value() == 0.0

    def test_inventory_get_total_inventory_value_with_products(self, inventory_with_products):
        # p1: 10.0 * 5 = 50
        # dp1: 50.0 * 2 = 100
        # pp1: 25.0 * 3 = 75
        # Total = 50 + 100 + 75 = 225
        assert inventory_with_products.get_total_inventory_value() == 225.00

    @pytest.mark.parametrize("search_term, case_sensitive, expected_count", [
        ("book", False, 1),
        ("Alpha", True, 1),
        ("beta", False, 1),
        ("ware", False, 1), # Software Beta
        ("Widget", True, 1),
        ("gamma", False, 1),
        ("ProductX", False, 0),
        ("alpha", True, 0) # Should not find "Book Alpha" if case sensitive
    ])
    def test_inventory_find_products_by_name(self, inventory_with_products, search_term, case_sensitive, expected_count):
        results = inventory_with_products.find_products_by_name(search_term, case_sensitive=case_sensitive)
        assert len(results) == expected_count
        if expected_count > 0:
            if case_sensitive:
                 assert search_term in results[0].name
            else:
                 assert search_term.lower() in results[0].name.lower()

    def test_inventory_find_products_by_name_empty_inventory(self, empty_inventory):
        assert empty_inventory.find_products_by_name("any") == []

    def test_inventory_find_products_by_name_invalid_search_term_type(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.find_products_by_name(123)

    @pytest.mark.parametrize("min_p, max_p, expected_ids", [
        (0, 1000, {"p1", "dp1", "pp1"}), # All products
        (20, 60, {"dp1", "pp1"}),      # Software Beta (50), Widget Gamma (25)
        (100, 200, set()),             # No products
        (10, 10, {"p1"}),              # Book Alpha (10)
        (0, 0, set()),
    ])
    def test_inventory_get_products_in_price_range(self, inventory_with_products, min_p, max_p, expected_ids):
        results = inventory_with_products.get_products_in_price_range(min_price=min_p, max_price=max_p)
        result_ids = {p.product_id for p in results}
        assert result_ids == expected_ids

    def test_inventory_get_products_in_price_range_empty_inventory(self, empty_inventory):
        assert empty_inventory.get_products_in_price_range(0, 100) == []

    @pytest.mark.parametrize("invalid_price", ["abc", -5, None])
    def test_inventory_get_products_in_price_range_invalid_min_price(self, inventory_with_products, invalid_price):
        with pytest.raises(ValueError if isinstance(invalid_price, (int, float)) else TypeError):
            inventory_with_products.get_products_in_price_range(min_price=invalid_price)

    @pytest.mark.parametrize("invalid_price", ["abc", None]) # float('inf') is default max, so -5 is fine if min_price < -5
    def test_inventory_get_products_in_price_range_invalid_max_price_type(self, inventory_with_products, invalid_price):
         with pytest.raises(TypeError):
            inventory_with_products.get_products_in_price_range(max_price=invalid_price)

    def test_inventory_get_products_in_price_range_invalid_max_price_less_than_min(self, inventory_with_products):
        with pytest.raises(ValueError):
            inventory_with_products.get_products_in_price_range(min_price=50, max_price=10)

    def test_inventory_get_stock_level_valid(self, inventory_with_products):
        assert inventory_with_products.get_stock_level("p1") == 5
        assert inventory_with_products.get_stock_level("dp1") == 2

    def test_inventory_get_stock_level_invalid_id_type(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.get_stock_level(12345)

    def test_inventory_get_stock_level_not_found(self, inventory_with_products):
        with pytest.raises(KeyError):
            inventory_with_products.get_stock_level("non_existent_id")


# Tests for Order class
class TestOrder:
    def test_order_creation_valid(self):
        order = Order()
        assert isinstance(order.order_id, str) and len(order.order_id) > 0
        assert order.customer_id is None
        assert order.items == {}
        assert order.status == "pending"
        assert not order._is_finalized

    def test_order_creation_with_ids(self):
        order = Order(order_id="custom_order_id", customer_id="custom_cust_id")
        assert order.order_id == "custom_order_id"
        assert order.customer_id == "custom_cust_id"

    @pytest.mark.parametrize("invalid_id", [123, True, []])
    def test_order_creation_invalid_order_id_type(self, invalid_id):
        with pytest.raises(TypeError):
            Order(order_id=invalid_id)

    @pytest.mark.parametrize("invalid_id", [123, True, {}])
    def test_order_creation_invalid_customer_id_type(self, invalid_id):
        with pytest.raises(TypeError):
            Order(customer_id=invalid_id)
    
    def test_order_add_item_valid_new_product(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 2)
        assert len(empty_order.items) == 1
        item_data = empty_order.items[sample_product.product_id]
        assert item_data["quantity"] == 2
        assert item_data["price_at_purchase"] == sample_product.price
        assert item_data["product_snapshot"]["name"] == sample_product.name

    def test_order_add_item_valid_existing_product(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 2)
        empty_order.add_item(sample_product, 3)
        assert empty_order.items[sample_product.product_id]["quantity"] == 5

    def test_order_add_item_with_inventory_sufficient_stock(self, empty_order, inventory_with_products):
        product_to_add = inventory_with_products.get_product("p1") # 5 in stock
        initial_stock = product_to_add.quantity
        empty_order.add_item(product_to_add, 3, inventory_with_products)
        assert empty_order.items[product_to_add.product_id]["quantity"] == 3
        assert inventory_with_products.get_product("p1").quantity == initial_stock - 3

    def test_order_add_item_with_inventory_insufficient_stock(self, empty_order, inventory_with_products):
        product_to_add = inventory_with_products.get_product("dp1") # 2 in stock
        with pytest.raises(ValueError, match="Not enough stock"):
            empty_order.add_item(product_to_add, 5, inventory_with_products)
        assert product_to_add.product_id not in empty_order.items # Item should not be added
        assert inventory_with_products.get_product("dp1").quantity == 2 # Stock unchanged

    def test_order_add_item_to_finalized_order(self, empty_order, sample_product):
        empty_order.finalize_order() # Finalizes if status is pending -> awaiting_payment
        if not empty_order.items: # finalize_order raises error if empty, so add dummy item if needed
             # Need a product with stock if using inventory, or just a product if not.
             # For this test, to isolate _is_finalized, we don't need inventory context for adding
             p_dummy = Product("Dummy",1)
             empty_order.add_item(p_dummy, 1) 
             empty_order.finalize_order()

        with pytest.raises(RuntimeError, match="Cannot add items to a finalized order"):
            empty_order.add_item(sample_product, 1)

    def test_order_add_item_invalid_product_type(self, empty_order):
        with pytest.raises(TypeError):
            empty_order.add_item("not a product", 1)

    @pytest.mark.parametrize("invalid_quantity", ["abc", 0, -1, None])
    def test_order_add_item_invalid_quantity(self, empty_order, sample_product, invalid_quantity):
        with pytest.raises(ValueError if isinstance(invalid_quantity, int) else TypeError):
            empty_order.add_item(sample_product, invalid_quantity)

    def test_order_add_item_invalid_inventory_type(self, empty_order, sample_product):
        with pytest.raises(TypeError):
            empty_order.add_item(sample_product, 1, inventory="not_inventory")
    
    def test_order_remove_item_valid_partial_quantity(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 5)
        empty_order.remove_item(sample_product.product_id, 2)
        assert empty_order.items[sample_product.product_id]["quantity"] == 3

    def test_order_remove_item_valid_all_quantity(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 5)
        empty_order.remove_item(sample_product.product_id, 5)
        assert sample_product.product_id not in empty_order.items

    def test_order_remove_item_with_inventory_restock(self, empty_order, inventory_with_products):
        prod_id = "p1"
        product_to_order = inventory_with_products.get_product(prod_id) # 5 in stock
        initial_inv_stock = product_to_order.quantity

        empty_order.add_item(product_to_order, 3, inventory_with_products)
        assert inventory_with_products.get_product(prod_id).quantity == initial_inv_stock - 3

        empty_order.remove_item(prod_id, 1, inventory_with_products)
        assert empty_order.items[prod_id]["quantity"] == 2
        assert inventory_with_products.get_product(prod_id).quantity == initial_inv_stock - 3 + 1

    @pytest.mark.parametrize("allowed_status", ["pending", "awaiting_payment"])
    def test_order_remove_item_from_finalized_order_allowed_status(self, empty_order, sample_product, allowed_status):
        empty_order.add_item(sample_product, 2)
        empty_order.status = allowed_status # Set status directly for testing
        empty_order._is_finalized = True # Manually set for test condition
        empty_order.remove_item(sample_product.product_id, 1)
        assert empty_order.items[sample_product.product_id]["quantity"] == 1

    @pytest.mark.parametrize("disallowed_status", ["shipped", "delivered", "cancelled", "refunded", "processing"])
    def test_order_remove_item_from_finalized_order_disallowed_status(self, empty_order, sample_product, disallowed_status):
        empty_order.add_item(sample_product, 2)
        empty_order.status = disallowed_status
        empty_order._is_finalized = True # Statuses like shipped make it finalized implicitly
        with pytest.raises(RuntimeError, match=f"Cannot remove items from an order with status '{disallowed_status}'."):
            empty_order.remove_item(sample_product.product_id, 1)

    def test_order_remove_item_invalid_product_id_type(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 1)
        with pytest.raises(TypeError):
            empty_order.remove_item(123, 1)

    @pytest.mark.parametrize("invalid_qty", ["abc", 0, -2, None])
    def test_order_remove_item_invalid_quantity_to_remove(self, empty_order, sample_product, invalid_qty):
        empty_order.add_item(sample_product, 5)
        with pytest.raises(ValueError if isinstance(invalid_qty, int) else TypeError):
            empty_order.remove_item(sample_product.product_id, invalid_qty)

    def test_order_remove_item_product_not_in_order(self, empty_order):
        with pytest.raises(KeyError):
            empty_order.remove_item("non_existent_id", 1)

    def test_order_remove_item_too_many_to_remove(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 2)
        with pytest.raises(ValueError, match="Cannot remove 3 units"):
            empty_order.remove_item(sample_product.product_id, 3)

    def test_order_remove_item_inventory_product_not_found_on_restock(self, empty_order, inventory_with_products):
        # Add product to order, depleting inventory (or at least getting it from there)
        prod_id_to_test = "dp1"
        product_in_inv = inventory_with_products.get_product(prod_id_to_test)
        empty_order.add_item(product_in_inv, 1, inventory_with_products)

        # Simulate product disappearing from inventory AFTER it was added to order
        inventory_with_products.remove_product(prod_id_to_test)
        
        with pytest.raises(RuntimeError, match=f"Product {prod_id_to_test} not found in inventory for restocking"):
            empty_order.remove_item(prod_id_to_test, 1, inventory_with_products)

    def test_order_calculate_total_empty_order(self, empty_order):
        assert empty_order.calculate_total() == 0.0

    def test_order_calculate_total_with_items(self, empty_order, sample_product, sample_digital_product):
        p1 = sample_product # price 29.99
        p2 = sample_digital_product # price 99.99
        empty_order.add_item(p1, 2) # 29.99 * 2 = 59.98
        empty_order.add_item(p2, 1) # 99.99 * 1 = 99.99
        # Total = 59.98 + 99.99 = 159.97
        assert empty_order.calculate_total() == 159.97

    @pytest.mark.parametrize("valid_status", Order.ALLOWED_STATUSES)
    def test_order_update_status_valid(self, empty_order, valid_status):
        # Skip special cases handled below
        if empty_order.status == "delivered" and valid_status not in ["delivered", "refunded"]:
            pytest.skip("Handled in specific test for delivered status change")
        if empty_order.status == "cancelled" and valid_status != "cancelled":
            pytest.skip("Handled in specific test for cancelled status change")
        
        empty_order.update_status(valid_status)
        assert empty_order.status == valid_status

    def test_order_update_status_invalid_type(self, empty_order):
        with pytest.raises(TypeError):
            empty_order.update_status(123)

    def test_order_update_status_invalid_value(self, empty_order):
        with pytest.raises(ValueError, match="Invalid order status 'unknown_status'"):
            empty_order.update_status("unknown_status")

    def test_order_update_status_from_delivered_to_invalid(self, empty_order):
        empty_order.status = "delivered"
        with pytest.raises(ValueError, match="Cannot change status from 'delivered' to 'pending'"):
            empty_order.update_status("pending")
        empty_order.update_status("refunded") # This should be allowed
        assert empty_order.status == "refunded"

    def test_order_update_status_from_cancelled_to_invalid(self, empty_order):
        empty_order.status = "cancelled"
        with pytest.raises(ValueError, match="Cannot change status of a 'cancelled' order."):
            empty_order.update_status("pending")
        empty_order.update_status("cancelled") # This should be allowed (no change)
        assert empty_order.status == "cancelled"

    @pytest.mark.parametrize("finalizing_status", ["shipped", "delivered", "cancelled", "refunded"])
    def test_order_update_status_finalizes_order(self, empty_order, finalizing_status):
        empty_order.update_status(finalizing_status)
        assert empty_order._is_finalized

    def test_order_get_order_summary_empty(self, empty_order):
        summary = empty_order.get_order_summary()
        assert summary["order_id"] == empty_order.order_id
        assert summary["customer_id"] == empty_order.customer_id
        assert summary["status"] == "pending"
        assert summary["total_items"] == 0
        assert summary["total_cost"] == 0.0
        assert summary["items"] == []

    def test_order_get_order_summary_with_items(self, empty_order, sample_product):
        p1 = sample_product # price 29.99, type Product
        empty_order.add_item(p1, 2)
        summary = empty_order.get_order_summary()
        assert summary["total_items"] == 2
        assert summary["total_cost"] == round(29.99 * 2, 2)
        assert len(summary["items"]) == 1
        item_summary = summary["items"][0]
        assert item_summary["product_id"] == p1.product_id
        assert item_summary["name"] == p1.name
        assert item_summary["quantity"] == 2
        assert item_summary["unit_price"] == p1.price
        assert item_summary["subtotal"] == round(p1.price * 2, 2)

    def test_order_finalize_order_valid(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 1)
        assert empty_order.status == "pending"
        empty_order.finalize_order()
        assert empty_order._is_finalized
        assert empty_order.status == "awaiting_payment"

    def test_order_finalize_order_empty_order(self, empty_order):
        with pytest.raises(ValueError, match="Cannot finalize an empty order."):
            empty_order.finalize_order()
    
    def test_order_finalize_order_when_not_pending(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 1)
        empty_order.update_status("processing")
        empty_order.finalize_order() # Should still set _is_finalized
        assert empty_order._is_finalized
        assert empty_order.status == "processing" # Status should not change from processing

    def test_order_repr(self, empty_order, sample_product):
        empty_order.add_item(sample_product, 1)
        expected_repr = f"Order(id='{empty_order.order_id}', status='{empty_order.status}', items=1, total={sample_product.price})"
        assert repr(empty_order) == expected_repr 