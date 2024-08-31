import datetime, pytz
from django.utils.crypto import get_random_string
import re
import hashlib

def evalResponse(x):
  new_dict={}
  myprint(x, new_dict)
  return new_dict

def myprint(x, new_dict):
  my_list = x.items() if isinstance(x, dict) else enumerate(x)

  for k, v in my_list:
    if isinstance(v, dict) or isinstance(v, list):
      myprint(v, new_dict)
    else:
      new_dict[k]=v

def deleteSessions(list, request):
  try:
    for i in list:
      del request.session[i]
    return True
  except Exception as e:
    return False

def setSessions(keys, values, request):
  try:
    for i, j in (keys, values):
      request.session[i] = j
    return True
  except:
    return False


def generate_ordernumber(value):
    if value >= 10:
        return str(value)
    else:
        return str(0) + str(value)


def timezoneshit():
    d = pytz.timezone('Africa/Lagos')
    d = datetime.datetime.now(d)
    ordernumber = str(d.year) + generate_ordernumber(d.month) + generate_ordernumber(d.day) + generate_ordernumber(d.hour + 1) + generate_ordernumber(d.minute) + get_random_string(length=8)
    return ordernumber
  
  


def correct_url(url):
    match = re.match(r'(https?:\/\/)(.+)', url)
    
    if match:
        protocol = match.group(1)  # Capture 'http://' or 'https://'
        route = match.group(2)     # Capture the rest of the URL
        
        # Replace any occurrence of multiple slashes in the route with a single slash
        corrected_route = re.sub(r'\/{2,}', '/', route)
        if not corrected_route.endswith('/'):
            corrected_route += '/'
        
        # Combine the protocol and the corrected route
        corrected_url = protocol + corrected_route
        return corrected_url
    else:
        return url  # Return the original URL if it doesn't match the regex


def generate_secret_key(activation_key, domain_name):
    combined_string = activation_key + domain_name
    hash_object = hashlib.sha256(combined_string.encode())
    secret_key = hash_object.hexdigest()
    return secret_key