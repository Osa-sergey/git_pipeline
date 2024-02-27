import re
import os


from omegaconf import OmegaConf
from git import Repo
from colorama import Back
import mlflow
from glob import glob

def save_pipe_to_git(cfg):
	repo = Repo()
	check_git_config(repo, cfg)

	untracked_files = repo.untracked_files
	print(f'{Back.GREEN}untracked_files:')
	for file in untracked_files:
		print(file)
	print()
	changed_files = 0
	print(f'{Back.GREEN}changed files:')
	for file in repo.index.diff(None):
		print(file)
		changed_files += 1

	if changed_files > 0 or len(untracked_files) > 0:
		repo.git.add(all=True)
		commit_msg = (OmegaConf.to_yaml(cfg, resolve=True) if cfg.message == 'config'
			   		 else cfg.message)
		repo.git.commit('-m', commit_msg, author=cfg.author)
	print(f'{Back.BLUE}commit hash: {repo.head.commit.hexsha}')
	mlflow.set_tag('git_commit_hash', repo.head.commit.hexsha)



def check_git_config(repo, cfg):
	errors = []
	if not str(repo.head.ref).startswith('exp'):
		errors.append('Experiment not in "exp*" branch')
	if 'author' not in cfg or not re.match(r'^[а-яА-ЯA-Za-z ]* <[A-Za-z.@]*>$', cfg.author):
	 	errors.append('Add commit author to cfg.author with "name <email>" format')
	if 'message' not in cfg or cfg.message is None or cfg.message == '':
		errors.append('Add commit message text or "config" to set config params as message')
	prep_data_cfg = cfg.prepared_data
	data_files = glob(os.path.join(prep_data_cfg.allowed_folder, '*')) 
	for data_file in data_files:
		if os.path.basename(data_file) not in prep_data_cfg.allowed_prep_data:
			errors.append(f'Not allowed data file: {data_file}')
	if len(errors) > 0:
		raise Exception('\n- '.join(errors))
