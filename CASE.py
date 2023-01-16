import os
import itertools
import requests
from multiprocessing import Pool

# Retrieve a list of all possible encodings
encodings = requests.get("https://www.w3schools.com/charsets/ref_html_utf8.asp").text
encodings = encodings.split("\n")

#Retrieve a list of all wayback urls for a specific domain
domain = input("Enter the domain you want to search for: ")
wayback_urls = requests.get(f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=txt&fl=original&collapse=urlkey").text
wayback_urls = wayback_urls.split("\n")

# Retrieve a list of all words in the English language
words = requests.get("https://raw.githubusercontent.com/dwyl/english-words/master/words.txt").text
words = words.split("\n")

# Retrieve a list of all public quotes
quotes = requests.get("https://raw.githubusercontent.com/talaikis/quotations/master/quotes.json").json()

# Create a dictionary of all possible binary outputs
binary_tree = {}
for i in range(1, 17):
    for binary in itertools.product("01", repeat=i):
        binary_tree["".join(binary)] = {}

# Create a dictionary to store binary outputs that don't lead to a word
ignored_binaries = {}

# Create a dictionary to store the first and last usage of each word
word_positions = {}

# Create a list of all possible word combinations
combinations = []
for i in range(1, len(words)):
    for comb in itertools.combinations(words, i):
        combinations.append(" ".join(comb))

# Create a dictionary to store the number of occurrences of each word on each wayback url
word_occurrences = {}

# Create a dictionary to store the number of occurrences of each word combination on each wayback url
combination_occurrences = {}

# Check each binary output
for binary in binary_tree:
    possible_matches = []
    for encoding in encodings:
        try:
            decoded = binary.encode(encoding).decode(encoding)
            if decoded in words:
                possible_matches.append((decoded, binary, encoding))
                # remove the word from the english dictionary list
                words.remove(decoded)
                # add the word to the word_positions dictionary
                if decoded not in word_positions:
                    word_positions[decoded] = {"first_usage": (binary, encoding), "last_usage": (binary, encoding)}
                else:
                    # update the last usage if it's later than the current last usage
                    if binary > word_positions[decoded]["last_usage"][0]:
                        word_positions[decoded]["last_usage"] = (binary, encoding)
                # create a file for the word
                with open(f"{decoded}.txt", "w") as f:
                    for url in wayback_urls:
                        try:
                            response = requests.get(url)
                            if response.status_code == 200:
                                if decoded in response.text:
                                    word_occurrences[decoded] +=1
                                    f.write(url + "\n")
                        except requests.exceptions.RequestException as e:
                            pass
                            # handle error
                f.close()
        except:
            ignored_binaries[binary] = encoding
# Check each combination against the public quotes
possible_combinations = []
for comb in combinations:
    for quote in quotes:
        if comb in quote['quote']:
            possible_combinations.append(comb)
            break

#Check each word combination in each url
for comb in possible_combinations:
    with open(f"{comb}.txt", "w") as f:
        for url in wayback_urls:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    if comb in response.text:
                        combination_occurrences[comb] +=1
                        f.write(url + "\n")
            except requests.exceptions.RequestException as e:
                pass
                # handle error
    f.close()


