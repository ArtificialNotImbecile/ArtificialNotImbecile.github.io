---
layout: post
comments: true
title:  "UTF-8"
excerpt: "Explain UTF-8 and implement in python from scratch"
date:   2022-04-18 15:00:00
mathjax: true
---

### Unicode (or Universal Coded Character Set) Transformation Format – 8-bit
1. Code points with lower numerical values, which tend to occur more frequently, are encoded using fewer bytes
2. backward compatible with ascii

### Encoding

|First code poin | Last code point | Byte 1 | Byte 2 | Byte 3 | Byte 4|
| --- | --- | --- | --- | --- | ---|
|U+0000 | U+007F | 0xxxxxxx	|          |          |
|U+0080 | U+07FF | 110xxxxx | 10xxxxxx |
|U+0800 | U+FFFF | 1110xxxx | 10xxxxxx | 10xxxxxx |	
|U+10000 | U+10FFFF| 11110xxx | 10xxxxxx | 10xxxxxx | 10xxxxxx|

why we design like this:
1. we can judge from first byte that it's a one/two/three/four byte character(so we can have VARIABLE bytes encoding):
   - if first byte starts with 0, then it's **one** byte encoding(ASCII)  
   - if first byte starts with 110, then it's **two** byte encoding
   - if first byte starts with 1110, then it's  **three** byte encoding
   - if first byte starts with 11110, then it's **four** byte encoding
2.  why not use 0, 10, 110, 1110? why use 10 in 2/3/4 bytes when there are two bytes?  
    - Because in this way we know by sure when we see a 10xxxxxx, we know that it belongs to byte 2/3/4, not byte 1  
    - And when we see a 0xxxxxxx, we know it's one byte encoding  
    - And when we see a 110xxxxx, we know it's two byte encoding  
    - ...
    - So we use 0, 110, 1110, 11110 for first byte, and leave 10 to 2/3/4 bytes! The set [0, 10, 110, 1110, 11110] is complete!
    - This is called [Self-synchronization](https://en.wikipedia.org/wiki/UTF-8#Comparison_with_other_encodings)
 
3. this is actually a mapping from dense to sparse range, **TODO**, visualize this process.  
   Which means some utf-8 bytes don't have corresponding unicode points, likt b'\xff'.decode('utf-8') will raise error

- The first 128(0-127) characters (US-ASCII) need one byte(7 bits actually, but we use one byte and throw away one bit)  
- The next 1920(128-2047) characters, which covers most latin world characters, need two bytes(but $2^{11}=2048$, so we    
  only need $11(total)=5(byte_1) + 6(byte_2)$

- The three bytes(2048-65535) characters, which covers almost all human languages like CJK(Chinese, Japanese, Korean), we   
  only need $16 = 4 + 6\times2$

- The four bytes(65535-111411) characters covers things like emojis, for [surrogate utf-16](https://stackoverflow.com/questions/52203351/why-unicode-is-restricted-to-0x10ffff), only $111411 = (16 + 1)\times2^{16} -1$ is used. 


### Example && Implementation




```python
def get_number_of_bits(number):
    if number < 0:
        raise ValueError
    if number < 128:
        return 1, 7
    if number < 2048:
        return 2, 5 + 6*1
    if number < 65536:
        return 3, 4 + 6*2
    if number < (16+1)*2**16:
        return 4, 3 + 6*3
    else:
        raise ValueError
    
def complete_bytes(filled_bin, order):
    if order == 1:
        assert len(filled_bin) == 7
        all_bin = [f"0{filled_bin}"]
    elif order == 2:
        assert len(filled_bin) == 11
        all_bin = [f"110{filled_bin[:5]}", f"10{filled_bin[5:11]}"]
    elif order == 3:
        assert len(filled_bin) == 16
        all_bin = [f"1110{filled_bin[:4]}", f"10{filled_bin[4:10]}", f"10{filled_bin[10:16]}"]
    elif order == 4:
        assert len(filled_bin) == 21
        all_bin = [f"11110{filled_bin[:3]}", f"10{filled_bin[3:9]}", f"10{filled_bin[9:15]}", f"10{filled_bin[15:21]}"]
    else:
        raise ValueError
    return all_bin

from termcolor import colored
s = '😳'
print(f'Start decoding: {s}')
# code_point_hex = ascii(s).split('U')[1].strip('\'')
code_point_dec = ord(s)
code_point_hex = hex(code_point_dec)
code_point_bin = bin(code_point_dec)[2:]
print(f'Code points is(hex): {code_point_hex}')
print(f'Code points is(dec): {code_point_dec}')
code_point_bin_colored = colored(code_point_bin, 'yellow')
print(f'Code points is(bin): {code_point_bin_colored}')

num_bytes, num_of_bits = get_number_of_bits(code_point_dec)
code_point_bin_fill = code_point_bin.zfill(num_of_bits)
padding = num_of_bits - len(code_point_bin)
print(f'Use {num_bytes} bytes encoding, so we need to pad binary into {num_of_bits} bits', end='')
code_point_bin_pad_colored = colored('0'*padding, 'green') + colored(code_point_bin_fill[padding:], 'yellow')
print(f'after padding, code points is: {code_point_bin_pad_colored}')

all_bin = complete_bytes(code_point_bin_fill, num_bytes)
print(f"The encoded string in binary is: {', '.join(all_bin)}")
all_hex = [hex(int(x, 2)) for x in all_bin]
print(f"The encoded string in hex is: {', '.join(all_hex)}")
print(f"Check result: s.encode('utf-8')=={s.encode('utf-8')}")

```
*And the output looks like this:*     

Start decoding: 😳  
Code points is(hex): 0x1f633    
Code points is(dec): 128563 
Code points is(bin): <span style="color:orange">11111011000110011</span>  
Use 4 bytes encoding, so we need to pad binary into 21 bitsafter padding, code points is:
    <span style="color:green">0000</span><span style="color:orange">11111011000110011</span>  
The encoded string in binary is: 11110000, 10011111, 10011000, 10110011 
The encoded string in hex is: 0xf0, 0x9f, 0x98, 0xb3    
Check result: s.encode('utf-8')==b'\xf0\x9f\x98\xb3'    
