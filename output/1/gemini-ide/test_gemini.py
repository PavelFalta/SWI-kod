import sys
sys.path.append("..")
import pytest
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# --- Fixtures ---

@pytest.fixture
def sample_product_data():
    return {"name": "Test Book", "price": 25.99, "quantity": 10}

@pytest.fixture
def sample_product(sample_product_data):
    return Product(**sample_product_data)

@pytest.fixture
def sample_digital_product_data():
    return {
        "name": "E-Book Alpha",
        "price": 15.00,
        "download_link": "http://example.com/ebook.pdf",
        "file_size_mb": 2.5,
        "quantity": 1 # Digital products typically have quantity 1 or unlimited handled differently
    }

@pytest.fixture
def sample_digital_product(sample_digital_product_data):
    return DigitalProduct(**sample_digital_product_data)

@pytest.fixture
def sample_physical_product_data():
    return {
        "name": "Laptop Pro",
        "price": 1200.00,
        "weight_kg": 2.2,
        "shipping_dimensions": (40, 30, 5), # cm
        "quantity": 5
    }

@pytest.fixture
def sample_physical_product(sample_physical_product_data):
    return PhysicalProduct(**sample_physical_product_data)

@pytest.fixture
def empty_inventory():
    return Inventory()

@pytest.fixture
def populated_inventory(sample_product, sample_digital_product, sample_physical_product):
    inventory = Inventory()
    inventory.add_product(Product("Keyboard", 75.00, quantity=20, product_id="key123"))
    inventory.add_product(DigitalProduct("Software License", 299.99, "https://example.com/license", 0.1, product_id="soft456"))
    inventory.add_product(PhysicalProduct("Monitor", 350.50, 5.5, (60,40,10), quantity=8, product_id="mon789"))
    return inventory

@pytest.fixture
def empty_order():
    return Order(customer_id="cust123")

# --- Testy pro třídu Product ---

class TestProduct:
    def test_product_creation_valid(self, sample_product_data):
        product = Product(**sample_product_data)
        assert product.name == sample_product_data["name"]
        assert product.price == sample_product_data["price"]
        assert product.quantity == sample_product_data["quantity"]
        assert isinstance(product.product_id, str)

    def test_product_creation_with_id(self):
        product_id = "custom_id_123"
        product = Product("Custom Product", 50.0, product_id=product_id)
        assert product.product_id == product_id

    @pytest.mark.parametrize("invalid_name", [None, "", "  ", 123])
    def test_product_creation_invalid_name(self, invalid_name):
        with pytest.raises(TypeError):
            Product(invalid_name, 10.0)

    @pytest.mark.parametrize("invalid_price", [None, "abc", 0, -10])
    def test_product_creation_invalid_price(self, invalid_price):
        with pytest.raises((TypeError, ValueError)):
            Product("Valid Name", invalid_price)

    def test_product_creation_invalid_id_type(self):
        with pytest.raises(TypeError):
            Product("Valid Name", 10.0, product_id=12345)

    @pytest.mark.parametrize("invalid_quantity", [None, "abc", -1])
    def test_product_creation_invalid_quantity(self, invalid_quantity):
        with pytest.raises((TypeError, ValueError)):
            Product("Valid Name", 10.0, quantity=invalid_quantity)

    def test_get_details(self, sample_product):
        details = sample_product.get_details()
        assert details["product_id"] == sample_product.product_id
        assert details["name"] == sample_product.name
        assert details["price"] == sample_product.price
        assert details["quantity"] == sample_product.quantity
        assert details["type"] == "GenericProduct"

    def test_update_quantity_valid(self, sample_product):
        initial_quantity = sample_product.quantity
        sample_product.update_quantity(5)
        assert sample_product.quantity == initial_quantity + 5
        sample_product.update_quantity(-3)
        assert sample_product.quantity == initial_quantity + 2

    def test_update_quantity_invalid_type(self, sample_product):
        with pytest.raises(TypeError):
            sample_product.update_quantity("abc")

    def test_update_quantity_below_zero(self, sample_product):
        with pytest.raises(ValueError):
            sample_product.update_quantity(-(sample_product.quantity + 1))

    def test_apply_discount_valid(self, sample_product):
        initial_price = sample_product.price
        sample_product.apply_discount(10) # 10%
        assert sample_product.price == round(initial_price * 0.9, 2)

    @pytest.mark.parametrize("invalid_discount", [None, "abc", -5, 101])
    def test_apply_discount_invalid(self, sample_product, invalid_discount):
        with pytest.raises((TypeError, ValueError)):
            sample_product.apply_discount(invalid_discount)

    def test_product_repr(self, sample_product):
        assert repr(sample_product) == f"Product(name='{sample_product.name}', price={sample_product.price}, id='{sample_product.product_id}', quantity={sample_product.quantity})"


