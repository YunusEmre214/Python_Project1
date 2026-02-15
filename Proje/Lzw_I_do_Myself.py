import math
import os
import numpy as np

class LZWCoding:

    def __init__(self,filename,data_type):
        self.filename=filename
        self.data_type=data_type
        self.codelength = None
    

    def compress_text_file(self):
      # get the current directory where this program is placed
      current_directory = os.path.dirname(os.path.realpath(__file__))
      # build the path of the input file
      input_file = self.filename + '.txt'
      input_path = current_directory + '/' + input_file
      # build the path of the output file
      output_file = self.filename + '.bin'
      output_path = current_directory + '/' + output_file

      # read the contents of the input file
      in_file = open(input_path, 'r')
      text = in_file.read().rstrip()
      in_file.close()

      # encode the text by using the LZW compression algorithm
      encoded_text_as_integers = self.compress(text)
      max_val = max(encoded_text_as_integers)
      self.codelength = max_val.bit_length()
      # get the binary string that corresponds to the compressed text
      encoded_text = self.int_array_to_binary_string(encoded_text_as_integers)
      # add the code length info to the beginning of the encoded text
      encoded_text = self.add_code_length_info(encoded_text)
      # perform padding if needed
      padded_encoded_text = self.pad_encoded_text(encoded_text)
      # convert the resulting string into a byte array
      byte_array = self.get_byte_array(padded_encoded_text)

      # write the bytes in the byte array to the output file (compressed file)
      out_file = open(output_path, 'wb')   # binary mode
      out_file.write(bytes(byte_array))
      out_file.close()

      # notify the user that the compression process is finished
      print(input_file + ' is compressed into ' + output_file + '.')
      # compute and print the details of the compression process
      uncompressed_size = len(text)
      print('Uncompressed Size: ' + '{:,d}'.format(uncompressed_size) + ' bytes')
      print('Code Length: ' + str(self.codelength))
      compressed_size = len(byte_array)
      print('Compressed Size: ' + '{:,d}'.format(compressed_size) + ' bytes')
      compression_ratio = uncompressed_size / compressed_size
      print('Compression Ratio: ' + '{:.2f}'.format(compression_ratio))

      # return the path of the output file
      return output_path
    

    def decompress_text_file(self):
      # get the current directory where this program is placed
      current_directory = os.path.dirname(os.path.realpath(__file__))
      # build the path of the input file
      input_file = self.filename + '.bin'
      input_path = current_directory + '/' + input_file
      # build the path of the output file
      output_file = self.filename + '_decompressed.txt'
      output_path = current_directory + '/' + output_file

      # read the contents of the input file
      in_file = open(input_path, 'rb')   # binary mode
      bytes = in_file.read()
      in_file.close()

      # create a binary string from the bytes read from the file
      from io import StringIO   # using StringIO for efficiency
      bit_string = StringIO()
      for byte in bytes:
         bits = bin(byte)[2:].rjust(8, '0')
         bit_string.write(bits)
      bit_string = bit_string.getvalue()

      # remove padding
      bit_string = self.remove_padding(bit_string)
      # remove the code length info and set the instance variable codelength
      bit_string = self.extract_code_length_info(bit_string)
      # convert the compressed binary string to a list of integer values
      encoded_text = self.binary_string_to_int_list(bit_string)
      # decode the encoded text by using the LZW decompression algorithm
      decompressed_text = self.decompress(encoded_text)

      # write the decompression output to the output file
      out_file = open(output_path, 'w')
      out_file.write(decompressed_text)
      out_file.close()

      # notify the user that the decompression process is finished
      print(input_file + ' is decompressed into ' + output_file + '.')
      
      # return the path of the output file
      return output_path
        


    def compress(self,uncompressed):
        """Compress a string to a list of output symbols."""
        dict_size=256
        dictionary={chr(i):i for i in range(dict_size)}

        w=""
        result=[]
        for c in uncompressed:
            wc=w+c
            if wc in dictionary:
                w=wc
            else:
                result.append(dictionary[w])
                dictionary[wc]=dict_size
                dict_size+=1
                w=c
        if w:
            result.append(dictionary[w])
        return result
    
    def decompress(self,compressed):
        """Decompress a list of output ks to a string."""
        from io import StringIO

        dict_size=256
        dictionary={i:chr(i) for i in range(dict_size)}

        result=StringIO()
        w=chr(compressed.pop(0))
        result.write(w)
        for k in compressed:
            if k in dictionary:
                entry=dictionary[k]
            elif k==dict_size:
                entry=w+w[0]
            else:
                raise ValueError("Bad compressed k:%s"%k)
            result.write(entry)

            dictionary[dict_size]=w+entry[0]
            dict_size+=1

            w=entry
        return result.getvalue()



    def calculate_compression_ratio(self,uncompressed_size,compressed_size):
        ratio=uncompressed_size/compressed_size
        saving=(1-(compressed_size/uncompressed_size))*100

        print(f"Original:{uncompressed_size} bytes")
        print(f"Compressed:{compressed_size} bytes")
        print(f"Ratio:{ratio:.2f}")
        print(f"Saving:%{saving:.2f}")


    def pad_encoded_text(self,encoded_text):
        extra_padding=8-len(encoded_text)%8
        for i in range(extra_padding):
            encoded_text+="0"
        
        padded_info="{0:08b}".format(extra_padding)
        print("Padded info:",padded_info)
        encoded_text=padded_info+encoded_text
        return encoded_text
        

    def get_byte_array(self,padded_encoded_text):
        if(len(padded_encoded_text)%8!=0):
            print("Encoded text not padded properly")
            exit(0)
        
        b=bytearray()
        for i in range(0,len(padded_encoded_text),8):
            byte=padded_encoded_text[i:i+8]
            b.append(int(byte,2))
        return b


    def int_array_to_binary_string(self,int_array):
        bitstr=""
        bits=self.codelength

        for num in int_array:
            for n in range(bits):
                if num &(1<<(bits-1-n)):
                    bitstr+="1"
                else:
                    bitstr+="0"
        return(bitstr)
    

    def binary_string_to_int_list(self, bitstring):
      
      int_codes = []
      for bits in range(0, len(bitstring), self.codelength):
         int_code = int(bitstring[bits: bits + self.codelength], 2)
         int_codes.append(int_code)
      
      return int_codes

    

    def remove_padding(self,padded_encoded_text):
      padding_info = padded_encoded_text[:8]
      encoded_data = padded_encoded_text[8:]
      
      extra_padding = int(padding_info, 2) 
      if extra_padding != 0:
         encoded_data = encoded_data[:-1 * extra_padding]
      return encoded_data


    def add_code_length_info(self, bitstring):
      codelength_info = '{0:08b}'.format(self.codelength)
      bitstring = codelength_info + bitstring
      
      return bitstring
    
    def extract_code_length_info(self, bitstring):
      codelength_info = bitstring[:8]
      self.codelength = int(codelength_info, 2)
      
      return bitstring[8:]
    
if __name__ == "__main__":
    # Dosya adını buraya yaz (uzantısız)
    file_to_test = "short_text" 
    
    # Sınıfı başlat
    lzw = LZWCoding(file_to_test, "text")
    
    # 1. Sıkıştır
    print("Sıkıştırma başlıyor...")
    lzw.compress_text_file()
    
    # 2. Geri Aç
    print("\nGeri açma başlıyor...")
    lzw.decompress_text_file()
    
    print("\nİşlem başarıyla tamamlandı.")
