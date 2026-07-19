# /// script
# dependencies = [
#   "napari[pyqt6,optional]",
#   "dask[array]",
# ]
# ///

"""Open the WM4196 PCA demo and keep the explanation in comments.

From: https://github.com/jni/napari-demos/tree/main/WM4196

Important idea:
this is not one tomogram changing over time.

Instead, the array has shape `(50, 10, 48, 48, 48)` and means:

- axis 0: principal component number
- axis 1: coefficient bin along that component
- axes 2-4: z, y, x of the reconstructed 3D volume

So each 3D volume is a "spectral average" summarizing many particles.
"""

import dask.array as da
import napari

DATA_URL = 'https://data.napari.dev/dynamo-pca.zarr'

volumes = da.from_zarr(DATA_URL)

viewer = napari.Viewer()
layer = viewer.add_image(
    volumes,
    name='spectral averages',
    rendering='attenuated_mip',
    colormap='gray',
)

# Start in the middle coefficient bin so the first view is representative.
viewer.dims.axis_labels = ('CoE', 'PC', 'Z', 'Y', 'X')
# viewer.dims.ndisplay = 3
viewer.dims.set_point(1, 1)
viewer.dims.set_point(0, 2)
viewer.axes.visible = True
viewer.scale_bar.visible = True
viewer.scale_bar.unit = 'pixel'
viewer.camera.angles = (20, -35, 110)
layer.reset_contrast_limits()

if __name__ == '__main__':
    napari.run()