# --- Testy pro třídu DigitalProduct ---

class TestDigitalProduct:
    def test_digital_product_creation_valid(self, sample_digital_product_data):
        dp = DigitalProduct(**sample_digital_product_data)
        assert dp.name == sample_digital_product_data["name"]
        assert dp.price == sample_digital_product_data["price"]
        assert dp.download_link == sample_digital_product_data["download_link"]
        assert dp.file_size_mb == sample_digital_product_data["file_size_mb"]
        assert dp.quantity == sample_digital_product_data["quantity"]
        assert isinstance(dp.product_id, str)

    @pytest.mark.parametrize("invalid_link", [None, "ftp://example.com", "example.com", 123])
    def test_digital_product_invalid_link(self, sample_digital_product_data, invalid_link):
        data = sample_digital_product_data.copy()
        data["download_link"] = invalid_link
        with pytest.raises(TypeError):
            DigitalProduct(**data)

    @pytest.mark.parametrize("invalid_size", [None, "abc", 0, -1.0])
    def test_digital_product_invalid_file_size(self, sample_digital_product_data, invalid_size):
        data = sample_digital_product_data.copy()
        data["file_size_mb"] = invalid_size
        with pytest.raises((TypeError, ValueError)):
            DigitalProduct(**data)

    def test_digital_product_get_details(self, sample_digital_product):
        details = sample_digital_product.get_details()
        assert details["type"] == "DigitalProduct"
        assert "download_link" in details
        assert "file_size_mb" in details
        assert details["download_link"] == sample_digital_product.download_link

    def test_generate_new_download_link(self, sample_digital_product):
        old_link = sample_digital_product.download_link
        base_url = "https://newstore.com/downloads"
        new_link = sample_digital_product.generate_new_download_link(base_url)
        assert new_link != old_link
        assert new_link.startswith(base_url)
        assert sample_digital_product.product_id in new_link
        assert sample_digital_product.download_link == new_link

    def test_generate_new_download_link_invalid_base_url(self, sample_digital_product):
        with pytest.raises(TypeError):
            sample_digital_product.generate_new_download_link("")
        with pytest.raises(TypeError):
            sample_digital_product.generate_new_download_link(None)

    def test_digital_product_repr(self, sample_digital_product):
        r = repr(sample_digital_product)
        assert sample_digital_product.name in r
        assert str(sample_digital_product.price) in r
        assert sample_digital_product.product_id in r
        assert sample_digital_product.download_link in r
        assert r.startswith("DigitalProduct(")


# --- Testy pro třídu PhysicalProduct ---

