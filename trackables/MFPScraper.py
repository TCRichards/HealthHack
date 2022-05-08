import pandas as pd
import os
from datetime import datetime, timedelta
import myfitnesspal

from util.paths import MFPDataPath as sheetPath

# Get account info
client = myfitnesspal.Client('totothekitty')


# Identifiers for the data I want from MFP
params = ["Carbohydrates", "Sugar", "Fat",  "Protein", "Calories"]


def getMealsFromDate(date):
    thisDaysNutritionData = client.get_date(
        date.strftime('%Y'), date.strftime('%m'), date.strftime('%d'))
    meals = thisDaysNutritionData.meals
    # Don't include any meals that weren't logged, since these contribute nothing
    return [m for m in meals if m.totals != {}]


# Returns an empty dictionary if the meal is not logged
def getNutritionFromMeal(meal):
    # Returns a list of all of the nutritional info gathered from components in the meal
    nutritionValues = meal.totals
    return nutritionValues


def updateSheet():

    # Over which dates are we collecting the data -- pick up where we left off
    startDateString = "06/03/2020"
    date = datetime.strptime(startDateString, "%m/%d/%Y").date()
    today = datetime.now().date()
    assert(date < today)

    meals = []
    mealDates = []
    print('Scraping Data From My Fitness Pal', end='')
    # Pulls measurements from each day
    while date <= today:
        # for param in params:
        todaysMeals = getMealsFromDate(date)
        meals += todaysMeals
        mealDates += [date] * len(todaysMeals)
        # Increment the day that we're looking at
        date += timedelta(days=1)
        print('.', end='')

    # Create the dataframe and add these values to it -- track everything by meal
    nameList = [m.name for m in meals]
    calorieList = [getNutritionFromMeal(m)['calories'] for m in meals]
    fatList = [getNutritionFromMeal(m)['fat'] for m in meals]
    carbList = [getNutritionFromMeal(m)['carbohydrates'] for m in meals]
    proteinList = [getNutritionFromMeal(m)['protein'] for m in meals]
    sodiumList = [getNutritionFromMeal(m)['sodium'] for m in meals]
    sugarList = [getNutritionFromMeal(m)['sugar'] for m in meals]
    timeList = [datetime.strptime('00:00', '%H:%M')] * len(nameList)

    data = {
        'Meal': nameList,
        'Date': mealDates,
        'Time': timeList,
        'Calories': calorieList,
        'Carbohydrates': carbList,
        'Fat': fatList,
        'Protein': proteinList,
        'Sodium': sodiumList,
        'Sugar': sugarList
    }

    print('Done!')
    df = pd.DataFrame(data=data, columns=list(data.keys()))

    try:
        os.remove(sheetPath)
    except FileNotFoundError:
        pass
    finally:
        df.to_csv(sheetPath, index=None)


if __name__ == '__main__':
    updateSheet()
