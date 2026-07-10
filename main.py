"""Amazon US women's shoes operation data analysis Streamlit app."""

from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Amazon US 女鞋运营分析", page_icon="👠", layout="wide")

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


def read_upload(uploaded_file) -> pd.DataFrame:
    """Read a CSV/XLSX file uploaded through Streamlit."""
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


def standardize_columns(df: pd.DataFrame, mapping: dict[str, list[str]]) -> pd.DataFrame:
    """Rename common Chinese/English column names to canonical names."""
    if df.empty:
        return df
    renamed = {}
    for target, candidates in mapping.items():
        match = _match_column(df.columns, candidates)
        if match is not None:
            renamed[match] = target
    return df.rename(columns=renamed)


def coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def load_example_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return built-in demo data without requiring binary files in the repo."""
    sales = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=12, freq="7D"),
            "asin": ["B0HSANDAL1", "B0FLATSAND2", "B0PUMPHEEL3"] * 4,
            "sku": ["HS-RED-7", "FS-BLK-8", "PH-NUDE-6"] * 4,
            "product_name": ["High Heel Sandals Red", "Flat Sandals Black", "Classic Pump Heels Nude"] * 4,
            "category": ["高跟凉鞋", "平底凉鞋", "高跟鞋"] * 4,
            "units": [18, 25, 12, 22, 30, 14, 28, 35, 20, 34, 41, 24],
            "sales": [899.82, 749.75, 719.88, 1099.78, 899.70, 839.86, 1399.72, 1049.65, 1199.80, 1699.66, 1229.59, 1439.76],
            "orders": [16, 23, 11, 20, 28, 13, 25, 33, 18, 31, 39, 22],
        }
    )
    ads = pd.DataFrame(
        {
            "keyword": [
                "womens high heel sandals",
                "flat sandals women",
                "nude pumps women",
                "strappy heels",
                "comfortable sandals",
                "wedding heels",
            ],
            "campaign": ["SP-Heel-Sandals", "SP-Flat-Sandals", "SP-Pumps", "SP-Heel-Sandals", "SP-Flat-Sandals", "SP-Pumps"],
            "impressions": [12000, 18500, 9000, 7600, 15000, 6800],
            "clicks": [420, 510, 260, 210, 390, 180],
            "cpc": [0.82, 0.65, 0.95, 1.10, 0.70, 1.25],
            "spend": [344.40, 331.50, 247.00, 231.00, 273.00, 225.00],
            "ad_sales": [1680.00, 980.00, 1420.00, 180.00, 760.00, 0.00],
            "orders": [32, 24, 21, 1, 17, 0],
        }
    )
    return sales, ads


def sales_module(sales_df: pd.DataFrame) -> pd.DataFrame:
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


def ppc_module(ads_df: pd.DataFrame) -> pd.DataFrame:
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


def profit_module() -> pd.DataFrame:
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


def dashboard(sales_df: pd.DataFrame, ads_df: pd.DataFrame) -> None:
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
    main()
