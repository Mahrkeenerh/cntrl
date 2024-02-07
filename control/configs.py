import os
import json
import platform
import subprocess

import bpy


def save_config(dummy1 = None, dummy2 = None):
    scene = bpy.context.scene
    config_name = scene.cntrl_config_name
    config_path = os.path.join(os.path.dirname(__file__), 'configs', config_name + '.json')

    save_list = [x.to_json() for x in scene.cntrl_save_list]

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(save_list, f, indent=4)


def load_config():
    scene = bpy.context.scene
    config_name = scene.cntrl_config_name
    config_path = os.path.join(os.path.dirname(__file__), 'configs', config_name + '.json')

    if not os.path.exists(config_path):
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        save_list = json.load(f)

    scene.cntrl_save_list.clear()
    for item in save_list:
        new_item = scene.cntrl_save_list.add()
        new_item.from_json(item)


class CNTRL_OT_PackConfig(bpy.types.Operator):
    bl_idname = "cntrl.pack_config"
    bl_label = "Pack Config"
    bl_description = "Pack active config into the blend file"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.cntrl_config_name != ''

    def execute(self, context):
        scene = context.scene
        config_name = scene.cntrl_config_name
        config_path = os.path.join(os.path.dirname(__file__), 'configs', config_name + '.json')

        with open(config_path, 'r', encoding='utf-8') as f:
            save_list = json.load(f)

        packed_data = json.dumps(save_list, indent=4)
        if f'cntrl_pack_{config_name}' in bpy.data.texts:
            bpy.data.texts[f'cntrl_pack_{config_name}'].clear()
            bpy.data.texts[f'cntrl_pack_{config_name}'].write(packed_data)
        else:
            bpy.data.texts.new(f'cntrl_pack_{config_name}').write(packed_data)

        self.report({'INFO'}, f'Config {config_name} packed into blend file')

        return {'FINISHED'}


class CNTRL_OT_UnpackConfigs(bpy.types.Operator):
    bl_idname = "cntrl.unpack_configs"
    bl_label = "Unpack Configs"
    bl_description = "Unpack the saved config files in this blend file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        configs_path = os.path.join(os.path.dirname(__file__), 'configs')

        file_count = 0

        for text in bpy.data.texts:
            if text.name.startswith('cntrl_pack_'):
                config_name = text.name.replace('cntrl_pack_', '')
                config_path = os.path.join(configs_path, f'{config_name}.json')

                if config_name.split('_')[-1].isdigit():
                    i = int(config_name.split('_')[-1])
                    config_name = '_'.join(config_name.split('_')[:-1])
                else:
                    i = 0

                while os.path.exists(config_path):
                    i += 1
                    config_path = os.path.join(configs_path, f'{config_name}_{i:03}.json')

                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(text.as_string())
                
                file_count += 1

        if file_count == 0:
            self.report({'INFO'}, 'No configs found in blend file')
        else:
            self.report({'INFO'}, f'{file_count} configs unpacked from blend file')

        return {'FINISHED'}


class CNTRL_OT_NewConfig(bpy.types.Operator):
    bl_idname = "cntrl.new_config"
    bl_label = "New Config"
    bl_description = "Create a new config"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        configs_path = os.path.join(os.path.dirname(__file__), 'configs')

        config_name = 'config.json'
        all_configs = os.listdir(configs_path)
        config_number = 0
        while config_name in all_configs:
            config_number += 1
            config_name = f'config_{config_number:03}.json'

        config_path = os.path.join(configs_path, config_name)
        with open(config_path, 'w') as f:
            json.dump([], f, indent=4)

        scene.cntrl_configs = config_name.replace('.json', '')
        scene.cntrl_editing = True

        scene.cntrl_save_list.clear()
        scene.cntrl_new_path = ''

        return {'FINISHED'}


class CNTRL_OT_OpenFolder(bpy.types.Operator):
    bl_idname = "cntrl.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open the folder containing the configs"
    bl_options = {'REGISTER'}

    def execute(self, context):
        addon_configs_path = os.path.join(os.path.dirname(__file__), 'configs')
        if platform.system() == "Windows":
            os.startfile(addon_configs_path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", addon_configs_path])
        else:
            subprocess.Popen(["xdg-open", addon_configs_path])
        return {'FINISHED'}


class CNTRL_OT_EditToggle(bpy.types.Operator):
    bl_idname = "cntrl.edit_toggle"
    bl_label = "Edit Toggle"
    bl_description = "Toggle edit mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.cntrl_editing = not scene.cntrl_editing

        if scene.cntrl_configs == '':
            bpy.ops.cntrl.new_config()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CNTRL_OT_PackConfig)
    bpy.utils.register_class(CNTRL_OT_UnpackConfigs)
    bpy.utils.register_class(CNTRL_OT_NewConfig)
    bpy.utils.register_class(CNTRL_OT_OpenFolder)
    bpy.utils.register_class(CNTRL_OT_EditToggle)


def unregister():
    bpy.utils.unregister_class(CNTRL_OT_PackConfig)
    bpy.utils.unregister_class(CNTRL_OT_UnpackConfigs)
    bpy.utils.unregister_class(CNTRL_OT_NewConfig)
    bpy.utils.unregister_class(CNTRL_OT_OpenFolder)
    bpy.utils.unregister_class(CNTRL_OT_EditToggle)
