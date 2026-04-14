import geopandas as gpd
from shapely.geometry import Polygon

# Example building polygons
polygons = [
    Polygon([(0,0), (1,0), (1,1), (0,1)]),
    Polygon([(2,2), (3,2), (3,3), (2,3)])
]

gdf = gpd.GeoDataFrame({
    "geometry": polygons,
    "type": ["building", "building"]
}, crs="EPSG:4326")

gdf.to_file("buildings.gpkg", driver="GPKG")

print("✅ GPKG created")