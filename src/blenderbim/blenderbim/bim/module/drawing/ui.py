# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.bim.helper
import blenderbim.tool as tool
from bpy.types import Panel
from blenderbim.bim.module.drawing.data import (
    ProductAssignmentsData,
    SheetsData,
    SchedulesData,
    DrawingsData,
    DecoratorData,
)


class BIM_PT_camera(Panel):
    bl_label = "Drawing Generation"
    bl_idname = "BIM_PT_camera"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.camera and hasattr(context.active_object.data, "BIMCameraProperties")

    def draw(self, context):
        layout = self.layout

        if "/" not in context.active_object.name:
            layout.label(text="This is not a BIM camera.")
            return

        layout.use_property_split = True
        dprops = context.scene.DocProperties
        props = context.active_object.data.BIMCameraProperties

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(props, "has_underlay", icon="OUTLINER_OB_IMAGE")
        row.prop(dprops, "should_use_underlay_cache", text="", icon="FILE_REFRESH")
        row = col.row(align=True)
        row.prop(props, "has_linework", icon="IMAGE_DATA")
        row.prop(dprops, "should_use_linework_cache", text="", icon="FILE_REFRESH")
        row = col.row(align=True)
        row.prop(props, "has_annotation", icon="MOD_EDGESPLIT")
        row.prop(dprops, "should_use_annotation_cache", text="", icon="FILE_REFRESH")

        row = layout.row()
        row.prop(props, "calculate_shapely_surfaces")
        row = layout.row()
        row.prop(props, "calculate_svgfill_surfaces")

        row = layout.row()
        row.prop(dprops, "should_extract")

        row = layout.row()
        row.prop(props, "is_nts")

        row = layout.row()
        row.operator("bim.resize_text")

        row = layout.row()
        row.prop(props, "raster_x")
        row = layout.row()
        row.prop(props, "raster_y")

        row = layout.row()
        row.prop(props, "diagram_scale")
        if props.diagram_scale == "CUSTOM":
            row = layout.row(align=True)
            row.prop(props, "custom_diagram_scale_input1", text="Custom Scale")
            if context.scene.unit_settings.system == "IMPERIAL":
                separator = "         ="
            else:
                separator = "         :"
            row.label(text=separator)
            row.prop(props, "custom_diagram_scale_input2", text="")

        row = layout.row(align=True)
        row.operator("bim.create_drawing", text="Create Drawing", icon="OUTPUT")
        op = row.operator("bim.open_drawing", icon="URL", text="")
        op.view = context.active_object.name.split("/")[1]


