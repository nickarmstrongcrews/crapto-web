import numpy as np
import random
import json
import re
import csv

WALLETS_CSV_FILENAME = "/home/ubuntu/crapto-web/data/wallets.csv"

def read_wallet(wallet_address):
    wallets = {}
    with open(WALLETS_CSV_FILENAME, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            wallets[row[0]] = row[1]

    #wallet_address = str(wallets)
    amount = wallets[wallet_address] if wallet_address in wallets else 0.0
            
    # Formatting in html
    html = ''
    html = addContent(html, header(
        'Wallet ', color='black', gen_text='Amount'))
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
