import requests
import json
import pandas as pd
import webbrowser
import os

API_POKEMON = "https://pokeapi.co/api/v2/pokemon/{pokemon}"


def call_api(url):
    """Call the Pokemon API and return the response or 404."""
    response = requests.get(url)
    if response.status_code == 404:
        return 404
    if response.status_code != 200:
        raise Exception(f"API response: {response.status_code}")
    return response


def write_pokemon_to_jsonfile(json_res):
    """Extract relevant info and write to pokemon.json"""
    moves = [move["move"]["name"] for move in json_res["moves"]]
    abilities = [ability["ability"]["name"] for ability in json_res["abilities"]]
    types = [t["type"]["name"] for t in json_res["types"]]
    data = {
        "id": json_res["id"],
        "pokemon": json_res["name"],
        "weight": json_res["weight"],
        "height": json_res["height"],
        "types": types,
        "abilities": abilities,
        "moves": moves,
        "image": json_res["sprites"]["front_default"],
    }
    with open("pokemon.json", "w") as f:
        print("Writing pokemon to json file...")
        json.dump(data, f, indent=2)
        print("Done.")


def image_formatter(url):
    if not url:
        return ""
    return f'<img src="{url}" width="200" height="200">'


def list_formatter(lst):
    if not lst:
        return ""
    return ", ".join(lst)
def format_html_content(df):
        df["image"] = df["image"].apply(image_formatter)
        df["types"] = df["types"].apply(list_formatter)
        df["abilities"] = df["abilities"].apply(list_formatter)
        df["moves"] = df["moves"].apply(list_formatter)
        return f"""
            <div style="display: flex; flex-direction: column; width: 500px;">
               <div style="display: flex; flex-direction: row; width: 500px; border: 1px solid black; gap: 10px; padding: 10px; align-items: center;">
               <span style="width: 20%; font-weight: bold;">Image: </span>
               {df["image"].values[0]}
               </div>
               <div style="display: flex; flex-direction: row; width: 500px; border: 1px solid black; gap: 10px; align-items: center; padding: 10px; ">
               <span style="width: 20%; font-weight: bold;">Weight</span>
               {df["weight"].values[0]/10}Kg  
               </div>
               <div style="display: flex; flex-direction: row; width: 500px; border: 1px solid black; gap: 10px; align-items: center; padding: 10px; ">
               <span style="width: 20%; font-weight: bold;">Height</span>
               {df["height"].values[0]*10}cm 
               </div>
               <div style="display: flex; flex-direction: row; width: 500px; border: 1px solid black; gap: 10px; align-items: center; padding: 10px; ">
               <span style="width: 20%; font-weight: bold;">Types</span>
               {df["types"].values[0]}  
               </div>
               <div style="display: flex; flex-direction: row; width: 500px; border: 1px solid black; gap: 10px; align-items: center; padding: 10px;">
               <span style="width: 20%; font-weight: bold;">Moves</span>
               {df["moves"].values[0]}
               </div>
               <div style="display: flex; flex-direction: row; width: 500px; border: 1px solid black; gap: 10px; align-items: center; padding: 10px;">
               <span style="width: 20%; font-weight: bold;">Abilities</span>
               {df["abilities"].values[0]}
               </div>
               </div>
            
        """

def generate_pokedex_html(list_pokemon):
    """Generate HTML table from list of Pokémon and open in browser."""
    if not list_pokemon:
        print("No Pokémon data to display!")
        return

    # Build DataFrame from list of dicts
    df = pd.DataFrame(list_pokemon)

    # Sort by 'id' if present
    if "id" in df.columns:
        df.sort_values("id", inplace=True)

    # Convert DataFrame to HTML
    

    # Wrap in full HTML page
    full_html = f"""
    <html>
    <head>
        <title>Pokédex</title>
        <style>
            table {{
                border-collapse: collapse;
            }}
            td, th {{
                border: 1px solid black;
                padding: 5px;
                text-align: center;
                vertical-align: top;
            }}
            img {{
                display: block;
                margin: auto;
            }}
        </style>
    </head>
    <body>
        <h1>Pokédex</h1>
        {format_html_content(df)}
    </body>å
    </html>
    """

    # Save to file and open in browser
    filename = "pokedex.html"
    with open(filename, "w") as f:
        f.write(full_html)
    filepath = os.path.abspath(filename)  # full path
    webbrowser.open_new_tab(f"file://{filepath}")
    print(f"Pokédex saved and opened in browser: {filename}")


def get_pokemon_by_name(name):
    """Fetch a single Pokémon by name"""
    res = call_api(API_POKEMON.format(pokemon=name.lower()))
    if res == 404:
        print("Pokemon not found")
        return None
    return res.json()


def process_pokemon(name):
    """Fetch Pokémon, write JSON, and display in HTML"""
    data = get_pokemon_by_name(name)
    if not data:
        return

    write_pokemon_to_jsonfile(data)
    generate_pokedex_html([{
        "id": data["id"],
        "pokemon": data["name"],
        "weight": data["weight"],
        "height": data["height"],
        "types": [t["type"]["name"] for t in data["types"]],
        "abilities": [a["ability"]["name"] for a in data["abilities"]],
        "moves": [m["move"]["name"] for m in data["moves"]],
        "image": data["sprites"]["front_default"],
    }])


if __name__ == "__main__":
    pokemon_name = input("Enter Pokémon name: ")
    process_pokemon(pokemon_name)
