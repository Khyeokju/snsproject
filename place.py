import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

# ----------------------------------------
# ✅ 데이터 불러오기
# ----------------------------------------

# 좌표 데이터
coord_df = pd.read_csv("place_coords_updated.csv")

# 분석 결과
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

# ----------------------------------------
# ✅ 읍면동 SHP
# ----------------------------------------

shp_path = "LSMD_ADM_SECT_UMD_50_202506.shp"
jeju_gdf = gpd.read_file(shp_path)
jeju_gdf = jeju_gdf.to_crs(epsg=4326)

# ----------------------------------------
# ✅ choropleth + markers → 하나의 FeatureGroup
# ----------------------------------------

def create_category_layer(category, gdf_points, gdf_boundary):
    # 해당 카테고리만 필터
    filtered = gdf_points[gdf_points["category"] == category]

    if len(filtered) == 0:
        # 아무 데이터가 없는 카테고리는 빈 FeatureGroup 반환
        return folium.FeatureGroup(name=category, show=False)

    # spatial join
    joined = gpd.sjoin(
        filtered,
        gdf_boundary,
        how="left",
        predicate="within"
    )

    # 읍면동별 카운트
    emd_counts = joined.groupby("EMD_NM").size().reset_index(name="num_points")

    # boundary와 merge
    choropleth_gdf = gdf_boundary.merge(
        emd_counts,
        on="EMD_NM",
        how="left"
    )
    choropleth_gdf["num_points"] = choropleth_gdf["num_points"].fillna(0)

    # GeoJson style
    def style_function(feature):
        n = feature["properties"]["num_points"]
        if n == 0:
            color = "#ffffff"
        elif n < 2:
            color = "#ffeda0"
        elif n < 5:
            color = "#feb24c"
        else:
            color = "#f03b20"
        return {
            "fillColor": color,
            "color": "gray",
            "weight": 0.5,
            "fillOpacity": 0.6,
        }

    # GeoJson layer
    geojson = folium.GeoJson(
        choropleth_gdf,
        name=f"{category} Choropleth",
        style_function=style_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=["EMD_NM", "num_points"],
            aliases=["읍면동", "장소수"],
            localize=True
        )
    )

    # FeatureGroup 생성 (✅ show=False 로 초기 비활성화)
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

# ----------------------------------------
# ✅ 지도 생성
# ----------------------------------------

m = folium.Map(location=[33.3617, 126.5292], zoom_start=10)

category_names = ["카페", "관광명소", "음식점", "문화시설", "기타"]

for cat in category_names:
    layer = create_category_layer(cat, all_points_gdf, jeju_gdf)
    layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

m.save("hotplace_map.html")

print("✅ hotplace_map.html 저장 완료!")
