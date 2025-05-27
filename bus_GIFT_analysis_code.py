# -*- coding: utf-8 -*-

import os
import json
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from haversine import haversine
from shapely.geometry import Point, Polygon


# Step 1: 加载 0407 文件夹内所有 JSON
import glob

data_folder = "bus_GIFT_API_data/0423_2025"
vehicle_files = sorted(glob.glob(os.path.join(data_folder, "vehicle_data_*.json")))

all_records = []
for file in vehicle_files:
    filename = os.path.basename(file)
    timestamp_str = filename.split("_")[2] + "_" + filename.split("_")[3].split(".")[0]
    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
    with open(file) as f:
        data = json.load(f)
        vehicles = data.get("Siri", {}).get("ServiceDelivery", {}).get("VehicleMonitoringDelivery", [{}])[0].get("VehicleActivity", [])
        for v in vehicles:
            journey = v.get("MonitoredVehicleJourney", {})
            record = {
                "timestamp": timestamp,
                "hour": timestamp.hour,
                "line": journey.get("PublishedLineName", [None])[0],
                "lat": journey.get("VehicleLocation", {}).get("Latitude"),
                "lon": journey.get("VehicleLocation", {}).get("Longitude"),
                "vehicle_id": journey.get("VehicleRef")
            }
            all_records.append(record)

df = pd.DataFrame(all_records)
df.dropna(subset=["lat", "lon", "line"], inplace=True)

# Step 2: 计算速度
df = df.sort_values(by=["vehicle_id", "timestamp"])
df["prev_lat"] = df.groupby("vehicle_id")["lat"].shift(1)
df["prev_lon"] = df.groupby("vehicle_id")["lon"].shift(1)
df["prev_time"] = df.groupby("vehicle_id")["timestamp"].shift(1)

df["distance_km"] = df.apply(
    lambda row: haversine((row["prev_lat"], row["prev_lon"]), (row["lat"], row["lon"])) if pd.notnull(row["prev_lat"]) else None,
    axis=1
)
df["time_diff_hr"] = (df["timestamp"] - df["prev_time"]).dt.total_seconds() / 3600
df["speed_kmh"] = df["distance_km"] / df["time_diff_hr"]

# Step 3: 区分 local 与 express routes
local_routes = {"M1", "M2", "M3", "M4", "M5", "M7", "M10", "M11", "M15", "M20", "M31", "M50", "M57", "M66", "M72", "M79", "M101", "M102", "M103", "Q32", "B39"}
express_routes = {"BxM1", "BxM2", "BxM3", "BxM4", "BxM6", "BxM7", "BxM18", "BM1", "BM2", "BM3", "BM4", "BM5", "X27", "X28", "X37", "X38",
                  "QM1", "QM2", "QM4", "QM5", "QM6", "QM7", "QM8", "QM10", "QM11", "QM12", "QM15", "QM16", "QM17", "QM18", "QM20", "QM21", "QM24",
                  "QM25", "QM31", "QM32", "QM34", "QM35", "QM36",
                  "SIM1", "SIM1C", "SIM3", "SIM3C", "SIM4", "SIM4C", "SIM4X", "SIM7", "SIM8", "SIM8X", "SIM9", "SIM10", "SIM11", "SIM15",
                  "SIM22", "SIM23", "SIM24", "SIM25", "SIM26", "SIM30", "SIM31", "SIM32", "SIM33", "SIM33C", "SIM34", "SIM35"}

df["route_type"] = df["line"].apply(lambda x: "local" if str(x) in local_routes else ("express" if str(x) in express_routes else "other"))

# Step 4: 绘图函数（通用）
def plot_speed_heatmap(data, title, filename):
    pivot = data.groupby(["line", "hour"])["speed_kmh"].mean().reset_index()
    heatmap = pivot.pivot(index="line", columns="hour", values="speed_kmh")
    plt.figure(figsize=(18, len(heatmap) * 0.3 + 2))
    sns.heatmap(heatmap, annot=True, fmt=".1f", cmap="RdYlGn")
    plt.title(title)
    plt.xlabel("Hour of Day")
    plt.ylabel("Bus Line")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"✅ {filename} saved.")

