"""
═══════════════════════════════════════════════════════════════════════════════
  AUTOMOTIVE INVENTORY & SLOW-MOVER ANALYZER
  ─────────────────────────────────────────────
  A comprehensive Python/Pandas dashboard that analyzes a mock dataset of
  automotive parts across 6 South African branches.

  Features:
    • Demand classification: High Demand / Stable / Slow-Moving
    • Reorder Point calculator with safety stock & lead time
    • Dead stock identification & capital-at-risk analysis
    • Branch-level performance comparison
    • Full visual report exported as PDF

  Tech: Python · Pandas · Matplotlib · Seaborn
═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
BRANCHES = ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Bloemfontein", "Port Elizabeth"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

COLORS = {
    "High Demand": "#10b981",
    "Stable":      "#3b82f6",
    "Slow-Moving": "#ef4444",
}
BG_DARK   = "#0a0c10"
BG_CARD   = "#111318"
BG_GRID   = "#1e2330"
TEXT_DIM   = "#6b7280"
TEXT_LIGHT = "#e2e8f0"
ACCENT_ORANGE = "#f97316"
ACCENT_YELLOW = "#f59e0b"

plt.rcParams.update({
    "figure.facecolor": BG_DARK,
    "axes.facecolor":   BG_CARD,
    "axes.edgecolor":   BG_GRID,
    "axes.labelcolor":  TEXT_DIM,
    "text.color":       TEXT_LIGHT,
    "xtick.color":      TEXT_DIM,
    "ytick.color":      TEXT_DIM,
    "grid.color":       BG_GRID,
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
    "font.size":        10,
    "legend.facecolor": BG_CARD,
    "legend.edgecolor": BG_GRID,
    "legend.fontsize":  8,
})


# ═══════════════════════════════════════════════════════════════
# 1. GENERATE MOCK DATASET
# ═══════════════════════════════════════════════════════════════

def generate_dataset() -> pd.DataFrame:
    """Generate a realistic mock dataset of 40 automotive SKUs across 6 branches."""

    parts = [
        ("SP-1001", "Spark Plug – Iridium",      "Engine",       89.99),
        ("SP-1002", "Spark Plug – Copper",        "Engine",       42.50),
        ("BP-2001", "Brake Pad Set – Front",      "Brakes",      385.00),
        ("BP-2002", "Brake Pad Set – Rear",       "Brakes",      340.00),
        ("BP-2003", "Brake Disc – Ventilated",    "Brakes",      720.00),
        ("BP-2004", "Brake Fluid DOT 4",          "Brakes",       95.00),
        ("EL-3001", "Alternator 12V 120A",        "Electrical",  2450.00),
        ("EL-3002", "Battery 60Ah",               "Electrical",  1350.00),
        ("EL-3003", "Starter Motor",              "Electrical",  1890.00),
        ("EL-3004", "Ignition Coil Pack",         "Electrical",   560.00),
        ("SU-4001", "Shock Absorber – Front",     "Suspension",   890.00),
        ("SU-4002", "Shock Absorber – Rear",      "Suspension",   780.00),
        ("SU-4003", "Control Arm – Lower",        "Suspension",  1120.00),
        ("SU-4004", "Tie Rod End",                "Suspension",   320.00),
        ("FI-5001", "Oil Filter",                 "Filters",       65.00),
        ("FI-5002", "Air Filter",                 "Filters",      110.00),
        ("FI-5003", "Fuel Filter",                "Filters",      185.00),
        ("FI-5004", "Cabin Filter",               "Filters",      145.00),
        ("FI-5005", "Transmission Filter Kit",    "Filters",      290.00),
        ("TR-6001", "Clutch Kit Complete",        "Transmission", 3200.00),
        ("TR-6002", "CV Joint – Outer",           "Transmission",  680.00),
        ("TR-6003", "Flywheel – Dual Mass",       "Transmission", 4500.00),
        ("TR-6004", "Gearbox Mount",              "Transmission",  450.00),
        ("EN-1003", "Timing Belt Kit",            "Engine",       1250.00),
        ("EN-1004", "Water Pump",                 "Engine",        680.00),
        ("EN-1005", "Thermostat Housing",         "Engine",        390.00),
        ("EN-1006", "Valve Cover Gasket",         "Engine",        220.00),
        ("EN-1007", "Engine Mount",               "Engine",        560.00),
        ("BD-7001", "Side Mirror – Electric",     "Body",          890.00),
        ("BD-7002", "Headlight Assembly – LED",   "Body",         2800.00),
        ("BD-7003", "Tail Light Assembly",        "Body",         1200.00),
        ("BD-7004", "Wiper Blade Set",            "Body",          165.00),
        ("BD-7005", "Door Handle – Exterior",     "Body",          340.00),
        ("CL-8001", "Radiator – Aluminium",       "Cooling",      1850.00),
        ("CL-8002", "Radiator Fan Motor",         "Cooling",      1100.00),
        ("CL-8003", "Coolant Hose Kit",           "Cooling",       280.00),
        ("CL-8004", "Expansion Tank",             "Cooling",       420.00),
        ("CL-8005", "A/C Compressor",             "Cooling",      3800.00),
        ("EN-1008", "Piston Ring Set",            "Engine",        750.00),
        ("SU-4005", "Stabiliser Link",            "Suspension",    210.00),
    ]

    rng = np.random.default_rng(42)
    rows = []

    for pi, (sku, name, category, cost) in enumerate(parts):
        for bi, branch in enumerate(BRANCHES):
            # Deterministic demand profile
            seed_val = (pi * 7 + bi * 13) % 10
            if seed_val < 3:
                profile = "high"
                avg_monthly = int(rng.integers(40, 120))
            elif seed_val < 7:
                profile = "stable"
                avg_monthly = int(rng.integers(10, 30))
            else:
                profile = "low"
                avg_monthly = int(rng.integers(0, 8))

            # 12-month sales with seasonality + noise
            monthly_sales = []
            for m in range(12):
                seasonal = 1 + 0.2 * np.sin((m / 12) * np.pi * 2)
                noise = 0.7 + rng.random() * 0.6
                monthly_sales.append(max(0, int(avg_monthly * seasonal * noise)))

            total_12m = sum(monthly_sales)
            current_stock = int(rng.integers(2, avg_monthly * 4 + 5))
            lead_time_days = int(rng.integers(7, 28))

            rows.append({
                "sku": sku,
                "part_name": name,
                "category": category,
                "branch": branch,
                "unit_cost_zar": cost,
                "avg_monthly_sales": avg_monthly,
                "total_sold_12m": total_12m,
                "current_stock": current_stock,
                "lead_time_days": lead_time_days,
                "safety_stock_days": 7,
                **{f"sales_{MONTHS[m].lower()}": monthly_sales[m] for m in range(12)},
            })

    df = pd.DataFrame(rows)
    return df


# ═══════════════════════════════════════════════════════════════
# 2. CLASSIFICATION & CALCULATIONS
# ═══════════════════════════════════════════════════════════════

def classify_demand(avg_monthly: int) -> str:
    """Classify part demand based on average monthly sales."""
    if avg_monthly >= 30:
        return "High Demand"
    elif avg_monthly >= 8:
        return "Stable"
    else:
        return "Slow-Moving"


def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add all derived analytics columns."""
    df = df.copy()

    # Demand classification
    df["demand_class"] = df["avg_monthly_sales"].apply(classify_demand)

    # Daily sales rate
    df["daily_sales_rate"] = df["avg_monthly_sales"] / 30

    # Safety stock (units)
    df["safety_stock_units"] = np.ceil(df["daily_sales_rate"] * df["safety_stock_days"]).astype(int)

    # Lead time demand
    df["lead_time_demand"] = np.ceil(df["daily_sales_rate"] * df["lead_time_days"]).astype(int)

    # ──────────────────────────────────────────
    # REORDER POINT FORMULA:
    #   ROP = (Daily Sales Rate × Lead Time) + Safety Stock
    # ──────────────────────────────────────────
    df["reorder_point"] = df["lead_time_demand"] + df["safety_stock_units"]

    # Days of stock remaining
    df["days_of_stock"] = np.where(
        df["daily_sales_rate"] > 0,
        np.round(df["current_stock"] / df["daily_sales_rate"]),
        9999
    ).astype(int)

    # Reorder flag
    df["needs_reorder"] = df["current_stock"] <= df["reorder_point"]

    # Stock value
    df["stock_value_zar"] = df["current_stock"] * df["unit_cost_zar"]

    # Suggested order quantity (cover 1 month + shortfall)
    df["shortfall"] = np.maximum(0, df["reorder_point"] - df["current_stock"])
    df["suggested_order"] = np.maximum(df["shortfall"], df["avg_monthly_sales"])

    # Inventory turnover (12-month)
    df["turnover_ratio"] = np.where(
        df["stock_value_zar"] > 0,
        (df["total_sold_12m"] * df["unit_cost_zar"]) / df["stock_value_zar"],
        0
    ).round(1)

    return df


