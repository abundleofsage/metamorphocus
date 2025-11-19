# metamorphocus Business Manager

## Overview

A comprehensive business management system for metamorphocus with dual interfaces: a customer-facing sales page and an internal manager backend. The sales page (Flask) allows customers to browse products and place orders, while the manager backend (Streamlit) provides inventory tracking, material management, Bill of Materials (BOM), production tracking, finance management, labor tracking, order fulfillment, and collaborative idea planning with persistent PostgreSQL storage.

**Dual Workflow Architecture:**
- **Sales Page** (Port 5000 - Public): Flask app with dark stone aesthetic for customer purchases
- **Manager Backend** (Port 8000 - Internal): Streamlit app with blue-purple gradient for business operations

## User Preferences

Preferred communication style: Simple, everyday language.

## Key Features

### 1. Dashboard
- Financial overview with income vs expenses visualization
- Low stock alerts for both inventory items and materials
- Automated reorder quantity suggestions (brings stock to 2x minimum level)
- Key business metrics at a glance

### 2. Advanced Analytics
- Financial performance metrics (revenue, expenses, net profit, profit margins)
- Monthly revenue vs expenses trends
- Income sources and expense category breakdowns
- Cumulative cash flow visualization
- Inventory insights with low-stock warnings
- Materials cost analysis and reorder status tracking

### 3. Inventory Management
- Product tracking with SKU, category, stock levels, and pricing
- Minimum stock level monitoring
- **Image Upload**: Upload product images directly through the manager backend
- **Product Descriptions**: Add detailed descriptions for each product
- **Edit Products**: Full editing capability including image updates and removal
- **Material Cost & Profit Display**: Shows BOM-derived material cost, profit per unit, and margin percentage
- **Bill of Materials (BOM)**: Define which materials and quantities are needed for each product
- Real-time profit margin calculations
- CSV export functionality
- Search and filter capabilities

### 4. Materials Tracking
- Raw materials and supplies management
- Quantity tracking with reorder points
- Supplier information
- Cost per unit tracking
- Low-stock alerts with reorder suggestions
- CSV export with reconciliation IDs

### 5. Production Management
- **Production Orders**: Create production orders to manufacture products from materials
- **Material Availability Checking**: Verifies sufficient materials before production
- **Auto-deduction**: Automatically deducts materials from inventory when production is completed
- **Auto-addition**: Automatically adds finished products to inventory
- **Production History**: Track all production events with dates, quantities, and costs
- Material cost tracking per production run
- Producer assignment (Emily, Sage, or Both)

### 6. Finance Tracking
- Income and expense transaction recording
- Payment method tracking
- Financial overview with charts
- Transaction history with filtering
- CSV export with reconciliation IDs

### 7. Labor Tracking
- **Hourly Rate Setting**: Configure a shared hourly rate for labor cost calculations
- **Work Hour Logging**: Track hours worked by Emily, Sage, or Both on specific products
- **Labor Cost Calculation**: Automatically calculates per-unit labor cost based on hours logged and production quantities
- **Labor History**: View, filter, and export labor records by worker and product
- **Integrated Cost Display**: Shows labor costs alongside material costs in inventory view
- **Total Cost Transparency**: Profit margins account for both material AND labor costs

### 8. Customer Orders
- **Order Management**: View and manage customer orders from the sales page
- **Status Tracking**: pending, processing, completed, cancelled
- **Order Details**: Customer info, order items, quantities, and pricing
- **Filtering & Sorting**: By status, date, order value
- **Order Statistics**: Total revenue, average order value, top products sold
- **Analytics Dashboard**: Revenue trends, order status breakdown, daily performance charts
- **CSV Export**: Download order data for external analysis

