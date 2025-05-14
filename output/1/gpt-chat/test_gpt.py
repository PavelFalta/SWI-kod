import pytest
import sys
sys.path.append("..")
from code_normal import (
    Product, DigitalProduct, PhysicalProduct, Inventory, Order
)

# ---------- PRODUCT ----------
def test_product_creation_valid():
    p = Product("Koska", 99.9, quantity=5)
    assert p.name == "Koska"
    assert p.price == 99.9
    assert isinstance(p.product_id, str)
    assert p.quantity == 5

def test_product_creation_invalid_name():
    with pytest.raises(TypeError):
        Product("", 1)
    with pytest.raises(TypeError):
        Product(123, 1)

def test_product_creation_invalid_price():
    with pytest.raises(ValueError):
        Product("A", -1)
    with pytest.raises(ValueError):
        Product("A", 0)
    with pytest.raises(ValueError):
        Product("A", "x")

def test_product_creation_invalid_product_id():
    with pytest.raises(TypeError):
        Product("B", 1, product_id=12345)

def test_product_creation_invalid_quantity():
    with pytest.raises(ValueError):
        Product("B", 1, quantity=-1)
    with pytest.raises(ValueError):
        Product("B", 1, quantity=2.5)

def test_product_get_details():
    p = Product("A", 10.0, product_id="abc", quantity=2)
    d = p.get_details()
    assert d["name"] == "A"
    assert d["product_id"] == "abc"
    assert d["quantity"] == 2
    assert d["type"] == "GenericProduct"

def test_update_quantity_valid():
    p = Product("A", 1.0, quantity=3)
    p.update_quantity(2)
    assert p.quantity == 5

def test_update_quantity_invalid():
    p = Product("A", 1.0, quantity=2)
    with pytest.raises(TypeError):
        p.update_quantity("x")
    with pytest.raises(ValueError):
        p.update_quantity(-3)

def test_apply_discount_valid():
    p = Product("A", 100)
    p.apply_discount(25)
    assert p.price == 75.0

def test_apply_discount_invalid():
    p = Product("A", 100)
    with pytest.raises(TypeError):
        p.apply_discount("abc")
    with pytest.raises(ValueError):
        p.apply_discount(-1)
    with pytest.raises(ValueError):
        p.apply_discount(101)

def test_product_repr():
    p = Product("Cake", 10, product_id="xyz", quantity=4)
    r = repr(p)
    assert "Cake" in r and "10.0" in r and "xyz" in r and "4" in r

# ---------- DIGITAL PRODUCT ----------
def test_digital_product_creation_valid():
    dp = DigitalProduct("SW", 50, "https://x.com/dl", 478)
    d = dp.get_details()
    assert d["download_link"].startswith("https://")
    assert d["file_size_mb"] == 478
    assert d["type"] == "DigitalProduct"

def test_digital_product_invalid_link():
    with pytest.raises(TypeError):
        DigitalProduct("SW", 10, "ftp://fail", 20)
    with pytest.raises(TypeError):
        DigitalProduct("SW", 10, 42, 20)

def test_digital_product_invalid_file_size():
    with pytest.raises(ValueError):
        DigitalProduct("SW", 10, "https://x.com", 0)
    with pytest.raises(ValueError):
        DigitalProduct("SW", 10, "https://x.com", -1)

def test_generate_new_download_link_valid():
    dp = DigitalProduct("SW", 30, "https://ok.com/dl", 123)
    new_link = dp.generate_new_download_link("https://base.url/dl")
    assert new_link.startswith("https://base.url/dl")
    assert dp.download_link == new_link
    # změna tokenu a ID ve výsledném odkazu
    assert dp.product_id in new_link

def test_generate_new_download_link_invalid():
    dp = DigitalProduct("SW", 20, "https://x.com/dl", 12)
    with pytest.raises(TypeError):
        dp.generate_new_download_link("")
    with pytest.raises(TypeError):
        dp.generate_new_download_link(None)

