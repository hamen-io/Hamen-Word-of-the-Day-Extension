import re
import nltk
from nltk.corpus import wordnet
from PyDictionary import PyDictionary
import pyttsx3
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from wiktionaryparser import WiktionaryParser

def getResources():
    nltk.download('omw-1.4')

def testInt(value: str) -> bool:
    try:
        return int(value)
    except:
        return False

class Word:
    def __init__(self, word: str) -> None:
        assert word and type(word) is str
        self.word = word
        
        parser = WiktionaryParser()
        self._wiktionary = parser.fetch(self.word)
        assert len(self._wiktionary) >= 1 and any([len(x.keys()) >= 3 for x in self._wiktionary])
        self._wiktionary = [x for x in self._wiktionary if len(x.keys()) >= 3][0]

        self.etymology: str = ""
        self.definition: str = ""
        self.example: str = ""
        self.synonyms: list[str] = []
        self.antonyms: list[str] = []
        self.hypernyms: list[str] = []
        self.hyponyms: list[str] = []
        self.translations = { "fr": [], "de": [], "it": [], "es": [] }

        self.getData()

    def getData(self) -> str:
        print("Definition; which definition best fits the word?")
        definitionList = dict()

        i = 0 # Total definition index (increased per definition)
        g = 0 # Group index
        j = 0 # Definition index (reset per group; increased per definition)
        for definitions in self._wiktionary["definitions"]:
            for definition in definitions["text"]:
                print(f"{i+1}. {definition.strip()}")
                i += 1
                j += 1

                definitionList[str(i)] = {"group": g, "index": j, "definition": definition.strip()}

            g += 1
            j = 0

        correctDefinition = input("> ")
        while not testInt(correctDefinition) or int(correctDefinition) <= 0 or int(correctDefinition) > i+1:
            correctDefinition = input("!> ")

        correctDefinition = definitionList[correctDefinition]
        print(f"\n! Definition chosen: \"{correctDefinition['definition']}\"\n")
        self.definition = correctDefinition["definition"]

        target = self._wiktionary["definitions"][correctDefinition["group"]]
        self.partOfSpeech = target["partOfSpeech"]
        relatedWords = target["relatedWords"]
        print(f"Part of Speech; pos found automatically!\n")

        print(f"Related Words; related words found automatically!\n")
        for rel in relatedWords:
            relType = rel["relationshipType"]
            words = "\n".join(rel["words"])
            words = re.findall(r"((?<![\w:])[a-z]+[a-z ]*[a-z]+(?![a-z:]))", words)
            match relType.lower():
                case "synonyms":
                    self.synonyms = words
                case "antonyms":
                    self.antonyms = words
                case "hyponyms":
                    self.hyponyms = words
                case _:
                    raise KeyError(f"Invalid related-word-relationship-type: \"{relType}\"")

        examples = target["examples"]

        print("Examples; which example best fits the word?")
        i = 0
        for example in examples:
            print(f"{i+1}. {example}")
            i += 1
        correctExample = input("> ")
        while not testInt(correctExample) or int(correctExample) <= 0 or int(correctExample) > i+1:
            correctExample = input("!> ")
        self.example = examples[int(correctExample) - 1]
        print(f"\n! Example chosen: \"{self.example}\"\n")

        self.etymology = self._wiktionary["etymology"].strip()
        print(f"Etymology; etymology found automatically!\n")

        for lang in self.translations:
            url = f"https://www.wordreference.com/{lang}/{self.word}"
            if lang in "es":
                url = f"https://www.wordreference.com/{lang}/translation.asp?tranword={self.word}"
            
            response = requests.get(url)
            data = BeautifulSoup(response.text, "lxml")
            translations = data.find(class_="even")
            if not translations:
                print("ERROR: ", lang)
                continue

            translations = translations.find_all(class_="ToWrd")
            print([x.tag for x in translations])

    # def getDefinition(self) -> str:
    #     return self._wiktionary["etymology"].strip()

w = Word("test")
print("etymology", w.etymology)
print("definition", w.definition)
print("example", w.example)
print("synonyms", w.synonyms)
print("antonyms", w.antonyms)
print("hypernyms", w.hypernyms)
print("hyponyms", w.hyponyms)
print("translations", w.translations)