class TestPhysicalProduct:
    def test_physical_product_creation_valid(self, sample_physical_product_data):
        pp = PhysicalProduct(**sample_physical_product_data)
        assert pp.name == sample_physical_product_data["name"]
        assert pp.weight_kg == sample_physical_product_data["weight_kg"]
        assert pp.shipping_dimensions == sample_physical_product_data["shipping_dimensions"]
        assert pp.quantity == sample_physical_product_data["quantity"]

    @pytest.mark.parametrize("invalid_weight", [None, "abc", 0, -2.0])
    def test_physical_product_invalid_weight(self, sample_physical_product_data, invalid_weight):
        data = sample_physical_product_data.copy()
        data["weight_kg"] = invalid_weight
        with pytest.raises((TypeError, ValueError)):
            PhysicalProduct(**data)

    @pytest.mark.parametrize("invalid_dims", [None, "abc", (10,20), (10,20,0), (10,-5,10), (10,20,"30")])
    def test_physical_product_invalid_dimensions(self, sample_physical_product_data, invalid_dims):
        data = sample_physical_product_data.copy()
        data["shipping_dimensions"] = invalid_dims
        with pytest.raises(TypeError): # TypeError covers all these due to tuple structure and type checks
            PhysicalProduct(**data)

    def test_physical_product_get_details(self, sample_physical_product):
        details = sample_physical_product.get_details()
        assert details["type"] == "PhysicalProduct"
        assert "weight_kg" in details
        assert "shipping_dimensions_cm" in details
        assert details["weight_kg"] == sample_physical_product.weight_kg

    def test_calculate_shipping_cost(self, sample_physical_product):
        # dimensions (40, 30, 5), weight 2.2kg
        # Volumetric weight = (40*30*5)/5000 = 6000/5000 = 1.2 kg
        # Chargeable weight = max(2.2, 1.2) = 2.2 kg
        cost = sample_physical_product.calculate_shipping_cost(rate_per_kg=10)
        assert cost == 22.00 # 2.2 * 10

        # Test volumetric weight dominance
        product_light_large = PhysicalProduct("Feather Box", 10, 0.5, (100,50,20), quantity=1)
        # Volumetric weight = (100*50*20)/5000 = 100000/5000 = 20 kg
        # Chargeable weight = max(0.5, 20) = 20 kg
        cost_vol = product_light_large.calculate_shipping_cost(rate_per_kg=5, volumetric_factor=5000)
        assert cost_vol == 100.00 # 20 * 5

    @pytest.mark.parametrize("invalid_rate", [None, "abc", 0, -5])
    def test_calculate_shipping_cost_invalid_rate(self, sample_physical_product, invalid_rate):
        with pytest.raises((TypeError, ValueError)):
            sample_physical_product.calculate_shipping_cost(invalid_rate)
            
    @pytest.mark.parametrize("invalid_factor", [None, "abc", 0, -5000])
    def test_calculate_shipping_cost_invalid_factor(self, sample_physical_product, invalid_factor):
        with pytest.raises((TypeError, ValueError)):
            sample_physical_product.calculate_shipping_cost(rate_per_kg=10, volumetric_factor=invalid_factor)

    def test_physical_product_repr(self, sample_physical_product):
        r = repr(sample_physical_product)
        assert sample_physical_product.name in r
        assert str(sample_physical_product.price) in r
        assert sample_physical_product.product_id in r
        assert str(sample_physical_product.weight_kg) in r
        assert r.startswith("PhysicalProduct(")


# --- Testy pro třídu Inventory ---

