bl_info = {
    "name": "ugx Import/Export",
    "author": "Niklas Conen (nordegraf)",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Export > ugx (.ugx)",
    "description": "Export mesh to UG4 grid format (ugx)",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export"
}

if "bpy" in locals():
    import importlib
    modules = [ugx_io, visualizer, subsets]

    for module in modules:
        importlib.reload(module)
else:
    from . import ugx_io
    from . import visualizer
    from . import subsets

from io_ugx.visualizer import ViewportDrawing
from io_ugx.ugx_io import UGXExporter, UGXImporter
from io_ugx.subsets import UGXSubsetsListActions, UGXSubsetsAdditions, UGXSUBSETS_UL_Items, UGXSubset, UGXSubsetsProperties, UGXSubsetsPanel, UGXSubsetsIntitialize

import bpy
from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty,
                       FloatVectorProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

def menu_func_export(self, context):
    self.layout.operator(UGXExporter.bl_idname, text="UG4 Grid (.ugx)")

def menu_func_import(self, context):
    self.layout.operator(UGXImporter.bl_idname, text="UG4 Grid (.ugx)")

classes = (
    UGXSubsetsListActions,
    UGXSubsetsAdditions,
    UGXSUBSETS_UL_Items,
    UGXSubset,
    UGXSubsetsProperties,
    UGXSubsetsPanel,
    UGXSubsetsIntitialize,
    UGXExporter,
    UGXImporter
)

def register():
    dns = bpy.app.driver_namespace
    dns["viewport_drawing"] = ViewportDrawing()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ugx_subsets = CollectionProperty(type=UGXSubset)
    bpy.types.Scene.ugx_properties = PointerProperty(type=UGXSubsetsProperties)
    bpy.types.Scene.active_subset = IntProperty(default=1)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    del bpy.types.Scene.ugx_subsets
    del bpy.types.Scene.ugx_properties
    del bpy.types.Scene.active_subset

    dns = bpy.app.driver_namespace

    for dh in dns["viewport_drawing"].draw_handler:
        bpy.types.SpaceView3D.draw_handler_remove(dh, 'WINDOW')


if __name__ == "__main__":
    register()
