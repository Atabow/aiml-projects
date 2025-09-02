# Seattle Crime Data Analysis - Capstone Project

Machine learning analysis of Seattle Police Department crime data with US Census demographics to predict crime volumes and identify key factors influencing criminal activity.

## Key Findings
- **RandomForest model achieved 78.3% variance explained** (R² = 0.783, RMSE = 7.72 crimes)
- **Household income levels** are the top predictor of crime (8.7% feature importance)
- **North Beacon Hill and Pioneer Square** are consistent crime hotspots
- **Socioeconomic factors** outperform geographic factors in predictive power

## Dataset
- **Source**: Seattle PD Crime Data + US Census Demographics (2015-2025)
- **Size**: 726K+ crime records with census tract demographics
- **Features**: 40+ temporal, geographic, and demographic variables

## Model Performance
| Model | Test RMSE | R² Score |
|-------|-----------|----------|
| **RandomForest** | **7.72** | **0.783** |
| Ridge Regression | 12.35 | 0.446 |
| Lasso Regression | 12.35 | 0.446 |
| AdaBoost | 14.48 | 0.239 |

## Getting Started
```bash
pip install -r requirements.txt
jupyter notebook main.ipynb
```

## Files
- `main.ipynb` - Complete analysis notebook
- `data/spd_census_joined.csv` - Combined crime and census data
- `requirements.txt` - Python dependencies

## Key Insights
- **High Crime Areas**: North Beacon Hill, Pioneer Square, Highland Park
- **Low Crime Areas**: Roosevelt/Ravenna, Lakewood/Seward Park, Miller Park
- **Top Predictors**: Income levels, population density, home values
- **Resource Allocation**: Focus on socioeconomic interventions alongside geographic patrols
