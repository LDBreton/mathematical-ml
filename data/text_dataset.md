# Support tickets for lecture 05

`support_tickets.csv` is a deterministic, entirely synthetic teaching fixture. It contains 480 authored ticket variants: 96 tickets in each of five equally sized categories and 60 independently written template groups. Each group has eight related variants. No real messages, people, organizations, or customer records were used.

| Column | Meaning |
|---|---|
| `ticket_id` | Stable row identifier (`T-0001` through `T-0480`). |
| `category` | Intended support queue: `account_access`, `billing`, `order_status`, `refund_return`, or `technical_issue`. |
| `template_group` | ID of the independently authored template family used to make the row. All eight related variants in a family share this ID. Use it as a group when splitting so close siblings cannot occur across train, validation, and test. |
| `text` | A short synthetic customer-style support request. Names and reference codes use fictional or reserved examples. |

The dataset is balanced by construction. It has 12 groups per category and eight rows per group. The lesson assigns eight groups per category to training, two to validation, and two to test, giving 320, 80, and 80 rows respectively, with every split containing 64, 16, and 16 rows from each category. The split is reproducible and keeps every template group intact.

Regenerate from the repository root with:

```powershell
.venv\Scripts\python.exe scripts\generate_text_data.py
```

This is an authored template exercise, not a real-language benchmark. Repeated structures and a small vocabulary make it useful for TF-IDF, sparse linear models, macro-F1, and leakage demonstrations. Scores do not estimate performance on real customer tickets, changing language, imbalanced queues, or operational costs. The fixture cannot support claims about deployment readiness or customer outcomes.
