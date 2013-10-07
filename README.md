BWT
===

Purpose:

bwt.py implements linear time encoding of a text into its Burrows Wheeler Transform, and inversion of the transform back to the original text. The dc3 algorithm is implemented for linear time construction of a suffix array, which is used in the encoding to BWT. Decoding is achieved via an occurrence function on the BWT and backwards decoding. 

BWT is a popular data structure for compressing the information contained within a suffix array. It can also be used for finding all positions in the encoded text matching a pattern, in time linear in the size of the pattern.

Use: 

The program is run from the command line, and takes three arguments: -bwt/-ibwt for encoding/decoding, input_filename, and output_filename. For example: 

python bwt.py -bwt moby_dick.fasta moby_dick.bwt.fasta
python bwt.py -ibwt moby_dick.bwt.fasta moby_dick.ibwt.fasta

The first command would read the text from moby_dick.fasta and output its bwt in fasta format to moby_dick.bwt.fasta
The second command would read the bwt in fasta format and output the decoded text to moby_dick.ibwt.fasta
Note that moby_dick.fasta and moby_dick.ibwt.fasta will have identical contents

bwt.py expects the input fasta file to be in the same directory as itself. It outputs to the specified file name within the same directory.

Format: 

The program takes input and outputs files in fasta format. This includes a header line '>BWT' or '>iBWT', and subsequent lines limited to 80 characters of text each. The program will tolerate in the input file 1) comment lines designated with '>' or ';', and 2) newlines, but output is standard. Header is not critical to program function.
