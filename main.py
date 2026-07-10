"""Amazon US women's shoes operation data analysis tool.

The Streamlit dashboard is preserved when dependencies are installed. In offline
or restricted environments, run ``python main.py --self-test`` (or simply
``python main.py`` when Streamlit is missing) to validate the core analytics
logic without third-party packages.
"""

from __future__ import annotations

import importlib.util
import sys
from collections import defaultdict
from typing import Any, Iterable

HAS_PANDAS = importlib.util.find_spec("pandas") is not None
HAS_PLOTLY = importlib.util.find_spec("plotly") is not None
HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None

if HAS_PANDAS:
    import pandas as pd
else:
    pd = None

if HAS_PLOTLY:
    import plotly.express as px
else:
    px = None

if HAS_STREAMLIT:
    import streamlit as st
else:
    st = None

SALES_COLUMNS = {
    "date": ["date", "日期", "purchase date", "order date"],
    "asin": ["asin", "ASIN"],
    "sku": ["sku", "SKU", "seller sku"],
    "product_name": ["product name", "产品名称", "title", "商品名称"],
    "category": ["category", "类目", "品类"],
    "units": ["units", "销量", "quantity", "数量"],
    "sales": ["sales", "销售额", "revenue", "item price"],
    "orders": ["orders", "订单数量", "order count"],
}

ADS_COLUMNS = {
    "keyword": ["keyword", "关键词", "targeting", "customer search term"],
    "campaign": ["campaign", "广告活动", "campaign name"],
    "impressions": ["impressions", "展示量"],
    "clicks": ["clicks", "点击量"],
    "cpc": ["cpc", "CPC"],
    "spend": ["spend", "广告花费", "cost"],
    "ad_sales": ["ad sales", "广告销售额", "sales"],
    "orders": ["orders", "订单数量", "purchases"],
}

DEMO_SALES_ROWS: list[dict[str, Any]] = [
    {"date": "2026-01-01", "asin": "B0HSANDAL1", "sku": "HS-RED-7", "product_name": "High Heel Sandals Red", "category": "高跟凉鞋", "units": 18, "sales": 899.82, "orders": 16},
    {"date": "2026-01-08", "asin": "B0FLATSAND2", "sku": "FS-BLK-8", "product_name": "Flat Sandals Black", "category": "平底凉鞋", "units": 25, "sales": 749.75, "orders": 23},
    {"date": "2026-01-15", "asin": "B0PUMPHEEL3", "sku": "PH-NUDE-6", "product_name": "Classic Pump Heels Nude", "category": "高跟鞋", "units": 12, "sales": 719.88, "orders": 11},
    {"date": "2026-01-22", "asin": "B0HSANDAL1", "sku": "HS-RED-7", "product_name": "High Heel Sandals Red", "category": "高跟凉鞋", "units": 22, "sales": 1099.78, "orders": 20},
    {"date": "2026-01-29", "asin": "B0FLATSAND2", "sku": "FS-BLK-8", "product_name": "Flat Sandals Black", "category": "平底凉鞋", "units": 30, "sales": 899.70, "orders": 28},
    {"date": "2026-02-05", "asin": "B0PUMPHEEL3", "sku": "PH-NUDE-6", "product_name": "Classic Pump Heels Nude", "category": "高跟鞋", "units": 14, "sales": 839.86, "orders": 13},
    {"date": "2026-02-12", "asin": "B0HSANDAL1", "sku": "HS-RED-7", "product_name": "High Heel Sandals Red", "category": "高跟凉鞋", "units": 28, "sales": 1399.72, "orders": 25},
    {"date": "2026-02-19", "asin": "B0FLATSAND2", "sku": "FS-BLK-8", "product_name": "Flat Sandals Black", "category": "平底凉鞋", "units": 35, "sales": 1049.65, "orders": 33},
    {"date": "2026-02-26", "asin": "B0PUMPHEEL3", "sku": "PH-NUDE-6", "product_name": "Classic Pump Heels Nude", "category": "高跟鞋", "units": 20, "sales": 1199.80, "orders": 18},
    {"date": "2026-03-05", "asin": "B0HSANDAL1", "sku": "HS-RED-7", "product_name": "High Heel Sandals Red", "category": "高跟凉鞋", "units": 34, "sales": 1699.66, "orders": 31},
    {"date": "2026-03-12", "asin": "B0FLATSAND2", "sku": "FS-BLK-8", "product_name": "Flat Sandals Black", "category": "平底凉鞋", "units": 41, "sales": 1229.59, "orders": 39},
    {"date": "2026-03-19", "asin": "B0PUMPHEEL3", "sku": "PH-NUDE-6", "product_name": "Classic Pump Heels Nude", "category": "高跟鞋", "units": 24, "sales": 1439.76, "orders": 22},
]

