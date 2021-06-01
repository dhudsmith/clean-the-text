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

# dirty_text = "www.paypal.com"

clean_text = clean.kitchen_sink(dirty_text)

print(clean_text)
