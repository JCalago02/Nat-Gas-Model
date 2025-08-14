import os
from time import timezone
import requests
import json
from typing import Dict, List, Tuple
from datetime import datetime
from utils.custom_types import (
    FuelType, 
    Respondent, 
    Timezone, 
    StorageRegion, 
    EIAConsumptionType,
    storage_region_to_power_gen_respondent_region
)
from typing import Any, Optional
import pandas as pd

MAX_QUERY_SIZE = 5000
SET_TIMEZONE = Timezone.EASTERN # Hardcoded to ensure all data queries are consistent

class EIADataPuller:
    def __init__(self, storage_region: StorageRegion):
        self.api_key = os.getenv('EIA_API_KEY')
        self.storage_region: StorageRegion = storage_region
        self.power_gen_respondents: List[Respondent] = storage_region_to_power_gen_respondent_region[storage_region]
        self.eia_duoareas: List[str] = [f"S{abbr.value}" for abbr in self.power_gen_respondents]

    def _build_header(self, 
        frequency: Optional[str], 
        data: Optional[list[str]],
        facets: Optional[Dict[str, list[str]]],
        start: str,
        end: str,
        sort: Optional[List[Dict[str, str]]] = None,
        offset: int = 0,
        length: int = 1
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

        print(req.json())
        return req.json()['response']['data'], int(req.json()['response']['total'])
    
    def _get_data_with_offset(self, header: Dict[str, Any], url: str, offset: int, length: int) -> List[Dict[str, Any]]:
        header["offset"] = offset
        header["length"] = length
        req = requests.get(url, headers=self._generate_header_str(header), params={"api_key": self.api_key})
        return req.json()['response']['data']

    def _get_all_data(self, header: Dict[str, Any], url: str) -> List[Dict[str, Any]]:
        res_list, res_size = self._get_data_and_size(header, url)
        print(f"Querying {res_size} rows of data...")
        while len(res_list) < res_size:
            query_size = min(MAX_QUERY_SIZE, res_size - len(res_list))
            res_list.extend(self._get_data_with_offset(header, url, len(res_list), query_size))
            print(f"Recieved {len(res_list)} rows of data...")
        return res_list

    def get_power_gen_data(self, fueltype: FuelType) -> pd.DataFrame:
        """
        Pulls EIA Power Generation Consumption data for a specific fueltype. 
        Daily data is aggregated across all respondents for a given storage 
        region, then is grouped again to find a weekly average.
        """
        POWER_GEN_URL = f"https://api.eia.gov/v2/electricity/rto/daily-fuel-type-data/data/"
        POWER_GEN_START_DATE = "2019-01-01"
        EXP_COLS = ["period", "value", "respondent-name"]
        header = self._build_header(
            frequency="daily",
            data=["value"],
            facets={"respondent": [respondent.value for respondent in self.power_gen_respondents], "fueltype": [fueltype.value], "timezone": [SET_TIMEZONE.value]},
            start=POWER_GEN_START_DATE,
            end=datetime.now().strftime("%Y-%m-%d"),
        )

        df = (pd.DataFrame(self._get_all_data(header, POWER_GEN_URL))[EXP_COLS]
            .astype({"value": int, "period": "datetime64[ns]", "respondent-name": "category"})
        )

        df['Week'] = df['period'].dt.strftime("%U").astype(int)
        df['Year'] = df['period'].dt.year
        return (df.groupby(["period", "Year", "Week"])["value"].sum()
            .reset_index(drop=False)
            .groupby(["Week", "Year"])["value"].mean()
            .reset_index(drop=False) 
            .rename(columns={"value": f"Region_NG_Power_Gen_MWh"})
        )



    def get_storage_data(self) -> pd.DataFrame:
        """
        Pulls EIA Natural Gas Storage data for a specific storage
        region. Data is retrieved at a weekly frequency.
        """
        STORAGE_URL = f"https://api.eia.gov/v2/natural-gas/stor/wkly/data/"
        STORAGE_START_DATE= "2019-01-01"
        EXP_COLS = ["period", "value"]

        header = self._build_header(
            frequency="weekly",
            data=["value"],
            facets={"series": [self.storage_region.value]},
            start=STORAGE_START_DATE,
            end=datetime.now().strftime("%Y-%m-%d"),
        )

        return (pd.DataFrame(self._get_all_data(header, STORAGE_URL))[EXP_COLS]
            .astype({"value": int, "period": 'datetime64[ns]'})
            .rename(columns={"value": f"{self.storage_region.name}_Region_NG_Storage_BCF"})
            .sort_values(by="period", ascending=False)
            .reset_index(drop=True)
        )

    def get_ng_usage_data(self, consumption_type: EIAConsumptionType) -> pd.DataFrame:
        USAGE_URL = f"https://api.eia.gov/v2/natural-gas/cons/sum/data/"
        USAGE_START_DATE = "2005-01-01"

        header = self._build_header(
            frequency="monthly",
            data=["value"],
            facets={"duoarea": self.eia_duoareas, "process": [consumption_type.value]},
            start=USAGE_START_DATE,
            end=datetime.now().strftime("%Y-%m-%d"),
        )

        return pd.DataFrame(self._get_all_data(header, USAGE_URL))