DEMO_AD_ROWS: list[dict[str, Any]] = [
    {"keyword": "womens high heel sandals", "campaign": "SP-Heel-Sandals", "impressions": 12000, "clicks": 420, "cpc": 0.82, "spend": 344.40, "ad_sales": 1680.00, "orders": 32},
    {"keyword": "flat sandals women", "campaign": "SP-Flat-Sandals", "impressions": 18500, "clicks": 510, "cpc": 0.65, "spend": 331.50, "ad_sales": 980.00, "orders": 24},
    {"keyword": "nude pumps women", "campaign": "SP-Pumps", "impressions": 9000, "clicks": 260, "cpc": 0.95, "spend": 247.00, "ad_sales": 1420.00, "orders": 21},
    {"keyword": "strappy heels", "campaign": "SP-Heel-Sandals", "impressions": 7600, "clicks": 210, "cpc": 1.10, "spend": 231.00, "ad_sales": 180.00, "orders": 1},
    {"keyword": "comfortable sandals", "campaign": "SP-Flat-Sandals", "impressions": 15000, "clicks": 390, "cpc": 0.70, "spend": 273.00, "ad_sales": 760.00, "orders": 17},
    {"keyword": "wedding heels", "campaign": "SP-Pumps", "impressions": 6800, "clicks": 180, "cpc": 1.25, "spend": 225.00, "ad_sales": 0.00, "orders": 0},
]


def _require_pandas() -> None:
    if pd is None:
        raise RuntimeError("pandas is required for Streamlit mode. Run `python main.py --self-test` for offline validation.")


def read_upload(uploaded_file):
    """Read a CSV/XLSX file uploaded through Streamlit."""
    _require_pandas()
    if uploaded_file is None:
        return pd.DataFrame()
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)


def _match_column(columns: Iterable[str], candidates: list[str]) -> str | None:
    normalized = {str(col).strip().lower(): col for col in columns}
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in normalized:
            return normalized[key]
    return None


def standardize_columns(df, mapping: dict[str, list[str]]):
    """Rename common Chinese/English column names to canonical names."""
    if df.empty:
        return df
    renamed = {}
    for target, candidates in mapping.items():
        match = _match_column(df.columns, candidates)
        if match is not None:
            renamed[match] = target
    return df.rename(columns=renamed)


def coerce_numeric(df, columns: list[str]):
    _require_pandas()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def load_example_data():
    """Return built-in demo data without requiring binary files in the repo."""
    _require_pandas()
    return pd.DataFrame(DEMO_SALES_ROWS), pd.DataFrame(DEMO_AD_ROWS)