### 9. Sales Page (Customer-Facing)
- **Beautiful Dark Stone Design**: "Pieces of Colorado" aesthetic (#0f1115 background)
- **Product Catalog**: Live product listings from inventory database
- **Product Images**: Display product photos uploaded through manager backend
- **Product Descriptions**: Show detailed product information
- **Shopping Cart**: Add/remove items, adjust quantities
- **Checkout Process**: Customer info form, order placement
- **Stock Management**: Automatically shows only in-stock items
- **Real-time Updates**: Inventory syncs with backend database
- **Image Serving**: Flask serves uploaded product images from static directory

### 10. Idea Board
- Collaborative idea and project management
- Status tracking (Brainstorming, In Progress, Completed, On Hold)
- Priority levels (High, Medium, Low)
- Assignment to team members (Emily, Sage, or Both)
- **File Attachments**: Upload and download supporting documents (PDF, images, Office files, etc.)
- **Idea Editing**: Full edit capability with attachment management (keep, replace, or remove)
- Status filtering

## System Architecture

### Database Architecture
- **PostgreSQL**: Persistent data storage with SQLAlchemy ORM
- **Tables**:
  - `inventory`: Products with stock levels, pricing, minimum stock thresholds, image URLs, and descriptions
  - `materials`: Raw materials with quantities, suppliers, and reorder points
  - `finance`: Financial transactions (income/expenses)
  - `ideas`: Collaborative ideas with file attachments (binary storage)
  - `bill_of_materials`: Product-material relationships with quantity requirements
  - `production_orders`: Production event tracking with costs and dates
  - `labor`: Labor hours tracking with worker, product, and date information
  - `settings`: Application settings (hourly rate, etc.)
  - `orders`: Customer orders with contact info, totals, status, and timestamps
  - `order_items`: Individual line items linking orders to products with quantities and prices

### Frontend Architecture

**Manager Backend (Streamlit):**
- **Framework**: Streamlit - Python web framework for building data applications
- **Visualization Library**: Plotly - Interactive charts (Express and Graph Objects)
- **Data Processing**: Pandas - Data manipulation and analysis
- **Styling**: Custom CSS with Google Fonts (Inter), indigo/emerald/amber color scheme
- **Color Scheme**: Dark mode with Blue (#3B82F6 - Emily) and Purple (#8B5CF6 - Sage) gradient theme
  - Background: #0F172A (dark slate)
  - Cards: Gradient dark gray (#1E293B to #334155)
  - Text: Light slate (#CBD5E1)
  - Headings: Light indigo (#E0E7FF)

**Sales Page (Flask):**
- **Framework**: Flask - Python web framework with Jinja2 templating
- **Styling**: Tailwind CSS via CDN
- **API**: RESTful endpoints for products and orders
- **CORS**: Enabled for cross-origin requests
- **Color Scheme**: Dark stone aesthetic matching "Pieces of Colorado" design
  - Background: #0f1115 (near-black stone)
  - Text: Light gray/white for contrast
  - Cards: Semi-transparent with backdrop blur

### Code Organization
- **app.py**: Main Streamlit manager application (2400+ lines)
- **sales.py**: Flask sales page and API server with static file serving
- **database.py**: SQLAlchemy models and database connection management
- **templates/index.html**: Sales page frontend with product catalog and cart
- **static/product_images/**: Directory for uploaded product images

## Technical Features

### Data Export
- CSV export for inventory (uses SKU as business identifier)
- CSV export for materials and finance (includes reconciliation IDs)
- Date-stamped export files

### Smart Calculations
- **BOM Cost Calculation**: Automatically calculates material cost per unit based on defined materials
- **Profit Margins**: Real-time profit and margin percentage display (Unit Price - Material Cost)
- **Reorder Suggestions**: Calculates suggested reorder quantities to restore healthy stock levels
- **Production Costing**: Tracks material costs for each production run

### Edge Case Handling
- Products without BOM show "No BOM" gracefully
- Color-coded profit indicators (green for positive, red for negative)
- Material availability validation before production
- Division by zero protection in margin calculations

## Recent Changes (November 2025)

1. Added **Product Image Upload** functionality to manager backend with file uploader
2. Created **Edit Product** tab for updating existing products including images and descriptions
3. Implemented **Static File Serving** in Flask for product images
4. Built **Customer-Facing Sales Page** with Flask, dark stone design, product carousel, and shopping cart
5. Added **Orders Management** page to Streamlit manager with status tracking and analytics
6. Created **Dual Workflow Architecture** with separate URLs for sales (port 5000) and manager (port 8000)
7. Extended **Inventory Table** with `image_url` and `description` fields for product listings
8. Implemented **REST API** endpoints for products and order placement (`/api/products`, `/api/orders`)
9. Added **Order Statistics Dashboard** with revenue trends, top products, and status breakdowns
10. Built **Order Fulfillment System** connecting customer purchases to internal inventory management
11. Added **Labor Tracking** system with hourly rate configuration and per-unit labor cost calculations
12. Updated **Inventory Display** to show both material and labor costs with updated profit margins
13. Added **Test Data Generator** with buttons to populate all data types including labor entries
14. Added **Idea Editing** functionality with session state management
15. Implemented **Bill of Materials (BOM)** system for product recipes
16. Created **Production Management** module with auto-deduction/addition logic

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for manager backend
- **flask**: Web framework for sales page
- **flask-cors**: Cross-origin resource sharing for API endpoints
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization
- **sqlalchemy**: Database ORM
- **psycopg2-binary**: PostgreSQL adapter

### External Services
- **PostgreSQL Database**: Replit-managed persistent storage
- **Google Fonts API**: Inter font family for typography
- **Tailwind CSS CDN**: Styling framework for sales page (development mode)