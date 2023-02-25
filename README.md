# Energy Analysis
This project provides code to download, analyse and display product and price information using the [Octopus Developer API](https://developer.octopus.energy/docs/api/).

In addition, the code loads, aggregates and displays solar yield forcasts from http://solcast.com.au

It uses Python for loading and analysis and Jupyter Lab for display. Jupyter Lab provides a flexible way for users to build simple scripts to analyse data that is specific to them.

The core code is contained in [energy.py](energy.py) and an example Jupyter notebook is provided in [energy.ipynb](energy.ipynb). Clicking [energy.ipynb](energy.ipynb) will display the last uploaded notebook so you can see what this looks like.

A file 'private.py' contains user keys and meter details and is not uploaded to the public github repository.
A template [template_private.py](template_private.py) is provided needs to be edited to add personal details and then renamed to 'private.py'

Octopus product analysis sits in a python class called Product. This takes an Octopus product code to select a product. Attempting to create a product with a blank code will get a list of
available product codes for you. You only need to enter a partial code that is unique for it to work, which helps if product codes are updated over time as the prefix tends to remain the same.

Once you find a valid product, you can report key details simply by printing the product. This will show standard pricing including VAT for Octopus import tariffs and also export pricing for outgoing products.

Where a product is agile and has 30 minute pricing available, you can call the method plot_30_minute_pricing() on the product. This will display a graph, averaged over a number of days, with the min,
max and average price for each 30 minute slot. You can also view 'tracked' periods of time: these will be highlighted in the plot and the average pricing for each period will be displayed.

The tracked periods are named. The following are configured by default:

* night  : night off peak period, typically 1.30am to 5am
* am     : morning peak periods, typically 6.30am to 10.30am
* pm     : afternoon off peak period, typically 12.30pm to 4pm
* peak   : evening peak period, typically 4pm to 8pm

You can adjust the time periods using the method period_setting as shown in the example ipynb, using 24 hour / time notation. Please note that a period cannot run through midnight e.g. 2330 to 0130

