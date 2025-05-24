# -*- coding: utf-8 -*-


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# 读取 CSV（注意使用 Colab 左侧上传的文件名）
pre_2025_df = pd.read_csv("bus_monthly_speed_data/MTA_Bus_Speeds__2020_-_2024_20250430.csv")
post_2025_df = pd.read_csv("bus_monthly_speed_data/MTA_Bus_Speeds_Beginning_2025_20250430.csv")

# 日期和标记
pre_2025_df['month'] = pd.to_datetime(pre_2025_df['month'])
post_2025_df['month'] = pd.to_datetime(post_2025_df['month'])

combined_df = pd.concat([pre_2025_df, post_2025_df])
combined_df['year'] = combined_df['month'].dt.year
combined_df['month_num'] = combined_df['month'].dt.month

# 路线分类
local_crz_inside_only = {"M8", "M9", "M14A+", "M14D+", "M21", "M22", "M55"}
local_crz_crossing = {"M1", "M2", "M3", "M4", "M5", "M7", "M10", "M11", "M15", "M20", "M31", "M50", "M57", "M66",
                      "M72", "M79", "M101", "M102", "M103", "Q32", "B39"}
express_crz = {
    "BxM1", "BxM2", "BxM3", "BxM4", "BxM6", "BxM7", "BxM18", "BM1", "BM2", "BM3", "BM4", "BM5",
    "X27", "X28", "X37", "X38", "QM1", "QM2", "QM4", "QM5", "QM6", "QM7", "QM8", "QM10", "QM11", "QM12",
    "QM15", "QM16", "QM17", "QM18", "QM20", "QM21", "QM24", "QM25", "QM31", "QM32", "QM34", "QM35", "QM36",
    "SIM1", "SIM1C", "SIM3", "SIM3C", "SIM4", "SIM4C", "SIM4X", "SIM7", "SIM8", "SIM8X", "SIM9", "SIM10",
    "SIM11", "SIM15", "SIM22", "SIM23", "SIM24", "SIM25", "SIM26", "SIM30", "SIM31", "SIM32", "SIM33", "SIM33C",
    "SIM34", "SIM35"
}

def classify_route(route):
    if route in local_crz_inside_only:
        return "Local Only in CRZ"
    elif route in local_crz_crossing:
        return "Local Crosses CRZ"
    elif route in express_crz:
        return "Express to CRZ"
    else:
        return None

# 筛选 weekday 且 trip_type 为 LCL/LTD 或 EXP

filtered_all = combined_df[(combined_df['day_type'] == 1) & (combined_df['trip_type'].isin(['LCL/LTD', 'EXP', 'SBS']))].copy()
filtered_all['New_Group'] = filtered_all['route_id'].apply(classify_route)
filtered_all[filtered_all['route_id'].str.contains("M14A+")]
filtered_all[filtered_all['route_id'].str.contains("M14D+")]


# 重新使用最新结构绘图并在柱状图上加上数值标签
def plot_monthly_comparison_by_period_annotated(data, label="All Periods"):
    def compute_change(month):
        before = data[(data['year'] == 2024) & (data['month_num'] == month)]
        after = data[(data['year'] == 2025) & (data['month_num'] == month)]
        before_avg = before.groupby('New_Group')['average_speed'].mean()
        after_avg = after.groupby('New_Group')['average_speed'].mean()
        change = ((after_avg - before_avg) / before_avg) * 100
        return change.rename(f'{month}')

    jan = compute_change(1)
    feb = compute_change(2)
    mar = compute_change(3)
    comp_df = pd.concat([jan, feb, mar], axis=1)

    # 绘图
    ax = comp_df.T.plot(kind='bar', figsize=(10, 6))
    plt.title(f'2024 vs 2025 Monthly Speed Change (%) - {label}')
    plt.ylabel('Percent Change in Average Speed')
    plt.xlabel('month')
    plt.xticks(rotation=0)
    plt.axhline(0, color='gray', linestyle='--')
    plt.grid(axis='y')
    plt.legend(title='Route Group')

    # 添加百分比标签
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f%%', label_type='edge', fontsize=9)

    plt.tight_layout()
    plt.show()

