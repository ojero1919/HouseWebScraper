import scrapy
import re
from time import sleep

class HouseSpider(scrapy.Spider):
    name = 'house'
    start_urls = ['https://classifieds.startribune.com/mn/mortgage-foreclosures/search?limit=240']

    def parse(self, response):
       for link in response.css('div.ap_ad_wrap a::attr(href)'):
            yield response.follow(link.get(), callback = self.parse_notices)

    def parse_notices(self, response):
        notices = response.css('div.details-body')
        for notice in notices:

            #txt = notice.css('div.details-body::text').getall()

            body = notice.get()
           

            #for string in body:
            #    address = string.re(r'STREET ADDRESS OF PROPERTY: (.+),')[0].strip() if string.re(r'STREET ADDRESS OF PROPERTY: (.+)') else None
            #    principal_amount = string.re(r'ORIGINAL PRINCIPAL AMOUNT OF MORTGAGE: (\$[\d,\.]+)')[0] if string.re(r'ORIGINAL PRINCIPAL AMOUNT OF MORTGAGE: (\$[\d,\.]+)') else None
            #    amount_due = string.re(r'THE AMOUNT CLAIMED TO BE DUE ON THE MORTGAGE ON THE DATE OF THE NOTICE: (\$[\d,\.]+) ')[0] if string.re(r'THE AMOUNT CLAIMED TO BE DUE ON THE MORTGAGE ON THE DATE OF THE NOTICE: (\$[\d,\.]+) ') else None
            #    date_of_auction = string.re(r'DATE AND TIME OF SALE: ([\w, ]+) ')[0] if string.re(r'DATE AND TIME OF SALE: ([\w, ]+)') else None

            #address = notice.css('div.details-body::text').re(r'STREET ADDRESS OF PROPERTY: (.+),')[0].strip() if notice.css('p.desktop::text').re(r'STREET ADDRESS OF PROPERTY: (.+),') else None
            #principal_amount = notice.css('div.details-body::text').re(r'ORIGINAL PRINCIPAL AMOUNT OF MORTGAGE: (\$[\d,\.]+),')[0] if notice.css('p.desktop::text').re(r'ORIGINAL PRINCIPAL AMOUNT OF MORTGAGE: (\$[\d,\.]+),') else None
            #amount_due = notice.css('div.details-body::text').re(r'THE AMOUNT CLAIMED TO BE DUE ON THE MORTGAGE ON THE DATE OF THE NOTICE: (\$[\d,\.]+),')[0] if notice.css('p.desktop::text').re(r'THE AMOUNT CLAIMED TO BE DUE ON THE MORTGAGE ON THE DATE OF THE NOTICE: (\$[\d,\.]+),') else None
            #date_of_auction = notice.css('div.details-body::text').re(r'DATE AND TIME OF SALE: ([\w, ]+),')[0] if notice.css('p.desktop::text').re(r'DATE AND TIME OF SALE: ([\w, ]+),') else None
            title_match = 'NOTICE OF MORTGAGE FORECLOSURE SALE'


            address = None
            principal_amount = None
            amount_due = None
            date_of_auction = None
            place = None

            if(re.search(r'NOTICE OF MORTGAGE FORECLOSURE SALE(.+?)', body)):
                #address_match = re.search(r'ADDRESS: (.+?),', body)
                #address_match = re.search(r'ADDRESS (?.*),', body)
                #MORTGAGED PROPERTY ADDRESS: 959 4th Street East, Saint Paul, MN 55106
                address_match = re.search(r'(\s*\d+\w+.*MN\s*\d\d\d\d\d)', body)
                #address_match2 = re.search(r'(\s*\d+ [A-Z1-9]+[a-z].*)', body)
                #address_match2 = re.search(r'(\s*\d+ [A-Z1-9]+[a-z].*)', body)
                
                if not address_match:
                    address_match2 = re.compile(r"(ADDRESS.*PROPERTY.*:.*(\n)?(.+\n)?^\w+.*MN\s*\d\d\d\d\d)", re.MULTILINE)
                    if not address_match2:
                        address_match2 = re.compile(r"(PROPERTY.*ADDRESS.*:.*(\n)?(.+\n)?^\w+.*MN\s*\d\d\d\d\d)", re.MULTILINE)

                    matchess = address_match2.findall(body)
                    address = matchess.pop()
                else:
                    address = address_match.group(1).strip() if address_match.group(1) else address_match.group(0).strip()
                
                principal_amount_match = re.search(r'ORIGINAL PRINCIPAL AMOUNT OF MORTGAGE: (\$[\d,\.]+)', body)
                if principal_amount_match:
                    principal_amount = principal_amount_match.group(1)
                #AMOUNT DUE AND CLAIMED TO BE DUE AS OF DATE OF NOTICE:$244,233.61
                amount_due_match = re.search(r'THE AMOUNT CLAIMED TO BE DUE ON THE MORTGAGE ON THE DATE OF THE NOTICE: (\$[\d,\.]+)', body)
                #amount_due_match = re.search(r'AMOUNT.*DUE.*CLAIMED:.*(\$[\d,\.]+)', body)
                if not amount_due_match:
                    aamount_due_match2 = re.compile(r'AMOUNT DUE.*CLAIMED.*:.*\n?.*(\$[\d,\.]+)', re.MULTILINE)
                    matchesss = aamount_due_match2.findall(body)
                    #print(amount_due_match)
                    if matchesss.pop(0):
                        amount_due_match = matchesss.pop(0)
                    else:
                        amount_due_match = matchesss.pop(1)
                else:
                    amount_due = amount_due_match.group(1) if amount_due_match.group(1) else amount_due_match.group(0) 
                
#DATE AND TIME OF SALE:
#September 9, 2024 at 10 AM .
                date_of_auction_match = re.search(r'DATE AND TIME OF SALE:\n?([\w, ]+).*', body)
                if date_of_auction_match is not None:               
                    date_of_auction = date_of_auction_match.group(1).strip() if date_of_auction_match.group(1) else date_of_auction_match.group(0)                
                
                place_match = re.search(r'PLACE OF SALE: (.+?),', body)
                if place_match:
                    place = place_match.group(1).strip()

                link = notice.css('a::attr(href)').get()

                yield{
                    #'body': txt,
                    'address': address,
                    'principal amount': principal_amount,
                    'amount due': amount_due,
                    'date of auction': date_of_auction,
                    'place of sale': place,
                    'link': response.urljoin(link),  # Ensure the link is absolute
                }           
                sleep(0.05)
           
