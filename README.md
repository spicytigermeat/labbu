# labbu
"labbu" is a tool created to assist in contextual editing of phonetic "lab" files. These files are common place in a lot of SVS tools. (DiffSinger, NNSVS, etc)
# Quick Usage
To quickly and easily convert MFA TextGrids to Labs you can use this notebook:   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1_U8sEel7T8QAYBi3nrwTucnG4marIfxb?usp=sharing)<br>
<sub>Please Note: Currenly, I have only implemented support for English and Japanese in the notebook, but by editing code you can do it with any.</sub>
# Basic Usage
Currently, labbu must be installed manually, and the only dependency is ```mytextgrid```, so make sure that's installed first! Simply download "labbu.py" and place it in the folder you'll be using other code out of. Below is an example of a script that will replace all label indexes with [SP] as the phoneme with [slay], but only if the next phoneme is [aa]. All information about the lab is saved in the object, which I recommend calling "labu" for the sake of consistency.
```python
import labbu

labu = labbu.labbu()
labu.load_lab({file_path_to_label})

for i in range(len(labu.get_length())): #check in each index of the lab file
  if labu.curr_phone(i) == 'SP' and labu.next_phone(i) == 'aa':
    labu.change_phone(i, 'slay')

labu.export_lab({output_path})
```
Further documentation and examples will come as labbu is developed.
# Citations
Loading from Praat TextGrid was referenced from [Overdramatic's "text2lab" (Thank you!)](https://github.com/overdramatic/text2lab)
