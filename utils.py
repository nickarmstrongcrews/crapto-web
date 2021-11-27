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

def read_passwords_file():
    passwords = {}
    with open(PASSWORDS_CSV_FILENAME, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            passwords[row[0]] = row[1]
    return passwords

def hash_passphrase(passphrase):
  return hashlib.sha1(passphrase).hex_digest()

def check_password(wallet_address, passphrase):
  passwords = read_passwords_file()
  given_pass_hash = hash_passphrase(passphrase)
  true_pass_hash = passwords[wallet_address] if wallet_address in passwords else hash_passphrase(wallet_address)
  return given_pass_hash == true_pass_hash

def lookup_balance(wallet_address):
  wallets = read_wallets_file()
  return float(wallets[wallet_address]) if wallet_address in wallets else 0.0

def write_error(error_string):
  return error_string

def render_send_prep(from_address, passphrase):
    if not authenticate(from_address, passphrase):
      return "Bad passphrase for wallet address %s" % from_address

    balance = lookup_balance(from_address)

    # Formatting in html
    html = ''
    html = addContent(html, header(
        'Wallet ', color='black', gen_text='Balance'))
    html = addContent(html, box(from_address + ": ", amount2str(balance)))
    html = addContent(html, '<form action="/send" method="get">')
    html = addContent(html, '<input type="hidden" name="from" value="%s">' % from_address)
    html = addContent(html, """
<label>To wallet address: </label><input type="text" name="to"><br>
<label>Amount (in billions): </label><input type="number" name="amount"><br>
<input type="submit">
</form>""")
    return f'<div>{html}</div>'

def send(from_address, to_address, passphrase, amount):
    if not authenticate(from_address, passphrase):
      return "Bad passphrase for wallet address %s" % from_address

    # Note: since the file is read within this method, which is called for every request,
    #       updates to the CSV file will not require a server restart.
    wallets = read_wallets_file()

    from_address = from_address.lower()
    to_address = to_address.lower()
    amount = float(amount)
    if to_address not in wallets:
      wallets[to_address] = 0

    if wallets[from_address] < amount:
      return "Could not send; you tried to send %s, but your wallet only has %s." % (amount2str(amount), amount2str(wallets[from_address]))

    # TODO: for some reason, without this, we reliably change by double the amount requested. ???
    amount = amount / 2.0

    wallets[from_address] -= amount
    wallets[to_address] += amount
    from_balance = wallets[from_address]

    with open(WALLETS_CSV_FILENAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(wallets.items())

    # Formatting in html
    html = ''
    html = addContent(html, header(
        'Wallet ', color='black', gen_text='Balance'))
    html = addContent(html, box(from_address + ": ", amount2str(from_balance)))
    return f'<div>{html}</div>'

def add_wallet(wallet_address, passphrase, amount):
    if not authenticate(wallet_address, passphrase):
      return "Bad passphrase for wallet address %s" % wallet_address

    # Note: since the file is read within this method, which is called for every request,
    #       updates to the CSV file will not require a server restart.
    wallets = read_wallets_file()

    wallet_address = wallet_address.lower()
    amount = float(amount)
    if wallet_address not in wallets:
      wallets[wallet_address] = 0
    wallets[wallet_address] += amount
    total_amount = wallets[wallet_address]

    with open(WALLETS_CSV_FILENAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(wallets.items())

    # Formatting in html
    html = ''
    html = addContent(html, header(
        'Wallet ', color='black', gen_text='Balance'))
    html = addContent(html, box(wallet_address + ": ", amount2str(total_amount)))
    return f'<div>{html}</div>'

def authenticate(wallet_address, passphrase):
    return wallet_address.lower() == passphrase.lower()

def read_wallet(wallet_address, passphrase):
    if not authenticate(wallet_address, passphrase):
      return "Bad passphrase for wallet address %s" % wallet_address

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
    action_html = addContent(action_html, '<form action="/send_prep" method="get">')
    action_html = addContent(action_html, '<input type="hidden" name="from" value="%s">' % wallet_address)
    action_html = addContent(action_html, '<input type="submit" value="Send" />')
    action_html = addContent(action_html, '</form>')
    action_html = addContent(action_html, '<form action="/mine" method="get">')
    action_html = addContent(action_html, '<input type="hidden" name="wallet_address" value="%s">' % wallet_address)
    action_html = addContent(action_html, '<input type="submit" value="Mine" />')
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

def render_email_template(wallet_address, amount, sender_name='&lt;Someone&gt;'):
    passphrase = wallet_address
    wallet_url = '%s/?wallet_address=%s' % (ROOT_URL, wallet_address)
    html = ''
    html = addContent(html, '<h5>%s has sent you a gift of %s. This has been deposited into a new Crapto wallet as follows...</h5>' % (sender_name, amount2str(amount)))
    html = addContent(html, '<h5>Wallet address: %s</h5>' % wallet_address)
    html = addContent(html, '<h5>Passphrase: %s</h5>' % passphrase)
    html = addContent(html, '<h5>You can access your Crapto wallet at: <a href="%s">%s</a></h5>' % (wallet_url, wallet_url))
    html = addContent(html, """
  <center>
	<img src="static/images/crapto256.png" alt="Crapto icon"/>
  </center>

<h3>FAQ</h3>

<h4>What is Crapto?</h4>
<h5>Crapto, short for "Craptocurrency," is a digital currency (or "cryptocurrency") similar to Bitcoin.</h5>

<h4>What can I do with my Crapto?</h4>
<h5>Most likely you will want to save it until its value follows the trend of cryptocurrencies like Bitcoin (which started at $0.0008 and today sells for around $60k). You can also send and receive Crapto, for example in exchange for goods and services, to any individual or entity which accepts Crapto as a form of payment.</h5>

<h4>Can I mine for more Crapto?</h4>
<h5>Yes. However, it is somewhat rudimentary through the web interface; instead, you probably want to build from source and install the client (for Linux and Windows) at: <a href=https://github.com/nickarmstrongcrews/crapto>https://github.com/nickarmstrongcrews/crapto</a> (note: this is not recommended for the uninitiated).</h5>

<h4>Where can I learn more about cryprocurrency?</h4>
<h5><a href="https://en.wikipedia.org/wiki/Cryptocurrency">Wikipedia article</a></h5>

<h4>Is this real?</h4>
<h5>Is anything "real?" Is Bitcoin "real?" Does cash printed on pieces of paper have any inherent value? Anything in demand has value. Crapto is as "real" as Bitcoin, or any other cryptocurrency... and we believe demand will grow. At the very least, we can all agree Crapto is a memorable name.</h5>

<h4>Is this a joke?</h4>
<h5>Yes. But it is also a cryptocurrency. Another joke cryptocurrency is <a href="https://en.wikipedia.org/wiki/Dogecoin">Dogecoin</a>.</h5>
""")
    return html
