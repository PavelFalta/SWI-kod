import uuid

class Product:
    """
    Represents a generic product in the system.
    """
    def __init__(self, name: str, price: float, product_id: str = None, quantity: int = 0):
        """Initializes a Product instance. Raises: TypeError, ValueError."""
        if not isinstance(name, str) or not name.strip():
            raise TypeError("Product name must be a non-empty string.")
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("Product price must be a positive number.")
        if product_id is not None and not isinstance(product_id, str):
            raise TypeError("Product ID must be a string if provided.")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("Product quantity must be a non-negative integer.")

        self.name = name.strip()
        self.price = float(price)
        self.product_id = product_id if product_id else str(uuid.uuid4())
        self.quantity = quantity

    def get_details(self) -> dict:
        """Returns a dictionary with product details."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "type": "GenericProduct"
        }

    def update_quantity(self, change: int) -> None:
        """Updates the product quantity. Raises: TypeError, ValueError."""
        if not isinstance(change, int):
            raise TypeError("Quantity change must be an integer.")
        if self.quantity + change < 0:
            raise ValueError("Quantity cannot be reduced below zero.")
        self.quantity += change

    def apply_discount(self, discount_percentage: float) -> None:
        """Applies a discount to the product's price. Raises: TypeError, ValueError."""
        if not isinstance(discount_percentage, (int, float)):
            raise TypeError("Discount percentage must be a number.")
        if not 0 <= discount_percentage <= 100:
            raise ValueError("Discount percentage must be between 0 and 100.")
        self.price -= self.price * (discount_percentage / 100.0)
        self.price = round(self.price, 2)

    def __repr__(self):
        return f"Product(name='{self.name}', price={self.price}, id='{self.product_id}', quantity={self.quantity})"

class DigitalProduct(Product):
    """
    Represents a digital product, inheriting from Product.
    """
    def __init__(self, name: str, price: float, download_link: str, 
                 file_size_mb: float, product_id: str = None, quantity: int = 1):
        """Initializes a DigitalProduct. Raises: TypeError, ValueError."""
        super().__init__(name, price, product_id, quantity)
        if not isinstance(download_link, str) or not download_link.startswith(("http://", "https://")):
            raise TypeError("Download link must be a valid URL string starting with http:// or https://.")
        if not isinstance(file_size_mb, (int, float)) or file_size_mb <= 0:
            raise ValueError("File size must be a positive number.")

        self.download_link = download_link
        self.file_size_mb = float(file_size_mb)

    def get_details(self) -> dict:
        """Returns a dictionary with digital product details."""
        details = super().get_details()
        details.update({
            "download_link": self.download_link,
            "file_size_mb": self.file_size_mb,
            "type": "DigitalProduct"
        })
        return details

    def generate_new_download_link(self, base_url: str) -> str:
        """Generates a new pseudo-unique download link. Raises: TypeError."""
        if not isinstance(base_url, str) or not base_url.strip():
            raise TypeError("Base URL must be a non-empty string.")
        new_token = str(uuid.uuid4()).split('-')[0]
        self.download_link = f"{base_url.rstrip('/')}/{self.product_id}/download_{new_token}"
        return self.download_link

    def __repr__(self):
        return f"DigitalProduct(name='{self.name}', price={self.price}, id='{self.product_id}', link='{self.download_link}')"


class PhysicalProduct(Product):
    """
    Represents a physical product, inheriting from Product.
    """
    def __init__(self, name: str, price: float, weight_kg: float, 
                 shipping_dimensions: tuple, product_id: str = None, quantity: int = 0):
        """Initializes a PhysicalProduct. Raises: TypeError, ValueError."""
        super().__init__(name, price, product_id, quantity)
        if not isinstance(weight_kg, (int, float)) or weight_kg <= 0:
            raise ValueError("Weight must be a positive number.")
        if not (isinstance(shipping_dimensions, tuple) and len(shipping_dimensions) == 3 and
                all(isinstance(dim, (int, float)) and dim > 0 for dim in shipping_dimensions)):
            raise TypeError("Shipping dimensions must be a tuple of three positive numbers (length, width, height).")

        self.weight_kg = float(weight_kg)
        self.shipping_dimensions = shipping_dimensions

    def get_details(self) -> dict:
        """Returns a dictionary with physical product details."""
        details = super().get_details()
        details.update({
            "weight_kg": self.weight_kg,
            "shipping_dimensions_cm": self.shipping_dimensions,
            "type": "PhysicalProduct"
        })
        return details

    def calculate_shipping_cost(self, rate_per_kg: float, volumetric_factor: int = 5000) -> float:
        """Calculates shipping cost. Raises: ValueError."""
        if not isinstance(rate_per_kg, (int, float)) or rate_per_kg <= 0:
            raise ValueError("Rate per kg must be a positive number.")
        if not isinstance(volumetric_factor, int) or volumetric_factor <= 0:
            raise ValueError("Volumetric factor must be a positive integer.")
            
        volumetric_weight = (self.shipping_dimensions[0] * self.shipping_dimensions[1] * self.shipping_dimensions[2]) / volumetric_factor
        chargeable_weight = max(self.weight_kg, volumetric_weight)
        cost = chargeable_weight * rate_per_kg
        return round(cost, 2)

    def __repr__(self):
        return f"PhysicalProduct(name='{self.name}', price={self.price}, id='{self.product_id}', weight={self.weight_kg}kg)"


