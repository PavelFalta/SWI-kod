import pytest
import uuid
import sys
sys.path.append("..")
from code_normal import Product, DigitalProduct, PhysicalProduct, Inventory, Order

# Product tests
class TestProduct:
    def test_init_valid(self):
        p = Product("Test Item", 19.99, quantity=5)
        assert p.name == "Test Item"
        assert p.price == 19.99
        assert p.quantity == 5
        assert isinstance(p.product_id, str)

    def test_init_invalid_name(self):
        with pytest.raises(TypeError):
            Product("", 10.0)
        with pytest.raises(TypeError):
            Product(123, 10.0)

    def test_init_invalid_price(self):
        with pytest.raises(ValueError):
            Product("Test", -10.0)
        with pytest.raises(ValueError):
            Product("Test", 0)

    def test_init_invalid_quantity(self):
        with pytest.raises(ValueError):
            Product("Test", 10.0, quantity=-1)

    def test_get_details(self):
        p = Product("Test", 10.0, product_id="123", quantity=5)
        details = p.get_details()
        assert details["name"] == "Test"
        assert details["price"] == 10.0
        assert details["product_id"] == "123"
        assert details["quantity"] == 5
        assert details["type"] == "GenericProduct"

    def test_update_quantity(self):
        p = Product("Test", 10.0, quantity=5)
        p.update_quantity(3)
        assert p.quantity == 8
        p.update_quantity(-3)
        assert p.quantity == 5
        
        with pytest.raises(ValueError):
            p.update_quantity(-10)

    def test_apply_discount(self):
        p = Product("Test", 100.0)
        p.apply_discount(20)
        assert p.price == 80.0
        
        with pytest.raises(ValueError):
            p.apply_discount(101)
        with pytest.raises(ValueError):
            p.apply_discount(-1)

# DigitalProduct tests
class TestDigitalProduct:
    def test_init_valid(self):
        dp = DigitalProduct("Ebook", 9.99, "https://example.com/download", 25.5)
        assert dp.name == "Ebook"
        assert dp.price == 9.99
        assert dp.download_link == "https://example.com/download"
        assert dp.file_size_mb == 25.5

    def test_init_invalid_link(self):
        with pytest.raises(TypeError):
            DigitalProduct("Ebook", 9.99, "example.com", 25.5)

    def test_init_invalid_size(self):
        with pytest.raises(ValueError):
            DigitalProduct("Ebook", 9.99, "https://example.com", -5)

    def test_get_details(self):
        dp = DigitalProduct("Ebook", 9.99, "https://example.com/download", 25.5, product_id="123")
        details = dp.get_details()
        assert details["download_link"] == "https://example.com/download"
        assert details["file_size_mb"] == 25.5
        assert details["type"] == "DigitalProduct"

    def test_generate_new_download_link(self):
        dp = DigitalProduct("Ebook", 9.99, "https://example.com/download", 25.5)
        new_link = dp.generate_new_download_link("https://newdomain.com")
        assert new_link.startswith("https://newdomain.com/")
        assert dp.product_id in new_link

# PhysicalProduct tests
class TestPhysicalProduct:
    def test_init_valid(self):
        pp = PhysicalProduct("Book", 15.99, 0.5, (20, 15, 3))
        assert pp.name == "Book"
        assert pp.price == 15.99
        assert pp.weight_kg == 0.5
        assert pp.shipping_dimensions == (20, 15, 3)

    def test_init_invalid_weight(self):
        with pytest.raises(ValueError):
            PhysicalProduct("Book", 15.99, -1, (20, 15, 3))

    def test_init_invalid_dimensions(self):
        with pytest.raises(TypeError):
            PhysicalProduct("Book", 15.99, 0.5, [20, 15, 3])
        with pytest.raises(TypeError):
            PhysicalProduct("Book", 15.99, 0.5, (20, 15))
        with pytest.raises(TypeError):
            PhysicalProduct("Book", 15.99, 0.5, (20, 15, -3))

    def test_get_details(self):
        pp = PhysicalProduct("Book", 15.99, 0.5, (20, 15, 3))
        details = pp.get_details()
        assert details["weight_kg"] == 0.5
        assert details["shipping_dimensions_cm"] == (20, 15, 3)
        assert details["type"] == "PhysicalProduct"

    def test_calculate_shipping_cost(self):
        pp = PhysicalProduct("Book", 15.99, 0.5, (20, 15, 3))
        cost = pp.calculate_shipping_cost(5.0)
        assert cost == 2.5  # 0.5kg * $5.0
        
        pp = PhysicalProduct("Large Box", 25.0, 1.0, (50, 40, 30))
        cost = pp.calculate_shipping_cost(5.0)
        # Volumetric weight: (50*40*30)/5000 = 12kg > actual weight 1kg
        assert cost == 60.0  # 12kg * $5.0

