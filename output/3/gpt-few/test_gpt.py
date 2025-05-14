import sys
sys.path.append("..")
import pytest
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# ---------- FIXTURES ----------

@pytest.fixture
def product_data():
    return {"name": "Test Product", "price": 100.0, "quantity": 5}

@pytest.fixture
def digital_product_data():
    return {
        "name": "E-Book",
        "price": 15.5,
        "download_link": "https://example.com/ebook",
        "file_size_mb": 2.5,
        "quantity": 3
    }

@pytest.fixture
def sample_product(product_data):
    return Product(**product_data)

@pytest.fixture
def sample_digital_product(digital_product_data):
    return DigitalProduct(**digital_product_data)

@pytest.fixture
def physical_product_data():
    return {
        "name": "Laptop",
        "price": 1200.0,
        "weight_kg": 2.2,
        "shipping_dimensions": (35, 25, 3),
        "quantity": 10
    }

@pytest.fixture
def sample_physical_product(physical_product_data):
    return PhysicalProduct(**physical_product_data)

@pytest.fixture
def sample_inventory(sample_product, sample_digital_product, sample_physical_product):
    inv = Inventory()
    inv.add_product(sample_product)
    inv.add_product(sample_digital_product)
    inv.add_product(sample_physical_product)
    return inv

@pytest.fixture
def sample_order(sample_product):
    return Order(customer_id="cust-123")

# ---------- PRODUCT TESTS ----------

class TestProduct:
    def test_product_creation_ok(self, product_data):
        product = Product(**product_data)
        assert product.name == product_data["name"]
        assert product.price == product_data["price"]
        assert product.quantity == product_data["quantity"]
        assert isinstance(product.product_id, str)

    @pytest.mark.parametrize("name", ["", 123, None])
    def test_product_invalid_name(self, name, product_data):
        data = product_data.copy()
        data["name"] = name
        with pytest.raises(TypeError):
            Product(**data)

    @pytest.mark.parametrize("price", [0, -10, "free"])
    def test_product_invalid_price(self, price, product_data):
        data = product_data.copy()
        data["price"] = price
        with pytest.raises((ValueError, TypeError)):
            Product(**data)

    @pytest.mark.parametrize("quantity", [-1, "many"])
    def test_product_invalid_quantity(self, quantity, product_data):
        data = product_data.copy()
        data["quantity"] = quantity
        with pytest.raises((ValueError, TypeError)):
            Product(**data)

    def test_product_get_details(self, sample_product):
        details = sample_product.get_details()
        assert details["name"] == sample_product.name
        assert details["price"] == sample_product.price
        assert details["quantity"] == sample_product.quantity
        assert details["type"] == "GenericProduct"

    def test_update_quantity_ok(self, sample_product):
        sample_product.update_quantity(3)
        assert sample_product.quantity == 8
        sample_product.update_quantity(-2)
        assert sample_product.quantity == 6

    def test_update_quantity_invalid(self, sample_product):
        with pytest.raises(TypeError):
            sample_product.update_quantity("a")
        with pytest.raises(ValueError):
            sample_product.update_quantity(-100)

    def test_apply_discount_ok(self, sample_product):
        sample_product.apply_discount(10)
        assert sample_product.price == 90.0

    @pytest.mark.parametrize("discount", [-1, 101, "big"])
    def test_apply_discount_invalid(self, discount, sample_product):
        with pytest.raises((ValueError, TypeError)):
            sample_product.apply_discount(discount)

    def test_product_repr(self, sample_product):
        rep = repr(sample_product)
        assert sample_product.name in rep
        assert str(sample_product.price) in rep

# ---------- DIGITAL PRODUCT TESTS ----------

