from utils import read_wallet, add_wallet, write_error, render_send_prep, send, render_email_template, amount2str
from flask import Flask, render_template, request
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
        return render_template('wallet.html', input=read_wallet(wallet_address, passphrase))

    # Send template information to index.html
    return render_template('index.html', form=form)

# admin interface to add to a wallet (existing or not)
@app.route('/about')
def about():
  return render_template('about.html')

# admin interface to add to a wallet (existing or not)
@app.route('/add', methods=['GET'])
def admin():
  wallet_address = request.args.get('wallet_address')
  amount = request.args.get('amount')
  passphrase = wallet_address
  if not wallet_address or not amount or not passphrase:
    error_string = "usage: /add?wallet_address=[addr]&amount=[billion_crapto]"
    return render_template('error.html', input=write_error(error_string))
  if amount < 0:
    error_string = "nice try, but amount has to be greater than zero."
    return render_template('error.html', input=write_error(error_string))
  return render_template('add.html', input=add_wallet(wallet_address, passphrase, amount))

@app.route('/mine', methods=['GET'])
def mine_page():
  wallet_address = request.args.get('wallet_address')
  passphrase = wallet_address
  if not wallet_address or not passphrase:
    error_string = "usage: /mine?wallet_address=[addr]"
    return render_template('error.html', input=write_error(error_string))
  MINE_INCREMENT = 0.001
  MINE_TIME = 3.0
  time.sleep(MINE_TIME)
  rendered_output = "<div><center><h4>Mined %s</h4></center></div><hr>" % amount2str(MINE_INCREMENT)
  rendered_output += add_wallet(wallet_address, passphrase, MINE_INCREMENT)
  return render_template('add.html', input=rendered_output)

# admin interface to add to a wallet (existing or not)
@app.route('/send_prep', methods=['GET', 'POST'])
def send_prep_page():
  from_address = request.args.get('from')
  passphrase = from_address
  return render_template('send.html', input=render_send_prep(from_address, passphrase))

# admin interface to add to a wallet (existing or not)
@app.route('/send', methods=['GET', 'POST'])
def send_page():
  from_address = request.args.get('from')
  to_address = request.args.get('to')
  amount = request.args.get('amount')
  passphrase = from_address

  if not from_address or not to_address or not amount or not passphrase:
    error_string = "usage: /send?from=[wallet_addr]&to=[wallet_addr]&amount=[billion_crapto]"
    if not from_address:
      error_string += "\n(you lacked from_address)"
    if not to_address:
      error_string += "\n(you lacked to_address)"
    if not amount:
      error_string += "\n(you lacked amount)"
    return render_template('error.html', input=write_error(error_string))
  if amount < 0:
    error_string = "nice try, but amount has to be greater than zero."
    return render_template('error.html', input=write_error(error_string))

  send_output = send(from_address, to_address, passphrase, amount)
  return render_template('sent.html', send_output=send(from_address, to_address, passphrase, amount), email_template_output=render_email_template(to_address, amount))

if __name__ == "__main__":
    print(("* Loading Flask starting server..."
           "please wait until server has fully started"))
    # Run app
    app.run(host="0.0.0.0", port=80)
