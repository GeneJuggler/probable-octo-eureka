from textImport import getTextFile

dna_string = getTextFile().strip()

#def compliment(nucleotide):
#    if nucleotide == 'A':
#        return('T')
#    if nucleotide == 'T':
#        return('A')
#    if nucleotide == 'G':
#        return('C')
#    if nucleotide == 'C':
#        return('G')
#    else:
#        return('BOGUS')
#
#
#answer = ''
#for x in dna_string[::-1]:
#    answer += compliment(x)
#
#print(answer)

print(dna_string[::-1].translate(str.maketrans('ACGT', 'TGCA')))
