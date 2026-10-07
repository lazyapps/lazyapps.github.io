"""Export the editable, packed FondFont model without altering source artwork."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'scripts/assets/fondfont/blender-v2'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'factory.blend'))
# Preserve complete packed original imagegen textures and all native assembly roots.
bpy.ops.export_scene.gltf(filepath=str(OUT/'factory-raw.glb'),export_format='GLB',export_apply=True,export_cameras=False,export_lights=False,export_animations=False,export_extras=True,export_image_format='WEBP',export_image_quality=92)
