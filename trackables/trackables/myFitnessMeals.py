from util.dbInterface import DBInterface
from trackables.trackables.trackableFactories import NutrientFactory
from util.paths import MFPDataPath

import pandas as pd


# Interface that reads data from the myfitnesspal spreadsheet and stores information in trackables
class MFPManager():
    # TODO: REINDEX BY DATE
    def __init__(self):
        # If MFP integration is selected but no data is available
        try:
            df = pd.read_csv(MFPDataPath)
        except FileNotFoundError:
            self.nutrientTrackables = {}
            self.meals = []
            return
        # Data is written the Excel sheet by MFP.py automatically
        df['Date'] = df['Date'].apply(
                            lambda x: DBInterface.convertToDateTime(x, '%Y-%m-%d'))
        df = df.set_index('Date')
        df.sort_index(inplace=True)

        nutrients = ['Calories', 'Carbohydrates',
                     'Fat', 'Protein', 'Sodium', 'Sugar']
        self.nutrientTrackables = {nutrient: NutrientFactory.create(
            nutrient, df[nutrient].to_frame(name='Score')) for nutrient in nutrients}
        # Load each row in the spreadsheet into a separate meal object
        self.meals = [Meal(df.index.to_list()[i], *df.iloc[i].to_list())
                      for i in range(df.shape[0])]

    def getTrackables(self):
        return list(self.nutrientTrackables.values())

# Wrap the data describing each meal directly from the spreadsheet


class Meal:

    def __init__(self, date, mealName, time, calories, carbs, fat, protein, sodium, sugar):
        self.mealName = mealName
        self.date = date
        self.time = time
        self.calories = calories
        self.carbs = carbs
        self.fat = fat
        self.protein = protein
        self.sodium = sodium
        self.sugar = sugar
