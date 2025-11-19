import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, Text, LargeBinary, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime, date

# Base model for SQLAlchemy - MUST BE DEFINED BEFORE MODELS
Base = declarative_base()

# --- Unified Database Connection Setup ---
# This setup is now at the module level. Any script importing from this file will use the same engine.
# It checks for a DATABASE_URL environment variable and falls back to a local SQLite database if not found.
# This makes the application portable and easy to run for development without special configuration.

db_url = os.getenv('DATABASE_URL', 'sqlite:///metamorphocus.db')

engine = create_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600    # Recycle connections after 1 hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Provides a database session. Used by both Streamlit and Flask apps."""
    return SessionLocal()

def init_db():
    """Creates all database tables if they don't already exist.
    This should be called once at application startup."""
    Base.metadata.create_all(bind=engine)

# --- Model Definitions ---

# Inventory model
class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    stock_level = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=10)
    unit_price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    boms = relationship("BillOfMaterials", back_populates="product", cascade="all, delete-orphan")
    production_orders = relationship("ProductionOrder", back_populates="product", cascade="all, delete-orphan")
    labor_entries = relationship("Labor", back_populates="product", cascade="all, delete-orphan")

# Material model
class Material(Base):
    __tablename__ = 'materials'
    id = Column(Integer, primary_key=True, index=True)
    material_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String, nullable=False) # e.g., kg, lbs, pcs, meters
    supplier = Column(String, nullable=False)
    reorder_point = Column(Float, nullable=False, default=10.0)
    cost_per_unit = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    boms = relationship("BillOfMaterials", back_populates="material", cascade="all, delete-orphan")

# Finance model
class Finance(Base):
    __tablename__ = 'finance'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=date.today)
    type = Column(String, nullable=False) # Income or Expense
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=True)

# Idea Board model
class Idea(Base):
    __tablename__ = 'ideas'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default='Brainstorming') # Brainstorming, In Progress, Completed, On Hold
    priority = Column(String, nullable=False, default='Medium') # Low, Medium, High
    assigned_to = Column(String, nullable=False, default='Both') # Emily, Sage, Both
    created_date = Column(Date, default=date.today)
    attachment_filename = Column(String, nullable=True)
    attachment_data = Column(LargeBinary, nullable=True)

# Bill of Materials (Junction Table)
class BillOfMaterials(Base):
    __tablename__ = 'bill_of_materials'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    material_id = Column(Integer, ForeignKey('materials.id'), nullable=False)
    quantity_needed = Column(Float, nullable=False)

    # Relationships
    product = relationship("Inventory", back_populates="boms")
    material = relationship("Material", back_populates="boms")

# Production Orders model
class ProductionOrder(Base):
    __tablename__ = 'production_orders'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    quantity_produced = Column(Integer, nullable=False)
    produced_by = Column(String, nullable=False) # Emily, Sage, Both
    production_date = Column(Date, nullable=False, default=date.today)
    material_cost = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationship
    product = relationship("Inventory", back_populates="production_orders")

# Labor Tracking model
class Labor(Base):
    __tablename__ = 'labor'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    worker = Column(String, nullable=False)
    hours = Column(Float, nullable=False)
    work_date = Column(Date, nullable=False, default=date.today)
    notes = Column(Text, nullable=True)

    # Relationship
    product = relationship("Inventory", back_populates="labor_entries")

# Settings model for key-value storage
class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, nullable=False)
    setting_value = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Customer Order model
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default='pending') # pending, processing, completed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

# Order Items model
class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
