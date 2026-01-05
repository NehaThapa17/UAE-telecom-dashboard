"""
Data Cleaning Script for ConnectUAE Dataset
This script addresses all identified data quality issues.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def load_raw_data():
    """Load raw data files"""
    print("Loading raw data files...")
    
    subscribers = pd.read_csv('data/subscribers.csv')
    usage = pd.read_csv('data/usage_records.csv')
    billing = pd.read_csv('data/billing.csv')
    tickets = pd.read_csv('data/tickets.csv')
    outages = pd.read_csv('data/network_outages.csv')
    
    # Convert dates
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

def remove_duplicates(subscribers, usage, billing, tickets, outages):
    """Remove duplicate records based on primary keys"""
    print("\n1. Removing duplicates...")
    
    orig_sub = len(subscribers)
    subscribers = subscribers.drop_duplicates(subset=['subscriber_id'], keep='first')
    print(f"   Subscribers: Removed {orig_sub - len(subscribers)} duplicates")
    
    orig_usage = len(usage)
    usage = usage.drop_duplicates(subset=['usage_id'], keep='first')
    print(f"   Usage: Removed {orig_usage - len(usage)} duplicates")
    
    orig_bill = len(billing)
    billing = billing.drop_duplicates(subset=['bill_id'], keep='first')
    print(f"   Billing: Removed {orig_bill - len(billing)} duplicates")
    
    orig_ticket = len(tickets)
    tickets = tickets.drop_duplicates(subset=['ticket_id'], keep='first')
    print(f"   Tickets: Removed {orig_ticket - len(tickets)} duplicates")
    
    orig_outage = len(outages)
    outages = outages.drop_duplicates(subset=['outage_id'], keep='first')
    print(f"   Outages: Removed {orig_outage - len(outages)} duplicates")
    
    return subscribers, usage, billing, tickets, outages

def standardize_labels(subscribers, usage, billing, tickets, outages):
    """Standardize inconsistent labels"""
    print("\n2. Standardizing labels...")
    
    # Plan types
    plan_type_mapping = {
        'prepaid': 'Prepaid',
        'PREPAID': 'Prepaid',
        'Pre-paid': 'Prepaid',
        'postpaid': 'Postpaid',
        'POSTPAID': 'Postpaid',
        'Post-paid': 'Postpaid'
    }
    subscribers['plan_type'] = subscribers['plan_type'].replace(plan_type_mapping)
    print(f"   Standardized plan types: {subscribers['plan_type'].unique()}")
    
    # Cities
    city_mapping = {
        'AbuDhabi': 'Abu Dhabi',
        'Abu-Dhabi': 'Abu Dhabi',
        'AD': 'Abu Dhabi',
        'dubai': 'Dubai',
        'DUBAI': 'Dubai'
    }
    subscribers['city'] = subscribers['city'].replace(city_mapping)
    print(f"   Standardized cities: {subscribers['city'].unique()}")
    
    # Ticket status
    status_mapping = {
        'resolved': 'Resolved',
        'RESOLVED': 'Resolved',
        'Closed': 'Resolved',
        'open': 'Open',
        'OPEN': 'Open'
    }
    tickets['ticket_status'] = tickets['ticket_status'].replace(status_mapping)
    print(f"   Standardized ticket statuses: {tickets['ticket_status'].unique()}")
    
    return subscribers, usage, billing, tickets, outages

def handle_missing_values(subscribers, usage, billing, tickets, outages):
    """Handle missing values"""
    print("\n3. Handling missing values...")
    
    # Impute missing data_usage_gb with subscriber average
    missing_usage = usage['data_usage_gb'].isna().sum()
    print(f"   Found {missing_usage} missing data_usage_gb values")
    
    for sub_id in usage[usage['data_usage_gb'].isna()]['subscriber_id'].unique():
        sub_avg = usage[
            (usage['subscriber_id'] == sub_id) & 
            (usage['data_usage_gb'].notna())
        ]['data_usage_gb'].mean()
        
        if pd.notna(sub_avg):
            usage.loc[
                (usage['subscriber_id'] == sub_id) & 
                (usage['data_usage_gb'].isna()), 
                'data_usage_gb'
            ] = sub_avg
        else:
            usage.loc[
                (usage['subscriber_id'] == sub_id) & 
                (usage['data_usage_gb'].isna()), 
                'data_usage_gb'
            ] = 0
    
    print(f"   Imputed {missing_usage} missing data_usage_gb values")
    
    # Flag missing payment_date for Paid bills
    missing_payment = billing[
        (billing['payment_status'] == 'Paid') & 
        (billing['payment_date'].isna())
    ].shape[0]
    
    billing['data_quality_flag'] = False
    billing.loc[
        (billing['payment_status'] == 'Paid') & 
        (billing['payment_date'].isna()),
        'data_quality_flag'
    ] = True
    
    print(f"   Flagged {missing_payment} bills with missing payment_date")
    
    # Flag missing resolution_date for Resolved tickets
    missing_resolution = tickets[
        (tickets['ticket_status'] == 'Resolved') & 
        (tickets['resolution_date'].isna())
    ].shape[0]
    
    tickets['data_quality_flag'] = False
    tickets.loc[
        (tickets['ticket_status'] == 'Resolved') & 
        (tickets['resolution_date'].isna()),
        'data_quality_flag'
    ] = True
    
    print(f"   Flagged {missing_resolution} tickets with missing resolution_date")
    
    # Calculate missing outage_duration_mins
    missing_duration = outages['outage_duration_mins'].isna().sum()
    outages.loc[
        outages['outage_duration_mins'].isna(),
        'outage_duration_mins'
    ] = (
        outages['outage_end_time'] - outages['outage_start_time']
    ).dt.total_seconds() / 60
    
    print(f"   Calculated {missing_duration} missing outage durations")
    
    return subscribers, usage, billing, tickets, outages

def handle_outliers(subscribers, usage, billing, tickets, outages):
    """Handle outlier values"""
    print("\n4. Handling outliers...")
    
    # Cap extreme data usage at 100 GB, flag for review
    extreme_usage = (usage['data_usage_gb'] > 100).sum()
    usage['outlier_flag'] = usage['data_usage_gb'] > 100
    usage.loc[usage['data_usage_gb'] > 100, 'data_usage_gb'] = 100
    print(f"   Capped {extreme_usage} extreme data usage values at 100 GB")
    
    # Flag extreme bills for review
    extreme_bills = (billing['bill_amount'] > 2000).sum()
    billing.loc[billing['bill_amount'] > 2000, 'data_quality_flag'] = True
    print(f"   Flagged {extreme_bills} bills exceeding AED 2,000 for review")
    
    # Flag extreme outages
    extreme_outages = (outages['outage_duration_mins'] > 1440).sum()
    outages['outlier_flag'] = outages['outage_duration_mins'] > 1440
    print(f"   Flagged {extreme_outages} outages exceeding 24 hours")
    
    return subscribers, usage, billing, tickets, outages

def fix_impossible_values(subscribers, usage, billing, tickets, outages):
    """Fix impossible values and date conflicts"""
    print("\n5. Fixing impossible values...")
    
    # Remove negative bill amounts
    negative_bills = (billing['bill_amount'] < 0).sum()
    billing = billing[billing['bill_amount'] >= 0]
    print(f"   Removed {negative_bills} bills with negative amounts")
    
    # Fix impossible ticket dates (resolution before creation)
    impossible_tickets = (
        tickets['resolution_date'] < tickets['ticket_date']
    ).sum()
    
    tickets.loc[
        tickets['resolution_date'] < tickets['ticket_date'],
        'resolution_date'
    ] = pd.NaT
    tickets.loc[
        tickets['resolution_date'].isna() & 
        (tickets['ticket_status'] == 'Resolved'),
        'ticket_status'
    ] = 'In Progress'
    
    print(f"   Fixed {impossible_tickets} tickets with impossible resolution dates")
    
    # Remove usage records before activation
    usage_merged = usage.merge(
        subscribers[['subscriber_id', 'activation_date']], 
        on='subscriber_id'
    )
    impossible_usage = (
        usage_merged['usage_date'] < usage_merged['activation_date']
    ).sum()
    
    valid_usage_ids = usage_merged[
        usage_merged['usage_date'] >= usage_merged['activation_date']
    ]['usage_id']
    usage = usage[usage['usage_id'].isin(valid_usage_ids)]
    
    print(f"   Removed {impossible_usage} usage records before activation")
    
    return subscribers, usage, billing, tickets, outages

def generate_summary_report(subscribers, usage, billing, tickets, outages):
    """Generate data quality summary report"""
    print("\n" + "="*60)
    print("DATA CLEANING SUMMARY REPORT")
    print("="*60)
    
    print(f"\n📊 Final Record Counts:")
    print(f"   Subscribers: {len(subscribers):,}")
    print(f"   Usage Records: {len(usage):,}")
    print(f"   Billing Records: {len(billing):,}")
    print(f"   Tickets: {len(tickets):,}")
    print(f"   Network Outages: {len(outages):,}")
    
    print(f"\n🚨 Remaining Data Quality Flags:")
    print(f"   Billing records flagged: {billing['data_quality_flag'].sum()}")
    print(f"   Tickets flagged: {tickets['data_quality_flag'].sum()}")
    print(f"   Usage outliers: {usage['outlier_flag'].sum()}")
    print(f"   Outage outliers: {outages['outlier_flag'].sum()}")
    
    print(f"\n✅ Data Quality Improvements:")
    print(f"   ✓ Duplicates removed")
    print(f"   ✓ Labels standardized")
    print(f"   ✓ Missing values handled")
    print(f"   ✓ Outliers capped/flagged")
    print(f"   ✓ Impossible values fixed")
    
    print("\n" + "="*60)

def save_cleaned_data(subscribers, usage, billing, tickets, outages):
    """Save cleaned data to new CSV files"""
    print("\n6. Saving cleaned data...")
    
    # Create cleaned data directory
    Path("data_cleaned").mkdir(exist_ok=True)
    
    subscribers.to_csv('data_cleaned/subscribers_clean.csv', index=False)
    usage.to_csv('data_cleaned/usage_records_clean.csv', index=False)
    billing.to_csv('data_cleaned/billing_clean.csv', index=False)
    tickets.to_csv('data_cleaned/tickets_clean.csv', index=False)
    outages.to_csv('data_cleaned/network_outages_clean.csv', index=False)
    
    print("   ✓ Saved to data_cleaned/ directory")

def main():
    """Main cleaning pipeline"""
    print("="*60)
    print("ConnectUAE Data Cleaning Pipeline")
    print("="*60)
    
    # Load data
    subscribers, usage, billing, tickets, outages = load_raw_data()
    
    # Apply cleaning steps
    subscribers, usage, billing, tickets, outages = remove_duplicates(
        subscribers, usage, billing, tickets, outages
    )
    
    subscribers, usage, billing, tickets, outages = standardize_labels(
        subscribers, usage, billing, tickets, outages
    )
    
    subscribers, usage, billing, tickets, outages = handle_missing_values(
        subscribers, usage, billing, tickets, outages
    )
    
    subscribers, usage, billing, tickets, outages = handle_outliers(
        subscribers, usage, billing, tickets, outages
    )
    
    subscribers, usage, billing, tickets, outages = fix_impossible_values(
        subscribers, usage, billing, tickets, outages
    )
    
    # Save cleaned data
    save_cleaned_data(subscribers, usage, billing, tickets, outages)
    
    # Generate summary
    generate_summary_report(subscribers, usage, billing, tickets, outages)
    
    print("\n✅ Data cleaning complete!")
    print("📁 Cleaned files available in data_cleaned/ directory")

if __name__ == "__main__":
    main()
