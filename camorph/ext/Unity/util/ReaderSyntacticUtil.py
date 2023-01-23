import yaml
import re

def get_unity_from_yaml(yaml_txt):
    # we could add a tag constructor for unity objects
    # but as the only relevant information is the internal id
    # this is some magic regex to replace the tag with a proper yaml attribute
    yaml_txt = re.sub("%TAG.*", "", yaml_txt)
    yaml_txt = re.sub(r"(--- )([^&]*)&(\d*)(.*\n)(.*\n)", "---\n \g<5>  obj_id: \g<3>\n", yaml_txt)
    data = yaml.safe_load_all(yaml_txt)
    game_objs = []
    cameras = []
    transforms = []
    for unity_obj in data:
        if 'GameObject' in unity_obj:
            game_objs.append(unity_obj['GameObject'])
        elif 'Camera' in unity_obj:
            cameras.append(unity_obj['Camera'])
        elif 'Transform' in unity_obj:
            if 'm_GameObject' in unity_obj['Transform']:
                transforms.append(unity_obj['Transform'])

    return game_objs, cameras, transforms