# XP2-member-networks
(Work in progress)

## Intro
Visualize networks of individuals and memberships on the XP2 core/ Data Explorer data warehouse using NetworkX.

Many-to-many relationships between individuals (people) and memberships (accounts) complicate the understanding of how credit union members are connected and related. For example, one individual can participate in multiple memberships, and a membership can have multiple individuals associated with it (primary/joint/beneficiary, etc). 

This script automates the discovery and visualization of these relationships. It outputs visualizations of groups meeting a threshold of nodes and returns summary statistics of that member subgraph. The sqlite database contains dummy data analogous to the tables required.

## Setup (for an intended audience of non-Python users)

#### 1. Download Python and install required packages
If you don't have Python installed already, Anaconda is a good option: https://docs.anaconda.com/anaconda/install/.  

The following packages are required in addition to the base Python installation: matplotlib, networkx, openpyxl, pandas, pyodbc. At the time of writing decorator version 4.4.2 is required due to a bug in version 5.

You have three options for installing: 

1) Manually install these via pip or Anaconda. See:  
Installing packages via conda cli: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html  
Managing environments in Anaconda: https://docs.anaconda.com/anaconda/navigator/getting-started/#navigator-managing-environments  
Installing packages via Anaconda GUI: https://docs.anaconda.com/anaconda/navigator/tutorials/manage-packages/

2) Use the environment.yml file to setup a virtual environment containg the base conda installation + required packages  
With Anaconda installed, navigate to ./XP2-member-networks via Anaconda prompt and run `conda env create -f environment.yml`  
See: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file

3) Use the requirements.txt file to install all at once using pip  
Navigate to ./XP2-member-networks and run `pip install -r requirements.txt`  

#### 2. Clone or download this repository  
Clone this repository using git, or download via the web and unzip (Click the green Code button > click "Download Zip").  
Before running, activate the virtual environment if necessary.

#### 3. Setting up the SQL server connection  
Before running, the name of your MSSQL server and datamart are required to connect. Windows authentication is the method for authentication (the only method supported at this time).  

Server details must be saved in the server_details.py file, located in XP2-member-networks/config. Open this file in a text editor of your choice, and replace the 'xxxx' in the code with relevant names. For example, if your sever is called "cool-server" and your database is "cool-datamart", the server_details.py should contain:
```
MSSQL_server_name = 'cool-server'
datamart_name = 'cool-datamart'
```
**NOTE:** A dummy sqlite database is included for testing without the need to connect to your datawarehouse. No setup is required to use this dataset unless the location of the sqlite file has been changed. If the location changed, you can set the filepath to the new location in this same file.  Example: `sqlite_location = 'C:\\Users\\Username\\new directory\\demo_data.db'`

#### 4. Optional: changing the output folder location and file prefixes  
By default, when the script runs it will output results to xp2-member-networks/output. If you wish to change this, you can specify a new filepath in output_location.py within the config folder. It should accept relative paths or absolute paths but take care to use 

## Running the program  
App.py is the entry point. Using terminal or the Anaconda prompt, navigate to ./XP2-member-networks and run `app.py` to run the program with a GUI. To enter the CLI instead, run `app.py cli`.  
Both the CLI and GUI should be pretty self explanatory. Please pay attention to the terminal when running the GUI, as status messages and errors will be displayed here.  

## Managing the output files (important!)  
The user is responsible for archiving and organizing the output. By default, the program will *not* delete any files in the output folder from the last time it was run, but *will* overwrite any old files with the same name. This will primarily affect the PDFs unless it is run multiple times within the same day, in which case the tables and gephx files will also be overwritten. The easiest way to archive/retain the output is to cut/paste the entire folder somewhere else, or simply rename it. When the program runs it will re-create the output folder if it doesn't exist, so there is no risk to deleting or renaming it.  

If you don't wish to retain any historical output files, it is recommended to delete the output folder before re-running the program. This will prevent old files from accumulating, particularly in the pdf folder.  

## What to do with the output  
#### Whats included?
The output will include:
* Member subgraphs.xlsx: This is a summary of all the networks of members identified. It contains a name and summaries of attributes, along with a link to the corresponding pdf (see below). Click the link to open the pdf and see the network visualization.
* Total membership graph. gephx: All membership data saved in a .gephx file. Open with a network analysis program such as Gephi, Cytoscape, etc. Can also be opened in Python/NetworkX.
* PDFs: For each connected component (subgraph) of the membership base, a pdf is generated which contains a visualization and attribute summary table.
* individual group.csv: Table containing the individual ID and group the individual is part of.
* member group.csv: Table containing member number and group a membership is part of 