def calculate_basic_metrics(sales_rows: list[dict[str, Any]], ad_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate core metrics with the Python standard library for offline tests."""
    sales_by_month: dict[str, dict[str, float]] = defaultdict(lambda: {"units": 0, "sales": 0.0, "orders": 0})
    product_units: dict[str, int] = defaultdict(int)
    for row in sales_rows:
        month = str(row["date"])[:7]
        sales_by_month[month]["units"] += int(row.get("units", 0))
        sales_by_month[month]["sales"] += float(row.get("sales", 0))
        sales_by_month[month]["orders"] += int(row.get("orders", 0))
        product_units[str(row.get("product_name", row.get("sku", "Unknown")))] += int(row.get("units", 0))

    ad_metrics = []
    for row in ad_rows:
        spend = float(row.get("spend", 0))
        ad_sales = float(row.get("ad_sales", 0))
        clicks = float(row.get("clicks", 0))
        orders = float(row.get("orders", 0))
        ad_metrics.append(
            {
                "keyword": row.get("keyword", ""),
                "acos": spend / ad_sales * 100 if ad_sales else 0,
                "roas": ad_sales / spend if spend else 0,
                "conversion_rate": orders / clicks * 100 if clicks else 0,
                "is_profitable": ad_sales > spend,
            }
        )

    return {
        "total_units": sum(int(row.get("units", 0)) for row in sales_rows),
        "total_sales": sum(float(row.get("sales", 0)) for row in sales_rows),
        "total_orders": sum(int(row.get("orders", 0)) for row in sales_rows),
        "monthly_sales": dict(sorted(sales_by_month.items())),
        "top_products": sorted(product_units.items(), key=lambda item: item[1], reverse=True)[:10],
        "ad_metrics": ad_metrics,
    }


def run_local_data_test() -> int:
    """Run a dependency-free smoke test for the analytics logic."""
    metrics = calculate_basic_metrics(DEMO_SALES_ROWS, DEMO_AD_ROWS)
    required = ["total_units", "total_sales", "total_orders", "monthly_sales", "top_products", "ad_metrics"]
    missing = [key for key in required if key not in metrics]
    if missing:
        print(f"基础数据处理测试失败，缺少指标: {', '.join(missing)}")
        return 1

    print("基础数据处理测试通过")
    print(f"总销量: {metrics['total_units']}")
    print(f"总销售额: ${metrics['total_sales']:.2f}")
    print(f"总订单数: {metrics['total_orders']}")
    print(f"月份数量: {len(metrics['monthly_sales'])}")
    print(f"TOP产品: {metrics['top_products'][0][0]} ({metrics['top_products'][0][1]} 件)")
    print(f"广告关键词数量: {len(metrics['ad_metrics'])}")
    if not HAS_STREAMLIT:
        print("提示: 当前环境未安装 streamlit，已跳过页面启动。安装依赖后运行 `streamlit run main.py`。")
    return 0


def sales_module(sales_df):
    st.header("1. 销售数据模块")
    sales_df = standardize_columns(sales_df, SALES_COLUMNS)
    if sales_df.empty:
        st.info("请上传销售 CSV/Excel，或勾选侧边栏示例数据。")
        return sales_df

    sales_df = coerce_numeric(sales_df, ["units", "sales", "orders"])
    if "date" in sales_df.columns:
        sales_df["date"] = pd.to_datetime(sales_df["date"], errors="coerce")
        sales_df = sales_df.dropna(subset=["date"])
    else:
        st.warning("未找到日期列，请使用 date/日期/order date 等列名。")
        return sales_df

    total_units = sales_df["units"].sum() if "units" in sales_df else 0
    total_sales = sales_df["sales"].sum() if "sales" in sales_df else 0
    total_orders = sales_df["orders"].sum() if "orders" in sales_df else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("总销量", f"{total_units:,.0f}")
    c2.metric("总销售额", f"${total_sales:,.2f}")
    c3.metric("总订单数", f"{total_orders:,.0f}")

    required = [col for col in ["date", "asin", "sku", "product_name", "units", "sales", "orders"] if col in sales_df]
    st.dataframe(sales_df[required], use_container_width=True)

    daily = sales_df.groupby("date", as_index=False).agg(units=("units", "sum"), sales=("sales", "sum"))
    st.plotly_chart(px.line(daily, x="date", y="units", title="日销量趋势", markers=True), use_container_width=True)

    monthly = sales_df.set_index("date").resample("ME").agg({"units": "sum", "sales": "sum"}).reset_index()
    st.plotly_chart(px.bar(monthly, x="date", y="units", title="月销量趋势"), use_container_width=True)
    return sales_df


def ppc_module(ads_df):
    st.header("2. 亚马逊广告 PPC 分析模块")
    ads_df = standardize_columns(ads_df, ADS_COLUMNS)
    if ads_df.empty:
        st.info("请上传广告 CSV/Excel，或勾选侧边栏示例数据。")
        return ads_df

    ads_df = coerce_numeric(ads_df, ["impressions", "clicks", "cpc", "spend", "ad_sales", "orders"])
    ads_df["acos"] = (ads_df["spend"] / ads_df["ad_sales"].replace(0, pd.NA) * 100).fillna(0)
    ads_df["roas"] = (ads_df["ad_sales"] / ads_df["spend"].replace(0, pd.NA)).fillna(0)
    ads_df["conversion_rate"] = (ads_df["orders"] / ads_df["clicks"].replace(0, pd.NA) * 100).fillna(0)

    c1, c2, c3 = st.columns(3)
    c1.metric("广告花费", f"${ads_df['spend'].sum():,.2f}")
    c2.metric("广告销售额", f"${ads_df['ad_sales'].sum():,.2f}")
    blended_acos = ads_df["spend"].sum() / ads_df["ad_sales"].sum() * 100 if ads_df["ad_sales"].sum() else 0
    c3.metric("整体 ACOS", f"{blended_acos:.2f}%")

    spend_threshold = st.slider("高花费阈值（美元）", 0.0, float(max(ads_df["spend"].max(), 1)), float(ads_df["spend"].median()))
    low_conversion = ads_df[(ads_df["spend"] >= spend_threshold) & (ads_df["orders"] <= 1)].sort_values("spend", ascending=False)
    profitable = ads_df[(ads_df["ad_sales"] - ads_df["spend"]) > 0].sort_values("roas", ascending=False)
    unprofitable = ads_df[(ads_df["ad_sales"] - ads_df["spend"]) <= 0].sort_values("spend", ascending=False)

    tab1, tab2, tab3 = st.tabs(["高花费低转化关键词", "盈利广告", "亏损广告"])
    tab1.dataframe(low_conversion, use_container_width=True)
    tab2.dataframe(profitable, use_container_width=True)
    tab3.dataframe(unprofitable, use_container_width=True)
    st.plotly_chart(px.bar(ads_df, x="keyword", y="spend", color="acos", title="关键词广告花费与 ACOS"), use_container_width=True)
    return ads_df


def profit_module():
    st.header("3. 利润计算模块")
    c1, c2, c3 = st.columns(3)
    price = c1.number_input("产品售价", min_value=0.0, value=49.99, step=1.0)
    purchase_cost = c2.number_input("采购成本", min_value=0.0, value=12.0, step=1.0)
    logistics = c3.number_input("物流费用", min_value=0.0, value=4.5, step=0.5)
    fba = c1.number_input("FBA费用", min_value=0.0, value=5.6, step=0.5)
    commission = c2.number_input("Amazon佣金", min_value=0.0, value=7.5, step=0.5)
    ad_fee = c3.number_input("广告费用", min_value=0.0, value=6.0, step=0.5)

    unit_profit = price - purchase_cost - logistics - fba - commission - ad_fee
    profit_margin = unit_profit / price * 100 if price else 0
    c1.metric("单件利润", f"${unit_profit:.2f}")
    c2.metric("利润率", f"{profit_margin:.2f}%")
    return pd.DataFrame({"metric": ["单件利润", "利润率"], "value": [unit_profit, profit_margin]})


def dashboard(sales_df, ads_df) -> None:
    st.header("4. 数据仪表盘")
    if not sales_df.empty and "date" in sales_df and "sales" in sales_df:
        daily = sales_df.groupby("date", as_index=False).agg(sales=("sales", "sum"), units=("units", "sum"))
        daily["estimated_profit"] = daily["sales"] * 0.22
        st.plotly_chart(px.line(daily, x="date", y="sales", title="销售趋势图"), use_container_width=True)
        st.plotly_chart(px.line(daily, x="date", y="estimated_profit", title="利润趋势图（按22%估算）"), use_container_width=True)
        product_col = "product_name" if "product_name" in sales_df else "sku"
        top10 = sales_df.groupby(product_col, as_index=False).agg(units=("units", "sum")).sort_values("units", ascending=False).head(10)
        st.plotly_chart(px.bar(top10, x=product_col, y="units", title="产品排名 TOP10"), use_container_width=True)
    if not ads_df.empty and "spend" in ads_df:
        st.plotly_chart(px.pie(ads_df, names="keyword", values="spend", title="广告花费图"), use_container_width=True)


def main() -> None:
    if not (HAS_STREAMLIT and HAS_PANDAS and HAS_PLOTLY):
        missing = [name for name, installed in {"streamlit": HAS_STREAMLIT, "pandas": HAS_PANDAS, "plotly": HAS_PLOTLY}.items() if not installed]
        print("无法启动 Streamlit 页面，缺少依赖: " + ", ".join(missing))
        print("可先运行 `python main.py --self-test` 验证基础数据分析逻辑。")
        return

    st.set_page_config(page_title="Amazon US 女鞋运营分析", page_icon="👠", layout="wide")
    st.title("👠 Amazon US 女鞋运营数据分析工具")
    st.caption("适用于高跟凉鞋、平底凉鞋、高跟鞋等美国站女鞋店铺运营分析。")

    with st.sidebar:
        st.header("数据导入")
        use_example = st.checkbox("使用内置示例数据", value=True)
        sales_file = st.file_uploader("上传销售数据（Excel/CSV）", type=["xlsx", "xls", "csv"])
        ads_file = st.file_uploader("上传广告数据（Excel/CSV）", type=["xlsx", "xls", "csv"])

    if use_example and sales_file is None and ads_file is None:
        sales_df, ads_df = load_example_data()
    else:
        sales_df = read_upload(sales_file)
        ads_df = read_upload(ads_file)

    sales_df = sales_module(sales_df)
    ads_df = ppc_module(ads_df)
    profit_module()
    dashboard(sales_df, ads_df)


if __name__ == "__main__":
    if "--self-test" in sys.argv or not HAS_STREAMLIT:
        raise SystemExit(run_local_data_test())
    main()
