# Energy Analysis
This code downloads, analyses and displays product and price information from the Octopus Developer API. It uses Python for loading and analysis and Jupyter Lab for display. Jupyter Lab provides a flexible way for
users to build simple scripts to analyse data that is specific to them.

In addition, the code loads, aggregates and displays solar yield forcasts from http://solcast.com.ua

The core code is contained in 'energy.py' and an example Jupyter notebook is provided in 'energy.ipynb'. A file 'private.py' contains user keys and meter details and is not uploaded to the public github repository.
Instead, a template file 'template private.py' is provided that a user needs to edit to add their personal details and then rename to 'private.py'

The basis of the Octopus product analysis is a python class called Product. This requires an Octopus product code to select a specific product. Attempting to create a product with a blank code will return a list of
available product codes for you to select from. You only need to enter a partial code that is unique.

Once you have a valid product, you can report details of it simply by printing the product. You can also plot 30 minute prices (where available) using the method plot_30_minutes_prices.
