import rasterio
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles

input_raster = "prediction.tif"
output_cog = "prediction_cog.tif"

profile = cog_profiles.get("deflate")

cog_translate(
    input_raster,
    output_cog,
    profile,
    in_memory=True
)

print("✅ COG created")