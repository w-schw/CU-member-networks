# XP2-member-networks
(Work in progress)

## Intro
Visualize networks of individuals and memberships on the XP2 core/ Data Explorer data warehouse using NetworkX.

Many-to-many relationships between individuals (people) and memberships (accounts) complicate the understanding of how credit union members are connected and related. For example, one individual can participate in multiple memberships, and a membership can have multiple individuals associated with it (primary/joint/beneficiary, etc). 

This script automates the discovery and visualization of these relationships. It outputs visualizations of groups meeting a threshold of nodes and returns summary statistics of that member subgraph. The sqlite database contains dummy data analogous to the tables required.

