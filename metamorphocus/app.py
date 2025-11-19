import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from database import get_db, init_db, Inventory, Material, Finance, Idea, BillOfMaterials, ProductionOrder, Labor, Settings, Order, OrderItem
from sqlalchemy import func
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="metamorphocus Business Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database tables
init_db()

# Custom CSS for Dark Mode styling with Blue & Purple theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', 'Source Sans Pro', sans-serif;
    }
    
    .main {
        background-color: #0F172A;
    }
    
    .stApp {
        background-color: #0F172A;
    }
    
    h1, h2, h3 {
        color: #E0E7FF;
        font-weight: 600;
    }
    
    p, label, div {
        color: #CBD5E1;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #3B82F6 0%, #8B5CF6 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3B82F6 0%, #8B5CF6 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    .css-1d391kg {
        padding: 20px;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    .success-badge {
        background-color: #10B981;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .warning-badge {
        background-color: #F59E0B;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .danger-badge {
        background-color: #EF4444;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    
    [data-testid="stMarkdownContainer"] {
        color: #CBD5E1;
    }
    
    .stSelectbox, .stTextInput, .stTextArea, .stNumberInput {
        background-color: #1E293B;
        color: #E0E7FF;
    }
    
    input, textarea, select {
        background-color: #1E293B !important;
        color: #E0E7FF !important;
        border-color: #475569 !important;
    }
    
    .stExpander {
        background-color: #1E293B;
        border: 1px solid #475569;
    }
    
    hr {
        border-color: #475569 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📊 Business Manager")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "📈 Analytics", "📦 Inventory", "🔧 Materials", "🏭 Production", "💰 Finance", "👷 Labor", "🛒 Orders", "💡 Ideas", "🧪 Test Data"],
    label_visibility="collapsed"
)
st.sidebar.markdown("---")
st.sidebar.markdown("**metamorphocus**")
st.sidebar.markdown(f"*Last updated: {datetime.now().strftime('%B %d, %Y')}*")

# Dashboard Page
if page == "🏠 Dashboard":
    st.title("🏠 Dashboard Overview")
    st.markdown("Welcome to your business management system!")
    
    # Get data from database
    db = get_db()
    try:
        total_products = db.query(Inventory).count()
        low_stock_count = db.query(Inventory).filter(Inventory.stock_level <= Inventory.min_stock).count()
        total_materials = db.query(Material).count()
        total_transactions = db.query(Finance).count()
        
        income = db.query(func.sum(Finance.amount)).filter(Finance.type == 'Income').scalar() or 0
        expenses = db.query(func.sum(Finance.amount)).filter(Finance.type == 'Expense').scalar() or 0
        balance = income - expenses
        
        total_ideas = db.query(Idea).count()
        active_ideas = db.query(Idea).filter(Idea.status == 'In Progress').count()
    finally:
        db.close()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", total_products, f"{low_stock_count} low stock" if low_stock_count > 0 else "All good")
    
    with col2:
        st.metric("Materials Tracked", total_materials)
    
    with col3:
        st.metric("Balance", f"${balance:,.2f}", f"{total_transactions} transactions")
    
    with col4:
        st.metric("Active Ideas", active_ideas, f"{total_ideas} total")
    
    # Quick insights
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Financial Overview")
        db = get_db()
        try:
            finance_records = db.query(Finance).all()
        finally:
            db.close()
        
        if finance_records:
            df_finance = pd.DataFrame([{
                'Date': f.date,
                'Type': f.type,
                'Amount': f.amount
            } for f in finance_records])
            
            df_finance['Date'] = pd.to_datetime(df_finance['Date'])
            monthly_summary = df_finance.groupby([df_finance['Date'].dt.to_period('M'), 'Type'])['Amount'].sum().reset_index()
            monthly_summary['Date'] = monthly_summary['Date'].astype(str)
            
            fig = px.bar(monthly_summary, x='Date', y='Amount', color='Type',
                        color_discrete_map={'Income': '#10B981', 'Expense': '#EF4444'},
                        title="Monthly Income vs Expenses")
            fig.update_layout(
                plot_bgcolor='#0F172A', 
                paper_bgcolor='#0F172A',
                font=dict(color='#CBD5E1'),
                title_font=dict(color='#E0E7FF')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No financial data yet. Start tracking in the Finance section!")
    
    with col2:
        st.subheader("⚠️ Low Stock Alerts & Reorder Suggestions")
        db = get_db()
        try:
            low_stock_items = db.query(Inventory).filter(Inventory.stock_level <= Inventory.min_stock).all()
            low_materials = db.query(Material).filter(Material.quantity <= Material.reorder_point).all()
        finally:
            db.close()
        
        if low_stock_items or low_materials:
            if low_stock_items:
                st.markdown("**📦 Inventory Items:**")
                for item in low_stock_items:
                    # Calculate suggested reorder quantity: bring stock up to 2x min_stock
                    shortage = item.min_stock - item.stock_level
                    suggested_reorder = max(shortage + item.min_stock, item.min_stock)
                    
                    st.warning(f"**{item.product_name}** (SKU: {item.sku})")
                    st.caption(f"Current: {item.stock_level} | Min: {item.min_stock} | 📈 Suggest reorder: **{suggested_reorder} units**")
            
            if low_materials:
                st.markdown("**🔧 Materials:**")
                for material in low_materials:
                    # Calculate suggested reorder quantity
                    shortage = material.reorder_point - material.quantity
                    suggested_reorder = max(shortage + material.reorder_point, material.reorder_point)
                    
                    st.warning(f"**{material.material_name}**")
                    st.caption(f"Current: {material.quantity} {material.unit} | Reorder at: {material.reorder_point} | 📈 Suggest reorder: **{suggested_reorder:.1f} {material.unit}**")
        elif total_products > 0:
            st.success("All inventory & material levels are healthy! ✅")
        else:
            st.info("No inventory items yet. Start tracking in the Inventory section!")

# Analytics Page
elif page == "📈 Analytics":
    st.title("📈 Advanced Analytics & Insights")
    st.markdown("Deep dive into your business performance and trends")
    
    # Get all data from database
    db = get_db()
    try:
        finance_records = db.query(Finance).all()
        inventory_items = db.query(Inventory).all()
        materials = db.query(Material).all()
        labor_records = db.query(Labor).all()
    finally:
        db.close()
    
    # Financial Analytics Section
    st.subheader("💰 Financial Performance")
    
    if finance_records:
        df_finance = pd.DataFrame([{
            'Date': f.date,
            'Type': f.type,
            'Category': f.category,
            'Amount': f.amount,
            'Description': f.description
        } for f in finance_records])
        
        df_finance['Date'] = pd.to_datetime(df_finance['Date'])
        
        # Key Financial Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_income = df_finance[df_finance['Type'] == 'Income']['Amount'].sum()
            st.metric("Total Revenue", f"${total_income:,.2f}")
        
        with col2:
            total_expenses = df_finance[df_finance['Type'] == 'Expense']['Amount'].sum()
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        
        with col3:
            net_profit = total_income - total_expenses
            profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
            st.metric("Net Profit", f"${net_profit:,.2f}", f"{profit_margin:.1f}% margin")
        
        with col4:
            avg_transaction = df_finance['Amount'].mean()
            st.metric("Avg Transaction", f"${avg_transaction:,.2f}")
        
        st.markdown("---")
        
        # Charts Row 1
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly Revenue vs Expenses Trend
            monthly_data = df_finance.groupby([df_finance['Date'].dt.to_period('M'), 'Type'])['Amount'].sum().reset_index()
            monthly_data['Date'] = monthly_data['Date'].astype(str)
            
            fig = px.line(monthly_data, x='Date', y='Amount', color='Type',
                         title='Monthly Revenue vs Expenses Trend',
                         color_discrete_map={'Income': '#10B981', 'Expense': '#EF4444'},
                         markers=True)
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'), hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top Expense Categories
            expense_data = df_finance[df_finance['Type'] == 'Expense'].groupby('Category')['Amount'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(x=expense_data.values, y=expense_data.index, orientation='h',
                        title='Top 10 Expense Categories',
                        labels={'x': 'Amount ($)', 'y': 'Category'},
                        color=expense_data.values,
                        color_continuous_scale='Reds')
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Charts Row 2
        col1, col2 = st.columns(2)
        
        with col1:
            # Income Sources Breakdown
            income_data = df_finance[df_finance['Type'] == 'Income'].groupby('Category')['Amount'].sum()
            
            fig = px.pie(values=income_data.values, names=income_data.index,
                        title='Income Sources Breakdown',
                        color_discrete_sequence=px.colors.sequential.Greens_r)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cash Flow Over Time
            df_finance_sorted = df_finance.sort_values('Date')
            df_finance_sorted['Cumulative'] = df_finance_sorted.apply(
                lambda x: x['Amount'] if x['Type'] == 'Income' else -x['Amount'], axis=1
            ).cumsum()
            
            fig = px.area(df_finance_sorted, x='Date', y='Cumulative',
                         title='Cumulative Cash Flow',
                         labels={'Cumulative': 'Cash Flow ($)'})
            fig.update_traces(line_color='#6366F1', fillcolor='rgba(99, 102, 241, 0.2)')
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No financial data available. Start tracking transactions to see analytics!")
    
    st.markdown("---")
    
    # Inventory Analytics Section
    st.subheader("📦 Inventory Insights")
    
    if inventory_items:
        df_inventory = pd.DataFrame([{
            'Product Name': i.product_name,
            'Category': i.category,
            'Stock Level': i.stock_level,
            'Min Stock': i.min_stock,
            'Unit Price': i.unit_price,
            'Total Value': i.stock_level * i.unit_price,
            'Stock Status': 'Low' if i.stock_level <= i.min_stock else 'Healthy'
        } for i in inventory_items])
        
        # Inventory Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_value = df_inventory['Total Value'].sum()
            st.metric("Total Inventory Value", f"${total_value:,.2f}")
        
        with col2:
            total_units = df_inventory['Stock Level'].sum()
            st.metric("Total Units", f"{int(total_units):,}")
        
        with col3:
            low_stock_count = len(df_inventory[df_inventory['Stock Status'] == 'Low'])
            st.metric("Low Stock Items", low_stock_count)
        
        with col4:
            avg_value = df_inventory['Total Value'].mean()
            st.metric("Avg Product Value", f"${avg_value:,.2f}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Inventory by Category
            category_value = df_inventory.groupby('Category')['Total Value'].sum().sort_values(ascending=False)
            
            fig = px.bar(x=category_value.index, y=category_value.values,
                        title='Inventory Value by Category',
                        labels={'x': 'Category', 'y': 'Total Value ($)'},
                        color=category_value.values,
                        color_continuous_scale='Blues')
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Stock Health Status
            stock_status = df_inventory['Stock Status'].value_counts()
            
            fig = px.pie(values=stock_status.values, names=stock_status.index,
                        title='Stock Health Status',
                        color_discrete_map={'Healthy': '#10B981', 'Low': '#EF4444'})
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No inventory data available. Start adding products to see analytics!")
    
    st.markdown("---")
    
    # Materials Analytics Section
    st.subheader("🔧 Materials Cost Analysis")
    
    if materials:
        df_materials = pd.DataFrame([{
            'Material Name': m.material_name,
            'Category': m.category,
            'Quantity': m.quantity,
            'Cost per Unit': m.cost_per_unit,
            'Total Cost': m.quantity * m.cost_per_unit,
            'Reorder Point': m.reorder_point,
            'Status': 'Need Reorder' if m.quantity <= m.reorder_point else 'Sufficient'
        } for m in materials])
        
        # Materials Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_material_value = df_materials['Total Cost'].sum()
            st.metric("Total Materials Value", f"${total_material_value:,.2f}")
        
        with col2:
            reorder_needed = len(df_materials[df_materials['Status'] == 'Need Reorder'])
            st.metric("Reorder Needed", reorder_needed)
        
        with col3:
            avg_material_cost = df_materials['Total Cost'].mean()
            st.metric("Avg Material Cost", f"${avg_material_cost:,.2f}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top Materials by Cost
            top_materials = df_materials.nlargest(10, 'Total Cost')
            
            fig = px.bar(top_materials, x='Material Name', y='Total Cost',
                        title='Top 10 Materials by Total Cost',
                        color='Total Cost',
                        color_continuous_scale='Oranges')
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'), showlegend=False)
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Materials Status
            status_counts = df_materials['Status'].value_counts()
            
            fig = px.pie(values=status_counts.values, names=status_counts.index,
                        title='Materials Reorder Status',
                        color_discrete_map={'Sufficient': '#10B981', 'Need Reorder': '#F59E0B'})
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No materials data available. Start tracking materials to see analytics!")
    
    st.markdown("---")
    
    # Labor Analytics Section
    st.subheader("👷 Labor Cost Analysis")
    
    if labor_records:
        # Get hourly rate from settings
        db = get_db()
        try:
            hourly_rate_setting = db.query(Settings).filter(Settings.setting_key == 'hourly_rate').first()
            hourly_rate = float(hourly_rate_setting.setting_value) if hourly_rate_setting else 0.0
        finally:
            db.close()
        
        if hourly_rate > 0:
            df_labor = pd.DataFrame([{
                'Date': l.work_date,
                'Worker': l.worker,
                'Product ID': l.product_id,
                'Hours': l.hours,
                'Labor Cost': l.hours * hourly_rate,
                'Notes': l.notes
            } for l in labor_records])
            
            df_labor['Date'] = pd.to_datetime(df_labor['Date'])
            
            # Add product names
            product_map = {i.id: i.product_name for i in inventory_items}
            df_labor['Product Name'] = df_labor['Product ID'].map(product_map)
            
            # Labor Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_labor_cost = df_labor['Labor Cost'].sum()
                st.metric("Total Labor Cost", f"${total_labor_cost:,.2f}")
            
            with col2:
                total_hours = df_labor['Hours'].sum()
                st.metric("Total Hours Logged", f"{total_hours:,.1f}")
            
            with col3:
                st.metric("Hourly Rate", f"${hourly_rate:.2f}/hr")
            
            with col4:
                unique_products = df_labor['Product ID'].nunique()
                st.metric("Products Worked On", unique_products)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Labor Distribution by Worker
                worker_data = df_labor.groupby('Worker')['Labor Cost'].sum().sort_values(ascending=False)
                
                fig = px.pie(values=worker_data.values, names=worker_data.index,
                            title='Labor Cost Distribution by Worker',
                            color_discrete_sequence=['#3B82F6', '#8B5CF6', '#6366F1'])
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top Products by Labor Cost
                product_labor = df_labor.groupby('Product Name')['Labor Cost'].sum().sort_values(ascending=False).head(10)
                
                fig = px.bar(x=product_labor.index, y=product_labor.values,
                            title='Top 10 Products by Labor Cost',
                            labels={'x': 'Product', 'y': 'Labor Cost ($)'},
                            color=product_labor.values,
                            color_continuous_scale='Purples')
                fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'), showlegend=False)
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Monthly Labor Trend
            st.markdown("---")
            monthly_labor = df_labor.groupby(df_labor['Date'].dt.to_period('M'))['Labor Cost'].sum().reset_index()
            monthly_labor['Date'] = monthly_labor['Date'].astype(str)
            
            fig = px.line(monthly_labor, x='Date', y='Labor Cost',
                         title='Monthly Labor Cost Trend',
                         markers=True)
            fig.update_traces(line_color='#8B5CF6', marker=dict(size=8))
            fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hourly rate configured. Set the hourly rate in the Labor page to see analytics!")
    else:
        st.info("No labor data available. Start logging work hours to see analytics!")

# Inventory Page
elif page == "📦 Inventory":
    st.title("📦 Inventory Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 View Inventory", "➕ Add Product", "✏️ Edit Product", "🔧 Bill of Materials"])
    
    with tab1:
        st.subheader("Current Inventory")
        
        db = get_db()
        try:
            inventory_items = db.query(Inventory).all()
        finally:
            db.close()
        
        if inventory_items:
            # Convert to DataFrame for filtering
            df_inventory = pd.DataFrame([{
                'id': i.id,
                'Product Name': i.product_name,
                'SKU': i.sku,
                'Category': i.category,
                'Stock Level': i.stock_level,
                'Min Stock': i.min_stock,
                'Unit Price': i.unit_price
            } for i in inventory_items])
            
            # Search and filter row
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search = st.text_input("🔍 Search products", placeholder="Search by name or SKU...")
            with col2:
                categories = df_inventory['Category'].unique().tolist()
                category_filter = st.selectbox("Filter by Category", ["All"] + categories)
            with col3:
                # Export button
                export_df = df_inventory.drop('id', axis=1)
                csv = export_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export CSV",
                    data=csv,
                    file_name=f"inventory_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Filter data
            filtered_df = df_inventory.copy()
            if search:
                filtered_df = filtered_df[
                    filtered_df['Product Name'].str.contains(search, case=False, na=False) |
                    filtered_df['SKU'].str.contains(search, case=False, na=False)
                ]
            if category_filter != "All":
                filtered_df = filtered_df[filtered_df['Category'] == category_filter]
            
            # Display inventory
            for idx, row in filtered_df.iterrows():
                # Calculate material cost from BOM
                db = get_db()
                try:
                    bom_items = db.query(BillOfMaterials).filter(BillOfMaterials.product_id == row['id']).all()
                    material_cost = 0.0
                    for bom_item in bom_items:
                        material = db.query(Material).filter(Material.id == bom_item.material_id).first()
                        if material:
                            material_cost += material.cost_per_unit * bom_item.quantity_needed
                finally:
                    db.close()
                
                # Calculate labor cost per unit
                db = get_db()
                try:
                    # Get hourly rate
                    hourly_rate_setting = db.query(Settings).filter(Settings.setting_key == 'hourly_rate').first()
                    hourly_rate = float(hourly_rate_setting.setting_value) if hourly_rate_setting else 0.0
                    
                    # Get all labor entries for this product
                    labor_entries = db.query(Labor).filter(Labor.product_id == row['id']).all()
                    total_labor_hours = sum(entry.hours for entry in labor_entries)
                    
                    # Get total quantity produced
                    production_orders = db.query(ProductionOrder).filter(ProductionOrder.product_id == row['id']).all()
                    total_quantity_produced = sum(order.quantity_produced for order in production_orders)
                    
                    # Calculate per-unit labor cost
                    if total_quantity_produced > 0 and total_labor_hours > 0:
                        labor_cost_per_unit = (total_labor_hours * hourly_rate) / total_quantity_produced
                    else:
                        labor_cost_per_unit = 0.0
                finally:
                    db.close()
                
                total_cost = material_cost + labor_cost_per_unit
                profit = row['Unit Price'] - total_cost
                margin = (profit / row['Unit Price'] * 100) if row['Unit Price'] > 0 else 0
                
                with st.container():
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 0.5])
                    with col1:
                        st.markdown(f"**{row['Product Name']}**")
                        st.caption(f"SKU: {row['SKU']} | {row['Category']}")
                    with col2:
                        if row['Stock Level'] <= row['Min Stock']:
                            st.markdown(f"<span class='danger-badge'>Stock: {row['Stock Level']}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='success-badge'>Stock: {row['Stock Level']}</span>", unsafe_allow_html=True)
                        st.caption(f"Min: {row['Min Stock']}")
                    with col3:
                        st.write(f"${row['Unit Price']:.2f}")
                        st.caption("Sell Price")
                    with col4:
                        if material_cost > 0:
                            st.write(f"${material_cost:.2f}")
                            st.caption("Material")
                        else:
                            st.caption("No BOM")
                    with col5:
                        if labor_cost_per_unit > 0:
                            st.write(f"${labor_cost_per_unit:.2f}")
                            st.caption("Labor")
                        else:
                            st.caption("No labor")
                    with col6:
                        if total_cost > 0:
                            profit_color = "#10B981" if profit > 0 else "#EF4444"
                            st.markdown(f"<span style='color:{profit_color};font-weight:600;'>${profit:.2f}</span>", unsafe_allow_html=True)
                            st.caption(f"{margin:.1f}% margin")
                        else:
                            st.caption("-")
                    with col7:
                        if st.button("🗑️", key=f"del_inv_{row['id']}"):
                            db = get_db()
                            try:
                                item_to_delete = db.query(Inventory).filter(Inventory.id == row['id']).first()
                                if item_to_delete:
                                    db.delete(item_to_delete)
                                    db.commit()
                            finally:
                                db.close()
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No products in inventory yet. Add your first product in the 'Add Product' tab!")
    
    with tab2:
        st.subheader("Add New Product")
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("Product Name*")
                sku = st.text_input("SKU*")
                category = st.text_input("Category*")
                description = st.text_area("Description", placeholder="Describe the product features, materials, size, etc.")
            with col2:
                stock_level = st.number_input("Stock Level*", min_value=0, value=0)
                min_stock = st.number_input("Minimum Stock Level*", min_value=0, value=10)
                unit_price = st.number_input("Unit Price ($)*", min_value=0.0, value=0.0, step=0.01)
                uploaded_file = st.file_uploader("Product Image", type=['png', 'jpg', 'jpeg', 'webp'], help="Upload a product image (PNG, JPG, or WEBP)")
            
            submitted = st.form_submit_button("➕ Add Product", use_container_width=True)
            
            if submitted:
                if product_name and sku and category:
                    # Handle image upload
                    image_url = None
                    if uploaded_file is not None:
                        # Create product_images directory if it doesn't exist
                        img_dir = Path("static/product_images")
                        img_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Generate unique filename using SKU
                        file_extension = uploaded_file.name.split('.')[-1]
                        filename = f"{sku.replace(' ', '_')}.{file_extension}"
                        filepath = img_dir / filename
                        
                        # Save the uploaded file
                        with open(filepath, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Store the URL path
                        image_url = f"/static/product_images/{filename}"
                    
                    db = get_db()
                    try:
                        new_product = Inventory(
                            product_name=product_name,
                            sku=sku,
                            category=category,
                            stock_level=stock_level,
                            min_stock=min_stock,
                            unit_price=unit_price,
                            image_url=image_url,
                            description=description,
                            last_updated=datetime.utcnow()
                        )
                        db.add(new_product)
                        db.commit()
                        st.success(f"✅ {product_name} added successfully!")
                    finally:
                        db.close()
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    with tab3:
        st.subheader("Edit Existing Product")
        
        db = get_db()
        try:
            all_products = db.query(Inventory).all()
        finally:
            db.close()
        
        if not all_products:
            st.info("No products available to edit. Add products in the 'Add Product' tab first.")
        else:
            # Select product to edit
            product_options = {f"{p.product_name} (SKU: {p.sku})": p.id for p in all_products}
            selected_product_label = st.selectbox("Select Product to Edit", list(product_options.keys()))
            selected_product_id = product_options[selected_product_label]
            
            # Get selected product
            db = get_db()
            try:
                product = db.query(Inventory).filter(Inventory.id == selected_product_id).first()
            finally:
                db.close()
            
            if product:
                # Show current image if exists
                if product.image_url:
                    st.image(product.image_url, caption="Current Product Image", width=200)
                
                with st.form("edit_product_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_product_name = st.text_input("Product Name*", value=product.product_name)
                        edit_sku = st.text_input("SKU*", value=product.sku)
                        edit_category = st.text_input("Category*", value=product.category)
                        edit_description = st.text_area("Description", value=product.description or "", placeholder="Describe the product features, materials, size, etc.")
                    with col2:
                        edit_stock_level = st.number_input("Stock Level*", min_value=0, value=product.stock_level)
                        edit_min_stock = st.number_input("Minimum Stock Level*", min_value=0, value=product.min_stock)
                        edit_unit_price = st.number_input("Unit Price ($)*", min_value=0.0, value=float(product.unit_price), step=0.01)
                        edit_uploaded_file = st.file_uploader("Update Product Image", type=['png', 'jpg', 'jpeg', 'webp'], help="Upload a new product image (PNG, JPG, or WEBP)")
                        if product.image_url:
                            remove_image = st.checkbox("Remove current image")
                        else:
                            remove_image = False
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_submitted = st.form_submit_button("💾 Update Product", use_container_width=True)
                    with col2:
                        cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
                    
                    if update_submitted:
                        if edit_product_name and edit_sku and edit_category:
                            # Handle image upload/removal
                            new_image_url = product.image_url
                            
                            if remove_image:
                                new_image_url = None
                                # Delete old image file if exists
                                if product.image_url and product.image_url.startswith('/static/product_images/'):
                                    old_filepath = Path(product.image_url.lstrip('/'))
                                    if old_filepath.exists():
                                        old_filepath.unlink()
                            
                            if edit_uploaded_file is not None:
                                # Create product_images directory if it doesn't exist
                                img_dir = Path("static/product_images")
                                img_dir.mkdir(parents=True, exist_ok=True)
                                
                                # Delete old image if SKU changed
                                if product.image_url and product.sku != edit_sku:
                                    old_filepath = Path(product.image_url.lstrip('/'))
                                    if old_filepath.exists():
                                        old_filepath.unlink()
                                
                                # Generate unique filename using SKU
                                file_extension = edit_uploaded_file.name.split('.')[-1]
                                filename = f"{edit_sku.replace(' ', '_')}.{file_extension}"
                                filepath = img_dir / filename
                                
                                # Save the uploaded file
                                with open(filepath, "wb") as f:
                                    f.write(edit_uploaded_file.getbuffer())
                                
                                # Store the URL path
                                new_image_url = f"/static/product_images/{filename}"
                            
                            db = get_db()
                            try:
                                product.product_name = edit_product_name
                                product.sku = edit_sku
                                product.category = edit_category
                                product.stock_level = edit_stock_level
                                product.min_stock = edit_min_stock
                                product.unit_price = edit_unit_price
                                product.image_url = new_image_url
                                product.description = edit_description
                                product.last_updated = datetime.utcnow()
                                db.commit()
                                st.success(f"✅ {edit_product_name} updated successfully!")
                            finally:
                                db.close()
                            st.rerun()
                        else:
                            st.error("Please fill in all required fields (*)")
    
    with tab4:
        st.subheader("🔧 Bill of Materials - Product Recipes")
        st.caption("Define which materials are needed to make each product")
        
        db = get_db()
        try:
            products = db.query(Inventory).all()
            materials = db.query(Material).all()
        finally:
            db.close()
        
        if not products:
            st.info("Please add products in the 'Add Product' tab first before creating bills of materials.")
        elif not materials:
            st.info("Please add materials in the Materials section first before creating bills of materials.")
        else:
            # Select product to manage BOM
            product_options = {f"{p.product_name} (SKU: {p.sku})": p.id for p in products}
            selected_product_label = st.selectbox("Select Product", list(product_options.keys()))
            selected_product_id = product_options[selected_product_label]
            
            # Get current BOM for selected product
            db = get_db()
            try:
                current_bom = db.query(BillOfMaterials).filter(BillOfMaterials.product_id == selected_product_id).all()
                selected_product = db.query(Inventory).filter(Inventory.id == selected_product_id).first()
            finally:
                db.close()
            
            # Display current BOM
            if current_bom:
                st.markdown("**Current Materials for this Product:**")
                total_material_cost = 0
                for bom_item in current_bom:
                    db = get_db()
                    try:
                        material = db.query(Material).filter(Material.id == bom_item.material_id).first()
                    finally:
                        db.close()
                    
                    if material:
                        item_cost = material.cost_per_unit * bom_item.quantity_needed
                        total_material_cost += item_cost
                        
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
                        with col1:
                            st.write(f"**{material.material_name}**")
                        with col2:
                            st.write(f"{bom_item.quantity_needed} {material.unit}")
                        with col3:
                            st.write(f"${item_cost:.2f}")
                        with col4:
                            if st.button("🗑️", key=f"del_bom_{bom_item.id}"):
                                db = get_db()
                                try:
                                    bom_to_delete = db.query(BillOfMaterials).filter(BillOfMaterials.id == bom_item.id).first()
                                    if bom_to_delete:
                                        db.delete(bom_to_delete)
                                        db.commit()
                                finally:
                                    db.close()
                                st.rerun()
                
                st.markdown(f"**Total Material Cost per Unit:** ${total_material_cost:.2f}")
                if selected_product:
                    profit = selected_product.unit_price - total_material_cost
                    margin = (profit / selected_product.unit_price * 100) if selected_product.unit_price > 0 else 0
                    st.markdown(f"**Profit per Unit:** ${profit:.2f} ({margin:.1f}% margin)")
                st.markdown("---")
            else:
                st.info("No materials defined for this product yet. Add materials below.")
            
            # Add new material to BOM
            st.markdown("**Add Material to Product:**")
            with st.form(f"add_bom_form_{selected_product_id}"):
                col1, col2 = st.columns(2)
                with col1:
                    material_options = {f"{m.material_name} (${m.cost_per_unit:.2f}/{m.unit})": m.id for m in materials}
                    selected_material_label = st.selectbox("Material*", list(material_options.keys()))
                    selected_material_id = material_options[selected_material_label]
                with col2:
                    # Get material unit for display
                    selected_material = next((m for m in materials if m.id == selected_material_id), None)
                    unit_label = selected_material.unit if selected_material else "units"
                    quantity_needed = st.number_input(f"Quantity Needed ({unit_label})*", min_value=0.01, value=1.0, step=0.1)
                
                submitted = st.form_submit_button("➕ Add to BOM", use_container_width=True)
                
                if submitted:
                    # Check if material already exists in BOM
                    db = get_db()
                    try:
                        existing = db.query(BillOfMaterials).filter(
                            BillOfMaterials.product_id == selected_product_id,
                            BillOfMaterials.material_id == selected_material_id
                        ).first()
                        
                        if existing:
                            st.error("This material is already in the BOM. Delete it first if you want to change the quantity.")
                        else:
                            new_bom = BillOfMaterials(
                                product_id=selected_product_id,
                                material_id=selected_material_id,
                                quantity_needed=quantity_needed
                            )
                            db.add(new_bom)
                            db.commit()
                            st.success("✅ Material added to BOM!")
                    finally:
                        db.close()
                    st.rerun()

# Materials Page
elif page == "🔧 Materials":
    st.title("🔧 Material Tracking")
    
    tab1, tab2 = st.tabs(["📋 View Materials", "➕ Add Material"])
    
    with tab1:
        st.subheader("Raw Materials & Supplies")
        
        db = get_db()
        try:
            materials = db.query(Material).all()
        finally:
            db.close()
        
        if materials:
            # Convert to DataFrame for export
            df_materials = pd.DataFrame([{
                'ID': m.id,
                'Material Name': m.material_name,
                'Category': m.category,
                'Quantity': m.quantity,
                'Unit': m.unit,
                'Supplier': m.supplier,
                'Reorder Point': m.reorder_point,
                'Cost per Unit': m.cost_per_unit
            } for m in materials])
            
            # Export button
            csv = df_materials.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Materials CSV",
                data=csv,
                file_name=f"materials_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            st.markdown("---")
            
            for material in materials:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{material.material_name}**")
                        st.caption(f"Category: {material.category} | Supplier: {material.supplier}")
                    with col2:
                        if material.quantity <= material.reorder_point:
                            st.markdown(f"<span class='warning-badge'>{material.quantity} {material.unit}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='success-badge'>{material.quantity} {material.unit}</span>", unsafe_allow_html=True)
                    with col3:
                        st.write(f"Reorder: {material.reorder_point}")
                    with col4:
                        st.write(f"${material.cost_per_unit:.2f}/{material.unit}")
                    with col5:
                        if st.button("🗑️", key=f"del_mat_{material.id}"):
                            db = get_db()
                            try:
                                mat_to_delete = db.query(Material).filter(Material.id == material.id).first()
                                if mat_to_delete:
                                    db.delete(mat_to_delete)
                                    db.commit()
                            finally:
                                db.close()
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No materials tracked yet. Add your first material in the 'Add Material' tab!")
    
    with tab2:
        st.subheader("Add New Material")
        
        with st.form("add_material_form"):
            col1, col2 = st.columns(2)
            with col1:
                material_name = st.text_input("Material Name*")
                category = st.text_input("Category*")
                supplier = st.text_input("Supplier*")
                unit = st.selectbox("Unit*", ["kg", "lbs", "pcs", "meters", "liters", "gallons", "boxes"])
            with col2:
                quantity = st.number_input("Current Quantity*", min_value=0.0, value=0.0, step=0.1)
                reorder_point = st.number_input("Reorder Point*", min_value=0.0, value=10.0, step=0.1)
                cost_per_unit = st.number_input("Cost per Unit ($)*", min_value=0.0, value=0.0, step=0.01)
            
            submitted = st.form_submit_button("➕ Add Material", use_container_width=True)
            
            if submitted:
                if material_name and category and supplier:
                    db = get_db()
                    try:
                        new_material = Material(
                            material_name=material_name,
                            category=category,
                            quantity=quantity,
                            unit=unit,
                            supplier=supplier,
                            reorder_point=reorder_point,
                            cost_per_unit=cost_per_unit,
                            last_updated=datetime.utcnow()
                        )
                        db.add(new_material)
                        db.commit()
                        st.success(f"✅ {material_name} added successfully!")
                    finally:
                        db.close()
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")

# Production Page
elif page == "🏭 Production":
    st.title("🏭 Production Management")
    
    tab1, tab2 = st.tabs(["📋 Production History", "➕ New Production Order"])
    
    with tab1:
        st.subheader("Production History")
        
        db = get_db()
        try:
            production_orders = db.query(ProductionOrder).order_by(ProductionOrder.production_date.desc()).all()
        finally:
            db.close()
        
        if production_orders:
            for order in production_orders:
                db = get_db()
                try:
                    product = db.query(Inventory).filter(Inventory.id == order.product_id).first()
                finally:
                    db.close()
                
                if product:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        with col1:
                            st.markdown(f"**{product.product_name}**")
                            st.caption(f"SKU: {product.sku}")
                            if order.notes:
                                st.caption(f"Notes: {order.notes}")
                        with col2:
                            st.write(f"Qty: {order.quantity_produced}")
                            st.caption(f"By: {order.produced_by}")
                        with col3:
                            st.write(f"${order.material_cost:.2f}")
                            st.caption("Material Cost")
                        with col4:
                            st.write(f"{order.production_date}")
                            st.caption("Production Date")
                        st.markdown("---")
        else:
            st.info("No production orders yet. Create your first production order in the 'New Production Order' tab!")
    
    with tab2:
        st.subheader("Create New Production Order")
        
        db = get_db()
        try:
            products = db.query(Inventory).all()
        finally:
            db.close()
        
        if not products:
            st.info("Please add products in the Inventory section first before creating production orders.")
        else:
            # Select product
            product_options = {f"{p.product_name} (SKU: {p.sku})": p.id for p in products}
            selected_product_label = st.selectbox("Select Product to Produce*", list(product_options.keys()))
            selected_product_id = product_options[selected_product_label]
            
            # Get BOM for selected product
            db = get_db()
            try:
                bom_items = db.query(BillOfMaterials).filter(BillOfMaterials.product_id == selected_product_id).all()
                selected_product = db.query(Inventory).filter(Inventory.id == selected_product_id).first()
            finally:
                db.close()
            
            if not bom_items:
                st.warning("⚠️ This product has no Bill of Materials defined. Please define the materials needed in the Inventory > Bill of Materials tab first.")
            else:
                # Display BOM and check material availability
                st.markdown("**Materials Required per Unit:**")
                
                total_cost_per_unit = 0
                materials_available = True
                material_details = []
                
                for bom_item in bom_items:
                    db = get_db()
                    try:
                        material = db.query(Material).filter(Material.id == bom_item.material_id).first()
                    finally:
                        db.close()
                    
                    if material:
                        cost = material.cost_per_unit * bom_item.quantity_needed
                        total_cost_per_unit += cost
                        material_details.append({
                            'material': material,
                            'quantity_needed': bom_item.quantity_needed,
                            'cost': cost
                        })
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{material.material_name}**")
                        with col2:
                            st.write(f"{bom_item.quantity_needed} {material.unit}")
                        with col3:
                            st.write(f"${cost:.2f}")
                
                st.markdown(f"**Total Material Cost per Unit:** ${total_cost_per_unit:.2f}")
                st.markdown("---")
                
                # Production form
                with st.form("production_order_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        quantity_to_produce = st.number_input("Quantity to Produce*", min_value=1, value=1)
                        produced_by = st.selectbox("Produced By*", ["Emily", "Sage", "Both"])
                    with col2:
                        production_date = st.date_input("Production Date*", value=date.today())
                        notes = st.text_area("Notes (Optional)", height=50)
                    
                    # Calculate total materials needed
                    st.markdown(f"**Materials Needed for {quantity_to_produce} units:**")
                    all_materials_sufficient = True
                    
                    for detail in material_details:
                        total_needed = detail['quantity_needed'] * quantity_to_produce
                        available = detail['material'].quantity
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"{detail['material'].material_name}")
                        with col2:
                            st.write(f"{total_needed} {detail['material'].unit}")
                        with col3:
                            if available >= total_needed:
                                st.markdown(f"<span class='success-badge'>✓ Available ({available} {detail['material'].unit})</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<span class='danger-badge'>✗ Insufficient ({available}/{total_needed} {detail['material'].unit})</span>", unsafe_allow_html=True)
                                all_materials_sufficient = False
                    
                    total_material_cost = total_cost_per_unit * quantity_to_produce
                    st.markdown(f"**Total Production Cost:** ${total_material_cost:.2f}")
                    
                    submitted = st.form_submit_button("🏭 Complete Production", use_container_width=True)
                    
                    if submitted:
                        if not all_materials_sufficient:
                            st.error("❌ Cannot complete production - insufficient materials. Please restock before producing.")
                        else:
                            # Execute production
                            db = get_db()
                            try:
                                # Deduct materials
                                for detail in material_details:
                                    total_needed = detail['quantity_needed'] * quantity_to_produce
                                    material = db.query(Material).filter(Material.id == detail['material'].id).first()
                                    if material:
                                        material.quantity -= total_needed
                                        material.last_updated = datetime.utcnow()
                                
                                # Add finished products to inventory
                                product = db.query(Inventory).filter(Inventory.id == selected_product_id).first()
                                if product:
                                    product.stock_level += quantity_to_produce
                                    product.last_updated = datetime.utcnow()
                                
                                # Create production order record
                                new_order = ProductionOrder(
                                    product_id=selected_product_id,
                                    quantity_produced=quantity_to_produce,
                                    produced_by=produced_by,
                                    production_date=production_date,
                                    material_cost=total_material_cost,
                                    notes=notes
                                )
                                db.add(new_order)
                                db.commit()
                                st.success(f"✅ Production completed! Added {quantity_to_produce} units of {selected_product.product_name} to inventory.")
                            finally:
                                db.close()
                            st.rerun()

# Finance Page
elif page == "💰 Finance":
    st.title("💰 Finance Tracking")
    
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📋 Transactions", "➕ Add Transaction"])
    
    with tab1:
        st.subheader("Financial Overview")
        
        db = get_db()
        try:
            finance_records = db.query(Finance).all()
        finally:
            db.close()
        
        if finance_records:
            df_finance = pd.DataFrame([{
                'Date': f.date,
                'Type': f.type,
                'Category': f.category,
                'Amount': f.amount
            } for f in finance_records])
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                total_income = df_finance[df_finance['Type'] == 'Income']['Amount'].sum()
                st.metric("Total Income", f"${total_income:,.2f}", delta="", delta_color="normal")
            
            with col2:
                total_expenses = df_finance[df_finance['Type'] == 'Expense']['Amount'].sum()
                st.metric("Total Expenses", f"${total_expenses:,.2f}", delta="", delta_color="normal")
            
            with col3:
                net_balance = total_income - total_expenses
                st.metric("Net Balance", f"${net_balance:,.2f}", delta="", delta_color="normal")
            
            # Charts
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                # Income vs Expense by category
                category_summary = df_finance.groupby(['Type', 'Category'])['Amount'].sum().reset_index()
                fig = px.pie(category_summary, values='Amount', names='Category', 
                            title='Expenses & Income by Category',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Monthly trend
                df_finance['Date'] = pd.to_datetime(df_finance['Date'])
                monthly = df_finance.groupby([df_finance['Date'].dt.to_period('M'), 'Type'])['Amount'].sum().reset_index()
                monthly['Date'] = monthly['Date'].astype(str)
                fig = px.line(monthly, x='Date', y='Amount', color='Type',
                             title='Monthly Financial Trend',
                             color_discrete_map={'Income': '#10B981', 'Expense': '#EF4444'})
                fig.update_layout(plot_bgcolor='#0F172A', paper_bgcolor='#0F172A', font=dict(color='#CBD5E1'), title_font=dict(color='#E0E7FF'))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No financial transactions yet. Add your first transaction in the 'Add Transaction' tab!")
    
    with tab2:
        st.subheader("Transaction History")
        
        db = get_db()
        try:
            transactions = db.query(Finance).order_by(Finance.date.desc()).all()
        finally:
            db.close()
        
        if transactions:
            # Convert to DataFrame for export
            df_transactions = pd.DataFrame([{
                'ID': t.id,
                'Date': t.date,
                'Type': t.type,
                'Category': t.category,
                'Description': t.description,
                'Amount': t.amount,
                'Payment Method': t.payment_method
            } for t in transactions])
            
            # Export button
            csv = df_transactions.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Transactions CSV",
                data=csv,
                file_name=f"finance_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            st.markdown("---")
            
            for trans in transactions:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{trans.description}**")
                        st.caption(f"{trans.date} | {trans.category}")
                    with col2:
                        type_badge = 'success-badge' if trans.type == 'Income' else 'danger-badge'
                        st.markdown(f"<span class='{type_badge}'>{trans.type}</span>", unsafe_allow_html=True)
                    with col3:
                        amount_color = '#10B981' if trans.type == 'Income' else '#EF4444'
                        st.markdown(f"<span style='color:{amount_color};font-weight:600;'>${trans.amount:,.2f}</span>", unsafe_allow_html=True)
                    with col4:
                        st.write(trans.payment_method)
                    with col5:
                        if st.button("🗑️", key=f"del_fin_{trans.id}"):
                            db = get_db()
                            try:
                                fin_to_delete = db.query(Finance).filter(Finance.id == trans.id).first()
                                if fin_to_delete:
                                    db.delete(fin_to_delete)
                                    db.commit()
                            finally:
                                db.close()
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No transactions recorded yet.")
    
    with tab3:
        st.subheader("Add New Transaction")
        
        with st.form("add_transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                trans_date = st.date_input("Date*", value=date.today())
                trans_type = st.selectbox("Type*", ["Income", "Expense"])
                category = st.text_input("Category*", placeholder="e.g., Sales, Rent, Supplies")
            with col2:
                description = st.text_input("Description*")
                amount = st.number_input("Amount ($)*", min_value=0.0, value=0.0, step=0.01)
                payment_method = st.selectbox("Payment Method*", ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Check"])
            
            submitted = st.form_submit_button("➕ Add Transaction", use_container_width=True)
            
            if submitted:
                if description and category and amount > 0:
                    db = get_db()
                    try:
                        new_transaction = Finance(
                            date=trans_date,
                            type=trans_type,
                            category=category,
                            description=description,
                            amount=amount,
                            payment_method=payment_method
                        )
                        db.add(new_transaction)
                        db.commit()
                        st.success(f"✅ Transaction added successfully!")
                    finally:
                        db.close()
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*) and ensure amount is greater than 0")

# Labor Page
elif page == "👷 Labor":
    st.title("👷 Labor Tracking")
    st.markdown("Track hours worked and calculate labor costs per product.")
    
    tab1, tab2, tab3 = st.tabs(["📝 Log Hours", "📊 Labor History", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Log Work Hours")
        
        # Get hourly rate
        db = get_db()
        try:
            hourly_rate_setting = db.query(Settings).filter(Settings.setting_key == 'hourly_rate').first()
            if hourly_rate_setting:
                current_hourly_rate = float(hourly_rate_setting.setting_value)
            else:
                current_hourly_rate = 0.0
        finally:
            db.close()
        
        if current_hourly_rate == 0:
            st.warning("⚠️ Please set your hourly rate in the Settings tab before logging hours.")
        
        st.info(f"💵 Current hourly rate: **${current_hourly_rate:.2f}/hour**")
        
        with st.form("log_labor_form"):
            col1, col2 = st.columns(2)
            with col1:
                work_date = st.date_input("Date*", value=date.today())
                worker = st.selectbox("Worker*", ["Emily", "Sage", "Both"])
            with col2:
                hours = st.number_input("Hours Worked*", min_value=0.0, value=0.0, step=0.25)
                
                # Get products for selection
                db = get_db()
                try:
                    products = db.query(Inventory).all()
                    product_options = {f"{p.product_name} ({p.sku})": p.id for p in products}
                finally:
                    db.close()
                
                if product_options:
                    selected_product = st.selectbox("Product*", list(product_options.keys()))
                else:
                    st.warning("No products available. Please add products first.")
                    selected_product = None
            
            notes = st.text_area("Notes (Optional)", placeholder="e.g., Made 20 candles, Applied labels, Packaging")
            
            submitted = st.form_submit_button("➕ Log Hours", use_container_width=True)
            
            if submitted:
                if selected_product and hours > 0:
                    product_id = product_options[selected_product]
                    labor_cost = hours * current_hourly_rate
                    
                    db = get_db()
                    try:
                        new_labor = Labor(
                            product_id=product_id,
                            worker=worker,
                            hours=hours,
                            work_date=work_date,
                            notes=notes
                        )
                        db.add(new_labor)
                        db.commit()
                        st.success(f"✅ Logged {hours} hours for {selected_product.split(' (')[0]}! Labor cost: ${labor_cost:.2f}")
                    finally:
                        db.close()
                    st.rerun()
                else:
                    st.error("Please select a product and enter hours greater than 0")
    
    with tab2:
        st.subheader("Labor History")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            worker_filter = st.selectbox("Filter by Worker", ["All", "Emily", "Sage", "Both"])
        with col2:
            # Get products for filter
            db = get_db()
            try:
                products = db.query(Inventory).all()
                product_filter_options = ["All"] + [f"{p.product_name} ({p.sku})" for p in products]
                product_filter = st.selectbox("Filter by Product", product_filter_options)
            finally:
                db.close()
        
        # Get labor records
        db = get_db()
        try:
            query = db.query(Labor)
            if worker_filter != "All":
                query = query.filter(Labor.worker == worker_filter)
            
            labor_records = query.all()
        finally:
            db.close()
        
        if labor_records:
            # Get current hourly rate
            db = get_db()
            try:
                hourly_rate_setting = db.query(Settings).filter(Settings.setting_key == 'hourly_rate').first()
                hourly_rate = float(hourly_rate_setting.setting_value) if hourly_rate_setting else 0.0
            finally:
                db.close()
            
            # Build dataframe
            labor_data = []
            for labor in labor_records:
                db = get_db()
                try:
                    product = db.query(Inventory).filter(Inventory.id == labor.product_id).first()
                    product_name = f"{product.product_name} ({product.sku})" if product else "Unknown"
                finally:
                    db.close()
                
                # Apply product filter if needed
                if product_filter != "All" and product_name != product_filter:
                    continue
                
                labor_cost = labor.hours * hourly_rate
                labor_data.append({
                    'Date': labor.work_date,
                    'Product': product_name,
                    'Worker': labor.worker,
                    'Hours': labor.hours,
                    'Cost': labor_cost,
                    'Notes': labor.notes or '-'
                })
            
            if labor_data:
                df_labor = pd.DataFrame(labor_data)
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Hours", f"{df_labor['Hours'].sum():.2f}")
                with col2:
                    st.metric("Total Labor Cost", f"${df_labor['Cost'].sum():.2f}")
                with col3:
                    st.metric("Entries", len(df_labor))
                
                st.markdown("---")
                
                # Display table
                st.dataframe(df_labor, use_container_width=True, hide_index=True)
                
                # Export option
                csv = df_labor.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Labor History CSV",
                    csv,
                    f"labor_history_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            else:
                st.info("No labor records match the selected filters.")
        else:
            st.info("No labor hours logged yet. Start tracking in the 'Log Hours' tab!")
    
    with tab3:
        st.subheader("⚙️ Labor Settings")
        
        # Get current hourly rate
        db = get_db()
        try:
            hourly_rate_setting = db.query(Settings).filter(Settings.setting_key == 'hourly_rate').first()
            current_rate = float(hourly_rate_setting.setting_value) if hourly_rate_setting else 0.0
        finally:
            db.close()
        
        st.markdown(f"**Current Hourly Rate:** ${current_rate:.2f}/hour")
        
        with st.form("hourly_rate_form"):
            new_rate = st.number_input("Set Hourly Rate ($)*", min_value=0.0, value=current_rate, step=0.50)
            st.caption("This rate will be used to calculate labor costs across all products.")
            
            submitted = st.form_submit_button("💾 Save Hourly Rate", use_container_width=True)
            
            if submitted:
                db = get_db()
                try:
                    # Check if setting exists
                    existing_setting = db.query(Settings).filter(Settings.setting_key == 'hourly_rate').first()
                    if existing_setting:
                        existing_setting.setting_value = str(new_rate)
                        existing_setting.updated_at = datetime.now()
                    else:
                        new_setting = Settings(
                            setting_key='hourly_rate',
                            setting_value=str(new_rate)
                        )
                        db.add(new_setting)
                    db.commit()
                    st.success(f"✅ Hourly rate updated to ${new_rate:.2f}/hour")
                finally:
                    db.close()
                st.rerun()

# Orders Page
elif page == "🛒 Orders":
    st.title("🛒 Customer Orders")
    
    tab1, tab2 = st.tabs(["📋 All Orders", "📊 Order Stats"])
    
    with tab1:
        st.subheader("Recent Orders")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "pending", "processing", "completed", "cancelled"])
        with col2:
            sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Highest Value", "Lowest Value"])
        
        db = get_db()
        try:
            # Get orders with filters
            query = db.query(Order)
            if status_filter != "All":
                query = query.filter(Order.status == status_filter)
            
            # Apply sorting
            if sort_by == "Newest First":
                query = query.order_by(Order.created_at.desc())
            elif sort_by == "Oldest First":
                query = query.order_by(Order.created_at.asc())
            elif sort_by == "Highest Value":
                query = query.order_by(Order.total_amount.desc())
            else:
                query = query.order_by(Order.total_amount.asc())
            
            orders = query.all()
            
            if orders:
                for order in orders:
                    # Get order items
                    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
                    
                    with st.expander(f"Order #{order.id} - {order.customer_name} - ${order.total_amount:.2f}", expanded=False):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**Customer:** {order.customer_name}")
                            st.markdown(f"**Email:** {order.customer_email}")
                            if order.customer_phone:
                                st.markdown(f"**Phone:** {order.customer_phone}")
                            st.markdown(f"**Order Date:** {order.created_at.strftime('%Y-%m-%d %H:%M')}")
                        
                        with col2:
                            st.markdown(f"**Total Amount:** ${order.total_amount:.2f}")
                            st.markdown(f"**Status:** {order.status.upper()}")
                            if order.notes:
                                st.markdown(f"**Notes:** {order.notes}")
                        
                        with col3:
                            # Status update
                            new_status = st.selectbox(
                                "Update Status",
                                ["pending", "processing", "completed", "cancelled"],
                                index=["pending", "processing", "completed", "cancelled"].index(order.status),
                                key=f"status_{order.id}"
                            )
                            
                            if st.button("Update", key=f"update_{order.id}"):
                                order.status = new_status
                                db.commit()
                                st.success(f"✅ Status updated to {new_status}")
                                st.rerun()
                        
                        st.markdown("---")
                        st.markdown("**Order Items:**")
                        
                        # Display order items
                        items_df = pd.DataFrame([{
                            'Product': item.product_name,
                            'Quantity': item.quantity,
                            'Price': f"${item.price:.2f}",
                            'Subtotal': f"${item.price * item.quantity:.2f}"
                        } for item in order_items])
                        
                        st.dataframe(items_df, use_container_width=True, hide_index=True)
                
                # Export button
                st.markdown("---")
                export_df = pd.DataFrame([{
                    'Order ID': o.id,
                    'Date': o.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Customer Name': o.customer_name,
                    'Customer Email': o.customer_email,
                    'Total Amount': o.total_amount,
                    'Status': o.status
                } for o in orders])
                
                csv = export_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Orders CSV",
                    data=csv,
                    file_name=f"orders_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No orders found matching your filters.")
        finally:
            db.close()
    
    with tab2:
        st.subheader("Order Statistics")
        
        db = get_db()
        try:
            all_orders = db.query(Order).all()
            
            if all_orders:
                # Key Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                total_orders = len(all_orders)
                total_revenue = sum(o.total_amount for o in all_orders)
                avg_order = total_revenue / total_orders if total_orders > 0 else 0
                pending_orders = len([o for o in all_orders if o.status == 'pending'])
                
                with col1:
                    st.metric("Total Orders", f"{total_orders:,}")
                
                with col2:
                    st.metric("Total Revenue", f"${total_revenue:,.2f}")
                
                with col3:
                    st.metric("Avg Order Value", f"${avg_order:.2f}")
                
                with col4:
                    st.metric("Pending Orders", pending_orders)
                
                st.markdown("---")
                
                # Charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Orders by Status
                    status_counts = {}
                    for order in all_orders:
                        status_counts[order.status] = status_counts.get(order.status, 0) + 1
                    
                    fig = px.pie(
                        values=list(status_counts.values()),
                        names=list(status_counts.keys()),
                        title='Orders by Status',
                        color_discrete_sequence=['#6366F1', '#10B981', '#F59E0B', '#EF4444']
                    )
                    fig.update_layout(
                        plot_bgcolor='#0F172A',
                        paper_bgcolor='#0F172A',
                        font=dict(color='#CBD5E1'),
                        title_font=dict(color='#E0E7FF')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Top Products Sold
                    order_items = db.query(OrderItem).all()
                    product_sales = {}
                    for item in order_items:
                        product_sales[item.product_name] = product_sales.get(item.product_name, 0) + item.quantity
                    
                    if product_sales:
                        sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
                        
                        fig = px.bar(
                            x=[p[1] for p in sorted_products],
                            y=[p[0] for p in sorted_products],
                            orientation='h',
                            title='Top 10 Products Sold',
                            labels={'x': 'Quantity', 'y': 'Product'},
                            color=[p[1] for p in sorted_products],
                            color_continuous_scale='Blues'
                        )
                        fig.update_layout(
                            plot_bgcolor='#0F172A',
                            paper_bgcolor='#0F172A',
                            font=dict(color='#CBD5E1'),
                            title_font=dict(color='#E0E7FF'),
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No order items data available yet.")
                
                # Revenue over time
                st.markdown("---")
                df_orders = pd.DataFrame([{
                    'Date': o.created_at.date(),
                    'Amount': o.total_amount
                } for o in all_orders])
                
                daily_revenue = df_orders.groupby('Date')['Amount'].sum().reset_index()
                
                fig = px.line(
                    daily_revenue,
                    x='Date',
                    y='Amount',
                    title='Daily Revenue',
                    markers=True
                )
                fig.update_traces(line_color='#6366F1', marker=dict(size=8))
                fig.update_layout(
                    plot_bgcolor='#0F172A',
                    paper_bgcolor='#0F172A',
                    font=dict(color='#CBD5E1'),
                    title_font=dict(color='#E0E7FF')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No orders yet. Orders will appear here when customers make purchases.")
        finally:
            db.close()

# Ideas Page
elif page == "💡 Ideas":
    st.title("💡 Idea Board")
    
    tab1, tab2 = st.tabs(["📋 View Ideas", "➕ Add Idea"])
    
    with tab1:
        st.subheader("Collaborative Ideas & Projects")
        
        # Filter by status
        status_filter = st.selectbox("Filter by Status", ["All", "Brainstorming", "In Progress", "Completed", "On Hold"])
        
        db = get_db()
        try:
            if status_filter == "All":
                ideas = db.query(Idea).all()
            else:
                ideas = db.query(Idea).filter(Idea.status == status_filter).all()
        finally:
            db.close()
        
        if ideas:
            # Display ideas
            for idea in ideas:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 0.5, 0.5])
                    with col1:
                        st.markdown(f"**{idea.title}**")
                        st.caption(idea.description)
                        # Show attachment if exists
                        if idea.attachment_filename:
                            st.download_button(
                                label=f"📎 {idea.attachment_filename}",
                                data=idea.attachment_data,
                                file_name=idea.attachment_filename,
                                mime="application/octet-stream",
                                key=f"download_{idea.id}"
                            )
                    with col2:
                        # Status badge
                        status_colors = {
                            'Brainstorming': 'warning-badge',
                            'In Progress': 'success-badge',
                            'Completed': 'success-badge',
                            'On Hold': 'danger-badge'
                        }
                        badge_class = status_colors.get(idea.status, 'warning-badge')
                        st.markdown(f"<span class='{badge_class}'>{idea.status}</span>", unsafe_allow_html=True)
                    with col3:
                        priority_colors = {'High': '#EF4444', 'Medium': '#F59E0B', 'Low': '#10B981'}
                        priority_color = priority_colors.get(idea.priority, '#6B7280')
                        st.markdown(f"<span style='color:{priority_color};font-weight:600;'>● {idea.priority}</span>", unsafe_allow_html=True)
                    with col4:
                        if st.button("✏️", key=f"edit_idea_{idea.id}"):
                            if 'editing_idea_id' in st.session_state and st.session_state.editing_idea_id == idea.id:
                                del st.session_state.editing_idea_id
                            else:
                                st.session_state.editing_idea_id = idea.id
                            st.rerun()
                    with col5:
                        if st.button("🗑️", key=f"del_idea_{idea.id}"):
                            db = get_db()
                            try:
                                idea_to_delete = db.query(Idea).filter(Idea.id == idea.id).first()
                                if idea_to_delete:
                                    db.delete(idea_to_delete)
                                    db.commit()
                            finally:
                                db.close()
                            st.rerun()
                    
                    st.caption(f"👤 {idea.assigned_to} | 📅 {idea.created_date}")
                    
                    # Show edit form if this idea is being edited
                    if 'editing_idea_id' in st.session_state and st.session_state.editing_idea_id == idea.id:
                        with st.expander("✏️ Edit Idea", expanded=True):
                            with st.form(f"edit_idea_form_{idea.id}"):
                                edit_title = st.text_input("Title*", value=idea.title)
                                edit_description = st.text_area("Description*", value=idea.description, height=100)
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    status_options = ["Brainstorming", "In Progress", "Completed", "On Hold"]
                                    edit_status = st.selectbox("Status*", status_options, index=status_options.index(idea.status))
                                with col2:
                                    priority_options = ["High", "Medium", "Low"]
                                    edit_priority = st.selectbox("Priority*", priority_options, index=priority_options.index(idea.priority))
                                with col3:
                                    assigned_options = ["Emily", "Sage", "Both"]
                                    edit_assigned_to = st.selectbox("Assigned To*", assigned_options, index=assigned_options.index(idea.assigned_to))
                                
                                # Attachment handling
                                st.markdown("**📎 File Attachment**")
                                if idea.attachment_filename:
                                    st.info(f"Current attachment: {idea.attachment_filename}")
                                    remove_attachment = st.checkbox("Remove current attachment", key=f"remove_att_{idea.id}")
                                else:
                                    remove_attachment = False
                                
                                new_uploaded_file = st.file_uploader(
                                    "Upload new file (replaces current attachment if any)",
                                    type=['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'],
                                    key=f"new_file_{idea.id}",
                                    label_visibility="collapsed"
                                )
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    save_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)
                                with col2:
                                    cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
                                
                                if save_edit:
                                    if edit_title and edit_description:
                                        db = get_db()
                                        try:
                                            idea_to_update = db.query(Idea).filter(Idea.id == idea.id).first()
                                            if idea_to_update:
                                                idea_to_update.title = edit_title
                                                idea_to_update.description = edit_description
                                                idea_to_update.status = edit_status
                                                idea_to_update.priority = edit_priority
                                                idea_to_update.assigned_to = edit_assigned_to
                                                
                                                # Handle attachment updates
                                                if new_uploaded_file is not None:
                                                    # Replace with new file
                                                    idea_to_update.attachment_filename = new_uploaded_file.name
                                                    idea_to_update.attachment_data = new_uploaded_file.read()
                                                elif remove_attachment:
                                                    # Remove attachment
                                                    idea_to_update.attachment_filename = None
                                                    idea_to_update.attachment_data = None
                                                # else: keep existing attachment
                                                
                                                db.commit()
                                                st.success("✅ Idea updated successfully!")
                                                del st.session_state.editing_idea_id
                                        finally:
                                            db.close()
                                        st.rerun()
                                    else:
                                        st.error("Please fill in all required fields (*)")
                                
                                if cancel_edit:
                                    del st.session_state.editing_idea_id
                                    st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No ideas yet. Start brainstorming in the 'Add Idea' tab!")
    
    with tab2:
        st.subheader("Add New Idea")
        
        with st.form("add_idea_form"):
            title = st.text_input("Title*")
            description = st.text_area("Description*", height=100)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                status = st.selectbox("Status*", ["Brainstorming", "In Progress", "Completed", "On Hold"])
            with col2:
                priority = st.selectbox("Priority*", ["High", "Medium", "Low"])
            with col3:
                assigned_to = st.selectbox("Assigned To*", ["Emily", "Sage", "Both"])
            
            # File attachment
            st.markdown("**📎 Attach File (Optional)**")
            uploaded_file = st.file_uploader(
                "Upload supporting documents, images, or files",
                type=['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'],
                label_visibility="collapsed"
            )
            
            submitted = st.form_submit_button("➕ Add Idea", use_container_width=True)
            
            if submitted:
                if title and description:
                    db = get_db()
                    try:
                        # Prepare attachment data if file was uploaded
                        attachment_filename = None
                        attachment_data = None
                        if uploaded_file is not None:
                            attachment_filename = uploaded_file.name
                            attachment_data = uploaded_file.read()
                        
                        new_idea = Idea(
                            title=title,
                            description=description,
                            status=status,
                            priority=priority,
                            assigned_to=assigned_to,
                            created_date=date.today(),
                            attachment_filename=attachment_filename,
                            attachment_data=attachment_data
                        )
                        db.add(new_idea)
                        db.commit()
                        st.success(f"✅ Idea '{title}' added successfully!")
                    finally:
                        db.close()
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")

# Test Data Generator Page
elif page == "🧪 Test Data":
    st.title("🧪 Test Data Generator")
    st.markdown("Quickly populate your database with sample data for testing purposes.")
    
    st.warning("⚠️ **Warning:** This will add test data to your database. Use the 'Clear All Data' option to remove everything.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Current Data Count")
        db = get_db()
        try:
            inventory_count = db.query(Inventory).count()
            materials_count = db.query(Material).count()
            finance_count = db.query(Finance).count()
            ideas_count = db.query(Idea).count()
            bom_count = db.query(BillOfMaterials).count()
            production_count = db.query(ProductionOrder).count()
            labor_count = db.query(Labor).count()
            
            # Get hourly rate
            hourly_rate_setting = db.query(Settings).filter(Settings.setting_key == 'hourly_rate').first()
            hourly_rate = float(hourly_rate_setting.setting_value) if hourly_rate_setting else 0.0
        finally:
            db.close()
        
        st.metric("Products", inventory_count)
        st.metric("Materials", materials_count)
        st.metric("Finance Transactions", finance_count)
        st.metric("Ideas", ideas_count)
        st.metric("BOM Entries", bom_count)
        st.metric("Production Orders", production_count)
        st.metric("Labor Entries", labor_count)
        st.metric("Hourly Rate", f"${hourly_rate:.2f}")
    
    with col2:
        st.subheader("🎲 Generate Test Data")
        
        if st.button("➕ Generate Sample Products (5)", use_container_width=True):
            db = get_db()
            try:
                sample_products = [
                    {"sku": "CANDLE-001", "product_name": "Lavender Soy Candle", "category": "Candles", 
                     "stock_level": 45, "unit_price": 24.99, "min_stock": 20},
                    {"sku": "SOAP-001", "product_name": "Eucalyptus Mint Soap", "category": "Soaps", 
                     "stock_level": 78, "unit_price": 8.99, "min_stock": 30},
                    {"sku": "BALM-001", "product_name": "Healing Lip Balm", "category": "Skincare", 
                     "stock_level": 15, "unit_price": 5.99, "min_stock": 25},
                    {"sku": "DIFFUSER-001", "product_name": "Reed Diffuser Set", "category": "Home Fragrance", 
                     "stock_level": 32, "unit_price": 34.99, "min_stock": 15},
                    {"sku": "SCRUB-001", "product_name": "Coffee Body Scrub", "category": "Skincare", 
                     "stock_level": 22, "unit_price": 18.99, "min_stock": 20}
                ]
                
                for prod in sample_products:
                    # Check if SKU already exists
                    existing = db.query(Inventory).filter(Inventory.sku == prod["sku"]).first()
                    if not existing:
                        new_product = Inventory(**prod, last_updated=datetime.now())
                        db.add(new_product)
                
                db.commit()
                st.success("✅ Sample products added!")
            finally:
                db.close()
            st.rerun()
        
        if st.button("➕ Generate Sample Materials (8)", use_container_width=True):
            db = get_db()
            try:
                sample_materials = [
                    {"material_name": "Soy Wax Flakes", "category": "Raw Materials", "quantity": 500, 
                     "unit": "lbs", "cost_per_unit": 4.50, "supplier": "Wax Supply Co", "reorder_point": 100},
                    {"material_name": "Lavender Essential Oil", "category": "Fragrance", "quantity": 32, 
                     "unit": "oz", "cost_per_unit": 12.00, "supplier": "Essential Oils Inc", "reorder_point": 10},
                    {"material_name": "Glass Jars 8oz", "category": "Packaging", "quantity": 200, 
                     "unit": "units", "cost_per_unit": 1.25, "supplier": "Container World", "reorder_point": 50},
                    {"material_name": "Cotton Wicks", "category": "Components", "quantity": 500, 
                     "unit": "units", "cost_per_unit": 0.15, "supplier": "Candle Supplies", "reorder_point": 100},
                    {"material_name": "Shea Butter", "category": "Raw Materials", "quantity": 25, 
                     "unit": "lbs", "cost_per_unit": 8.75, "supplier": "Natural Ingredients", "reorder_point": 10},
                    {"material_name": "Coconut Oil", "category": "Raw Materials", "quantity": 15, 
                     "unit": "gallons", "cost_per_unit": 22.50, "supplier": "Bulk Oils", "reorder_point": 5},
                    {"material_name": "Beeswax", "category": "Raw Materials", "quantity": 8, 
                     "unit": "lbs", "cost_per_unit": 15.00, "supplier": "Local Apiaries", "reorder_point": 5},
                    {"material_name": "Labels Custom", "category": "Packaging", "quantity": 300, 
                     "unit": "units", "cost_per_unit": 0.35, "supplier": "Print Shop", "reorder_point": 75}
                ]
                
                for mat in sample_materials:
                    # Check if material already exists
                    existing = db.query(Material).filter(Material.material_name == mat["material_name"]).first()
                    if not existing:
                        new_material = Material(**mat, last_updated=datetime.now())
                        db.add(new_material)
                
                db.commit()
                st.success("✅ Sample materials added!")
            finally:
                db.close()
            st.rerun()
        
        if st.button("➕ Generate Finance Transactions (12)", use_container_width=True):
            db = get_db()
            try:
                import random
                sample_transactions = [
                    {"date": date(2024, 11, 1), "type": "Income", "category": "Product Sales", 
                     "amount": 450.00, "payment_method": "Credit Card", "description": "Online order #1234"},
                    {"date": date(2024, 11, 3), "type": "Expense", "category": "Supplies", 
                     "amount": 225.00, "payment_method": "Bank Transfer", "description": "Wax supply order"},
                    {"date": date(2024, 11, 5), "type": "Income", "category": "Product Sales", 
                     "amount": 680.50, "payment_method": "PayPal", "description": "Market booth sales"},
                    {"date": date(2024, 11, 8), "type": "Expense", "category": "Marketing", 
                     "amount": 150.00, "payment_method": "Credit Card", "description": "Social media ads"},
                    {"date": date(2024, 11, 10), "type": "Income", "category": "Wholesale", 
                     "amount": 1200.00, "payment_method": "Check", "description": "Bulk order - Gift shop"},
                    {"date": date(2024, 11, 12), "type": "Expense", "category": "Utilities", 
                     "amount": 85.00, "payment_method": "Auto-pay", "description": "Electric bill"},
                    {"date": date(2024, 11, 14), "type": "Income", "category": "Product Sales", 
                     "amount": 320.75, "payment_method": "Credit Card", "description": "Website orders"},
                    {"date": date(2024, 11, 15), "type": "Expense", "category": "Supplies", 
                     "amount": 340.00, "payment_method": "Credit Card", "description": "Essential oils restock"},
                    {"date": date(2024, 11, 16), "type": "Income", "category": "Custom Orders", 
                     "amount": 275.00, "payment_method": "Venmo", "description": "Wedding favors"},
                    {"date": date(2024, 11, 17), "type": "Expense", "category": "Packaging", 
                     "amount": 120.00, "payment_method": "Credit Card", "description": "Jar and label order"},
                    {"date": date(2024, 11, 18), "type": "Income", "category": "Product Sales", 
                     "amount": 580.00, "payment_method": "Cash", "description": "Craft fair sales"},
                    {"date": date(2024, 11, 18), "type": "Expense", "category": "Business Services", 
                     "amount": 50.00, "payment_method": "Credit Card", "description": "Accounting software"}
                ]
                
                for trans in sample_transactions:
                    new_transaction = Finance(**trans)
                    db.add(new_transaction)
                
                db.commit()
                st.success("✅ Sample finance transactions added!")
            finally:
                db.close()
            st.rerun()
        
        if st.button("➕ Generate Sample Ideas (4)", use_container_width=True):
            db = get_db()
            try:
                sample_ideas = [
                    {"title": "Launch Holiday Gift Sets", "description": "Create themed gift bundles for the holiday season with curated product combinations. Include special packaging and holiday-themed scents.", 
                     "status": "In Progress", "priority": "High", "assigned_to": "Both", "created_date": date(2024, 11, 1)},
                    {"title": "Expand to Farmer's Markets", "description": "Research and apply to local farmer's markets for spring/summer season. Create portable booth setup.", 
                     "status": "Brainstorming", "priority": "Medium", "assigned_to": "Emily", "created_date": date(2024, 11, 5)},
                    {"title": "Subscription Box Service", "description": "Monthly subscription model with rotating product selections. Need to calculate pricing and logistics.", 
                     "status": "On Hold", "priority": "Low", "assigned_to": "Sage", "created_date": date(2024, 10, 20)},
                    {"title": "Instagram Reels Content Strategy", "description": "Develop a content calendar for daily/weekly reels showing behind-the-scenes production, product tips, and customer testimonials.", 
                     "status": "In Progress", "priority": "High", "assigned_to": "Both", "created_date": date(2024, 11, 10)}
                ]
                
                for idea in sample_ideas:
                    new_idea = Idea(**idea)
                    db.add(new_idea)
                
                db.commit()
                st.success("✅ Sample ideas added!")
            finally:
                db.close()
            st.rerun()
        
        if st.button("➕ Generate Sample BOMs (3)", use_container_width=True):
            db = get_db()
            try:
                # Get existing products and materials
                products = db.query(Inventory).all()
                materials = db.query(Material).all()
                
                if not products or not materials:
                    st.error("⚠️ Please generate products and materials first!")
                else:
                    # Create BOMs for first 3 products if they exist
                    bom_data = []
                    
                    # Lavender Soy Candle BOM
                    if len(products) >= 1:
                        candle = products[0]
                        soy_wax = next((m for m in materials if "Soy Wax" in m.material_name), None)
                        lavender_oil = next((m for m in materials if "Lavender" in m.material_name), None)
                        jar = next((m for m in materials if "Glass Jar" in m.material_name), None)
                        wick = next((m for m in materials if "Wick" in m.material_name), None)
                        
                        if soy_wax and lavender_oil and jar and wick:
                            bom_data.extend([
                                {"product_id": candle.id, "material_id": soy_wax.id, "quantity_needed": 0.5},
                                {"product_id": candle.id, "material_id": lavender_oil.id, "quantity_needed": 0.3},
                                {"product_id": candle.id, "material_id": jar.id, "quantity_needed": 1},
                                {"product_id": candle.id, "material_id": wick.id, "quantity_needed": 1}
                            ])
                    
                    # Soap BOM
                    if len(products) >= 2:
                        soap = products[1]
                        shea = next((m for m in materials if "Shea" in m.material_name), None)
                        coconut = next((m for m in materials if "Coconut" in m.material_name), None)
                        
                        if shea and coconut:
                            bom_data.extend([
                                {"product_id": soap.id, "material_id": shea.id, "quantity_needed": 0.25},
                                {"product_id": soap.id, "material_id": coconut.id, "quantity_needed": 0.1}
                            ])
                    
                    # Lip Balm BOM
                    if len(products) >= 3:
                        balm = products[2]
                        beeswax = next((m for m in materials if "Beeswax" in m.material_name), None)
                        shea = next((m for m in materials if "Shea" in m.material_name), None)
                        
                        if beeswax and shea:
                            bom_data.extend([
                                {"product_id": balm.id, "material_id": beeswax.id, "quantity_needed": 0.15},
                                {"product_id": balm.id, "material_id": shea.id, "quantity_needed": 0.1}
                            ])
                    
                    added_count = 0
                    for bom in bom_data:
                        # Check if BOM entry already exists
                        existing = db.query(BillOfMaterials).filter(
                            BillOfMaterials.product_id == bom["product_id"],
                            BillOfMaterials.material_id == bom["material_id"]
                        ).first()
                        if not existing:
                            new_bom = BillOfMaterials(**bom)
                            db.add(new_bom)
                            added_count += 1
                    
                    db.commit()
                    if added_count > 0:
                        st.success(f"✅ {added_count} BOM entries added!")
                    else:
                        st.info("ℹ️ All BOMs already exist!")
            finally:
                db.close()
            st.rerun()
        
        if st.button("➕ Generate Sample Production Orders (3)", use_container_width=True):
            db = get_db()
            try:
                products = db.query(Inventory).all()
                
                if not products:
                    st.error("⚠️ Please generate products first!")
                else:
                    sample_orders = []
                    
                    if len(products) >= 1:
                        sample_orders.append({
                            "product_id": products[0].id,
                            "quantity_produced": 20,
                            "production_date": date(2024, 11, 10),
                            "produced_by": "Emily",
                            "material_cost": 95.00,
                            "notes": "First batch of holiday season candles"
                        })
                    
                    if len(products) >= 2:
                        sample_orders.append({
                            "product_id": products[1].id,
                            "quantity_produced": 30,
                            "production_date": date(2024, 11, 12),
                            "produced_by": "Sage",
                            "material_cost": 42.50,
                            "notes": "Eucalyptus mint soap batch for market"
                        })
                    
                    if len(products) >= 3:
                        sample_orders.append({
                            "product_id": products[2].id,
                            "quantity_produced": 50,
                            "production_date": date(2024, 11, 15),
                            "produced_by": "Both",
                            "material_cost": 28.75,
                            "notes": "Lip balm production for wholesale order"
                        })
                    
                    added_count = 0
                    for order in sample_orders:
                        new_order = ProductionOrder(**order)
                        db.add(new_order)
                        added_count += 1
                    
                    db.commit()
                    if added_count > 0:
                        st.success(f"✅ {added_count} production orders added!")
                    else:
                        st.warning("⚠️ Not enough products to generate production orders!")
            finally:
                db.close()
            st.rerun()
        
        if st.button("💵 Set Hourly Rate ($15/hour)", use_container_width=True):
            db = get_db()
            try:
                # Check if setting exists
                existing_setting = db.query(Settings).filter(Settings.setting_key == 'hourly_rate').first()
                if existing_setting:
                    st.info(f"ℹ️ Hourly rate already set to ${existing_setting.setting_value}/hour")
                else:
                    new_setting = Settings(
                        setting_key='hourly_rate',
                        setting_value='15.00'
                    )
                    db.add(new_setting)
                    db.commit()
                    st.success("✅ Hourly rate set to $15.00/hour")
            finally:
                db.close()
            st.rerun()
        
        if st.button("➕ Generate Sample Labor Entries (6)", use_container_width=True):
            db = get_db()
            try:
                products = db.query(Inventory).all()
                
                if not products:
                    st.error("⚠️ Please generate products first!")
                else:
                    sample_labor = []
                    
                    # Labor for candles
                    if len(products) >= 1:
                        sample_labor.extend([
                            {"product_id": products[0].id, "worker": "Emily", "hours": 3.0, 
                             "work_date": date(2024, 11, 10), "notes": "Melted wax and poured candles"},
                            {"product_id": products[0].id, "worker": "Sage", "hours": 2.5, 
                             "work_date": date(2024, 11, 11), "notes": "Applied labels and packaged"}
                        ])
                    
                    # Labor for soap
                    if len(products) >= 2:
                        sample_labor.extend([
                            {"product_id": products[1].id, "worker": "Both", "hours": 4.0, 
                             "work_date": date(2024, 11, 12), "notes": "Made soap batch"},
                            {"product_id": products[1].id, "worker": "Emily", "hours": 1.5, 
                             "work_date": date(2024, 11, 13), "notes": "Cut and wrapped soaps"}
                        ])
                    
                    # Labor for lip balm
                    if len(products) >= 3:
                        sample_labor.extend([
                            {"product_id": products[2].id, "worker": "Sage", "hours": 2.0, 
                             "work_date": date(2024, 11, 15), "notes": "Mixed and filled lip balm tubes"},
                            {"product_id": products[2].id, "worker": "Emily", "hours": 1.0, 
                             "work_date": date(2024, 11, 15), "notes": "Labeled and quality checked"}
                        ])
                    
                    added_count = 0
                    for labor in sample_labor:
                        new_labor = Labor(**labor)
                        db.add(new_labor)
                        added_count += 1
                    
                    db.commit()
                    if added_count > 0:
                        st.success(f"✅ {added_count} labor entries added!")
                    else:
                        st.warning("⚠️ Not enough products to generate labor entries!")
            finally:
                db.close()
            st.rerun()
    
    st.markdown("---")
    
    # Danger zone
    st.subheader("🗑️ Danger Zone")
    
    with st.expander("⚠️ Clear All Data", expanded=False):
        st.error("**Warning:** This will permanently delete ALL data from your database. This action cannot be undone!")
        
        confirm_text = st.text_input("Type 'DELETE ALL DATA' to confirm:")
        
        if st.button("🗑️ Clear All Data", type="primary", use_container_width=True):
            if confirm_text == "DELETE ALL DATA":
                db = get_db()
                try:
                    # Delete in proper order to respect foreign keys
                    # First delete all child records that reference parent tables
                    db.query(Labor).delete()
                    db.query(ProductionOrder).delete()
                    db.query(BillOfMaterials).delete()
                    db.query(OrderItem).delete() # Added OrderItem delete
                    db.query(Order).delete()     # Added Order delete
                    # Then delete independent tables
                    db.query(Finance).delete()
                    db.query(Idea).delete()
                    db.query(Settings).delete()
                    # Finally delete parent tables
                    db.query(Inventory).delete()
                    db.query(Material).delete()
                    db.commit()
                    st.success("✅ All data has been cleared!")
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Error clearing data: {str(e)}")
                finally:
                    db.close()
                st.rerun()
            else:
                st.error("Please type 'DELETE ALL DATA' exactly to confirm.")