class TestInventory:
    def test_inventory_creation(self, empty_inventory):
        assert isinstance(empty_inventory.products, dict)
        assert len(empty_inventory.products) == 0

    def test_add_product_valid(self, empty_inventory, sample_product):
        empty_inventory.add_product(sample_product)
        assert sample_product.product_id in empty_inventory.products
        assert empty_inventory.products[sample_product.product_id] == sample_product

    def test_add_product_with_initial_stock(self, empty_inventory, sample_product_data):
        product = Product(sample_product_data["name"], sample_product_data["price"])
        initial_quantity = product.quantity # should be 0 initially if not specified
        assert initial_quantity == 0
        
        empty_inventory.add_product(product, initial_stock=50)
        assert product.product_id in empty_inventory.products
        assert empty_inventory.get_product(product.product_id).quantity == 50

    def test_add_product_invalid_initial_stock(self, empty_inventory, sample_product):
        with pytest.raises(ValueError):
            empty_inventory.add_product(sample_product, initial_stock=-5)
        with pytest.raises(TypeError):
            empty_inventory.add_product(sample_product, initial_stock="many")


    def test_add_product_duplicate_id(self, empty_inventory, sample_product):
        empty_inventory.add_product(sample_product)
        with pytest.raises(ValueError):
            another_product_same_id = Product("Another Name", 10.0, product_id=sample_product.product_id)
            empty_inventory.add_product(another_product_same_id)

    def test_add_product_invalid_type(self, empty_inventory):
        with pytest.raises(TypeError):
            empty_inventory.add_product("not a product")

    def test_remove_product_valid(self, populated_inventory):
        product_id_to_remove = "key123"
        assert product_id_to_remove in populated_inventory.products
        removed_product = populated_inventory.remove_product(product_id_to_remove)
        assert product_id_to_remove not in populated_inventory.products
        assert removed_product.product_id == product_id_to_remove

    def test_remove_product_not_found(self, empty_inventory):
        with pytest.raises(KeyError):
            empty_inventory.remove_product("non_existent_id")

    def test_remove_product_invalid_id_type(self, empty_inventory):
        with pytest.raises(TypeError):
            empty_inventory.remove_product(123)

    def test_get_product_valid(self, populated_inventory):
        product_id = "soft456"
        product = populated_inventory.get_product(product_id)
        assert product is not None
        assert product.product_id == product_id

    def test_get_product_not_found(self, populated_inventory):
        with pytest.raises(KeyError):
            populated_inventory.get_product("non_existent_id")

    def test_get_product_invalid_id_type(self, populated_inventory):
        with pytest.raises(TypeError):
            populated_inventory.get_product(12345)
            
    def test_update_stock_valid(self, populated_inventory):
        product_id = "key123"
        initial_stock = populated_inventory.get_product(product_id).quantity
        
        populated_inventory.update_stock(product_id, 5)
        assert populated_inventory.get_product(product_id).quantity == initial_stock + 5
        
        populated_inventory.update_stock(product_id, -3)
        assert populated_inventory.get_product(product_id).quantity == initial_stock + 2

    def test_update_stock_product_not_found(self, populated_inventory):
        with pytest.raises(KeyError):
            populated_inventory.update_stock("non_existent_id", 5)

    def test_update_stock_invalid_id_type(self, populated_inventory):
        with pytest.raises(TypeError):
            populated_inventory.update_stock(123, 5)

    def test_update_stock_resulting_negative(self, populated_inventory):
        product_id = "key123" # Has 20
        with pytest.raises(ValueError):
            populated_inventory.update_stock(product_id, -25)

    def test_get_total_inventory_value(self, populated_inventory):
        # key123: 75.00 * 20 = 1500
        # soft456: 299.99 * 1 = 299.99 (assuming default quantity for digital is 1)
        # mon789: 350.50 * 8 = 2804
        # Total = 1500 + 299.99 + 2804 = 4603.99
        # Need to ensure soft456 has quantity 1, as it was set during its fixture
        p_soft = populated_inventory.get_product("soft456")
        p_soft.quantity = 1 # Ensure quantity for digital product
        
        expected_value = (75.00 * 20) + (299.99 * 1) + (350.50 * 8)
        assert populated_inventory.get_total_inventory_value() == round(expected_value, 2)

    def test_find_products_by_name(self, populated_inventory):
        results_keyboard = populated_inventory.find_products_by_name("Keyboard")
        assert len(results_keyboard) == 1
        assert results_keyboard[0].name == "Keyboard"

        results_board_case_insensitive = populated_inventory.find_products_by_name("keyboard", case_sensitive=False)
        assert len(results_board_case_insensitive) == 1

        results_ware = populated_inventory.find_products_by_name("ware") # Software
        assert len(results_ware) == 1
        assert results_ware[0].name == "Software License"
        
        results_none = populated_inventory.find_products_by_name("XYZ_NonExistent")
        assert len(results_none) == 0

    def test_find_products_by_name_invalid_term(self, populated_inventory):
        with pytest.raises(TypeError):
            populated_inventory.find_products_by_name(123)

    def test_get_products_in_price_range(self, populated_inventory):
        # Products: Keyboard (75), Software (299.99), Monitor (350.50)
        results_mid_range = populated_inventory.get_products_in_price_range(min_price=100, max_price=300)
        assert len(results_mid_range) == 1
        assert results_mid_range[0].name == "Software License"

        results_all = populated_inventory.get_products_in_price_range()
        assert len(results_all) == 3

        results_low = populated_inventory.get_products_in_price_range(max_price=100)
        assert len(results_low) == 1
        assert results_low[0].name == "Keyboard"

        results_high = populated_inventory.get_products_in_price_range(min_price=350)
        assert len(results_high) == 1
        assert results_high[0].name == "Monitor"
        
        results_none = populated_inventory.get_products_in_price_range(min_price=1000)
        assert len(results_none) == 0

    @pytest.mark.parametrize("min_p, max_p", [(-1, 100), (10, "abc"), (100, 50)])
    def test_get_products_in_price_range_invalid(self, populated_inventory, min_p, max_p):
        with pytest.raises(ValueError):
            populated_inventory.get_products_in_price_range(min_price=min_p, max_price=max_p)
    
    def test_get_stock_level(self, populated_inventory):
        assert populated_inventory.get_stock_level("key123") == 20
        
        # Digital product quantity
        p_soft = populated_inventory.get_product("soft456")
        p_soft.quantity = 1 # ensure it's 1 for this test
        assert populated_inventory.get_stock_level("soft456") == 1

    def test_get_stock_level_not_found(self, populated_inventory):
        with pytest.raises(KeyError):
            populated_inventory.get_stock_level("non_existent")
            
    def test_get_stock_level_invalid_id_type(self, populated_inventory):
        with pytest.raises(TypeError):
            populated_inventory.get_stock_level(123)