class TestDigitalProduct:
    def test_digital_product_creation_ok(self, digital_product_data):
        product = DigitalProduct(**digital_product_data)
        assert product.name == digital_product_data["name"]
        assert product.price == digital_product_data["price"]
        assert product.download_link == digital_product_data["download_link"]
        assert product.file_size_mb == digital_product_data["file_size_mb"]
        assert product.quantity == digital_product_data["quantity"]
        assert isinstance(product.product_id, str)

    def test_digital_product_creation_default_quantity(self):
        data = {"name": "Test App", "price": 9.99, "download_link": "https://example.com/app", "file_size_mb": 50.0}
        product = DigitalProduct(**data)
        assert product.quantity == 1

    @pytest.mark.parametrize("link", ["ftp://invalid.com", "example.com", 123])
    def test_digital_product_invalid_download_link(self, link, digital_product_data):
        data = digital_product_data.copy()
        data["download_link"] = link
        with pytest.raises(TypeError, match="Download link must be a valid URL string starting with http:// or https://."):
            DigitalProduct(**data)

    @pytest.mark.parametrize("size", [0, -10, "big"])
    def test_digital_product_invalid_file_size(self, size, digital_product_data):
        data = digital_product_data.copy()
        data["file_size_mb"] = size
        with pytest.raises((ValueError, TypeError)):
            DigitalProduct(**data)

    def test_digital_product_get_details(self, sample_digital_product):
        details = sample_digital_product.get_details()
        assert details["product_id"] == sample_digital_product.product_id
        assert details["name"] == sample_digital_product.name
        assert details["download_link"] == sample_digital_product.download_link
        assert details["file_size_mb"] == sample_digital_product.file_size_mb
        assert details["type"] == "DigitalProduct"
        assert details["quantity"] == sample_digital_product.quantity

    def test_generate_new_download_link(self, sample_digital_product):
        base_url = "https://newstore.com/downloads"
        original_link = sample_digital_product.download_link
        new_link = sample_digital_product.generate_new_download_link(base_url)
        assert new_link != original_link
        assert new_link.startswith(f"{base_url}/{sample_digital_product.product_id}/download_")
        assert sample_digital_product.download_link == new_link

    def test_generate_new_download_link_invalid_base_url(self, sample_digital_product):
        with pytest.raises(TypeError, match="Base URL must be a non-empty string."):
            sample_digital_product.generate_new_download_link("")

    def test_digital_product_repr(self, sample_digital_product):
        representation = repr(sample_digital_product)
        expected_repr = f"DigitalProduct(name='{sample_digital_product.name}', price={sample_digital_product.price}, id='{sample_digital_product.product_id}', link='{sample_digital_product.download_link}')"
        assert representation == expected_repr

# ---------- PHYSICAL PRODUCT TESTS ----------

class TestPhysicalProduct:
    def test_physical_product_creation_ok(self, physical_product_data):
        product = PhysicalProduct(**physical_product_data)
        assert product.name == physical_product_data["name"]
        assert product.price == physical_product_data["price"]
        assert product.weight_kg == physical_product_data["weight_kg"]
        assert product.shipping_dimensions == physical_product_data["shipping_dimensions"]
        assert product.quantity == physical_product_data["quantity"]

    @pytest.mark.parametrize("weight", [0, -1, "heavy"])
    def test_physical_product_invalid_weight(self, weight, physical_product_data):
        data = physical_product_data.copy()
        data["weight_kg"] = weight
        with pytest.raises((ValueError, TypeError)):
            PhysicalProduct(**data)

    @pytest.mark.parametrize("dims", [
        (0, 1, 1), (1, -1, 1), (1, 1, 0), (1, 1), "big", (1, 1, "a")
    ])
    def test_physical_product_invalid_dimensions(self, dims, physical_product_data):
        data = physical_product_data.copy()
        data["shipping_dimensions"] = dims
        with pytest.raises(TypeError):
            PhysicalProduct(**data)

    def test_physical_product_get_details(self, sample_physical_product):
        details = sample_physical_product.get_details()
        assert details["weight_kg"] == sample_physical_product.weight_kg
        assert details["shipping_dimensions_cm"] == sample_physical_product.shipping_dimensions
        assert details["type"] == "PhysicalProduct"

    def test_calculate_shipping_cost(self, sample_physical_product):
        cost = sample_physical_product.calculate_shipping_cost(rate_per_kg=100)
        assert isinstance(cost, float)
        assert cost > 0

    @pytest.mark.parametrize("rate", [0, -1, "fast"])
    def test_calculate_shipping_cost_invalid_rate(self, rate, sample_physical_product):
        with pytest.raises((ValueError, TypeError)):
            sample_physical_product.calculate_shipping_cost(rate)

    def test_physical_product_repr(self, sample_physical_product):
        rep = repr(sample_physical_product)
        assert sample_physical_product.name in rep
        assert str(sample_physical_product.weight_kg) in rep

