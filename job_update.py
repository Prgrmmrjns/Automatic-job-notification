from email.message import EmailMessage
from bs4 import BeautifulSoup
import ssl, smtplib, os, requests, time
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("PASSWORD")
RECEIVER = 'jonascw@web.de'

subject = 'Neueste Stellenangebote'
body = '''
Hallo Flo, 
hier ist Jonas. Das ist eine automatisierte Email, die du 
einmal am Tag kriegst. Im Anhang findest du die neuesten
Jobangebote für Medizintechniker in der Nähe.
Gern geschehen!
'''
print(EMAIL_ADDRESS)
print(PASSWORD)
job = input("Nach welchem Job suchst du: ")
search_area = input("Welche Stadt: ")
url = 'https://www.stepstone.de/jobs/' + job + '/in-' + search_area + '?radius=30'

stepstone =	{
  "job_name_el": "a",
  "job_name_cl": "resultlist-1uvdp0v",
  "company_el": "span",
  "company_cl": "resultlist-1va1dj8",
  "job_location_el":"span",
  "job_location_cl":"resultlist-suri3e"
}

def find_jobs():
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('div',class_='Wrapper-sc-11673k2-0')
    num_offers = len(jobs)
    print(f'{num_offers} Stellenangebote gefunden!')
    with open(f'posts/Angebote.txt','w') as f:
        for index,job in enumerate(jobs):
            job_name = job.find(stepstone["job_name_el"],class_=stepstone["job_name_cl"]).text
            job_link = job.a['href']
            company = job.find(stepstone["company_el"],class_=stepstone["company_cl"]).text
            job_location = job.find(stepstone["job_location_el"],class_=stepstone["job_location_cl"]).text
            publication_date = job.find('time').text
            home_office = job.find('span', class_ = 'resultlist-1u79rpn')
            if home_office != None:
                home_office = home_office.text
            else:
                home_office = 'Kein Home-Office'
            if 'Woche' not in publication_date:  
                f.write(f'Stellenbeschreibung: {job_name} \n')
                f.write(f'Standort: {job_location} \n')
                f.write(f'Arbeitgeber: {company}\n')
                f.write(f'{publication_date} veröffentlicht.\n')
                f.write(f'{home_office}\n')
                f.write(f'Link: {job_link}\n')
                f.write(f'\n')
                f.write(f'\n')
    print("Angebote wurden gespeichert!")

find_jobs()

email = EmailMessage()
email['From'] = EMAIL_ADDRESS
email['To'] = RECEIVER
email['Subject'] = subject
email.set_content(body)

context = ssl.create_default_context()

with open('posts/Angebote.txt', 'rb') as f:
    file_data = f.read()

email.add_attachment(file_data, maintype='text', subtype='plain',filename='Angebote.txt')

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
    smtp.login(EMAIL_ADDRESS,PASSWORD)
    smtp.sendmail(EMAIL_ADDRESS,RECEIVER, email.as_string())

print("Email sent.")