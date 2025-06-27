
def parse_transactions(text):
    import re
    from datetime import datetime

    lines = text.strip().split("\n")
    transactions = []

    # Pattern: MM/DD   Card Purchase   MM/DD Description   Amount
    pattern = re.compile(r"^(\d{2}/\d{2})\s+(.*?)\s{2,}(\d{2}/\d{2})\s+(.*?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$")

    for line in lines:
        match = pattern.match(line)
        if match:
            try:
                date_str = match.group(1)
                date = datetime.strptime(date_str, "%m/%d")
                date = date.replace(year=datetime.now().year)
                description = match.group(4)
                amount = float(match.group(5).replace(",", ""))
                transactions.append({
                    "Date": date,
                    "Description": description,
                    "Amount": amount,
                    "Category": "Uncategorized"
                })
            except Exception as e:
                continue
    return pd.DataFrame(transactions)
