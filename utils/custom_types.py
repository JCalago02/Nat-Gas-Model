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
    CAL = "CAL"
    NORTHWEST = "NW"
    SOUTHWEST = "SW"
    TEXAS = "TX"
    CENTRAL = "CENT"
    MIDWEST = "MIDW"
    TENNESSEE = "TEN"
    FLORIDA = "FL"
    SOUTHEAST = "SE"
    CAROLINAS = "CAR"
    MIDATLANTIC = "MIDA"
    NEWYORK = "NY"
    NEWENGLAND = "NE"

class Timezone(Enum):
    EASTERN = "Eastern"
    CENTRAL = "Central"
    MOUNTAIN = "Mountain"
    PACIFIC = "Pacific"

class StorageRegion(Enum):
    EAST = "NW2_EPG0_SWO_R31_BCF"
    MIDWEST = "NW2_EPG0_SWO_R32_BCF"
    PACIFIC = "NW2_EPG0_SWO_R35_BCF"
    SOUTH = "NW2_EPG0_SWO_R33_BCF"
    MOUNTAIN = "NW2_EPG0_SWO_R34_BCF"
    SALT = "NW2_EPG0_SSO_R33_BCF"
    NONSALT = "NW2_EPG0_SNO_R33_BCF"
    LOWER_48 = "NW2_EPG0_SWO_R48_BCF"

class EIAConsumptionType(Enum):
    ELECTRICITY = "VEU"
    COMMERCIAL = "VCS"
    VEHICLEFUEL = "VDV"
    DELIVERY = "VGT"
    INDUSTRIAL = "VIN"
    RESIDENTIAL = "VRS"

storage_region_to_noaa_states = {
    StorageRegion.EAST: ["FL", "GA", "SC", "NC", "VA", "WV", "OH", "PA", "MD", "DE", "NJ", "NY", "CT", "RI", "MA", "NH", "ME", "VT"],
    StorageRegion.MIDWEST: ["MN", "IA", "MO", "IL", "WI", "MI", "IN", "KY", "TN"],
    StorageRegion.SOUTH: ["TX", "OK", "KS", "AR", "LA", "MS", "AL"],
    StorageRegion.MOUNTAIN: ["NV", "AZ", "UT", "ID", "MT", "WY", "CO", "NM", "NE", "SD", "ND"],
    StorageRegion.PACIFIC: ["CA", "OR", "WA"]
}

storage_region_to_power_gen_respondent_region = {
    StorageRegion.EAST: [Respondent.MIDATLANTIC, Respondent.NEWYORK, Respondent.NEWENGLAND, Respondent.CAROLINAS, Respondent.FLORIDA],
    StorageRegion.MIDWEST: [Respondent.MIDWEST, Respondent.TENNESSEE],
    StorageRegion.SOUTH: [Respondent.TEXAS, Respondent.SOUTHEAST],
    StorageRegion.MOUNTAIN: [Respondent.CENTRAL, Respondent.NORTHWEST, Respondent.SOUTHWEST],
    StorageRegion.PACIFIC: [Respondent.CAL, Respondent.NORTHWEST]
}
