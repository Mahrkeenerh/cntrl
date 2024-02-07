# YES, THIS IS JUST COPIED FROM SERPENS

import bpy


REPLACE_NAMES = {
    "ObjectBase": "bpy.data.objects['Object']", # outliner object hide
    "LayerCollection": "bpy.context.view_layer.active_layer_collection", # outliner collection hide
    "SpaceView3D": "bpy.context.screen.areas[0].spaces[0]", # 3d space data
    "ToolSettings": "bpy.context.scene.tool_settings", # any space tool settings
}


class WM_MT_button_context(bpy.types.Menu):
    bl_label = ""

    def draw(self, context):
        pass


class CNTRL_OT_CopyProperty(bpy.types.Operator):
    bl_idname = "cntrl.copy_property"
    bl_label = "Copy Property"
    bl_description = "Copy the path of this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        # get property details
        property_pointer = getattr(context, "button_pointer", None)
        property_value = getattr(context, "button_prop", None)

        # copy data path if available
        if bpy.ops.ui.copy_data_path_button.poll():
            bpy.ops.ui.copy_data_path_button("INVOKE_DEFAULT", full_path=True)

            path = context.window_manager.clipboard.replace('"', "'")

            if path and path[-1] == "]" and path[:-1].split("[")[-1].isdigit():
                path = "[".join(path.split("[")[:-1])

            context.window_manager.clipboard = path

            context.scene.cntrl_new_path = context.window_manager.clipboard

            self.report({"INFO"}, message="Copied!")

            return {"FINISHED"}

        # check if replacement is available
        if property_pointer and property_value:
            if property_pointer.bl_rna.identifier in REPLACE_NAMES:
                context.window_manager.clipboard = f"{REPLACE_NAMES[property_pointer.bl_rna.identifier]}.{property_value.identifier}"
                context.window_manager.clipboard = context.window_manager.clipboard.replace('"', "'")
                context.scene.cntrl_new_path = context.window_manager.clipboard
                self.report({"INFO"}, message="Copied!")
                return {"FINISHED"}

        # error when property not available
        self.report({"ERROR"}, message="Can't copy this property, you'll have to do it manually!")
        return {"CANCELLED"}


class CNTRL_OT_CopyOperator(bpy.types.Operator):
    bl_idname = "cntrl.copy_operator"
    bl_label = "Copy Operator"
    bl_description = "Copy the path of this operator"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def find_ops_path_from_rna(self, rna_identifier):
        for cat_name in dir(bpy.ops):
            if cat_name[0].isalpha() and not cat_name == "class":
                try: cat = eval(f"bpy.ops.{cat_name}")
                except: cat = None
                if cat:
                    for op_name in dir(cat):
                        if op_name[0].isalpha():
                            try: op = eval(f"bpy.ops.{cat_name}.{op_name}")
                            except: op = None
                            if op and op.get_rna_type().identifier == rna_identifier:
                                return f"bpy.ops.{cat_name}.{op_name}()"
        return None

    def execute(self, context):
        # copy operator if available
        if bpy.ops.ui.copy_python_command_button.poll():
            bpy.ops.ui.copy_python_command_button("INVOKE_DEFAULT")
            context.scene.cntrl_new_path = context.window_manager.clipboard
            self.report({"INFO"}, message="Copied!")
            return {"FINISHED"}

        # get button details
        button_value = getattr(context, "button_operator", None)    

        # check if value exists
        if button_value:
            op_path = self.find_ops_path_from_rna(button_value.bl_rna.identifier)
            if op_path:
                context.window_manager.clipboard = op_path
                context.scene.cntrl_new_path = context.window_manager.clipboard
                self.report({"INFO"}, message="Copied!")
                return {"FINISHED"}

        # error when button not available
        self.report({"ERROR"}, message="Can't copy this operator, you'll have to do it manually!")
        return {"CANCELLED"}


def control_right_click(self, context):
    layout = self.layout

    property_pointer = getattr(context, "button_pointer", None)
    property_value = getattr(context, "button_prop", None)
    button_value = getattr(context, "button_operator", None)    

    if property_value or button_value:
        layout.separator()

    if property_value and property_pointer:
        layout.operator("cntrl.copy_property", text="Get Control Property", icon="COPYDOWN")

    if button_value:
        layout.operator("cntrl.copy_operator", text="Get Control Operator", icon="COPYDOWN")


def register():
    bpy.utils.register_class(CNTRL_OT_CopyProperty)
    bpy.utils.register_class(CNTRL_OT_CopyOperator)

    rcmenu = getattr(bpy.types, "WM_MT_button_context", None)
    if rcmenu is None:
        bpy.utils.register_class(WM_MT_button_context)
        rcmenu = WM_MT_button_context

    # Retrieve a python list for inserting draw functions.
    draw_funcs = rcmenu._dyn_ui_initialize()
    draw_funcs.append(control_right_click)


def unregister():
    bpy.utils.unregister_class(CNTRL_OT_CopyProperty)
    bpy.utils.unregister_class(CNTRL_OT_CopyOperator)

    bpy.types.WM_MT_button_context.remove(control_right_click)
