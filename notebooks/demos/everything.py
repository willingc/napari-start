"""
Synthetic 4D multilayer (time, z, y, x)
========================================

Display synthetic 4D sample data across time and space:
``(time, z, y, x)``.

The spatial volume (z, y, x) contains three continuously varying image
channels (spots, fibers, rings), a 4-label segmentation, 16 tracked
trajectories, and decorative shapes.

.. tags:: visualization-nD, visualization-advanced, layers
"""

from __future__ import annotations

import napari
import numpy as np
from napari.utils.colormaps import DirectLabelColormap

AXIS_LABELS = ('time', 'z', 'y', 'x')
IMAGE_SHAPE = (16, 24, 160, 192)
LAYER_SCALE = (1, 2.0, 1.0, 1.0)
LAYER_UNITS = ('second', 'micrometer', 'micrometer', 'micrometer')
OPENING_SLICE = (0,)


def make_coordinate_grids() -> tuple[np.ndarray, ...]:
    """Return broadcast coordinate arrays for four axes (time, z, y, x)."""
    n_time, n_z, n_y, n_x = IMAGE_SHAPE

    time = np.arange(n_time, dtype=np.float32)[:, None, None, None]
    z = np.linspace(-1.0, 1.0, n_z, dtype=np.float32)[None, :, None, None]
    y = np.linspace(-1.0, 1.0, n_y, dtype=np.float32)[None, None, :, None]
    x = np.linspace(-1.15, 1.15, n_x, dtype=np.float32)[None, None, None, :]
    return time, z, y, x


def normalize_layers(*layers: np.ndarray) -> tuple[np.ndarray, ...]:
    """Normalize all layers to [0, 1] using their shared maximum."""
    max_value = max(float(layer.max()) for layer in layers)
    normalized = [(layer / max_value).astype(np.float32) for layer in layers]
    return tuple(normalized)


def _downsample_spatial(arr: np.ndarray, factor: int) -> np.ndarray:
    """Downsample the last 3 spatial dims (z, y, x) by *factor* using local mean."""
    *leading, nz, ny, nx = arr.shape
    nz_out, ny_out, nx_out = nz // factor, ny // factor, nx // factor
    return arr.reshape(*leading, nz_out, factor, ny_out, factor, nx_out, factor).mean(
        axis=(-5, -3, -1)
    )


def _spot_positions(time_idx: int, spot_id: int) -> tuple[int, int, int]:
    """Return (z, y, x) voxel indices for a spot.

    Each *spot_id* (0‑15) follows a unique trajectory through the volume.
    """
    n_time, n_z, n_y, n_x = IMAGE_SHAPE
    tf = time_idx / max(n_time - 1, 1)
    phase = spot_id * np.pi / 8

    z_pos = 0.25 * np.sin(tf * np.pi + phase * 0.5)
    y_pos = -0.35 + 0.5 * tf + 0.30 * np.cos(phase)
    x_pos = 0.35 - 0.5 * tf + 0.30 * np.sin(phase * 0.7)

    z_idx = int(np.clip(np.round((z_pos + 1) * 0.5 * (n_z - 1)), 0, n_z - 1))
    y_idx = int(np.clip(np.round((y_pos + 1) * 0.5 * (n_y - 1)), 0, n_y - 1))
    x_idx = int(np.clip(np.round((x_pos + 1.15) / 2.3 * (n_x - 1)), 0, n_x - 1))
    return z_idx, y_idx, x_idx


