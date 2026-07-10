# Amazon US 女鞋运营数据分析工具

一个使用 **Python + Streamlit + Pandas + Plotly** 构建的亚马逊美国站女鞋店铺运营分析工具，适用于高跟凉鞋、平底凉鞋、高跟鞋等产品线。

## 功能

- **销售数据模块**：导入 Excel/CSV，按日期、ASIN、SKU、产品名称统计销量、销售额、订单数量，并展示日销量、月销量趋势。
- **亚马逊广告 PPC 分析模块**：导入展示量、点击量、CPC、广告花费、广告销售额、订单数量，自动计算 ACOS 与 ROAS，识别高花费低转化关键词、盈利广告和亏损广告。
- **利润计算模块**：输入售价、采购成本、物流费用、FBA 费用、Amazon 佣金、广告费用，自动计算单件利润和利润率。
- **数据仪表盘**：展示销售趋势图、利润趋势图、广告花费图和产品排名 TOP10。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

打开浏览器中的 Streamlit 地址后，可直接使用默认勾选的内置示例数据，也可以在侧边栏上传自己的 CSV/Excel 文件。

## 数据字段建议

### 销售数据

| 字段 | 示例列名 |
| --- | --- |
| 日期 | `date` / `日期` / `order date` |
| ASIN | `asin` |
| SKU | `sku` |
| 产品名称 | `product_name` / `产品名称` |
| 销量 | `units` / `销量` / `quantity` |
| 销售额 | `sales` / `销售额` / `revenue` |
| 订单数量 | `orders` / `订单数量` |

### 广告数据

| 字段 | 示例列名 |
| --- | --- |
| 关键词 | `keyword` / `关键词` / `targeting` |
| 展示量 | `impressions` / `展示量` |
| 点击量 | `clicks` / `点击量` |
| CPC | `cpc` |
| 广告花费 | `spend` / `广告花费` / `cost` |
| 广告销售额 | `ad_sales` / `广告销售额` |
| 订单数量 | `orders` / `订单数量` |

## 示例数据

仓库不包含 xlsx、图片等二进制示例文件；应用在 `main.py` 中内置了销售与 PPC 广告演示数据，方便直接运行预览。
