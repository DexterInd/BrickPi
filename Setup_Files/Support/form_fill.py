import requests
uid=open("uid.txt","r")
email=open("email.txt","r")
prob=open("pdesc.txt","r")
err=open("error_log.txt","r")

url = 'https://docs.google.com/forms/d/1XnYfFcKMtWjJ7dRgEl3kbMMWMoCduBYp7G5TqvWmAXo/formResponse'
form_data = {'entry.1096877754':uid.read(),'entry.1390387548':email.read(),'entry.95207887':prob.read(),"entry.913116113":err.read()}
user_agent = {'Referer':'https://docs.google.com/forms/d/1XnYfFcKMtWjJ7dRgEl3kbMMWMoCduBYp7G5TqvWmAXo/viewform','User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
try:
	r = requests.post(url, data=form_data, headers=user_agent,timeout=5)
        print '1'
except requests.exceptions.Timeout:
	print '0'
uid.close()
email.close()
prob.close()
err.close()