# 使用加注释版本重新绘制三张图
plot_monthly_comparison_by_period_annotated(filtered_all, label="All Periods")
plot_monthly_comparison_by_period_annotated(filtered_all[filtered_all['period'] == 'Off-Peak'], label="Off-Peak Only")
plot_monthly_comparison_by_period_annotated(filtered_all[filtered_all['period'] == 'Peak'], label="Peak Only")

# Re-import required modules after kernel reset
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV files again
pre_2025_df = pd.read_csv("MTA_Bus_Speeds__2020_-_2024_20250430.csv")
post_2025_df = pd.read_csv("MTA_Bus_Speeds__Beginning_2025_20250430.csv")

# Convert date column and add year/month
pre_2025_df['month'] = pd.to_datetime(pre_2025_df['month'])
post_2025_df['month'] = pd.to_datetime(post_2025_df['month'])
combined_df = pd.concat([pre_2025_df, post_2025_df])
combined_df['year'] = combined_df['month'].dt.year
combined_df['month_num'] = combined_df['month'].dt.month

# Define route classification sets
local_crz_inside_only = {"M8", "M9", "M14A+", "M14D+", "M21", "M22", "M55"}
local_crz_crossing = {"M1", "M2", "M3", "M4", "M5", "M7", "M10", "M11", "M15", "M20", "M31", "M50", "M57", "M66", "M72", "M79", "M101", "M102", "M103", "Q32", "B39"}
express_crz = {
    "BxM1", "BxM2", "BxM3", "BxM4", "BxM6", "BxM7", "BxM18", "BM1", "BM2", "BM3", "BM4", "BM5",
    "X27", "X28", "X37", "X38", "QM1", "QM2", "QM4", "QM5", "QM6", "QM7", "QM8", "QM10", "QM11", "QM12",
    "QM15", "QM16", "QM17", "QM18", "QM20", "QM21", "QM24", "QM25", "QM31", "QM32", "QM34", "QM35", "QM36",
    "SIM1", "SIM1C", "SIM3", "SIM3C", "SIM4", "SIM4C", "SIM4X", "SIM7", "SIM8", "SIM8X", "SIM9", "SIM10",
    "SIM11", "SIM15", "SIM22", "SIM23", "SIM24", "SIM25", "SIM26", "SIM30", "SIM31", "SIM32", "SIM33", "SIM33C",
    "SIM34", "SIM35"
}

# Classification function
def classify_route(route):
    if route in local_crz_inside_only:
        return "Local Only in CRZ"
    elif route in local_crz_crossing:
        return "Local Crosses CRZ"
    elif route in express_crz:
        return "Express to CRZ"
    else:
        return None

# Apply classification
combined_df['New_Group'] = combined_df['route_id'].apply(classify_route)

# Filter valid subset
filtered_df = combined_df[
    (combined_df['trip_type'].isin(['LCL/LTD', 'EXP', 'SBS'])) &
    (combined_df['month_num'].isin([1, 2, 3])) &
    (combined_df['year'].isin([2024, 2025]))
].copy()

# Plotting function
def plot_by_filters(data, day_type_val, period_val, title_suffix):
    data = data[(data['day_type'] == day_type_val)]
    if period_val:
        data = data[data['period'] == period_val]
    results = {}
    for month in [1, 2, 3]:
        before = data[(data['year'] == 2024) & (data['month_num'] == month)].groupby('New_Group')['average_speed'].mean()
        after = data[(data['year'] == 2025) & (data['month_num'] == month)].groupby('New_Group')['average_speed'].mean()
        pct_change = ((after - before) / before * 100).rename(str(month))
        results[month] = pct_change
    result_df = pd.concat(results.values(), axis=1)
    result_df.columns = ['Jan', 'Feb', 'Mar']
    ax = result_df.T.plot(kind='bar', figsize=(10, 6))
    plt.title(f"2024 vs 2025 Speed Change - {title_suffix}")
    plt.ylabel('% Speed Change')
    plt.xlabel('Month')
    plt.xticks(rotation=0)
    plt.axhline(0, color='gray', linestyle='--')
    plt.legend(title='Route Group')
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%')
    plt.tight_layout()
    return plt