def test_digital_repr():
    dp = DigitalProduct("Soft", 10, "https://soft", 1)
    r = repr(dp)
    assert r.startswith("DigitalProduct")

# ---------- PHYSICAL PRODUCT ----------
def test_physical_product_valid():
    pp = PhysicalProduct("Chair", 70, 5.2, (32, 32, 140))
    d = pp.get_details()
    assert d["weight_kg"] == 5.2
    assert d["shipping_dimensions_cm"] == (32, 32, 140)
    assert d["type"] == "PhysicalProduct"

def test_physical_product_invalid_weight():
    with pytest.raises(ValueError):
        PhysicalProduct("A", 1, 0, (1,1,1))
    with pytest.raises(ValueError):
        PhysicalProduct("A", 1, -1, (1,1,1))

def test_physical_product_invalid_dims():
    with pytest.raises(TypeError):
        PhysicalProduct("A", 1, 1, (1,1))
    with pytest.raises(TypeError):
        PhysicalProduct("A", 1, 1, (1, 0, 1))
    with pytest.raises(TypeError):
        PhysicalProduct("A", 1, 1, ("x",1,1))

def test_calculate_shipping_cost_basic():
    pp = PhysicalProduct("Box", 5, 3, (10, 10, 10))
    # weight=3, volumetric = 1000/5000=0.2, charge = max(3,0.2)*10=30
    assert pp.calculate_shipping_cost(10) == 30

def test_calculate_shipping_cost_invalid():
    pp = PhysicalProduct("Box", 5, 3, (10,10,10))
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(0)
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(-1)
    with pytest.raises(ValueError):
        pp.calculate_shipping_cost(1, volumetric_factor=0)

def test_physical_repr():
    pp = PhysicalProduct("A", 1, 2, (1,2,3))
    r = repr(pp)
    assert r.startswith("PhysicalProduct")

# ---------- INVENTORY ----------
def test_inventory_add_and_get_product():
    inv = Inventory()
    p = Product("Coke", 5, product_id="id123")
    inv.add_product(p)
    assert inv.get_product("id123").name == "Coke"

def test_inventory_add_existing_raises():
    inv = Inventory()
    p = Product("X", 1, product_id="a")
    inv.add_product(p)
    with pytest.raises(ValueError):
        inv.add_product(Product("Y", 2, product_id="a"))

def test_inventory_add_invalid():
    inv = Inventory()
    with pytest.raises(TypeError):
        inv.add_product("not a product")
    with pytest.raises(ValueError):
        inv.add_product(Product("W", 2), initial_stock=-1)
    with pytest.raises(ValueError):
        inv.add_product(Product("W", 2), initial_stock=1.5)

def test_inventory_remove_product():
    inv = Inventory()
    p = Product("Cola", 2, product_id="z")
    inv.add_product(p)
    removed = inv.remove_product("z")
    assert removed.name == "Cola"
    with pytest.raises(KeyError):
        inv.remove_product("z")

def test_inventory_remove_invalid():
    inv = Inventory()
    with pytest.raises(TypeError):
        inv.remove_product(42)
    with pytest.raises(KeyError):
        inv.remove_product("noid")

def test_inventory_update_stock_and_value():
    inv = Inventory()
    p = Product("Bread", 20, product_id="bread", quantity=4)
    inv.add_product(p)
    inv.update_stock("bread", 1)
    assert p.quantity == 5
    with pytest.raises(ValueError):
        inv.update_stock("bread", -20)
    value = inv.get_total_inventory_value()
    assert value == 5 * 20

