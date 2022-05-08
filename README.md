# TrackMe Health Dashboard

## Goal
To develop a desktop application capable of logging data and pulling data from different sources.  These different sources of data can then be cleaned and analyzed to find insights across sources that no single app supports.

## Currently Support Data Sources
1. Data Manually Logged Within the App
2. Oura Ring
3. MyFitnessPal
4. HabitBull

This Python-based desktop app allows users to automate health data logging and analysis.

Currently supports logging a variety of data types, and integrating data from Oura Ring, MyFitnessPal, and HabitBull.


## Setup Instructions
Still Under Development

## Screenshots

The home page controls what kind of data can be tracked and analyzed.  It's easy to add a new category of data for manual entry.
![image](./images/addCategory.png)

Once a category is created, multiple variables can be added.
![image](./images/addSupplement.png)

A simple GUI enables logging the relevant entries for each type of data
![image](./images/logData.png)

The fun begins once data is collected.  The analysis dashboard provides a level of control over your data that no health app will give you directly.  Plot up to two data sources side-by-side and run various statistical tests to find correlations and causality.

![image](./images/analysisDashboard.png)

This dashboard can also be used to clean data in a variety of different ways.  The cleaned data can be output to CSV for your own purposes.

Forgot to wear your fitness tracker during sleep?  Control how missing data is handled across all sources by excluding it or filling with the most reasonable values.

The above example shows that I can be reasonably sure that taking glutathione does not impact by sleep quality. Now I know! 