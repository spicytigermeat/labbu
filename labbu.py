import sys, os, re
import mytextgrid
from pathlib import Path

class labbu:
	def __init__(self, lang='default'):
		super().__init__()
		#initialize language from kwargs
		if lang != 'default':
			with open(lang, 'r', encoding='utf-8') as f:
				self.pho_dict = {line.split(' ')[0]: line.rstrip().split(' ')[1] for line in f}
				f.close()
		else:
			#default to my prewritten phoneme dictionary
			self.pho_dict={
		'AP':'stop', 'SP':'stop', 
		'pau':'stop', 'sil':'stop',
		'a':'vowel', 'aa':'vowel', 'ae':'vowel', 'ah':'vowel', 'ao':'vowel', 'aw':'vowel', 'ax':'vowel', 'ay':'vowel', 
		'b':'stop', 'bcl':'stop', 'by':'stop',
		'cl':'stop', 'ch':'affricate',
		'd':'stop', 'dh':'fricative', 'dx':'stop', 'dcl':'stop', 'dy':'stop',
		'e':'vowel', 'eh':'vowel', 'er':'vowel', 'en':'vowel', 'eng':'vowel', 'ey':'vowel', 'el':'vowel', 'em':'vowel', 'ee':'vowel',
		'f':'fricative', 'fy':'fricative',
		'g':'stop', 'gcl':'stop', 'gy':'stop',
		'hh':'fricative', 'h':'fricative', 'hy':'fricative', 'hv':'fricative',
		'i':'vowel', 'ih':'vowel', 'iy':'vowel', 'ix':'vowel', 'ii':'vowel',
		'j':'fricative', 'jh':'affricate',
		'k':'stop', 'kcl': 'stop', 'ky':'stop',
		'l':'liquid',
		'm':'nasal', 'my':'nasal',
		'n':'nasal', 'ng':'nasal', 'nx':'nasal', 'ny':'nasal', 'N':'nasal',
		'o':'vowel', 'ow':'vowel', 'ox':'vowel', 'oy':'vowel', 'oo':'vowel',
		'p':'stop', 'pcl':'stop', 'py':'stop',
		'q':'stop',
		'r':'liquid', 'rr':'stop', 'rx':'fricative', 'ry':'stop',
		's':'fricative', 'sh':'fricative',
		't':'stop', 'tcl':'stop', 'th':'fricative', 'ty':'stop',
		'u':'vowel', 'uh':'vowel', 'uw':'vowel', 'uu':'vowel', 'ux':'vowel',
		'v':'fricative', 'vf':'stop',
		'w':'semivowel',
		'y':'semivowel',
		'z':'fricative', 'zh':'fricative',
		'spn': 'stop'}

		self.palatal_consonants = ['by', 'dy', 'fy', 'gy', 'hy',
								   'jy', 'ky', 'ly', 'my', 'ny',
								   'py', 'ry', 'ty', 'vy', 'zy']
		self.plosive_consonants = ['b', 'bcl', 'd', 'dcl', 'g', 'gcl', 'k', 'kcl', 'p', 'pcl', 't', 'tcl']
		self.silence_phones = ['SP', 'pau', 'sil', 'spn']
		self.breath_phones = ['AP', 'br']
		self.depal_length = 355000

	#loads the label. can be used to save a lab to a dict as well
	def load_lab(self, fpath):
		#load lab file
		#syntax: [['phoneme', 'time_start', 'time_end']]
		self.lab = []
		with open(fpath, 'r', encoding='utf-8') as f:
			for line in f:
				split_line = line.rstrip().split(' ')
				self.lab.append({'phone': split_line[2],'start': split_line[0],'end': split_line[1]})
			f.close()
		return self.lab

	#loads lab from textgrid. meant for MFA TextGrids :3
	#code referenced from the amazing HAI-D (overdramatic on github)
	def load_lab_from_textgrid(self, fpath, silence='SP', breath='AP'):
		self.lab = []
		tg = mytextgrid.read_from_file(fpath)
		for tier in tg:
			if tier.name == 'phones' and tier.is_interval():
				for interval in tier:
					time_start = int(float(interval.xmin)*10000000)
					time_end = int(float(interval.xmax)*10000000)
					label = interval.text
					if label == '':
						label = silence
					if label in self.breath_phones:
						label = breath
					self.lab.append({'phone': label,'start': time_start,'end': time_end})
		return self.lab

	#debug/reference to print the phoneme dictionary.
	def validate_phonemes(self):
		print('PHONE - TYPE\n')
		for key in self.pho_dict:
			print(f"{key} - {self.pho_dict[key]}")

	#check if any stray phonemes are in the label
	def check_label(self):
		print('Checking label!\n')
		for i in range(self.get_length()):
			if self.lab[i]['phone'] in self.pho_dict:
				pass
			else:
				print(f"ERR @ {i}:\t{self.lab[i]['phone']}")

	#checks if current index is the first or last in the label
	def is_boe(self, i):
		return True if i == 0 or i == len(self.lab) else False

	#returns the length of the label as an int
	def get_length(self):
		return len(self.lab) 

	#overwrite the phoneme at a given index: labu.overwrite_phone(i, 'aa')
	def overwrite_phone(self, i, new_phone):
		self.lab[i]['phone'] = new_phone

	#merges the current index with the next index: labu.merge_phones(i, 'cl')
	def merge(self, i, new_phone):
		if not self.is_boe(i):
			try:
				new_start = self.lab[i]['start']
				new_end = self.lab[i+1]['end']
				self.lab.pop(i+1)
				self.lab[i]['start'] = new_start
				self.lab[i]['end'] = new_end
				self.lab[i]['phone'] = new_phone
			except:
				pass
		else:
			print(f'Unable to merge label at index {i}. Make sure it is not the end of the file!')

	#makes palatalized consonants [ky] into 2 seperate consonants [k] [y]
	#places the end of [y] 355000 units into the consonant, to guess where it would be?
	#input should be index of palatilized consonant
	def depalatilize(self, i):
		#check if next label is a vowel
		assert self.is_type(self.lab[i]['phone'], 'palatal')
		if self.is_type(self.next_phone(i), 'vowel'):
			#define where the y be starting!
			y_start = int(self.lab[i]['end'])
			y_end = y_start + self.depal_length
			#update vowel
			self.lab[i+1]['start'] = y_end
			#rename original phoneme to remove y
			self.lab[i]['phone'] = self.lab[i]['phone'][0]
			#finally, insert the new lab
			self.lab.insert(i+1, {'phone': 'y','start': y_start,'end': y_end})

	def get_pho_len(self, i):
		return int(self.lab[i]['end']) - int(self.lab[i]['start'])

	#splits label in half
	def split_label(self, i, pho1, pho2):
		p1_start = int(self.lab[i]['start'])
		p2_end = int(self.lab[i]['end'])
		p1_end = p1_start + int(self.get_pho_len(i) / 2)
		p2_start = p1_end

		self.lab[i]['phone'] = pho1
		self.lab[i]['start'] = p1_start
		self.lab[i]['end'] = p1_end
		self.lab.insert(i+1, {'phone': pho2, 'start': p2_start, 'end': p2_end})

	#replaces all instances with new phone
	def replace_all(self, old_phone, new_phone):
		for i in range(self.get_length()):
			if self.lab[i]['phone'] == old_phone:
				self.lab[i]['phone'] = new_phone

	#returns the current phoneme at a given index
	def curr_phone(self, i):
		if self.is_boe(i):
			pass
		else:
			try:
				return self.lab[i]['phone']
			except IndexError:
				print('IndexError: Please verify your output is correct!')
				pass

	#returns the phoneme directly before a given index
	def prev_phone(self, i):
		if self.is_boe(i):
			pass
		else:
			try:
				return self.lab[i-1]['phone']
			except IndexError:
				print('IndexError: Please verify your output is correct!')
				pass

	#returns the phoneme directly after a given index
	def next_phone(self, i):
		if self.is_boe(i):
			pass
		else:
			try:
				return self.lab[i+1]['phone']
			except IndexError:
				print('IndexError: Please verify your output is correct!')
				pass

	#returns true if phoneme (arg1) is a certain type (arg2)
	# labu.is_type('aa', 'vowel') returns 'True'
	def is_type(self, phone, ph_type):
		try:
			if ph_type == 'plosive':
				return True if phone in self.plosive_consonants else False
			elif ph_type == 'palatal':
				return True if phone in self.palatal_consonants and not self.is_type(phone, 'vowel') else False
			elif ph_type == 'silence':
				return True if phone in self.silence_phones else False
			else:
				curr_type = self.pho_dict[phone]
				return True if curr_type == ph_type else False
		except KeyError as e:
			print(f"ERR: Phoneme not defined, returning False | {e}")
			return False

	def export_lab(self, output_name): #exports the label file
		#build output string
		output_text = ''
		for i in range(self.get_length()):
			output_text += f"{self.lab[i]['start']} {self.lab[i]['end']} {self.lab[i]['phone']}\n"

		if not output_name.endswith('.lab'):
			p = Path(output_name)
			output_name = p.stem + '.lab'

		with open(output_name, 'w+', encoding='utf-8') as out:
			out.seek(0)
			out.write(output_text)
			out.close()

	#remove any numbers from the phone and lower it, but leave SP and AP alone
	def clean_phones(self, i):
		if self.curr_phone(i) != 'SP' or self.curr_phone(i) != 'AP':
			try:
				new_phone = re.sub(r'[0-9]', '', self.curr_phone(i))
				self.overwrite_phone(i, new_phone.lower())
			except TypeError as e:
				print(f"Type Error at {i}: {e}")

	def clean_all_phones(self):
		for i in range(self.get_length()):
			self.clean_phones(i)

	#ensures there are no conflicts of timing in labels
	def normalize_time(self):
		for i in range(self.get_length()):
			if self.lab[i]['start'] == self.lab[i-1]['end']:
				pass
			else:
				self.lab[i]['start'] = self.lab[i-1]['end']

	#gets the mean of each occurance of a phoneme
	def get_mean_phone_length(self, phone):
		dur_list = []
		for i in range(self.get_length()):
			if self.lab.curr_phone(i) == phone:
				dur_list.append(self.get_pho_len(i))
		return dur_list.mean()

	#this is untested heehee
	def adjust_lab_end(self, i, factor):
		new_end = self.lab[i]['end'] + factor
		self.lab[i]['end'] = new_end
		self.lab[i+1]['start'] = new_end

	def is_between_vowels(self, i):
		return True if self.is_type(self.next_phone(i), 'vowel') and self.is_type(self.prev_phone(i), 'vowel') else False

	#converts lab from enunu-style to diffsinger-style
	#(pau, br) > (SP, AP)
	def enunu2diff(self):
		self.replace_all('pau', 'SP')
		self.replace_all('br', 'AP')

	def diff2enunu(self):
		self.replace_all('SP', 'pau')
		self.replace_all('AP', 'br')

	#unloads the label, you never know if you'll need it
	def unload_lab(self):
		del self.lab
		self.lab = []

	def fix_spap(self):
		for i in range(self.get_length()):
			if self.lab[i]['phone'] == 'sp' or self.lab[i]['phone'] == 'ap':
				self.lab[i]['phone'] = self.lab[i]['phone'].upper()

if __name__ == '__main__':
	labu = labbu()