def test_inventory_find_by_name():
    inv = Inventory()
    p1 = Product("Red apple", 1)
    p2 = Product("Green apple", 2)
    p3 = Product("Pear", 3)
    inv.add_product(p1)
    inv.add_product(p2)
    inv.add_product(p3)
    res = inv.find_products_by_name("apple")
    assert len(res) == 2
    res = inv.find_products_by_name("APPLE", case_sensitive=True)
    assert len(res) == 0
    res = inv.find_products_by_name("Pear", case_sensitive=True)
    assert res[0].name == "Pear"
    with pytest.raises(TypeError):
        inv.find_products_by_name(123)

def test_inventory_price_range():
    inv = Inventory()
    inv.add_product(Product("a", 10))
    inv.add_product(Product("b", 20))
    inv.add_product(Product("c", 30))
    res = inv.get_products_in_price_range(15,25)
    assert len(res) == 1
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(-1,20)
    with pytest.raises(ValueError):
        inv.get_products_in_price_range(30,20)

def test_inventory_stock_level():
    inv = Inventory()
    p = Product("toy", 7, quantity=12, product_id="id2")
    inv.add_product(p)
    assert inv.get_stock_level("id2") == 12
    with pytest.raises(KeyError):
        inv.get_stock_level("noid")

# ---------- ORDER ----------
def test_order_basic_flow():
    inv = Inventory()
    p = Product("Cake", 20, product_id="cake1", quantity=12)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 2, inv)
    assert p.quantity == 10
    assert order.calculate_total() == 40
    order.remove_item("cake1", 1, inv)
    assert order.items["cake1"]["quantity"] == 1
    assert p.quantity == 11
    s = order.get_order_summary()
    assert s["total_items"] == 1
    assert s["total_cost"] == 20

def test_order_add_item_errors():
    inv = Inventory()
    p = Product("Biscuit", 20, product_id="p1", quantity=2)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 1, inv)
    with pytest.raises(TypeError):
        order.add_item("not product", 1)
    with pytest.raises(ValueError):
        order.add_item(p, 0, inv)
    with pytest.raises(ValueError):
        order.add_item(p, 5, inv)
    with pytest.raises(TypeError):
        order.add_item(p, 1, inventory="not inv")

def test_order_remove_item_errors():
    inv = Inventory()
    p = Product("Bis", 20, product_id="p2", quantity=10)
    inv.add_product(p)
    order = Order()
    order.add_item(p, 4, inv)
    with pytest.raises(KeyError):
        order.remove_item("invalid", 1, inv)
    with pytest.raises(ValueError):
        order.remove_item("p2", 20, inv)
    with pytest.raises(ValueError):
        order.remove_item("p2", 0, inv)
    with pytest.raises(TypeError):
        order.remove_item("p2", "str", inv)
    # zkusíme dotlačit order._is_finalized, status != pending, a zkusíme mazat
    order.finalize_order()
    order.update_status("shipped")
    with pytest.raises(RuntimeError):
        order.remove_item("p2", 1, inv)

def test_order_finalize_empty():
    order = Order()
    with pytest.raises(ValueError):
        order.finalize_order()

def test_order_status_flow():
    order = Order()
    order.finalize_order()
    order.update_status("processing")
    order.update_status("shipped")
    assert order.status == "shipped"
    with pytest.raises(ValueError):
        order.update_status("awaiting_payment")
    order.update_status("delivered")
    assert order.status == "delivered"
    # Nyní už stav kromě delivered/refunded není možný
    with pytest.raises(ValueError):
        order.update_status("cancelled")

def test_order_status_invalid():
    order = Order()
    with pytest.raises(TypeError):
        order.update_status(123)
    with pytest.raises(ValueError):
        order.update_status("notastatus")
    order.update_status("cancelled")
    with pytest.raises(ValueError):
        order.update_status("pending")

def test_order_repr():
    order = Order(order_id="z1", customer_id="c1")
    r = repr(order)
    assert "Order" in r

def test_order_get_order_summary_keys():
    order = Order()
    summary = order.get_order_summary()
    for k in ["order_id", "customer_id", "status", "total_items", "total_cost", "items"]:
        assert k in summary
