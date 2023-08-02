import bpy

import bmesh

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

dns = bpy.app.driver_namespace

try:
    drawing = dns["viewport_drawing"]
except KeyError:
    from .visualizer import ViewportDrawing
    drawing = dns["viewport_drawing"] = ViewportDrawing()

class UGXSubsetsListActions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "ugx_subsets.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def random_color(self):
        from random import random
        return [random(), random(), random(), 1.0]

    def invoke(self, context, event):
        scene = context.scene
        idx = scene.active_subset

        try:
            item = scene.ugx_subsets[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scene.ugx_subsets) - 1:
                item_next = scene.ugx_subsets[idx+1].name
                scene.ugx_subsets.move(idx, idx+1)
                scene.ugx_properties.current_subset += 1
                self.report({'INFO'}, f'{item.name} moved to position {scene.ugx_properties.current_subset + 1}')

            elif self.action == 'UP' and idx >= 1:
                item_prev = scene.ugx_subsets[idx-1].name
                scene.ugx_subsets.move(idx, idx-1)
                scene.ugx_properties.current_subset -= 1
                self.report({'INFO'}, f'{item.name} moved to position {scene.ugx_properties.current_subset + 1}')

            elif self.action == 'REMOVE':
                item = scene.ugx_subsets[scene.active_subset]
                name = item.name

                if len(scene.ugx_subsets) == 1:
                    self.report({'ERROR'}, "At least one subset must be defined.")
                    return {"CANCELLED"}

                if scene.ugx_properties.current_subset == 0:
                    scene.ugx_properties.current_subset = 0
                else:
                    scene.ugx_properties.current_subset -= 1

                scene.ugx_subsets.remove(idx)
                self.report({'INFO'}, f'{name} removed')

        if self.action == 'ADD':
            item = scene.ugx_subsets.add()
            item.index = len(scene.ugx_subsets)-1
            item.name = f'Subset {len(scene.ugx_subsets) - 1}'
            item.color = self.random_color()
            scene.ugx_properties.current_subset = (len(scene.ugx_subsets)-1)
            self.report({'INFO'}, f'{item.name} added')

        return {"FINISHED"}


class UGXSubsetsAdditions(bpy.types.Operator):
    """Add Vertices/Edges/Faces to a subset"""
    bl_idname = "ugx.subset_action"
    bl_label = "Add Selected Vertices to Subset"
    bl_description = "Add Vertices/Edges/Faces to a subset"
    bl_options = {'REGISTER'}
    action: bpy.props.EnumProperty(
        items=(
            ('VERTICES', "Vertices", ""),
            ('EDGES', "Edges", ""),
            ('FACES', "Faces", "")))

    def invoke(self, context, event):
        # mode must be changed to object mode, to update the selection
        scene = bpy.context.scene

        if len(scene.ugx_subsets) == 0:
            self.report({'ERROR'}, "No subsets defined.")
            return {"CANCELLED"}

        # get selected vertices
        obj = context.active_object

        if "vertex_subset" not in obj.data.attributes and "edge_subset" not in obj.data.attributes and "face_subset" not in obj.data.attributes:
            self.report({'ERROR'}, "No subsets defined. Subsets not initialized?")
            return {"CANCELLED"}

        # enter object mode once to update the selection
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        match self.action:
            case 'VERTICES':
                bm.verts.ensure_lookup_table()
                subsets = bm.verts.layers.int["vertex_subset"]

                for v in obj.data.vertices:
                    if v.select:
                        bm.verts[v.index][subsets] = scene.active_subset

            case 'EDGES':
                bm.edges.ensure_lookup_table()
                subsets = bm.edges.layers.int["edge_subset"]

                for e in obj.data.edges:
                    if e.select:
                        bm.edges[e.index][subsets] = scene.active_subset

            case 'FACES':
                bm.faces.ensure_lookup_table()
                subsets = bm.faces.layers.int["face_subset"]

                for f in obj.data.polygons:
                    if f.select:
                        bm.faces[f.index][subsets] = scene.active_subset

                # update visualisation
                drawing.draw_faces(obj)


        bmesh.update_edit_mesh(obj.data)

        return {"FINISHED"}

