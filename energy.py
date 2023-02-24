##################################################################################################
"""
Module:   Energy Analysis
Date:     13 February 2023
Author:   Tony Matthews
"""
##################################################################################################

##################################################################################################

import os.path
import json
import datetime
import math
import matplotlib.pyplot as plt
import requests
from requests.auth import HTTPBasicAuth

# global settings
debug_setting = 0       # debug setting: 0 = silent, 1 = info, 2 = details
base_url = 'https://api.octopus.energy/v1/'
credentials = None      # account credetials for API access
gsp = None              # region code
imp_meter = None        # electricity import meter details
exp_meter = None        # electricity export meter details
gas_meter = None        # gas meter details
page_width = 140        # maximum text string for display
figure_width = 24       # width of plots

regions = {'_A':'Eastern England', '_B':'East Midlands', '_C':'London', '_D':'Merseyside and Northern Wales', '_E':'West Midlands', '_F':'North Eastern England', '_G':'North Western England', '_H':'Southern England',
    '_J':'South Eastern England', '_K':'Southern Wales', '_L':'South Western England', '_M':'Yorkshire', '_N':'Southern Scotland', '_P':'Northern Scotland'}

def c_int(i):
    # handle None in integer conversion
    if i is None :
        return None
    return int(i)

def c_float(n):
    # handle None in float conversion
    if n is None :
        return float(0)
    return float(n)

# tracked time periods. Time is stored as 4 digit string
tracked = {
        # tracked time periods
        'night' : {'start' : '0130', 'end' : '0500', 'label' : 'Night time off peak', 'color' : 'green'},
        'am'    : {'start' : '0630', 'end' : '1030', 'label' : 'Morning peak', 'color' : 'orange'},
        'pm'    : {'start' : '1230', 'end' : '1500', 'label' : 'Afternoon off peak', 'color' : 'grey'},
        'peak'  : {'start' : '1600', 'end' : '2000', 'label' : 'Evening peak', 'color' : 'red'}}

def period_setting (t, start=None, end=None, label=None, color=None) :
    global tracked
    if t not in tracked.keys() :
        tracked[t] = {}
    if start is not None :
        tracked[t]['start'] = start
    if end is not None :
        tracked[t]['end'] = end
    if label is not None :
        tracked[t]['label'] = label
    if color is not None :
        tracked[t]['color'] = color
    return

def time_add(t, n = 30) :
    # add or remove minutes from time e.g. 0100 -> 0130, 1430 -> 1500
    h = c_int(t[:2])
    m = c_int(t[-2:]) + n
    while m > 59 :
        h += 1
        m -= 60
    while m < 0 :
        h -= 1
        m += 60
    while h > 23 :
        h -= 24
    while h < 0 :
        h += 24
    return f"{h:02d}{m:02d}"

def time_list(p) :
    global tracked
    start = tracked[p]['start']
    end = tracked[p]['end']
    if c_int(start) > c_int(end) :
        print(f"** {tracked[p]['label']} period start {start} cannot be after end {end}")
        return None
    new = [start]
    while start != end :
        start = time_add(start,30)
        new.append(start)
    return new

def time_span(t) :
    # return time span for a period
    global tracked
    start = tracked[t]['start']
    end = time_add(tracked[t]['end'], -1)
    return f"{start} to {end}"

class Meter :
    """
    Load meter info
    """
    def __init__(self, mpn, ser) :
        global debug_setting, base_url, gsp, credentials
        self.mpn = mpn
        self.ser = ser
        if gsp is None :
            response = requests.get(base_url + 'electricity-meter-points/' + self.mpn + '/', auth=credentials)
            if response.status_code == 200:
                gsp = response.json().get("gsp")
                if debug_setting > 1 :
                    print(f"{self.mpn} / {self.ser} validated")
        self.gsp = gsp
        return

def account_setting(api_key = None, url = None, r = None, imp = None, exp = None, gas = None, debug = None, p = None, f = None) :
    """
    Load account settings to use
    """ 
    global debug_setting, base_url, gsp, imp_meter, exp_meter, gas_meter, page_width, figure_width
    if debug is not None :
        debug_setting = debug
        if debug_setting > 1 :
            print(f"Debug set to {debug}")
    if p is not None :
        page_width = p
        if debug_setting > 1 :
            print(f"Page width set to {page_width}")
    if f is not None :
        figure_width = f
        if debug_setting > 1 :
            print(f"Figure width set to {figure_width}")
    if api_key is not None :
        credentials = HTTPBasicAuth(api_key,'')
        if debug_setting > 0 :
            print(f"Octopus credentials provided")
    if url is not None :
        base_url = url
        if debug_setting > 1 :
            print(f"Base url: {url}")
    if r is not None :
        gsp = r
        if debug_setting > 0 :
            print(f"Region is {regions[gsp]} ({gsp})")
    if imp is not None :
        imp_meter = imp
        if debug_setting > 1 :
            print(f"Electricity: MPAN={imp_meter.mpn}, serial={imp_meter.ser}, gsp={imp_meter.gsp}")
    if exp is not None :
        exp_meter = exp
        if debug_setting > 1 :
            print(f"Export: MPAN={exp_meter.mpn}, serial={exp_meter.ser}, gsp={imp_meter.gsp}")
    if gas is not None :
        gas_meter = gas
        if debug_setting > 1 :
            print(f"Gas: MPRN={gas_meter.mpn}, serial={gas_meter.ser}, gsp={gas_meter.gsp}")
    return

