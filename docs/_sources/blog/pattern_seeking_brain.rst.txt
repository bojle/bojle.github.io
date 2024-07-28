When Reverse Engineering, Your Pattern Seeking Brain Is Your Friend
###################################################################

At work, I've been working on reverse engineering a propreitary file format that
is used to represent a synthesized `netlist
<https://en.wikipedia.org/wiki/Netlist>`_ for FPGAs by our vendor's EDA tools.

It's a binary file, and here's a sample of the hexdump:

.. code::

   00000000  12 6c 1f 03 0b 00 00 a0  00 00 00 00 40 e4 7a 1f  |.l..........@.z.|
   00000010  03 08 b6 84 a3 66 00 00  00 00 01 00 20 20 00 02  |.....f......  ..|
   00000020  40 31 00 ab 00 0e 43 45  4e 4e 41 48 45 68 65 46  |@1....CENNAHEheF|
   00000030  62 66 4b 49 03 8f 8d a3  03 8f 8d a3 02 00 08 aa  |bfKI............|
   00000040  ba b9 9e 40 b6 9b 99 00  00 00 00 00 00 00 00 01  |...@............|
   00000050  0a 49 4d 41 4f 40 4e 4e  49 48 82 08 aa ba b9 9e  |.IMAO@NNIH......|
   00000060  40 b6 9b 99 00 40 31 00  ab 00 00 b6 84 a3 66 00  |@....@1.......f.|
   00000070  00 00 00 ff 00 00 00 00  00 00 00 00 03 8f 8d a3  |................|
   00000080  00 00 00 00 00 00 00 00  00 00 40 31 00 ab 00 00  |..........@1....|
   00000090  b6 84 a3 66 00 00 00 00  ff 06 00 14 00 05 00 01  |...f............|

Without any information on the file, this stands as a wall full of random bytes.
Although complex, there's a lot that can be deduced by looking for patterns.
File formats are often divided in sections. The bytes may look random, but in
reality, they ought to be very structured. The first step in dealing with this
is to **extract the structure**.

One trick I use is to zoom out on the hexdump. This isolates zeros and all other bytes.

Here's an image of a hexdump of the same file, zoomed out:

.. image:: /_static/zoomed-out-vdb.png
   :align: center

Do you notice any patterns? 

There are alternating strips of dark and light patterns. The light patterns are
just zeros and darker ones appear to be 'data'. Here's a highlighted image with
the patterns. White rectangles represent dark parts and greens represent the
zeros.

.. image:: /_static/zoomed-out-vdb-highlighted.png
   :align: center

Since this repeats it's likely encoding the same 'type' of information. The pattern
starts with dark section followed by white and ends with a white section. They
always come in a pair. So we can deduce that to represent one of this type of
data, we need a dark part followed by the light part. 

Now, what could this be?

This is a question that falls into the 'content' part. What we did above was the 
'structure' part. As it turns out, getting meaning out of this is much more 
tedious. 

A `Fuzzer <https://en.wikipedia.org/wiki/Fuzzing>`_ is the right tool for this
job. As fuzzers tend to be very special purpose, i wrote one for myself.
Extracting the details with the fuzzer vindicates our suspicion. The dark and
light parts are indeed part of the structure. The dark part is sort of a
preamble to the light part. The light part is a port reference list for all
the black-box module present in the netlist. 

That this pattern represents black-box modules can be deduced by counting the
number of times this pattern is present, and what other thing is present as
many times in the original source file from which this was generated. Inspecting
the source, which is just a verilog file confirms that this are indeed the
black-box modules.

Conclusion
##########

In conclusion, file formats or any other type of data that are supposed to be 
regular can be brute-forced by our pattern-seeking brains to reveal their 
structures.

PS: I'll write a full description of the fuzzer and document other details as
this project progresses.
