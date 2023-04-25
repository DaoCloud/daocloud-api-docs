import json
import yaml
import os

def merged_nav(master_nav,openapi_nav):
    if os.path.exists('navigation.yaml') and os.path.exists('openapi-nav.yaml'):
        # Load the master_nav YAML file
        with open(master_nav) as f:
            master = yaml.load(f, Loader=yaml.FullLoader)

        # Load the openapi YAML file
        with open(openapi_nav) as f:
            openapi = yaml.load(f, Loader=yaml.FullLoader)

        json_master = json.dumps(master, ensure_ascii=False)
        json_openapi = json.dumps(openapi, ensure_ascii=False)

        merged_nav = json.loads(json_master)['nav'] + json.loads(json_openapi)['nav']

        # Convert merged_nav to YAML and save to disk
        with open('all.yaml', 'w') as f:
            yaml.dump({'nav': merged_nav}, f, allow_unicode=True)
    else:
        print('One or both of the files do not exist.')


if __name__ == '__main__':
    merged_nav('navigation.yaml', 'openapi-nav.yaml')