class UGXSUBSETS_UL_Items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.1)
            split.label(text=f'{index}')
            split.prop(item, "name", text="", emboss=False, icon_value=icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

    def invoke(self, context, event):
        pass

class UGXSubset(PropertyGroup):
    name: StringProperty()
    index: IntProperty()
    color: FloatVectorProperty(name="Color", subtype='COLOR', size=4, min=0.0, max=1.0, default=(0.0, 0.0, 0.0, 1.0))

class UGXSubsetsProperties(PropertyGroup):
    view_check: BoolProperty(name="Show Subsets",
                             description="Enable/Disable Visibility of Subsets",
                             default=False)
    current_subset: IntProperty(name="Current Subset",
                                description="Index of Currently Selected Subset")

class UGXSubsetsIntitialize(Operator):
    """Initialize the Subset Property"""
    bl_idname = "ugx.subset_initialize"
    bl_label = "Initialize Subset Property"
    bl_description = "Initialize Subset Property"

    def execute(self, context):
        scene = bpy.context.scene
        obj = context.active_object

        if obj is None:
            self.report({'ERROR'}, "No object selected.")
            return {"CANCELLED"}

        if "vertex_subset" in obj.data.attributes and "edge_subset" in obj.data.attributes and "face_subset" in obj.data.attributes:
            self.report({'ERROR'}, "Subset property already exists.")
            return {"CANCELLED"}

        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        # create new attribute
        vertices = bm.verts.layers.int.new("vertex_subset")
        edges = bm.edges.layers.int.new("edge_subset")
        faces = bm.faces.layers.int.new("face_subset")

        bmesh.update_edit_mesh(obj.data)

        # add default subset
        if len(scene.ugx_subsets) == 0:
            item = scene.ugx_subsets.add()
            item.id = len(scene.ugx_subsets)
            item.name = 'Subset 0'
            item.color = (1.0, 0.0, 0.0, 1.0)
            scene.ugx_properties.current_subset = 0

        return {"FINISHED"}

class UGXSubsetsPanel(bpy.types.Panel):
    """Subset Panel for ugx files"""
    bl_idname = "OBJECT_PT_ugxsubsets"
    bl_label = ""
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='UGX Subsets')

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        obj = context.active_object

        row = layout.row()
        row.operator("ugx.subset_initialize", text="Initialize Subsets")

        row = layout.row()
        row.prop(scene.ugx_properties, "view_check", text="Show Subsets")

        # visualisation of subsets
        if scene.ugx_properties.view_check:
            if len(drawing.draw_handler) == 0:
                if obj.data.attributes.get("vertex_subset"):
                    drawing.create_draw_handler(obj)

                # show faces
                #drawing.draw_faces(obj)

        else:
            if len(drawing.draw_handler) > 0:
                for dh in drawing.draw_handler:
                    bpy.types.SpaceView3D.draw_handler_remove(dh, 'WINDOW')
                drawing.draw_handler.clear()

                # hide faces by setting viewport mode to solid
                bpy.context.space_data.shading.type = 'SOLID'

        # list of subsets
        row = layout.row()
        row.template_list("UGXSUBSETS_UL_Items", "ugx_subsets_def_list", scene, "ugx_subsets",
            scene, "active_subset", rows=3)

        col = row.column(align=True)
        col.operator(UGXSubsetsListActions.bl_idname, icon='ADD', text="").action = 'ADD'
        col.operator(UGXSubsetsListActions.bl_idname, icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator(UGXSubsetsListActions.bl_idname, icon='TRIA_UP', text="").action = 'UP'
        col.operator(UGXSubsetsListActions.bl_idname, icon='TRIA_DOWN', text="").action = 'DOWN'

        # add selected items to subset
        row = layout.row()
        row.operator(UGXSubsetsAdditions.bl_idname, text="Add Selected Vertices").action = 'VERTICES'
        row = layout.row()
        row.operator(UGXSubsetsAdditions.bl_idname, text="Add Selected Edges").action = 'EDGES'
        row = layout.row()
        row.operator(UGXSubsetsAdditions.bl_idname, text="Add Selected Faces").action = 'FACES'