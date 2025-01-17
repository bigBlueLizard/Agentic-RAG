from fastapi import FastAPI, Depends, HTTPException, Header, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, datetime, timedelta
from typing import Optional, List
from models import *
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, conint

# Database setup
DATABASE_URL = "sqlite:///./ecommerce.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()  # Creates a new session
    try:
        yield db  # Provides the session to the endpoint
    finally:
        db.close()  # Closes the session after the request


app = FastAPI(title="Test Amazon API")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key"  # Replace with a secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 6000


def verify_password(plain_password, stored_password):
    return plain_password == stored_password


# Enhanced Response Models
class ProductDetailsResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    is_available: bool
    category_id: int
    # Optional: Add more fields if needed
    image_url: Optional[str] = None
    average_rating: Optional[float] = None


# Schema for token generation
class TokenRequest(BaseModel):
    username: str = Field(...,
                          description="The username of the user requesting the token")
    password: str = Field(...,
                          description="The password of the user requesting the token")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Access token of the user")
    token_type: str = "bearer"


class OrderCreate(BaseModel):
    items: List[dict] = Field(
        ...,
        description="List of items with product IDs and quantities",
        example=[{"product_id": 1, "quantity": 2}]
    )


class ReviewCreate(BaseModel):
    product_id: int = Field(
        ..., description="ID of the Product for which the review is being posted")
    rating: conint(ge=1, le=5) = Field(...,
                                       description="Rating given to the product (1-5)")
    comment: str = Field(..., description="Comment reviewing the product")


class CartItemCreate(BaseModel):
    product_id: int = Field(...,
                            description="ID of the product to be added in cart")
    quantity: conint(gt=0) = Field(...,
                                   description="Quantity of the item to be added to cart")


class OrderItemResponse(BaseModel):
    product_id: int = Field(..., description="ID of the product")
    product_name: str = Field(..., description="Name of the product")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: float = Field(..., description="Price per unit")


class OrderResponse(BaseModel):
    order_id: int = Field(..., description="Order ID")
    status: str = Field(..., description="Order status")
    total_amount: float = Field(..., description="Total order amount")
    created_at: datetime = Field(..., description="Order creation datetime")
    items: List[OrderItemResponse] = Field(..., description="Order items")


class EnhancedReviewResponse(BaseModel):
    product_id: int
    product_details: ProductDetailsResponse
    rating: int
    comment: str
    created_at: datetime


class EnhancedCartItemResponse(BaseModel):
    product_id: int
    product_details: ProductDetailsResponse
    quantity: int
    total_price: Optional[float] = None


