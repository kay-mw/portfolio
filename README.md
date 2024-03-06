# Projects

## Project 1: Anilist Popularity Project

### Project Overview

[AniList](https://anilist.co) is a website that allows users to catalogue, score, and discuss the anime they have watched. The website is run using the [AniList GraphQL API](https://anilist.gitbook.io/anilist-apiv2-docs/), which is publicly available for use. As a user of AniList myself, I wanted to see if I could use this API to extract unique user insights. I wanted to create an ETL pipeline that could calculate a users most "popular" and "unpopular" anime take, and display the results to them on a basic web interface. This approach was inspired by [Obscurify](https://www.obscurifymusic.com), a website that uses the Spotify API to identify how popular your music taste is based on the obscurity of songs you listen to. 

#### Basic Outline

1. Create a python script that could extract user anime data as well as the site-wide data for those anime from the Anilist API.
2. Transform this data into a usable format and perform basic analysis to identify the users most "popular" and "unpoplular" anime opinions.
3. Upload the data to a cloud SQL database (in this case, Azure).
4. Create a basic web interface to facilitate this pipeline, including a page where users could enter their ID, and a dashboard page that displays their results.

### Step 1: Extract

As is the case with most data engineering projects, the first step is to figure out how to extract the data you need. Prior to this project I had never worked with a GraphQL API before, so the first step was understanding the basics of GraphQL queries, namely the syntax, variables, and navigating the JSON structure. The AniList API [documentation](https://anilist.gitbook.io/anilist-apiv2-docs/overview/graphql/getting-started) was very helpful in this regard.

I then constructed my first GraphQL query (see below). 

```anilist_popularity_project/user_query.gql
```

Initially, I pasted the entire query into my python script.

## Project 2: The Impact of Winner and Loser Effects on eSports Competitions (Dissertation)

### Introduction

This project investigated the winner and loser effect, which refers to the phenomenon wherein winners and more likely to win and losers more likely to lose, even when confronted with new opponents. Prior investigations have explored this phenomenon in animals (Franz et al., 2015) and traditional sports like tennis (Page & Coates, 2017), however there exists no extant literature scrutinizing this phenomenon within the realm of eSports. This project endeavors to bridge this gap by examining the presence of and factors affecting the winner/loser effect in eSports competitions.

### Problem Statement

- Does the winner/loser effect persist in a largely psychological competitions like eSports?
- Could factors such as tournmanet prize money, tournament tier and bracket stage mediate the effect of wins and losses on performance?

### Data Sourcing

After defining the problems mentioned above, I searched for an API that would contain the relevant data. I used an API called Pandascore, which allowed me to gather large amounts of eSports game data from multiple different videogame titles.

Using [this code](code/CSGO_API_request_final.py), the API returned 48459 rows and 134 columns.

### References

Franz, M., McLean, E., Tung, J., Altmann, J., & Alberts, S. C. (2015). Self-organizing dominance hierarchies in a wild primate population. Proceedings of the Royal Society B: Biological Sciences, 282(1814), 20151512. https://doi.org/10.1098/rspb.2015.1512

Page, L., & Coates, J. (2017). Winner and loser effects in human competitions. Evidence from equally matched tennis players. Evolution and Human Behavior, 38(4), 530-535. https://doi.org/10.1016/j.evolhumbehav.2017.02.003
