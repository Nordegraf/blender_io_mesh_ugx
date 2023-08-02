import bpy
import bmesh

from lxml import etree


class UGXExporter(bpy.types.Operator):
    """Exporter class for the UGX format in Blender."""

    bl_idname: str = "export.ugx"
    bl_label: str = "Export UGX"
    bl_options: str = {'REGISTER', 'UNDO'}

    def add_vertices(self, obj: bpy.types.Object, grid: etree.Element) -> None:
        """Adds vertices to the grid element in the ugx file.

        Args:
            obj (bpy.types.Object): The object to export.
            grid (lxml.etree.Element): The grid element.
        """
        coords = ""
        for v in obj.data.vertices:
            for c in v.co:
                c = int(c) if c.is_integer() else c
                coords += str(c) + " "

        etree.SubElement(grid, "vertices", coords="3").text = coords

    def add_edges(self, obj: bpy.types.Object, grid: etree.Element) -> None:
        """Adds edges to the grid element in the ugx file.

        Args:
            obj (bpy.types.Object): The object to export.
            grid (lxml.etree.Element): The grid element.
        """
        edges = ""
        for e in obj.data.edges:
            edges += str(e.vertices[0]) + " " + str(e.vertices[1]) + " "

        etree.SubElement(grid, "edges").text = edges

    def add_faces(self, obj: bpy.types.Object, grid: etree.Element) -> None:
        """Add triangles and quads to the grid element in the ugx file.

        Args:
            obj (bpy.types.Object): The object to export.
            grid (lxml.etree.Element): The grid element.
        """
        triangles = ""
        quads = ""
        for f in obj.data.polygons:
            if len(f.vertices) == 3:
                triangles += str(f.vertices[0]) + " " + str(f.vertices[1]) + " " + str(f.vertices[2]) + " "
            elif len(f.vertices) == 4:
                quads += str(f.vertices[0]) + " " + str(f.vertices[1]) + " " + str(f.vertices[2]) + " " + str(f.vertices[3]) + " "
            else:
                self.report({'ERROR'}, "Only triangles and quads are supported.")
                return {'CANCELLED'}

        if triangles != "":
            etree.SubElement(grid, "triangles").text = triangles
        if quads != "":
            etree.SubElement(grid, "quads").text = quads

    def add_subsets(self, obj: bpy.types.Object, grid: etree.Element) -> None:
        """Add subsets to the grid element in the ugx file.

        Args:
            obj (bpy.types.Object): The object to export.
            grid (lxml.etree.Element): The grid element.
        """
        # add subset handler
        subset_handler = etree.SubElement(grid, "subset_handler", name="defSH")

        subsets = {}
        # add subsets
        for s in bpy.context.scene.ugx_subsets:
            coords = ""
            for c in tuple(s.color):
                c = int(c) if c.is_integer() else c
                coords += str(c) + " "
            subsets[s.index] = {"main" : etree.SubElement(subset_handler, "subset", name=s.name, color=coords, state="393216")}

        bm = bmesh.from_edit_mesh(obj.data)

        s = bm.verts.layers.int.get("vertex_subset")
        for v in bm.verts:
            if "vertices" in subsets[bm.verts[v.index][s]].keys():
                subsets[bm.verts[v.index][s]]["vertices"].text += str(v.index) + " "
            else:
                sub = etree.SubElement(subsets[bm.verts[v.index][s]]["main"], "vertices")
                sub.text = str(v.index) + " "
                subsets[bm.verts[v.index][s]]["vertices"] = sub

        s = bm.edges.layers.int.get("edge_subset")
        for e in bm.edges:
            if "edges" in subsets[bm.edges[e.index][s]].keys():
                subsets[bm.edges[e.index][s]]["edges"].text += str(e.index) + " "
            else:
                sub = etree.SubElement(subsets[bm.edges[e.index][s]]["main"], "edges")
                sub.text = str(e.index) + " "
                subsets[bm.edges[e.index][s]]["edges"] = sub

        s = bm.faces.layers.int.get("face_subset")
        for f in bm.faces:
            if "faces" in subsets[bm.faces[f.index][s]].keys():
                subsets[bm.faces[f.index][s]]["faces"].text += str(f.index) + " "
            else:
                sub = etree.SubElement(subsets[bm.faces[f.index][s]]["main"], "faces")
                sub.text = str(f.index) + " "
                subsets[bm.faces[f.index][s]]["faces"] = sub

    def add_mark_subset_handler(self, grid: etree.Element) -> None:
        """Add mark subset handler to the grid element in the ugx file.

        Args:
            grid (lxml.etree.Element): The grid element.
        """
        # add mark subset handler
        mark_subset_handler = etree.SubElement(grid, "subset_handler", name="markSH")

        # i do not know yet, what this is for
        etree.SubElement(mark_subset_handler, "subset", name="crease", color="1 1 1 1", state="0")
        etree.SubElement(mark_subset_handler, "subset", name="fixed", color="1 1 1 1", state="0")

    def add_selector(self, obj: bpy.types.Object, grid: etree.Element) -> None:
        """Add selector to the grid element in the ugx file.

        Args:
            obj (bpy.types.Object): The object to export.
            grid (lxml.etree.Element): The grid element.
        """
        # the selector saves the current selection
        selector = etree.SubElement(grid, "selector", name="defSel")

        # add vertices
        vertices = ""
        for v in obj.data.vertices:
            if v.select:
                vertices += str(v.index) + " "

        if vertices != "":
            etree.SubElement(selector, "vertices").text = vertices

        # add edges
        edges = ""
        for e in obj.data.edges:
            if e.select:
                edges += str(e.index) + " "

        if edges != "":
            etree.SubElement(selector, "edges").text = edges

        # add faces
        faces = ""
        for f in obj.data.polygons:
            if f.select:
                faces += str(f.index) + " "

        if faces != "":
            etree.SubElement(selector, "faces").text = faces

    def add_projection_handler(self, grid: etree.Element) -> None:
        """Add projection handler to the grid element in the ugx file.

        Args:
            grid (lxml.etree.Element): The grid element.
        """
        # add projection handler
        projection_handler = etree.SubElement(grid, "projection_handler", name="defPH")

        # add default projection, i also do not know yet what this is for
        default = etree.SubElement(projection_handler, "default", type="default")
        default.text = "0 0"

    def execute(self, context: bpy.types.Context) -> set:
        """Execute the export.

        Args:
            context (bpy.types.Context): Blender context.

        Returns:
            set: The result status of the export.
        """
        scene = context.scene
        cursor = scene.cursor.location
        obj = context.active_object

        # start of the xml file
        grid = etree.Element("grid", name="defGrid")

        self.add_vertices(obj, grid)
        self.add_edges(obj, grid)
        self.add_faces(obj, grid)

        self.add_subsets(obj, grid)

        self.add_mark_subset_handler(obj, grid)

        self.add_selector(obj, grid)

        self.add_projection_handler(obj, grid)

        # write to file
        tree = etree.ElementTree(grid)
        tree.write("/home/nordegraf/bwSyncShare/Projekte/blender_io_mesh_ugx/test.xml", pretty_print=True)

        self.report({'INFO'}, "File written.")

        return {'FINISHED'}

