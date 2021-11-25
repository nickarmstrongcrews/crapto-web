Followed instructions at: https://towardsdatascience.com/deploying-a-python-web-app-on-aws-57ed772b2319
(then modified webapp heavily)

Note: these instructions will only work as-is for strongarm; to let others do it, at the very least, we need to generate and distribute more SSH keys.

Last known URL for Crapto web server: http://18.237.79.243/

To view a wallet, just point a web browser at the address above. There should always be two test wallets with addresses "wallet1" and "wallet2" and no passphrase. If you have a wallet pre-allocated to you, the convention is to use your first name lowercase and the same for passphrase.

To restart web server:
0) SSH into VM using instructions below
1) kill the old web server: sudo killall run_server.py
2) sudo python3 ~/crapto-web/run_server.py

To power up VM:
1) Go to https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#Instances:
2) Note the IP address ("Public IPv4" field on Instances page)


To SSH into VM:
0) be Nick and use strongarm-glaptop2
1) ssh -i "~/crapto/keys/strongarm-glaptop2_priv_key" 18.237.79.243

To manually modify a wallet:
1) SSH into server from strongarm-glaptop2:
2) edit the file ~/crapto-web/data/wallets.csv
3) follow instructions above to restart the server