product_codes = None        # cached product codes

class Product :
    """
    Load Product details
    """ 

    def __init__(self, code = '', days = 7, clear_cache = False, period_to = None) :
        # load product details using a partial product code
        global product_codes, base_url, credentials
        if clear_cache :
            product_codes = None
        if product_codes is None :
            response = requests.get(base_url + 'products', auth=credentials)
            if response.status_code != 200 :
                print("** response code getting list of products = {response.status_code}")
                return
            product_codes = {}
            for r in response.json().get('results') :
                product_codes[r.get('code')] = r.get('description')
        p = [r for r in product_codes.keys() if r[:len(code)] == code]
        # check how many products we found
        if p is None or len(p) == 0 :
            print(f"** no products were found using code '{code}'")
            return
        if len(p) > 1 :
            print(f"** more than 1 product was found using code '{code}':")
            for t in p :
                print(f"   {t}: {product_codes[t][:150]}")
            return
        # load product details
        self.code = p[0]
        response = requests.get(base_url + 'products/' + self.code + '/', auth=credentials)
        if response.status_code != 200 :
            print(f"** response code getting product details for {self.code} from {response.url} was {response.status_code}")
            return
        self.json = response.json()
        self.display_name = self.json.get('display_name')
        self.full_name = self.json.get('full_name')
        self.description = self.json.get('description')
        self.is_variable = self.json.get('is_variable')
        self.is_green = self.json.get('is_green')
        # detect export products
        self.is_outgoing = 'OUTGOING' in self.code
        self.term = c_int(self.json.get('term'))
        # datetime conversion not reliable, store date as provided for now
        self.available_from = self.json.get('available_from')
        self.available_to = self.json.get('available_to')
        # load prices. standing charges in p/day, unit rates in p/kwh
        if gsp is not None :
            self.gsp = gsp
            t = self.json.get('single_register_electricity_tariffs')
            if t is not None and len(t) != 0 :
                t = t.get(self.gsp)
                t = t.get('direct_debit_monthly')
                if self.is_outgoing :
                    self.exp_code = t.get('code')
                    self.exp_day = c_float(t.get('standing_charge_inc_vat'))
                    self.exp_kwh = c_float(t.get('standard_unit_rate_inc_vat'))
                else :
                    self.imp_code = t.get('code')
                    self.imp_day = c_float(t.get('standing_charge_inc_vat'))
                    self.imp_kwh = c_float(t.get('standard_unit_rate_inc_vat'))
            t = self.json.get('single_register_gas_tariffs')
            if t is not None and len(t) != 0 :
                t = t.get(self.gsp)
                t = t.get('direct_debit_monthly')
                self.gas_code = t.get('code')
                self.gas_day = c_float(t.get('standing_charge_inc_vat'))
                self.gas_kwh = c_float(t.get('standard_unit_rate_inc_vat'))
        # load 30 minute pricing, if available
        if days > 31 :
            print(f"** too many days, maximum is 31")
            days = 31
        self.days = days
        self.load_30_minute_prices(period_to)
        return

    def __str__(self) :
        # format product details for display
        global regions, imp_meter, exp_meter, gas_meter, debug_setting, page_width
        if hasattr(self, 'code') :
            standard_pricing = len(self.keys) != 48
            s = f"Product details for code: {self.code}\n"
            s += f"   Display name:      {self.display_name}\n"
            s += f"   Full name:         {self.full_name}\n"
            s += f"   Description:       {self.description[:page_width]}\n"
            s += f"   Available from:    {self.available_from}\n"
            s += f"   Available to:      {self.available_to}\n"
            if self.term is not None :
                s += f"   Term:              {self.term} months\n"
            if imp_meter is not None :
                if hasattr(self, 'gsp') :
                    s += f"   Your region (GSP): {regions[self.gsp]}\n"
                if hasattr(self, 'imp_code') :
                    s += f"   Import price code: {self.imp_code}\n"
                if hasattr(self, 'imp_day'):
                    s += f"   Import day rate:   {self.imp_day} p/day inc VAT\n"
                if hasattr(self, 'imp_kwh') and standard_pricing :
                    s += f"   Import unit cost:  {self.imp_kwh} p/kwh inc VAT\n"
            if exp_meter is not None:
                if hasattr(self, 'exp_code') :
                    s += f"   Export price code: {self.exp_code}\n"
                if hasattr(self, 'exp_day') :
                    s += f"   Export day cost:   {self.exp_day} p/day inc VAT\n"
                if hasattr(self, 'exp_kwh') and standard_pricing:
                    s += f"   Export unit cost:  {self.exp_kwh} p/kwh inc VAT\n"
            if gas_meter is not None:
                if hasattr(self, 'gas_code') :
                    s += f"   Gas price code:    {self.gas_code}\n"
                if hasattr(self, 'gas_day') :
                    s += f"   Gas day cost:      {self.gas_day} p/day inc VAT\n"
                if hasattr(self, 'gas_kwh') :
                    s += f"   Gas unit cost:     {self.gas_kwh} p/kwh inc VAT\n"
            if debug_setting > 1 :
                s += f"   Is variable:       {self.is_variable}\n"
                s += f"   Is green:          {self.is_green}\n"
                s += f"   Is outgoing:       {self.is_outgoing}\n"
            if not standard_pricing :
                s += f"   Average " + (f"export prices" if self.is_outgoing else f"import prices inc VAT") + f" over last {self.days} days:\n"
                for t in self.tracked.keys() :
                    s += f"       {tracked[t]['label']+':':<20} {self.period_avg[t]:.2f} p/kwh ({time_span(t)})\n"
            return s[:-1]
        return f"** not a valid product\n"

    def load_30_minute_prices(self, period_to = None) :
        # get the pricing for a product
        global tracked
        if self.code is None:
            return
        tariff_code = None
        if hasattr(self, 'imp_code') or hasattr(self, 'exp_code') :
            tariff_code = self.exp_code if self.is_outgoing else self.imp_code
        if tariff_code is None:
            return
        params = {}
        if period_to is None :
            period_to = datetime.datetime.now()
        self.period_to = period_to.replace(hour=23, minute=00, second=00, microsecond=0) + datetime.timedelta(days=1)
        self.period_from = period_to + datetime.timedelta(days=-self.days-1)
        params['period_from'] = self.period_from
        params['period_to'] = self.period_to
        params['page_size'] = self.days * 48
        if debug_setting > 1 :
            print(params)
        response = requests.get(base_url + 'products/' + self.code + '/electricity-tariffs/' + tariff_code + '/standard-unit-rates/', auth=credentials, params=params)
        if response.status_code != 200 :
            print(f"** response code for {self.code} / {self.imp_code} from {response.url} was {response.status_code}")
            return None
        self.prices = {}
        for r in response.json().get('results') :
            s = r.get('valid_from')
            day = s[:10]
            hour = s[11:16].replace(':','')
            value = c_float(r.get('value_inc_vat'))
            if hour not in self.prices.keys() :
                self.prices[hour] = {}
            self.prices[hour][day] = value
        self.keys = sorted(self.prices)
        if len(self.keys) != 48 :
            return
        self.averages = {}
        self.avg = []
        self.min = []
        self.max = []
        for t in self.keys :
            l = [v for v in self.prices[t].values()]
            self.averages[t] = sum(l) / len(l)
            self.avg.append(self.averages[t])
            self.min.append(min(l))
            self.max.append(max(l))
        self.period_avg = {}
        self.per = []
        self.tracked = tracked
        for p in self.tracked.keys() :
            v = [self.averages[k] for k in time_list(p)[:-1]]
            self.period_avg[p] = sum(v) / len(v)
        return

    def plot_30_minute_prices(self, period_to = None) :
        global page_width, figure_width
        if len(self.keys) != 48 :
            print(f"** no 30 minute pricing for {self.full_name} ({self.code})")
            return
        plt.figure(figsize=(figure_width, figure_width/3))
        plt.plot(self.keys, self.avg, color='black', linestyle='solid', label='30 minute average', linewidth=2)
        plt.plot(self.keys, self.min, color='blue', linestyle='dashed', label='30 minute min', linewidth=0.8)
        plt.plot(self.keys, self.max, color='red', linestyle='dashed', label='30 minute max', linewidth=0.8)
        for p in self.tracked.keys() :
            times = time_list(p)
            values = [self.period_avg[p] for t in times]
            plt.plot(times, values, color=self.tracked[p]['color'], linestyle='dotted', label=self.tracked[p]['label'], linewidth=3)
            plt.axvspan(times[0], times[-1], label=self.tracked[p]['label'], color=self.tracked[p]['color'], alpha=0.07)
        plt.title(f"Average daily pricing (p/kwh inc VAT) for {self.full_name} ({self.code}) over {self.days} days from {self.period_from.date()}", fontsize=16)
        plt.grid(axis='x', which='major', linewidth=0.8)
        plt.grid(axis='y', which='major', linewidth=0.8)
        plt.grid(axis='y',which='minor', linewidth=0.4)
        plt.minorticks_on()
        plt.legend(fontsize=14)
        plt.xticks(rotation=45)
        print()
        plt.show()
        return


