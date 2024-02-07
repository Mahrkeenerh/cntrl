import os

import bpy

from . import configs


ignore_change = False

# vector_selections = {}

class CNTRL_GROUP_SaveList(bpy.types.PropertyGroup):
    display_name: bpy.props.StringProperty(
        name="Display Name",
        description="Name of the property or operator",
        default="",
        update=configs.save_config
    )
    path: bpy.props.StringProperty(
        name="Path",
        description="Python path to the property or operator",
        default=""
    )
    struct_type: bpy.props.EnumProperty(
        name="Type",
        description="Type of the property or operator",
        items=[
            ('CATEGORY_SEPARATOR', 'Category Separator', 'Category Separator'),
            ('CATEGORY_END', 'Category End', 'Category End'),
            ('OPERATOR', 'Operator', 'Operator'),
            ('INT', 'Integer', 'Integer'),
            ('FLOAT', 'Float', 'Float'),
            ('BOOL', 'Boolean', 'Boolean'),
            ('INT_VECTOR', 'Integer Vector', 'Integer Vector'),
            ('FLOAT_VECTOR', 'Float Vector', 'Float Vector'),
            ('BOOL_VECTOR', 'Boolean Vector', 'Boolean Vector'),
            ('OTHER', 'Other', 'Other')
        ],
        default='OPERATOR'
    )
    # map_min: bpy.props.FloatProperty(
    #     name="Min",
    #     description="Minimum value for midi mapping",
    #     default=0.0,
    #     update=configs.save_config
    # )
    # map_max: bpy.props.FloatProperty(
    #     name="Max",
    #     description="Maximum value for midi mapping",
    #     default=1.0,
    #     update=configs.save_config
    # )

    # def vector_selection_generator(self, context):
    #     prop = eval(self.path)
    #     if prop is None:
    #         return []
    #     if 'VECTOR' not in self.struct_type:
    #         return []

    #     for i in range(len(prop)):
    #         if i not in vector_selections:
    #             vector_selections[i] = (str(i), str(i), str(i))

    #     return [vector_selections[i] for i in range(len(prop))]

    # vector_selection: bpy.props.EnumProperty(
    #     name="Vector Selection",
    #     description="Select the vector component to map to midi",
    #     items=vector_selection_generator,
    #     options={'ENUM_FLAG'},
    #     update=configs.save_config
    # )

    def to_json(self):
        return {
            'display_name': self.display_name,
            'path': self.path,
            'struct_type': self.struct_type,
            # 'map_min': self.map_min,
            # 'map_max': self.map_max,
            # 'vector_selection': list(self.vector_selection)
        }

    def from_json(self, json):
        self.display_name = json['display_name']
        self.path = json['path']
        self.struct_type = json['struct_type']
        # self.map_min = json['map_min']
        # self.map_max = json['map_max']
        # self.vector_selection = set(json['vector_selection'])


def get_configs(self, context):
    addon_configs_path = os.path.join(os.path.dirname(__file__), 'configs')
    configs = [config for config in os.listdir(addon_configs_path) if config.endswith('.json')]
    configs = [config.replace('.json', '') for config in configs]

    return [(config, config, config) for config in configs]


def on_config_change(self, context):
    global ignore_change

    if ignore_change:
        return

    if self.cntrl_configs == '':
        return

    ignore_change = True
    self.cntrl_config_name = self.cntrl_configs
    ignore_change = False

    configs.load_config()


def set_config_name(self, value):
    global ignore_change

    # old_value = self["cntrl_config_name"]
    old_value = getattr(self, "cntrl_config_name", "")
    self['cntrl_config_name'] = value

    if ignore_change or old_value == value:
        return

    old_config_path = os.path.join(os.path.dirname(__file__), 'configs', old_value + '.json')
    new_config_path = os.path.join(os.path.dirname(__file__), 'configs', value + '.json')

    i = value.split('_')[-1]
    if i.isdigit():
        i = int(i)
    else:
        i = 0
    while os.path.exists(new_config_path):
        i += 1
        value = f'config_{i:03}'
        new_config_path = os.path.join(os.path.dirname(__file__), 'configs', value + '.json')

    os.rename(old_config_path, new_config_path)
    ignore_change = True
    self.cntrl_configs = value
    ignore_change = False
    self['cntrl_config_name'] = value


def redraw_panel(self, context):
    for region in context.area.regions:
        if region.type == "UI":
            region.tag_redraw()


def register():
    bpy.types.Scene.cntrl_configs = bpy.props.EnumProperty(
        name="Configurations",
        description="Select the panel configuration to load",
        items=get_configs,
        update=on_config_change
    )
    bpy.types.Scene.cntrl_editing = bpy.props.BoolProperty(
        name="Editing",
        description="Enable editing mode",
        default=False
    )
    bpy.types.Scene.cntrl_config_name = bpy.props.StringProperty(
        name="Config Name",
        description="Name of the configuration",
        default="",
        get=lambda self: self.cntrl_configs,
        set=set_config_name
    )

    bpy.types.Scene.cntrl_new_path = bpy.props.StringProperty(
        name="New Path",
        description="Python path to the property or operator",
        default="",
        update=redraw_panel
    )

    bpy.utils.register_class(CNTRL_GROUP_SaveList)
    bpy.types.Scene.cntrl_save_list = bpy.props.CollectionProperty(type=CNTRL_GROUP_SaveList)


def unregister():
    del bpy.types.Scene.cntrl_configs
    del bpy.types.Scene.cntrl_new_path
    del bpy.types.Scene.cntrl_save_list
    bpy.utils.unregister_class(CNTRL_GROUP_SaveList)

    del bpy.types.Scene.cntrl_editing
    del bpy.types.Scene.cntrl_config_name
