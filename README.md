# Kiran Malhotra Portfolio

# Project 1: Anilist Popularity Project

[REPO](https://github.com/kay-mw/anilist-popularity-project)

## Project Overview

#### _Python_ | _SQL_ | _Azure_ | _Terraform_

- Created a Python script that extracts user and site-wide anime data from the AniList GraphQL API.
- Transformed this data using Pandas into a usable format and performed basic analysis to identify the user's most "popular" and "unpopular" anime opinions.
- Incorporated data quality checks with Great Expectations.
- Uploaded this data to an Azure SQL Database using SQLAlchemy. Selected a `MERGE` function to `INSERT` new records and `UPDATE` existing records.
- Created a basic web interface using Flask and Jinja2 to facilitate this pipeline. Included a page where users could enter their ID, and a dashboard page that displays their results (see below).

![example_1](./images/firefox_4DIEhq58Ry.png)
![example_2](./images/g7GNO07zZA.png)

# Project 2: The Impact of Winner and Loser Effects on eSports Competitions (Dissertation)

[REPO](https://github.com/kay-mw/esports_wleffects)

## Project Overview

#### _Python_ | _R_  

- Extracted esports data from a REST API using Python.
- Transformed the data extensively, which included the integration and transformation of multiple other datasets (exchange rates, GDP per capita).
- Analyzed data using a general linear mixed effects model (see results below).

![main winner/loser effect](./images/main_wl_effect.png)

![prize money winner/loser effect interaction](./images/wl_money_interaction.png)
