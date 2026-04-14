import laspy
import numpy as np

# Create new LAS file
las = laspy.create(point_format=3, file_version="1.2")

# Example points
las.x = np.random.rand(100)
las.y = np.random.rand(100)
las.z = np.random.rand(100)

# Classification: 6 = building (standard LAS class)
las.classification = np.random.randint(0, 7, 100)

las.write("classified.las")

print("✅ LAS file saved")