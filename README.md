# WIP: blender_io_mesh_ugx
Standalone Blender Addon to add import/export capabilities for UG4's ugx grid format.

Currently only 2D grids are supported, meaning the ugx export class currently only accounts for vertices, edges, triangles and quadrilaterals. Support for volumes will be added in the future.

For now it is possible to export ugx grids and to visualize subset data.

ToDos:
* correctly import ugx grids with subsets
* add support for volumes

# ugx file format
UG4's grids are stored using the ugx file format, which is derived from the xml file format.
Like most mesh storage formats vertices, edges, faces are stored. Additionally .ugx supports information about volumes abd user defined subsets, which are used to define different materials, boundary conditions, etc.

