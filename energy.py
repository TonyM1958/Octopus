##################################################################################################
"""
Module:   Energy Analysis
Date:     13 February 2023
Author:   Tony Matthews
"""
##################################################################################################

##################################################################################################

import json
import datetime
import math
import matplotlib.pyplot as plt
import requests
from requests.auth import HTTPBasicAuth

# global settings
debug_setting = 1       # debug setting: 0 = silent, 1 = info, 2 = details
base_url = 'https://api.octopus.energy/v1/'
credentials = None      # account credetials for API access
e_meter = None          # electricity import meter details
x_meter = None          # electricity export meter details
g_meter = None          # gas meter details

def c_int(i):
    # handle None in integer conversion
    if i is None :
        return None
    return int(i)

def c_float(n):
    # handle None in float conversion
    if n is None :
        return None
    return float(n)

def parse_datetime(s, f='%Y-%m-%dT%H:%M:%SZ') :
    # handle None in datetime conversion
    if s is None :
        return None
    return(datetime.datetime.strptime(s,f))

class Meter :
    """
    Meter details
    """ 

    def __init__(self, mpn, number) :
        self.mpn = mpn
        self.number = number
        return

def account_setting(api_key = None, url = None, e = None, x = None, g = None, debug = None) :
    """
    Load account settings to use
    """ 
    global debug_setting, e_meter, x_meter, g_meter
    if debug is not None :
        debug_setting = debug
        print(f"debug setting: {debug}")
    if url is not None :
        base_url = url
        if debug_setting > 0 :
            print(f"base url: {url}")
    if api_key is not None :
        credentials = HTTPBasicAuth(api_key,'')
        if debug_setting > 0 :
            print(f"credentials set")
    if e is not None :
        e_meter = e
        if debug_setting > 0 :
            print(f"Electricity meter: MPAN={e_meter.mpn}, number={e_meter.number}")
    if x is not None :
        x_meter = x
        if debug_setting > 0 :
            print(f"Export meter: MPAN={x_meter.mpn}, number={x_meter.number}")
    if g is not None :
        g_meter = g
        if debug_setting > 0 :
            print(f"Gas meter: MPRN={g_meter.mpn}, number={g_meter.number}")
    return

products_json = None        # cached product details

class Product :
    """
    Load Product details
    """ 

    def __init__(self, code = '', clear_cache = False) :
        # load product details using a partial product code
        global products_json
        if clear_cache :
            products_json = None
        if products_json is None :
            response = requests.get(base_url + 'products', auth=credentials)
            if response.status_code != 200 :
                print("** response code getting list of products = {response.status_code}")
                return
            products_json = response.json().get('results')
        p = [r for r in products_json if r.get('code')[:len(code)] == code]
        # check how many products we found
        if p is None or len(p) == 0 :
            print(f"** no products were found using code '{code}'")
            return
        if len(p) > 1 :
            print(f"** more than 1 product was found using code '{code}':")
            for t in p :
                print(f"   {t.get('code')} / {t.get('display_name')}")
            return
        # load product details
        self.code = p[0].get('code')
        response = requests.get(base_url + 'products/' + self.code + '/', auth=credentials)
        if response.status_code != 200 :
            print(f"** response code getting product details for {self.code} = {response.status_code}")
            return
        p = response.json()
        self.display_name = p.get('display_name')
        self.full_name = p.get('full_name')
        self.description = p.get('description')
        self.is_variable = p.get('is_variable')
        self.is_green = p.get('is_green')
        self.is_outgoing = 'OUTGOING' in self.code
        self.term = c_int(p.get('term'))
        self.available_from = p.get('available_from')
        self.available_to = p.get('available_to')
        t = p.get('single_register_electricity_tariffs')
        if t is not None and len(t) != 0 :
            t = t.get('_A').get('direct_debit_monthly')
            if self.is_outgoing :
                self.x_daily_charge = c_float(t.get('standing_charge_inc_vat'))
                self.x_unit_rate = c_float(t.get('standard_unit_rate_inc_vat'))
            else :
                self.e_daily_charge = c_float(t.get('standing_charge_inc_vat'))
                self.e_unit_rate = c_float(t.get('standard_unit_rate_inc_vat'))
        t = p.get('single_register_gas_tariffs')
        if t is not None and len(t) != 0 :
            t = t.get('_A').get('direct_debit_monthly')
            self.g_daily_charge = c_float(t.get('standing_charge_inc_vat'))
            self.g_unit_rate = c_float(t.get('standard_unit_rate_inc_vat'))
        return

    def report(self) :
        # show product details
        if hasattr(self, 'code') :
            print(f"code: {self.code}")
            print(f"   display_name:   {self.display_name}")
            print(f"   full_name:      {self.full_name}")
            print(f"   description:    {self.description}")
            print(f"   is_variable:    {self.is_variable}")
            print(f"   is_green:       {self.is_green}")
            print(f"   is_outgoing:    {self.is_outgoing}")
            print(f"   term:           {self.term}")
            print(f"   available_from: {self.available_from}")
            print(f"   available_to:   {self.available_to}")
            if hasattr(self, 'e_daily_charge') :
                print(f"   e_daily_charge: {self.e_daily_charge}")
            if hasattr(self, 'e_unit_rate') :
                print(f"   e_unit_rate:    {self.e_unit_rate}")
            if hasattr(self, 'x_daily_charge') :
                print(f"   x_daily_charge: {self.x_daily_charge}")
            if hasattr(self, 'x_unit_rate') :
                print(f"   x_unit_rate:    {self.x_unit_rate}")
            if hasattr(self, 'g_daily_charge') :
                print(f"   g_daily_charge: {self.g_daily_charge}")
            if hasattr(self, 'g_unit_rate') :
                print(f"   g_unit_rate:    {self.g_unit_rate}")
            return
        print(f"** {self} is not a valid product")
        return