# Step 5: 绘图：local / express overall
plot_speed_heatmap(df[df["route_type"] == "local"], "Local Routes – Hourly Avg Speed (km/h)", "local_speed_hourly.png")
plot_speed_heatmap(df[df["route_type"] == "express"], "Express Routes – Hourly Avg Speed (km/h)", "express_speed_hourly.png")

# Step 6: 使用官方定义的CRZ边界CSV文件，创建Polygon并标记是否在CRZ内
from shapely.geometry import Polygon, Point
import ast

# CSV 文件路径
crz_csv_path = "bus_GIFT_API_data/MTA_Central_Business_District_Geofence__Beginning_June_2024_20250407.csv"


# 读取 CSV 中的 polygon 字符串
with open(crz_csv_path, "r") as f:
    lines = f.readlines()
    first_polygon_line = lines[1].strip()

# 清理 POLYGON 字符串格式
polygon_text = first_polygon_line.replace("POLYGON ((", "").replace("))", "")
coord_pairs = polygon_text.split(", ")
polygon_coords = [
    (float(pair.split(" ")[0].strip(" \"()")), float(pair.split(" ")[1].strip(" \"()")))
    for pair in coord_pairs
]

# 创建 shapely Polygon 对象
crz_polygon = Polygon(polygon_coords)

# 判断是否在CRZ内
df["in_crz"] = df.apply(lambda row: crz_polygon.contains(Point(row["lon"], row["lat"])), axis=1)

# Step 7: 分开画图 – local/express in CRZ and outside
plot_speed_heatmap(df[(df["route_type"] == "local") & (df["in_crz"])], "Local Routes – In CRZ", "local_in_crz.png")
plot_speed_heatmap(df[(df["route_type"] == "local") & (~df["in_crz"])], "Local Routes – Outside CRZ", "local_outside_crz.png")
plot_speed_heatmap(df[(df["route_type"] == "express") & (df["in_crz"])], "Express Routes – In CRZ", "express_in_crz.png")
plot_speed_heatmap(df[(df["route_type"] == "express") & (~df["in_crz"])], "Express Routes – Outside CRZ", "express_outside_crz.png")

# ✅ Step 8: 计算 Local / Express 每小时 CRZ in vs out 的速度百分比变化，并绘图

from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap

# ✅ 自定义红绿颜色映射：负值红色，正值绿色，无黄色
red_green_cmap = LinearSegmentedColormap.from_list("RedGreen", ["red", "white", "green"], N=256)

# ✅ 绘图函数
def plot_speed_pct_change_heatmap(data, title, filename):
    plt.figure(figsize=(20, 12))
    ax = sns.heatmap(
        data,
        annot=True,
        fmt=".1f",
        cmap=red_green_cmap,
        norm=TwoSlopeNorm(vmin=data.min().min(), vcenter=0, vmax=data.max().max()),
        linewidths=0.2,
        cbar_kws={'label': '% Speed Change (In vs Out CRZ)'}
    )
    plt.title(title, fontsize=16)
    plt.xlabel("Hour of Day", fontsize=14)
    plt.ylabel("Bus Route", fontsize=14)
    plt.figtext(0.5, -0.05, "Green = Faster inside CRZ, Red = Slower inside CRZ", ha='center', fontsize=12)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"✅ {filename} saved.")



# ✅ 计算每条线路每小时的 CRZ in vs out 平均速度百分比变化
def compute_speed_pct_change(df_subset):
    in_df = df_subset[df_subset["in_crz"]]
    out_df = df_subset[~df_subset["in_crz"]]

    avg_speed_in = in_df.groupby(["line", "hour"])["speed_kmh"].mean().reset_index(name="avg_speed_in")
    avg_speed_out = out_df.groupby(["line", "hour"])["speed_kmh"].mean().reset_index(name="avg_speed_out")

    merged = pd.merge(avg_speed_in, avg_speed_out, on=["line", "hour"], how="inner")
    merged["pct_change"] = (merged["avg_speed_in"] - merged["avg_speed_out"]) / merged["avg_speed_out"] * 100

    pivot = merged.pivot(index="line", columns="hour", values="pct_change")
    return pivot