# ✅ 显示图像 + 保存 PNG 图像的版本
import os
os.makedirs("charts", exist_ok=True)  # 创建 charts 文件夹

plots = {
    "Weekday Only": (1, None),
    "Weekend Only": (2, None),
    "Weekday Peak": (1, 'Peak'),
    "Weekend Peak": (2, 'Peak'),
    "Weekday Off-Peak": (1, 'Off-Peak'),
    "Weekend Off-Peak": (2, 'Off-Peak'),
}

plot_files = []
for label, (day, period) in plots.items():
    fig = plt.figure(figsize=(10, 6))
    plt_obj = plot_by_filters(filtered_df, day, period, label)

    # 保存路径
    filename = f"charts/speed_change_{label.replace(' ', '_')}.png"
    plt.savefig(filename, dpi=300)
    plot_files.append(filename)

    # 显示图像
    plt.show()
    plt.close()

# 输出文件名列表确认保存成功
print("✅ PNG 图保存至:")
for f in plot_files:
    print(f)

# ✅ 创建以“巴士线路 × 月份”为热力图的速度同比变化（2025 vs 2024）图

# 筛选 1–3 月份，2024 和 2025，weekday 且为 LCL/LTD 或 EXP
compare_df = combined_df[
    (combined_df['month_num'].isin([1, 2, 3])) &
    (combined_df['year'].isin([2024, 2025])) &
    (combined_df['day_type'] == 1) &
    (combined_df['trip_type'].isin(['LCL/LTD', 'EXP', 'SBS']))
].copy()

# 更新路线分类
compare_df['Route_Type'] = compare_df['route_id'].apply(classify_route)
compare_df = compare_df.dropna(subset=['Route_Type'])

# 添加 year-month 标签
compare_df['ym'] = compare_df['year'].astype(str) + '-' + compare_df['month_num'].astype(str)

# 每月每条路线的平均速度
monthly_speed = compare_df.groupby(['Route_Type', 'route_id', 'ym'])['average_speed'].mean().reset_index()

# 转换为透视表
pivot_speed = monthly_speed.pivot_table(index='route_id', columns='ym', values='average_speed')

# 计算每月同比变化（2025 vs 2024）
for m in ['1', '2', '3']:
    y25 = '2025-' + m
    y24 = '2024-' + m
    if y24 in pivot_speed.columns and y25 in pivot_speed.columns:
        pivot_speed[f'{m}月'] = ((pivot_speed[y25] - pivot_speed[y24]) / pivot_speed[y24]) * 100

# 提取速度变化列并标注类型
change_cols = [col for col in pivot_speed.columns if col.endswith('月')]
heatmap_data = pivot_speed[change_cols].copy()
heatmap_data['Route_Type'] = heatmap_data.index.map(lambda r: classify_route(r))

# 🎨 使用 seaborn 按每组生成热力图
for group in ['Local Only in CRZ', 'Local Crosses CRZ', 'Express to CRZ']:
    subset = heatmap_data[heatmap_data['Route_Type'] == group].drop(columns='Route_Type')
    plt.figure(figsize=(10, max(4, 0.4 * len(subset))))
    sns.heatmap(subset, annot=True, fmt=".1f", cmap='RdYlGn', center=0,
                cbar_kws={'label': '% Speed Change (2025 vs 2024)'})
    plt.title(f"{group} - Monthly Speed Change Heatmap (2025 vs 2024)")
    plt.xlabel("Month")
    plt.ylabel("Bus Route")
    plt.tight_layout()
    plt.show()

