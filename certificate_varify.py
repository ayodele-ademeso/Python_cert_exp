import ssl
import socket
import datetime
import boto3

client = boto3.client("ses", region_name="us-east-1")

print(f"Program to check SSL certificate validity and expiration date\n")

##opening file
with open("server_ip.txt") as ip_file:

    ##check  certificate expiration
    for ip in ip_file:

        try:
            soon_to_expire = []
            host, port = ip.strip().split(":")
            print(f"\nChecking certifcate for server {host}")
            context = ssl.create_default_context()
            with socket.create_connection((host, port)) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    certificate = ssock.getpeercert()
                certExpires = datetime.datetime.strptime(
                    certificate["notAfter"], "%b %d %H:%M:%S %Y %Z"
                )
                daysToExpiration = (certExpires - datetime.datetime.now()).days
                if daysToExpiration < 45:
                    print(f"Expires on: {certExpires} in {daysToExpiration} days")
                    soon_to_expire.append(host)
                    
                    ##preparing mailbody
                    for h in soon_to_expire:
                        #print(h)
                        mailbody = (
                            "Server name: " + h + ", expires in " + str(daysToExpiration) + " days."
                        )
                    # print(mailbody)
                    # print("here")
        except:
            print(f"error on connection to Server, {host}")

        ##sending ses email
    response = client.send_email(
        Destination={
            "ToAddresses": ["nerdydreams92@gmail.com"],
        },
        Message={
            "Body": {
                "Text": {
                    "Charset": "UTF-8",
                    "Data": "The following certificates will expire soon; "
                    + mailbody
                    + "\nThank you.",
                },
            },
            "Subject": {
                "Charset": "UTF-8",
                "Data": "Certificate Expiring Soon",
            },
        },
        Source="nerdydreams92@gmail.com",
    )

print(f"\nCert check complete!")