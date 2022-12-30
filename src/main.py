import json
import os
import sys

import pandas as pd
import requests

from bs4 import BeautifulSoup
from datetime import date, datetime
from pdf import Team_PDF

API_URL = 'https://api.sportsdata.io/v3/nba/scores/json/{}'

HEADERS = {
    'Ocp-Apim-Subscription-Key': open("config.txt", "r").readline().rsplit(':')[1]
}

FORECAST_URL = 'https://www.sportytrader.es/pronosticos/baloncesto/usa/nba-306/'


def extract_json_from_api(url_api: str):
    """
    Extracts json from a given API, and saves it on the ../data directory.
    """
    try:
        response = requests.get(url_api, headers=HEADERS)
        if response.status_code != 200:
            raise ConnectionError
        data = response.json()
        file = open(f'../data/raw_{url_api.rsplit("/")[-1]}.json', 'w')
        json.dump(data, file, indent=2)
        return pd.json_normalize(data)
    except Exception:
        if f'raw_{url_api.rsplit("/")[-1]}.json' in os.listdir('../data'):
            with open(f'../data/raw_{url_api.rsplit("/")[-1]}.json', 'w') as infile:
                data = json.load(infile)
                infile.close()
            return pd.json_normalize(data)
        else:
            raise ConnectionError(f"Could not connect to {url_api} and there are no local files to use.")


def extract_dataframes_from_teams():
    """
    Given a team_id, it gets from sportsdata.io API a dataframe containing the player stats in 2023.
    """
    url_api = f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/{team_input}'
    dataframe = extract_json_from_api(url_api=url_api)
    return dataframe


def stylize_dataframe(styled_dataframe):
    """
    Given a dataframe, it returns a stylized version of it (with outer and inner borders).
    """
    styled_dataframe.set_properties(
        **{'border': '1px black solid !important'}
    ).set_table_styles([{
        'selector': '',
        'props': [('border', '2px black solid !important')]}]
    )

    styled_dataframe.set_table_styles([{'selector': 'th',
                                        'props': [('font-size', '10pt'),
                                                  ('border-style', 'solid'),
                                                  ('border-width', '1px')]}])
    return styled_dataframe


def get_best_player(team_dataframe):
    """
    Finds the best player of the team and returns his name, data and image path
    """
    # Find the best player's ID
    best_player_info = team_dataframe.iloc[team_dataframe['Points'].idxmax()]
    player_id = best_player_info['PlayerID']

    # Get the best player's details from players dataframe
    dataframe_player_details = dataframe_players
    details_full = dataframe_player_details[dataframe_player_details['PlayerID'] == player_id]

    # Sum up player information
    details = details_full[['Height', 'Weight', 'BirthDate', 'BirthCity', 'BirthCountry', 'Salary', 'Experience']].T
    details = details.rename(columns={details.columns[0]: best_player_info["Name"]})

    # Stylize details' dataframe
    styled_details = stylize_dataframe(details.style)

    # Save player image
    image = requests.get(details_full['PhotoUrl'].values[0])
    with open(f'../images/{best_player_info["Name"].replace(" ", "_")}.png', 'wb') as file:
        file.write(image.content)
        file.close()

    return {'Name': best_player_info['Name'], 'Data': styled_details,
            'Image_path': f'../images/{best_player_info["Name"].replace(" ", "_")}.png'}


def forecast_next_matches():
    response = requests.get(FORECAST_URL)
    soup = BeautifulSoup(response.content, "html.parser")
    predictions = soup.find_all("div", class_="w-full xl:w-2/5 flex justify-center items-center py-4")

    forecast = []
    for prediction in predictions:
        team_1 = prediction.find_all("div", class_="w-1/2 text-center break-word p-1 dark:text-white")[0].text.strip()
        team_2 = prediction.find_all("div", class_="w-1/2 text-center break-word p-1 dark:text-white")[1].text.strip()

        if (steam_name := team_name.split(" ")[-1]) in [team_1.split(" ")[-1], team_2.split(" ")[-1]]:
            wins = prediction.find("span", class_="flex justify-center items-center h-7 w-6 rounded-md font-semibold"
                                                  " bg-primary-green text-white mx-1").text

            if steam_name == team_1.split(" ")[-1]:
                text = f"{team_1} wins against {team_2}." if wins == "1" else (
                    f"{team_1} loses against {team_2}." if wins == "2" else (
                        f"{team_1} ties against {team_2}."))
            else:
                text = f"{team_2} loses against {team_1}." if wins == "1" else (
                    f"{team_2} wins against {team_1}." if wins == "2" else (
                        f"{team_2} ties against {team_1}."))
            forecast.append(text)
    return "\n".join(forecast) if len(forecast) > 0 else f"There are no close matches where {team_name} plays."