# ---------- INVENTORY TESTS ----------

class TestInventory:
    def test_add_and_get_product(self, sample_product):
        inv = Inventory()
        inv.add_product(sample_product)
        fetched = inv.get_product(sample_product.product_id)
        assert fetched is sample_product

    def test_add_product_duplicate(self, sample_product):
        inv = Inventory()
        inv.add_product(sample_product)
        with pytest.raises(ValueError):
            inv.add_product(sample_product)

    def test_remove_product(self, sample_product):
        inv = Inventory()
        inv.add_product(sample_product)
        removed = inv.remove_product(sample_product.product_id)
        assert removed is sample_product
        with pytest.raises(KeyError):
            inv.get_product(sample_product.product_id)

    def test_update_stock(self, sample_product):
        inv = Inventory()
        inv.add_product(sample_product)
        inv.update_stock(sample_product.product_id, 2)
        assert inv.get_product(sample_product.product_id).quantity == sample_product.quantity + 2

    def test_update_stock_invalid(self, sample_product):
        inv = Inventory()
        inv.add_product(sample_product)
        with pytest.raises(ValueError):
            inv.update_stock(sample_product.product_id, -100)

    def test_get_total_inventory_value(self, sample_inventory):
        total = sample_inventory.get_total_inventory_value()
        assert isinstance(total, float)
        assert total > 0

    def test_find_products_by_name(self, sample_inventory):
        results = sample_inventory.find_products_by_name("book")
        assert any("book" in p.name.lower() for p in results)

    def test_get_products_in_price_range(self, sample_inventory):
        products = sample_inventory.get_products_in_price_range(10, 1000)
        for p in products:
            assert 10 <= p.price <= 1000

    def test_get_stock_level(self, sample_inventory, sample_product):
        level = sample_inventory.get_stock_level(sample_product.product_id)
        assert level == sample_product.quantity

# ---------- ORDER TESTS ----------

class TestOrder:
    def test_order_creation(self):
        order = Order(customer_id="cust-1")
        assert order.status == "pending"
        assert order.customer_id == "cust-1"
        assert isinstance(order.order_id, str)

    def test_add_item_and_calculate_total(self, sample_product):
        order = Order()
        order.add_item(sample_product, 2)
        assert order.items[sample_product.product_id]["quantity"] == 2
        assert order.calculate_total() == round(sample_product.price * 2, 2)

    def test_add_item_not_enough_stock(self, sample_product):
        inv = Inventory()
        inv.add_product(sample_product)
        order = Order()
        with pytest.raises(ValueError):
            order.add_item(sample_product, 100, inventory=inv)

    def test_remove_item(self, sample_product):
        order = Order()
        order.add_item(sample_product, 2)
        order.remove_item(sample_product.product_id, 1)
        assert order.items[sample_product.product_id]["quantity"] == 1
        order.remove_item(sample_product.product_id, 1)
        assert sample_product.product_id not in order.items

    def test_remove_item_invalid(self, sample_product):
        order = Order()
        with pytest.raises(KeyError):
            order.remove_item("nonexistent", 1)
        order.add_item(sample_product, 1)
        with pytest.raises(ValueError):
            order.remove_item(sample_product.product_id, 2)

    def test_update_status(self, sample_product):
        order = Order()
        order.add_item(sample_product, 1)
        order.update_status("processing")
        assert order.status == "processing"
        with pytest.raises(ValueError):
            order.update_status("unknown")

    def test_finalize_order(self, sample_product):
        order = Order()
        order.add_item(sample_product, 1)
        order.finalize_order()
        assert order.status == "awaiting_payment"
        assert order._is_finalized

    def test_finalize_empty_order(self):
        order = Order()
        with pytest.raises(ValueError):
            order.finalize_order()

    def test_get_order_summary(self, sample_product):
        order = Order()
        order.add_item(sample_product, 2)
        summary = order.get_order_summary()
        assert summary["total_items"] == 2
        assert summary["total_cost"] == round(sample_product.price * 2, 2)
        assert summary["status"] == order.status

    def test_order_repr(self, sample_product):
        order = Order()
        order.add_item(sample_product, 1)
        rep = repr(order)
        assert order.order_id in rep
        assert str(order.calculate_total()) in rep