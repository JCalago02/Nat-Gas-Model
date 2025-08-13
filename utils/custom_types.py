from enum import Enum

class FuelType(Enum):
    NATURAL_GAS = "NG"
    PETROLEUM = "OIL"
    COAL = "COL"
    NUCLEAR = "NUC"
    HYDRO = "WAT"
    SOLAR = "SUN"
    WIND = "WND"
    OTHER = "OTH"

class Respondent(Enum):
    PJM = "PJM"
    MISO = "MISO"
    ERCOT = "ERCO"

class Timezone(Enum):
    EASTERN = "Eastern"
    CENTRAL = "Central"
    MOUNTAIN = "Mountain"
    PACIFIC = "Pacific"
