"""LSBSteg.py
Usage:
  LSBSteg.py encode -i <input> -o <output> -f <file>
  LSBSteg.py decode -i <input> -o <output>

Options:
  -h, --help                Show this help
  --version                 Show the version
  -f,--file=<file>          File to hide
  -i,--in=<input>           Input image (carrier)
  -o,--out=<output>         Output image (or extracted file)

example :
for text -->
python LSBSteg.py encode -i En_imag/captain.jpg -o Stegno_imag/captain_stegno1.png -f En_Msg/new.txt

python LSBSteg.py decode -i Stegno_imag/captain_stegno1.png -o DE_msg/captain_msg.txt

Image--->
python ImageLSB.py encode -i hist.png -o stegno12.png -f Capture.png

python ImageLSB.py decode -i stegno12.png -o imagelll.png
"""
import cv2
import docopt
import numpy as np

class SteganographyException(Exception):
    pass

class LSBSteg():
    def __init__(self, im):
        self.image = im
        self.height, self.width, self.nbchannels = im.shape
        self.size = self.width * self.height
        self.maskONEValues = [1,2,4,8,16,32,64,128]
        self.maskONE = self.maskONEValues.pop(0)
        self.maskZEROValues = [254,253,251,247,239,223,191,127]
        self.maskZERO = self.maskZEROValues.pop(0)
        
        self.curwidth = 0  
        self.curheight = 0 
        self.curchan = 0   

    def put_binary_value(self, bits):
       for c in bits:
            val = list(self.image[self.curheight,self.curwidth])

            if int(c) == 1:
                val[self.curchan] = int(val[self.curchan]) | self.maskONE 
            
            else:
                val[self.curchan] = int(val[self.curchan]) & self.maskZERO 
                
                
            self.image[self.curheight,self.curwidth] = tuple(val)
            
            self.next_slot() 
        
    def next_slot(self):
        if self.curchan == self.nbchannels-1: 
            self.curchan = 0
            if self.curwidth == self.width-1:
                self.curwidth = 0
                if self.curheight == self.height-1:
                    self.curheight = 0
                    if self.maskONE == 128: 
                        raise SteganographyException("No available slot remaining")
                    else: 
                        self.maskONE = self.maskONEValues.pop(0)
                        self.maskZERO = self.maskZEROValues.pop(0)
                else:
                    self.curheight +=1
            else:
                self.curwidth +=1
        else:
            self.curchan +=1


    def read_bit(self): #Read a single bit int the image
        val = self.image[self.curheight,self.curwidth][self.curchan]
        val = int(val) & self.maskONE
        self.next_slot()
        if val > 0:
            return "1"
        else:
            return "0"
    
    def read_byte(self):
        return self.read_bits(8)

    def read_bits(self, nb): #Read the given number of bits
        bits = ""
        for i in range(nb):
            bits += self.read_bit()
        return bits    

    def byteValue(self, val):
        return self.binary_value(val, 8)
        
    def binary_value(self, val, bitsize): 
        binval = bin(val)[2:]
        if len(binval) > bitsize:
            raise SteganographyException("binary value larger than the expected size")
        while len(binval) < bitsize:
            binval = "0"+binval
        return binval               
    
    def encode_binary(self, data):
        l = len(data)
        if self.width*self.height*self.nbchannels < l+64:
            raise SteganographyException("Carrier image not big enough to hold all the datas to steganography")
        self.put_binary_value(self.binary_value(l, 64))
        for byte in data:
            byte = byte if isinstance(byte, int) else ord(byte)
            self.put_binary_value(self.byteValue(byte))
        return self.image

    def decode_binary(self):
        l = int(self.read_bits(64), 2)
        if (l!=0 and l<50000):
            print("this image contain hidden msg")            
        else:
            a=1
            return a            
        d=int(input("you want to decode msg 1-Yes/0-No : "))
        if d==0:
                exit()
        output = b""
        for i in range(l):
            output += chr(int(self.read_byte(),2)).encode("utf-8")
        return output

    def decode_image(self):        
        width = int(self.read_bits(16),2) #Read 16bits and convert it in int
        height = int(self.read_bits(16),2)
        print(width,height)
        if width==0 or width > 2200:
            print("No text  and Image msg hide in image")
            exit()
        q=int(input("image have a secret msg \n do you want decode  1-->yes or 0-->  No"))
        if q==0:
            exit()
        unhideimg = np.zeros((width,height, 3), np.uint8) #Create an image in which we will put all the pixels read
        for w in range(width):        
            for h in range(height):
                for chan in range(3):
                    val = list(unhideimg[w,h])
                    val[chan] = int(self.read_byte(),2) #Read the value
                    unhideimg[w,h] = tuple(val)
        return unhideimg
    
    def encode_image(self, imtohide):
        (w1,h1,c) = imtohide.shape
        print(w1,h1,c)
        if self.width*self.height*self.nbchannels < w1*h1*c:
            raise SteganographyException("Carrier image not big enough to hold all the datas to steganography")
        binw = self.binary_value(w1, 16) #Width coded on to byte so width up to 65536
        binh = self.binary_value(h1, 16)
        self.put_binary_value(binw) #Put width
        self.put_binary_value(binh) #Put height
        for w in range(w1): #Iterate the hole image to put every pixel values
            for h in range(h1):
                for chan in range(c):
                    val = imtohide[w,h][chan]
                    self.put_binary_value(self.byteValue(int(val)))
        return self.image


def main():
    args = docopt.docopt(__doc__, version="0.2")
    in_f = args["--in"]
    out_f = args["--out"]
    
    in_img = cv2.imread(in_f)
    steg = LSBSteg(in_img)
    steg1=LSBSteg(in_img)

    if args['encode']:
        data=args["--file"]
        if ".txt" in data:
            data = open(data, "rb").read()
            res = steg.encode_binary(data)
            cv2.imwrite(out_f, res)
        else:
            img=cv2.imread(data)
            print(img.shape)
            res = steg.encode_image(img)
            cv2.imwrite(out_f, res)
        
        
    elif args["decode"]:
        raw = steg.decode_binary()
        if raw!=1:
          out_f+=".txt"
          with open(out_f, "wb") as f:
            f.write(raw)
        else :
            out_f+=".png"
            raw = steg1.decode_image()
            cv2.imwrite(out_f,raw)


if __name__=="__main__":
    main()