# ✅ Express Routes 的速度变化
express_speed_change = compute_speed_pct_change(df[df["route_type"] == "express"])
plot_speed_pct_change_heatmap(
    express_speed_change,
    "Hourly % Speed Change (Express Routes) – CRZ In vs Out",
    "express_crz_speed_change_by_hour.png"
)

# ✅ Local Routes 的速度变化
local_speed_change = compute_speed_pct_change(df[df["route_type"] == "local"])
plot_speed_pct_change_heatmap(
    local_speed_change,
    "Hourly % Speed Change (Local Routes) – CRZ In vs Out",
    "local_crz_speed_change_by_hour.png"
)

#step 9
# ✅ 加载 2024 年 CSV 数据
csv_2024 = pd.read_csv("bus_GIFT_API_data/4-24_2024.csv")
csv_2024 = csv_2024.rename(columns=lambda x: x.strip().lower())
csv_2024["timestamp"] = pd.to_datetime(csv_2024["responsetimestamp"])
csv_2024["hour"] = csv_2024["timestamp"].dt.hour
csv_2024["in_crz"] = csv_2024.apply(lambda row: crz_polygon.contains(Point(row["longitude"], row["latitude"])), axis=1)

# ✅ 排序、计算速度字段
csv_2024 = csv_2024.sort_values(by=["vehicleref", "timestamp"])
csv_2024["prev_lat"] = csv_2024.groupby("vehicleref")["latitude"].shift(1)
csv_2024["prev_lon"] = csv_2024.groupby("vehicleref")["longitude"].shift(1)
csv_2024["prev_time"] = csv_2024.groupby("vehicleref")["timestamp"].shift(1)
csv_2024["distance_km"] = csv_2024.apply(
    lambda row: haversine((row["prev_lat"], row["prev_lon"]), (row["latitude"], row["longitude"])) if pd.notnull(row["prev_lat"]) else None,
    axis=1
)
csv_2024["time_diff_hr"] = (csv_2024["timestamp"] - csv_2024["prev_time"]).dt.total_seconds() / 3600
csv_2024["speed_kmh"] = csv_2024["distance_km"] / csv_2024["time_diff_hr"]


# ✅ 加载 2025 年 4 月 1 日 JSON 数据（只取 M1）
folder_2025 = "bus_GIFT_API_data/0423"
vehicle_files_2025 = sorted(glob.glob(os.path.join(folder_2025, "vehicle_data_*.json")))

all_2025 = []
for file in vehicle_files_2025:
    timestamp_str = file.split("_")[2] + "_" + file.split("_")[3].split(".")[0]
    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
    with open(file) as f:
        data = json.load(f)
        vehicles = data.get("Siri", {}).get("ServiceDelivery", {}).get("VehicleMonitoringDelivery", [{}])[0].get("VehicleActivity", [])
        for v in vehicles:
            journey = v.get("MonitoredVehicleJourney", {})
            if journey.get("PublishedLineName", [None])[0] == "M1":
                record = {
                    "timestamp": timestamp,
                    "hour": timestamp.hour,
                    "lat": journey.get("VehicleLocation", {}).get("Latitude"),
                    "lon": journey.get("VehicleLocation", {}).get("Longitude"),
                    "vehicle_id": journey.get("VehicleRef")
                }
                all_2025.append(record)


df_2025 = pd.DataFrame(all_2025)
if df_2025.empty:
    print("⚠️ No valid vehicle data found in JSON files.")
else:
    df_2025.dropna(subset=["lat", "lon"], inplace=True)