def make_image_layers() -> tuple[dict[str, list[np.ndarray]], np.ndarray]:
    """Build three 4D image channels as multiscale pyramids, plus labels."""
    time, z, y, x = make_coordinate_grids()
    n_time, n_z, n_y, n_x = IMAGE_SHAPE

    time_fraction = time / max(n_time - 1, 1)
    time_phase = time_fraction * np.pi

    # ---- Accumulate multiple moving spots (sum of Gaussians) -----------
    spots = np.zeros(IMAGE_SHAPE, dtype=np.float32)
    for sid in range(8):
        phase = sid * np.pi / 8
        sz = 0.25 * np.sin(time_phase + phase * 0.5)
        sy = -0.35 + 0.5 * time_fraction + 0.30 * np.cos(phase)
        sx = 0.35 - 0.5 * time_fraction + 0.30 * np.sin(phase * 0.7)
        spots += np.exp(-(((z - sz) / 0.25) ** 2 + ((y - sy) / 0.18) ** 2 + ((x - sx) / 0.18) ** 2))

    # ---- Core (central sphere that pulses) -----------------------------
    core_radius = np.sqrt((0.85 * z) ** 2 + y**2 + x**2)
    core = np.exp(-(core_radius**2) / 0.18) * (0.85 + 0.15 * np.cos(time_phase))

    # ---- Shell (concentric shell around core) --------------------------
    shell = np.exp(-((core_radius - 0.48) ** 2) / 0.02)
    shell = shell * (0.85 + 0.15 * np.sin(time_phase + np.pi / 4))

    # ---- Fibers (stripe pattern rotating with time) --------------------
    theta = time_phase / 3
    fibers = 0.5 + 0.5 * np.cos(10 * np.pi * (np.cos(theta) * x + np.sin(theta) * y) + time_phase)
    fibers = fibers * np.exp(-(z**2) / 0.42)

    # ---- Rings (concentric ring pattern with radial fade) --------------
    r_rings = np.sqrt(x**2 + y**2 + (0.75 * z) ** 2)
    rings = 0.5 + 0.5 * np.cos(16 * np.pi * r_rings - 1.5 * time_phase)
    rings = rings * (1 - np.exp(-4 * r_rings))  # fade to 0 at center
    rings = rings * np.exp(-(z**2) / 0.65)

    # ---- Fiducial (static marker) --------------------------------------
    fiducial = ((np.abs(y + 0.75) < 0.05) & (np.abs(x + 0.82) < 0.05)).astype(np.float32)
    fiducial = fiducial * np.exp(-((z - 0.6 * np.sin(time_phase)) ** 2) / 0.03)

    # ---- Blend channels ------------------------------------------------
    channel_0 = 0.12 + 0.75 * spots + 0.18 * core
    channel_1 = 0.08 + 0.55 * fibers * (0.3 + 0.7 * core) + 0.2 * spots
    channel_2 = 0.05 + 0.45 * shell + 0.35 * rings + 0.4 * fiducial

    spots_ch, fibers_ch, rings_ch = normalize_layers(channel_0, channel_1, channel_2)

    def _pyramid(arr: np.ndarray) -> list[np.ndarray]:
        return [arr, _downsample_spatial(arr, 2), _downsample_spatial(arr, 4)]

    image_layers = {
        'spots': _pyramid(spots_ch),
        'fibers': _pyramid(fibers_ch),
        'rings': _pyramid(rings_ch),
    }

    # ---- Labels from thresholds ----------------------------------------
    shell_mask = (shell > 0.5) & ((x > 0.15) | (y > 0.15))
    core_mask = (core > 0.6) & ~shell_mask
    spot_mask = (spots > 0.72) & (core > 0.15) & (x < -0.1) & (y < -0.1)
    fiber_mask = (fibers > 0.88) & (core > 0.22) & (x < -0.1) & (y > 0.15)

    labels = np.zeros(IMAGE_SHAPE, dtype=np.uint8)
    labels[core_mask] = 1
    labels[shell_mask] = 2
    labels[spot_mask] = 3
    labels[fiber_mask] = 4

    return image_layers, labels


def make_tracks_data() -> tuple[np.ndarray, dict, dict]:
    """Generate 16 tracks through (z, y, x) over time.

    Returns
    -------
    data : np.ndarray, shape (128, 5)
        Columns: [track_id, t, z, y, x] for 8 time points × 16 tracks.
    features : dict
        Per-vertex feature dict with 'track_id'.
    graph : dict
        Empty.
    """
    n_time = IMAGE_SHAPE[0]
    rows = []
    for spot_id in range(16):
        for time_idx in range(n_time):
            z, y, x = _spot_positions(time_idx, spot_id)
            rows.append([spot_id, time_idx, z, y, x])
    data = np.array(rows, dtype=float)
    features = {'track_id': data[:, 0].copy()}
    return data, features, {}


