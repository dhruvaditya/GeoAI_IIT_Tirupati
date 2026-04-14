# 🚀 main.py
# End-to-End Pipeline: LiDAR → Building Segmentation → OGC Outputs

import os
import numpy as np
import laspy
import open3d as o3d
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
import geopandas as gpd
from shapely.geometry import Polygon
import rasterio
from rasterio.transform import from_origin
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles

# -----------------------------
# PARAMETERS
# -----------------------------
INPUT_LAS = "input.las"
OUTPUT_DIR = "outputs"

HEIGHT_THRESHOLD = 2.5
DBSCAN_EPS = 1.5
DBSCAN_MIN_POINTS = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)


# -----------------------------
# LOAD LiDAR
# -----------------------------
def load_lidar(path):
    las = laspy.read(path)
    points = np.vstack((las.x, las.y, las.z)).transpose()
    return points, las


# -----------------------------
# REMOVE GROUND
# -----------------------------
def remove_ground(points):
    ground_level = np.percentile(points[:, 2], 5)
    non_ground = points[points[:, 2] > ground_level + HEIGHT_THRESHOLD]
    return non_ground


# -----------------------------
# PLANARITY (ROOF DETECTION)
# -----------------------------
def compute_planarity(points, k=20):
    tree = o3d.geometry.KDTreeFlann(o3d.utility.Vector3dVector(points))
    planarity = []

    for i in range(len(points)):
        _, idx, _ = tree.search_knn_vector_3d(points[i], k)
        neighbors = points[idx]

        pca = PCA(n_components=3)
        pca.fit(neighbors)

        eigenvalues = np.sort(pca.explained_variance_)
        p = (eigenvalues[1] - eigenvalues[0]) / eigenvalues[2]
        planarity.append(p)

    return np.array(planarity)


# -----------------------------
# CLUSTER BUILDINGS
# -----------------------------
def extract_buildings(points):
    print("🔍 Computing planarity...")
    planarity = compute_planarity(points)

    roof_points = points[planarity > 0.3]

    print("🔗 Clustering buildings...")
    clustering = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_POINTS).fit(roof_points)
    labels = clustering.labels_

    buildings = []
    for label in set(labels):
        if label == -1:
            continue

        cluster = roof_points[labels == label]
        if len(cluster) < 100:
            continue

        buildings.append(cluster)

    print(f"🏠 Buildings detected: {len(buildings)}")
    return buildings


# -----------------------------
# SAVE LAS OUTPUT
# -----------------------------
def save_las(buildings):
    all_points = np.vstack(buildings)

    las = laspy.create(point_format=3, file_version="1.2")
    las.x = all_points[:, 0]
    las.y = all_points[:, 1]
    las.z = all_points[:, 2]

    # Classification: 6 = building
    las.classification = np.full(len(all_points), 6)

    output_path = os.path.join(OUTPUT_DIR, "buildings.las")
    las.write(output_path)

    print(f"✅ LAS saved: {output_path}")


# -----------------------------
# SAVE GPKG (VECTOR)
# -----------------------------
def save_gpkg(buildings):
    polygons = []

    for b in buildings:
        # Convex hull (simple footprint)
        hull = o3d.geometry.PointCloud(
            o3d.utility.Vector3dVector(b)
        ).compute_convex_hull()[0]

        vertices = np.asarray(hull.vertices)
        poly = Polygon(vertices[:, :2])  # use x,y only
        polygons.append(poly)

    gdf = gpd.GeoDataFrame({"geometry": polygons}, crs="EPSG:4326")

    output_path = os.path.join(OUTPUT_DIR, "buildings.gpkg")
    gdf.to_file(output_path, driver="GPKG")

    print(f"✅ GPKG saved: {output_path}")


# -----------------------------
# SAVE COG (RASTER MASK)
# -----------------------------
def save_cog(buildings):
    all_points = np.vstack(buildings)

    # Create simple grid
    x_min, y_min = all_points[:, 0].min(), all_points[:, 1].min()
    x_max, y_max = all_points[:, 0].max(), all_points[:, 1].max()

    resolution = 1.0
    width = int((x_max - x_min) / resolution)
    height = int((y_max - y_min) / resolution)

    raster = np.zeros((height, width))

    for p in all_points:
        x_idx = int((p[0] - x_min) / resolution)
        y_idx = int((p[1] - y_min) / resolution)

        if 0 <= x_idx < width and 0 <= y_idx < height:
            raster[y_idx, x_idx] = 1

    transform = from_origin(x_min, y_max, resolution, resolution)

    temp_tif = os.path.join(OUTPUT_DIR, "temp.tif")
    cog_path = os.path.join(OUTPUT_DIR, "buildings_cog.tif")

    with rasterio.open(
        temp_tif,
        "w",
        driver="GTiff",
        height=raster.shape[0],
        width=raster.shape[1],
        count=1,
        dtype=raster.dtype,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(raster, 1)

    profile = cog_profiles.get("deflate")
    cog_translate(temp_tif, cog_path, profile, in_memory=True)

    print(f"✅ COG saved: {cog_path}")


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def main():
    print("🚀 Starting Building Segmentation Pipeline")

    points, _ = load_lidar(INPUT_LAS)
    print(f"📊 Total points: {len(points)}")

    non_ground = remove_ground(points)
    print(f"🌍 Non-ground points: {len(non_ground)}")

    buildings = extract_buildings(non_ground)

    if len(buildings) == 0:
        print("❌ No buildings detected")
        return

    save_las(buildings)
    save_gpkg(buildings)
    save_cog(buildings)

    print("🎉 Pipeline completed successfully!")


if __name__ == "__main__":
    main()