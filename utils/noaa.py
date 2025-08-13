import requests


if __name__ == "__main__":
    test = requests.get("https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2024/ClimateDivisions.Cooling.txt")
    ab = test.text.split("\n")
    print(ab[0])
    print(ab[1])
    print(ab[3])

