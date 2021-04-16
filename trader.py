#Kucoin trading bot
import sys
sys.path.append('C:\\Users\\zinex\\Documents\\Python\\Trader')
from kucoinKeys import sandbox_keys as keys

apiKey = keys['apiKey']
apiSecret = keys['apiSecret']
passphrase = keys['apiPassphrase']

from kucoin.client import User 
client = User(apiKey, apiSecret, apiPassphrase, is_sandbox=True)

print(client)
