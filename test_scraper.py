import requests
import re
text = requests.get('https://drive.google.com/drive/folders/1awCPTpgpRAYdh7pDs6P5CvLeIG-HCyrl').text
matches = set(re.findall(r'"([a-zA-Z0-9_-]{33})"', text))
print("Found", len(matches), "files.")
for m in list(matches)[:5]:
    print("ID:", m)
