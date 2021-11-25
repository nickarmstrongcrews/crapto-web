from utils import read_wallet
from flask import Flask, render_template, request
from wtforms import Form, TextField, validators, SubmitField, DecimalField, IntegerField

# Create app
app = Flask(__name__)


class ReusableForm(Form):
    """User entry form for entering specifics"""
    wallet = TextField("Enter wallet address:", validators=[
                     validators.InputRequired()])
    diversity = TextField("Enter passphrase:", validators=[
                     validators.InputRequired()])
    submit = SubmitField("Enter")


# Home page
@app.route("/", methods=['GET', 'POST'])
def home():
    """Home page of app with form"""
    # Create form
    form = ReusableForm(request.form)

    # On form entry and all conditions met
    if request.method == 'POST' and form.validate():
        # Extract information
        wallet_address = request.form['wallet']
        return render_template('wallet.html', input=read_wallet(wallet_address))

    # Send template information to index.html
    return render_template('index.html', form=form)


if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started"))
    # Run app
    app.run(host="0.0.0.0", port=80)
