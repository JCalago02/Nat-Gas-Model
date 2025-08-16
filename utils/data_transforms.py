import pandas as pd
import numpy as np

class DataTransforms:
    @staticmethod
    def upscale_monthly_to_weekly(df: pd.DataFrame, datetime_col: str, value_col: str) -> pd.DataFrame:
        req_columns = [datetime_col, value_col]
        missing_cols = [col for col in req_columns if col not in df.columns]
        if len(missing_cols) > 0:
            raise ValueError(f"Columns {missing_cols} are required for the upscale_monthly_to_weekly()")

        weekly_index = pd.date_range(df[datetime_col].min(), df[datetime_col].max() + pd.Timedelta(weeks=4), freq='W', inclusive='both')

        weekly_df = (pd.DataFrame(weekly_index,columns=[datetime_col])
            .sort_values(by=[datetime_col])
            .assign(Year=lambda x: x[datetime_col].dt.year,
                    Month=lambda x: x[datetime_col].dt.month,
                    Week=lambda x: x[datetime_col].dt.strftime("%U").astype(int))
        )


        weekly_df['is_middle_week'] = (weekly_df
            .groupby(weekly_df[datetime_col].dt.to_period('M'), group_keys=False)
            .apply(lambda g: g[datetime_col] == min(g[datetime_col], key=lambda d: abs(d - (d.replace(day=15)))))
        )

        # Perform interpolation expanding out from middle weeks of each month
        return (pd.merge(weekly_df, df.drop(columns=[datetime_col]), on=["Year", "Month"], how="left")
            .assign(value=lambda x: 
                x[value_col]
                .where(x['is_middle_week'], np.nan)
                .interpolate('linear', limit_direction='both') / 4
            )
            .drop(columns=["is_middle_week"])
        )

    @staticmethod
    def calculate_deviation_from_yearly_avg(df: pd.DataFrame, datetime_col: str, value_col: str) -> pd.DataFrame:
        req_columns = [datetime_col, value_col]
        missing_cols = [col for col in req_columns if col not in df.columns]
        if len(missing_cols) > 0:
            raise ValueError(f"Columns {missing_cols} are required for the calculate_deviation_from_yearly_avg()")

        df['year'] = df[datetime_col].dt.year
        yearly_avg_df = (df
            .groupby(['Year'])[value_col].mean()
            .reset_index()
            .rename(columns={value_col: 'yearly_avg'})
        )

        return (pd.merge(df, yearly_avg_df, on='Year', how='left')
            .assign(deviation=lambda x: (x[value_col] / x['yearly_avg'] - 1) * 100)
        )

