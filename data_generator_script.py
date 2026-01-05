import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
SUBSCRIBER_COUNT = 5000
USAGE_COUNT = 50000
BILLING_COUNT = 15000
TICKET_COUNT = 6000
OUTAGE_COUNT = 200

# Date ranges
END_DATE = datetime(2026, 1, 4)
START_DATE = END_DATE - timedelta(days=120)
ACTIVATION_START = END_DATE - timedelta(days=730)  # 2 years back

# Distribution parameters
CITIES = {
    'Dubai': 0.35,
    'Abu Dhabi': 0.30,
    'Sharjah': 0.20,
    'Ajman': 0.10,
    'Fujairah': 0.05
}

PLAN_TYPES = {'Prepaid': 0.60, 'Postpaid': 0.40}

PLAN_NAMES = {
    'Basic': 0.30,
    'Standard': 0.35,
    'Premium': 0.25,
    'Unlimited': 0.10
}

PLAN_CHARGES = {
    'Basic': (50, 100),
    'Standard': (100, 200),
    'Premium': (200, 350),
    'Unlimited': (350, 500)
}

SUBSCRIBER_STATUS = {
    'Active': 0.85,
    'Suspended': 0.10,
    'Churned': 0.05
}

PAYMENT_STATUS = {
    'Paid': 0.70,
    'Overdue': 0.15,
    'Partial': 0.10,
    'Pending': 0.05
}

TICKET_CATEGORIES = {
    'Network Issue': 0.35,
    'Billing Query': 0.25,
    'Technical Support': 0.20,
    'Plan Change': 0.12,
    'Complaint': 0.08
}

TICKET_STATUS = {
    'Resolved': 0.65,
    'In Progress': 0.20,
    'Open': 0.10,
    'Escalated': 0.05
}

TICKET_CHANNELS = {
    'Call Center': 0.40,
    'App': 0.30,
    'Online Chat': 0.20,
    'Retail Store': 0.10
}

OUTAGE_TYPES = {
    'Planned Maintenance': 0.25,
    'Equipment Failure': 0.35,
    'Power Outage': 0.20,
    'Fiber Cut': 0.15,
    'Weather': 0.05
}

def weighted_choice(choices_dict):
    """Select item based on weighted probabilities"""
    choices = list(choices_dict.keys())
    weights = list(choices_dict.values())
    return random.choices(choices, weights=weights)[0]

def inject_inconsistent_labels(series, variations):
    """Inject label inconsistencies"""
    result = series.copy()
    num_changes = int(len(result) * 0.05)  # 5% variations
    indices = np.random.choice(len(result), num_changes, replace=False)
    
    for idx in indices:
        original = result.iloc[idx]
        if original in variations:
            result.iloc[idx] = random.choice(variations[original])
    
    return result

def generate_subscribers():
    """Generate subscribers table"""
    print("Generating subscribers...")
    
    subscribers = []
    for i in range(SUBSCRIBER_COUNT):
        subscriber_id = f"SUB{str(i+1).zfill(6)}"
        city = weighted_choice(CITIES)
        plan_type = weighted_choice(PLAN_TYPES)
        plan_name = weighted_choice(PLAN_NAMES)
        status = weighted_choice(SUBSCRIBER_STATUS)
        
        min_charge, max_charge = PLAN_CHARGES[plan_name]
        monthly_charge = round(random.uniform(min_charge, max_charge), 2)
        
        activation_date = ACTIVATION_START + timedelta(
            days=random.randint(0, (END_DATE - ACTIVATION_START).days)
        )
        
        churn_date = None
        if status == 'Churned':
            churn_date = activation_date + timedelta(days=random.randint(30, 700))
        
        subscribers.append({
            'subscriber_id': subscriber_id,
            'city': city,
            'plan_type': plan_type,
            'plan_name': plan_name,
            'monthly_charge': monthly_charge,
            'activation_date': activation_date,
            'status': status,
            'churn_date': churn_date
        })
    
    df = pd.DataFrame(subscribers)
    
    # Inject duplicates (80 records)
    duplicate_indices = np.random.choice(df.index, 80, replace=False)
    duplicates = df.loc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Inject inconsistent labels
    plan_variations = {
        'Prepaid': ['PREPAID', 'prepaid', 'Pre-paid'],
        'Postpaid': ['POSTPAID', 'postpaid', 'Post-paid']
    }
    city_variations = {
        'Abu Dhabi': ['AbuDhabi', 'Abu-Dhabi', 'AD'],
        'Dubai': ['DUBAI', 'dubai']
    }
    
    df['plan_type'] = inject_inconsistent_labels(df['plan_type'], plan_variations)
    df['city'] = inject_inconsistent_labels(df['city'], city_variations)
    
    return df

