# Kiran Malhotra Portfolio

# [Popularity Tool for Anilist](https://github.com/kay-mw/anilist-popularity-project)

##### _Python_ | _Data Orchestration_ | _CI/CD_ | _Azure (SQL, Blob Storage)_ | _GCP (Cloud Run, Artifact Registry)_

## Motivation

- This project was borne out of a desire to see how much my anime taste differed
  compared to the average person.

  - To achieve this goal, I created a website where you could enter your AniList
    username to see how your taste compares to the site-wide average!

## Project Overview

![project workflow diagram](./media/pop_project_diagram.png)

- When a user enters their AniList username on the website, the backend extracts
  their public AniList data from the official API, cleans this data, and uploads
  it to the data lake (Azure Blob Storage).
- An automated pipeline then uploads these files (CSVs) to the data warehouse
  (Azure SQL) every 24 hours.
- At each step of the way, there were automated tests and/or deployments
  (CI/CD), whether that be data quality checks with Pytest/Great Expectations or
  Docker deployments to a VPS.
- You can try this project out for yourself using the <a
  href="https://pop-tool-anilist-ftybdinz2q-nw.a.run.app/" target="_blank">website</a>, or
  you can get a taste by looking at the example images below!

![taste message](./media/example_dash_msg.png)
![plot of user vs. average taste](./media/example_dash_plot.png)
![most and least popular take](./media/example_dash_anime.png)

# [The Impact of Winner and Loser Effects on eSports Competitions (Dissertation)](https://github.com/kay-mw/esports_wleffects)

## Project Overview

#### _Python_ | _R_

- Extracted 41,421 CS:GO matches from a REST API using Python.
- Restructed the data to represent 91,551 individual games instead of matches.
- Converted prize money amounts for over 40 different currencies using
  historical exchange rates.
- Analyzed data using a general linear mixed effects model, and visualised data
  using ggplot and SJPlot (see below).

![main winner/loser effect](./media/main_wl_effect.png)

![prize money winner/loser effect interaction](./media/wl_money_interaction.png)
