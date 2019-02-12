
import argparse
import sys
import re
import logging
import requests
import json

zip_re = re.compile('^[0-9]{5}(?:-[0-9]{4})?$')
supported_zip = [
"20500", "20748", "34248", "37312", "46523",
"46523", "75093", "75876", "84111", "95361"
]

def validate_arguments(args):
    broken = 0
    m = zip_re.match(args.zipcode.strip())
    if m:
        if args.zipcode.strip() in supported_zip:
            pass
        else:
            logging.error(" Supported Zip Codes are: " + str(supported_zip))
            broken = 1
    else:
        logging.error(" Zip Code is not Valid. Please enter valid zip code")
        broken = 1
    try:
        subtotal = float(args.subtotal)
        if subtotal <= 0:
            logging.error(" Given Subtotal value should be greater than 0")
            broken = 1
    except ValueError:
        logging.error(" Given Subtotal is not valid.")
        broken = 1
    if broken:
        exit(1)
    return


def argument_parse():
    parser = argparse.ArgumentParser(description="Tax, verify, and return a given order")
    parser.add_argument('--zipcode', help="Zip Code", required=True)
    parser.add_argument('--subtotal', help="Sub Total", required=True)
    args = parser.parse_args()
    return args


class TaxCalculator:
    def __init__(self, args):
        self.zipcode = args.zipcode
        self.subtotal = args.subtotal
        self.get_tax_rate()
        self.tax_totals()
        self.post_total()

    def get_tax_rate(self):
        payload = {'zipcode': self.zipcode}
        try:
            output = requests.get(url="https://deft-cove-227620.appspot.com/api/tax", auth=('user', 'token'),
                              params=payload)
        except requests.exceptions.RequestException as e:
            logging.error(" Error in getting tax_rate from API", e)
            exit(1)
        self.tax_rate = json.loads(output.text)["tax_rate"]

    def percentage(self, percent, whole):
        return round((percent * whole) / 100.000, 2)

    def tax_totals(self):
        self.tax_total = str(self.percentage(float(self.tax_rate), float(self.subtotal)))
        self.total = round(float(self.subtotal) + float(self.tax_total), 2)

    def post_total(self):
        payload = {'zipcode': self.zipcode,
                   'sub_total': self.subtotal,
                   'tax_rate': self.tax_rate,
                   'tax_total': self.tax_total,
                   'total': str(self.total)}
        try:
            output = requests.post(url="https://deft-cove-227620.appspot.com/api/order", auth=('user', 'token'),
                               params=payload)
        except requests.exceptions.RequestException as e:
            logging.error(" Error in posting total to API", e)
            exit(1)
        print(output.text)


args = argument_parse()
validate_arguments(args)
tax_obj = TaxCalculator(args)