def generate_usage_records(subscribers):
    """Generate usage records"""
    print("Generating usage records...")
    
    active_churned = subscribers[subscribers['status'].isin(['Active', 'Suspended'])]
    
    usage_records = []
    for _ in range(USAGE_COUNT):
        sub = active_churned.sample(1).iloc[0]
        
        # Generate usage date after activation
        days_after_activation = (END_DATE - sub['activation_date']).days
        if days_after_activation > 0:
            usage_date = sub['activation_date'] + timedelta(
                days=random.randint(0, min(days_after_activation, 120))
            )
        else:
            usage_date = END_DATE - timedelta(days=random.randint(0, 120))
        
        # Generate usage metrics
        data_usage = round(random.lognormal(3, 1.2), 2)  # Log-normal for realistic distribution
        call_minutes = random.randint(0, 500)
        sms_count = random.randint(0, 200)
        roaming = random.choice([True, False]) if random.random() < 0.1 else False
        roaming_charges = round(random.uniform(20, 200), 2) if roaming else 0
        
        usage_records.append({
            'usage_id': f"USG{len(usage_records)+1:07d}",
            'subscriber_id': sub['subscriber_id'],
            'usage_date': usage_date,
            'data_usage_gb': data_usage,
            'call_minutes': call_minutes,
            'sms_count': sms_count,
            'roaming_charges': roaming_charges
        })
    
    df = pd.DataFrame(usage_records)
    
    # Inject missing values (~500 records)
    missing_indices = np.random.choice(df.index, 500, replace=False)
    df.loc[missing_indices, 'data_usage_gb'] = np.nan
    
    # Inject outliers (30 records with >500 GB)
    outlier_indices = np.random.choice(df.index, 30, replace=False)
    df.loc[outlier_indices, 'data_usage_gb'] = np.random.uniform(500, 1000, 30)
    
    # Inject impossible dates (10 records before activation)
    impossible_indices = np.random.choice(df.index, 10, replace=False)
    for idx in impossible_indices:
        sub_id = df.loc[idx, 'subscriber_id']
        activation = subscribers[subscribers['subscriber_id'] == sub_id]['activation_date'].iloc[0]
        df.loc[idx, 'usage_date'] = activation - timedelta(days=random.randint(1, 30))
    
    return df

def generate_billing(subscribers):
    """Generate billing records"""
    print("Generating billing records...")
    
    billing_records = []
    
    # Generate 3 months of bills for each subscriber
    for _, sub in subscribers.iterrows():
        if sub['status'] == 'Churned':
            num_bills = random.randint(1, 3)
        else:
            num_bills = 3
        
        for month in range(num_bills):
            bill_date = END_DATE - timedelta(days=90 - (month * 30))
            due_date = bill_date + timedelta(days=15)
            
            # Calculate bill amount
            base_charge = sub['monthly_charge']
            addon_charges = round(random.uniform(0, 50), 2) if random.random() < 0.3 else 0
            roaming_charges = round(random.uniform(20, 200), 2) if random.random() < 0.1 else 0
            bill_amount = round(base_charge + addon_charges + roaming_charges, 2)
            
            payment_status = weighted_choice(PAYMENT_STATUS)
            
            payment_date = None
            if payment_status == 'Paid':
                payment_date = due_date - timedelta(days=random.randint(0, 10))
            elif payment_status == 'Partial':
                payment_date = due_date + timedelta(days=random.randint(0, 20))
                bill_amount *= 0.5  # Partial payment
            
            billing_records.append({
                'bill_id': f"BILL{len(billing_records)+1:07d}",
                'subscriber_id': sub['subscriber_id'],
                'bill_date': bill_date,
                'due_date': due_date,
                'bill_amount': bill_amount,
                'payment_status': payment_status,
                'payment_date': payment_date
            })
    
    df = pd.DataFrame(billing_records).sample(BILLING_COUNT, replace=False).reset_index(drop=True)
    
    # Inject duplicates (40 records)
    duplicate_indices = np.random.choice(df.index, 40, replace=False)
    duplicates = df.loc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Inject missing payment_date for "Paid" status (~200 records)
    paid_records = df[df['payment_status'] == 'Paid'].index
    missing_indices = np.random.choice(paid_records, min(200, len(paid_records)), replace=False)
    df.loc[missing_indices, 'payment_date'] = pd.NaT
    
    # Inject outliers (20 bills >5000 AED)
    outlier_indices = np.random.choice(df.index, 20, replace=False)
    df.loc[outlier_indices, 'bill_amount'] = np.random.uniform(5000, 10000, 20)
    
    # Inject impossible values (5 negative bills)
    negative_indices = np.random.choice(df.index, 5, replace=False)
    df.loc[negative_indices, 'bill_amount'] = -np.random.uniform(50, 200, 5)
    
    return df