# 🔄 生成三组 × 2 时段（Off-Peak / Peak）共 6 幅热力图

# 准备数据源，只保留 1-3 月、2024/2025、weekday、trip_type 合法
filtered = combined_df[
    (combined_df['month_num'].isin([1, 2, 3])) &
    (combined_df['year'].isin([2024, 2025])) &
    (combined_df['day_type'] == 1) &
    (combined_df['trip_type'].isin(['LCL/LTD', 'EXP', 'SBS'])) &
    (combined_df['period'].isin(['Off-Peak', 'Peak']))
].copy()

# 加入标签
filtered['Route_Type'] = filtered['route_id'].apply(classify_route)
filtered = filtered.dropna(subset=['Route_Type'])
filtered['ym'] = filtered['year'].astype(str) + '-' + filtered['month_num'].astype(str)

# 创建空列表收集结果
heatmap_results = []

# 遍历 Off-Peak 和 Peak
for period in ['Off-Peak', 'Peak']:
    period_df = filtered[filtered['period'] == period]

    # 计算月度速度
    monthly_speed = period_df.groupby(['Route_Type', 'route_id', 'ym'])['average_speed'].mean().reset_index()
    pivot_speed = monthly_speed.pivot_table(index='route_id', columns='ym', values='average_speed')

    # 计算速度变化
    for m in ['1', '2', '3']:
        y25 = f'2025-{m}'
        y24 = f'2024-{m}'
        if y24 in pivot_speed.columns and y25 in pivot_speed.columns:
            pivot_speed[f'{m}月'] = ((pivot_speed[y25] - pivot_speed[y24]) / pivot_speed[y24]) * 100

    # 整理出结果并加标签
    change_cols = [col for col in pivot_speed.columns if col.endswith('月')]
    heatmap_data = pivot_speed[change_cols].copy()
    heatmap_data['Route_Type'] = heatmap_data.index.map(lambda r: classify_route(r))

    # 分组绘图
    for group in ['Local Only in CRZ', 'Local Crosses CRZ', 'Express to CRZ']:
        subset = heatmap_data[heatmap_data['Route_Type'] == group].drop(columns='Route_Type')
        plt.figure(figsize=(10, max(4, 0.4 * len(subset))))
        sns.heatmap(subset, annot=True, fmt=".1f", cmap='RdYlGn', center=0,
                    cbar_kws={'label': '% Speed Change (2025 vs 2024)'})
        plt.title(f"{group} - {period} - Monthly Speed Change Heatmap")
        plt.xlabel("Month")
        plt.ylabel("Bus Route")
        plt.tight_layout()
        plt.show()



# 🎯 生成 6 幅热力图：Route Group × Day Type (Weekday / Weekend)

# 筛选 2024/2025, LCL/LTD/EXP/SBS, Jan-Mar
daytype_df = combined_df[
    (combined_df['year'].isin([2024, 2025])) &
    (combined_df['month_num'].isin([1, 2, 3])) &
    (combined_df['trip_type'].isin(['LCL/LTD', 'EXP', 'SBS'])) &
    (combined_df['day_type'].isin([1, 2]))
].copy()

# 加上 route 分组标签、新日期列
daytype_df['Route_Type'] = daytype_df['route_id'].apply(classify_route)
daytype_df = daytype_df.dropna(subset=['Route_Type'])
daytype_df['ym'] = daytype_df['year'].astype(str) + '-' + daytype_df['month_num'].astype(str)