# JWT Utilities
def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/token", response_model=TokenResponse)
def login_for_access_token(form_data: TokenRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")

    # Create JWT token
    access_token = create_jwt_token(data={"user_id": user.id})
    return TokenResponse(access_token=access_token)


def verify_jwt_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Dependency for protected routes
def get_current_user(token: Optional[str] = Header(None)) -> int:
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")
    return verify_jwt_token(token)


@app.post("/orders/place", response_model=OrderResponse)
def place_order(
    order: OrderCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Place a new order with the following features:
    - Multiple items with different quantities
    - Stock availability check
    - Automatic stock update
    """
    new_order = Order(
        user_id=user_id,
        total_amount=0.0,
        status="Pending",
        created_at=datetime.utcnow()
    )
    db.add(new_order)
    db.commit()

    total_amount = 0.0
    items = []

    for item in order.items:
        product = db.query(Product).filter(
            Product.id == item["product_id"],
            Product.is_available == True,
            Product.stock >= item["quantity"]
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product ID {item['product_id']} not found, unavailable, or insufficient stock"
            )

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item["quantity"],
            unit_price=product.price
        )

        # Update product stock
        product.stock -= item["quantity"]

        db.add(order_item)
        total_amount += product.price * item["quantity"]

        items.append(OrderItemResponse(
            product_id=product.id,
            product_name=product.name,
            quantity=item["quantity"],
            unit_price=product.price
        ))

    new_order.total_amount = total_amount
    db.commit()

    return OrderResponse(
        order_id=new_order.id,
        status=new_order.status,
        total_amount=total_amount,
        created_at=new_order.created_at,
        items=items
    )


@app.get("/orders/my", response_model=List[OrderResponse])
def get_my_orders(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(
        None, description="Filter orders from this date"),
    end_date: Optional[date] = Query(
        None, description="Filter orders until this date"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    min_amount: Optional[float] = Query(
        None, ge=0, description="Minimum order amount"),
    max_amount: Optional[float] = Query(
        None, ge=0, description="Maximum order amount"),
    sort_by: Optional[str] = Query(
        None,
        description="Sort orders by: 'date', 'amount', 'status'",
        regex='^(date|amount|status)$'
    )
):
    """
    Get user's orders with the following features:
    - Date range filtering
    - Status filtering
    - Amount range filtering
    - Sorting options
    - Detailed order information including items
    """
    query = db.query(Order).filter(Order.user_id == user_id)

    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    if status:
        query = query.filter(Order.status == status)
    if min_amount is not None:
        query = query.filter(Order.total_amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Order.total_amount <= max_amount)

    if sort_by == 'date':
        query = query.order_by(Order.created_at.desc())
    elif sort_by == 'amount':
        query = query.order_by(Order.total_amount.desc())
    elif sort_by == 'status':
        query = query.order_by(Order.status)

    orders = query.all()

    return [
        OrderResponse(
            order_id=order.id,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                ) for item in order.order_items
            ]
        ) for order in orders
    ]


@app.post("/reviews/post", response_model=EnhancedReviewResponse)
def post_review(
    review: ReviewCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Post a product review with the following features:
    - Rating validation (1-5)
    - Verification of product existence
    """
    product = db.query(Product).get(review.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_review = Review(
        user_id=user_id,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment,
        created_at=datetime.utcnow()
    )
    db.add(new_review)
    db.commit()

    return EnhancedReviewResponse(
        product_id=new_review.product_id,
        product_details=ProductDetailsResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            is_available=product.is_available,
            category_id=product.category_id
        ),
        rating=new_review.rating,
        comment=new_review.comment,
        created_at=new_review.created_at
    )


@app.get("/reviews/my", response_model=List[EnhancedReviewResponse])
def get_my_reviews(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Filter reviews from this date"),
    end_date: Optional[date] = Query(None, description="Filter reviews until this date"),
    product_id: Optional[int] = Query(None, description="Filter reviews for specific product"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter reviews by rating"),
    sort_by: Optional[str] = Query(
        None,
        description="Sort reviews by: 'date', 'rating'",
        regex='^(date|rating)$'
    )
):
    """
    Get user's reviews with full product details
    """
    query = db.query(Review).filter(Review.user_id == user_id)

    # Existing filtering logic
    if start_date:
        query = query.filter(Review.created_at >= start_date)
    if end_date:
        query = query.filter(Review.created_at <= end_date)
    if product_id:
        query = query.filter(Review.product_id == product_id)
    if rating:
        query = query.filter(Review.rating == rating)

    if sort_by == 'date':
        query = query.order_by(Review.created_at.desc())
    elif sort_by == 'rating':
        query = query.order_by(Review.rating.desc())

    reviews = query.all()

    return [
        EnhancedReviewResponse(
            product_id=r.product_id,
            product_details=ProductDetailsResponse(
                id=r.product.id,
                name=r.product.name,
                description=r.product.description,
                price=r.product.price,
                stock=r.product.stock,
                is_available=r.product.is_available,
                category_id=r.product.category_id
            ),
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at
        ) for r in reviews
    ]


@app.post("/cart/add", response_model=EnhancedCartItemResponse)
def add_to_cart(
    cart_item: CartItemCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add item to cart with the following features:
    - Quantity validation
    - Stock availability check
    - Automatic merging with existing cart items
    """
    product = db.query(Product).filter(
        Product.id == cart_item.product_id,
        Product.is_available == True
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found or unavailable"
        )

    if product.stock < cart_item.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available: {product.stock}"
        )

    # Check if item already exists in cart
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == cart_item.product_id
    ).first()

    if existing_item:
        existing_item.quantity += cart_item.quantity
        cart_entry = existing_item
    else:
        cart_entry = CartItem(
            user_id=user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(cart_entry)

    db.commit()

    return EnhancedCartItemResponse(
        product_id=cart_entry.product_id,
        product_details=ProductDetailsResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            is_available=product.is_available,
            category_id=product.category_id
        ),
        quantity=cart_entry.quantity,
        total_price=product.price * cart_entry.quantity
    )


@app.get("/cart/my", response_model=List[EnhancedCartItemResponse])
def get_my_cart(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
    product_id: Optional[int] = Query(None, description="Filter by specific product"),
    min_quantity: Optional[int] = Query(None, ge=1, description="Minimum quantity"),
    max_quantity: Optional[int] = Query(None, ge=1, description="Maximum quantity"),
    sort_by: Optional[str] = Query(
        None,
        description="Sort items by: 'date', 'quantity'",
        regex='^(date|quantity)$'
    )
):
    """
    Get cart items with full product details
    """
    query = db.query(CartItem).filter(CartItem.user_id == user_id)

    # Existing filtering logic
    if product_id:
        query = query.filter(CartItem.product_id == product_id)
    if min_quantity:
        query = query.filter(CartItem.quantity >= min_quantity)
    if max_quantity:
        query = query.filter(CartItem.quantity <= max_quantity)

    if sort_by == 'date':
        query = query.order_by(CartItem.added_at.desc())
    elif sort_by == 'quantity':
        query = query.order_by(CartItem.quantity.desc())

    cart_items = query.all()

    return [
        EnhancedCartItemResponse(
            product_id=item.product_id,
            product_details=ProductDetailsResponse(
                id=item.product.id,
                name=item.product.name,
                description=item.product.description,
                price=item.product.price,
                stock=item.product.stock,
                is_available=item.product.is_available,
                category_id=item.product.category_id
            ),
            quantity=item.quantity,
            total_price=item.product.price * item.quantity
        ) for item in cart_items
    ]

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    is_available: bool
    category_id: int


@app.get("/products/search", response_model=List[ProductResponse])
def search_products(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(
        None, description="Search by product name (partial match)"),
    category_id: Optional[int] = Query(
        None, description="Filter by category ID"),
    min_price: Optional[float] = Query(
        None, ge=0, description="Minimum product price"),
    max_price: Optional[float] = Query(
        None, ge=0, description="Maximum product price"),
    in_stock: Optional[bool] = Query(
        None, description="Filter by stock availability"),
    sort_by: Optional[str] = Query(
        None,
        description="Sort products by: 'price', 'name', 'stock'",
        regex='^(price|name|stock)$'
    ),
    sort_order: Optional[str] = Query(
        'asc',
        description="Sort order: 'asc' or 'desc'",
        regex='^(asc|desc)$'
    ),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(
        20, ge=1, le=100, description="Number of results per page")
):
    """
    Search products with multiple filtering and sorting options:
    - Partial name search
    - Category filtering
    - Price range filtering
    - Stock availability filtering
    - Sorting by price, name, or stock
    - Pagination support
    """
    query = db.query(Product)

    # Name search (case-insensitive, partial match)
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))

    # Category filtering
    if category_id:
        query = query.filter(Product.category_id == category_id)

    # Price range filtering
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # Stock availability filtering
    if in_stock is not None:
        query = query.filter(Product.is_available ==
                             in_stock, Product.stock > 0)

    # Sorting logic
    if sort_by == 'price':
        query = query.order_by(
            Product.price.asc() if sort_order == 'asc' else Product.price.desc())
    elif sort_by == 'name':
        query = query.order_by(
            Product.name.asc() if sort_order == 'asc' else Product.name.desc())
    elif sort_by == 'stock':
        query = query.order_by(
            Product.stock.asc() if sort_order == 'asc' else Product.stock.desc())

    # Pagination
    total_count = query.count()
    total_pages = (total_count + page_size - 1) // page_size

    products = query.offset((page - 1) * page_size).limit(page_size).all()

    # Pydantic response model for returning product details
    return [
        ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            is_available=product.is_available,
            category_id=product.category_id
        ) for product in products
    ]
