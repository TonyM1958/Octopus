##################################################################################################
"""
Module:   Private data
Date:     23 February 2023
"""
##################################################################################################
# this is a template for the code used to store your private data. Copy this file, add the details
# and rename the file to 'private.py' so the details can be imported. 'private.py' should be
# configured so it is ignored by github to stop your private data being published. 
##################################################################################################

from energy import Meter

# private data
octopus_api_key = 'sk_live_****'                                                    # your API key copied from your Octopus account developer settings
imp_meter = Meter(mpan = '**mpan**', ser = '**serial number**')                     # the MPAN and serial number of your import meter
exp_meter = Meter(mpan = '**mpan**', ser = '**serial number**', export = True)      # the MPAN and serial number for export meter (serial may be same import and export, but MPAN is different)
gas_meter = Meter(mprn = '**mprn**', ser = '**serial number**')                     # the MPRN and serial number for your gas meter               
