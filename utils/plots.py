import matplotlib.pyplot as plt

class EDAPlots:
    @staticmethod
    def generate_year_plot(df, column: str, title: str):
        """
        Plot a time series by year.

        Args:
            df: DataFrame containing the data
            column: Name of the column to plot
            title: Title of the plot

        Raises:
            ValueError: If required columns are missing from the DataFrame
        """
        req_columns = ['Year', 'DayOfYear', column]
        missing_cols = [col for col in req_columns if col not in df.columns]
        if len(missing_cols) > 0:
            raise ValueError(f"Columns {missing_cols} are required for the plot")

        # Plot data column by year 
        plt.figure(figsize=(15, 8))
        for year in df['Year'].unique():
            year_data = df[df['Year'] == year]
            plt.plot(year_data['DayOfYear'], year_data[column], 
                    label=str(year), linewidth=2, alpha=0.7)

        # Add plot elements 
        plt.title(title, fontsize=14)
        plt.xlabel('Day of Year', fontsize=12)
        plt.ylabel(column, fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        plt.show()
    
    @staticmethod
    def plot_dual_time_series(title: str, df, series1_col: str, series2_col: str):
        """
        Plot two time series on the same chart.
        
        Args:
            title (str): Title for the plot
            df: DataFrame containing the data
            series1_col (str): Name of the first time series column
            series2_col (str): Name of the second time series column
        
        Raises:
            ValueError: If required columns are missing from the DataFrame
        """
        # Assert that required columns exist
        req_columns = ['period', series1_col, series2_col]
        missing_cols = [col for col in req_columns if col not in df.columns]
        if len(missing_cols) > 0:
            raise ValueError(f"Columns {missing_cols} are required for the plot")
        
        # Create the plot
        plt.figure(figsize=(15, 8))
        
        # Plot both time series
        plt.plot(df['period'], df[series1_col], label=series1_col, linewidth=2, alpha=0.8)
        plt.plot(df['period'], df[series2_col], label=series2_col, linewidth=2, alpha=0.8)
        
        # Add plot elements
        plt.title(title, fontsize=14)
        plt.xlabel('Period', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        plt.show()
    
    @staticmethod
    def plot_dual_time_series_separate_dfs(title: str, df1, series1_col: str, df2, series2_col: str, 
                                         series1_label: str, series2_label: str):
        """
        Plot two time series from different DataFrames on the same chart.
        
        Args:
            title (str): Title for the plot
            df1: First DataFrame containing the first time series
            series1_col (str): Name of the time series column in df1
            df2: Second DataFrame containing the second time series
            series2_col (str): Name of the time series column in df2
            series1_label (str, optional): Label for first series. Defaults to series1_col
            series2_label (str, optional): Label for second series. Defaults to series2_col
        
        Raises:
            ValueError: If required columns are missing from either DataFrame
        """
        # Assert that required columns exist in df1
        req_columns_df1 = ['period', series1_col]
        missing_cols_df1 = [col for col in req_columns_df1 if col not in df1.columns]
        if len(missing_cols_df1) > 0:
            raise ValueError(f"DataFrame 1 is missing columns: {missing_cols_df1}")
        
        # Assert that required columns exist in df2
        req_columns_df2 = ['period', series2_col]
        missing_cols_df2 = [col for col in req_columns_df2 if col not in df2.columns]
        if len(missing_cols_df2) > 0:
            raise ValueError(f"DataFrame 2 is missing columns: {missing_cols_df2}")
        
        # Create the plot
        plt.figure(figsize=(15, 8))
        
        # Plot both time series
        plt.plot(df1['period'], df1[series1_col], label=series1_label, linewidth=2, alpha=0.8)
        plt.plot(df2['period'], df2[series2_col], label=series2_label, linewidth=2, alpha=0.8)
        
        # Add plot elements
        plt.title(title, fontsize=14)
        plt.xlabel('Period', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        plt.show()