# ═══════════════════════════════════════════════════════════════
# 3. ANALYSIS SUMMARIES
# ═══════════════════════════════════════════════════════════════

def print_kpi_summary(df: pd.DataFrame):
    """Print high-level KPIs to console."""
    total_skus = len(df)
    total_stock_value = df["stock_value_zar"].sum()
    slow = df[df["demand_class"] == "Slow-Moving"]
    slow_count = len(slow)
    dead_stock_value = slow["stock_value_zar"].sum()
    reorder_count = df["needs_reorder"].sum()
    avg_turnover = df["turnover_ratio"].mean()

    print("\n" + "═" * 70)
    print("  AUTOMOTIVE INVENTORY & SLOW-MOVER ANALYZER — KPI SUMMARY")
    print("═" * 70)
    print(f"  Total SKU-Branch Records : {total_skus:>8,}")
    print(f"  Total Stock Value (ZAR)  : R {total_stock_value:>12,.0f}")
    print(f"  Slow-Moving Items        : {slow_count:>8,}  (R {dead_stock_value:,.0f} at risk)")
    print(f"  Items Needing Reorder    : {int(reorder_count):>8,}")
    print(f"  Avg Inventory Turnover   : {avg_turnover:>8.1f}x  (12-month)")
    print("═" * 70)


