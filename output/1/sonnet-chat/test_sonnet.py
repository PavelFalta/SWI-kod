import pytest
import uuid
from copy import deepcopy
from unittest.mock import patch
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

class TestProduct:
    def test_product_initialization(self):
        product = Product("Test Product", 99.99)
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert isinstance(product.product_id, str)
        assert product.quantity == 0

    def test_product_initialization_with_id_and_quantity(self):
        product = Product("Test Product", 99.99, product_id="test123", quantity=10)
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.product_id == "test123"
        assert product.quantity == 10

    def test_product_name_validation(self):
        with pytest.raises(TypeError):
            Product("", 99.99)
        with pytest.raises(TypeError):
            Product(123, 99.99)
        with pytest.raises(TypeError):
            Product(None, 99.99)

    def test_product_price_validation(self):
        with pytest.raises(ValueError):
            Product("Test Product", 0)
        with pytest.raises(ValueError):
            Product("Test Product", -10)
        with pytest.raises(ValueError):
            Product("Test Product", "invalid_price")

    def test_product_id_validation(self):
        with pytest.raises(TypeError):
            Product("Test Product", 99.99, product_id=123)

    def test_product_quantity_validation(self):
        with pytest.raises(ValueError):
            Product("Test Product", 99.99, quantity=-1)
        with pytest.raises(ValueError):
            Product("Test Product", 99.99, quantity="invalid")

    def test_get_details(self):
        product = Product("Test Product", 99.99, product_id="test123", quantity=10)
        details = product.get_details()
        assert details["product_id"] == "test123"
        assert details["name"] == "Test Product"
        assert details["price"] == 99.99
        assert details["quantity"] == 10
        assert details["type"] == "GenericProduct"

    def test_update_quantity(self):
        product = Product("Test Product", 99.99, quantity=10)
        product.update_quantity(5)
        assert product.quantity == 15
        product.update_quantity(-5)
        assert product.quantity == 10

    def test_update_quantity_validation(self):
        product = Product("Test Product", 99.99, quantity=10)
        with pytest.raises(TypeError):
            product.update_quantity("invalid")
        with pytest.raises(ValueError):
            product.update_quantity(-15)

    def test_apply_discount(self):
        product = Product("Test Product", 100.00)
        product.apply_discount(20)
        assert product.price == 80.00
        product.apply_discount(10)
        assert product.price == 72.00

    def test_apply_discount_validation(self):
        product = Product("Test Product", 100.00)
        with pytest.raises(TypeError):
            product.apply_discount("invalid")
        with pytest.raises(ValueError):
            product.apply_discount(-10)
        with pytest.raises(ValueError):
            product.apply_discount(110)

    def test_repr(self):
        product = Product("Test Product", 99.99, product_id="test123", quantity=10)
        expected = "Product(name='Test Product', price=99.99, id='test123', quantity=10)"
        assert repr(product) == expected


