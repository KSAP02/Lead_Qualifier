import csv
from faker import Faker
import random
from datetime import datetime, timedelta, timezone

fake = Faker()
industries = ["Technology", "Manufacturing", "Healthcare", "Finance"]
sources = ["Organic", "PPC", "Referral", "Email"]

path= r"D:\Projects\AI Apps\Agents\LeadQualifier\data\leads.csv"

with open(path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id","name","company","industry","size","source","created_at"])
    for i in range(1, 51):
        created = datetime.now(timezone.utc) - timedelta(days=random.randint(0,30))
        writer.writerow([
            i,
            fake.name(),
            fake.company(),
            random.choice(industries),
            random.randint(5, 500),
            random.choice(sources),
            created.isoformat() + "Z"
        ])
