import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

# Page config
st.set_page_config(
    page_title="ConnectUAE Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all data files"""
    try:
        subscribers = pd.read_csv('data/subscribers.csv')
        usage = pd.read_csv('data/usage_records.csv')
        billing = pd.read_csv('data/billing.csv')
        tickets = pd.read_csv('data/tickets.csv')
        outages = pd.read_csv('data/network_outages.csv')
        
        # Convert date columns
        subscribers['activation_date'] = pd.to_datetime(subscribers['activation_date'])
        subscribers['churn_date'] = pd.to_datetime(subscribers['churn_date'])
        usage['usage_date'] = pd.to_datetime(usage['usage_date'])
        billing['bill_date'] = pd.to_datetime(billing['bill_date'])
        billing['due_date'] = pd.to_datetime(billing['due_date'])
        billing['payment_date'] = pd.to_datetime(billing['payment_date'])
        tickets['ticket_date'] = pd.to_datetime(tickets['ticket_date'])
        tickets['resolution_date'] = pd.to_datetime(tickets['resolution_date'])
        outages['outage_start_time'] = pd.to_datetime(outages['outage_start_time'])
        outages['outage_end_time'] = pd.to_datetime(outages['outage_end_time'])
        
        return subscribers, usage, billing, tickets, outages
    except FileNotFoundError:
        st.error("Data files not found. Please run generate_data.py first.")
        st.stop()

def show_data_quality_report(subscribers, usage, billing, tickets, outages):
    """Display data quality issues"""
    st.header("🔍 Data Quality Report")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Missing Values")
        missing_usage = usage['data_usage_gb'].isna().sum()
        missing_billing = billing['payment_date'].isna().sum()
        missing_tickets = tickets['resolution_date'].isna().sum()
        
        st.metric("Usage Records (missing data_usage_gb)", missing_usage)
        st.metric("Billing Records (missing payment_date)", missing_billing)
        st.metric("Tickets (missing resolution_date)", missing_tickets)
    
    with col2:
        st.subheader("Duplicates")
        dup_subscribers = subscribers['subscriber_id'].duplicated().sum()
        dup_tickets = tickets['ticket_id'].duplicated().sum()
        dup_billing = billing['bill_id'].duplicated().sum()
        
        st.metric("Duplicate Subscribers", dup_subscribers)
        st.metric("Duplicate Tickets", dup_tickets)
        st.metric("Duplicate Bills", dup_billing)
    
    with col3:
        st.subheader("Data Issues")
        outlier_usage = (usage['data_usage_gb'] > 500).sum()
        outlier_bills = (billing['bill_amount'] > 5000).sum()
        impossible_dates = (tickets['resolution_date'] < tickets['ticket_date']).sum()
        
        st.metric("Outlier Usage (>500GB)", outlier_usage)
        st.metric("Outlier Bills (>5000 AED)", outlier_bills)
        st.metric("Impossible Ticket Dates", impossible_dates)
    
    # Inconsistent labels
    st.subheader("Label Consistency Issues")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Plan Type Variations**")
        st.write(subscribers['plan_type'].value_counts())
    
    with col2:
        st.write("**City Variations**")
        st.write(subscribers['city'].value_counts().head(10))
    
    with col3:
        st.write("**Ticket Status Variations**")
        st.write(tickets['ticket_status'].value_counts())

def executive_view(subscribers, usage, billing, tickets, outages):
    """Executive dashboard view"""
    st.header("📊 Executive View - Revenue & Subscriber Health")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    total_revenue = billing['bill_amount'].sum()
    active_subs = (subscribers['status'] == 'Active').sum()
    avg_arpu = billing.groupby('subscriber_id')['bill_amount'].mean().mean()
    overdue_revenue = billing[billing['payment_status'] == 'Overdue']['bill_amount'].sum()
    
    with col1:
        st.metric("Total Revenue (AED)", f"{total_revenue/1_000_000:.2f}M")
    with col2:
        st.metric("Active Subscribers", f"{active_subs:,}")
    with col3:
        st.metric("Avg ARPU (AED)", f"{avg_arpu:.0f}")
    with col4:
        st.metric("Revenue at Risk (AED)", f"{overdue_revenue/1_000_000:.2f}M")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # ARPU Trend
        billing['month'] = billing['bill_date'].dt.to_period('M')
        monthly_arpu = billing.groupby('month').agg({
            'bill_amount': 'sum',
            'subscriber_id': 'nunique'
        })
        monthly_arpu['arpu'] = monthly_arpu['bill_amount'] / monthly_arpu['subscriber_id']
        
        fig = px.line(monthly_arpu, y='arpu', title='ARPU Trend by Month')
        fig.update_layout(xaxis_title='Month', yaxis_title='ARPU (AED)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue by Plan Type
        sub_billing = subscribers.merge(billing, on='subscriber_id')
        plan_revenue = sub_billing.groupby('plan_type')['bill_amount'].sum().reset_index()
        
        fig = px.pie(plan_revenue, values='bill_amount', names='plan_type', 
                     title='Revenue Distribution by Plan Type')
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by City
        city_revenue = sub_billing.groupby('city')['bill_amount'].sum().reset_index()
        city_revenue = city_revenue.sort_values('bill_amount', ascending=False)
        
        fig = px.bar(city_revenue, x='city', y='bill_amount', 
                     title='Total Revenue by City (AED)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Overdue by City
        overdue_city = sub_billing[sub_billing['payment_status'] == 'Overdue'].groupby('city')['bill_amount'].sum().reset_index()
        
        fig = px.bar(overdue_city, x='city', y='bill_amount', 
                     title='Overdue Payments by City (AED)', color_discrete_sequence=['#ff4444'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Subscriber Status
    col1, col2 = st.columns(2)
    
    with col1:
        status_counts = subscribers['status'].value_counts().reset_index()
        fig = px.bar(status_counts, x='status', y='count', 
                     title='Subscriber Status Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Payment Status
        payment_counts = billing['payment_status'].value_counts().reset_index()
        fig = px.pie(payment_counts, values='count', names='payment_status',
                     title='Payment Status Distribution')
        st.plotly_chart(fig, use_container_width=True)

def operations_view(subscribers, usage, billing, tickets, outages):
    """Operations manager dashboard view"""
    st.header("⚙️ Operations View - Service Quality & Network")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    open_tickets = tickets[tickets['ticket_status'].isin(['Open', 'In Progress'])].shape[0]
    resolved_tickets = tickets[tickets['ticket_status'] == 'Resolved'].shape[0]
    
    # Calculate avg resolution time
    resolved = tickets[tickets['ticket_status'] == 'Resolved'].copy()
    resolved['resolution_time'] = (resolved['resolution_date'] - resolved['ticket_date']).dt.total_seconds() / 3600
    avg_resolution = resolved['resolution_time'].mean()
    
    # SLA compliance (48 hours)
    sla_compliant = (resolved['resolution_time'] <= 48).sum()
    sla_rate = (sla_compliant / len(resolved) * 100) if len(resolved) > 0 else 0
    
    total_outage_mins = outages['outage_duration_mins'].sum()
    
    with col1:
        st.metric("Open Tickets", open_tickets)
    with col2:
        st.metric("Avg Resolution (hours)", f"{avg_resolution:.1f}")
    with col3:
        st.metric("SLA Compliance", f"{sla_rate:.1f}%")
    with col4:
        st.metric("Total Outage Minutes", f"{total_outage_mins:,.0f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Top ticket categories
        category_counts = tickets['ticket_category'].value_counts().reset_index().head(5)
        fig = px.bar(category_counts, x='ticket_category', y='count',
                     title='Top 5 Ticket Categories')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Tickets by channel
        channel_counts = tickets['ticket_channel'].value_counts().reset_index()
        fig = px.pie(channel_counts, values='count', names='ticket_channel',
                     title='Tickets by Support Channel')
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tickets by city
        city_tickets = tickets.merge(subscribers[['subscriber_id', 'city']], on='subscriber_id')
        city_ticket_counts = city_tickets['city'].value_counts().reset_index()
        
        fig = px.bar(city_ticket_counts, x='city', y='count',
                     title='Ticket Volume by City')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Ticket status distribution
        status_counts = tickets['ticket_status'].value_counts().reset_index()
        fig = px.bar(status_counts, x='ticket_status', y='count',
                     title='Ticket Status Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Network outages by city
        outage_city = outages['affected_city'].value_counts().reset_index()
        fig = px.bar(outage_city, x='affected_city', y='count',
                     title='Network Outage Incidents by City')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Outage types
        outage_types = outages['outage_type'].value_counts().reset_index()
        fig = px.pie(outage_types, values='count', names='outage_type',
                     title='Outage Types Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Resolution time by category
    st.subheader("Average Resolution Time by Category")
    category_resolution = resolved.groupby('ticket_category')['resolution_time'].mean().reset_index()
    category_resolution = category_resolution.sort_values('resolution_time', ascending=False)
    
    fig = px.bar(category_resolution, x='ticket_category', y='resolution_time',
                 title='Avg Resolution Time by Category (hours)')
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Header
    st.title("📱 ConnectUAE - Revenue & Service Operations Dashboard")
    st.markdown("**Telecommunications Analytics Platform**")
    
    # Load data
    with st.spinner("Loading data..."):
        subscribers, usage, billing, tickets, outages = load_data()
    
    # Sidebar
    st.sidebar.title("Navigation")
    view = st.sidebar.radio(
        "Select View",
        ["Executive View", "Operations View", "Data Quality Report", "Raw Data Explorer"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **Data Summary**
    - Subscribers: {len(subscribers):,}
    - Usage Records: {len(usage):,}
    - Billing Records: {len(billing):,}
    - Tickets: {len(tickets):,}
    - Network Outages: {len(outages):,}
    """)
    
    # Display selected view
    if view == "Executive View":
        executive_view(subscribers, usage, billing, tickets, outages)
    elif view == "Operations View":
        operations_view(subscribers, usage, billing, tickets, outages)
    elif view == "Data Quality Report":
        show_data_quality_report(subscribers, usage, billing, tickets, outages)
    else:
        st.header("📋 Raw Data Explorer")
        dataset = st.selectbox("Select Dataset", 
                              ["Subscribers", "Usage Records", "Billing", "Tickets", "Network Outages"])
        
        if dataset == "Subscribers":
            st.dataframe(subscribers)
            st.download_button("Download CSV", subscribers.to_csv(index=False), 
                             "subscribers.csv", "text/csv")
        elif dataset == "Usage Records":
            st.dataframe(usage)
            st.download_button("Download CSV", usage.to_csv(index=False), 
                             "usage_records.csv", "text/csv")
        elif dataset == "Billing":
            st.dataframe(billing)
            st.download_button("Download CSV", billing.to_csv(index=False), 
                             "billing.csv", "text/csv")
        elif dataset == "Tickets":
            st.dataframe(tickets)
            st.download_button("Download CSV", tickets.to_csv(index=False), 
                             "tickets.csv", "text/csv")
        else:
            st.dataframe(outages)
            st.download_button("Download CSV", outages.to_csv(index=False), 
                             "network_outages.csv", "text/csv")

if __name__ == "__main__":
    main()