def create_pdf():
    """
    Creates a pdf with the most relevant information of the team, and a forecast for its next match
    """
    dataframe_players["BirthDate"] = pd.to_datetime(dataframe_players["BirthDate"])

    team_info = dataframe_teams[dataframe_teams['Key'] == team_input]
    color = '#' + team_info['SecondaryColor'].values[0]

    # Getting team logo
    image = requests.get(team_info['WikipediaLogoUrl'].values[0])
    with open(f'../images/{team_input}.svg', 'wb') as outfile:
        outfile.write(image.content)
    pdf = Team_PDF(f'{team_name}', f'../images/{team_input}.svg', color)

    # Extracting relevant information
    dataframe_team = dataframe_selected_team[['Name', 'Position', 'Games', 'FieldGoalsMade', 'FieldGoalsAttempted',
                                              'Rebounds', 'Assists', 'Steals', 'BlockedShots', 'Points']]

    # Stylize team dataframe
    styled_dataframe_team = stylize_dataframe(dataframe_team.style).background_gradient(subset=["Points"],
                                                                                        cmap="RdYlGn",
                                                                                        vmin=0,
                                                                                        vmax=dataframe_team
                                                                                             ["Points"].max())
    # Add table to pdf
    pdf.create_table(styled_dataframe_team, f"Players from {team_input} (stats):")

    # Find the best player of the team and create a card with his details
    best_player = get_best_player(dataframe_selected_team)
    pdf.create_card(f'Best player: {best_player["Name"]}', best_player['Image_path'], best_player['Data'])

    # Add graph to pdf
    pdf.create_graph("Goal Ratio (Made-Failed):", dataframe_team)

    # Get the average player's age
    def get_age(birthdate: int):
        today = date.today()
        return today.year - birthdate - 1970 - ((today.month, today.day) < (birthdate % 12 + 1, birthdate + 1))

    age = sum(
        (ages := [get_age(dataframe_players[dataframe_players["PlayerID"] == player]['BirthDate'].values[0].astype(
            'datetime64[Y]').astype(int)) for player in dataframe_selected_team["PlayerID"].to_list()
                  if len(dataframe_players[dataframe_players["PlayerID"] == player]['BirthDate'].values) > 0])) / len(
        ages)
    # Add average age to pdf
    pdf.create_text_card("Average Player Age:", f"The average age is {round(age, 1)}")

    # Create pdf footer (Forecast)
    now = datetime.now()
    pdf.create_footer(f"Forecast ({now.strftime('%d/%m/%Y %H:%M:%S')}):", forecast_next_matches())

    # Save the PDF
    pdf.output(f"../{team_input}.pdf")


if __name__ == "__main__":
    # Delete all current images in "../images" directory
    print("Deleting old images...")
    for image in os.listdir("../images"):
        os.remove(os.path.join("../images", image))

    print("Creating pdf...")
    try:
        # List of API endpoints
        urls = [API_URL.format(endpoint) for endpoint in ['teams', 'Players']]
        # Create dataframes
        dataframe_teams, dataframe_players = [extract_json_from_api(url) for url in urls]

        # Get team name
        team_name = "Philadelphia 76ers"

        # Remove hashtags from the code below if you want an input based search
        # print("Valid team names:", teams := (dataframe_teams["City"] + ' ' + dataframe_teams["Name"]).tolist())
        # team_name = input("Enter a valid team name: ")

        # if team_name not in teams:
        #     print(f'Sorry, there is no data from "{team_name}". Exiting program...')
        #     sys.exit()

        team_input = dataframe_teams[dataframe_teams["Name"] == team_name.rsplit(" ")[-1]]["Key"].values[0]
        dataframe_selected_team = extract_dataframes_from_teams()

        # Create pdf
        create_pdf()
        # Open pdf
        # os.system(fr"../{team_input}.pdf")
        print("Finished")
    except KeyboardInterrupt:
        print("Forced exit. Progress will not be saved.")
    sys.exit()

