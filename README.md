# 🚀 GeoAI_IIT_Tirupati  
## Deep Learning-Based Automated Feature Extraction from Drone Imagery for SVAMITVA Rural Mapping

---

## 📌 Project Overview  
The **SVAMITVA scheme** aims to provide rural property ownership records using drone-based surveys. However, converting raw drone imagery into usable GIS data remains largely manual.

Feature extraction tasks such as identifying building footprints, roads, and water bodies require extensive human digitization, making the process slow, labor-intensive, and error-prone. This bottleneck delays property card issuance and limits scalability across India’s ~6.4 lakh villages.

Additionally, most existing automated solutions are designed for urban or satellite imagery and fail to generalize to **rural Indian landscapes**, which are characterized by:
- Irregular settlement patterns  
- Diverse roof structures  
- Dense and heterogeneous layouts  

👉 This project proposes an **AI-driven, scalable GeoAI pipeline** that bridges the gap between drone data acquisition and GIS-ready outputs aligned with governance workflows.

---

## 🎯 Problem Statement  
Develop an automated and scalable system for extracting geospatial features (buildings, roads, water bodies, etc.) from high-resolution drone imagery and LiDAR data under the SVAMITVA scheme, reducing manual digitization effort and enabling faster generation of GIS-ready outputs compliant with government standards.

---

## 🏗️ Solution Architecture  

### 🔄 Pipeline Overview  


### 📥 Input  
- Drone Orthophotos (High-resolution RGB imagery)  
- LiDAR / Point Cloud Data  

### ⚙️ Processing  
**2D Semantic Segmentation:**
- U-Net  
- Mask R-CNN  
- Segment Anything Model (SAM)  

**3D Point Cloud Processing:**
- RandLA-Net  

### 🔗 Fusion Layer  
- Combine 2D segmentation + 3D structural features  
- Improve accuracy in dense rural areas  
- Extract attributes: building height, roof type  

### 📤 Output  
- 📦 GeoPackage (GPKG) → Vector layers  
- 🛰️ Cloud Optimized GeoTIFF (COG) → Raster outputs  

✔ OGC-compliant  
✔ Compatible with QGIS, ArcGIS, BhuNaksha, NIC systems

outputs/
│
├── raster/
│   ├── orthophoto_cog.tif
│   ├── building_mask_cog.tif
│
├── vector/
│   ├── buildings.gpkg
│   ├── roads.gpkg
│
├── pointcloud/
│   ├── classified.las
│
└── README.md

---

## ⚙️ Installation & Setup  

### 1️⃣ Clone Repository  
```bash
git clone https://github.com/your-username/GeoAI_IIT_Tirupati.git
cd GeoAI_IIT_Tirupati

conda create -n geoai python=3.10
conda activate geoai

pip install -r requirements.txt

Install Geospatial Libraries:
conda install -c conda-forge gdal rasterio geopandas fiona pdal
pip install laspy open3d
Google Collab Link:
https://colab.research.google.com/drive/1LD8__SY8oxMk1s-xewexxEo5iV0A_RhE?usp=sharing

