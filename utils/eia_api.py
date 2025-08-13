import os
from time import timezone
import requests
import json
from typing import Dict, List, Tuple
from datetime import datetime
from utils.custom_types import FuelType, Respondent, Timezone
from typing import Any, Optional

MAX_QUERY_SIZE = 5000
SET_TIMEZONE = Timezone.EASTERN # Hardcoded to ensure all data queries are consistent

class EIADataPuller:
    def __init__(self):
        self.api_key = os.getenv('EIA_API_KEY')

    def _build_header(self, 
        frequency: Optional[str], 
        data: Optional[list[str]],
        facets: Optional[Dict[str, list[str]]],
        start: str,
        end: str,
        sort: Optional[List[Dict[str, str]]],
        offset: int,
        length: int
    ) -> Dict[str, Any]:
        header = {
            "api_key": self.api_key,
            "start": start,
            "end": end,
            "offset": offset,
            "length": length,
        }
        if data:
            header["data"] = data
        if facets:
            header["facets"] = facets
        if sort: 
            header["sort"] = sort
        if frequency:
            header["frequency"] = frequency
        return header

    def _generate_header_str(self, header: Dict[str, Any]) -> str:
        return {
            "X-Params": json.dumps(header)
        }

    def _get_data_and_size(self, header: Dict[str, Any], url: str) -> Tuple[List[Dict[str, Any]], int]:
        header["offset"] = 0
        header["length"] = MAX_QUERY_SIZE
        req = requests.get(url, headers=self._generate_header_str(header), params={"api_key": self.api_key})
        return req.json()['response']['data'], int(req.json()['response']['total'])
    
    def _get_res_data(self, header: Dict[str, Any], url: str, offset: int, length: int) -> List[Dict[str, Any]]:
        header["offset"] = offset
        header["length"] = length
        req = requests.get(url, headers=self._generate_header_str(header), params={"api_key": self.api_key})
        return req.json()['response']['data']

    def get_power_gen_data(self, fueltype: FuelType, respondent: Respondent):
        POWER_GEN_START_DATE = "2019-01-01"
        header_params = self._build_header(
            frequency="daily",
            data=["value"],
            facets={"respondent": [respondent.value], "fueltype": [fueltype.value], "timezone": [SET_TIMEZONE.value]},
            start=POWER_GEN_START_DATE,
            end=datetime.now().strftime("%Y-%m-%d"),
            sort=[
                {
                    "column": "period",
                    "direction": "desc"
                }
            ],
            offset=0,
            length=1
        )
        power_gen_data_url = f"https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/"

        res_list, res_size = self._get_data_and_size(header_params, power_gen_data_url)

        print(f"Querying {res_size} rows of data...")
        while len(res_list) < res_size:
            query_size = min(MAX_QUERY_SIZE, res_size - len(res_list))
            res_list.extend(self._get_res_data(header_params, power_gen_data_url, len(res_list), query_size))
            print(f"Recieved {len(res_list)} rows of data...")

        return res_list