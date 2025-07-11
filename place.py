import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

# 좌표 데이터
coord_df = pd.read_csv("place_coords_updated.csv")

df = pd.read_csv("jeju_analysis_summary.csv")

geo_row = df[df["category"] == "geo_places"]["result"].values[0]

place_counts = []
for item in geo_row.split(","):
    if item.strip() == "":
        continue
    name, count = item.strip().split(":")
    place_counts.append({
        "place_name": name.strip(),
        "MentionCount": int(count.strip())
    })

geo_df = pd.DataFrame(place_counts)

# 병합
merged_df = pd.merge(
    coord_df,
    geo_df,
    on="place_name",
    how="left"
)

merged_df = merged_df.dropna(subset=["latitude", "longitude"])
merged_df["MentionCount"] = merged_df["MentionCount"].fillna(0).astype(int)
merged_df["category"] = merged_df["category"].fillna("기타")

# 카테고리 통합
category_mapping = {
    "시장": "문화시설",
    "숙박": "문화시설",
    "항구": "관광명소"
}
merged_df["category"] = merged_df["category"].replace(category_mapping)

# 좌표 → GeoDataFrame
geometry = [Point(float(x), float(y)) for x, y in zip(merged_df["longitude"], merged_df["latitude"])]
all_points_gdf = gpd.GeoDataFrame(merged_df, geometry=geometry, crs="EPSG:4326")

shp_path = "LSMD_ADM_SECT_UMD_50_202506.shp"
jeju_gdf = gpd.read_file(shp_path, encoding='euc-kr')
jeju_gdf = jeju_gdf.to_crs(epsg=4326)

region_mapping = {
    # ────────────── 제주시 ──────────────
    ("건입동", None): "제주시",
    ("이도일동", None): "제주시",
    ("이도이동", None): "제주시",
    ("삼도일동", None): "제주시",
    ("삼도이동", None): "제주시",
    ("일도일동", None): "제주시",
    ("일도이동", None): "제주시",
    ("용담일동", None): "제주시",
    ("용담이동", None): "제주시",
    ("용담삼동", None): "제주시",
    ("오라일동", None): "제주시",
    ("오라이동", None): "제주시",
    ("오라삼동", None): "제주시",
    ("연동", None): "제주시",
    ("화북일동", None): "제주시",
    ("화북이동", None): "제주시",
    ("도남동", None): "제주시",
    ("도련일동", None): "제주시",
    ("도련이동", None): "제주시",
    ("아라일동", None): "제주시",
    ("아라이동", None): "제주시",
    ("영평동", None): "제주시",
    ("봉개동", None): "제주시",
    ("오등동", None): "제주시",
    ("외도일동", None): "제주시",
    ("외도이동", None): "제주시",
    ("이호일동", None): "제주시",
    ("이호이동", None): "제주시",
    ("내도동", None): "제주시",
    ("용강동", None): "제주시",
    ("회수동", None): "제주시",
    ("회천동", None): "제주시",
    ("해안동", None): "제주시",
    ("도두일동", None): "제주시",
    ("도두이동", None): "제주시",
    ("노형동", None): "제주시",
    ("월평동", 118): "제주시",     # 제주시 월평동
    # ────────────── 제주시 동부 ──────────────
    ("조천읍", None): "제주시 동부",
    ("구좌읍", None): "제주시 동부",
    ("우도면", None): "제주시 동부",
    ("삼양일동", None): "제주시 동부",
    ("삼양이동", None): "제주시 동부",
    ("삼양삼동", None): "제주시 동부",
    ("추자면", None): "제주시 동부",
    # ────────────── 제주시 서부 ──────────────
    ("애월읍", None): "제주시 서부",
    ("한림읍", None): "제주시 서부",
    ("한경면", None): "제주시 서부",
    ("도평동", None): "제주시 서부",

    # ────────────── 서귀포시 ──────────────
    ("서귀동", None): "서귀포시",
    ("중문동", None): "서귀포시",
    ("서호동", None): "서귀포시",
    ("서홍동", None): "서귀포시",
    ("동홍동", None): "서귀포시",
    ("신효동", None): "서귀포시",
    ("상효동", None): "서귀포시",
    ("보목동", None): "서귀포시",
    ("토평동", None): "서귀포시",
    ("호근동", None): "서귀포시",
    ("강정동", None): "서귀포시",
    ("대포동", None): "서귀포시",
    ("영남동", None): "서귀포시",
    ("월평동", 80): "서귀포시",    # 서귀포시 월평동
    ("도순동", None): "서귀포시",
    ("법환동", None): "서귀포시",
    ("하원동", None): "서귀포시",
    ("하효동", None): "서귀포시",
    ("회수동", None): "서귀포시",
    # ────────────── 서귀포시 동부 ──────────────
    ("성산읍", None): "서귀포시 동부",
    ("표선면", None): "서귀포시 동부",
    ("남원읍", None): "서귀포시 동부",
    # ────────────── 서귀포시 서부 ──────────────
    ("안덕면", None): "서귀포시 서부",
    ("대정읍", None): "서귀포시 서부",
    ("색달동", None): "서귀포시 서부",
    ("상예동", None): "서귀포시 서부",
    ("하예동", None): "서귀포시 서부",
}