class Inventory:
    """
    Manages a collection of products.
    """
    def __init__(self):
        """Initializes the Inventory."""
        self.products = {}

    def add_product(self, product: Product, initial_stock: int = None) -> None:
        """Adds a product to the inventory. Raises: TypeError, ValueError."""
        if not isinstance(product, Product):
            raise TypeError("Item to add must be an instance of Product.")
        if product.product_id in self.products:
            raise ValueError(f"Product with ID {product.product_id} already exists in inventory.")
        
        if initial_stock is not None:
            if not isinstance(initial_stock, int) or initial_stock < 0:
                raise ValueError("Initial stock must be a non-negative integer.")
            product.quantity = initial_stock
            
        self.products[product.product_id] = product

    def remove_product(self, product_id: str) -> Product:
        """Removes a product from inventory by ID. Raises: TypeError, KeyError."""
        if not isinstance(product_id, str):
            raise TypeError("Product ID must be a string.")
        if product_id not in self.products:
            raise KeyError(f"Product with ID {product_id} not found in inventory.")
        return self.products.pop(product_id)

    def get_product(self, product_id: str) -> Product:
        """Retrieves a product from inventory by ID. Raises: TypeError, KeyError."""
        if not isinstance(product_id, str):
            raise TypeError("Product ID must be a string.")
        if product_id not in self.products:
            raise KeyError(f"Product with ID {product_id} not found in inventory.")
        return self.products[product_id]

    def update_stock(self, product_id: str, quantity_change: int) -> None:
        """Updates stock quantity of a product. Raises: TypeError, KeyError, ValueError."""
        if not isinstance(product_id, str):
            raise TypeError("Product ID must be a string.")
        product = self.get_product(product_id)
        
        try:
            product.update_quantity(quantity_change)
        except ValueError as e:
            raise ValueError(f"Stock update for {product_id} failed: {e}")


    def get_total_inventory_value(self) -> float:
        """Calculates the total value of all products in stock."""
        total_value = sum(p.price * p.quantity for p in self.products.values())
        return round(total_value, 2)

    def find_products_by_name(self, search_term: str, case_sensitive: bool = False) -> list:
        """Finds products by partial name match. Raises: TypeError."""
        if not isinstance(search_term, str):
            raise TypeError("Search term must be a string.")
        
        results = []
        for product in self.products.values():
            p_name = product.name
            s_term = search_term
            if not case_sensitive:
                p_name = product.name.lower()
                s_term = search_term.lower()
            if s_term in p_name:
                results.append(product)
        return results

    def get_products_in_price_range(self, min_price: float = 0, max_price: float = float('inf')) -> list:
        """Returns products in price range. Raises: ValueError."""
        if not isinstance(min_price, (int, float)) or min_price < 0:
            raise ValueError("Minimum price must be a non-negative number.")
        if not isinstance(max_price, (int, float)) or max_price < min_price:
            raise ValueError("Maximum price must be a number greater than or equal to minimum price.")

        return [p for p in self.products.values() if min_price <= p.price <= max_price]

    def get_stock_level(self, product_id: str) -> int:
        """Gets stock level for a product. Raises: TypeError, KeyError."""
        product = self.get_product(product_id)
        return product.quantity


