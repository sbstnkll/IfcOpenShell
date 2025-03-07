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
import json
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.attribute
import ifcopenshell.util.representation
import blenderbim.bim.helper
import blenderbim.tool as tool
import blenderbim.core.style
import blenderbim.core.material as core
import blenderbim.bim.module.model.profile as model_profile
from blenderbim.bim.module.material.prop import purge as material_prop_purge
from blenderbim.bim.ifc import IfcStore


class LoadMaterials(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_materials"
    bl_label = "Load Materials"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.load_materials(tool.Material, context.scene.BIMMaterialProperties.material_type)


class DisableEditingMaterials(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_materials"
    bl_label = "Disable Editing Materials"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_materials(tool.Material)


class SelectByMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_by_material"
    bl_label = "Select By Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_by_material(tool.Material, material=tool.Ifc.get().by_id(self.material))


class EnableEditingMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_material"
    bl_label = "Enable Editing Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_material(tool.Material, material=tool.Ifc.get().by_id(self.material))


class EditMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_material"
    bl_label = "Edit Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_material(tool.Ifc, tool.Material, material=tool.Ifc.get().by_id(self.material))


class DisableEditingMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_material"
    bl_label = "Disable Editing Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.disable_editing_material(tool.Material)


class AssignParameterizedProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_parameterized_profile"
    bl_label = "Assign Parameterized Profile"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    material_profile: bpy.props.IntProperty()
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        profile = ifcopenshell.api.run(
            "profile.add_parameterized_profile",
            self.file,
            **{"ifc_class": self.ifc_class},
        )
        ifcopenshell.api.run(
            "material.assign_profile",
            self.file,
            **{"material_profile": self.file.by_id(self.material_profile), "profile": profile},
        )
        bpy.ops.bim.enable_editing_material_set_item(obj=obj.name, material_set_item=self.material_profile)


class AddMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_material"
    bl_label = "Add Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        obj = bpy.data.materials.get(self.obj) if self.obj else None
        core.add_material(tool.Ifc, tool.Material, tool.Style, obj=obj)
        material_prop_purge()


class AddMaterialSet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_material_set"
    bl_label = "Add Material Set"
    bl_options = {"REGISTER", "UNDO"}
    set_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_material_set(tool.Ifc, tool.Material, set_type=self.set_type)
        material_prop_purge()


class RemoveMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_material"
    bl_label = "Remove Material"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_material(tool.Ifc, tool.Material, tool.Style, material=tool.Ifc.get().by_id(self.material))


class RemoveMaterialSet(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_material_set"
    bl_label = "Remove Material Set"
    bl_options = {"REGISTER", "UNDO"}
    material: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_material_set(tool.Ifc, tool.Material, material=tool.Ifc.get().by_id(self.material))


class UnlinkMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unlink_material"
    bl_label = "Unlink Material"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.unlink_material(tool.Ifc, obj=context.active_object.active_material)


class AssignMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_material"
    bl_label = "Assign Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_type: bpy.props.StringProperty()

    def _execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else tool.Blender.get_selected_objects()
        active_obj = context.active_object
        active_object_material_type = self.material_type or active_obj.BIMObjectMaterialProperties.material_type
        material = tool.Ifc.get().by_id(int(active_obj.BIMObjectMaterialProperties.material))
        for obj in objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            ifcopenshell.api.run(
                "material.assign_material",
                tool.Ifc.get(),
                product=element,
                type=active_object_material_type,
                material=material,
            )
            assigned_material = ifcopenshell.util.element.get_material(element)
            if assigned_material.is_a() in ("IfcMaterialLayerSet", "IfcMaterialLayerSetUsage"):
                if assigned_material.is_a("IfcMaterialLayerSet"):
                    layer_set = assigned_material
                else:
                    layer_set = assigned_material.ForLayerSet

                if not layer_set.MaterialLayers:
                    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                    layer = ifcopenshell.api.run(
                        "material.add_layer",
                        tool.Ifc.get(),
                        layer_set=layer_set,
                        material=material,
                    )
                    thickness = 0.1  # Arbitrary metric thickness for now
                    layer.LayerThickness = thickness / unit_scale

            elif assigned_material.is_a("IfcMaterialProfileSet"):
                if not assigned_material.MaterialProfiles:
                    named_profiles = [p for p in tool.Ifc.get().by_type("IfcProfileDef") if p.ProfileName]
                    if named_profiles:
                        profile = named_profiles[0]
                    else:
                        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                        size = 0.5 / unit_scale
                        profile = tool.Ifc.get().create_entity(
                            "IfcRectangleProfileDef",
                            ProfileName="New Profile",
                            ProfileType="AREA",
                            XDim=size,
                            YDim=size,
                        )
                        material_profile = ifcopenshell.api.run(
                            "material.add_profile",
                            tool.Ifc.get(),
                            profile_set=assigned_material,
                            material=tool.Ifc.get().by_type("IfcMaterial")[0],
                        )
                        ifcopenshell.api.run(
                            "material.assign_profile",
                            tool.Ifc.get(),
                            material_profile=material_profile,
                            profile=profile,
                        )


class UnassignMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_material"
    bl_label = "Unassign Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else tool.Blender.get_selected_objects()
        for obj in objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                material = ifcopenshell.util.element.get_material(element, should_inherit=False)
                if "Usage" not in material.is_a():
                    ifcopenshell.api.run("material.unassign_material", tool.Ifc.get(), product=element)


class AddConstituent(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_constituent"
    bl_label = "Add Constituent"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constituent_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.add_constituent",
            self.file,
            **{
                "constituent_set": self.file.by_id(self.constituent_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )


class RemoveConstituent(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_constituent"
    bl_label = "Remove Constituent"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    constituent: bpy.props.IntProperty()

    def _execute(self, context):
        for inverse in tool.Ifc.get().get_inverse(tool.Ifc.get().by_id(self.constituent)):
            if inverse.is_a("IfcMaterialConstituentSet") and len(inverse.MaterialConstituents) == 1:
                return
        ifcopenshell.api.run(
            "material.remove_constituent", tool.Ifc.get(), constituent=tool.Ifc.get().by_id(self.constituent)
        )


class AddProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_profile"
    bl_label = "Add Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    profile_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.add_profile",
            self.file,
            profile_set=self.file.by_id(self.profile_set),
            material=self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            profile=self.file.by_id(int(context.scene.BIMMaterialProperties.profiles)),
        )


class RemoveProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_profile"
    bl_label = "Remove Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    profile: bpy.props.IntProperty()

    def _execute(self, context):
        for inverse in tool.Ifc.get().get_inverse(tool.Ifc.get().by_id(self.profile)):
            if inverse.is_a("IfcMaterialProfileSet") and len(inverse.MaterialProfiles) == 1:
                return
        ifcopenshell.api.run("material.remove_profile", tool.Ifc.get(), profile=tool.Ifc.get().by_id(self.profile))


class AddLayer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_layer"
    bl_label = "Add Layer"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    layer_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        layer = ifcopenshell.api.run(
            "material.add_layer",
            self.file,
            **{
                "layer_set": self.file.by_id(self.layer_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        thickness = 0.1 # Arbitrary metric thickness for now
        layer.LayerThickness = thickness / unit_scale


class ReorderMaterialSetItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reorder_material_set_item"
    bl_label = "Reorder Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    old_index: bpy.props.IntProperty()
    new_index: bpy.props.IntProperty()
    material_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        material_set = self.file.by_id(self.material_set)
        ifcopenshell.api.run(
            "material.reorder_set_item",
            self.file,
            **{
                "material_set": material_set,
                "old_index": self.old_index,
                "new_index": self.new_index,
            },
        )


class RemoveLayer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_layer"
    bl_label = "Remove Layer"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    layer: bpy.props.IntProperty()

    def _execute(self, context):
        for inverse in tool.Ifc.get().get_inverse(tool.Ifc.get().by_id(self.layer)):
            if inverse.is_a("IfcMaterialLayerSet") and len(inverse.MaterialLayers) == 1:
                self.report(
                    {"ERROR"}, "Cannot remove material layer - IfcMaterialLayerSet should alawys have atleast 1 layer"
                )
                return {"ERROR"}
        ifcopenshell.api.run("material.remove_layer", tool.Ifc.get(), layer=tool.Ifc.get().by_id(self.layer))


class AddListItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_list_item"
    bl_label = "Add List Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    list_item_set: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.add_list_item",
            self.file,
            **{
                "material_list": self.file.by_id(self.list_item_set),
                "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material)),
            },
        )


class RemoveListItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_list_item"
    bl_label = "Remove List Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    list_item_set: bpy.props.IntProperty()
    list_item: bpy.props.IntProperty()
    list_item_index: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "material.remove_list_item",
            self.file,
            **{
                "material_list": self.file.by_id(self.list_item_set),
                "material_index": self.list_item_index,
            },
        )


class EnableEditingAssignedMaterial(bpy.types.Operator):
    bl_idname = "bim.enable_editing_assigned_material"
    bl_label = "Enable Editing Assigned Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectMaterialProperties
        props.is_editing = True
        element = tool.Ifc.get_entity(obj)
        material = ifcopenshell.util.element.get_material(element)

        if material.is_a("IfcMaterial"):
            props.material = str(material.id())
            return {"FINISHED"}

        props.material_set_usage_attributes.clear()
        props.material_set_attributes.clear()

        if "Usage" in material.is_a():
            blenderbim.bim.helper.import_attributes2(
                material, props.material_set_usage_attributes, callback=self.import_attributes
            )
            blenderbim.bim.helper.import_attributes2(material[0], props.material_set_attributes)
        else:
            blenderbim.bim.helper.import_attributes2(material, props.material_set_attributes)
        return {"FINISHED"}

    def import_attributes(self, name, prop, data):
        if name == "CardinalPoint":
            # TODO: complain to buildingSMART
            cardinal_point_map = {
                1: "bottom left",
                2: "bottom centre",
                3: "bottom right",
                4: "mid-depth left",
                5: "mid-depth centre",
                6: "mid-depth right",
                7: "top left",
                8: "top centre",
                9: "top right",
                10: "geometric centroid",
                11: "bottom in line with the geometric centroid",
                12: "left in line with the geometric centroid",
                13: "right in line with the geometric centroid",
                14: "top in line with the geometric centroid",
                15: "shear centre",
                16: "bottom in line with the shear centre",
                17: "left in line with the shear centre",
                18: "right in line with the shear centre",
                19: "top in line with the shear centre",
            }
            prop.data_type = "enum"
            prop.enum_items = json.dumps(cardinal_point_map)
            if data[name]:
                prop.enum_value = str(data[name])
            return True


class DisableEditingAssignedMaterial(bpy.types.Operator):
    bl_idname = "bim.disable_editing_assigned_material"
    bl_label = "Disable Editing Assigned Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.bim.disable_editing_material_set_item()
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectMaterialProperties
        props.is_editing = False
        return {"FINISHED"}


class EditAssignedMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_assigned_material"
    bl_label = "Edit Assigned Material"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set: bpy.props.IntProperty()
    material_set_usage: bpy.props.IntProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        active_obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = active_obj.BIMObjectMaterialProperties
        element = tool.Ifc.get_entity(active_obj)
        material = ifcopenshell.util.element.get_material(element)

        objects = tool.Blender.get_selected_objects()

        if props.active_material_set_item_id != 0:  # We were editing a material layer set item
            bpy.ops.bim.edit_material_set_item(material_set_item=props.active_material_set_item_id)

        if material.is_a("IfcMaterial"):
            for obj in objects:
                bpy.ops.bim.unassign_material(obj=obj.name)
                bpy.ops.bim.assign_material(obj=obj.name, material_type="IfcMaterial")
            bpy.ops.bim.disable_editing_assigned_material(obj=active_obj.name)
            return {"FINISHED"}

        material_set = self.file.by_id(self.material_set)
        attributes = blenderbim.bim.helper.export_attributes(props.material_set_attributes)
        ifcopenshell.api.run(
            "material.edit_assigned_material",
            self.file,
            **{"element": material_set, "attributes": attributes},
        )

        if self.material_set_usage:
            material_set_usage = self.file.by_id(self.material_set_usage)
            attributes = blenderbim.bim.helper.export_attributes(props.material_set_usage_attributes)
            if material_set_usage.is_a("IfcMaterialLayerSetUsage"):
                ifcopenshell.api.run(
                    "material.edit_layer_usage",
                    self.file,
                    **{"usage": material_set_usage, "attributes": attributes},
                )
            elif material_set_usage.is_a("IfcMaterialProfileSetUsage"):
                if attributes.get("CardinalPoint", None):
                    attributes["CardinalPoint"] = int(attributes["CardinalPoint"])
                ifcopenshell.api.run(
                    "material.edit_profile_usage",
                    self.file,
                    **{"usage": material_set_usage, "attributes": attributes},
                )

        bpy.ops.bim.disable_editing_assigned_material(obj=active_obj.name)


class EnableEditingMaterialSetItemProfile(bpy.types.Operator):
    bl_idname = "bim.enable_editing_material_set_item_profile"
    bl_label = "Enable Editing Material Set Item Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.props = obj.BIMObjectMaterialProperties
        self.props.material_set_item_profile_attributes.clear()
        profile = tool.Ifc.get().by_id(self.material_set_item).Profile
        blenderbim.bim.helper.import_attributes2(profile, self.props.material_set_item_profile_attributes)
        return {"FINISHED"}


class DisableEditingMaterialSetItemProfile(bpy.types.Operator):
    bl_idname = "bim.disable_editing_material_set_item_profile"
    bl_label = "Disable Editing Material Set Item Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.props = obj.BIMObjectMaterialProperties
        self.props.material_set_item_profile_attributes.clear()
        return {"FINISHED"}


class EditMaterialSetItemProfile(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_material_set_item_profile"
    bl_label = "Edit Material Set Item Profile"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.props = obj.BIMObjectMaterialProperties
        attributes = blenderbim.bim.helper.export_attributes(self.props.material_set_item_profile_attributes)
        profile = tool.Ifc.get().by_id(self.material_set_item).Profile
        ifcopenshell.api.run("profile.edit_profile", tool.Ifc.get(), profile=profile, attributes=attributes)
        self.props.material_set_item_profile_attributes.clear()
        model_profile.DumbProfileRegenerator().regenerate_from_profile_def(profile)


class EnableEditingMaterialSetItem(bpy.types.Operator):
    bl_idname = "bim.enable_editing_material_set_item"
    bl_label = "Enable Editing Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.mprops = context.scene.BIMMaterialProperties
        self.props = obj.BIMObjectMaterialProperties
        self.props.active_material_set_item_id = self.material_set_item

        element = tool.Ifc.get_entity(obj)
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        material_set_item = self.file.by_id(self.material_set_item)

        self.props.material_set_item_material = str(material_set_item.Material.id())

        self.props.material_set_item_attributes.clear()
        blenderbim.bim.helper.import_attributes2(material_set_item, self.props.material_set_item_attributes)

        if material_set_item.is_a("IfcMaterialProfile"):
            if material_set_item.Profile and material_set_item.Profile.ProfileName:
                self.mprops.profiles = str(material_set_item.Profile.id())

        return {"FINISHED"}


class DisableEditingMaterialSetItem(bpy.types.Operator):
    bl_idname = "bim.disable_editing_material_set_item"
    bl_label = "Disable Editing Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        props = obj.BIMObjectMaterialProperties
        props.active_material_set_item_id = 0
        return {"FINISHED"}


class EditMaterialSetItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_material_set_item"
    bl_label = "Edit Material Set Item"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    material_set_item: bpy.props.IntProperty()

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        self.file = IfcStore.get_file()
        props = obj.BIMObjectMaterialProperties
        mprops = context.scene.BIMMaterialProperties
        element = tool.Ifc.get_entity(obj)
        material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)

        attributes = blenderbim.bim.helper.export_attributes(props.material_set_item_attributes)

        if material.is_a("IfcMaterialConstituentSet"):
            ifcopenshell.api.run(
                "material.edit_constituent",
                self.file,
                **{
                    "constituent": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            )
        elif material.is_a("IfcMaterialLayerSet"):
            ifcopenshell.api.run(
                "material.edit_layer",
                self.file,
                **{
                    "layer": self.file.by_id(self.material_set_item),
                    "attributes": attributes,
                    "material": self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
                },
            )
        elif material.is_a("IfcMaterialProfileSet"):
            profile_def = None
            if mprops.profiles:
                profile_def = tool.Ifc.get().by_id(int(mprops.profiles))

            ifcopenshell.api.run(
                "material.edit_profile",
                self.file,
                profile=self.file.by_id(self.material_set_item),
                attributes=attributes,
                profile_def=profile_def,
                material=self.file.by_id(int(obj.BIMObjectMaterialProperties.material_set_item_material)),
            )
        else:
            pass

        bpy.ops.bim.disable_editing_material_set_item(obj=obj.name)


class CopyMaterial(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_material"
    bl_label = "Copy Material"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        blender_material = context.active_object.active_material
        material = tool.Ifc.get_entity(blender_material)

        if tool.Ifc.has_changed_shading(blender_material):
            blenderbim.core.style.update_style_colours(tool.Ifc, tool.Style, obj=blender_material)

        copied_material = ifcopenshell.api.run("material.copy_material", tool.Ifc.get(), material=material)
        copied_blender_material = blender_material.copy()
        copied_style = self.get_style(copied_material)
        tool.Ifc.link(copied_material, copied_blender_material)
        if copied_style:
            tool.Ifc.link(copied_style, copied_blender_material)
        context.active_object.active_material = copied_blender_material

    def get_style(self, material):
        for material_representation in material.HasRepresentation:
            for representation in material_representation.Representations:
                for item in representation.Items:
                    for style in item.Styles:
                        if style.is_a("IfcSurfaceStyle"):
                            return style


class ExpandMaterialCategory(bpy.types.Operator):
    bl_idname = "bim.expand_material_category"
    bl_label = "Expand Material Category"
    bl_options = {"REGISTER", "UNDO"}
    category: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMMaterialProperties
        for category in [c for c in props.materials if c.is_category and c.name == self.category]:
            category.is_expanded = True
        core.load_materials(tool.Material, props.material_type)
        return {"FINISHED"}


class ContractMaterialCategory(bpy.types.Operator):
    bl_idname = "bim.contract_material_category"
    bl_label = "Contract Material Category"
    bl_options = {"REGISTER", "UNDO"}
    category: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMMaterialProperties
        for category in [c for c in props.materials if c.is_category and c.name == self.category]:
            category.is_expanded = False
        core.load_materials(tool.Material, props.material_type)
        return {"FINISHED"}
