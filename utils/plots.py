import matplotlib.pyplot as plt

class EDAPlots:
    @staticmethod
    def generate_year_plot(df, column, title: str):
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