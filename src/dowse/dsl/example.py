EXAMPLE_PROGRAM = """
The command "Swap 0.001 ETH for $AERO and send half to @user2 and half to @user3" can be executed with the following code:

```code
PUSH "AERO"
GET_TOKEN_ADDRESS
PUSH 0.001
CONVERT_ETH_TO_WEI
// ['0.001_wei:token_amount 'aero_address:address]
EXCHANGE_FUNDS
// ['0.001_aero:token_amount]
PUSH 2
SWAP
DIV
ASSIGN aero_balance
// ['0.0005_aero:token_amount]
PUSH @user2
SWAP
// ['0.0005_aero:token_amount '@user2]
TRANSFER_FUNDS
PUSH @user3
PUSH &aero_balance
TRANSFER_FUNDS
// ['0.0005_aero:token_amount '0.0005_aero:token_amount]
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

Show the stack after each operation.
"""
