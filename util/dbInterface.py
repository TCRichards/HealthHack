from datetime import datetime
import os
from util.paths import dataDir


class DBInterface:

    @staticmethod
    def append_df_to_csv(filename, df):
        DBInterface.initializeFile(filename)
        df.to_csv(filename, mode='a', header=None, index=None)

    @staticmethod
    # @brief ensure that the data directory and category-specific directories for the file exist
    def initializeFile(filename):
        if not os.path.exists(dataDir):
            os.mkdir(dataDir)       # Create rawData/
        if not os.path.exists(os.path.dirname(filename)):
            # Create file at rawData/category
            os.mkdir(os.path.dirname(filename))

    # @brief stores the processed data for the given trackable in the file specified by savePath
    @staticmethod
    def saveTrackable(trackable, savePath):
        # For now, don't support saving times since this gets corruped in procesed data anyway
        trackable.processedData['Score'].to_csv(savePath, mode='w', index_label='Date')

    # @brief Forces all the entries to in a list that may consist of a combination of strings and datetime objects to be datetime objects
    # thanks to Excel's auto-casting to be all datetime objects
    @staticmethod
    def convertToDateTime(val, fmt):
        try:
            output = datetime.strptime(val, fmt)
            return output
        except TypeError:
            try:
                if fmt == '%H:%M':
                    output = datetime.strptime(
                        val.strftime('%H:%M'), '%H:%M').time()
                else:
                    output = val
            except AttributeError:
                output = val
            return output

    @staticmethod
    def makeListDateTimes(dtList, fmt):
        for i in range(len(dtList)):
            try:
                dtList[i] = datetime.strptime(dtList[i], fmt)
            except TypeError:
                # In case Excel made it a datetime object instead of datetime.datetime
                try:
                    if fmt == '%H:%M':
                        dtList[i] = datetime.strptime(
                            dtList[i].strftime('%H:%M'), '%H:%M')
                except AttributeError:
                    pass
