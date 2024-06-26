from pathlib import Path
from mooseherder.mooseconfig import MooseConfig

USER_DIR = Path.home()

config = {'main_path': USER_DIR / 'moose',
          'app_path': USER_DIR / 'proteus',
          'app_name': 'proteus-opt'}

moose_config = MooseConfig(config)

save_path = Path.cwd() / 'moose-config.json'
moose_config.save_config(save_path)

save_path = Path.home() / 'py-workdir' / 'pycave' / 'scripts' / 'moose-config.json'
moose_config.save_config
