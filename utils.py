import numpy as np
import random
import json
import re
import csv
import hashlib

ROOT_URL = 'http://craptocurrency.net'
WALLETS_CSV_FILENAME = '/home/ubuntu/crapto-web/data/wallets.csv'
PASSWORDS_CSV_FILENAME = '/home/ubuntu/crapto-web/data/passwords.csv'

def read_wallets_file():
    wallets = {}
    with open(WALLETS_CSV_FILENAME, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            wallets[row[0]] = float(row[1])
    return wallets

def write_wallets_file(wallets):
    with open(WALLETS_CSV_FILENAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(wallets.items())

def read_passwords_file():
    passwords = {}
    with open(PASSWORDS_CSV_FILENAME, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            passwords[row[0]] = row[1]
    return passwords

def write_passwords_file(passwords):
    with open(PASSWORDS_CSV_FILENAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(passwords.items())

def change_pass_prep(wallet_address, phash):
    if not authenticate(wallet_address, phash):
      return "Error: Bad passphrase for wallet address %s" % wallet_address

    # Formatting in html
    html = ''
    html = addContent(html, '<form action="/change_pass" method="post">')
    html = addContent(html, '<input type="hidden" name="wallet_address" value="%s">' % wallet_address)
    html = addContent(html, '<input type="hidden" name="phash" value="%s">' % phash)
    html = addContent(html, """
<label>Current passphrase: </label><input type="password" name="old_passphrase"><br>
<label>New passphrase: </label><input type="text" name="new_passphrase"><br>
<input type="submit">
</form>""")
    return f'<div>{html}</div>'

def change_pass(wallet_address, old_phash, new_passphrase):
  passwords = read_passwords_file()
  if authenticate(wallet_address, old_phash):
    passwords[wallet_address] = hash_passphrase(new_passphrase)
    write_passwords_file(passwords)
    return "Successfully changed passphrase."
  return "Error: Bad passphrase for wallet address %s" % wallet_address

def pseudorandom_wallet_address():
  chars = [chr(id) for id in list(range(48,58)) + list(range(65, 91)) + list(range(97, 123))]
  for c in 'l1I0O':
    chars.remove(c)
  return ''.join(random.choices(chars, k=6))

def hash_passphrase(passphrase):
  hash_object = hashlib.sha1(passphrase.encode('utf-8'))
  return hash_object.hexdigest()

def lookup_balance(wallet_address):
  wallets = read_wallets_file()
  return float(wallets[wallet_address]) if wallet_address in wallets else 0.0

def write_error(error_string):
  return error_string

def render_send_prep(from_address, phash):
    if not authenticate(from_address, phash):
      return "Error: Bad passphrase for wallet address %s" % from_address

    balance = lookup_balance(from_address)

    # Formatting in html
    html = ''
    html = addContent(html, header(
        'Wallet ', color='black', gen_text='Balance'))
    html = addContent(html, box(from_address + ": ", amount2str(balance)))
    html = addContent(html, '<table>')
    html = addContent(html, '<form action="/send" method="post">')
    html = addContent(html, '<input type="hidden" name="from" value="%s">' % from_address)
    html = addContent(html, '<input type="hidden" name="phash" value="%s">' % phash)
    html = addContent(html, '<input type="hidden" id="random_address" name="random_address" value="%s">' % pseudorandom_wallet_address())
    html = addContent(html, """
<tr><label>Amount (in billions): </label><input type="number" step="any" name="amount"><br></tr>
<tr><label>To wallet address: </label><input type="text" name="to" id="to"><br></tr>
<tr><label for="new_checkbox">Create New Wallet for Recipient</label> <input type="checkbox" id="new_checkbox" name="new_checkbox" onclick="document.getElementById('new_unique_div').style.display='block'"><br></tr>
<tr>
<div id="new_unique_div" style="display:none">
  <label for="new_unique_checkbox" id="new_unique_label">Generate New Unique Wallet Address</label> <input type="checkbox" id="new_unique_checkbox" onclick="document.getElementById('to').value=document.getElementById('random_address').value">
</div>
</tr>
<tr><label for="name">Your name (so recipient knows who it is from; optional): </label><input type="text" name="sender_name" value=""></tr>
<tr><div><input type="submit"></div></tr>
</form>
</table>""")
    return f'<div>{html}</div>'

def send(from_address, to_address, phash, amount, new_checkbox):
    if not authenticate(from_address, phash):
      return "Error: Bad passphrase for wallet address %s" % from_address

    # Note: since the file is read within this method, which is called for every request,
    #       updates to the CSV file will not require a server restart.
    wallets = read_wallets_file()

    if new_checkbox and to_address in wallets:
      return "Error: You requested to create a new wallet for recipient but wallet address %s already exists" % to_address

    from_address = from_address.lower()
    to_address = to_address.lower()
    amount = float(amount)
    if to_address not in wallets:
      wallets[to_address] = 0

    if wallets[from_address] < amount:
      return "Could not send; you tried to send %s, but your wallet only has %s." % (amount2str(amount), amount2str(wallets[from_address]))

    amount = amount

    wallets[from_address] -= amount
    wallets[to_address] += amount
    from_balance = wallets[from_address]

    write_wallets_file(wallets)

    # Formatting in html
    html = ''
    html = addContent(html, header(
        'Wallet ', color='black', gen_text='Balance'))
    html = addContent(html, box(from_address + ": ", amount2str(from_balance)))
    return f'<div>{html}</div>'

def add_wallet(wallet_address, phash, amount):
    if not authenticate(wallet_address, phash):
      return "Error: Bad passphrase for wallet address %s" % wallet_address

    # Note: since the file is read within this method, which is called for every request,
    #       updates to the CSV file will not require a server restart.
    wallets = read_wallets_file()

    wallet_address = wallet_address.lower()
    amount = float(amount)
    if wallet_address not in wallets:
      wallets[wallet_address] = 0
    wallets[wallet_address] += amount
    total_amount = wallets[wallet_address]

    write_wallets_file(wallets)

    # Formatting in html
    html = ''
    html = addContent(html, header(
        'Wallet ', color='black', gen_text='Balance'))
    html = addContent(html, box(wallet_address + ": ", amount2str(total_amount)))
    return f'<div>{html}</div>'

def authenticate(wallet_address, phash):
  passwords = read_passwords_file()
  true_pass_hash = passwords[wallet_address] if wallet_address in passwords else hash_passphrase(wallet_address)
  return phash == true_pass_hash

def read_wallet(wallet_address, phash):
    if not authenticate(wallet_address, phash):
      return "Error: Bad passphrase for wallet address %s" % wallet_address

    # Note: since the file is read within this method, which is called for every request,
    #       updates to the CSV file will not require a server restart.
    wallets = read_wallets_file()

    wallet_address = wallet_address.lower()
    amount = wallets[wallet_address] if wallet_address in wallets else 0.0

    # Formatting in html
    html = ''
    html = addContent(html, header(
        'Wallet ', color='black', gen_text='Balance'))
    html = addContent(html, box(wallet_address + ": ", amount2str(amount)))

    action_html = ''
    action_html = addContent(action_html, '<form action="/send_prep" method="post">')
    action_html = addContent(action_html, '<input type="hidden" name="from" value="%s">' % wallet_address)
    action_html = addContent(action_html, '<input type="hidden" name="phash" value="%s">' % phash)
    action_html = addContent(action_html, '<input type="submit" value="Send" />')
    action_html = addContent(action_html, '</form>')
    action_html = addContent(action_html, '<form action="/mine" method="post">')
    action_html = addContent(action_html, '<input type="hidden" name="wallet_address" value="%s">' % wallet_address)
    action_html = addContent(action_html, '<input type="hidden" name="phash" value="%s">' % phash)
    action_html = addContent(action_html, '<input type="submit" value="Mine" />')
    action_html = addContent(action_html, '</form>')
    action_html = addContent(action_html, '<form action="/change_pass_prep" method="post">')
    action_html = addContent(action_html, '<input type="hidden" name="wallet_address" value="%s">' % wallet_address)
    action_html = addContent(action_html, '<input type="hidden" name="phash" value="%s">' % phash)
    action_html = addContent(action_html, '<input type="submit" value="Change Passphrase" />')
    action_html = addContent(action_html, '</form>')
    return f'<div>{html}</div><div>{action_html}</div>'

def amount2str(amount):
    amount = float(amount)
    amount = round(amount,3)
    return "{:,}".format(amount) + " billion pieces of Crapto"

def header(text, color='black', gen_text=None):
    """Create an HTML header"""

    if gen_text:
        raw_html = f'<h1 style="margin-top:16px;color: {color};font-size:54px"><center>' + str(
            text) + '<span style="color: red">' + str(gen_text) + '</center></h1>'
    else:
        raw_html = f'<h1 style="margin-top:12px;color: {color};font-size:54px"><center>' + str(
            text) + '</center></h1>'
    return raw_html


def box(text, gen_text=None):
    """Create an HTML box of text"""

    if gen_text:
        raw_html = '<div style="padding:8px;font-size:28px;margin-top:28px;margin-bottom:14px;">' + str(
            text) + '<span style="color: red">' + str(gen_text) + '</div>'

    else:
        raw_html = '<div style="border-bottom:1px inset black;border-top:1px inset black;padding:8px;font-size: 28px;">' + str(
            text) + '</div>'
    return raw_html


def addContent(old_html, raw_html):
    """Add html content together"""

    old_html += raw_html
    return old_html


def format_sequence(s):
    """Add spaces around punctuation and remove references to images/citations."""

    # Add spaces around punctuation
    s = re.sub(r'(?<=[^\s0-9])(?=[.,;?])', r' ', s)

    # Remove references to figures
    s = re.sub(r'\((\d+)\)', r'', s)

    # Remove double spaces
    s = re.sub(r'\s\s', ' ', s)
    return s


def remove_spaces(s):
    """Remove spaces around punctuation"""

    s = re.sub(r'\s+([.,;?])', r'\1', s)

    return s

def render_help():
  return """
For fastest help, contact one of the creators (if you have their info):<br>
<table>
<tr>Nick Armstrong-Crews</tr><br>
<tr>Bill Yang</tr><br>
<tr>Kai Ruan</tr><br>
<tr>Vince Steffens</tr><br>
<tr>Dayle Armstrong</tr><br>
</table>
<br>
Otherwise, email: <a href="mailto:crapto.currency.help@gmail.com">crapto.currency.help@gmail.com</a>
"""

def render_email_template(wallet_address, amount, sender_name=''):
  inner_html = render_email_template_internal(wallet_address, amount, sender_name)
  return """
<iframe id="email_iframe" name="email_iframe" src="about:blank" style="border:none;" scrolling="no"></iframe>
<hr/>
<input type="button" onclick="window.frames['email_iframe'].focus();window.frames['email_iframe'].print()" value="Print"/>
<script type="text/javascript">
  var doc = document.getElementById('email_iframe').contentWindow.document;
  doc.open();
  doc.write(`<html><head><title></title></head><body>%s</body></html>`);
  doc.close();
  var iframe = document.getElementById("email_iframe");
  iframe.onload = function() {
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
  }
</script>
""" % inner_html

def render_email_template_internal(wallet_address, amount, sender_name=''):
    if not sender_name:
      sender_name = '&lt;Someone&gt;'
    passphrase = wallet_address
    wallet_url = '%s/?wallet_address=%s' % (ROOT_URL, wallet_address)
    html = ''
    html = addContent(html, '<h5>%s has sent you a gift of %s Currency. This has been deposited into a new wallet as follows...</h5>' % (sender_name, amount2str(amount)))
    html = addContent(html, '<h5>Wallet address: %s</h5>' % wallet_address)
    html = addContent(html, '<h5>Initial passphrase: %s</h5>' % passphrase)
    html = addContent(html, '<h5>You can access your Crapto wallet via web browser: <a href="%s">craptocurrency.net</a></h5>' % wallet_url)
    html = addContent(html, """
  <center>
	<img src="static/images/crapto128.png" alt="Crapto icon"/>
  </center>

<h4>What is Crapto Currency?</h4>
<h5>Crapto Currency, or simply "Crapto," is a digital cryptocurrency similar to Bitcoin.</h5>

<h4>What can I do with my Crapto?</h4>
<h5>Most people send some to a friend or two to make them smile. You may choose to hodl it while its value trends like Bitcoin (starting at US$0.0008 and today selling for around US$60k). You may exchange it for goods, services, or other currency, with any individual or entity accepting Crapto as a form of payment.</h5>

<h4>Is this real?</h4>
<h5>Is anything "real?" Is Bitcoin "real?" Does cash printed on pieces of paper have any inherent value? Anything in demand has value. Crapto is as "real" as Bitcoin, or any other cryptocurrency... and we believe demand will grow. At the very least, we can all agree Crapto is a memorable name.</h5>

<h4>Is this a joke?</h4>
<h5>Yes. But it is also a cryptocurrency. Another joke cryptocurrency is <a href="https://en.wikipedia.org/wiki/Dogecoin">Dogecoin</a>, which reached market cap of US$85 billion.</h5>

<h4>Where can I learn more?</h4>
<h5><a href="http://craptocurrency.com/about">http://craptocurrency.com/about</a></h5>
""")
    return html
