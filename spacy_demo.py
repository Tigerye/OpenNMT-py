import spacy
nlp = spacy.load('en_core_web_sm')

input1 = 'In July 2018 , Luzun and Luzun signed the cooperation framework agreement on the construction of the Luzhou-Zunyi section of the Rongzun high-speed railway and the Rongzun freight corridor-Gulin Dacun through Renhuai to Zunyi railway .'
input2 = 'The purchase of electric cars before April 15 is not immediately prohibited ! At present , many provinces have issued regulations on the management of over-standard vehicles , setting a transitional period of 3-7 years .'
input3 = 'Beijing Business Daily reporter Chen Tingting , Li Haojie / Wen Songyuan / Cartoon'
input4 = 'Wang Xiangnan , secretary-general of the Insurance and Economic Development Research Center of the Chinese Academy of Social Sciences , said that liability insurance is a relatively underdeveloped area of China &apos;s insurance market and has great market potential .'
input5 = "Hi, my name is Sicheng Tang"
input6 = "I work for an O2O company called Girosahggs"
input7 = "Oh I see, you don't want to buy from Apple anymore"
input8 = "It is rumored around that Facebook just released Libraaa"
input9 = "University of California sucks"
input0 = "The government of China forbid its citizens to go to WTO"

test_set = [input6, input7, input8, input9, input0]


def spacy_ner(sentence):
    doc = nlp(sentence)
    ret = []
    for ent in doc.ents:
        ret.append((ent.text, ent.start_char, ent.end_char, ent_label_))
    return ret


for sentence in test_set:
    doc = nlp(sentence)
    print(sentence)
    for ent in doc.ents:
        print(ent.text, ent.start_char, ent.end_char, ent.label_)


#print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)
