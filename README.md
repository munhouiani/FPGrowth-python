# FPGrowth-python
This implementation is based on [FP-Growth-Java](https://github.com/goodinges/FP-Growth-Java).
# Input File Format
The python script accepts input file with format:
```
f,c,a,m,p
f,c,b
```
or
```
f c a m p
f c a
```
Use along with IBM Quest Synthetic Data Generator and [IBM Data Converter](https://github.com/mhwong2007/IBM-Quest-Data-Converter) to produce csv file.

# How to Use
First make `main.py` executable.
``` sh
chmod +x main.py
```
Run FP-Growth algorithm with
``` sh
./main input_file minsup minconf
```

# Output
This program first prints frequent patterns:
```
{ frequent itemset } (support of the frequent item set)
```
Eg.
```
{ a } ( 3 )
{ a c } ( 3 )
{ a c f } ( 3 )
{ a f } ( 3 )
...
```
After that it prints the rules:
```
{ frequent itemset } => { frequent itemset } ( confidence )
```
Eg.
```
{ a } => { c } ( 1.0 )
{ c } => { a } ( 0.75 )
{ a } => { c f } ( 1.0 )
...
```
