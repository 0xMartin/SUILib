import glob
import os
import re

def camel_to_snake(name):
    # Převod camelCase nebo PascalCase na snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def find_camel_names(code):
    # Najde všechny kandidáty na camelCase identifikátory
    pattern = r'\b([a-z]+[A-Z][A-Za-z0-9]*)\b'
    return set(re.findall(pattern, code))

def replace_in_code(code, name_map):
    # Nahradí všechny výskyty klíčů ve slovníku name_map jejich hodnotami
    def replacer(match):
        word = match.group(0)
        return name_map.get(word, word)
    if not name_map:
        return code
    pattern = r'\b(' + '|'.join(re.escape(key) for key in name_map) + r')\b'
    return re.sub(pattern, replacer, code)

# Najdi všechny Python soubory ve složce SUILib rekurzivně
python_files = glob.glob("SUILib/**/*.py", recursive=True)

for filepath in python_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # Najdi všechny camelCase názvy funkcí a proměnných (včetně parametrů)
    camel_names = find_camel_names(code)
    name_map = {}
    for name in camel_names:
        snake = camel_to_snake(name)
        if snake != name:
            name_map[name] = snake

    # Pokud je co měnit, přepiš soubor
    if name_map:
        new_code = replace_in_code(code, name_map)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"Přejmenováno v {filepath}: {name_map}")

print("Hotovo. Všechny camelCase názvy byly převedeny na snake_case.")