# --- Testy pro třídu Order ---

class TestOrder:
    @pytest.fixture
    def product_for_order(self):
        return Product("Order Item", 10.00, quantity=100, product_id="order_prod_1")

    @pytest.fixture
    def product_for_order_2(self):
        return Product("Another Item", 25.50, quantity=50, product_id="order_prod_2")

    @pytest.fixture
    def inventory_for_order(self, product_for_order, product_for_order_2):
        inv = Inventory()
        # Create new product instances for inventory to avoid modifying fixture state directly in order tests
        inv.add_product(Product(product_for_order.name, product_for_order.price, product_id=product_for_order.product_id, quantity=product_for_order.quantity))
        inv.add_product(Product(product_for_order_2.name, product_for_order_2.price, product_id=product_for_order_2.product_id, quantity=product_for_order_2.quantity))
        return inv

    def test_order_creation(self):
        order = Order(customer_id="cust123")
        assert isinstance(order.order_id, str)
        assert order.customer_id == "cust123"
        assert order.status == "pending"
        assert not order._is_finalized
        assert isinstance(order.items, dict)

    def test_order_creation_with_id(self):
        order_id = "my_custom_order_id"
        order = Order(order_id=order_id)
        assert order.order_id == order_id

    @pytest.mark.parametrize("invalid_id", [123, False])
    def test_order_creation_invalid_id(self, invalid_id):
        with pytest.raises(TypeError):
            Order(order_id=invalid_id)
        with pytest.raises(TypeError):
            Order(customer_id=invalid_id)

    def test_add_item_no_inventory(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 2)
        assert product_for_order.product_id in empty_order.items
        assert empty_order.items[product_for_order.product_id]["quantity"] == 2
        assert empty_order.items[product_for_order.product_id]["price_at_purchase"] == product_for_order.price

        # Add more of the same item
        empty_order.add_item(product_for_order, 3)
        assert empty_order.items[product_for_order.product_id]["quantity"] == 5

    def test_add_item_with_inventory_sufficient_stock(self, empty_order, inventory_for_order, product_for_order):
        initial_inv_stock = inventory_for_order.get_stock_level(product_for_order.product_id)
        
        empty_order.add_item(product_for_order, 5, inventory=inventory_for_order)
        assert product_for_order.product_id in empty_order.items
        assert empty_order.items[product_for_order.product_id]["quantity"] == 5
        assert inventory_for_order.get_stock_level(product_for_order.product_id) == initial_inv_stock - 5

    def test_add_item_with_inventory_insufficient_stock(self, empty_order, inventory_for_order, product_for_order):
        with pytest.raises(ValueError, match="Not enough stock"):
            empty_order.add_item(product_for_order, product_for_order.quantity + 10, inventory=inventory_for_order)

    def test_add_item_to_finalized_order(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 1) # Add an item to make finalize possible
        empty_order.finalize_order() # status becomes awaiting_payment, _is_finalized = True
        with pytest.raises(RuntimeError, match="Cannot add items to a finalized order"):
            empty_order.add_item(product_for_order, 1)

    @pytest.mark.parametrize("invalid_product", [None, "not a product"])
    def test_add_item_invalid_product(self, empty_order, invalid_product):
        with pytest.raises(TypeError):
            empty_order.add_item(invalid_product, 1)

    @pytest.mark.parametrize("invalid_quantity", [None, "many", 0, -1])
    def test_add_item_invalid_quantity(self, empty_order, product_for_order, invalid_quantity):
        with pytest.raises((TypeError, ValueError)):
            empty_order.add_item(product_for_order, invalid_quantity)
            
    def test_add_item_invalid_inventory_type(self, empty_order, product_for_order):
        with pytest.raises(TypeError):
            empty_order.add_item(product_for_order, 1, inventory="not_inventory")


    def test_remove_item_partial(self, empty_order, product_for_order, inventory_for_order):
        empty_order.add_item(product_for_order, 5, inventory=inventory_for_order)
        initial_inv_stock = inventory_for_order.get_stock_level(product_for_order.product_id)

        empty_order.remove_item(product_for_order.product_id, 2, inventory=inventory_for_order)
        assert empty_order.items[product_for_order.product_id]["quantity"] == 3
        assert inventory_for_order.get_stock_level(product_for_order.product_id) == initial_inv_stock + 2
        
    def test_remove_item_all(self, empty_order, product_for_order, inventory_for_order):
        empty_order.add_item(product_for_order, 3, inventory=inventory_for_order)
        initial_inv_stock = inventory_for_order.get_stock_level(product_for_order.product_id)

        empty_order.remove_item(product_for_order.product_id, 3, inventory=inventory_for_order)
        assert product_for_order.product_id not in empty_order.items
        assert inventory_for_order.get_stock_level(product_for_order.product_id) == initial_inv_stock + 3

    def test_remove_item_not_in_order(self, empty_order):
        with pytest.raises(KeyError):
            empty_order.remove_item("non_existent_prod_id", 1)

    def test_remove_item_too_many(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 2)
        with pytest.raises(ValueError, match="Cannot remove 3 units"):
            empty_order.remove_item(product_for_order.product_id, 3)

    def test_remove_item_from_finalized_order_restricted(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 2)
        empty_order.update_status("shipped") # _is_finalized becomes True
        with pytest.raises(RuntimeError, match="Cannot remove items from an order with status 'shipped'"):
            empty_order.remove_item(product_for_order.product_id, 1)
            
    def test_remove_item_from_finalized_order_allowed(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 2)
        empty_order.finalize_order() # status: awaiting_payment, _is_finalized: True
        # This should be allowed as per logic: "if self._is_finalized and self.status not in ["pending", "awaiting_payment"]:"
        try:
            empty_order.remove_item(product_for_order.product_id, 1)
        except RuntimeError:
            pytest.fail("Removing item from 'awaiting_payment' finalized order raised RuntimeError unexpectedly.")
        assert empty_order.items[product_for_order.product_id]["quantity"] == 1


    @pytest.mark.parametrize("invalid_id", [None, 123])
    def test_remove_item_invalid_product_id(self, empty_order, invalid_id):
        with pytest.raises(TypeError):
            empty_order.remove_item(invalid_id, 1)

    @pytest.mark.parametrize("invalid_quantity", [None, "one", 0, -2])
    def test_remove_item_invalid_quantity(self, empty_order, product_for_order, invalid_quantity):
        empty_order.add_item(product_for_order, 5)
        with pytest.raises((TypeError, ValueError)):
            empty_order.remove_item(product_for_order.product_id, invalid_quantity)
            
    def test_remove_item_invalid_inventory_type(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 2)
        with pytest.raises(TypeError):
            empty_order.remove_item(product_for_order.product_id, 1, inventory="not_inventory")
            
    def test_remove_item_inventory_product_not_found_restock_error(self, empty_order, product_for_order, inventory_for_order):
        # Add item to order, simulate inventory interaction
        empty_order.add_item(product_for_order, 2, inventory_for_order)
        
        # Manually remove product from inventory to trigger the inconsistent state
        inventory_for_order.remove_product(product_for_order.product_id)
        
        with pytest.raises(RuntimeError, match="not found in inventory for restocking"):
            empty_order.remove_item(product_for_order.product_id, 1, inventory_for_order)


    def test_calculate_total(self, empty_order, product_for_order, product_for_order_2):
        empty_order.add_item(product_for_order, 2) # 2 * 10.00 = 20.00
        empty_order.add_item(product_for_order_2, 3) # 3 * 25.50 = 76.50
        # Total = 20.00 + 76.50 = 96.50
        assert empty_order.calculate_total() == 96.50

        # Test that price_at_purchase is used
        original_price = product_for_order.price
        product_for_order.price = 5.00 # Change price after adding to order
        assert empty_order.calculate_total() == 96.50 # Should still use 10.00 for product_for_order


    def test_update_status_valid(self, empty_order):
        valid_statuses = ["pending", "awaiting_payment", "processing", "shipped", "delivered", "cancelled", "refunded"]
        for status in valid_statuses:
            empty_order.status = "pending" # Reset for next transition (except for blocked ones)
            if status == "delivered": # Need a path to delivered first
                empty_order.update_status("shipped")
            if status == "refunded": # Need a path to delivered or other refundable state
                empty_order.status = "delivered" # set a state from which refund is possible
            
            if empty_order.status == "cancelled" and status != "cancelled": continue # Cannot change from cancelled
            if empty_order.status == "delivered" and status not in ["delivered", "refunded"]: continue # Limited changes from delivered

            empty_order.update_status(status)
            assert empty_order.status == status
            if status in ["shipped", "delivered", "cancelled", "refunded"]:
                assert empty_order._is_finalized

    def test_update_status_invalid_string(self, empty_order):
        with pytest.raises(ValueError, match="Invalid order status"):
            empty_order.update_status("non_existent_status")

    def test_update_status_invalid_type(self, empty_order):
        with pytest.raises(TypeError):
            empty_order.update_status(123)
            
    def test_update_status_from_delivered_invalid(self, empty_order):
        empty_order.update_status("delivered")
        with pytest.raises(ValueError, match="Cannot change status from 'delivered' to 'processing'"):
            empty_order.update_status("processing")
        # Should be allowed
        empty_order.update_status("refunded")
        assert empty_order.status == "refunded"

    def test_update_status_from_cancelled_invalid(self, empty_order):
        empty_order.update_status("cancelled")
        with pytest.raises(ValueError, match="Cannot change status of a 'cancelled' order."):
            empty_order.update_status("pending")
        # Should be allowed (no change)
        empty_order.update_status("cancelled")
        assert empty_order.status == "cancelled"


    def test_get_order_summary(self, empty_order, product_for_order, product_for_order_2):
        empty_order.add_item(product_for_order, 1) # 10.00
        empty_order.add_item(product_for_order_2, 2) # 2 * 25.50 = 51.00
        empty_order.customer_id = "test_cust_summary"
        
        summary = empty_order.get_order_summary()
        assert summary["order_id"] == empty_order.order_id
        assert summary["customer_id"] == "test_cust_summary"
        assert summary["status"] == "pending"
        assert summary["total_items"] == 3
        assert summary["total_cost"] == 61.00
        assert len(summary["items"]) == 2
        
        item1_summary = next(item for item in summary["items"] if item["product_id"] == product_for_order.product_id)
        assert item1_summary["name"] == product_for_order.name
        assert item1_summary["quantity"] == 1
        assert item1_summary["unit_price"] == product_for_order.price
        assert item1_summary["subtotal"] == product_for_order.price * 1


    def test_finalize_order_valid(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 1)
        assert empty_order.status == "pending"
        assert not empty_order._is_finalized

        empty_order.finalize_order()
        assert empty_order._is_finalized
        assert empty_order.status == "awaiting_payment" # Default status change from pending

    def test_finalize_order_empty(self, empty_order):
        with pytest.raises(ValueError, match="Cannot finalize an empty order."):
            empty_order.finalize_order()
            
    def test_finalize_order_already_processed_status(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 1)
        empty_order.update_status("processing")
        
        empty_order.finalize_order() # Should just set _is_finalized = True, status remains "processing"
        assert empty_order._is_finalized
        assert empty_order.status == "processing"


    def test_order_repr(self, empty_order, product_for_order):
        empty_order.add_item(product_for_order, 2)
        r = repr(empty_order)
        assert empty_order.order_id in r
        assert empty_order.status in r
        assert str(len(empty_order.items)) in r
        assert str(empty_order.calculate_total()) in r
        assert r.startswith("Order(")
