from trademark_extractor import extract_trademark_phrases

EXAMPLES = [
    ("funny t-shirt for cat lovers", ["funny", "cat", "cat lovers"]),
    ("APPLE logo decal for MacBook", ["APPLE", "APPLE logo", "MacBook", "logo decal"]),
    ("Taylor Swift era tour tee", ["Taylor Swift", "era tour", "Swift"]),
    ("gift for men and women", ["men", "women"]),
    ("LED RGB USB Gaming Keyboard", ["LED", "RGB", "USB", "Gaming Keyboard"]),
    ("Disney princess nightgown", ["Disney", "princess", "Disney princess"]),
    ("Custom Coca-Cola Christmas ornament", ["Coca-Cola", "Christmas ornament"]),
    ("Funny iPhone case with meme quote", ["iPhone", "iPhone case", "meme quote"]),
    ("NASA space program sweatshirt", ["NASA", "space program"]),
    ("Nestlé’s chocolate lovers bundle", ["Nestlé", "chocolate lovers"]),
    ("DJI drone controller skin", ["DJI", "drone controller"]),
    ("Graduation 2025 keepsake gift", ["Graduation 2025", "keepsake"]),
    ("AI-generated art shirt", ["AI-generated", "AI", "art shirt"]),
    ("Swift action running shoes", ["Swift action", "running shoes"]),
    ("Star Wars Jedi hoodie", ["Star Wars", "Jedi hoodie", "Jedi"]),
    ("Inspired by Louis Vuitton", ["Louis Vuitton"]),
    ("Barbiecore outfit aesthetic", ["Barbiecore", "Barbiecore outfit"]),
    ("Marvel Avengers Endgame mug", ["Marvel", "Avengers", "Endgame mug", "Avengers Endgame"]),
    ("The Beatles tribute tee", ["The Beatles", "Beatles", "tribute tee"]),
    ("Coca Cola vs Pepsi meme tee", ["Coca Cola", "Pepsi", "Coca Cola vs Pepsi"]),
    ("iPhone 15 Pro Max wallet case", ["iPhone 15 Pro Max", "wallet case"]),
    ("Call of Duty gaming mat", ["Call of Duty", "gaming mat"]),
    ("Harry Potter inspired mug", ["Harry Potter"]),
    ("Elon Musk fan club tee", ["Elon Musk", "fan club"]),
    ("GOAT sports legend tee", ["GOAT", "sports legend"]),
    ("F1 racing decal", ["F1", "racing decal"]),
    ("Anime inspired keychain", ["Anime", "Anime inspired"]),
    ("NFL Super Bowl 2025 poster", ["NFL", "Super Bowl", "Super Bowl 2025"]),
    ("Taylor’s version lyric shirt", ["Taylor’s version", "lyric shirt", "Taylor"]),
    ("Dog mom Starbucks parody mug", ["Starbucks", "parody mug", "dog mom"]),
]

if __name__ == '__main__':
    all_passed = True
    for text, expected in EXAMPLES:
        result = extract_trademark_phrases(text)
        if result != expected:
            print('FAIL', text, result)
            all_passed = False
    if all_passed:
        print('ALL PASSED')
