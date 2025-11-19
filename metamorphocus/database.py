import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, DateTime, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import streamlit as st

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please ensure the PostgreSQL database is configured.")

# Create engine with connection pooling configuration
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

# Define models
class Inventory(Base):
    __tablename__ = 'inventory'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    stock_level = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=10)
    unit_price = Column(Float, nullable=False, default=0.0)
    image_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

class Material(Base):
    __tablename__ = 'materials'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=False)
    supplier = Column(String(255), nullable=False)
    reorder_point = Column(Float, nullable=False, default=10.0)
    cost_per_unit = Column(Float, nullable=False, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class Finance(Base):
    __tablename__ = 'finance'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    type = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(100), nullable=False)

class Idea(Base):
    __tablename__ = 'ideas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False)
    assigned_to = Column(String(100), nullable=False)
    created_date = Column(Date, nullable=False)
    attachment_filename = Column(String(255), nullable=True)
    attachment_data = Column(LargeBinary, nullable=True)

class BillOfMaterials(Base):
    __tablename__ = 'bill_of_materials'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    material_id = Column(Integer, ForeignKey('materials.id'), nullable=False)
    quantity_needed = Column(Float, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)

class ProductionOrder(Base):
    __tablename__ = 'production_orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    quantity_produced = Column(Integer, nullable=False)
    produced_by = Column(String(100), nullable=False)
    production_date = Column(Date, nullable=False)
    material_cost = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Labor(Base):
    __tablename__ = 'labor'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    worker = Column(String(100), nullable=False)
    hours = Column(Float, nullable=False)
    work_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Settings(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String(100), nullable=False, unique=True)
    setting_value = Column(String(255), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default='pending')
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('inventory.id'), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Initialize database
def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

# Cache database initialization
@st.cache_resource
def get_db_connection():
    """Cached database connection for Streamlit"""
    init_db()
    return True
