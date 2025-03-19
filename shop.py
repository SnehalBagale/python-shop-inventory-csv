import csv
from tabulate import tabulate

class Product:
    def __init__(self, product_id, name, price, quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_quantity(self, quantity_sold):
        if quantity_sold > self.quantity:
            return False  # Not enough stock
        self.quantity -= quantity_sold
        return True

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.name,
            "price": self.price,
            "quantity": self.quantity
        }

class Inventory:
    def __init__(self):
        self.products = {}
        self.load_from_file()

    def add_product(self, product):
        self.products[product.product_id] = product
        self.save_to_file()

    def view_inventory(self):
        return [product.to_dict() for product in self.products.values()]

    def update_product(self, product_id, quantity_sold):
        if product_id in self.products:
            return self.products[product_id].update_quantity(quantity_sold)
        return False

    def save_to_file(self):
        with open("inventory.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["product_id", "product_name", "price", "quantity"])
            writer.writeheader()
            for product in self.products.values():
                writer.writerow(product.to_dict())

    def load_from_file(self):
        try:
            with open("inventory.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.products[row["product_id"]] = Product(
                        row["product_id"], row["product_name"], float(row["price"]), int(row["quantity"])
                    )
        except FileNotFoundError:
            pass

class Sale:
    def __init__(self, sale_id):
        self.sale_id = sale_id
        self.products_sold = []

    def add_product(self, product, quantity):
        self.products_sold.append((product, quantity))

    def calculate_total(self):
        return sum(product.price * quantity for product, quantity in self.products_sold)

    def to_dict(self):
        return [{"sale_id": self.sale_id, "product_id": p.product_id, "product_name": p.name,
                 "quantity_sold": q, "total_price": p.price * q} for p, q in self.products_sold]

class SalesManager:
    def __init__(self, inventory):
        self.inventory = inventory
        self.sales = []
        self.load_from_file()

    def record_sale(self, sale):
        for product, quantity in sale.products_sold:
            self.inventory.update_product(product.product_id, quantity)
        self.sales.append(sale)
        self.save_to_file()

    def view_sales_report(self):
        return [entry for sale in self.sales for entry in sale.to_dict()]

    def save_to_file(self):
        with open("sales.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["sale_id", "product_id", "product_name", "quantity_sold", "total_price"])
            writer.writeheader()
            for sale in self.sales:
                for entry in sale.to_dict():
                    writer.writerow(entry)

    def load_from_file(self):
        try:
            with open("sales.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    sale = Sale(row["sale_id"])
                    product = self.inventory.products.get(row["product_id"])
                    if product:
                        sale.add_product(product, int(row["quantity_sold"]))
                    self.sales.append(sale)
        except FileNotFoundError:
            pass

class ShopSystem:
    def __init__(self):
        self.inventory = Inventory()
        self.sales_manager = SalesManager(self.inventory)

    def display_menu(self):
        while True:
            print("\n--- Small Shop Management System ---")
            print("1. View Inventory")
            print("2. Add Product to Inventory")
            print("3. Process a Sale")
            print("4. View Sales Report")
            print("5. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                print(tabulate(self.inventory.view_inventory(), headers="keys", tablefmt="grid"))
            elif choice == "2":
                self.add_product()
            elif choice == "3":
                self.process_sale()
            elif choice == "4":
                print(tabulate(self.sales_manager.view_sales_report(), headers="keys", tablefmt="grid"))
            elif choice == "5":
                break
            else:
                print("Invalid choice! Try again.")

    def add_product(self):
        product_id = input("Enter Product ID: ")
        name = input("Enter Product Name: ")
        price = float(input("Enter Price: "))
        quantity = int(input("Enter Quantity: "))
        self.inventory.add_product(Product(product_id, name, price, quantity))
        print("Product added successfully!")

    def process_sale(self):
        sale_id = input("Enter Sale ID: ")
        sale = Sale(sale_id)
        while True:
            product_id = input("Enter Product ID to sell (or 'done' to finish): ")
            if product_id.lower() == 'done':
                break
            if product_id in self.inventory.products:
                quantity = int(input(f"Enter quantity for {self.inventory.products[product_id].name}: "))
                if self.inventory.update_product(product_id, quantity):
                    sale.add_product(self.inventory.products[product_id], quantity)
                else:
                    print("Not enough stock!")
            else:
                print("Invalid Product ID!")
        self.sales_manager.record_sale(sale)
        print(f"Sale {sale_id} recorded successfully!")

if __name__ == "__main__":
    system = ShopSystem()
    system.display_menu()
