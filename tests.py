from trademark_extractor import extract_trademark_phrases

EXAMPLES = [
    ("funny t-shirt for cat lovers", ["funny", "cat", "cat lovers"]),
    ("APPLE logo decal for MacBook", ["APPLE", "APPLE logo", "MacBook", "logo decal"]),
    ("Taylor Swift era tour tee", ["Taylor Swift", "era tour", "Swift"]),
    ("gift for men and women", ["men", "women"]),
    ("LED RGB USB Gaming Keyboard", ["LED", "RGB", "USB", "Gaming Keyboard"]),
]

if __name__ == '__main__':
    all_passed = True
    for text, expected in EXAMPLES:
        result = extract_trademark_phrases(text)
        if set(result) != set(expected):
            print('FAIL', text, result)
            all_passed = False
    if all_passed:
        print('ALL PASSED')