def iter_shapes():
    """Yield (vertices, shape_type) for each shape.

    Three decorative shapes at (angle=0, time=0), visible at the
    opening slice.  Each is a single z-slice polygon with a small
    z-extent so it's visible in 3D.
    """
    _, n_z, n_y, n_x = IMAGE_SHAPE
    mid_z, mid_y, mid_x = n_z // 2, n_y // 2, n_x // 2
    off = 30

    # Rectangle 1
    yield (
        np.array(
            [
                [0, mid_z, mid_y - off - 10, mid_x - off - 10],
                [0, mid_z, mid_y - off - 10, mid_x - off + 10],
                [0, mid_z, mid_y - off + 10, mid_x - off + 10],
                [0, mid_z, mid_y - off + 10, mid_x - off - 10],
            ]
        ),
        'rectangle',
    )

    # Ellipse
    yield (
        np.array(
            [
                [0, mid_z, mid_y + off - 8, mid_x + off - 12],
                [0, mid_z, mid_y + off - 8, mid_x + off + 12],
                [0, mid_z, mid_y + off + 8, mid_x + off + 12],
                [0, mid_z, mid_y + off + 8, mid_x + off - 12],
            ]
        ),
        'ellipse',
    )

    # Rectangle 2
    yield (
        np.array(
            [
                [0, mid_z, mid_y + 10, mid_x - off + 10],
                [0, mid_z, mid_y + 10, mid_x - off + 26],
                [0, mid_z, mid_y + 26, mid_x - off + 26],
                [0, mid_z, mid_y + 26, mid_x - off + 10],
            ]
        ),
        'rectangle',
    )


def make_shapes() -> tuple[list[np.ndarray], list[str]]:
    """Collect all shapes and their type strings from `iter_shapes`."""
    shapes = []
    shape_types = []
    for shape_data, shape_type in iter_shapes():
        shapes.append(shape_data)
        shape_types.append(shape_type)
    return shapes, shape_types


image_layers, labels = make_image_layers()
tracks, track_features, track_graph = make_tracks_data()
shapes, shape_types = make_shapes()

viewer = napari.Viewer(ndisplay=3)

# -- Multiscale image channels -------------------------------------------
for ch_name, ch_data, cmap, blend in (
    ('spots', image_layers['spots'], 'yellow', 'translucent_no_depth'),
    ('fibers', image_layers['fibers'], 'magenta', 'additive'),
    ('rings', image_layers['rings'], 'cyan', 'additive'),
):
    layer = viewer.add_image(
        ch_data,
        name=ch_name,
        colormap=cmap,
        blending=blend,
        opacity=1,
        scale=LAYER_SCALE,
        units=LAYER_UNITS,
        multiscale=True,
    )
    layer.locked_data_level = 0  # not an add_image arg

# set contrast limits, doesn't work with async on
viewer.layers['spots'].contrast_limits = (0.05, 1)
viewer.layers['fibers'].contrast_limits = (0.04, 0.3)
viewer.layers['rings'].contrast_limits = (0.05, 0.7)

viewer.add_labels(
    labels,
    name='labels',
    colormap=DirectLabelColormap(
        color_dict={
            0: 'transparent',
            1: 'red',
            2: 'orange',
            3: 'blue',
            4: 'white',
            None: 'gray',
        }
    ),
    rendering='iso_categorical',
    opacity=0.6,
    scale=LAYER_SCALE,
    units=LAYER_UNITS,
)

# -- Track vertices as points (4D: time, z, y, x) -----------------------
track_vertices = tracks[:, 1:]  # [t, z, y, x]
viewer.add_points(
    track_vertices,
    name='track vertices',
    features=track_features,
    face_color='track_id',
    face_colormap='husl',
    size=6,
    border_color='black',
    border_width=0.15,
    opacity=0.8,
    scale=LAYER_SCALE,
    units=LAYER_UNITS,
)

# -- Tracks layer: 16 trajectories through (z,y,x) over time -------------
viewer.add_tracks(
    tracks,
    features=track_features,
    graph=track_graph,
    name='tracks',
    opacity=0.7,
    tail_width=3,
    tail_length=3,
    scale=LAYER_SCALE,
    units=LAYER_UNITS,
)

# -- Shapes layer --------------------------------------------------------
_shape_colors = []
for st in shape_types:
    _shape_colors.append('cyan' if st == 'ellipse' else 'white' if st == 'path' else 'orange')

viewer.add_shapes(
    shapes,
    shape_type=shape_types,
    name='shapes',
    edge_color=_shape_colors,
    face_color=_shape_colors,
    opacity=0.6,
    edge_width=4,
    scale=LAYER_SCALE,
    units=LAYER_UNITS,
)

viewer.dims.axis_labels = AXIS_LABELS
for axis, value in enumerate(OPENING_SLICE):
    viewer.dims.set_point(axis=axis, value=value)

viewer.axes.visible = True
viewer.floating_axes.visible = True
viewer.scale_bar.visible = True
viewer.camera.angles = (20, -10, 145)

for layer in viewer.layers:
    if hasattr(layer, 'colorbar'):
        layer.colorbar.visible = True

viewer.fit_to_view()

if __name__ == '__main__':
    napari.run()
