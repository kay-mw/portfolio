# Kiran Malhotra Portfolio

# Project 1: Anilist Popularity Project

[REPO](https://github.com/kay-mw/anilist-popularity-project)

## Project Overview

[AniList](https://anilist.co) is a website that allows users to catalog, score, and discuss the anime they have watched. The website is run using the [AniList GraphQL API](https://anilist.gitbook.io/anilist-apiv2-docs/), which is publicly available for use. As an AniList user myself, I wanted to see if I could use this API to extract unique user insights. The goal was to create an ETL (Extract, Transform, Load) pipeline that could calculate a user's most "popular" and "unpopular" anime takes, and display the results to them on a basic web interface. This approach was inspired by [Obscurify](https://www.obscurifymusic.com), a website that uses the Spotify API to identify how popular your music taste is based on the obscurity of the songs you listen to.

### Basic Outline

1. Create a Python script that could extract user anime data and site-wide data for those anime from the AniList API.
2. Transform this data into a usable format and perform basic analysis to identify the user's most "popular" and "unpopular" anime opinions.
3. Upload the data to a cloud SQL database (in this case, Azure).
4. Create a basic web interface to facilitate this pipeline, including a page where users could enter their ID, and a dashboard page that displays their results.

## Step 1: Extract

The first step was to figure out how to extract the required data. Prior to this project, I had never worked with a GraphQL API before, so the first step was understanding the basics of GraphQL queries, namely the syntax, variables, and navigating the JSON structure. The AniList API [documentation](https://anilist.gitbook.io/anilist-apiv2-docs/overview/graphql/getting-started) was very helpful in this regard.

I then constructed my first GraphQL (GQL) query:
```
query ($page: Int, $id: Int!) {
  Page (page: $page) {
    pageInfo {
      total
      currentPage
      lastPage
      hasNextPage
      perPage
    }
    users (id: $id) {
      id
      name
      statistics {
        anime {
          scores {
            mediaIds
            score
          }
        }
      }
    }
  }
}
```
This would successfully retrieve the ID and score of each anime on a user's profile. Initially, I pasted these queries in full into my Python file, but I later set up a basic function that would load the queries so I could store them as separate .gql files.
```
def load_query(file_name):
    file_path = os.path.join("./", file_name)
    with open(file_path, "r") as file:
        return file.read()
```
I also created a function to perform API calls so that I wouldn't have to repeat the request code each time.
```
def fetch_anilist_data(query, variables):
    try:
        response = requests.post(url, json={'query': query, 'variables': variables}, timeout=10)
        response.raise_for_status()
        global response_header
        response_header = response.headers['Date']
        response_header = pd.Series(response_header)
        return response.json()
    except requests.exceptions.Timeout:
        print("Request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error in request: {e}")
        return None
```
This was simple enough to extract user data, but as anime data contained more information per page, I would need to utilize pagination with a basic while loop.
```
while True:
    response_ids = fetch_anilist_data(query_anime, variables_anime)
    print("Fetching anime info...")
    time.sleep(5)

    page_df = pd.json_normalize(response_ids, record_path=['data', 'Page', 'media'])
    anime_info = pd.concat([anime_info, page_df], ignore_index=True)

    if not response_ids['data']['Page']['pageInfo']['hasNextPage']:
        break

    variables_anime['page'] += 1
```
Importantly, by creating a list of anime IDs from the original user query and setting that as a variable, I would extract only the anime I needed for that user.
```
id_list = user_score['anime_id'].values.tolist()

variables_anime = {
    "page": 1,
    "id_in": id_list
}
```
With this, I had extracted all the data I needed - now I had to make the response usable.

## Step 2: Transform

Upon constructing the necessary GQL queries, I proceeded to extract the relevant information from the JSON response. To extract the data from JSON and put it in a data frame, I used `pd.json_normalize`. I then performed any additional transformations depending on the output format. For user data, I had to pivot the data from wide to long using `pd.explode`. I also renamed all the columns to maintain a consistent naming template.

## Step 3: Load

### Terraform Deployment

As I had never used the Azure Cloud Platform before, I wanted to try it out for this project. After initializing my credentials using the Azure CLI, I set up the infrastructure using Terraform.
```
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>2.0"
    }
  }
}

provider "azurerm" {
  features {}

  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "project-grp" {
  name     = "kiran-projects-grp"
  location = "West Europe"
}

resource "azurerm_storage_account" "anilistproject" {
  name                     = "anilistproject"
  resource_group_name      = azurerm_resource_group.project-grp.name
  location                 = azurerm_resource_group.project-grp.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_mssql_server" "anilist-sqlserver" {
  name                         = "anilist-sqlserver"
  resource_group_name          = azurerm_resource_group.project-grp.name
  location                     = azurerm_resource_group.project-grp.location
  version                      = "12.0"
  administrator_login          = var.administrator_login
  administrator_login_password = var.administrator_login_password
}

resource "azurerm_mssql_database" "anilist-db" {
  name           = "anilist-db"
  server_id      = azurerm_mssql_server.anilist-sqlserver.id
  max_size_gb    = 4
}
```
This made setting everything up super easy.

### Data Warehouse Model

I then spent some time trying to figure out the data warehouse structure I wanted to use. I eventually decided upon creating three separate tables: one containing the user's individual score data ("user_score"), one containing site-wide anime data ("anime_info"), and another containing user/request data ("user_info").

I chose this structure because it allows for clear identification of keys. anime_id is the primary key in "anime_info", user_id is the primary key in "user_info", and these then act as foreign keys to access the data in "user_score". I felt this made the relationships between the tables clear and intuitive, and made it simple to use joins if you wanted to access all of the data with one query. 

### Data Upload

I attempted a few different methods of uploading data. I found the built-in `df.to_sql` function limiting for my use case, as I wanted to replace existing data as well as append new data, which was difficult with pandas functionality. I eventually decided upon using SQLAlchemy to create a temporary table, which would then be used as a source to perform a merge on the existing data.
```
server = "anilist-sqlserver.database.windows.net"
database = "anilist-db"
connection_string = os.getenv('AZURE_ODBC')

params = quote_plus(connection_string)
connection_url = f"mssql+pyodbc:///?odbc_connect={params}"
engine = create_engine(connection_url)

session = sessionmaker(bind=engine)

def upload_table(primary_key, table_name, df, column_1, column_2):
    with engine.connect() as connection:
        print(f"Uploading {table_name} to Azure SQL Database...")

        df.to_sql("temp_table", con=connection, if_exists="replace")

        query = (f"MERGE {table_name} AS target USING temp_table AS source "
                    f"ON source.{primary_key} = target.{primary_key} "
                    f"WHEN NOT MATCHED BY target THEN INSERT ({primary_key}, {column_1}, {column_2}) "
                    f"VALUES (source.{primary_key}, source.{column_1}, source.{column_2}) "
                    f"WHEN MATCHED THEN UPDATE "
                    f"SET target.{primary_key} = source.{primary_key}, "
                    f"target.{column_1} = source.{column_1}, "
                    f"target.{column_2} = source.{column_2};")
        print(query)
        connection.execute(text(query))
        connection.commit()

upload_table("anime_id", "anime_info", anime_info, "average_score", "title_romaji")
upload_table("anime_id", "user_score", user_score, "user_id", "user_score")
upload_table("user_id", "user_info", user_info, "user_name", "request_date")
```
This worked well - it allowed me to replace existing data to keep entries up-to-date, while appending any new data. This enabled the system to keep all the information as current as possible, while allowing new users or profile updates to be appended to the table.

## Step 4: Web App

With this, the data engineering side of this project was essentially finished! Now I wanted to create a basic web interface, both for fun and to make this project feel more complete.

### Flask + Jinja2

I set up a basic HTML website and Flask backend that allowed a user to enter their AniList ID, stored the POST request, and then sent this as an argument to the API request Python module (which I had to wrap inside the `fetch_data(anilist_id)` function).
```
app = Flask(__name__)

anilist_fetcher = None


def process_data(anilist_id):
    global anilist_fetcher
    anilist_fetcher = FetchAnimeDataByUser(anilist_id)
    anilist_fetcher.fetch_data()


@app.route('/', methods=['GET', 'POST'])
def anilist():
    if request.method == 'POST':
        anilist_id = request.form.get('anilist_id')
        process_data(anilist_id)
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
    return render_template(
        'dashboard.html',
        image1=anilist_fetcher.cover_image_1,
        image2=anilist_fetcher.cover_image_2,
        u_score_max=anilist_fetcher.score_max,
        u_score_min=anilist_fetcher.score_min,
        avg_score_max=anilist_fetcher.avg_max,
        avg_score_min=anilist_fetcher.avg_min,
        title_max=anilist_fetcher.title_max,
        title_min=anilist_fetcher.title_min
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
```
I also used Jinja2 to insert variables from the API request file into the HTML file, which was primarily used to dynamically display the user's results.
```
<div class="image-wrapper">
    <h2>Your Most Unpopular Take</h2>
    <img class="box" src="{{ image1 }}" alt="unpopular anime cover image">
    <h3 class="caption">{{ title_max }}</h3>
    <p style="text-align: left">
        Your Score: {{ u_score_max }}
        <br>
        Average Score: {{ avg_score_max }}
    </p>
</div>
<div class="image-wrapper">
    <h2>Your Most Popular Take</h2>
    <img class="box" src="{{ image2 }}" alt="popular anime cover image">
    <h3 class="caption">{{ title_min }}</h3>
    <p style="text-align: left">
        Your Score: {{ u_score_min }}
        <br>
        Average Score: {{ avg_score_min }}
    </p>
</div>
```
Thanks to PicoCSS for styling, I think the website ended up looking pretty decent for my first-ever website. Okay, at least the home page, maybe not the dashboard...

![home page](./images/firefox_4DIEhq58Ry.png)

![dashboard](./images/g7GNO07zZA.png)

### Conclusion

With this, the project was complete! I had a lot of fun making it, and I may continue working on it since it has even more potential. It would be great if I could get it to the same level as Obscurify one day.

Thank you for reading, and feel free to try the pipeline out yourself!

# Project 2: The Impact of Winner and Loser Effects on eSports Competitions (Dissertation)

[REPO](https://github.com/kay-mw/esports_wleffects)

## Project Overview

This project was an analytical investigation into the winner and loser effect, a phenomenon where winning a previous competition appears to, in of itself, increase the likelihood of winning the current competition. The focus was on esport competitions, specifically the first person shooter (FPS) Counter:Strike Global Offensive (CS:GO). This was a novel approach given that most existing literature on winner/loser effects investigated animals or humans in physical competitions (judo, tennis). Though the project was more data analysis-focused, it followed a general ETL (Extract, Transform, Load) structure similar to a data engineering context. The goal was to create a batch pipeline using an orchestration tool that automates the API requests at regular intervals.

I collaborated with my dissertation supervisor, who contributed significantly to the complex code for data analysis (e.g., calculating previous outcomes for each team). My primary responsibilities were data extraction and transformation.

### Basic Outline

- Extract esports data from an API.
- Transform the data into a usable format for analysis.
- Use a general linear mixed effects model to see if, when controlling for team skill, winning/losing the previous game significantly predicts the outcome of the current game.

## Step 1: Extract

First, I searched for an API that would contain the relevant data. I used an API called [Pandascore](https://pandascore.co/), which allowed me to gather large amounts of esports game data for CS:GO.
```
import requests
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

headers = {
    "accept": "application/json",
    "authorization": f"Bearer {os.environ['API_KEY']}"
}

response = []
for page in range(1,2):
    url = "https://api.pandascore.co/csgo/matches/past?per_page=100&filter%5Bstatus%5D=finished&page="+str(page)
    page_response = requests.get(url, headers=headers).json()
    response.extend(page_response)

for item in response:
    for game_number,game in enumerate(item['games']):
        item['game_'+str(game_number)]=game
    for opponent_number,opponent in enumerate(item['opponents']):
        item['opponent_'+str(opponent_number)]=opponent['opponent']
    for result_number,result in enumerate(item['results']):
        item['result_'+str(result_number)]=result


df = pd.json_normalize(response)
df.drop(columns=['opponents','modified_at','slug','streams_list','live.opens_at','live.supported','live.url',
                 'videogame_title.slug','videogame.slug','winner.image_url','winner.modified_at','winner.slug',
                 'serie.modified_at','serie.slug','tournament.detailed_stats','tournament.live_supported',
                 'tournament.modified_at','tournament.slug','league.image_url','league.modified_at','league.slug',
                 'league.url','detailed_stats','opponent_0.image_url','opponent_0.modified_at','opponent_0.slug',
                 'opponent_1.image_url','opponent_1.modified_at','opponent_1.slug','games','results','game_0.complete',
                 'game_0.detailed_stats','game_0.finished','game_0.id','game_0.match_id','game_0.position',
                 'game_0.winner.type','game_0.winner_type','game_1.complete','game_1.detailed_stats','game_1.finished',
                 'game_1.id','game_1.match_id','game_1.position','game_1.winner.type','game_1.winner_type',
                 'game_2.complete','game_2.detailed_stats','game_2.finished','game_2.id','game_2.match_id',
                 'game_2.position','game_2.winner.type','game_2.winner_type','game_3.complete','game_3.detailed_stats',
                 'game_3.finished','game_3.id','game_3.match_id','game_3.position','game_3.winner.type',
                 'game_3.winner_type','game_4.complete','game_4.detailed_stats','game_4.finished','game_4.id',
                 'game_4.match_id','game_4.position','game_4.winner.type','game_4.winner_type'],inplace=True)
df.style

print(df)

df.to_csv('csgo_data_game_filtered.csv')
```
This returned a dataset containing 49,421 CS:GO matches from January 2016 to October 2023. This was the bulk of the data extraction work done, though the processing/transformation stage would require two more datasets.

## Step 2: Transform

### Exchange Rates

The first additional dataset needed was a historical exchange rates dataset, to tackle the issue of the CS:GO dataset having prize money amounts in over 30 different currencies. I decided on a dataset from the Bank for International Settlements (BIS) called "bilateral exchange rates," which contained conversion rates for hundreds of different currencies across a broad range of dates, all relative to the United States Dollar (USD). 

First, I converted all the currency names in the esports dataset into their relevant currency codes. The currency codes could then act as the key to connect the two datasets.
```
# separate prize pool amount and currency
esport.data <- separate(esport.data, tournament.prizepool, into = c(
  "tournament.prizepool.amount", "tournament.prizepool.currency"
  ), sep = "\\s", extra = "merge")

# convert prize pool amount column to int datatype
esport.data <- esport.data %>% mutate(across(tournament.prizepool.amount, as.integer))

# identify if separation worked as intended
unique(esport.data$tournament.prizepool.currency)

# saw that some values of United States Dollar had extra white space, so trim is necessary
esport.data$tournament.prizepool.currency <- trimws(esport.data$tournament.prizepool.currency)

# convert currency string to relevant abbreviation
esport.data <- esport.data %>%
  mutate(tournament.prizepool.currencycode = case_when(
    tournament.prizepool.currency == "United States Dollar" ~ "USD",
    tournament.prizepool.currency == "Chinese Yuan" ~ "CNY",
    tournament.prizepool.currency == "Euro" ~ "EUR",
    tournament.prizepool.currency == "Brazilian Real" ~ "BRL",
    tournament.prizepool.currency == "Polish Zloty" ~ "PLN",
    tournament.prizepool.currency == "Indian Rupee" ~ "INR",
    tournament.prizepool.currency == "Swedish Krona" ~ "SEK",
    tournament.prizepool.currency == "British Pound"  ~ "GBP",
    tournament.prizepool.currency == "Kazakhstani Tenge" ~ "KZT",
    tournament.prizepool.currency == "Russian Ruble" ~ "RUB",
    tournament.prizepool.currency == "Argentine Peso" ~ "ARS",
    tournament.prizepool.currency == "Norwegian Krone" ~ "NOK",
    tournament.prizepool.currency == "Danish Krone" ~ "DKK",
    tournament.prizepool.currency == "Czech Koruna" ~ "CZK",
    tournament.prizepool.currency == "Australian Dollar" ~ "AUD",
    tournament.prizepool.currency == "Swiss Franc" ~ "CHF",
    tournament.prizepool.currency == "Turkish Lira" ~ "TRY",
    tournament.prizepool.currency == "Japanese Yen" ~ "JPY",
    tournament.prizepool.currency == "Croatian Kuna"  ~ "HRK",
    tournament.prizepool.currency == "Vietnamese Dong" ~ "VND",
    tournament.prizepool.currency == "Icelandic Krona" ~ "ISK",
    tournament.prizepool.currency == "Qatari Riyal" ~ "QAR",
    tournament.prizepool.currency == "Mongolian Togrog" ~ "MNT",
    tournament.prizepool.currency == "Ukrainian Hryvnia" ~ "UAH",
    tournament.prizepool.currency == "Iranian Rial" ~ "IRR",
    tournament.prizepool.currency == "South African Rand" ~ "ZAR",
    tournament.prizepool.currency == "Serbian Dinar" ~ "RSD",
    tournament.prizepool.currency == "Bulgarian Lev" ~ "BGN",
    TRUE ~ tournament.prizepool.currency # Keep original value if no match.
  )
)
```
Next, I dealt with the historical exchange rates dataset, which needed to be reduced as its large size (407MB) slowed down transformations considerably. I removed all unnecessary currencies and standardized the dates to a consistent format using anytime(). Then, my supervisor used lubridate to remove all conversion rates from years outside our dataset (<2015).
```
# Separate currency abbreviaton from full name
historical_exchange_rates <- separate(historical_exchange_rates, "CURRENCY:Currency", 
into = c("currency_code", "currency_name"), sep = ":", extra = "merge")

# Check if all currencies are supported. All are except Croatian Kuna.
unique(historical_exchange_rates$currency_code)

# This isn't really a huge deal though because only two rows contain prize money in Croatian Kuna.
length(which(esport.data$tournament.prizepool.currencycode == "HRK"))

# Remove HRK (Croatian Kuna) from esport.data as there is no conversion data for it
esport.data <- esport.data %>%
  filter(!(tournament.prizepool.currencycode == "HRK" & !is.na(tournament.prizepool.amount)))

# Create a list of currency codes in esport.data
valid_currency_codes <- c("USD", "CNY", "EUR", "BRL", "PLN", "INR", "SEK", "GBP", 
                          "KZT", "RUB", "ARS", "NOK", "DKK", "CZK", "AUD", "CHF", 
                          "TRY", "JPY", "HRK", "VND", "ISK", "QAR", "MNT", "UAH", 
                          "IRR", "ZAR", "RSD", "BGN")

# Filter historical_exchange_rates to keep only rows with currencies in this list
filtered_exchange_rates <- historical_exchange_rates %>%
  filter(currency_code %in% valid_currency_codes)

# Convert the "begin_date" column to a Date object in esport.data
esport.data$begin_date <- as.Date(esport.data$begin_date)

# As date column in exchange rates dataset has inconsistent dates, use function to standardise format
filtered_exchange_rates$consistent_date <- as.Date(anytime(filtered_exchange_rates$`TIME_PERIOD:Time period or range`))
filtered_exchange_rates <- subset(filtered_exchange_rates,lubridate::year(consistent_date)>2015)
```
We then created a new dataset with only the necessary columns and merged it with the esports dataset to perform the conversion. The neatest part was the closest() argument in the merge function, which used the esport match date to get the closest available exchange rate for that date. This ensured the conversions were as accurate to the match time as possible.
```
# extract relevant columns
exchange <- filtered_exchange_rates[c("currency_code","OBS_VALUE:Observation Value","consistent_date")]
exchange <- exchange %>% rename(ObsValue=`OBS_VALUE:Observation Value`)
exchange$ObsValue <- ifelse(exchange$ObsValue=="NaN",NA,exchange$ObsValue)
exchange <- exchange %>% distinct(currency_code, consistent_date, .keep_all = TRUE)

merged_data <- esport.data %>%
  left_join(exchange, join_by("tournament.prizepool.currencycode" == "currency_code", closest(begin_date <= consistent_date)))

# Make a column based on date diff calculation
merged_data$date_diff <- difftime(merged_data$begin_date, merged_data$consistent_date, units = "days")

# Check it worked properly, seems like it worked perfectly (max is 0 days, min is -25 days)
max(na.omit(merged_data$date_diff))
min(na.omit(merged_data$date_diff))

# Convert prizepool amounts to USD using the exchange rates
merged_data <- mutate(merged_data, prizepool_usd = tournament.prizepool.amount / ObsValue)
```
### GDP Per Capita

Another consideration for tournament prize money was regarding GDP. CS:GO is massive on a global scale, with teams from all over the world competing in esports, and there are large disparities in economic standing between countries that might impact how they perceive a given amount of prize money. Getting GDP data for each team based on their location seemed wise, so we could adjust for GDP if needed.

I acquired a GDP dataset from the International Monetary Fund (IMF) that contained yearly GDP values for over 200 countries. However, the issue with this GDP dataset was that it didn't have country codes but instead had country names. Unfortunately, the esports dataset only had country codes, so I first had to merge the GDP dataset with the exchange rates dataset (which had both codes and names) to acquire the country codes.
```
GDP_merge <- GDP_long %>% left_join(historical_exchange_rates, join_by("country_name", "year"), multiple = "any")

GDP_merge <- GDP_merge[c("country_code", "country_name", "year", "GDP")]

GDP_merge <- GDP_merge[!is.na(GDP_merge$country_code),]
```
I then merged the GDP dataset with the esports dataset. I performed two joins, one for each team within a game, and then integrated these two joins into a single dataset.
```
# Process merged esport.data
merged_data$year <- format(as.Date(merged_data$begin_date, format ="%Y/%m/%d"), "%Y")

# Merge
main_GDP_merge <- merged_data %>%
  left_join(GDP_merge, join_by("opponent_0.location" == "country_code", "year"), multiple = "any")

main_GDP_merge <- main_GDP_merge %>% rename(
  opp0_GDP = GDP, opp0_country_name = country_name, opp0_year = year
)

secondary_GDP_merge <- merged_data %>%
  left_join(GDP_merge, join_by("opponent_1.location" == "country_code", "year"), multiple = "any")

main_GDP_merge$opp1_year <- secondary_GDP_merge$year
main_GDP_merge$opp1_country_name <- secondary_GDP_merge$country_name
main_GDP_merge$opp1_GDP <- secondary_GDP_merge$GDP
```
After this the data transformation was essentially done!

### Analysis

A large portion of the analysis was done by my supervisor, who set up a new dataframe with cleaner column names and performed necessary preparations, such as calculating the win-rates for each team based on their previous game outcomes. All of this is available in the repo near the bottom of the `WLeffects.R` file if you're interested.

We then ran a general linear mixed effects model to see if winning/losing previous games predicted the outcome of future games. For analysis, winner/loser effects were represented by "win/loss deviation"; this was calculated by subtracting a team's win rate (from 0-1) from 1 if they won the previous game, and 0 if they lost the previous game. The resulting value, ranging from -1 to 1, represented whether a team won (a deviation above 0) or lost (a deviation below 0) the previous game, relative to that team's average win-rate.

We found a significant effect of this win/loss deviation (winner/loser effect) as hypothesized (p < .001). Though the specifics of the odds ratios are more complicated, we could essentially say that winning a previous game increased a team's odds of winning the current game by approximately 1.07. 

![main winner/loser effect](./images/main_wl_effect.png)

Interestingly, this had a significant interaction effect with prize money as well. Essentially, for every extra $1 of prize money, the influence of the winner/loser effect on the likelihood of a team winning the current game increased by 1.04.

![prize money winner/loser effect interaction](./images/wl_money_interaction.png)

## Conclusion

This project was enjoyable, and I felt fortunate to have a great supervisor and an interesting topic to investigate and learn to code. It will be even more exciting when I transform this project into a full-fledged data pipeline...!