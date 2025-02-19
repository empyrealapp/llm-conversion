EXAMPLE_PROGRAM = """
The command "Swap 0.001 ETH for $AERO and send half to @user2 and half to @user3" can be executed with the following code:

```code
PUSH "AERO"
GET_TOKEN_ADDRESS
PUSH 0.001
CONVERT_ETH_TO_WEI
EXCHANGE_FUNDS
// ['0.001_aero:token_amount]

PUSH 0.5  // get 50% of the aero
SWAP
GET_PERCENTAGE
ASSIGN aero_balance  // assign the 50% aero to aero_balance

PUSH @user2
SWAP
TRANSFER_FUNDS // transfer the 50% aero to user2
PUSH @user3
PUSH &aero_balance
TRANSFER_FUNDS  // transfer the same aero amount to user3
```

---

Example Functions:

```code
PUSH 300
PUSH 200
PUSH 100
PUSH 500
// ['500:integer '100:integer '200:integer '300:integer]
DIV
// ['5:integer '200:integer '300:integer]
PUSH 3
GREATER_THAN
// ['false:boolean '200:integer '300:integer]
BRANCH
// ['300:integer]
```

Ensure the stack is empty at the end, with no unused values.
Return only the code without any additional text.

If you are giving 20% to one person and 80% to another,
you need to get both percentages of the whole, ie.

```code
PUSH 0.001
CONVERT_ETH_TO_WEI
ASSIGN eth_balance
PUSH 0.2
PUSH &eth_balance
GET_PERCENTAGE
ASSIGN 20_percent_eth

PUSH 0.8
PUSH &eth_balance
GET_PERCENTAGE
ASSIGN 80_percent_eth
```

Token amounts are not global, they just represent a location, an amount, and a token address.
When you transfer one token amount, it will not affect any other token amounts.
"""