def print_demand_breakdown(df: pd.DataFrame):
    """Print demand classification breakdown."""
    print("\n┌─────────────────────────────────────────────────────┐")
    print("│  DEMAND CLASSIFICATION BREAKDOWN                    │")
    print("├──────────────┬──────────┬────────────┬──────────────┤")
    print("│ Category     │  Count   │  % of Total│  Stock Value │")
    print("├──────────────┼──────────┼────────────┼──────────────┤")
    for cls in ["High Demand", "Stable", "Slow-Moving"]:
        subset = df[df["demand_class"] == cls]
        pct = len(subset) / len(df) * 100
        val = subset["stock_value_zar"].sum()
        print(f"│ {cls:<12} │ {len(subset):>6}   │ {pct:>8.1f}%  │ R {val:>10,.0f} │")
    print("└──────────────┴──────────┴────────────┴──────────────┘")


def print_reorder_alerts(df: pd.DataFrame, top_n: int = 20):
    """Print items needing reorder, sorted by urgency."""
    reorder_df = df[df["needs_reorder"]].sort_values("days_of_stock").head(top_n)

    print(f"\n⚠  TOP {top_n} REORDER ALERTS (sorted by days of stock remaining)")
    print("─" * 110)
    print(f"{'SKU':<10} {'Part Name':<28} {'Branch':<14} {'Stock':>6} {'ROP':>5} {'Short':>6} "
          f"{'Lead':>5} {'Daily':>6} {'Safety':>6} {'Order':>7}")
    print("─" * 110)

    for _, row in reorder_df.iterrows():
        print(f"{row['sku']:<10} {row['part_name'][:27]:<28} {row['branch']:<14} "
              f"{row['current_stock']:>6} {row['reorder_point']:>5} "
              f"{'-' + str(row['shortfall']):>6} {str(row['lead_time_days']) + 'd':>5} "
              f"{row['daily_sales_rate']:>5.1f}/d {row['safety_stock_units']:>6} "
              f"{row['suggested_order']:>5} units")
    print("─" * 110)


