# Energy Analysis
This code downloads, analyses and displays product and price information from the Octopus Developer API. It uses Python for loading and analysis and Jupyter Lab for display. Jupyter Lab provides a flexible way for
users to build simple scripts to analyse data that is specific to them.

In addition, the code loads, aggregates and displays solar yield forcasts from http://solcast.com.au

The core code is contained in 'energy.py' and an example Jupyter notebook is provided in 'energy.ipynb'. Clicking [energy.ipynb](energy.ipynb) will display the last uploaded notebook so you can see what this looks like.

A file 'private.py' contains user keys and meter details and is not uploaded to the public github repository.
Instead, a template file ['template private.py] is provided that a user needs to edit to add their personal details and then rename to 'private.py'

Octopus product analysis uses a python class called Product. This takes an Octopus product code to select a product. Attempting to create a product with a blank code will get a list of
available product codes for you. You only need to enter a partial code that is unique for it to work, which helps if product codes are updated over time as the prefix tends to remain the same.

Once you find a valid product, you can report key details by printing the product. This will show standard pricing including VAT for Octopus import tariffs and also export pricing for outgoing products.

Where product as agile and have 30 minute pricing, you can call the method plot_30_minute_pricing() on the product. This will display a graph, averaged over a number of days, with the min, max and average price for
each 30 minute slot. You can also define 'tracked' periods of time and these will be highlighted and the average pricing for that period will be displayed. The default tracked periods are:

* 'night': night off peak time period, typically 1am to 4am
* 'am' : morning peak time periods, typically 6am to 10am
* 'pm' : afternoon off peak time period, typically 1pm to 3pm
* 'peak' : evening peak time period, typically 4pm to 8pm

You can adjust the time periods using the method period_setting as shown in the example ipynb.


