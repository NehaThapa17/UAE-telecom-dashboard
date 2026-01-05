# ConnectUAE - Telecom Revenue & Service Operations Dashboard

A comprehensive Streamlit dashboard for analyzing telecommunications revenue, subscriber health, and service operations with realistic UAE market data.

## 📋 Project Overview

This project simulates a telecommunications provider "ConnectUAE" serving 5,000+ subscribers across UAE cities (Dubai, Abu Dhabi, Sharjah, Ajman, Fujairah). The dashboard provides:

- **Executive View**: Revenue trends, ARPU analysis, subscriber retention, billing insights
- **Operations View**: Ticket management, SLA compliance, network outages, service quality metrics
- **Data Quality Report**: Identifies missing values, duplicates, inconsistent labels, and outliers
- **Raw Data Explorer**: Browse and download all datasets

## 🗂️ Project Structure

```
connectuae-dashboard/
│
├── app.py                      # Main Streamlit application
├── generate_data.py            # Data generation script with quality issues
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── data/                       # Generated CSV files (created by generate_data.py)
│   ├── subscribers.csv
│   ├── usage_records.csv
│   ├── billing.csv
│   ├── tickets.csv
│   └── network_outages.csv
│
└── .gitignore                  # Git ignore file
```

## 📊 Dataset Details

### Tables & Row Counts

| Table | Row Count | Description |
|-------|-----------|-------------|
| **subscribers.csv** | 5,000+ | Subscriber profiles with plan details |
| **usage_records.csv** | 50,000 | Daily usage data (calls, data, SMS) |
| **billing.csv** | 15,000 | Monthly billing records |
| **tickets.csv** | 6,000+ | Support tickets across channels |
| **network_outages.csv** | 200+ | Network incident logs |

### Intentional Data Quality Issues

The dataset includes realistic data quality problems for analysis practice:

1. **Missing Values (3-5%)**
   - ~500 usage records with missing `data_usage_gb`
   - ~200 billing records with missing `payment_date` for "Paid" status
   - ~100 tickets with missing `resolution_date` for "Resolved" status
   - ~10 outages with missing `outage_duration_mins`

2. **Duplicate Records**
   - 80 duplicate subscribers
   - 60 duplicate tickets
   - 40 duplicate bills

3. **Inconsistent Labels**
   - Plan types: "Prepaid", "PREPAID", "prepaid", "Pre-paid"
   - Cities: "Abu Dhabi", "AbuDhabi", "Abu-Dhabi", "AD"
   - Status: "Resolved", "resolved", "RESOLVED", "Closed"

4. **Outliers**
   - 30 usage records with >500 GB data usage
   - 20 bills exceeding AED 5,000
   - 10 outages lasting >24 hours

5. **Impossible Values**
   - 15 tickets where `resolution_date < ticket_date`
   - 10 usage records before subscriber `activation_date`
   - 5 bills with negative amounts

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/connectuae-dashboard.git
cd connectuae-dashboard
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Generate Data
```bash
python generate_data.py
```

This will create a `data/` folder with all CSV files (~120MB total).

### Step 5: Run the Dashboard
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📈 Key Features

### Executive View
- **KPI Cards**: Total Revenue, ARPU, Active Subscribers, Revenue at Risk
- **ARPU Trend**: Monthly average revenue per user tracking
- **Revenue Distribution**: By plan type (Prepaid/Postpaid)
- **City Performance**: Revenue and overdue payments by city
- **Subscriber Status**: Active, Suspended, Churned distribution
- **Payment Analysis**: Payment status breakdown

### Operations View
- **Operational KPIs**: Open tickets, avg resolution time, SLA compliance, total outage minutes
- **Ticket Analytics**: Top categories, volume by channel and city
- **Resolution Metrics**: Average time by category
- **Network Stability**: Outage incidents by city and type
- **SLA Monitoring**: Compliance rates by support channel

### Data Quality Report
- Missing value counts across all tables
- Duplicate record identification
- Label inconsistency detection
- Outlier and impossible value highlighting

## 🔧 Data Cleaning Recommendations

Based on identified issues, recommended cleaning steps:

1. **Remove duplicates** using primary keys (`subscriber_id`, `ticket_id`, `bill_id`)
2. **Standardize labels**: Convert all plan types, cities, and statuses to title case
3. **Impute missing values**:
   - Use subscriber's average for missing `data_usage_gb`
   - Flag missing `payment_date` for paid bills
4. **Cap outliers**:
   - Data usage >100 GB → flag for review
   - Bills >AED 2,000 → verify enterprise accounts
5. **Fix date conflicts**:
   - Remove records where `resolution_date < ticket_date`
   - Remove usage before `activation_date`
6. **Calculate missing durations**: Derive from `outage_end_time - outage_start_time`

## 📊 Business Metrics Explained

### Executive Metrics
- **ARPU**: Average Revenue Per User = Total Revenue / Active Subscribers
- **Retention Rate**: (Retained Subscribers / Total Subscribers) × 100
- **Revenue at Risk**: Sum of overdue payment amounts
- **Churn Rate**: (Churned Subscribers / Total Subscribers) × 100

### Operations Metrics
- **SLA Compliance**: % of tickets resolved within 48 hours
- **Avg Resolution Time**: Mean hours from ticket creation to resolution
- **Ticket Backlog**: Count of Open + In Progress tickets
- **Outage Impact**: Total downtime minutes across all zones

## 🌐 Deployment to GitHub

### Initial Setup
```bash
# Initialize git repository
git init

# Create .gitignore file
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".DS_Store" >> .gitignore

# Add files
git add .
git commit -m "Initial commit: ConnectUAE dashboard"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/connectuae-dashboard.git
git branch -M main
git push -u origin main
```

### Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select repository: `yourusername/connectuae-dashboard`
4. Set main file path: `app.py`
5. Click "Deploy"

**Important**: Run `python generate_data.py` locally first and commit the `data/` folder to GitHub, or set up the script to run automatically on Streamlit Cloud.

## 📝 Usage Examples

### Answering Executive Questions

**Q: What is our ARPU trend and which plan drives most revenue?**
- Navigate to Executive View
- Check ARPU Trend chart (line graph)
- Review Revenue Distribution pie chart

**Q: Which city has highest overdue payments?**
- Executive View → "Overdue Payments by City" bar chart
- Typically Dubai shows highest absolute amount due to subscriber concentration

**Q: What's our retention rate?**
- Executive View → "Subscriber Retention" chart
- Current rate displayed prominently below the graph

### Answering Operations Questions

**Q: What's the ticket backlog and which zones are worst?**
- Operations View → "Open Tickets" KPI card
- "Ticket Volume by City" chart shows distribution

**Q: Which support channel underperforms on SLA?**
- Operations View → "SLA Compliance by Channel" chart
- Identifies channels below 48-hour target

**Q: Is there correlation between outages and tickets?**
- Cross-reference "Network Outage Incidents by City" with "Ticket Volume by City"
- Check "Network Issue" category in ticket analytics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

Your Name - [your.email@example.com](mailto:your.email@example.com)

## 🙏 Acknowledgments

- Based on realistic UAE telecommunications market data
- Built with Streamlit, Pandas, and Plotly
- Designed for data analysis and business intelligence education

---

**Note**: This is a synthetic dataset created for educational purposes. All data is randomly generated and does not represent any real telecommunications company.
