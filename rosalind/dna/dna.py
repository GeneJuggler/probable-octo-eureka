def qt(s):
    return s.count("A"), s.count("C"), s.count("G"), s.count("T")

demo = "TTGACTGGAATCCTGTTGCGGTAAACTATCACTGCTGAATACGTGCAAGCCCTACCAAGTACACCTGACCAATGCGACCTTCCGGGCTTTCACACGTGTTGATCTGAGTTAGGCATCAAAGCGCCCTTGTATGCGTGGGCCCATTCGTACAGACTACATCCCGTAACATACCGCATGGGTCCACTCATCCGGCAGCTCCCGGACAAAAGATCACGGGCATATGCCAAACTGATCGCTAGAGTCTCCCCTAGATACTCTTAGTACAGCCGGTTGTGAAGCCACGTGTCCAGGGCACTGGCACCCTTATAGCAAGAAACCACCAATGTTCTTTGTAATTCGAATCCGAGCCATGGCGAGGCTTTCTACTAGTTCCTCAGGACCTATAGTCCGGGGATGCAAGTGATTCAGATGGCAGTTTCTGTGCGGCCTGAGCACGCTTATACCATAATCCAATTGAACAAGAACTTTCACCAGCAACCGACGTAATAGGGCAAATGTCCTTGCATTTTAGGTATTACACCAGTTGGAAGCGACGAACGGGGAAATTTTCTAACTAGGCATGTAGGTTAGGGTAGTCGGTTAATACACACTTGCGAGCCGTCCCCCAATCATAGGAGAGCCAGATATGCCACATGTGCCGCAATAGCTTGCTATCTACTGTGCACCTATAGTCTGAACACGGCTTCGCGTCGTGTTTTTCGTGTTTCCATTCCCCTAAGGGTTAGCGGTTTTCGATTTCGCGTCATCTGTTTCAAGCCGTAGGGGAACTTGAGCCTTCTTAACATGTCTGGACTTTTAAACGTTAACGTGTGGATGTCACTTCGGCAATATCAATACGATACGACTTTAAGCAATATCAGGAGTCGTCAACAGCTGATTTAGGTGCTTC"

print(qt(demo))