jeju_gdf = gpd.read_file(shp_path, encoding='euc-kr')
jeju_gdf = jeju_gdf.to_crs(epsg=4326)

def map_region(row):
    key = (row["EMD_NM"], row["SGG_OID"])
    if key in region_mapping:
        return region_mapping[key]
    return region_mapping.get((row["EMD_NM"], None), "기타")

jeju_gdf["REGION_GROUP"] = jeju_gdf.apply(map_region, axis=1)

# REGION_GROUP 단위 dissolve
jeju_region_gdf = jeju_gdf.dissolve(
    by="REGION_GROUP", 
    as_index=False
)
missing_regions = jeju_gdf[
    jeju_gdf["REGION_GROUP"].isnull() | (jeju_gdf["REGION_GROUP"] == "기타")
]

def create_category_layer(category, gdf_points, gdf_boundary, gdf_regions):
    # 해당 카테고리만 필터
    filtered = gdf_points[gdf_points["category"] == category]

    if len(filtered) == 0:
        return folium.FeatureGroup(name=category, show=False)

    # Spatial Join → REGION_GROUP
    joined = gpd.sjoin(
        filtered,
        gdf_boundary[["geometry", "REGION_GROUP"]],
        how="left",
        predicate="within"
    )

    # REGION_GROUP별 개수 집계
    region_counts = joined.groupby("REGION_GROUP").size().reset_index(name="num_points")

    total_points = region_counts["num_points"].sum()
    if total_points == 0:
        total_points = 1

    region_counts["ratio"] = region_counts["num_points"] / total_points

    # REGION_GROUP별 Choropleth geometry와 merge
    choropleth_gdf = gdf_regions.merge(
        region_counts,
        on="REGION_GROUP",
        how="left"
    )
    choropleth_gdf["num_points"] = choropleth_gdf["num_points"].fillna(0)
    choropleth_gdf["ratio"] = choropleth_gdf["ratio"].fillna(0)

    # 스타일 함수
    def style_function(feature):
        r = feature["properties"]["ratio"]
        if r == 0:
            color = "#ffffff"
        elif r < 0.05:
            color = "#ffeda0"
        elif r < 0.15:
            color = "#feb24c"
        elif r < 0.30:
            color = "#f03b20"
        else:
            color = "#bd0026"
        return {
            "fillColor": color,
            "color": "gray",
            "weight": 0.5,
            "fillOpacity": 0.6,
        }

    geojson = folium.GeoJson(
        choropleth_gdf,
        name=f"{category} Choropleth",
        style_function=style_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=["REGION_GROUP", "num_points", "ratio"],
            aliases=["권역", "점수", "비율"],
            localize=True,
            labels=True,
            sticky=False
        )
    )

    group = folium.FeatureGroup(name=category, show=False)
    geojson.add_to(group)

    # 마커 추가
    for _, row in filtered.iterrows():
        place = row["place_name"]
        lat = float(row["latitude"])
        lon = float(row["longitude"])
        count = row["MentionCount"]
        address = row["address"]

        popup_text = f"<b>{place}</b><br>언급 횟수: {count}<br>주소: {address}<br>카테고리: {category}"
        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=300)
        )
        marker.add_to(group)

    return group

m = folium.Map(location=[33.3617, 126.5292], zoom_start=11)

category_names = ["카페", "관광명소", "음식점", "문화시설", "기타"]

for cat in category_names:
    layer = create_category_layer(cat, all_points_gdf, jeju_gdf, jeju_region_gdf)
    layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

m.save("hotplace_map.html")

print("hotplace_map.html 저장 완료")