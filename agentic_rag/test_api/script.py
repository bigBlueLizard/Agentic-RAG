from sqlalchemy.orm import sessionmaker
from models import Base, engine, User, Product, Category, Review, CartItem, Order, OrderItem
import random

# Set up the session
Session = sessionmaker(bind=engine)
session = Session()

# Helper function to create categories
def create_categories():
    categories = [
        Category(name="Electronics", description="Gadgets and electronic devices"),
        Category(name="Books", description="Wide range of books and novels"),
        Category(name="Clothing", description="Fashionable clothing for men and women"),
        Category(name="Home Appliances", description="Appliances to make life easier"),
        Category(name="Toys", description="Fun toys for children of all ages"),
    ]
    session.add_all(categories)
    session.commit()
    return categories

# Helper function to create products
def create_products(categories):
    products_data = {
        "Electronics": [
            ("Smartphone Pro Max", "High-end smartphone with advanced features.", 999.99, 50),
            ("Wireless Earbuds", "Compact and powerful sound experience.", 49.99, 100),
            ("Gaming Laptop", "Powerful laptop for gaming and productivity.", 1299.99, 20),
            ("Smartwatch", "Stylish watch with health tracking features.", 199.99, 75),
            ("Bluetooth Speaker", "Portable speaker with deep bass.", 29.99, 120),
        ],
        "Books": [
            ("The Art of Programming", "Comprehensive guide to coding.", 39.99, 200),
            ("World History", "A detailed look at global events.", 19.99, 150),
            ("Mystery Novel", "A thrilling tale of suspense.", 14.99, 50),
            ("Self-Help Guide", "Motivational tips for a better life.", 9.99, 300),
            ("Cookbook", "Delicious recipes for all occasions.", 24.99, 100),
        ],
        "Clothing": [
            ("Men's T-Shirt", "Comfortable and stylish cotton t-shirt.", 15.99, 80),
            ("Women's Dress", "Elegant evening wear.", 49.99, 40),
            ("Sports Jacket", "Lightweight jacket for outdoor activities.", 59.99, 30),
            ("Jeans", "Classic denim for everyday wear.", 39.99, 60),
            ("Sneakers", "Trendy and comfortable footwear.", 69.99, 50),
        ],
        "Home Appliances": [
            ("Air Conditioner", "Stay cool during summer.", 299.99, 15),
            ("Vacuum Cleaner", "Efficient cleaning for your home.", 89.99, 25),
            ("Microwave Oven", "Convenient cooking and reheating.", 119.99, 35),
            ("Refrigerator", "Energy-efficient cooling solution.", 499.99, 10),
            ("Coffee Maker", "Brew your favorite coffee at home.", 79.99, 50),
        ],
        "Toys": [
            ("Building Blocks", "Fun and educational toy set.", 29.99, 100),
            ("Doll House", "Charming playhouse for kids.", 49.99, 30),
            ("Remote Control Car", "Fast and exciting toy car.", 39.99, 25),
            ("Puzzle Game", "Brain-teasing activity for kids.", 19.99, 80),
            ("Action Figures", "Popular characters for imaginative play.", 24.99, 60),
        ],
    }

    products = []
    for category in categories:
        for name, description, price, stock in products_data[category.name]:
            product = Product(
                category_id=category.id,
                name=name,
                description=description,
                price=price,
                stock=stock,
                is_available=stock > 0,
            )
            products.append(product)
    session.add_all(products)
    session.commit()
    return products

# Helper function to create users
def create_users():
    users = [
        User(username="johndoe", email="johndoe@example.com", password="password123"),
        User(username="janedoe", email="janedoe@example.com", password="password456"),
        User(username="alicew", email="alicew@example.com", password="password789"),
        User(username="bobsmith", email="bobsmith@example.com", password="password321"),
        User(username="charlieb", email="charlieb@example.com", password="password654"),
    ]
    session.add_all(users)
    session.commit()
    return users

# Helper function to create reviews
def create_reviews(users, products):
    review_comments = [
        "Excellent product, highly recommend!",
        "Good value for the price.",
        "Not what I expected, but okay overall.",
        "Amazing quality, would buy again!",
        "Terrible experience, do not recommend.",
    ]
    
    for product in products[:10]:  # Add reviews to the first 10 products
        for user in users:
            review = Review(
                user_id=user.id,
                product_id=product.id,
                rating=random.randint(1, 5),
                comment=random.choice(review_comments),
            )
            session.add(review)
    session.commit()

# Create categories, products, users, and reviews
categories = create_categories()
products = create_products(categories)
users = create_users()
create_reviews(users, products)

# Print the data that was added
print("Categories:")
for category in categories:
    print(f"  - {category.name}")

print("\nProducts:")
for product in products[:10]:  # Show first 10 products
    print(f"  - {product.name}: {product.price} ({product.stock} in stock)")

print("\nUsers:")
for user in users:
    print(f"  - {user.username}: {user.email}")

print("\nReviews created.")
print("Orders table is empty.")

# Close the session
session.close()
