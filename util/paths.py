import os
from pathlib import Path

# Define lots of paths to data files
utilDir = os.path.dirname(__file__)
projDir = Path(utilDir).parent
dataDir = os.path.join(projDir, 'rawData')
processedDataDir = os.path.join(projDir, 'processedData')
integrationDir = os.path.join(dataDir, 'integrations')

habitDataPath = os.path.join(integrationDir, 'habitBullData.csv')
MFPDataPath = os.path.join(integrationDir, 'MFPData.csv')
settingsPath = os.path.join(utilDir, 'settings.JSON')
imgPath = os.path.join(projDir, 'images')