class TestDigitalProduct:
    def test_digital_product_initialization(self):
        product = DigitalProduct("Digital Book", 19.99, "https://example.com/download", 15.5)
        assert product.name == "Digital Book"
        assert product.price == 19.99
        assert isinstance(product.product_id, str)
        assert product.quantity == 1  # Defaultně by měla být 1 u digitálních produktů
        assert product.download_link == "https://example.com/download"
        assert product.file_size_mb == 15.5

    def test_digital_product_with_custom_values(self):
        product = DigitalProduct("Digital Book", 19.99, "https://example.com/download", 15.5, 
                               product_id="digital123", quantity=100)
        assert product.name == "Digital Book"
        assert product.price == 19.99
        assert product.product_id == "digital123"
        assert product.quantity == 100
        assert product.download_link == "https://example.com/download"
        assert product.file_size_mb == 15.5

    def test_download_link_validation(self):
        with pytest.raises(TypeError):
            DigitalProduct("Digital Book", 19.99, "invalid-url", 15.5)
        with pytest.raises(TypeError):
            DigitalProduct("Digital Book", 19.99, 123, 15.5)

    def test_file_size_validation(self):
        with pytest.raises(ValueError):
            DigitalProduct("Digital Book", 19.99, "https://example.com", 0)
        with pytest.raises(ValueError):
            DigitalProduct("Digital Book", 19.99, "https://example.com", -5)
        with pytest.raises(ValueError):
            DigitalProduct("Digital Book", 19.99, "https://example.com", "invalid")

    def test_get_details(self):
        product = DigitalProduct("Digital Book", 19.99, "https://example.com/download", 15.5, 
                               product_id="digital123")
        details = product.get_details()
        assert details["product_id"] == "digital123"
        assert details["name"] == "Digital Book"
        assert details["price"] == 19.99
        assert details["quantity"] == 1
        assert details["download_link"] == "https://example.com/download"
        assert details["file_size_mb"] == 15.5
        assert details["type"] == "DigitalProduct"

    def test_generate_new_download_link(self):
        product = DigitalProduct("Digital Book", 19.99, "https://example.com/download", 15.5)
        new_link = product.generate_new_download_link("https://newexample.com")
        assert new_link.startswith("https://newexample.com/")
        assert product.product_id in new_link
        assert "download_" in new_link

    def test_generate_new_download_link_validation(self):
        product = DigitalProduct("Digital Book", 19.99, "https://example.com/download", 15.5)
        with pytest.raises(TypeError):
            product.generate_new_download_link("")
        with pytest.raises(TypeError):
            product.generate_new_download_link(123)

    def test_repr(self):
        product = DigitalProduct("Digital Book", 19.99, "https://example.com/download", 15.5, 
                               product_id="digital123")
        expected = "DigitalProduct(name='Digital Book', price=19.99, id='digital123', link='https://example.com/download')"
        assert repr(product) == expected


class TestPhysicalProduct:
    def test_physical_product_initialization(self):
        product = PhysicalProduct("Phone", 499.99, 0.5, (15, 8, 2))
        assert product.name == "Phone"
        assert product.price == 499.99
        assert isinstance(product.product_id, str)
        assert product.quantity == 0
        assert product.weight_kg == 0.5
        assert product.shipping_dimensions == (15, 8, 2)

    def test_physical_product_with_custom_values(self):
        product = PhysicalProduct("Phone", 499.99, 0.5, (15, 8, 2), 
                                product_id="phone123", quantity=20)
        assert product.name == "Phone"
        assert product.price == 499.99
        assert product.product_id == "phone123"
        assert product.quantity == 20
        assert product.weight_kg == 0.5
        assert product.shipping_dimensions == (15, 8, 2)

    def test_weight_validation(self):
        with pytest.raises(ValueError):
            PhysicalProduct("Phone", 499.99, 0, (15, 8, 2))
        with pytest.raises(ValueError):
            PhysicalProduct("Phone", 499.99, -1, (15, 8, 2))
        with pytest.raises(ValueError):
            PhysicalProduct("Phone", 499.99, "invalid", (15, 8, 2))

    def test_shipping_dimensions_validation(self):
        with pytest.raises(TypeError):
            PhysicalProduct("Phone", 499.99, 0.5, "invalid")
        with pytest.raises(TypeError):
            PhysicalProduct("Phone", 499.99, 0.5, (15, 8))  # Neúplné rozměry
        with pytest.raises(TypeError):
            PhysicalProduct("Phone", 499.99, 0.5, (15, 8, 0))  # Nulová hodnota
        with pytest.raises(TypeError):
            PhysicalProduct("Phone", 499.99, 0.5, (15, -8, 2))  # Záporná hodnota

    def test_get_details(self):
        product = PhysicalProduct("Phone", 499.99, 0.5, (15, 8, 2), product_id="phone123")
        details = product.get_details()
        assert details["product_id"] == "phone123"
        assert details["name"] == "Phone"
        assert details["price"] == 499.99
        assert details["quantity"] == 0
        assert details["weight_kg"] == 0.5
        assert details["shipping_dimensions_cm"] == (15, 8, 2)
        assert details["type"] == "PhysicalProduct"

    def test_calculate_shipping_cost(self):
        product = PhysicalProduct("Phone", 499.99, 0.5, (15, 8, 2))
        # Výpočet podle hmotnostní váhy
        cost = product.calculate_shipping_cost(10.0)
        assert cost == 5.0  # 0.5 kg * 10.0
        
        # Test s objemovou hmotností jako rozhodující faktor
        heavy_product = PhysicalProduct("TV", 999.99, 5.0, (100, 60, 10))
        # Objemová hmotnost: (100*60*10)/5000 = 12 kg, což je > 5 kg
        cost = heavy_product.calculate_shipping_cost(5.0)
        assert cost == 60.0  # 12 kg * 5.0

    def test_calculate_shipping_cost_validation(self):
        product = PhysicalProduct("Phone", 499.99, 0.5, (15, 8, 2))
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(0)
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(-5)
        with pytest.raises(ValueError):
            product.calculate_shipping_cost(10, 0)

    def test_repr(self):
        product = PhysicalProduct("Phone", 499.99, 0.5, (15, 8, 2), product_id="phone123")
        expected = "PhysicalProduct(name='Phone', price=499.99, id='phone123', weight=0.5kg)"
        assert repr(product) == expected