# 分为 weekday/weekend
for d_type in [1, 2]:
    d_label = "Weekday" if d_type == 1 else "Weekend"
    temp = daytype_df[daytype_df['day_type'] == d_type]

    # 按月和 route 计算平均速度
    monthly_speed = temp.groupby(['Route_Type', 'route_id', 'ym'])['average_speed'].mean().reset_index()
    pivot_speed = monthly_speed.pivot_table(index='route_id', columns='ym', values='average_speed')

    # 计算速度同比变化
    for m in ['1', '2', '3']:
        y24, y25 = f'2024-{m}', f'2025-{m}'
        if y24 in pivot_speed.columns and y25 in pivot_speed.columns:
            pivot_speed[f'{m}月'] = ((pivot_speed[y25] - pivot_speed[y24]) / pivot_speed[y24]) * 100

    # 抽取变化值
    change_cols = [col for col in pivot_speed.columns if col.endswith('月')]
    heatmap_data = pivot_speed[change_cols].copy()
    heatmap_data['Route_Type'] = heatmap_data.index.map(lambda r: classify_route(r))

    # 分组绘图
    for group in ['Local Only in CRZ', 'Local Crosses CRZ', 'Express to CRZ']:
        subset = heatmap_data[heatmap_data['Route_Type'] == group].drop(columns='Route_Type')
        if len(subset) == 0:
            continue
        plt.figure(figsize=(10, max(4, 0.4 * len(subset))))
        sns.heatmap(subset, annot=True, fmt=".1f", cmap='RdYlGn', center=0,
                    cbar_kws={'label': '% Speed Change (2025 vs 2024)'})
        plt.title(f"{group} - {d_label} - Monthly Speed Change Heatmap")
        plt.xlabel("Month")
        plt.ylabel("Bus Route")
        plt.tight_layout()
        plt.show()

# 🎯 生成 Route Type × Weekday + Peak 的热力图（共 3 张）

# 筛选 2024/2025, 1-3月, 周中 (day_type=1), Peak 时段, 合法 trip_type
wp_df = combined_df[
    (combined_df['year'].isin([2024, 2025])) &
    (combined_df['month_num'].isin([1, 2, 3])) &
    (combined_df['day_type'] == 1) &
    (combined_df['period'] == 'Peak') &
    (combined_df['trip_type'].isin(['LCL/LTD', 'EXP', 'SBS']))
].copy()

# 加上标签
wp_df['Route_Type'] = wp_df['route_id'].apply(classify_route)
wp_df = wp_df.dropna(subset=['Route_Type'])
wp_df['ym'] = wp_df['year'].astype(str) + '-' + wp_df['month_num'].astype(str)

# 按 Route+Month 平均速度
monthly_speed = wp_df.groupby(['Route_Type', 'route_id', 'ym'])['average_speed'].mean().reset_index()
pivot_speed = monthly_speed.pivot_table(index='route_id', columns='ym', values='average_speed')

# 计算速度变化
for m in ['1', '2', '3']:
    y24, y25 = f'2024-{m}', f'2025-{m}'
    if y24 in pivot_speed.columns and y25 in pivot_speed.columns:
        pivot_speed[f'{m}月'] = ((pivot_speed[y25] - pivot_speed[y24]) / pivot_speed[y24]) * 100

# 抽取变化数据并标注 Route 类型
change_cols = [col for col in pivot_speed.columns if col.endswith('月')]
heatmap_data = pivot_speed[change_cols].copy()
heatmap_data['Route_Type'] = heatmap_data.index.map(lambda r: classify_route(r))

# 🔥 绘图（每个 route group 一张图）
for group in ['Local Only in CRZ', 'Local Crosses CRZ', 'Express to CRZ']:
    subset = heatmap_data[heatmap_data['Route_Type'] == group].drop(columns='Route_Type')
    if len(subset) == 0:
        continue
    plt.figure(figsize=(10, max(4, 0.4 * len(subset))))
    sns.heatmap(subset, annot=True, fmt=".1f", cmap='RdYlGn', center=0,
                cbar_kws={'label': '% Speed Change (2025 vs 2024)'})
    plt.title(f"{group} - Weekday Peak - Monthly Speed Change Heatmap")
    plt.xlabel("Month")
    plt.ylabel("Bus Route")
    plt.tight_layout()
    plt.show()

import os
import seaborn as sns

# 创建保存目录
os.makedirs("charts", exist_ok=True)

