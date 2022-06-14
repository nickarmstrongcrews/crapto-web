from utils import read_wallet, add_wallet, write_error, render_send_prep, send, render_email_template, amount2str, hash_passphrase, change_pass, change_pass_prep, render_help, log, create_empty, n4r_donate, n4r_claim, random_nft, retrieve_nft, n4r_donated
from flask import Flask, render_template, request
import requests
from wtforms import Form, TextField, PasswordField, validators, SubmitField, DecimalField, IntegerField
import time

# Create app
app = Flask(__name__)


class ReusableForm(Form):
    wallet = TextField("Enter wallet address:", validators=[
                     validators.InputRequired()])
    passphrase = PasswordField("Enter passphrase:", validators=[
                     validators.InputRequired()])
    submit = SubmitField("Enter")


def verify_recaptcha(token, remote_addr):
  recaptcha_url = 'https://www.google.com/recaptcha/api/siteverify'
  recaptcha_secret_key = 'SECRET-KEY'
  payload = {
     'secret': '6LeWbG4gAAAAALoyL_aN_90yVdQaIgTG_-1zV6Vn',
     'response': token,
     'remoteip': remote_addr,
  }
  response = requests.post(recaptcha_url, data = payload)
  result = response.json()
  return result.get('success', False)


# Home page
@app.route("/", methods=['GET', 'POST'])
def home():
    """Home page of app with form"""
    wallet_address = request.args.get('wallet_address')

    # Create form
    form = ReusableForm(request.form, wallet=wallet_address)

    # On form entry and all conditions met
    if request.method == 'POST' and form.validate():
        # Extract information
        wallet_address = request.form['wallet']
        passphrase = request.form['passphrase']
        phash = hash_passphrase(passphrase)
        log('wallet', wallet_address, request.remote_addr)
        return render_template('wallet.html', input=read_wallet(wallet_address, phash))

    # Send template information to index.html
    log('home', wallet_address, request.remote_addr)
    return render_template('index.html', form=form)

# admin interface to add to a wallet (existing or not)
@app.route('/about')
def about():
  log('about', 'none', request.remote_addr)
  return render_template('about.html')

@app.route('/help')
def help():
  log('help', 'none', request.remote_addr)
  return render_template('help.html', input=render_help())

# admin interface to add to a wallet (existing or not)
@app.route('/add', methods=['GET'])
def admin():
  wallet_address = request.args.get('wallet_address')
  amount = request.args.get('amount')
  phash = request.args.get('phash')
  if not phash:
    phash = hash_passphrase(wallet_address)
  if not wallet_address or not amount or not phash:
    error_string = "usage: /add?wallet_address=[addr]&amount=[billion_crapto]"
    return render_template('error.html', input=write_error(error_string))
  if float(amount) < 0:
    error_string = "nice try, but amount has to be greater than zero."
    return render_template('error.html', input=write_error(error_string))
  log('add', wallet_address, request.remote_addr)
  return render_template('add.html', input=add_wallet(wallet_address, phash, amount))

@app.route('/mine', methods=['POST'])
def mine_page():
  wallet_address = request.form.get('wallet_address')
  phash = request.form.get('phash')
  if not phash:
    phash = hash_passphrase(wallet_address)
  if not wallet_address or not phash:
    error_string = "usage: /mine?wallet_address=[addr]"
    return render_template('error.html', input=write_error(error_string))
  MINE_INCREMENT = 0.001
  MINE_TIME = 1.0
  time.sleep(MINE_TIME)
  rendered_output = "<div><center><h4>Mined %s</h4></center></div><hr>" % amount2str(MINE_INCREMENT)
  rendered_output += add_wallet(wallet_address, phash, MINE_INCREMENT)
  log('mine', wallet_address, request.remote_addr)
  return render_template('add.html', input=rendered_output)

def get_param(param_name):
  param = request.form.get(param_name)
  if not param:
    param = request.args.get(param_name)
  return param

# usage: http://craptocurrency.net/create_empty?wallet_address=<new_wallet_name>
@app.route('/create_empty', methods=['GET','POST'])
def create_empty_page():
  wallet_address = get_param('wallet_address')
  log('create_empty', wallet_address, request.remote_addr)
  if create_empty(wallet_address):
    #return send_prep_page_inner(wallet_address)
    return render_template('wallet.html', input=read_wallet(wallet_address, hash_passphrase(wallet_address)))
  else:
    return render_template('error.html', input="<div>Error: cannot create new wallet, since wallet_address %s already exists</div>" % wallet_address)

# balance page, shown after login, can prepare to send form here
@app.route('/send_prep', methods=['POST'])
def send_prep_page():
  return send_prep_page_inner(request.form.get('from'))

def send_prep_page_inner(from_address):
  phash = request.form.get('phash')
  if not phash:
    phash = hash_passphrase(from_address)
  log('send_prep', from_address, request.remote_addr)
  return render_template('send.html', input=render_send_prep(from_address, phash))