class UGXImporter(bpy.types.Operator):
    """Importer class for the UGX format."""
    bl_idname: str = "import.ugx"
    bl_label: str = "Import UGX"
    bl_options: str = {'REGISTER', 'UNDO'}

    def get_vertices(self, grid: etree.Element, bm: bmesh.types.BMesh) -> None:
        """Gets the vertices from the ugx file.

        Args:
            grid (lxml.etree.Element): The grid element.
            bm (bmesh.types.BMesh): The bmesh object.
        """
        verts = grid.findtext("vertices").split(" ")
        verts = [float(v) for v in verts]

        num_verts = len(verts) // 3

        for i in range(num_verts):
            v = bm.verts.new(verts[i*3:(i+1)*3])
            v.index = i

    def get_edges(self, grid: etree.Element, bm: bmesh.types.BMesh) -> None:
        """Gets the edges from the ugx file.

        Args:
            grid (lxml.etree.Element): The grid element.
            bm (bmesh.types.BMesh): The bmesh object.
        """
        edges = grid.findtext("edges").split(" ")
        edges = [int(e) for e in edges]

        num_edges = len(edges) // 2

        for i in range(num_edges):
            bm.edges.new([bm.verts[edges[i*2]], bm.verts[edges[i*2+1]]])

    def get_triangles(self, grid: etree.Element, bm: bmesh.types.BMesh) -> None:
        """Gets the triangles from the ugx file.

        Args:
            grid (lxml.etree.Element): The grid element.
            bm (bmesh.types.BMesh): The bmesh object.
        """

        triangles = grid.findtext("triangles").split(" ")
        triangles = [int(t) for t in triangles]

        num_triangles = len(triangles) // 3

        for i in range(num_triangles):
            bm.faces.new([bm.verts[triangles[i*3]], bm.verts[triangles[i*3+1]], bm.verts[triangles[i*3+2]]])

    def get_quads(self, grid: etree.Element, bm: bmesh.types.BMesh) -> None:
        """Gets the quads from the ugx file.

        Args:
            grid (lxml.etree.Element): The grid element.
            bm (bmesh.types.BMesh): The bmesh object.
        """
        quads = grid.findtext("quads").split(" ")
        quads = [int(q) for q in quads]

        num_quads = len(quads) // 4

        for i in range(num_quads):
            bm.faces.new([bm.verts[quads[i*4]], bm.verts[quads[i*4+1]], bm.verts[quads[i*4+2]], bm.verts[quads[i*4+3]]])

    def get_subsets(self, grid: etree.Element, bm: bmesh.types.BMesh, scene: bpy.types.Scene) -> None:
        """Gets the subsets from the ugx file.

        Args:
            grid (lxml.etree.Element): The grid element.
            bm (bmesh.types.BMesh): The bmesh object.
            scene (bpy.types.Scene): The scene.
        """
        subsets = grid.find("subset_handler").findall("subset")

        vertex_subset = bm.verts.layers.int.new("vertex_subset")
        edge_subset = bm.edges.layers.int.new("edge_subset")
        face_subset = bm.faces.layers.int.new("face_subset")

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        i = 0
        for s in subsets:
            name = s.get("name")
            color = s.get("color")

            subset = scene.ugx_subsets.add()
            subset.name = name
            subset.color = [float(c) for c in color.split(" ")]
            subset.index = i

            if s.findtext("vertices") is not None:
                for v in s.findtext("vertices").split(" "):
                    bm.verts[int(v)][vertex_subset] = i

            if s.findtext("edges") is not None:
                for e in s.findtext("edges").split(" "):
                    bm.edges[int(e)][edge_subset] = i

            if s.findtext("triangles") is not None:
                for t in s.findtext("triangles").split(" "):
                    bm.faces[int(t)][face_subset] = i

            if s.findtext("quads") is not None:
                for q in s.findtext("quads").split(" "):
                    bm.faces[int(q)][face_subset] = i

            i += 1


    def get_selector(self, grid: etree.Element) -> None:
        """Gets the selector from the ugx file.

        Args:
            grid (lxml.etree.Element): The grid element.
        """
        selector = grid.find("selector")

        vertices = selector.findtext("vertices")
        edges = selector.findtext("edges")
        faces = selector.findtext("faces")

        print(vertices, edges, faces)

    def execute(self, context: bpy.types.Context) -> set:
        """Executes the import.

        Args:
            context (bpy.types.Context): The context.

        Returns:
            set: The result.
        """
        scene = context.scene
        mesh = bpy.data.meshes.new("UGXMesh")
        obj = bpy.data.objects.new("UGXObject", mesh)
        scene.collection.objects.link(obj)
        tree = etree.parse("/home/nordegraf/bwSyncShare/Projekte/blender_io_mesh_ugx/henry.ugx")

        grid = tree.getroot()

        bm = bmesh.new()

        self.get_vertices(grid, bm)
        bm.verts.ensure_lookup_table()

        self.get_edges(grid, bm)

        if grid.find("triangles") is not None:
            self.get_triangles(grid, bm)

        if grid.find("quads") is not None:
            self.get_quads(grid, bm)

        self.get_subsets(grid, bm, scene)
        self.get_selector(grid, bm)

        bm.to_mesh(mesh)
        bm.free()

        return {'FINISHED'}
