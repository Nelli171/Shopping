
import json
import os
import getpass
PRODUCTS_FILE = 'products.json'
USERS_FILE = 'users.json'

class Product:
    # \"\"\"Represents a product in the catalog.\"\"\"
    def __init__(self, product_id: int, name: str, price: float, stock: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"{self.product_id}: {self.name} - ${self.price:.2f} (Stock: {self.stock})"


class Catalog:
    # \"\"\"Product catalog managing available products.\"\"\"

    def __init__(self):
        self.products = {}

    def load_products(self, filepath=PRODUCTS_FILE):
        if not os.path.exists(filepath):
            print(f"Products file {filepath} not found. Starting with empty catalog.")
            return
        with open(filepath, 'r') as f:
            data = json.load(f)
            for item in data:
                product = Product(
                    item['product_id'], item['name'], item['price'], item['stock']
                )
                self.products[product.product_id] = product

    def save_products(self, filepath=PRODUCTS_FILE):
        data = [
            {
                'product_id': p.product_id,
                'name': p.name,
                'price': p.price,
                'stock': p.stock
            }
            for p in self.products.values()
        ]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def list_products(self):
        print("\nAvailable Products:")
        for product in self.products.values():
            print(product)

    def get_product(self, product_id):
        return self.products.get(product_id)


class ShoppingCart:
    # \"\"\"Shopping cart for a user.\"\"\"

    def __init__(self):
        # key: product_id, value: quantity
        self.items = {}

    def add_item(self, product: Product, quantity: int):
        if product.stock < quantity:
            print(f"Only {product.stock} units of '{product.name}' are available.")
            return False
        current_quantity = self.items.get(product.product_id, 0)
        self.items[product.product_id] = current_quantity + quantity
        print(f"Added {quantity} x '{product.name}' to cart.")
        return True

    def remove_item(self, product_id: int):
        if product_id in self.items:
            del self.items[product_id]
            print(f"Removed product ID {product_id} from cart.")
        else:
            print(f"Product ID {product_id} is not in the cart.")

    def view_cart(self, catalog: Catalog):
        if not self.items:
            print("Your cart is empty.")
            return
        print("\nYour Cart:")
        total = 0.0
        for pid, qty in self.items.items():
            product = catalog.get_product(pid)
            if product:
                subtotal = product.price * qty
                total += subtotal
                print(f"{product.name}: {qty} x ${product.price:.2f} = ${subtotal:.2f}")
        print(f"Total: ${total:.2f}")

    def checkout(self, catalog: Catalog):
        if not self.items:
            print("Your cart is empty. Cannot checkout.")
            return False

        # Check stock availability again
        for pid, qty in self.items.items():
            product = catalog.get_product(pid)
            if not product or product.stock < qty:
                print(f"Insufficient stock for product {product.name if product else pid}. Checkout aborted.")
                return False

        # Deduct stock
        for pid, qty in self.items.items():
            product = catalog.get_product(pid)
            product.stock -= qty

        total = sum(catalog.get_product(pid).price * qty for pid, qty in self.items.items())
        print(f"\nCheckout successful! Total amount: ${total:.2f}")
        self.items.clear()
        return True


class User:
    # \"\"\"User with username, password, and shopping cart.\"\"\"

    def __init__(self, username: str, password: str, cart: ShoppingCart = None):
        self.username = username
        self.password = password
        self.cart = cart if cart else ShoppingCart()

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'cart': self.cart.items
        }

    @staticmethod
    def from_dict(data):
        user = User(data['username'], data['password'])
        cart = ShoppingCart()
        cart.items = data.get('cart', {})
        user.cart = cart
        return user


class Store:
    # \"\"\"Manages users and catalog.\"\"\"

    def __init__(self):
        self.catalog = Catalog()
        self.users = {}
        self.current_user = None

    def load_data(self):
        self.catalog.load_products()
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users_data = json.load(f)
                for udata in users_data:
                    user = User.from_dict(udata)
                    self.users[user.username] = user
        else:
            # Start with empty users
            self.users = {}

    def save_data(self):
        self.catalog.save_products()
        users_data = [user.to_dict() for user in self.users.values()]
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=4)

    def register_user(self):
        print("\n--- User Registration ---")
        username = input("Enter username: ").strip()
        if username in self.users:
            print("Username already exists. Try logging in.")
            return
        password = getpass.getpass("Enter password: ").strip()
        # Simple password validation
        if len(password) < 4:
            print("Password should be at least 4 characters.")
            return
        self.users[username] = User(username, password)
        print(f"User '{username}' registered successfully.")

    def login_user(self):
        print("\n--- User Login ---")
        username = input("Enter username: ").strip()
        password = getpass.getpass("Enter password: ").strip()
        user = self.users.get(username)
        if not user or user.password != password:
            print("Invalid username or password.")
            return False
        self.current_user = user
        print(f"Welcome back, {username}!")
        return True

    def logout_user(self):
        print(f"User '{self.current_user.username}' logged out.")
        self.current_user = None

    def user_menu(self):
        while True:
            print("\n--- Shopping Cart Menu ---")
            print("1. View Products")
            print("2. Add Product to Cart")
            print("3. Remove Product from Cart")
            print("4. View Cart")
            print("5. Checkout")
            print("6. Logout")
            choice = input("Select option: ").strip()
            if choice == "1":
                self.catalog.list_products()
            elif choice == "2":
                self.catalog.list_products()
                try:
                    pid = int(input("Enter Product ID to add: "))
                    product = self.catalog.get_product(pid)
                    if not product:
                        print("Invalid Product ID.")
                        continue
                    qty = int(input("Enter quantity: "))
                    if qty <= 0:
                        print("Quantity must be positive.")
                        continue
                    if product.stock < qty:
                        print(f"Sorry, only {product.stock} items available.")
                        continue
                    self.current_user.cart.add_item(product, qty)
                except ValueError:
                    print("Invalid input. Please enter numbers only.")
            elif choice == "3":
                self.current_user.cart.view_cart(self.catalog)
                try:
                    pid = int(input("Enter Product ID to remove from cart: "))
                    self.current_user.cart.remove_item(pid)
                except ValueError:
                    print("Invalid input.")
            elif choice == "4":
                self.current_user.cart.view_cart(self.catalog)
            elif choice == "5":
                if self.current_user.cart.checkout(self.catalog):
                    self.save_data()  # Save stock and cart changes after checkout
            elif choice == "6":
                self.logout_user()
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def run(self):
        print("Welcome to the Multi-User Shopping Cart")
        self.load_data()
        while True:
            print("\n--- Main Menu ---")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Select option: ").strip()
            if choice == "1":
                self.register_user()
                self.save_data()
            elif choice == "2":
                if self.login_user():
                    self.user_menu()
                    self.save_data()
            elif choice == "3":
                print("Thank you for visiting. Goodbye!")
                self.save_data()
                break
            else:
                print("Invalid choice. Please select a valid option.")


def main():
    store = Store()
    store.run()


if __name__ == '__main__':
    main()