# Inventory tests
class TestInventory:
    def test_add_product(self):
        inv = Inventory()
        p = Product("Test", 10.0)
        inv.add_product(p)
        assert p.product_id in inv.products
        
        # Adding same product again should raise error
        with pytest.raises(ValueError):
            inv.add_product(p)
            
        # Test with initial stock
        p2 = Product("Test2", 20.0)
        inv.add_product(p2, 10)
        assert inv.products[p2.product_id].quantity == 10

    def test_remove_product(self):
        inv = Inventory()
        p = Product("Test", 10.0)
        inv.add_product(p)
        removed = inv.remove_product(p.product_id)
        assert removed is p
        assert p.product_id not in inv.products
        
        with pytest.raises(KeyError):
            inv.remove_product("nonexistent")

    def test_get_product(self):
        inv = Inventory()
        p = Product("Test", 10.0)
        inv.add_product(p)
        assert inv.get_product(p.product_id) is p
        
        with pytest.raises(KeyError):
            inv.get_product("nonexistent")

    def test_update_stock(self):
        inv = Inventory()
        p = Product("Test", 10.0, quantity=5)
        inv.add_product(p)
        inv.update_stock(p.product_id, 3)
        assert p.quantity == 8
        
        with pytest.raises(ValueError):
            inv.update_stock(p.product_id, -10)

    def test_get_total_inventory_value(self):
        inv = Inventory()
        p1 = Product("Test1", 10.0, quantity=5)
        p2 = Product("Test2", 20.0, quantity=3)
        inv.add_product(p1)
        inv.add_product(p2)
        assert inv.get_total_inventory_value() == 110.0  # (10*5) + (20*3)

    def test_find_products_by_name(self):
        inv = Inventory()
        p1 = Product("Test Product", 10.0)
        p2 = Product("Another Item", 20.0)
        inv.add_product(p1)
        inv.add_product(p2)
        
        results = inv.find_products_by_name("Test")
        assert len(results) == 1
        assert results[0] is p1
        
        results = inv.find_products_by_name("item", case_sensitive=False)
        assert len(results) == 1
        assert results[0] is p2

    def test_get_products_in_price_range(self):
        inv = Inventory()
        p1 = Product("Budget", 10.0)
        p2 = Product("Mid", 50.0)
        p3 = Product("Premium", 100.0)
        inv.add_product(p1)
        inv.add_product(p2)
        inv.add_product(p3)
        
        results = inv.get_products_in_price_range(0, 30)
        assert len(results) == 1
        assert results[0] is p1
        
        results = inv.get_products_in_price_range(20, 80)
        assert len(results) == 1
        assert results[0] is p2
        
        results = inv.get_products_in_price_range(0, 999)
        assert len(results) == 3

# Order tests
class TestOrder:
    def test_init(self):
        o = Order(customer_id="customer123")
        assert o.customer_id == "customer123"
        assert isinstance(o.order_id, str)
        assert o.status == "pending"
        assert not o._is_finalized

    def test_add_item(self):
        o = Order()
        p = Product("Test", 10.0, quantity=5)
        o.add_item(p, 2)
        
        assert p.product_id in o.items
        assert o.items[p.product_id]["quantity"] == 2
        assert o.items[p.product_id]["price_at_purchase"] == 10.0
        
        # Adding same product increases quantity
        o.add_item(p, 1)
        assert o.items[p.product_id]["quantity"] == 3

    def test_add_item_with_inventory(self):
        inv = Inventory()
        p = Product("Test", 10.0, quantity=5)
        inv.add_product(p)
        
        o = Order()
        o.add_item(p, 3, inv)
        assert inv.get_product(p.product_id).quantity == 2
        
        with pytest.raises(ValueError):
            o.add_item(p, 3, inv)  # Only 2 left in inventory

    def test_remove_item(self):
        o = Order()
        p = Product("Test", 10.0)
        o.add_item(p, 3)
        
        o.remove_item(p.product_id, 1)
        assert o.items[p.product_id]["quantity"] == 2
        
        o.remove_item(p.product_id, 2)
        assert p.product_id not in o.items
        
        with pytest.raises(KeyError):
            o.remove_item("nonexistent", 1)

    def test_calculate_total(self):
        o = Order()
        p1 = Product("Item1", 10.0)
        p2 = Product("Item2", 20.0)
        o.add_item(p1, 2)
        o.add_item(p2, 1)
        
        assert o.calculate_total() == 40.0  # (2*10) + (1*20)

    def test_update_status(self):
        o = Order()
        o.update_status("processing")
        assert o.status == "processing"
        
        with pytest.raises(ValueError):
            o.update_status("invalid_status")
        
        # Test status restrictions
        o.update_status("delivered")
        with pytest.raises(ValueError):
            o.update_status("processing")  # Can't go from delivered to processing

    def test_finalize_order(self):
        o = Order()
        p = Product("Test", 10.0)
        o.add_item(p, 1)
        
        o.finalize_order()
        assert o._is_finalized
        assert o.status == "awaiting_payment"
        
        with pytest.raises(RuntimeError):
            o.add_item(p, 1)  # Can't add to finalized order
            
        empty_order = Order()
        with pytest.raises(ValueError):
            empty_order.finalize_order()  # Can't finalize empty order

    def test_get_order_summary(self):
        o = Order(customer_id="customer123")
        p1 = Product("Item1", 10.0)
        p2 = Product("Item2", 20.0)
        o.add_item(p1, 2)
        o.add_item(p2, 1)
        
        summary = o.get_order_summary()
        assert summary["customer_id"] == "customer123"
        assert summary["total_items"] == 3
        assert summary["total_cost"] == 40.0
        assert len(summary["items"]) == 2