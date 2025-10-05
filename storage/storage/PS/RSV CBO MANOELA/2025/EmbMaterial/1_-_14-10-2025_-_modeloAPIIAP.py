import adal

authority = 'https://login.microsoftonline.com/5b6f6241-9a57-4be4-8e50-1dfa72e79a57'
client_id = '404e72ec-2b28-459f-b167-40730d7610ae'
resource_id = client_id

context = adal.AuthenticationContext(authority)
code = context.acquire_user_code(resource_id, client_id)

print(code['message'])

token = context.acquire_token_with_device_code(resource_id, code, client_id)
print(token['accessToken'])