def print_branch_comparison(df: pd.DataFrame):
    """Print branch-level comparison."""
    branch_stats = df.groupby("branch").agg(
        total_sales=("total_sold_12m", "sum"),
        stock_value=("stock_value_zar", "sum"),
        slow_movers=("demand_class", lambda x: (x == "Slow-Moving").sum()),
        reorder_alerts=("needs_reorder", "sum"),
        avg_turnover=("turnover_ratio", "mean"),
    ).sort_values("total_sales", ascending=False)

    print("\n┌────────────────────────────────────────────────────────────────────────┐")
    print("│  BRANCH PERFORMANCE COMPARISON                                         │")
    print("├────────────────┬───────────┬──────────────┬────────┬─────────┬──────────┤")
    print("│ Branch         │ 12M Sales │ Stock Value  │ Slow   │ Reorder │ Turnover │")
    print("├────────────────┼───────────┼──────────────┼────────┼─────────┼──────────┤")
    for branch, row in branch_stats.iterrows():
        print(f"│ {branch:<14} │ {int(row['total_sales']):>9,} │ R {row['stock_value']:>10,.0f} │ "
              f"{int(row['slow_movers']):>5}  │ {int(row['reorder_alerts']):>6}  │ {row['avg_turnover']:>6.1f}x  │")
    print("└────────────────┴───────────┴──────────────┴────────┴─────────┴──────────┘")


def print_dead_stock_by_category(df: pd.DataFrame):
    """Print slow-moving stock analysis by category."""
    slow = df[df["demand_class"] == "Slow-Moving"]
    cat_stats = slow.groupby("category").agg(
        count=("sku", "count"),
        total_value=("stock_value_zar", "sum"),
        avg_days=("days_of_stock", lambda x: x[x < 9999].mean() if (x < 9999).any() else float("inf")),
    ).sort_values("total_value", ascending=False)

    print("\n💀  DEAD STOCK ANALYSIS — Slow-Movers by Category")
    print("─" * 60)
    print(f"{'Category':<16} {'Count':>6} {'Total Value':>14} {'Avg Days Left':>14}")
    print("─" * 60)
    for cat, row in cat_stats.iterrows():
        days_str = f"{row['avg_days']:.0f}d" if row["avg_days"] < 9999 else "∞"
        print(f"{cat:<16} {int(row['count']):>6} R {row['total_value']:>12,.0f} {days_str:>14}")
    print("─" * 60)
    print(f"{'TOTAL':<16} {len(slow):>6} R {slow['stock_value_zar'].sum():>12,.0f}")


# ═══════════════════════════════════════════════════════════════
# 4. MATPLOTLIB VISUALIZATIONS → PDF
# ═══════════════════════════════════════════════════════════════

def zar_fmt(x, _): return f"R{x/1000:.0f}k" if x >= 1000 else f"R{x:.0f}"

