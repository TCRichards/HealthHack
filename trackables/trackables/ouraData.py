"""
Utility class that handles reading data from the Oura JSON file
Stores conversions and methods for interfacing with Oura data directly
"""
from trackables.variableCategories.trackType import TrackType
import trackables.trackables.trackableFactories as factories
from util.paths import integrationDir

import os
from datetime import datetime
import json
import pandas as pd
import numpy as np


# Documentation on the API found at: https://cloud.ouraring.com/docs/
class Oura:  # Make this class a singleton to avoid unecessary painful reloading of JSON data
    __instance = None

    @staticmethod
    def instance():
        if Oura.__instance is None:
            Oura()
        return Oura.__instance

    def __init__(self):
        if Oura.__instance is not None:
            raise Exception("Oura Ring is not to be instantiated externally!")
        else:
            Oura.__instance = self

        self.data = self.loadJSON()
        self.readinessTrackables = None
        self.sleepTrackables = None
        self.activityTrackables = None
        (
            self.readinessNameDict,
            self.sleepNameDict,
            self.activityNameDict,
        ) = self.createShorthandDicts()
        (
            self.readinessTypeDict,
            self.sleepTypeDict,
            self.activityTypeDict,
        ) = self.createOuraTypeDicts()

    # Creates Trackables for all the scores associated with 'readiness'
    def createReadinessTrackables(self):
        return self.createGenericTrackables("readiness")

    def createSleepTrackables(self):
        return self.createGenericTrackables("sleep")

    def createActivityTrackables(self):
        return self.createGenericTrackables("activity")

    # Getter functions that delay the loading of oura data until explicitly called
    def getReadinessTrackables(self):
        if self.readinessTrackables in (None, []):
            self.readinessTrackables = self.createReadinessTrackables()
        return self.readinessTrackables

    def getSleepTrackables(self):
        if self.sleepTrackables in (None, []):
            self.sleepTrackables = self.createSleepTrackables()
        return self.sleepTrackables

    def getActivityTrackables(self):
        if self.activityTrackables in (None, []):
            self.activityTrackables = self.createActivityTrackables()
        return self.activityTrackables

    # Allows access to the Oura's trackables using only a string identifier
    def getTrackablesOfCategory(self, category):
        if category == "readiness":
            return self.getReadinessTrackables()
        elif category == "sleep":
            return self.getSleepTrackables()
        elif category == "activity":
            return self.getActivityTrackables()
        return []  # Default to an empty list

    def getAllTrackables(self):
        return (
            self.getReadinessTrackables()
            + self.getSleepTrackables()
            + self.getActivityTrackables()
        )

    # Loads data from the JSON coresponding to the given category and returns a list of Trackables
    def createGenericTrackables(self, category):
        if self.data is None:
            return []

        entries = self.data[category]
        # One trackable for each datapoint except 'period_id' and 'summary_date'
        # Use most recent measurement because some parameters are not included early
        df = pd.DataFrame(data=entries)
        df = df.rename(columns={"summary_date": "Date"})
        # Convert from string dates to datetime objects
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
        df.set_index("Date", inplace=True)
        trackables = []

        for name in df.columns:
            if name != "period_id":
                prettyName = self.shorthandToName(category, name)

                # If we're not supporting the trackable (yet)
                if prettyName is None:
                    continue

                newDf = df[name].rename("Score").to_frame()
                newTrackable = factories.OuraFactory.create(
                    prettyName,
                    category,
                    newDf,
                )
                if newTrackable is not None:
                    trackables.append(newTrackable)

        return trackables

    def getOuraTypeFromName(self, category, name):
        if category == "readiness":
            return self.readinessTypeDict[name]
        if category == "sleep":
            return self.sleepTypeDict[name]
        if category == "activity":
            return self.activityTypeDict[name]

    # Fetches data about the given field from the master JSON and returns its value over a range of dates
    def getDataField(self, category, field):
        dates = []
        scores = []

        for entry in self.data[category]:
            try:
                scores.append(entry[field])
            except KeyError:
                raise KeyError(
                    field + "is is not a valid field name for readiness data"
                )
            dates.append(entry["summary_date"])
        return dates, np.array(scores)

    def loadJSON(self):
        dataPath = self.findMostRecentOuraJSON()
        if dataPath is None:
            return None
        with open(dataPath, "r") as read_file:
            data = json.load(read_file)
            return data

    def ouraJSONExists(self):
        return self.findMostRecentOuraJSON() is not None

    # Looks through all the Oura JSONs in the integrationDir and returns the path to the newest one
    def findMostRecentOuraJSON(self):
        dirFiles = os.listdir(integrationDir)
        ouraFiles = [f for f in dirFiles if "oura" in f and ".json" in f]
        # Remove any files that look like oura JSONs but don't contain valid dates in name
        for f in ouraFiles:
            try:
                datetime.strptime(
                    f[5:15], "%Y-%m-%d"
                )  # Will raise ValueError if invalid
            except ValueError:
                ouraFiles.remove(f)
                print(
                    'Invalid JSON file for Oura Ring data found: {}\n'
                    'Make sure the name of this file is in the allowed format'.format(f)
                )

        if len(ouraFiles) == 0:
            print('No Valid Oura Ring JSON Files Found')
            return None
        relativePath = max(
            ouraFiles, key=lambda file: datetime.strptime(file[5:15], "%Y-%m-%d")
        )
        return os.path.join(integrationDir, relativePath)

    def shorthandToName(self, category, abbrev):
        try:
            if category == "readiness":
                return self.readinessNameDict[abbrev]
            elif category == "sleep":
                return self.sleepNameDict[abbrev]
            elif category == "activity":
                return self.activityNameDict[abbrev]
        except KeyError:
            return None

    # Converts long trackable name to Oura Shorthand
    def nameToShorthand(self, name):
        for d in (self.readinessNameDict, self.sleepNameDict, self.activityNameDict):
            for key, value in d:
                if value == name:
                    return key
        raise ValueError("Oura Trackable '{}' has no translation")

    # ================================= Metadata To Add to Oura API Results =====================
    # Create a dictionary that can translate from Oura Ring's abbreviated names to longer names and back
    def createShorthandDicts(self):

        readinessDict = {
            "score": "Readiness Score",
            "score_previous_night": "Readiness Score Factor: Previous Night's Sleep",
            "score_sleep_balance": "Readiness Score Factor: Sleep Balance",
            "score_previous_day": "Readiness Score Factor: Previous Day's Score",
            "score_activity_balance": "Readiness Score Factor: Activity Balance",
            "score_resting_hr": "Readiness Score Factor: Resting HR",
            "score_hrv_balance": "Readiness Score Factor: HRV Balance",
            "score_recovery_index": "Readiness Score Factor: Recovery Index",
            "score_temperature": "Readiness Score Factor: Temperature",
            "rest_mode_state": "Rest Mode State",
        }

        sleepDict = {
            "bedtime_start": "Bedtime",
            "bedtime_end": "Wake-Up Time",
            "duration": "Sleep Duration",
            "total": "Total Sleep",
            "awake": "Time Awake",
            "rem": "Time in REM Sleep",
            "light": "Time in Light Sleep",
            "deep": "Time in Deep Sleep",
            "restless": "Time in Restless Sleep",
            "hr_lowest": "Lowest Sleeping Heart Rate",
            "hr_average": "Average Sleeping Heart Rate",
            "hr_5min": "5-Minute Averaged Heart Rate",
            "efficiency": "Sleep Efficiency",
            "onset_latency": "Sleep Onset Latency",
            "midpoint_time": "Sleep Midpoint Time",
            "temperature_delta": "Sleeping Temperature Delta",
            "temperature_deviation": "Sleeping Temperature Deviation",
            "temperature_trend_deviation": "Sleeping Temperature Deviation From Trend",
            "breath_average": "Average Sleeping Breath Rate",
            "score": "Sleep Score",
            "score_total": "Sleep Score Factor: Total Sleep",
            "score_rem": "Sleep Score Factor: REM Sleep",
            "score_deep": "Sleep Score Factor: Deep Sleep",
            "score_efficiency": "Sleep Score Factor: Efficiency",
            "score_latency": "Sleep Score Factor: Latency",
            "score_disturbances": "Sleep Score Factor: Disturbances",
            "score_alignment": "Sleep Score Factor: Circadian Alignment",
            "rmssd": "Average HRV From rMSSD",
            "hypnogram_5min": "5-Minute hypnogram",
            "rmssd_5min": "5-Minute-Averaged HRV from rMSSD",
            # Categories that either don't appear in documentation, that don't make sense to track,
            # or that currently don't have support
            # 'bedtime_end_delta': 'Wake-Up Time Delta',
            # 'bedtime_start_delta': 'Bedtime Delta',
            # 'is_longest': 'Is Longest?',
            # 'midpoint_at_delta': 'Midpoint AT Delta',
            # 'timezone': 'Timezone'
        }

        activityDict = {
            "score": "Activity Score",
            "score_stay_active": "Activity Score Factor: Stay Active",
            "score_move_every_hour": "Activity Score Factor: Move Every Hour",
            "score_meet_daily_targets": "Activity Score Factor: Meet Daily Targets",
            "score_training_frequency": "Activity Score Factor: Training Frequency",
            "score_training_volume": "Activity Score Factor: Training Volume",
            "score_recovery_time": "Activity Score Factor: Recovery Time",
            "daily_movement": "Daily Movement Equivalent in Meters",
            "non_wear": "Minutes With Ring Off",
            "rest": "Minutes Resting",
            "inactive": "Minutes Inactive",
            "inactivity_alerts": "Number of Inactivity Alerts",
            "low": "Minutes of Low Intensity Exercise",
            "medium": "Minutes of Medium Intensity Exercise",
            "high": "Minutes of High Intensity Exercise",
            "steps": "Number of Steps",
            "cal_total": "Total Calories Burned",
            "cal_active": "Active Calories Burned",
            "target_calories": "Target Calorie Burn",
            "target_km": "Target Distance (km)",
            "target_miles": "Target Distance (miles)",
            "to_target_km": "Deviation From Target Distance (km)",
            "to_target_miles": "Deviation From Target Distnace (miles)",
            "to_target_calories": "Deviation From Target Calorie Burn",
            "met_min_inactive": "MET Minutes for Inactive Time",
            "met_min_low": "MET Minutes for Low Intensity Exercise",
            "met_min_medium": "MET Minutes for Medium Intensity Exercise",
            "met_min_medium_plus": "MET Minutes for Medium and High Intensity Exercise",
            "met_min_high": "MET Minutes for High Intensity Exercise",
            "average_met": "Average MET",
            "total": "Total Active Time",
            "class_5min": "5-Minute Activity Classification",
            # This is just a constant 4 AM -- no fun to track
            # 'day_start': 'Activity Day Starting Time',
            # 'day_end': 'Activity Day Ending Time',
            # 'timezone': 'Timezone'
            # 'met_1min': '1-Minute MET Levels',
        }
        return readinessDict, sleepDict, activityDict

    # Create a dictionary that stores the type of each trackable
    def createOuraTypeDicts(self):

        readinessDict = {
            "Readiness Score": TrackType.CONTINUOUS,
            "Readiness Score Factor: Previous Night's Sleep": TrackType.CONTINUOUS,
            "Readiness Score Factor: Sleep Balance": TrackType.CONTINUOUS,
            "Readiness Score Factor: Previous Day's Score": TrackType.CONTINUOUS,
            "Readiness Score Factor: Activity Balance": TrackType.CONTINUOUS,
            "Readiness Score Factor: Resting HR": TrackType.CONTINUOUS,
            "Readiness Score Factor: HRV Balance": TrackType.CONTINUOUS,
            "Readiness Score Factor: Recovery Index": TrackType.CONTINUOUS,
            "Readiness Score Factor: Temperature": TrackType.CONTINUOUS,
            "Rest Mode State": TrackType.CONTINUOUS,
        }

        sleepDict = {
            # Sleep
            "Bedtime": TrackType.TIME,
            "Wake-Up Time": TrackType.TIME,
            "Sleep Duration": TrackType.DURATION,
            "Total Sleep": TrackType.DURATION,
            "Time Awake": TrackType.DURATION,
            "Time in REM Sleep": TrackType.DURATION,
            "Time in Light Sleep": TrackType.DURATION,
            "Time in Deep Sleep": TrackType.DURATION,
            "Time in Restless Sleep": TrackType.DURATION,
            "Lowest Sleeping Heart Rate": TrackType.CONTINUOUS,
            "Average Sleeping Heart Rate": TrackType.CONTINUOUS,
            "5-Minute Averaged Heart Rate": TrackType.CONTINUOUS_5_MIN_WINDOW,
            "Sleep Efficiency": TrackType.CONTINUOUS,
            "Sleep Onset Latency": TrackType.CONTINUOUS,
            "Sleep Midpoint Time": TrackType.DURATION,
            "Sleeping Temperature Delta": TrackType.CONTINUOUS,
            "Sleeping Temperature Deviation": TrackType.CONTINUOUS,
            "Sleeping Temperature Deviation From Trend": TrackType.CONTINUOUS,
            "Average Sleeping Breath Rate": TrackType.CONTINUOUS,
            "Sleep Score": TrackType.CONTINUOUS,
            "Sleep Score Factor: Total Sleep": TrackType.CONTINUOUS,
            "Sleep Score Factor: REM Sleep": TrackType.CONTINUOUS,
            "Sleep Score Factor: Deep Sleep": TrackType.CONTINUOUS,
            "Sleep Score Factor: Efficiency": TrackType.CONTINUOUS,
            "Sleep Score Factor: Latency": TrackType.CONTINUOUS,
            "Sleep Score Factor: Disturbances": TrackType.CONTINUOUS,
            "Sleep Score Factor: Circadian Alignment": TrackType.CONTINUOUS,
            "Average HRV From rMSSD": TrackType.CONTINUOUS,
            "5-Minute hypnogram": TrackType.HYPNOGRAM,
            "5-Minute-Averaged HRV from rMSSD": TrackType.CONTINUOUS_5_MIN_WINDOW,
        }

        activityDict = {
            "Activity Score": "Activity Score",
            "Activity Score Factor: Stay Active": TrackType.CONTINUOUS,
            "Activity Score Factor: Move Every Hour": TrackType.CONTINUOUS,
            "Activity Score Factor: Meet Daily Targets": TrackType.CONTINUOUS,
            "Activity Score Factor: Training Frequency": TrackType.CONTINUOUS,
            "Activity Score Factor: Training Volume": TrackType.CONTINUOUS,
            "Activity Score Factor: Recovery Time": TrackType.CONTINUOUS,
            "Daily Movement Equivalent in Meters": TrackType.CONTINUOUS,
            "Minutes With Ring Off": TrackType.CONTINUOUS,
            "Minutes Resting": TrackType.CONTINUOUS,
            "Minutes Inactive": TrackType.CONTINUOUS,
            "Number of Inactivity Alerts": TrackType.CONTINUOUS,
            "Minutes of Low Intensity Exercise": TrackType.CONTINUOUS,
            "Minutes of Medium Intensity Exercise": TrackType.CONTINUOUS,
            "Minutes of High Intensity Exercise": TrackType.CONTINUOUS,
            "Number of Steps": TrackType.CONTINUOUS,
            "Total Calories Burned": TrackType.CONTINUOUS,
            "Active Calories Burned": TrackType.CONTINUOUS,
            "Target Calorie Burn": TrackType.CONTINUOUS,
            "Target Distance (km)": TrackType.CONTINUOUS,
            "Target Distance (miles)": TrackType.CONTINUOUS,
            "Deviation From Target Distance (km)": TrackType.CONTINUOUS,
            "Deviation From Target Distnace (miles)": TrackType.CONTINUOUS,
            "Deviation From Target Calorie Burn": TrackType.CONTINUOUS,
            "MET Minutes for Inactive Time": TrackType.CONTINUOUS,
            "MET Minutes for Low Intensity Exercise": TrackType.CONTINUOUS,
            "MET Minutes for Medium Intensity Exercise": TrackType.CONTINUOUS,
            "MET Minutes for Medium and High Intensity Exercise": TrackType.CONTINUOUS,
            "MET Minutes for High Intensity Exercise": TrackType.CONTINUOUS,
            "Average MET": TrackType.CONTINUOUS,
            "Total Active Time": TrackType.CONTINUOUS,
            "5-Minute Activity Classification": TrackType.CONTINUOUS_5_MIN_WINDOW,
        }

        return readinessDict, sleepDict, activityDict


if __name__ == "__main__":
    print(Oura.instance().shorthandToName("readiness", "score"))
    print(Oura.instance().nameToShorthand("Readiness Score"))
