import mathutils

import bpy

from . import configs


class CNTRL_OT_AddToPanel(bpy.types.Operator):
    bl_idname = "cntrl.add_to_panel"
    bl_label = "Add To Panel"
    bl_description = "Add the selected property or operator to the panel"
    bl_options = {'REGISTER', 'UNDO'}

    def get_type(self, path, prop):
        if path.startswith('bpy.ops.'):
            return 'OPERATOR'

        # SWITCH CASE
        match prop:
            case bool():
                return 'BOOL'
            case int():
                return 'INT'
            case float():
                return 'FLOAT'
            case w if isinstance(w, mathutils.Vector) or isinstance(w, mathutils.Euler) or isinstance(w, mathutils.Quaternion):
                match prop[0]:
                    case bool():
                        return 'BOOL_VECTOR'
                    case int():
                        return 'INT_VECTOR'
                    case float():
                        return 'FLOAT_VECTOR'
                    case _:
                        return 'OTHER'
            case _:
                return 'OTHER'

    def execute(self, context):
        scene = context.scene
        new_path = scene.cntrl_new_path
        if new_path == "":
            self.report({'ERROR'}, "Empty path")
            return {'CANCELLED'}

        if new_path.endswith('()'):
            new_path = new_path[:-2]

        # check if path is valid
        try:
            prop = eval(new_path)
        except SyntaxError:
            self.report({'ERROR'}, "Invalid path - Syntax Error")
            return {'CANCELLED'}
        except AttributeError:
            self.report({'ERROR'}, "Invalid path - Attribute Error (Typo/Property does not exist)")
            return {'CANCELLED'}

        if prop is None:
            self.report({'ERROR'}, "Invalid path - None")
            return {'CANCELLED'}

        if new_path.endswith(']'):
            temp_path = '['.join(new_path.split('[')[:-1])
            temp_prop = eval(temp_path)
            temp_type = self.get_type(temp_path, temp_prop)

            # It's not a collection - remove the index
            if temp_type != 'OTHER':
                new_path = temp_path
                prop = temp_prop

        item_type = self.get_type(new_path, prop)

        # check if path is already in list
        for item in scene.cntrl_save_list:
            if item.path == new_path:
                self.report({'WARNING'}, "Path is already in list")
                break

        # add to list
        item = scene.cntrl_save_list.add()
        item.path = new_path
        item.struct_type = item_type

        configs.save_config()

        return {'FINISHED'}


class CNTRL_OT_AddCategorySeparator(bpy.types.Operator):
    bl_idname = "cntrl.add_category_separator"
    bl_label = "Add Category Separator"
    bl_description = "Add a separator to the panel"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        item = scene.cntrl_save_list.add()
        item.struct_type = 'CATEGORY_SEPARATOR'
        item.display_name = 'My Separator'

        configs.save_config()

        return {'FINISHED'}


class CNTRL_OT_AddCategoryEnd(bpy.types.Operator):
    bl_idname = "cntrl.add_category_end"
    bl_label = "Add Category End"
    bl_description = "Add a separator to the panel"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        item = scene.cntrl_save_list.add()
        item.struct_type = 'CATEGORY_END'

        configs.save_config()

        return {'FINISHED'}


class CNTRL_OT_MoveItem(bpy.types.Operator):
    bl_idname = "cntrl.move_item"
    bl_label = "Move Item"
    bl_description = "Move the selected item up or down in the list"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(options={'HIDDEN'})
    direction: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene

        if self.index + self.direction < 0:
            return {'CANCELLED'}

        if self.index + self.direction >= len(scene.cntrl_save_list):
            return {'CANCELLED'}

        scene.cntrl_save_list.move(self.index, self.index + self.direction)

        configs.save_config()

        return {'FINISHED'}


class CNTRL_OT_RemoveItem(bpy.types.Operator):
    bl_idname = "cntrl.remove_item"
    bl_label = "Remove Item"
    bl_description = "Remove the selected item from the panel"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        scene.cntrl_save_list.remove(self.index)

        configs.save_config()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CNTRL_OT_AddToPanel)
    bpy.utils.register_class(CNTRL_OT_AddCategorySeparator)
    bpy.utils.register_class(CNTRL_OT_AddCategoryEnd)
    bpy.utils.register_class(CNTRL_OT_MoveItem)
    bpy.utils.register_class(CNTRL_OT_RemoveItem)


def unregister():
    bpy.utils.unregister_class(CNTRL_OT_AddToPanel)
    bpy.utils.unregister_class(CNTRL_OT_AddCategorySeparator)
    bpy.utils.unregister_class(CNTRL_OT_AddCategoryEnd)
    bpy.utils.unregister_class(CNTRL_OT_MoveItem)
    bpy.utils.unregister_class(CNTRL_OT_RemoveItem)
