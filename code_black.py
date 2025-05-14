import uuid

class Product:
    """
    Represents a generic product in the system.
    """
    def __init__(self, name: str, price: float, product_id: str = None, quantity: int = 0):
        """Initializes a Product instance. Raises: TypeError, ValueError."""
        ...

    def get_details(self) -> dict:
        """Returns a dictionary with product details."""
        ...

    def update_quantity(self, change: int) -> None:
        """Updates the product quantity. Raises: TypeError, ValueError."""
        ...

    def apply_discount(self, discount_percentage: float) -> None:
        """Applies a discount to the product's price. Raises: TypeError, ValueError."""
        ...

    def __repr__(self):
        ...

class DigitalProduct(Product):
    """
    Represents a digital product, inheriting from Product.
    """
    def __init__(self, name: str, price: float, download_link: str, 
                 file_size_mb: float, product_id: str = None, quantity: int = 1):
        """Initializes a DigitalProduct. Raises: TypeError, ValueError."""
        ...

    def get_details(self) -> dict:
        """Returns a dictionary with digital product details."""
        ...

    def generate_new_download_link(self, base_url: str) -> str:
        """Generates a new pseudo-unique download link. Raises: TypeError."""
        ...

    def __repr__(self):
        ...


class PhysicalProduct(Product):
    """
    Represents a physical product, inheriting from Product.
    """
    def __init__(self, name: str, price: float, weight_kg: float, 
                 shipping_dimensions: tuple, product_id: str = None, quantity: int = 0):
        """Initializes a PhysicalProduct. Raises: TypeError, ValueError."""
        ...

    def get_details(self) -> dict:
        """Returns a dictionary with physical product details."""
        ...

    def calculate_shipping_cost(self, rate_per_kg: float, volumetric_factor: int = 5000) -> float:
        """Calculates shipping cost. Raises: ValueError."""
        ...

    def __repr__(self):
        ...


class Inventory:
    """
    Manages a collection of products.
    """
    def __init__(self):
        """Initializes the Inventory."""
        ...

    def add_product(self, product: Product, initial_stock: int = None) -> None:
        """Adds a product to the inventory. Raises: TypeError, ValueError."""
        ...

    def remove_product(self, product_id: str) -> Product:
        """Removes a product from inventory by ID. Raises: TypeError, KeyError."""
        ...

    def get_product(self, product_id: str) -> Product:
        """Retrieves a product from inventory by ID. Raises: TypeError, KeyError."""
        ...

    def update_stock(self, product_id: str, quantity_change: int) -> None:
        """Updates stock quantity of a product. Raises: TypeError, KeyError, ValueError."""
        ...


    def get_total_inventory_value(self) -> float:
        """Calculates the total value of all products in stock."""
        ...

    def find_products_by_name(self, search_term: str, case_sensitive: bool = False) -> list:
        """Finds products by partial name match. Raises: TypeError."""
        ...

    def get_products_in_price_range(self, min_price: float = 0, max_price: float = float('inf')) -> list:
        """Returns products in price range. Raises: ValueError."""
        ...

    def get_stock_level(self, product_id: str) -> int:
        """Gets stock level for a product. Raises: TypeError, KeyError."""
        ...


class Order:
    """
    Represents a customer order.
    """
    ALLOWED_STATUSES = ["pending", "awaiting_payment", "processing", "shipped", "delivered", "cancelled", "refunded"]

    def __init__(self, order_id: str = None, customer_id: str = None):
        """Initializes a new Order. Raises: TypeError."""
        ...

    def add_item(self, product: Product, quantity: int, inventory: Inventory = None) -> None:
        """Adds an item to the order. Raises: RuntimeError, TypeError, ValueError, KeyError."""
        ...

    def remove_item(self, product_id: str, quantity_to_remove: int, inventory: Inventory = None) -> None:
        """Removes item quantity from order. Raises: RuntimeError, TypeError, ValueError, KeyError."""
        ...


    def calculate_total(self) -> float:
        """Calculates the total cost of the order based on prices at time of purchase."""
        ...

    def update_status(self, new_status: str) -> None:
        """Updates the order status. Raises: TypeError, ValueError."""
        ...

    def get_order_summary(self) -> dict:
        """Returns a summary of the order."""
        ...

    def finalize_order(self):
        """Marks order as finalized. Raises: ValueError."""
        ...

    def __repr__(self):
        ...