# Functions and methods for handling the msbt files found in the tears of the kingdom data
import util
import io
import sys
import time
import numpy as np
import pathlib
import os
import text_replacers

msbt_lib_path = pathlib.Path(__file__).parent / 'lib/EPD-Libraries/msbt/build/pymsbt3/'
sys.path.append(str(msbt_lib_path.absolute()))
import pymsbt3 as msbt

class MSBT:
    def __init__(self, msbt_path=None) -> None:
        if (msbt_path != None):
            self.load(msbt_path)
        else:
            return

    def replace_strings(self, replacement_method, **kwargs):
        start_time = time.time()
        entries = self.data.text_section.text_entries
        for entry in entries:
            current_msg = ""
            for segment in entry.values:
                current_msg += f' | {segment.text}'
                if segment.text != None:
                    self.data.text_section.text_entries[entries.index(entry)].values[entry.values.index(segment)].text = replacement_method(segment.text, **kwargs)

        function_time = time.time() - start_time
        print(f'Function completed in {function_time} seconds.')
        return

    def save(self):
        raw = self.data.ToBinary()
        print('Finished converting to binary')
        with open(str(self.path.absolute()), 'wb') as output:
            output.write(bytearray(raw))
            print('Saved file data')
        return

    def load(self, path):
        self.path = pathlib.Path(path)
        self.data = msbt.FromBinary(list(np.fromfile(str(self.path.absolute()), dtype='uint8')))
        return

def pass_val(data):
    #print(f"called pass_val function with value {data}")
    return "test string"

if __name__ == '__main__':
    msg = MSBT("D:/Console Stuff/Switch Stuff/Game Dumps/TotK/romfs/Mals/USen.Product.110/StaticMsg/Tips.msbt")
    data = msg.data
    msg.replace_strings(text_replacers.randomSentence)
    msg.save()
    print(data.ToText())