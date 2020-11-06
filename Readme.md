#Readme

## User APIs
```http request
POST /api/user/auth/sign_up

Request-Body
{"email":"abc@brightmoney.co", "password":"abcd123.", "first_name": "First", "last_name": "Name"}


POST /api/user/auth/login

Request-Body
{"email":"abc@brightmoney.co", "password":"abcd123."}


POST /api/user/auth/logout

Request-Body
{}

```

## Token APIs
```http request
GET /api/data/token/plaid/get_public_token



POST /api/data/token/plain/get_access_token

Header
"Authorization" : "Token {{auth-token}}"

Request-Body
{"public_token": "public-sandbox-9e24d6ab-2cd9-470f-80ba-486fb9485569"}

```

## Account APIs
```http request
GET /api/data/accounts

Header
"Authorization" : "Token {{auth-token}}"

GET /api/data/accounts/{id}

Header
"Authorization" : "Token {{auth-token}}"

```

## Transactions APIs
```http request
GET /api/data/transactions

Header
"Authorization" : "Token {{auth-token}}"

GET /api/data/transactions/{id}

Header
"Authorization" : "Token {{auth-token}}"


POST /api/data/transactions/webhook

Header
"Authorization" : "Token {{auth-token}}"

Request-Body
{
  "webhook_type": "TRANSACTIONS",
  "webhook_code": "INITIAL_UPDATE",
  "item_id": "kPZwAaLyzNHKNPKWVrgMS81KXmo7R4FLqNJ1m",
  "error": null,
  "new_transactions": 19
}
```
