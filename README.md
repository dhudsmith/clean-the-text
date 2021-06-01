# Clean the Text!

# Installation
In a terminal, run
```shell
pip install --upgrade git+https://github.com/dhudsmith/clean-the-text
```

# Usage
In python, 
```python
from ctt import clean

dirty_text = """
To: foo@bar.net
From: baz@bar.net
Subject: You owe me $$$
Body:
<div>
Dear foo,
<br>
Need I remind you that you owe me 700 gil? I accept payment via paypal.com or bitcoin of course. 
<br>
Sincerely yours,
baz
</div>
"""

clean_text = clean.kitchen_sink(dirty_text)

print(clean_text)
# >> "subject owe body dear foo need remind owe gil accept payment via bitcoin course sincerely baz"
```