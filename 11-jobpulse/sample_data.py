# ──────────────────────────────────────────
# REALISTIC SAMPLE JOB APPLICATION DATA
# Used for demo purposes.
# Replace with your real data in production.
# ──────────────────────────────────────────

import pandas as pd
from datetime import datetime, timedelta
import random

def generate_sample_data() -> pd.DataFrame:
    """
    Generate realistic job application data
    for demo purposes.
    Reflects real job search patterns.
    """
    random.seed(42)

    companies = [
        ("Google", "Large", "Tech"),
        ("Meta", "Large", "Tech"),
        ("Stripe", "Mid", "Fintech"),
        ("Anthropic", "Mid", "AI"),
        ("Notion", "Mid", "SaaS"),
        ("Linear", "Small", "SaaS"),
        ("Vercel", "Small", "DevTools"),
        ("OpenAI", "Mid", "AI"),
        ("Figma", "Mid", "Design"),
        ("Hugging Face", "Mid", "AI"),
        ("Databricks", "Large", "Data"),
        ("Mistral AI", "Small", "AI"),
        ("Cohere", "Small", "AI"),
        ("Scale AI", "Mid", "AI"),
        ("Weights & Biases", "Small", "MLOps"),
        ("AWS", "Large", "Cloud"),
        ("Microsoft", "Large", "Tech"),
        ("Apple", "Large", "Tech"),
        ("Uber", "Large", "Tech"),
        ("Airbnb", "Large", "Tech"),
    ]

    sources = [
        "LinkedIn", "LinkedIn", "LinkedIn",
        "Direct", "Direct",
        "Referral", "Referral", "Referral",
        "AngelList", "Company Website"
    ]

    statuses = [
        "Applied", "Applied", "Applied",
        "Applied", "Applied",
        "Phone Screen",
        "Technical Interview",
        "Final Round",
        "Offer",
        "Rejected", "Rejected",
        "No Response", "No Response",
        "No Response", "No Response"
    ]

    roles = [
        "AI Engineer",
        "ML Engineer",
        "Software Engineer",
        "Full Stack Engineer",
        "Backend Engineer"
    ]

    base_date = datetime.now() - timedelta(
        days=60
    )
    rows = []

    for i in range(35):
        company, size, industry = random.choice(
            companies
        )
        applied_date = base_date + timedelta(
            days=random.randint(0, 55)
        )
        status = random.choice(statuses)
        source = random.choice(sources)

        # Referrals more likely to progress
        if source == "Referral" and \
           random.random() > 0.4:
            status = random.choice([
                "Phone Screen",
                "Technical Interview",
                "Final Round",
                "Offer"
            ])

        # Direct applications less likely
        if source == "Direct" and \
           random.random() > 0.7:
            status = random.choice([
                "No Response",
                "Applied",
                "Rejected"
            ])

        rows.append({
            "company":        company,
            "role":           random.choice(roles),
            "source":         source,
            "status":         status,
            "date_applied":   applied_date.strftime(
                "%Y-%m-%d"
            ),
            "company_size":   size,
            "industry":       industry,
            "notes":          "",
            "salary_range":   random.choice([
                "$120k-$160k",
                "$140k-$180k",
                "$160k-$200k",
                ""
            ])
        })

    return pd.DataFrame(rows)


def get_sample_csv() -> str:
    """Return sample data as CSV string."""
    df = generate_sample_data()
    return df.to_csv(index=False)