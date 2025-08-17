import pandas as pd
import numpy as np
from typing import List

class DataTransforms:
    @staticmethod
    def _validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
        missing_cols = [col for col in required_columns if col not in df.columns]
        if len(missing_cols) > 0:
            raise ValueError(f"Columns {missing_cols} are required for the upscale_monthly_to_weekly()")

    @staticmethod
    def downscale_daily_to_weekly(df: pd.DataFrame, datetime_col: str, value_col: str) -> pd.DataFrame:
        DataTransforms._validate_required_columns(df, [datetime_col, value_col])


        return (df
            .sort_index()
            .resample(rule="W-FRI", on=datetime_col).mean()
            .reset_index(drop=False)
        )

    @staticmethod
    def upscale_monthly_to_weekly(df: pd.DataFrame, datetime_col: str, value_col: str) -> pd.DataFrame:
        DataTransforms._validate_required_columns(df, [datetime_col, value_col])
        
        df[value_col] = df[value_col] / df[datetime_col].dt.days_in_month

        weekly_index = pd.date_range(df[datetime_col].min(), df[datetime_col].max() + pd.Timedelta(weeks=4), freq='W-FRI', inclusive='both')

        weekly_df = (pd.DataFrame(weekly_index,columns=[datetime_col])
            .sort_values(by=[datetime_col])
            .assign(Year=lambda x: x[datetime_col].dt.year,
                    Month=lambda x: x[datetime_col].dt.month,
                    Week=lambda x: x[datetime_col].dt.strftime("%U").astype(int))
        )
        return (pd.merge(weekly_df, df.drop(columns=[datetime_col]), on=["Year", "Month"], how="left")
            .assign(value=lambda x: x['value'] / 30 * 4) # Assume scaled to 30 days/month, then scale to 4 weeks/month
        )

    @staticmethod
    def weekly_interpolate_from_middle_week(df: pd.DataFrame, datetime_col: str, value_col: str) -> pd.DataFrame:
        DataTransforms._validate_required_columns(df, [datetime_col, value_col])

        df['is_middle_week'] = (df
            .groupby(df[datetime_col].dt.to_period('M'), group_keys=False)
            .apply(lambda g: g[datetime_col] == min(g[datetime_col], key=lambda d: abs(d - (d.replace(day=15)))))
        )

        return (df
            .assign(value=lambda x: 
                x[value_col]
                .where(x['is_middle_week'], np.nan)
                .interpolate('linear', limit_direction='both')
            )
            .drop(columns=["is_middle_week"])
        )

    @staticmethod
    def calculate_deviation_from_yearly_avg(df: pd.DataFrame, datetime_col: str, value_col: str) -> pd.DataFrame:
        DataTransforms._validate_required_columns(df, [datetime_col, value_col])

        df['year'] = df[datetime_col].dt.year
        yearly_avg_df = (df
            .groupby(['Year'])[value_col].mean()
            .reset_index()
            .rename(columns={value_col: 'yearly_avg'})
        )

        weekly_avg_deviation_df = (pd.merge(df, yearly_avg_df, on='Year', how='left')
            .assign(deviation=lambda x: (x[value_col] / x['yearly_avg'] - 1) * 100)
            .groupby("Week")['deviation'].mean()
            .reset_index()
        )

        return pd.merge(df, weekly_avg_deviation_df, on='Week', how='left').drop(columns=['value'])