##################################################################################################
# Solar forecast using solcast.com.au
##################################################################################################

# solcast settings
solcast_url = 'https://api.solcast.com.au/'
solcast_credentials = None
solcast_rids = []
solcast_save = None

def solcast_setting(api_key = None, url = None, rids = None, save = None) :
    """
    Load account settings to use
    """ 
    global debug_setting, solcast_url, solcast_credentials, solcast_rids, solcast_save
    if api_key is not None :
        solcast_credentials = HTTPBasicAuth(api_key, '')
        if debug_setting > 0 :
            print(f"Solcast credentials provided")
    if url is not None :
        solcast_url = url
        if debug_setting > 1 :
            print(f"Solcast url: {solcast_url}")
    if rids is not None :
        solcast_rids = rids
        if debug_setting > 1 :
            print(f"Solcast resource ids: {solcast_rids}")
    if save is not None :
        solcast_save = save
    return

class Forecast :
    """
    Load Forecast daily yield
    """ 

    def __init__(self, days=14, period='PT30M', threshold=10, reload=0) :
        global debug_setting, solcast_url, solcast_credentials, solcast_rids, solcast_save
        if days > 14 :
            print(f"** maximum number of days exceeded")
            days = 14
        self.threshold = threshold
        if reload == 1 and os.path.exists(solcast_save):
            os.remove(solcast_save)
        if solcast_save is not None and os.path.exists(solcast_save):
            f = open(solcast_save)
            self.forecasts = json.load(f)
            f.close()
        else :
            self.forecasts = {}
            for rid in solcast_rids :
                params = {'period' : period, 'format' : 'json', 'hours' : days * 24}
                response = requests.get(solcast_url + 'rooftop_sites/' + rid + '/forecasts', auth = solcast_credentials, params = params)
                if response.status_code != 200 :
                    print(f"** response code getting product details for {rid} from {response.url} was {response.status_code}")
                    return
                self.forecasts[rid] = response.json().get('forecasts')
            if solcast_save is not None :
                f = open(solcast_save, 'w')
                json.dump(self.forecasts, f, sort_keys = True, indent=4, ensure_ascii= False)
                f.close()
        self.estimate = {}
        self.days = 0
        for k in self.forecasts.keys() :
            for f in self.forecasts[k] :
                date = f.get('period_end')[:10]
                if date not in self.estimate.keys() :
                    self.estimate[date] = 0.0
                    self.days += 1
                self.estimate[date] += c_float(f.get('pv_estimate')/2)      # 30 minute yield / 2 = kwh...
        self.keys = sorted(self.estimate.keys())[1:]
        self.values = [self.estimate[k] for k in self.keys]
        self.total = sum(self.values)
        if len(self.keys) >0 :
            self.avg = self.total / len(self.values)
        self.days -= 1
        return

    def __str__(self) :
        s = f'\nSolcast yield forecast for next {self.days} days:\n\n'
        for k in self.keys :
            y = self.estimate[k]
            d = datetime.datetime.strptime(k, '%Y-%m-%d').strftime('%A')[:3]
            s += f"    {k[5:]} {d} : {y:5.2f} kwh\n"
        return s[:-1]

    def plot_estimate(self) :
        if not hasattr(self, 'estimate') :
            print(f"** no estimate available")
            return
        x = [f"{k[5:]} {datetime.datetime.strptime(k, '%Y-%m-%d').strftime('%A')[:3]}" for k in self.keys]
        y = [self.estimate[k] for k in self.keys]
        figwidth = 12 * self.days / 7
        self.figsize = (figwidth, figwidth/3)     # size of charts
        plt.figure(figsize=self.figsize)
        alpha=0.07       # background transparency
        plt.plot(x, self.values, color='green', linestyle='solid', label='daily estimate', linewidth=2)
        if hasattr(self, 'avg') :
            plt.axhline(self.avg, color='blue', linestyle='solid', label=f'average {self.avg:.1f} kwh / day', linewidth=2)
        plt.axhspan(0, self.threshold, color='red', alpha=0.1, label='threshold')
        plt.title(f"Solcast yield forecast for next {self.days} days (total yield = {self.total:.0f} kwh)", fontsize=16)
        plt.grid()
        plt.legend(fontsize=14)
        plt.xticks(rotation=45, ha='right')
        print()
        plt.show()
        return