# sent page; shown after the send_prep page
@app.route('/send', methods=['POST'])
def send_page():
  from_address = get_param('from')
  to_address = get_param('to')
  amount = get_param('amount')
  phash = get_param('phash')
  sender_name = get_param('sender_name')
  new_checkbox = get_param('new_checkbox')
  if not phash:
    phash = hash_passphrase(from_address)

  if not from_address or not to_address or not amount or not phash:
    error_string = "usage: /send?from=[wallet_addr]&to=[wallet_addr]&amount=[billion_crapto]"
    if not from_address:
      error_string += "\n(you lacked from_address)"
    if not to_address:
      error_string += "\n(you lacked to_address)"
    if not amount:
      error_string += "\n(you lacked amount)"
    return render_template('error.html', input=write_error(error_string))
  if float(amount) < 0:
    error_string = "nice try, but amount has to be greater than zero."
    return render_template('error.html', input=write_error(error_string))
  send_output=send(from_address, to_address, phash, amount, new_checkbox)
  email_template_output=''
  if not 'Error' in send_output:
    email_template_output=render_email_template(to_address, amount, sender_name)
  log('send', to_address, request.remote_addr)
  return render_template('sent.html', send_output=send_output, email_template_output=email_template_output)

@app.route('/change_pass_prep', methods=['POST'])
def change_pass_prep_page():
  wallet_address = request.form.get('wallet_address')
  phash = request.form.get('phash')
  if not phash:
    phash = hash_passphrase(wallet_address)
  log('chpass_prep', wallet_address, request.remote_addr)
  return render_template('change_pass_prep.html', input=change_pass_prep(wallet_address, phash))

# page shown after change_pass_prep
@app.route('/change_pass', methods=['POST'])
def change_pass_page():
  wallet_address = request.form.get('wallet_address')
  old_passphrase = request.form.get('old_passphrase')
  new_passphrase = request.form.get('new_passphrase')
  phash = request.form.get('phash')

  if not phash == hash_passphrase(old_passphrase):
    error_string = "old passphrase incorrect"
    return render_template('error.html', input=write_error(error_string))

  if not wallet_address or not old_passphrase or not new_passphrase or not phash:
    error_string = "usage: /change_pass?wallet_address=[wallet_addr]&old_passphrase=[old_passphrase]&new_passphrase=[new_passphrase]&phash=[passphrase_hash]"

  log('chpass', wallet_address, request.remote_addr)
  return render_template('change_pass.html', input=change_pass(wallet_address, phash, new_passphrase))

##############################################################
# N4R
#####

@app.route('/n4r', methods=['GET'])
def n4r_home():
  log('n4r_home', None, request.remote_addr)
  return render_template('n4r_home.html')

@app.route('/n4r_refugee', methods=['GET'])
def n4r_refugee():
  log('n4r_refugee', None, request.remote_addr)
  return render_template('n4r_generic.html', title="Claim NFT", input=n4r_claim())

@app.route('/n4r_create', methods=['GET'])
def n4r_create():
  log('n4r_donate', None, request.remote_addr)
  return render_template('n4r_generic.html', input=n4r_donate(), title="Donate")

@app.route('/n4r_donated', methods=['POST'])
def n4r_donated_page():
  nft_id = request.form.get('nft_id')
  nft_type = request.form.get('nft_type')
  wallet_address = request.form.get('wallet_address')
  passphrase = request.form.get('passphrase')
  log('n4r_donated', nft_id + '/' + wallet_address, request.remote_addr)
  return render_template('n4r_generic.html', title="Donated NFT", input=n4r_donated(nft_id, nft_type, wallet_address, passphrase))

@app.route('/n4r_retrieved', methods=['GET','POST'])
def n4r_retrieved():
  nft_id = get_param('nft_id')
  claimed_str = get_param('claimed')
  claimed = claimed_str == 'Yes'  # convert to boolean
  log('n4r_retrieved', nft_id, request.remote_addr)
  return render_template('n4r_generic.html', title="Gaze Upon Your NFT", input=retrieve_nft(nft_id, claimed))

@app.route('/n4r_faq', methods=['GET'])
def n4r_faq():
  log('n4r_faq', None, request.remote_addr)
  return render_template('n4r_faq.html')

@app.route('/robosha', methods=['GET'])
def robosha():
  log('robosha', None, request.remote_addr)
  return render_template('robosha_faq.html')

@app.route('/robosha_join', methods=['POST'])
def robosha_join():
  member_id = get_param('member_id')
  token = get_param('g-recaptcha-response')
  success = verify_recaptcha(token, request.remote_addr)
  log('robosha_join', member_id, request.remote_addr)
  if success:
    html = "Sorry, no humans allowed!"
  else:
    html = "Welcome to RobOSHA, %s!" % member_id
  return render_template('robosha_generic.html', title="Join RobOSHA", input=html)

if __name__ == "__main__":
    print(("* Loading Flask starting server..."
           "please wait until server has fully started"))
    # Run app
    app.run(host="0.0.0.0", port=80)
