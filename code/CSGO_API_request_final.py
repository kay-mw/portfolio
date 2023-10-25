import requests
import pandas as pd

headers = {
    "accept": "application/json",
    "authorization": "Bearer V6AgJUND-4v26c2PFZTRu2_V4yJ9GvZTMar1I9fe6RhRTFCnW9o"
}

response = []
for page in range(1,998):
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
                 'opponent_1.image_url','opponent_1.modified_at','opponent_1.slug','games','results'],inplace=True)
df.style

print(df)

df.to_csv('max_api_test.csv')