def generate_tickets(subscribers):
    """Generate support tickets"""
    print("Generating tickets...")
    
    tickets = []
    for i in range(TICKET_COUNT):
        sub = subscribers.sample(1).iloc[0]
        
        ticket_date = START_DATE + timedelta(days=random.randint(0, 120))
        category = weighted_choice(TICKET_CATEGORIES)
        status = weighted_choice(TICKET_STATUS)
        channel = weighted_choice(TICKET_CHANNELS)
        
        resolution_date = None
        if status == 'Resolved':
            resolution_hours = random.randint(1, 96)  # 1 to 96 hours
            resolution_date = ticket_date + timedelta(hours=resolution_hours)
        
        tickets.append({
            'ticket_id': f"TKT{i+1:07d}",
            'subscriber_id': sub['subscriber_id'],
            'ticket_date': ticket_date,
            'ticket_category': category,
            'ticket_status': status,
            'ticket_channel': channel,
            'resolution_date': resolution_date
        })
    
    df = pd.DataFrame(tickets)
    
    # Inject duplicates (60 records)
    duplicate_indices = np.random.choice(df.index, 60, replace=False)
    duplicates = df.loc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Inject missing resolution_date for "Resolved" (~100 records)
    resolved_records = df[df['ticket_status'] == 'Resolved'].index
    missing_indices = np.random.choice(resolved_records, min(100, len(resolved_records)), replace=False)
    df.loc[missing_indices, 'resolution_date'] = pd.NaT
    
    # Inject inconsistent status labels
    status_variations = {
        'Resolved': ['resolved', 'RESOLVED', 'Closed'],
        'Open': ['open', 'OPEN']
    }
    df['ticket_status'] = inject_inconsistent_labels(df['ticket_status'], status_variations)
    
    # Inject impossible dates (15 records)
    impossible_indices = np.random.choice(df[df['resolution_date'].notna()].index, 15, replace=False)
    for idx in impossible_indices:
        ticket_date = df.loc[idx, 'ticket_date']
        df.loc[idx, 'resolution_date'] = ticket_date - timedelta(hours=random.randint(1, 48))
    
    return df

def generate_outages():
    """Generate network outage records"""
    print("Generating network outages...")
    
    outages = []
    for i in range(OUTAGE_COUNT):
        city = weighted_choice(CITIES)
        outage_type = weighted_choice(OUTAGE_TYPES)
        
        outage_start = START_DATE + timedelta(
            days=random.randint(0, 120),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Duration based on type
        if outage_type == 'Planned Maintenance':
            duration_mins = random.randint(60, 360)
        elif outage_type == 'Weather':
            duration_mins = random.randint(30, 180)
        else:
            duration_mins = random.randint(15, 720)
        
        outage_end = outage_start + timedelta(minutes=duration_mins)
        affected_subscribers = random.randint(100, 5000)
        
        outages.append({
            'outage_id': f"OUT{i+1:05d}",
            'affected_city': city,
            'outage_type': outage_type,
            'outage_start_time': outage_start,
            'outage_end_time': outage_end,
            'outage_duration_mins': duration_mins,
            'affected_subscribers': affected_subscribers
        })
    
    df = pd.DataFrame(outages)
    
    # Inject missing duration (~10 records)
    missing_indices = np.random.choice(df.index, 10, replace=False)
    df.loc[missing_indices, 'outage_duration_mins'] = np.nan
    
    # Inject outliers (10 outages >1440 minutes)
    outlier_indices = np.random.choice(df.index, 10, replace=False)
    df.loc[outlier_indices, 'outage_duration_mins'] = np.random.uniform(1440, 2880, 10)
    for idx in outlier_indices:
        start = df.loc[idx, 'outage_start_time']
        duration = df.loc[idx, 'outage_duration_mins']
        df.loc[idx, 'outage_end_time'] = start + timedelta(minutes=duration)
    
    return df

def main():
    """Main data generation function"""
    print("Starting data generation for ConnectUAE...")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    
    # Generate all tables
    subscribers = generate_subscribers()
    usage = generate_usage_records(subscribers)
    billing = generate_billing(subscribers)
    tickets = generate_tickets(subscribers)
    outages = generate_outages()
    
    # Save to CSV
    print("\nSaving data to CSV files...")
    subscribers.to_csv('data/subscribers.csv', index=False)
    usage.to_csv('data/usage_records.csv', index=False)
    billing.to_csv('data/billing.csv', index=False)
    tickets.to_csv('data/tickets.csv', index=False)
    outages.to_csv('data/network_outages.csv', index=False)
    
    print("\n✅ Data generation complete!")
    print(f"\nGenerated files:")
    print(f"  - data/subscribers.csv ({len(subscribers)} rows)")
    print(f"  - data/usage_records.csv ({len(usage)} rows)")
    print(f"  - data/billing.csv ({len(billing)} rows)")
    print(f"  - data/tickets.csv ({len(tickets)} rows)")
    print(f"  - data/network_outages.csv ({len(outages)} rows)")
    
    print("\n📊 Data Quality Issues Injected:")
    print(f"  ✓ Missing values in usage, billing, tickets")
    print(f"  ✓ Duplicate records across all tables")
    print(f"  ✓ Inconsistent labels (plan types, cities, status)")
    print(f"  ✓ Outliers (usage >500GB, bills >5000 AED)")
    print(f"  ✓ Impossible values (negative bills, date conflicts)")

if __name__ == "__main__":
    main()
