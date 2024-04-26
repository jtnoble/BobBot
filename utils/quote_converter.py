import os, json

def textfile_to_json(filename) -> None:
    with open(f'{filename}.txt', 'r', encoding='utf-8') as textfile:
        lines = textfile.read().splitlines()
    
    data = []
    count = 0
    for line in lines:
        count += 1
        quote, author = line.rsplit(" -", 1)
        data.append({"num": count, "author": author, "quote": quote})
    
    with open(f'{filename}.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)

    print("Complete!")

def json_to_textfile(filename) -> None:
    with open(f'{filename}.json', 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    
    with open(f'{filename}.txt', 'w', encoding='utf-8') as textfile:
        for entry in data:
            quote, author = entry['quote'], entry['author']
            textfile.write(f'{quote} -{author}\n')

    print("Complete!")

def check_filename(filename) -> bool:
    return os.path.exists(filename + ".txt") or os.path.exists(filename + ".json")

if __name__ == '__main__':
    msg = '''
********************************************
Use this utility to generate a textfile from json or vice versa.
Meant to be an easy way to go from a readable file for your quotes
to a JSON file for the program.

Remember, you must be in the utils directory for this to work,
otherwise, you will get file not found errors.
********************************************
\n
'''
    print(msg)
    _input = input("1) Textfile to JSON\n2) JSON to textfile\n")
    _filename = input("Filename (no file extension): ")

    if not check_filename(_filename):
        print("File not found!")
        quit()

    match _input:
        case "1":
            textfile_to_json(_filename)
        case "2":
            json_to_textfile(_filename)
        case _:
            print("Incorrect option, closing...")