class BIM_PT_drawing_underlay(Panel):
    bl_label = "Drawing Underlay"
    bl_idname = "BIM_PT_drawing_underlay"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "BIM_PT_camera"

    @classmethod
    def poll(cls, context):
        return context.camera and hasattr(context.active_object.data, "BIMCameraProperties")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        dprops = context.scene.DocProperties
        props = context.active_object.data.BIMCameraProperties
        drawing_index_is_valid = props.active_drawing_style_index < len(dprops.drawing_styles)

        if not DrawingsData.is_loaded:
            DrawingsData.load()
        drawing_pset_data = DrawingsData.data["active_drawing_pset_data"]

        row = layout.row(align=True)
        current_shading_style = drawing_pset_data.get("CurrentShadingStyle", None)
        if current_shading_style is None:
            row.label(text="Current style is not set.")
        else:
            row.label(text="Current Shading Style:")
            row.label(text=current_shading_style)
        row.operator("bim.add_drawing_style", icon="ADD", text="")
        if drawing_index_is_valid:
            row.operator("bim.remove_drawing_style", icon="X", text="").index = props.active_drawing_style_index
        row.operator("bim.reload_drawing_styles", icon="FILE_REFRESH", text="")

        if not dprops.drawing_styles:
            return
        layout.template_list("BIM_UL_generic", "", dprops, "drawing_styles", props, "active_drawing_style_index")

        if not drawing_index_is_valid:
            return
        drawing_style = dprops.drawing_styles[props.active_drawing_style_index]

        row = layout.row(align=True)
        row.prop(drawing_style, "name")

        row = layout.row()
        row.prop(drawing_style, "render_type")
        row = layout.row(align=True)
        row.prop(drawing_style, "include_query")
        row = layout.row(align=True)
        row.prop(drawing_style, "exclude_query")

        row = layout.row()
        row.operator("bim.add_drawing_style_attribute")

        for index, attribute in enumerate(drawing_style.attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.operator("bim.remove_drawing_style_attribute", icon="X", text="").index = index

        row = layout.row(align=True)
        row.operator("bim.save_drawing_style")
        row.operator("bim.activate_drawing_style")


class BIM_PT_drawings(Panel):
    bl_label = "Drawings"
    bl_idname = "BIM_PT_drawings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BIM Documentation"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not DrawingsData.is_loaded:
            DrawingsData.load()

        if not DrawingsData.data["has_saved_ifc"]:
            row = self.layout.row()
            row.label(text="Project Not Yet Saved", icon="ERROR")
            row = self.layout.row()
            op = row.operator("export_ifc.bim", icon="EXPORT", text="Save Project")
            op.should_save_as = False
            return

        self.props = context.scene.DocProperties

        if not self.props.is_editing_drawings:
            row = self.layout.row(align=True)
            row.label(text=f"{DrawingsData.data['total_drawings']} Drawings Found", icon="IMAGE_DATA")
            row.operator("bim.load_drawings", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.prop(self.props, "target_view", text="")
        row.prop(self.props, "location_hint", text="")
        row.operator("bim.add_drawing", text="", icon="ADD")
        row.operator("bim.disable_editing_drawings", text="", icon="CANCEL")

        if self.props.drawings:
            if self.props.active_drawing_index < len(self.props.drawings):
                active_drawing = self.props.drawings[self.props.active_drawing_index]
                row = self.layout.row(align=True)
                col = row.column()
                col.alignment = "LEFT"
                row2 = col.row(align=True)
                row2.operator("bim.remove_drawing", icon="X", text="").drawing = active_drawing.ifc_definition_id
                row2.operator(
                    "bim.duplicate_drawing", icon="COPYDOWN", text=""
                ).drawing = active_drawing.ifc_definition_id
                col = row.column()
                col.alignment = "RIGHT"
                op = row.operator("bim.select_all_drawings", icon="SELECT_SUBTRACT", text="")
                op = row.operator("bim.open_drawing", icon="URL", text="")
                op.view = active_drawing.name
                row.operator("bim.activate_model", icon="VIEW3D", text="")
                op = row.operator("bim.activate_drawing", icon="OUTLINER_OB_CAMERA", text="")
                op.drawing = active_drawing.ifc_definition_id
                row.operator("bim.create_drawing", text="", icon="OUTPUT")
            self.layout.template_list(
                "BIM_UL_drawinglist", "", self.props, "drawings", self.props, "active_drawing_index"
            )

        # Commented out until federated drawing generation is rebuilt
        # row = self.layout.row()
        # row.operator("bim.add_ifc_file")

        # for index, ifc_file in enumerate(self.props.ifc_files):
        #     row = self.layout.row(align=True)
        #     row.prop(ifc_file, "name", text="IFC #{}".format(index + 1))
        #     row.operator("bim.select_doc_ifc_file", icon="FILE_FOLDER", text="").index = index
        #     row.operator("bim.remove_ifc_file", icon="X", text="").index = index


class BIM_PT_schedules(Panel):
    bl_label = "Schedules"
    bl_idname = "BIM_PT_schedules"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BIM Documentation"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not SchedulesData.is_loaded:
            SchedulesData.load()

        if not SchedulesData.data["has_saved_ifc"]:
            row = self.layout.row()
            row.label(text="Project Not Yet Saved", icon="ERROR")
            row = self.layout.row()
            op = row.operator("export_ifc.bim", icon="EXPORT", text="Save Project")
            op.should_save_as = False
            return

        self.props = context.scene.DocProperties

        if not self.props.is_editing_schedules:
            row = self.layout.row(align=True)
            row.label(text=f"{SchedulesData.data['total_schedules']} Schedules Found", icon="LONGDISPLAY")
            row.operator("bim.load_schedules", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.operator("bim.add_schedule", icon="ADD")
        row.operator("bim.disable_editing_schedules", text="", icon="CANCEL")

        if self.props.schedules:
            if self.props.active_schedule_index < len(self.props.schedules):
                active_schedule = self.props.schedules[self.props.active_schedule_index]
                row = self.layout.row(align=True)
                row.alignment = "RIGHT"
                row.operator("bim.open_schedule", icon="URL", text="").schedule = active_schedule.ifc_definition_id
                row.operator(
                    "bim.build_schedule", icon="LINENUMBERS_ON", text=""
                ).schedule = active_schedule.ifc_definition_id
                row.operator("bim.remove_schedule", icon="X", text="").schedule = active_schedule.ifc_definition_id

            self.layout.template_list(
                "BIM_UL_generic", "", self.props, "schedules", self.props, "active_schedule_index"
            )


class BIM_PT_sheets(Panel):
    bl_label = "Sheets"
    bl_idname = "BIM_PT_sheets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BIM Documentation"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not SheetsData.is_loaded:
            SheetsData.load()

        if not SheetsData.data["has_saved_ifc"]:
            row = self.layout.row()
            row.label(text="Project Not Yet Saved", icon="ERROR")
            row = self.layout.row()
            op = row.operator("export_ifc.bim", icon="EXPORT", text="Save Project")
            op.should_save_as = False
            return

        self.props = context.scene.DocProperties

        if not self.props.is_editing_sheets:
            row = self.layout.row(align=True)
            row.label(text=f"{SheetsData.data['total_sheets']} Sheets Found", icon="FILE")
            row.operator("bim.load_sheets", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.prop(self.props, "titleblock", text="")
        row.operator("bim.add_sheet", text="", icon="ADD")
        row.operator("bim.disable_editing_sheets", text="", icon="CANCEL")

        if self.props.sheets and self.props.active_sheet_index < len(self.props.sheets):
            active_sheet = self.props.sheets[self.props.active_sheet_index]
            row = self.layout.row(align=True)
            row.alignment = "RIGHT"
            row.operator("bim.edit_sheet", icon="GREASEPENCIL", text="")
            row.operator("bim.open_sheet", icon="URL", text="")
            row.operator("bim.add_drawing_to_sheet", icon="IMAGE_PLANE", text="")
            row.operator("bim.add_schedule_to_sheet", icon="PRESET_NEW", text="")
            row.operator("bim.create_sheets", icon="FILE_REFRESH", text="")
            if active_sheet.is_sheet:
                row.operator("bim.remove_sheet", icon="X", text="").sheet = active_sheet.ifc_definition_id
            else:
                op = row.operator("bim.remove_drawing_from_sheet", icon="X", text="")
                op.reference = active_sheet.ifc_definition_id

        self.layout.template_list("BIM_UL_sheets", "", self.props, "sheets", self.props, "active_sheet_index")


class BIM_PT_product_assignments(Panel):
    bl_label = "IFC Product Assignments"
    bl_idname = "BIM_PT_product_assignments"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get() or not context.active_object:
            return
        element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return
        return element.is_a("IfcAnnotation")

    def draw(self, context):
        if not ProductAssignmentsData.is_loaded:
            ProductAssignmentsData.load()

        props = context.active_object.BIMAssignedProductProperties

        if props.is_editing_product:
            row = self.layout.row(align=True)
            row.prop(props, "relating_product", text="")
            row.operator("bim.edit_assigned_product", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_assigned_product", icon="CANCEL", text="")
        else:
            row = self.layout.row(align=True)
            row.label(text=ProductAssignmentsData.data["relating_product"] or "No Relating Product", icon="OBJECT_DATA")
            row.operator("bim.enable_editing_assigned_product", icon="GREASEPENCIL", text="")
            row.operator("bim.select_assigned_product", icon="RESTRICT_SELECT_OFF", text="")


class BIM_PT_text(Panel):
    bl_label = "IFC Text"
    bl_idname = "BIM_PT_text"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get() or not context.active_object:
            return
        element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return
        return tool.Drawing.is_annotation_object_type(element, ["TEXT", "TEXT_LEADER"])

    def draw(self, context):
        obj = context.active_object
        props = obj.BIMTextProperties

        if props.is_editing:
            # shares most of the code with EditTextPopup.draw()
            # need to keep them in sync or move to some common function

            row = self.layout.row(align=True)
            row.operator("bim.edit_text", icon="CHECKMARK")
            row.operator("bim.add_text_literal", icon="ADD", text="")
            row.operator("bim.disable_editing_text", icon="CANCEL", text="")

            row = self.layout.row(align=True)
            row.prop(props, "font_size")

            for i, literal_props in enumerate(props.literals):
                box = self.layout.box()
                row = self.layout.row(align=True)

                row = box.row(align=True)
                row.label(text=f"Literal[{i}]:")
                row.operator("bim.remove_text_literal", icon="X", text="").literal_prop_id = i

                # skip BoxAlignment since we're going to format it ourselves
                attributes = [a for a in literal_props.attributes if a.name != "BoxAlignment"]
                blenderbim.bim.helper.draw_attributes(attributes, box)

                row = box.row(align=True)
                cols = [row.column(align=True) for i in range(3)]
                for i in range(9):
                    cols[i % 3].prop(
                        literal_props,
                        "box_alignment",
                        text="",
                        index=i,
                        icon="RADIOBUT_ON" if literal_props.box_alignment[i] else "RADIOBUT_OFF",
                    )

                col = row.column(align=True)
                col.label(text="    Text box alignment:")
                col.label(text=f'    {literal_props.attributes["BoxAlignment"].string_value}')

        else:
            text_data = DecoratorData.get_ifc_text_data(obj)

            row = self.layout.row()
            row.operator("bim.enable_editing_text", icon="GREASEPENCIL")

            row = self.layout.row(align=True)
            row.label(text="FontSize")
            row.label(text=str(text_data["FontSize"]))

            for literal_data in text_data["Literals"]:
                box = self.layout.box()
                for attribute in literal_data:
                    row = box.row(align=True)
                    row.label(text=attribute)
                    row.label(text=literal_data[attribute])


class BIM_PT_annotation_utilities(Panel):
    bl_idname = "BIM_PT_annotation_utilities"
    bl_label = "Annotation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BIM Documentation"

    def draw(self, context):
        layout = self.layout

        self.props = context.scene.DocProperties

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Dimension", icon="FIXED_SIZE")
        op.object_type = "DIMENSION"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Angle", icon="DRIVER_ROTATIONAL_DIFFERENCE")
        op.object_type = "ANGLE"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Radius", icon="FORWARD")
        op.object_type = "RADIUS"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Diameter", icon="ARROW_LEFTRIGHT")
        op.object_type = "DIAMETER"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Text", icon="SMALL_CAPS")
        op.object_type = "TEXT"
        op.data_type = "empty"
        op = row.operator("bim.add_annotation", text="Leader", icon="TRACKING_BACKWARDS")
        op.object_type = "TEXT_LEADER"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Stair Arrow", icon="SCREEN_BACK")
        op.object_type = "STAIR_ARROW"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Hidden", icon="CON_TRACKTO")
        op.object_type = "HIDDEN_LINE"
        op.data_type = "mesh"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Level (Plan)", icon="SORTBYEXT")
        op.object_type = "PLAN_LEVEL"
        op.data_type = "curve"
        op = row.operator("bim.add_annotation", text="Level (Section)", icon="TRIA_DOWN")
        op.object_type = "SECTION_LEVEL"
        op.data_type = "curve"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Breakline", icon="FCURVE")
        op.object_type = "BREAKLINE"
        op.data_type = "mesh"
        op = row.operator("bim.add_annotation", text="Line", icon="MESH_MONKEY")
        op.object_type = "LINEWORK"
        op.data_type = "mesh"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Batting", icon="FORCE_FORCE")
        op.object_type = "BATTING"
        op.data_type = "mesh"
        op.description = "Add batting annotation.\nThickness could be changed through Thickness property of BBIM_Batting property set"
        op = row.operator("bim.add_annotation", text="Fill Area", icon="NODE_TEXTURE")
        op.object_type = "FILL_AREA"

        row = layout.row(align=True)
        op = row.operator("bim.add_annotation", text="Fall", icon="SORT_ASC")
        op.object_type = "FALL"
        op.data_type = "curve"

        row = layout.row(align=True)
        row.prop(self.props, "should_draw_decorations", text="Viewport Annotations")
        row.enabled = context.scene.camera is not None


class BIM_UL_drawinglist(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            selected_icon = "CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT"
            row.prop(item, "is_selected", text="", icon=selected_icon)
            icon = "UV_FACESEL"
            if item.target_view == "ELEVATION_VIEW":
                icon = "UV_VERTEXSEL"
            elif item.target_view == "SECTION_VIEW":
                icon = "UV_EDGESEL"
            elif item.target_view == "REFLECTED_PLAN_VIEW":
                icon = "XRAY"
            elif item.target_view == "MODEL_VIEW":
                icon = "SNAP_VOLUME"
            row.prop(item, "name", text="", icon=icon, emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_sheets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if not item:
            layout.label(text="", translate=False)
            return

        row = layout.row(align=True)
        if item.is_sheet:
            if item.is_expanded:
                row.operator(
                    "bim.contract_sheet", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                ).sheet = item.ifc_definition_id
            else:
                row.operator(
                    "bim.expand_sheet", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                ).sheet = item.ifc_definition_id

            row.label(text=f"{item.identification} - {item.name}")
        else:
            row.label(text="", icon="BLANK1")
            if item.reference_type == "DRAWING":
                row.label(text="", icon="IMAGE_DATA")
            elif item.reference_type == "SCHEDULE":
                row.label(text="", icon="LONGDISPLAY")
            elif item.reference_type == "TITLEBLOCK":
                row.label(text="", icon="MENU_PANEL")
            elif item.reference_type == "REVISION":
                row.label(text="", icon="RECOVER_LAST")

            if item.identification:
                name = f"{item.identification} - {item.name or 'Unnamed'}"
            else:
                name = item.name or "Unnamed"
            row.label(text=name)