def plot_monthly_comparison_by_period_annotated(data, label="All Periods"):
    import os
    os.makedirs("charts", exist_ok=True)  # 创建 charts 文件夹用于保存图像

    def compute_change(month):
        before = data[(data['year'] == 2024) & (data['month_num'] == month)]
        after = data[(data['year'] == 2025) & (data['month_num'] == month)]
        before_avg = before.groupby('New_Group')['average_speed'].mean()
        after_avg = after.groupby('New_Group')['average_speed'].mean()
        change = ((after_avg - before_avg) / before_avg) * 100
        return change.rename(f'{month}')

    jan = compute_change(1)
    feb = compute_change(2)
    mar = compute_change(3)
    comp_df = pd.concat([jan, feb, mar], axis=1)

    # 绘图
    ax = comp_df.T.plot(kind='bar', figsize=(10, 6))
    plt.title(f'2024 vs 2025 Monthly Speed Change (%) - {label}')
    plt.ylabel('Percent Change in Average Speed')
    plt.xlabel('month')
    plt.xticks(rotation=0)
    plt.axhline(0, color='gray', linestyle='--')
    plt.grid(axis='y')
    plt.legend(title='Route Group')

    # 添加百分比标签
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f%%', label_type='edge', fontsize=9)

    plt.tight_layout()

    # 保存图像
    filename = f"charts/barplot_{label.replace(' ', '_').replace('-', '')}.png"
    plt.savefig(filename, dpi=300)
    plt.close()
plot_monthly_comparison_by_period_annotated(filtered_all, label="All Periods")
plot_monthly_comparison_by_period_annotated(filtered_all[filtered_all['period'] == 'Off-Peak'], label="Off-Peak Only")
plot_monthly_comparison_by_period_annotated(filtered_all[filtered_all['period'] == 'Peak'], label="Peak Only")


import os
os.makedirs("charts", exist_ok=True)  # 创建 charts 文件夹保存图像

for period in ['Off-Peak', 'Peak']:
    period_df = filtered[filtered['period'] == period]

    # 计算月度平均速度
    monthly_speed = period_df.groupby(['Route_Type', 'route_id', 'ym'])['average_speed'].mean().reset_index()
    pivot_speed = monthly_speed.pivot_table(index='route_id', columns='ym', values='average_speed')

    # 计算同比变化（2025 vs 2024）
    for m in ['1', '2', '3']:
        y25 = f'2025-{m}'
        y24 = f'2024-{m}'
        if y24 in pivot_speed.columns and y25 in pivot_speed.columns:
            pivot_speed[f'{m}月'] = ((pivot_speed[y25] - pivot_speed[y24]) / pivot_speed[y24]) * 100

    # 抽取变动数据并标记路线类型
    change_cols = [col for col in pivot_speed.columns if col.endswith('月')]
    heatmap_data = pivot_speed[change_cols].copy()
    heatmap_data['Route_Type'] = heatmap_data.index.map(lambda r: classify_route(r))

    # 生成图像
    for group in ['Local Only in CRZ', 'Local Crosses CRZ', 'Express to CRZ']:
        subset = heatmap_data[heatmap_data['Route_Type'] == group].drop(columns='Route_Type')

        if subset.empty:
            print(f"⚠️ Skipped: {group} - {period} (no valid data)")
            continue

        plt.figure(figsize=(10, max(4, 0.4 * len(subset))))
        sns.heatmap(subset, annot=True, fmt=".1f", cmap='RdYlGn', center=0,
                    cbar_kws={'label': '% Speed Change (2025 vs 2024)'})
        plt.title(f"{group} - {period} - Monthly Speed Change Heatmap")
        plt.xlabel("Month")
        plt.ylabel("Bus Route")
        plt.tight_layout()

        # 保存为 PNG 图像
        filename = f"charts/heatmap_{group.replace(' ', '_')}_{period.replace('-', '')}.png"
        plt.savefig(filename, dpi=300)
        plt.close()