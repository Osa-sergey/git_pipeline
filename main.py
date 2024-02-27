import os

from omegaconf import OmegaConf
from glob import glob
from colorama import init, Back
import polars as pl
import mmh3
import mlflow

from git_utils.save_pipeline import save_pipe_to_git
try: from pip._internal.operations import freeze
except ImportError: # pip < 10.0
    from pip.operations import freeze

#инит 
path = 'conf'

def load_config(path):
	files_cfg = []
	for file in glob(os.path.join(path, '*.yaml')):
		files_cfg.append(OmegaConf.load(file))
	cfg = OmegaConf.merge(*files_cfg)
	return cfg

cfg = load_config(path)

init()

mlflow_cfg = cfg.mlflow
mlflow.set_tracking_uri(uri=mlflow_cfg.uri)
mlflow.set_experiment(mlflow_cfg.exp_name)
mlflow.start_run(run_name=mlflow_cfg.run_name, description=mlflow_cfg.run_description)

pkgs = freeze.freeze()
pkgs = ('\n').join([pkg for pkg in pkgs])
mlflow.log_text(pkgs, 'requirements.txt')

mlflow.log_params(mlflow_cfg.log_params)


for i in range(5):
	mlflow.log_metric(key='train_loss', value=i*3, step=i)
	mlflow.log_metric(key='val_loss', value=15 - i*2, step=i)




mlflow.log_dict(OmegaConf.to_container(cfg), 'config.yaml')

df = pl.read_csv('ex.csv')
seed = 42

# убрать в init датасета
row_hashes = df.hash_rows(seed=seed)
hasher = mmh3.mmh3_x64_128(seed=seed)
# убрать в датасет
# добавить логирование количества семплов 
for row_hash in row_hashes:
    hasher.update(row_hash.to_bytes(64, "little"))
print(f'data hash: {hasher.digest().hex()}')


print(f'{Back.BLUE}debug_mode: {cfg.debug}')
if not cfg.debug:
	save_pipe_to_git(cfg.git)


		