# ✅ 计算 2025 年速度
df_2025 = df_2025.sort_values(by=["vehicle_id", "timestamp"])
df_2025["prev_lat"] = df_2025.groupby("vehicle_id")["lat"].shift(1)
df_2025["prev_lon"] = df_2025.groupby("vehicle_id")["lon"].shift(1)
df_2025["prev_time"] = df_2025.groupby("vehicle_id")["timestamp"].shift(1)
df_2025["distance_km"] = df_2025.apply(
    lambda row: haversine((row["prev_lat"], row["prev_lon"]), (row["lat"], row["lon"])) if pd.notnull(row["prev_lat"]) else None,
    axis=1
)
df_2025["time_diff_hr"] = (df_2025["timestamp"] - df_2025["prev_time"]).dt.total_seconds() / 3600
df_2025["speed_kmh"] = df_2025["distance_km"] / df_2025["time_diff_hr"]
df_2025["in_crz"] = df_2025.apply(lambda row: crz_polygon.contains(Point(row["lon"], row["lat"])), axis=1)

# ✅ 添加线路名称字段（用于热力图）
csv_2024["line"] = "M1"
df_2025["line"] = "M1"

# ✅ 调用你之前写好的热力图函数
plot_speed_heatmap(csv_2024[csv_2024["in_crz"]], "2024 M1 ⬅️ In CRZ", "m1_2024_in_crz_speed.png")
plot_speed_heatmap(csv_2024[~csv_2024["in_crz"]], "2024 M1 ⬅️ Out CRZ", "m1_2024_out_crz_speed.png")
plot_speed_heatmap(df_2025[df_2025["in_crz"]], "2025 M1 ⬅️ In CRZ", "m1_2025_in_crz_speed.png")
plot_speed_heatmap(df_2025[~df_2025["in_crz"]], "2025 M1 ⬅️ Out CRZ", "m1_2025_out_crz_speed.png")


# Step 10: 输出 Local Bus Routes 的 In/Out CRZ 每小时速度和 % 变化

# 从 data_folder 提取日期字符串
data_date = os.path.basename(data_folder)  # e.g., "0413"

# 分别聚合：in CRZ 和 out CRZ
local_df = df[df["route_type"] == "local"]

local_in = local_df[local_df["in_crz"]].groupby(["line", "hour"])["speed_kmh"].mean().reset_index(name="speed_in_crz")
local_out = local_df[~local_df["in_crz"]].groupby(["line", "hour"])["speed_kmh"].mean().reset_index(name="speed_out_crz")

# 合并两个 dataframe
local_speed_comparison = pd.merge(local_in, local_out, on=["line", "hour"], how="inner")

# 计算百分比变化
local_speed_comparison["pct_change"] = (local_speed_comparison["speed_in_crz"] - local_speed_comparison["speed_out_crz"]) / local_speed_comparison["speed_out_crz"] * 100

# 导出 CSV，文件名中包含日期
output_csv_path = f"local_bus_crz_speed_comparison_{data_date}.csv"
local_speed_comparison.to_csv(output_csv_path, index=False)

print(f"✅ Local bus CRZ speed comparison exported to {output_csv_path}")

#step 11
data = {
    "hour": ["8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16"],
    "2024_IN_CRZ": [7.5, 6.8, 6.1, 5.9, 6.3, 6.3, 6.3, 6.3],
    "2025_IN_CRZ": [8.0, 6.1, 6.0, 6.0, 6.3, 6.2, 5.6, 6.5],
    "2024_OUT_CRZ": [9.1, 8.9, 8.3, 7.4, 7.7, 7.3, 7.3, 7.1],
    "2025_OUT_CRZ": [8.3, 7.7, 7.8, 7.1, 6.5, 6.6, 6.6, 6.0],
}

df = pd.DataFrame(data)

# 计算速度变化（2025 - 2024）
df["IN_CRZ_Change"] = df["2025_IN_CRZ"] - df["2024_IN_CRZ"]
df["OUT_CRZ_Change"] = df["2025_OUT_CRZ"] - df["2024_OUT_CRZ"]

# 保存为 CSV（可选）
df.to_csv("M1_CRZ_Comparison.csv", index=False)

# 打印结果表格
print(df)