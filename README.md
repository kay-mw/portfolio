# Data Projects

## Project 1: Dissertation - The Impact of Winner and Loser Effects on eSports Competitions

### Introduction

This project investigated the winner and loser effect, which refers to the phenomenon wherein winners and more likely to win and losers more likely to lose, even when confronted with new opponents. Prior investigations have explored this phenomenon in animals (Franz et al., 2015) and traditional sports like tennis (Page & Coates, 2017), however there exists no extant literature scrutinizing this phenomenon within the realm of eSports. This project endeavors to bridge this gap by examining the presence of and factors affecting the winner/loser effect in eSports competitions.

### Problem Statement

- Does the winner/loser effect persist in a largely psychological competition like eSports?
- Could factors such as tournmanet prize money, tournament tier and bracket stage mediate the effect of wins and losses on performance?

### Data Sourcing

After defining the goals mentioned above, I searched for an API that would contain the relevant data. I used an API called Pandascore, which allowed me to gather large amoubnts of past eSports game data for multiple different videogame titles.

Using [this code](code/CSGO_API_request_final.py), the API returned 48459 rows and 134 columns.

### References

Franz, M., McLean, E., Tung, J., Altmann, J., & Alberts, S. C. (2015). Self-organizing dominance hierarchies in a wild primate population. Proceedings of the Royal Society B: Biological Sciences, 282(1814), 20151512. https://doi.org/10.1098/rspb.2015.1512
Page, L., & Coates, J. (2017). Winner and loser effects in human competitions. Evidence from equally matched tennis players. Evolution and Human Behavior, 38(4), 530-535. https://doi.org/10.1016/j.evolhumbehav.2017.02.003
