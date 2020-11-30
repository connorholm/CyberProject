def main():
    import urllib.request
    pub_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    print(pub_ip)
main()
