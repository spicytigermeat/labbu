import sys, os, re, glob
sys.path.append(os.getcwd())
import labbu
import click

@click.command()
@click.option(
	'--check_path',
	'-p',
	type=str,
	required=True,
	help='Path of labels to check.'
	)
@click.option(
	'--lang',
	'-l',
	type=click.Choice(['default', 'japanese', 'millefeuille', 'custom']),
	default='default',
	required=False,
	help='Language of labels.'
	)
@click.option(
	'--custom_lang',
	'-cl',
	type=str,
	required=False,
	help='Path to custom language yaml file, if \'--lang\' is \'custom\''
	)

def main(check_path, lang, custom_lang):
	try:
		if lang.lower() == 'custom':
			labu = labbu.labbu()
			labu.define_custom_lang(custom_lang)
		else:
			labu = labbu.labbu(lang=lang)
	except: 
		print('Error loading labbu.')

	for lab in glob.glob(f"{check_path}/**/*.lab", recursive=True):
		labu.load_lab(lab)
		labu.check_label()

if __name__ == '__main__':
	main()