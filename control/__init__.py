'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy

from . import props
from . import configs
from . import item_ops
from . import copy_item


bl_info = {
    "name" : "CNTRL",
    "author" : "Mahrkeenerh",
    "description" : "Copy-paste any properties and operators to this custom panel",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "N-panel",
    "category" : "3D View"
}


class CNTRL_PT_DynamicPanel(bpy.types.Panel):
    bl_label = "CNTRL"
    bl_idname = "CNTRL_PT_DynamicPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CNTRL"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row(align=True)
        row.prop(bpy.context.scene, "cntrl_configs", text="")
        row.operator(
            "cntrl.edit_toggle",
            text='',
            icon='GREASEPENCIL',
            depress=scene.cntrl_editing
        )

        if scene.cntrl_editing:
            row = layout.row(align=True)
            row.operator("cntrl.new_config", text="New", icon='ADD')
            row.operator("cntrl.open_folder", text="Open Folder", icon='FILE_FOLDER')
            row = layout.row(align=True)
            row.operator("cntrl.pack_config", text="Pack", icon='PACKAGE')
            row.operator("cntrl.unpack_configs", text="Unpack", icon='EXPORT')

        if scene.cntrl_configs == '':
            return

        if scene.cntrl_editing:
            layout.separator()
            layout.prop(bpy.context.scene, "cntrl_config_name", text="")
        layout.separator()

        def draw_items():
            outer = layout
            for i, item in enumerate(scene.cntrl_save_list):
                if scene.cntrl_editing:
                    inner = outer.box()
                else:
                    inner = outer

                error = False

                if item.struct_type == 'CATEGORY_SEPARATOR' and not scene.cntrl_editing:
                    inner.separator()
                    outer = layout.box()
                    if item.display_name != '':
                        outer.label(text=item.display_name)

                if item.struct_type == 'CATEGORY_END' and not scene.cntrl_editing:
                    outer = layout

                if scene.cntrl_editing:
                    row = inner.row()
                    if item.struct_type == 'CATEGORY_END':
                        row.label(text="Category End")
                    elif item.struct_type == 'CATEGORY_SEPARATOR':
                        row.prop(item, "display_name", text="Category")
                    else:
                        row.prop(item, "display_name", text="Display Name")
                    align_row = row.row(align=True)
                    up_row = align_row.row(align=True)
                    down_row = align_row.row(align=True)
                    op = up_row.operator("cntrl.move_item", text="", icon='TRIA_UP')
                    op.index = i
                    op.direction = -1
                    op = down_row.operator("cntrl.move_item", text="", icon='TRIA_DOWN')
                    op.index = i
                    op.direction = 1
                    op = align_row.operator("cntrl.remove_item", text="", icon='X')
                    op.index = i

                    up_row.enabled = i != 0
                    down_row.enabled = i != len(scene.cntrl_save_list) - 1

                # if item.struct_type == 'OPERATOR':
                match item.struct_type:
                    case 'OPERATOR':
                        try:
                            short_path = item.path.replace('bpy.ops.', '')
                            if item.display_name == '':
                                inner.operator(short_path)
                            else:
                                inner.operator(short_path, text=item.display_name if item.display_name != ' ' else '')
                        except Exception as e:
                            print(f'CNTRL: {e}')
                            if scene.cntrl_editing:
                                inner.label(text="Error: " + item.path, icon='ERROR')
                            error = True
                    case 'CATEGORY_SEPARATOR':
                        pass
                    case 'CATEGORY_END':
                        pass
                    case _:
                        try:
                            dirs = item.path.split('.')
                            domain = ".".join(dirs[:-1])
                            name = dirs[-1]
                            row = inner.row()

                            if item.display_name == '':
                                row.prop(eval(domain), name)
                            else:
                                row.prop(eval(domain), name, text=item.display_name if item.display_name != ' ' else '')
                        except Exception as e:
                            print(f'CNTRL: {e}')
                            if scene.cntrl_editing:
                                inner.label(text="Error: " + item.path, icon='ERROR')
                            error = True

                # MIDI options
                # Check if type is not OTHER
                # if not error and scene.cntrl_editing and item.struct_type != 'CATEGORY_SEPARATOR':
                #     row_out = outer.row()
                #     row = row_out.row()
                #     row.alignment = 'LEFT'
                #     row.operator("cntrl.add_to_panel", text="Record", icon='REC')

                #     if 'BOOL' not in item.struct_type and item.struct_type != 'OPERATOR':
                #         row.prop(item, "map_min", text="Min")
                #         row.prop(item, "map_max", text="Max")

                #     if 'VECTOR' in item.struct_type:
                #         row = row_out.row()
                #         row.prop(item, "vector_selection")

        draw_items()

        if not scene.cntrl_editing:
            return

        layout.separator()

        box = layout.box()
        box.prop(bpy.context.scene, "cntrl_new_path", text="")
        box.operator("cntrl.add_to_panel")
        row = box.row()
        row.operator("cntrl.add_category_separator")
        row.operator("cntrl.add_category_end")


def register():
    props.register()
    configs.register()
    item_ops.register()
    copy_item.register()

    bpy.utils.register_class(CNTRL_PT_DynamicPanel)


def unregister():
    props.unregister()
    configs.unregister()
    item_ops.unregister()
    copy_item.unregister()

    bpy.utils.unregister_class(CNTRL_PT_DynamicPanel)