class TestInventory:
    @pytest.fixture
    def sample_products(self):
        return [
            Product("Generic Product", 29.99, product_id="gen123"),
            DigitalProduct("E-book", 9.99, "https://example.com/ebook", 2.5, product_id="dig123"),
            PhysicalProduct("Headphones", 99.99, 0.3, (20, 15, 8), product_id="phys123")
        ]

    @pytest.fixture
    def inventory_with_products(self, sample_products):
        inventory = Inventory()
        for product in sample_products:
            inventory.add_product(product, 10)
        return inventory

    def test_inventory_initialization(self):
        inventory = Inventory()
        assert inventory.products == {}

    def test_add_product(self, sample_products):
        inventory = Inventory()
        inventory.add_product(sample_products[0], 5)
        assert len(inventory.products) == 1
        assert inventory.products["gen123"].quantity == 5
        
        inventory.add_product(sample_products[1])
        assert inventory.products["dig123"].quantity == 0

    def test_add_product_validation(self, sample_products):
        inventory = Inventory()
        with pytest.raises(TypeError):
            inventory.add_product("not_a_product")
        
        # Přidání produktu, který již existuje
        inventory.add_product(sample_products[0])
        with pytest.raises(ValueError):
            inventory.add_product(sample_products[0])
        
        # Neplatný počáteční stav
        with pytest.raises(ValueError):
            inventory.add_product(sample_products[1], -5)

    def test_remove_product(self, inventory_with_products):
        removed = inventory_with_products.remove_product("gen123")
        assert removed.product_id == "gen123"
        assert len(inventory_with_products.products) == 2
        assert "gen123" not in inventory_with_products.products

    def test_remove_product_validation(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.remove_product(123)
        
        with pytest.raises(KeyError):
            inventory_with_products.remove_product("nonexistent")

    def test_get_product(self, inventory_with_products, sample_products):
        product = inventory_with_products.get_product("gen123")
        assert product.product_id == "gen123"
        assert product.name == sample_products[0].name

    def test_get_product_validation(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.get_product(123)
        
        with pytest.raises(KeyError):
            inventory_with_products.get_product("nonexistent")

    def test_update_stock(self, inventory_with_products):
        inventory_with_products.update_stock("gen123", 5)
        assert inventory_with_products.get_product("gen123").quantity == 15
        
        inventory_with_products.update_stock("gen123", -3)
        assert inventory_with_products.get_product("gen123").quantity == 12

    def test_update_stock_validation(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.update_stock(123, 5)
        
        with pytest.raises(KeyError):
            inventory_with_products.update_stock("nonexistent", 5)
        
        # Pokus o snížení zásoby pod nulu
        with pytest.raises(ValueError):
            inventory_with_products.update_stock("gen123", -15)

    def test_get_total_inventory_value(self, inventory_with_products, sample_products):
        expected_value = sum(p.price * 10 for p in sample_products)
        assert inventory_with_products.get_total_inventory_value() == expected_value

    def test_find_products_by_name(self, inventory_with_products):
        products = inventory_with_products.find_products_by_name("product")
        assert len(products) == 1
        assert products[0].product_id == "gen123"
        
        products = inventory_with_products.find_products_by_name("e", case_sensitive=False)
        assert len(products) == 3  # Všechny produkty obsahují "e" v názvu
        
        products = inventory_with_products.find_products_by_name("E", case_sensitive=True)
        assert len(products) == 1  # Jen "E-book" obsahuje velké "E"

    def test_find_products_by_name_validation(self, inventory_with_products):
        with pytest.raises(TypeError):
            inventory_with_products.find_products_by_name(123)

    def test_get_products_in_price_range(self, inventory_with_products):
        products = inventory_with_products.get_products_in_price_range(0, 50)
        assert len(products) == 2  # Generic Product a E-book
        
        products = inventory_with_products.get_products_in_price_range(50, 200)
        assert len(products) == 1  # Headphones
        
        products = inventory_with_products.get_products_in_price_range(100, 200)
        assert len(products) == 0  # Žádný produkt není dražší než 100

    def test_get_products_in_price_range_validation(self, inventory_with_products):
        with pytest.raises(ValueError):
            inventory_with_products.get_products_in_price_range(-10, 50)
        
        with pytest.raises(ValueError):
            inventory_with_products.get_products_in_price_range(50, 10)

    def test_get_stock_level(self, inventory_with_products):
        assert inventory_with_products.get_stock_level("gen123") == 10
        inventory_with_products.update_stock("gen123", 5)
        assert inventory_with_products.get_stock_level("gen123") == 15


class TestOrder:
    @pytest.fixture
    def sample_products(self):
        return [
            Product("Generic Product", 29.99, product_id="gen123"),
            DigitalProduct("E-book", 9.99, "https://example.com/ebook", 2.5, product_id="dig123"),
            PhysicalProduct("Headphones", 99.99, 0.3, (20, 15, 8), product_id="phys123")
        ]

    @pytest.fixture
    def inventory(self, sample_products):
        inventory = Inventory()
        for product in sample_products:
            inventory.add_product(product, 10)
        return inventory

    def test_order_initialization(self):
        order = Order()
        assert isinstance(order.order_id, str)
        assert order.customer_id is None
        assert order.items == {}
        assert order.status == "pending"
        assert order._is_finalized is False

    def test_order_initialization_with_ids(self):
        order = Order(order_id="order123", customer_id="cust123")
        assert order.order_id == "order123"
        assert order.customer_id == "cust123"

    def test_order_id_validation(self):
        with pytest.raises(TypeError):
            Order(order_id=123)

    def test_customer_id_validation(self):
        with pytest.raises(TypeError):
            Order(customer_id=123)

    def test_add_item(self, sample_products):
        order = Order()
        order.add_item(sample_products[0], 2)
        assert len(order.items) == 1
        assert order.items["gen123"]["quantity"] == 2
        assert order.items["gen123"]["price_at_purchase"] == 29.99

        # Přidání dalších kusů stejného produktu
        order.add_item(sample_products[0], 3)
        assert len(order.items) == 1
        assert order.items["gen123"]["quantity"] == 5

    def test_add_item_validation(self, sample_products):
        order = Order()
        with pytest.raises(TypeError):
            order.add_item("not_a_product", 1)
        
        with pytest.raises(ValueError):
            order.add_item(sample_products[0], 0)
        
        with pytest.raises(ValueError):
            order.add_item(sample_products[0], -1)

    def test_add_item_with_inventory(self, sample_products, inventory):
        order = Order()
        order.add_item(sample_products[0], 5, inventory)
        assert inventory.get_stock_level("gen123") == 5
        
        # Ověření, že nelze objednat více, než je skladem
        with pytest.raises(ValueError):
            order.add_item(sample_products[0], 10, inventory)

    def test_add_item_with_inventory_validation(self, sample_products):
        order = Order()
        with pytest.raises(TypeError):
            order.add_item(sample_products[0], 1, "not_an_inventory")

    def test_add_item_to_finalized_order(self, sample_products):
        order = Order()
        order.add_item(sample_products[0], 1)
        order._is_finalized = True
        
        with pytest.raises(RuntimeError):
            order.add_item(sample_products[1], 1)

    def test_remove_item(self, sample_products, inventory):
        order = Order()
        order.add_item(sample_products[0], 5, inventory)
        order.remove_item("gen123", 2, inventory)
        
        assert order.items["gen123"]["quantity"] == 3
        assert inventory.get_stock_level("gen123") == 7
        
        # Odebrání všech kusů by mělo odstranit produkt z objednávky
        order.remove_item("gen123", 3, inventory)
        assert "gen123" not in order.items
        assert inventory.get_stock_level("gen123") == 10

    def test_remove_item_validation(self, sample_products, inventory):
        order = Order()
        order.add_item(sample_products[0], 5, inventory)
        
        with pytest.raises(TypeError):
            order.remove_item(123, 1)
        
        with pytest.raises(ValueError):
            order.remove_item("gen123", 0)
        
        with pytest.raises(ValueError):
            order.remove_item("gen123", -1)
        
        with pytest.raises(KeyError):
            order.remove_item("nonexistent", 1)
        
        with pytest.raises(ValueError):
            order.remove_item("gen123", 10)
        
        # Nelze odebrat položky z finalizované objednávky v určitých stavech
        order.finalize_order()
        order.update_status("shipped")
        with pytest.raises(RuntimeError):
            order.remove_item("gen123", 1)

    def test_calculate_total(self, sample_products):
        order = Order()
        order.add_item(sample_products[0], 2)  # 2 * 29.99
        order.add_item(sample_products[1], 1)  # 1 * 9.99
        
        expected_total = 2 * 29.99 + 9.99
        assert order.calculate_total() == expected_total

    def test_update_status(self):
        order = Order()
        
        # Platné změny stavu
        order.update_status("awaiting_payment")
        assert order.status == "awaiting_payment"
        
        order.update_status("processing")
        assert order.status == "processing"
        
        order.update_status("shipped")
        assert order.status == "shipped"
        assert order._is_finalized is True

    def test_update_status_validation(self):
        order = Order()
        
        with pytest.raises(TypeError):
            order.update_status(123)
        
        with pytest.raises(ValueError):
            order.update_status("invalid_status")
        
        # Test nemožnosti změny z delivered na jinou hodnotu kromě refunded
        order.update_status("delivered")
        with pytest.raises(ValueError):
            order.update_status("processing")
        
        # Ale mělo by být možné změnit z delivered na refunded
        order.update_status("refunded")
        assert order.status == "refunded"
        
        # Resetujeme a testujeme, že nelze změnit stav cancelled
        order = Order()
        order.update_status("cancelled")
        with pytest.raises(ValueError):
            order.update_status("processing")

    def test_get_order_summary(self, sample_products):
        order = Order(order_id="order123", customer_id="cust123")
        order.add_item(sample_products[0], 2)  # 2 * 29.99
        order.add_item(sample_products[1], 1)  # 1 * 9.99
        
        summary = order.get_order_summary()
        assert summary["order_id"] == "order123"
        assert summary["customer_id"] == "cust123"
        assert summary["status"] == "pending"
        assert summary["total_items"] == 3
        assert summary["total_cost"] == 2 * 29.99 + 9.99
        assert len(summary["items"]) == 2

    def test_finalize_order(self, sample_products):
        order = Order()
        order.add_item(sample_products[0], 1)
        
        order.finalize_order()
        assert order._is_finalized is True
        assert order.status == "awaiting_payment"

    def test_finalize_empty_order(self):
        order = Order()
        with pytest.raises(ValueError):
            order.finalize_order()

    def test_repr(self, sample_products):
        order = Order(order_id="order123")
        order.add_item(sample_products[0], 2)
        expected = f"Order(id='order123', status='pending', items=1, total={2 * 29.99})"
        assert repr(order) == expected