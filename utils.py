import numpy as np
import random
import json
import re
import csv

WALLETS_CSV_FILENAME = "/home/ubuntu/crapto-web/data/wallets.csv"

def read_wallets_file():
    wallets = {}
    with open(WALLETS_CSV_FILENAME, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            wallets[row[0]] = float(row[1])
    return wallets

def write_error(error_string):
  return error_string

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
    return f'<div>{html}</div>'

def amount2str(amount):
    amount = float(amount)
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
