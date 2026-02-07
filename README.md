# Automotive Inventory & Slow-Mover Analyzer

A Python/Pandas tool that analyzes automotive parts inventory across 6 South African branches — identifying slow-moving stock, calculating reorder points, and generating a 4-page visual PDF report.

---

## Features

### Demand Classification
Every SKU-branch combination is classified based on average monthly sales:
- **High Demand** — 30 or more units/month
- **Stable** — 8 to 29 units/month
- **Slow-Moving** — fewer than 8 units/month

### Reorder Point Calculator
Uses a standard inventory management formula to flag items needing purchase orders:

```
Reorder Point = (Daily Sales Rate x Lead Time Days) + Safety Stock

Where:
  Daily Sales Rate = Avg Monthly Sales / 30
  Safety Stock     = Daily Sales Rate x 7 days
```

### Console Output
- KPI summary (total SKUs, stock value, slow-movers, reorder alerts)
- Demand classification breakdown table
- Top 15 most urgent reorder alerts
- Branch performance comparison across 6 SA branches
- Dead stock analysis by category

### PDF Report (4 pages)

| Page | Contents |
|------|----------|
| 1 | KPI cards, demand pie chart, category stacked bar chart |
| 2 | 12-month sales trend (area chart), velocity vs days-of-stock scatter plot |
| 3 | Reorder formula display, top 15 urgent items, dead stock value by category |
| 4 | Branch comparison — sales volume, stock value, slow-movers, reorder alerts |

### CSV Export
Full analysed dataset with 21+ calculated columns, ready for Power BI or Tableau import.

---

## Dataset

Mock dataset of 40 realistic automotive SKUs across 6 branches, totalling 240 records.

Parts include spark plugs, brake pads, alternators, clutch kits, A/C compressors, and more — with realistic pricing in South African Rand. Each record includes 12 months of sales data with built-in seasonality and noise.

---

## Getting Started

### Prerequisites
- Python 3.10 or later

### Installation

```bash
git clone https://github.com/MondeNT/automotive-inventory-analyzer.git
cd automotive-inventory-analyzer

pip install -r requirements.txt

python inventory_analyzer.py
```

### Output
After running, two files are generated in the project folder:
- `inventory_report.pdf` — 4-page visual dashboard
- `inventory_dataset.csv` — full analysed dataset (240 rows, 21+ columns)

---

## PDF Output
<img width="1245" height="776" alt="Image" src="https://github.com/user-attachments/assets/7b364867-c08c-44f2-8db4-a6f4bd400b29" />
<img width="1245" height="776" alt="Image" src="https://github.com/user-attachments/assets/777dfca5-4f73-4560-be32-7f764226568b" />
<img width="1245" height="776" alt="Image" src="https://github.com/user-attachments/assets/6ad8c14f-1047-4c12-8fec-edf2805c7cc7" />
<img width="1245" height="776" alt="Image" src="https://github.com/user-attachments/assets/d64a26ca-91de-4925-8a99-ada5906ad9b6" />
## Project Structure

```
automotive-inventory-analyzer/
├── inventory_analyzer.py   # Main script (data generation, analysis, PDF report)
├── requirements.txt        # Python dependencies
├── .gitignore              # Ignores generated outputs and cache files
└── README.md
```

---

## Key Formulas

### Reorder Point (ROP)
```
ROP = Lead Time Demand + Safety Stock
    = (Avg Monthly Sales / 30 x Lead Time Days) + (Avg Monthly Sales / 30 x 7)
```

### Days of Stock
```
Days of Stock = Current Stock / Daily Sales Rate
```

### Inventory Turnover
```
Turnover = (12-Month Units Sold x Unit Cost) / Current Stock Value
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Pandas | Data manipulation and analysis |
| NumPy | Numerical calculations |
| Matplotlib | PDF chart generation |
| Seaborn | Statistical visualization support |

---

## Sample Console Output

```
======================================================================
  AUTOMOTIVE INVENTORY & SLOW-MOVER ANALYZER — KPI SUMMARY
======================================================================
  Total SKU-Branch Records :      240
  Total Stock Value (ZAR)  : R   12,396,268
  Slow-Moving Items        :       72  (R 720,340 at risk)
  Items Needing Reorder    :       58
  Avg Inventory Turnover   :     12.9x  (12-month)
======================================================================
```

---

## License

MIT — free to use, modify, and distribute.