class Order:
    """
    Represents a customer order.
    """
    ALLOWED_STATUSES = ["pending", "awaiting_payment", "processing", "shipped", "delivered", "cancelled", "refunded"]

    def __init__(self, order_id: str = None, customer_id: str = None):
        """Initializes a new Order. Raises: TypeError."""
        if order_id is not None and not isinstance(order_id, str):
            raise TypeError("Order ID must be a string if provided.")
        if customer_id is not None and not isinstance(customer_id, str):
            raise TypeError("Customer ID must be a string if provided.")
            
        self.order_id = order_id if order_id else str(uuid.uuid4())
        self.customer_id = customer_id
        self.items = {}
        self.status = "pending"
        self._is_finalized = False

    def add_item(self, product: Product, quantity: int, inventory: Inventory = None) -> None:
        """Adds an item to the order. Raises: RuntimeError, TypeError, ValueError, KeyError."""
        if self._is_finalized:
            raise RuntimeError("Cannot add items to a finalized order.")
        if not isinstance(product, Product):
            raise TypeError("Item to add must be an instance of Product.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        if inventory:
            if not isinstance(inventory, Inventory):
                raise TypeError("Inventory must be an Inventory instance.")
            inv_product = inventory.get_product(product.product_id)
            if inv_product.quantity < quantity:
                raise ValueError(f"Not enough stock for {product.name} (ID: {product.product_id}). Requested: {quantity}, Available: {inv_product.quantity}")
            inventory.update_stock(product.product_id, -quantity)

        product_snapshot = {
            "product_id": product.product_id,
            "name": product.name,
            "type": product.__class__.__name__
        }

        if product.product_id in self.items:
            self.items[product.product_id]["quantity"] += quantity
        else:
            self.items[product.product_id] = {
                "product_snapshot": product_snapshot, 
                "quantity": quantity,
                "price_at_purchase": product.price
            }

    def remove_item(self, product_id: str, quantity_to_remove: int, inventory: Inventory = None) -> None:
        """Removes item quantity from order. Raises: RuntimeError, TypeError, ValueError, KeyError."""
        if self._is_finalized and self.status not in ["pending", "awaiting_payment"]:
             raise RuntimeError(f"Cannot remove items from an order with status '{self.status}'.")
        if not isinstance(product_id, str):
            raise TypeError("Product ID must be a string.")
        if not isinstance(quantity_to_remove, int) or quantity_to_remove <= 0:
            raise ValueError("Quantity to remove must be a positive integer.")
        
        if product_id not in self.items:
            raise KeyError(f"Product with ID {product_id} not found in order.")

        if self.items[product_id]["quantity"] < quantity_to_remove:
            raise ValueError(f"Cannot remove {quantity_to_remove} units of {product_id}; only {self.items[product_id]['quantity']} in order.")

        self.items[product_id]["quantity"] -= quantity_to_remove
        
        if inventory:
            if not isinstance(inventory, Inventory):
                raise TypeError("Inventory must be an Inventory instance.")
            try:
                inventory.update_stock(product_id, quantity_to_remove)
            except KeyError:
                raise RuntimeError(f"Product {product_id} not found in inventory for restocking. Inconsistent state.")


        if self.items[product_id]["quantity"] == 0:
            del self.items[product_id]


    def calculate_total(self) -> float:
        """Calculates the total cost of the order based on prices at time of purchase."""
        total_cost = sum(item_data["price_at_purchase"] * item_data["quantity"] for item_data in self.items.values())
        return round(total_cost, 2)

    def update_status(self, new_status: str) -> None:
        """Updates the order status. Raises: TypeError, ValueError."""
        if not isinstance(new_status, str):
            raise TypeError("New status must be a string.")
        if new_status.lower() not in self.ALLOWED_STATUSES:
            raise ValueError(f"Invalid order status '{new_status}'. Allowed statuses are: {', '.join(self.ALLOWED_STATUSES)}")
        
        if self.status == "delivered" and new_status not in ["delivered", "refunded"]:
            raise ValueError(f"Cannot change status from 'delivered' to '{new_status}'.")
        if self.status == "cancelled" and new_status != "cancelled":
            raise ValueError("Cannot change status of a 'cancelled' order.")
            
        self.status = new_status.lower()
        if self.status in ["shipped", "delivered", "cancelled", "refunded"]:
            self._is_finalized = True

    def get_order_summary(self) -> dict:
        """Returns a summary of the order."""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "status": self.status,
            "total_items": sum(item["quantity"] for item in self.items.values()),
            "total_cost": self.calculate_total(),
            "items": [
                {
                    "product_id": pid,
                    "name": data["product_snapshot"]["name"],
                    "quantity": data["quantity"],
                    "unit_price": data["price_at_purchase"],
                    "subtotal": round(data["price_at_purchase"] * data["quantity"], 2)
                } for pid, data in self.items.items()
            ]
        }

    def finalize_order(self):
        """Marks order as finalized. Raises: ValueError."""
        if not self.items:
            raise ValueError("Cannot finalize an empty order.")
        self._is_finalized = True
        if self.status == "pending":
            self.status = "awaiting_payment" 

    def __repr__(self):
        return f"Order(id='{self.order_id}', status='{self.status}', items={len(self.items)}, total={self.calculate_total()})"