def create_pdf_report(df: pd.DataFrame, output_path: str):
    """Generate a multi-page PDF report with all visualizations."""

    month_cols = [f"sales_{m.lower()}" for m in MONTHS]

    with PdfPages(output_path) as pdf:

        # ──────────────── PAGE 1: TITLE + KPIs + PIE ────────────────
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle("AUTOMOTIVE INVENTORY & SLOW-MOVER ANALYZER",
                      fontsize=20, fontweight="bold", color=TEXT_LIGHT, y=0.97)
        fig.text(0.5, 0.935,
                 f"40 SKUs · 6 Branches · {len(df)} Records · Mock Dataset",
                 ha="center", fontsize=11, color=TEXT_DIM)

        # KPI bar across the top
        kpi_data = [
            ("Total SKUs", f"{len(df):,}", COLORS["Stable"]),
            ("Stock Value", f"R {df['stock_value_zar'].sum():,.0f}", "#10b981"),
            ("Slow-Movers", f"{(df['demand_class'] == 'Slow-Moving').sum()}", COLORS["Slow-Moving"]),
            ("Need Reorder", f"{int(df['needs_reorder'].sum())}", ACCENT_YELLOW),
            ("Avg Turnover", f"{df['turnover_ratio'].mean():.1f}x", "#8b5cf6"),
        ]
        for i, (label, value, color) in enumerate(kpi_data):
            ax_kpi = fig.add_axes([0.04 + i * 0.19, 0.81, 0.17, 0.08])
            ax_kpi.set_xlim(0, 1); ax_kpi.set_ylim(0, 1)
            ax_kpi.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor=BG_CARD,
                             edgecolor=BG_GRID, linewidth=1, transform=ax_kpi.transAxes))
            ax_kpi.text(0.5, 0.65, value, ha="center", va="center",
                        fontsize=16, fontweight="bold", color=color)
            ax_kpi.text(0.5, 0.22, label.upper(), ha="center", va="center",
                        fontsize=8, color=TEXT_DIM, fontweight="bold")
            ax_kpi.axis("off")

        # Pie chart — demand classification
        ax_pie = fig.add_axes([0.03, 0.08, 0.38, 0.68])
        demand_counts = df["demand_class"].value_counts().reindex(["High Demand", "Stable", "Slow-Moving"])
        wedges, texts, autotexts = ax_pie.pie(
            demand_counts.values,
            labels=demand_counts.index,
            colors=[COLORS[c] for c in demand_counts.index],
            autopct=lambda p: f"{p:.0f}%\n({int(p * len(df) / 100)})",
            pctdistance=0.72,
            wedgeprops=dict(width=0.45, edgecolor=BG_DARK, linewidth=2),
            textprops=dict(color=TEXT_LIGHT, fontsize=10),
            startangle=90,
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_color(TEXT_LIGHT)
        ax_pie.set_title("Demand Classification", fontsize=13, fontweight="bold",
                          color=TEXT_LIGHT, pad=12)

        # Stacked bar — category breakdown
        ax_cat = fig.add_axes([0.50, 0.08, 0.46, 0.68])
        cat_demand = df.groupby(["category", "demand_class"]).size().unstack(fill_value=0)
        cat_demand = cat_demand.reindex(columns=["High Demand", "Stable", "Slow-Moving"], fill_value=0)
        cat_demand = cat_demand.loc[cat_demand.sum(axis=1).sort_values(ascending=True).index]

        y_pos = np.arange(len(cat_demand))
        left = np.zeros(len(cat_demand))
        for cls in ["High Demand", "Stable", "Slow-Moving"]:
            vals = cat_demand[cls].values
            ax_cat.barh(y_pos, vals, left=left, height=0.6,
                        color=COLORS[cls], edgecolor=BG_DARK, linewidth=0.5, label=cls)
            for i, (v, l) in enumerate(zip(vals, left)):
                if v > 0:
                    ax_cat.text(l + v / 2, i, str(v), ha="center", va="center",
                                fontsize=8, fontweight="bold", color=TEXT_LIGHT)
            left += vals

        ax_cat.set_yticks(y_pos)
        ax_cat.set_yticklabels(cat_demand.index, fontsize=9)
        ax_cat.set_xlabel("Number of SKU-Branch Records", fontsize=9)
        ax_cat.set_title("SKU Count by Category & Demand", fontsize=13,
                          fontweight="bold", color=TEXT_LIGHT, pad=12)
        ax_cat.legend(loc="lower right", fontsize=8, framealpha=0.8)
        ax_cat.grid(axis="x", alpha=0.3)

        pdf.savefig(fig, facecolor=BG_DARK)
        plt.close(fig)

        # ──────────────── PAGE 2: TRENDS + SCATTER ────────────────
        fig, axes = plt.subplots(2, 1, figsize=(16, 10))
        fig.suptitle("SALES TRENDS & VELOCITY ANALYSIS", fontsize=16,
                      fontweight="bold", color=TEXT_LIGHT, y=0.97)
        plt.subplots_adjust(hspace=0.35, top=0.91, bottom=0.08)

        # Area chart — monthly sales by demand class
        ax1 = axes[0]
        for cls in ["High Demand", "Stable", "Slow-Moving"]:
            subset = df[df["demand_class"] == cls]
            monthly_totals = subset[month_cols].sum().values
            ax1.fill_between(range(12), monthly_totals, alpha=0.25, color=COLORS[cls])
            ax1.plot(range(12), monthly_totals, color=COLORS[cls], linewidth=2.5,
                     label=cls, marker="o", markersize=4)

        ax1.set_xticks(range(12))
        ax1.set_xticklabels(MONTHS)
        ax1.set_ylabel("Total Units Sold")
        ax1.set_title("12-Month Sales Trend by Demand Category", fontsize=12,
                       fontweight="bold", color=TEXT_LIGHT, pad=10)
        ax1.legend(loc="upper right")
        ax1.grid(alpha=0.3)

        # Scatter — avg monthly sales vs days of stock
        ax2 = axes[1]
        for cls in ["High Demand", "Stable", "Slow-Moving"]:
            subset = df[df["demand_class"] == cls]
            days = subset["days_of_stock"].clip(upper=400)
            sizes = (subset["stock_value_zar"] / subset["stock_value_zar"].max() * 200).clip(lower=15)
            ax2.scatter(subset["avg_monthly_sales"], days, s=sizes,
                        c=COLORS[cls], alpha=0.55, edgecolors=COLORS[cls],
                        linewidth=0.5, label=cls)

        ax2.set_xlabel("Average Monthly Sales (units)")
        ax2.set_ylabel("Days of Stock Remaining")
        ax2.set_title("Sales Velocity vs Days of Stock  (bubble size = stock value)",
                       fontsize=12, fontweight="bold", color=TEXT_LIGHT, pad=10)
        ax2.axhline(y=30, color=ACCENT_YELLOW, linestyle="--", linewidth=1, alpha=0.6, label="30-day threshold")
        ax2.legend(loc="upper right")
        ax2.grid(alpha=0.3)

        pdf.savefig(fig, facecolor=BG_DARK)
        plt.close(fig)

        # ──────────────── PAGE 3: REORDER ANALYSIS ────────────────
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle("REORDER POINT ANALYSIS", fontsize=16,
                      fontweight="bold", color=TEXT_LIGHT, y=0.97)

        # Formula box
        ax_formula = fig.add_axes([0.05, 0.85, 0.90, 0.07])
        ax_formula.set_xlim(0, 1); ax_formula.set_ylim(0, 1)
        ax_formula.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="#1a1520",
                             edgecolor=ACCENT_YELLOW, linewidth=1.5, transform=ax_formula.transAxes))
        ax_formula.text(0.5, 0.6,
            "Reorder Point  =  (Daily Sales Rate × Lead Time Days)  +  Safety Stock",
            ha="center", va="center", fontsize=13, fontweight="bold", color=ACCENT_YELLOW,
            fontfamily="monospace")
        ax_formula.text(0.5, 0.18,
            "Where:  Daily Rate = Avg Monthly / 30   |   Safety Stock = Daily Rate × 7 days",
            ha="center", va="center", fontsize=9, color=TEXT_DIM, fontfamily="monospace")
        ax_formula.axis("off")

        # Top 15 most urgent reorder items
        ax_bar = fig.add_axes([0.06, 0.38, 0.88, 0.42])
        reorder_df = df[df["needs_reorder"]].nsmallest(15, "days_of_stock")

        if len(reorder_df) > 0:
            labels = [f"{r['part_name'][:20]} ({r['branch'][:3]})" for _, r in reorder_df.iterrows()]
            labels.reverse()
            stocks = reorder_df["current_stock"].values[::-1]
            rops = reorder_df["reorder_point"].values[::-1]
            y_pos = np.arange(len(labels))

            ax_bar.barh(y_pos, rops, height=0.5, color=COLORS["Slow-Moving"],
                        alpha=0.35, label="Reorder Point", edgecolor=COLORS["Slow-Moving"], linewidth=0.8)
            ax_bar.barh(y_pos, stocks, height=0.5, color=ACCENT_ORANGE,
                        label="Current Stock", edgecolor=ACCENT_ORANGE, linewidth=0.8)

            for i, (s, r) in enumerate(zip(stocks, rops)):
                ax_bar.text(r + 1, i, f"ROP: {r}", va="center", fontsize=7, color=COLORS["Slow-Moving"])
                ax_bar.text(max(s - 2, 1), i, str(s), va="center", ha="right",
                            fontsize=7, fontweight="bold", color=TEXT_LIGHT)

            ax_bar.set_yticks(y_pos)
            ax_bar.set_yticklabels(labels, fontsize=8)
            ax_bar.set_xlabel("Units")
            ax_bar.set_title("Top 15 Most Urgent Reorder Items (stock vs reorder point)",
                              fontsize=11, fontweight="bold", color=TEXT_LIGHT, pad=10)
            ax_bar.legend(loc="lower right", fontsize=8)
            ax_bar.grid(axis="x", alpha=0.3)

        # Dead stock by category
        ax_dead = fig.add_axes([0.06, 0.06, 0.88, 0.26])
        slow = df[df["demand_class"] == "Slow-Moving"]
        dead_cat = slow.groupby("category")["stock_value_zar"].sum().sort_values(ascending=False)

        if len(dead_cat) > 0:
            bars = ax_dead.bar(range(len(dead_cat)), dead_cat.values, width=0.55,
                               color=COLORS["Slow-Moving"], edgecolor=BG_DARK, linewidth=1)
            ax_dead.set_xticks(range(len(dead_cat)))
            ax_dead.set_xticklabels(dead_cat.index, fontsize=9)
            ax_dead.yaxis.set_major_formatter(mticker.FuncFormatter(zar_fmt))
            ax_dead.set_title("Dead Stock Value at Risk — Slow-Movers by Category",
                               fontsize=11, fontweight="bold", color=TEXT_LIGHT, pad=10)
            for bar, val in zip(bars, dead_cat.values):
                ax_dead.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 500,
                             f"R{val:,.0f}", ha="center", fontsize=7, color=TEXT_LIGHT)
            ax_dead.grid(axis="y", alpha=0.3)

        pdf.savefig(fig, facecolor=BG_DARK)
        plt.close(fig)

        # ──────────────── PAGE 4: BRANCH COMPARISON ────────────────
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle("BRANCH PERFORMANCE COMPARISON", fontsize=16,
                      fontweight="bold", color=TEXT_LIGHT, y=0.97)
        plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.90, bottom=0.08)

        branch_stats = df.groupby("branch").agg(
            total_sales=("total_sold_12m", "sum"),
            stock_value=("stock_value_zar", "sum"),
            slow_count=("demand_class", lambda x: (x == "Slow-Moving").sum()),
            reorder_count=("needs_reorder", "sum"),
        ).sort_values("total_sales", ascending=False)

        colors_branch = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#06b6d4"]

        # 12M Sales
        ax = axes[0, 0]
        bars = ax.bar(range(len(branch_stats)), branch_stats["total_sales"].values,
                       color=colors_branch[:len(branch_stats)], width=0.6, edgecolor=BG_DARK)
        ax.set_xticks(range(len(branch_stats)))
        ax.set_xticklabels([b[:5] for b in branch_stats.index], fontsize=8, rotation=30)
        ax.set_title("12-Month Sales Volume", fontsize=11, fontweight="bold", color=TEXT_LIGHT, pad=8)
        ax.grid(axis="y", alpha=0.3)
        for bar, val in zip(bars, branch_stats["total_sales"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                     f"{val:,}", ha="center", fontsize=7, color=TEXT_LIGHT)

        # Stock Value
        ax = axes[0, 1]
        bars = ax.bar(range(len(branch_stats)), branch_stats["stock_value"].values,
                       color=colors_branch[:len(branch_stats)], width=0.6, edgecolor=BG_DARK)
        ax.set_xticks(range(len(branch_stats)))
        ax.set_xticklabels([b[:5] for b in branch_stats.index], fontsize=8, rotation=30)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(zar_fmt))
        ax.set_title("Current Stock Value (ZAR)", fontsize=11, fontweight="bold", color=TEXT_LIGHT, pad=8)
        ax.grid(axis="y", alpha=0.3)

        # Slow-movers per branch
        ax = axes[1, 0]
        bars = ax.bar(range(len(branch_stats)), branch_stats["slow_count"].values,
                       color=[COLORS["Slow-Moving"]] * len(branch_stats), width=0.6,
                       edgecolor=BG_DARK, alpha=0.85)
        ax.set_xticks(range(len(branch_stats)))
        ax.set_xticklabels([b[:5] for b in branch_stats.index], fontsize=8, rotation=30)
        ax.set_title("Slow-Moving SKUs per Branch", fontsize=11, fontweight="bold",
                      color=TEXT_LIGHT, pad=8)
        ax.grid(axis="y", alpha=0.3)
        for bar, val in zip(bars, branch_stats["slow_count"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                     str(val), ha="center", fontsize=9, fontweight="bold", color=COLORS["Slow-Moving"])

        # Reorder alerts per branch
        ax = axes[1, 1]
        bars = ax.bar(range(len(branch_stats)), branch_stats["reorder_count"].values,
                       color=[ACCENT_YELLOW] * len(branch_stats), width=0.6,
                       edgecolor=BG_DARK, alpha=0.85)
        ax.set_xticks(range(len(branch_stats)))
        ax.set_xticklabels([b[:5] for b in branch_stats.index], fontsize=8, rotation=30)
        ax.set_title("Reorder Alerts per Branch", fontsize=11, fontweight="bold",
                      color=TEXT_LIGHT, pad=8)
        ax.grid(axis="y", alpha=0.3)
        for bar, val in zip(bars, branch_stats["reorder_count"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                     str(val), ha="center", fontsize=9, fontweight="bold", color=ACCENT_YELLOW)

        pdf.savefig(fig, facecolor=BG_DARK)
        plt.close(fig)

    print(f"\n✅  PDF report saved → {output_path}")


# ═══════════════════════════════════════════════════════════════
# 5. EXPORT CSV
# ═══════════════════════════════════════════════════════════════

def export_csv(df: pd.DataFrame, path: str):
    """Export the full analysed dataset to CSV."""
    export_cols = [
        "sku", "part_name", "category", "branch", "unit_cost_zar",
        "avg_monthly_sales", "total_sold_12m", "current_stock",
        "lead_time_days", "safety_stock_days", "demand_class",
        "daily_sales_rate", "safety_stock_units", "lead_time_demand",
        "reorder_point", "days_of_stock", "needs_reorder",
        "stock_value_zar", "shortfall", "suggested_order", "turnover_ratio",
    ] + [f"sales_{m.lower()}" for m in MONTHS]

    df[export_cols].to_csv(path, index=False)
    print(f"✅  CSV dataset saved → {path}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 1. Generate data
    print("Generating mock automotive parts dataset...")
    df_raw = generate_dataset()

    # 2. Add analytics columns
    df = add_calculated_columns(df_raw)

    # 3. Console summaries
    print_kpi_summary(df)
    print_demand_breakdown(df)
    print_reorder_alerts(df, top_n=15)
    print_branch_comparison(df)
    print_dead_stock_by_category(df)

    # 4. Visual PDF report
    create_pdf_report(df, "inventory_report.pdf")

    # 5. Export CSV
    export_csv(df, "inventory_dataset.csv")

    print("\n🏁  Done! Files generated:")
    print("   • inventory_report.pdf  — 4-page visual dashboard")
    print("   • inventory_dataset.csv — full analysed dataset (240 rows)")
