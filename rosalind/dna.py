from textImport import getTextFile

dna = getTextFile()
print(dna.count('A'), dna.count('C'), dna.count('G'), dna.count('T'))
