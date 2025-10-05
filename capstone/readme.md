## Seattle Crime Data Analysis and Prediction

### Executive summary

**Project overview and goals:** The goal of this project is to develop a predictive model for crime volumes in Seattle neighborhoods by analyzing Seattle Police Department crime data combined with US Census demographics. We trained and evaluated six machine learning regression models to accurately predict monthly crime counts across Seattle neighborhoods, enabling law enforcement agencies to optimize resource allocation and implement targeted crime prevention strategies. Models predict future crime volumes based on socioeconomic, demographic, and geographic factors. We evaluated and compared the models' performances to identify the best one, then conducted feature importance analysis to understand the key factors driving crime predictions. Through both global and local analyses, we identified the most significant predictors and generated actionable insights for law enforcement and community intervention programs.

**Findings:** The best model for predicting Seattle crime volumes is the XGBoost Regressor, achieving an R² score of 0.815 (81.5% variance explained) with an RMSE of 7.57 crimes per month per neighborhood. This model significantly outperformed other algorithms including GradientBoosting (R² = 0.802), RandomForest (R² = 0.789), Lasso Regression (R² = 0.424), Ridge Regression (R² = 0.422), AdaBoost (R² = 0.234), and Dummy Baseline (R² = -0.003). The XGBoost model demonstrated excellent performance and robustness, indicating high reliability for crime prediction tasks.

**Results and conclusion:** Feature importance analysis revealed that specific geographic locations are the strongest predictors of crime volume. The top five predictive features from the XGBoost model are: Pioneer Square neighborhood (16.3% importance), North Beacon Hill neighborhood (7.1% importance), Unknown location category (6.3% importance), Police Sector G (5.9% importance), and Population Density bins (4.4% importance). Geographic analysis identified North Beacon Hill, Pioneer Square, and First Hill as the highest crime areas, while Roosevelt/Ravenna and Lakewood/Seward Park maintain consistently low crime rates. The model successfully captures seasonal patterns and temporal trends in crime activity.

This study demonstrates that specific geographic locations (neighborhoods and police sectors) are the primary drivers of crime prediction, with socioeconomic factors like population density also playing important roles. The analysis revealed consistent crime hotspots including Pioneer Square, North Beacon Hill, and specific police administrative zones like Sector G, indicating that location-based factors are critical for accurate crime forecasting.

**Next steps and recommendations:** We recommend implementing a real-time crime prediction system using our XGBoost model for monthly resource allocation. Law enforcement should focus 40% of patrol resources on the top 10 predicted neighborhoods and increase afternoon patrols by 25%. Community intervention programs should target economic development in low-income areas, support homeownership initiatives in rental-heavy neighborhoods, and establish youth programs in identified hotspots. A phased implementation over 12 months should begin with predictive monitoring, followed by resource reallocation and community intervention programs.

### Rationale

The problem this project addresses is the growing need for effective crime prevention and resource allocation in urban areas. In Seattle, crime patterns vary significantly across neighborhoods, with some areas experiencing crime rates substantially higher than others. Traditional reactive policing approaches often result in inefficient resource deployment and missed opportunities for prevention.

Crime can be prevented through targeted interventions, and the first step to effective prevention is accurately predicting where and when crimes are most likely to occur based on underlying socioeconomic and demographic factors.

### Research Question

The question this project aims to answer is: What is the best machine learning model for predicting monthly crime volumes in Seattle neighborhoods, and what are the most important socioeconomic and demographic factors that influence crime patterns?

### Data Sources

**Dataset:** The dataset used in this project combines Seattle Police Department crime data with US Census demographic information, covering the period from 2018-2024.

The crime data contains 726,885 individual crime incidents collected from Seattle PD records, including geographic coordinates, offense types, timestamps, and neighborhood classifications. Each incident includes latitude/longitude coordinates, allowing for precise geographic analysis. The demographic data from US Census provides neighborhood-level statistics on income, housing, population density, and racial composition.

**Exploratory data analysis:** The dataset shows consistent temporal patterns with approximately 10,000 crimes per month. Crime distribution is heavily concentrated in downtown and southern neighborhoods, with North Beacon Hill, Pioneer Square, and First Hill showing the highest incident counts. Property crimes (theft, burglary) comprise approximately 60% of all incidents, while violent crimes are more evenly distributed across demographics. Mean monthly crime count per neighborhood is 85.4, with a range from 12 to 247 crimes per month.

**Cleaning and preparation:** Missing geographic coordinates were handled through data imputation and removal of incomplete records, resulting in 97.9% data completeness. Neighborhood boundaries were standardized, and census tract data was aggregated to match neighborhood classifications. Temporal features were engineered including month, season, and year indicators.

**Preprocessing:** Feature engineering created demographic bins for income levels, population density categories, and housing value ranges. Ordinal encoding was applied to categorical demographic variables, while numerical features were standardized using scikit-learn's preprocessing pipeline.

**Final Dataset:** The final dataset aggregates monthly crime counts by neighborhood with corresponding demographic features, resulting in 45+ predictor variables including temporal, geographic, and socioeconomic factors. The target variable represents monthly crime counts per neighborhood, suitable for regression modeling. The data shows balanced representation across neighborhoods and time periods.

## Data Visualization and Analysis

### Crime Volume Distribution Analysis
<img src="images/CrimeVolumeInsights.png" alt="Crime Volume Insights" width="1200">

*Comprehensive analysis of Seattle crime patterns showing temporal trends, geographic hotspots, demographic correlations, and seasonal variations across neighborhoods, precincts, and police sectors.*

### Crime Predictions and Forecasting
<img src="images/crime_prediction.png" alt="Crime Prediction" width="1200">

*12-month crime forecasts using the best-performing model, including citywide trends, neighborhood rankings, and precinct-level resource allocation planning.*

<img src="images/seattle_crime_forcast_areas.jpg" alt="Crime Areas" width="600">

### Methodology

Holdout cross-validation was implemented with an 80/20 train-test split. Models were trained on the training set and validated using both 5-fold cross-validation and holdout testing. GridSearchCV was used to optimize hyperparameters for each model, maximizing R score as the primary metric. R score is appropriate for this regression task as it measures the proportion of variance in crime counts explained by the model, calculated as:

R = 1 - (SS_residual / SS_total)

Six regression models were trained, fine-tuned, and compared:

**RandomForest Regressor:** A pipeline with standard scaling and RandomForest regression. GridSearchCV optimized n_estimators (50-200), max_depth (10-20), and min_samples_split (2-10). Best parameters: 100 estimators, max_depth=15, min_samples_split=5.

**XGBoost Regressor:** Pipeline with XGBoost gradient boosting. Hyperparameter tuning for learning_rate (0.01-0.3), n_estimators (100-300), and max_depth (3-10). Best model achieved strong performance with learning_rate=0.1.

**Ridge Regression:** L2 regularized linear regression with alpha tuning from 0.1 to 100. Cross-validation selected optimal regularization strength to prevent overfitting.

**Lasso Regression:** L1 regularized regression for feature selection. Alpha parameter tuned to balance feature selection and prediction accuracy.

**AdaBoost Regressor:** Ensemble method with decision tree base estimators. Tuned n_estimators and learning_rate for optimal boost performance.

**Linear Regression:** Baseline model using ordinary least squares for comparison with more complex algorithms.

### Model evaluation and results

Model performance was evaluated using R score, RMSE, and cross-validation stability. Results are visualized through residual plots and feature importance analysis.

**XGBoost Regressor:** The XGBoost model is the best model for predicting Seattle crime volumes, with an R² score of 0.815, RMSE of 7.57, demonstrating exceptional performance in capturing crime patterns. This model explains 81.5% of the variance in monthly crime counts and demonstrates excellent stability and accuracy. The model effectively handles non-linear relationships and provides reliable feature importance rankings for understanding key crime drivers.

**GradientBoosting Regressor:** The GradientBoosting model achieved the second-best performance with R² = 0.802 and RMSE = 7.84. This sequential boosting algorithm corrects previous errors effectively, offering strong predictive power and good feature importance interpretability.

**RandomForest Regressor:** The RandomForest model achieved the third-best performance with R² = 0.789 and RMSE = 8.09. While slightly less accurate than the gradient boosting models, it offers good interpretability and ensemble robustness through multiple decision trees. Training time was efficient, making it practical for regular retraining.

**Lasso Regression:** Lasso achieved R² = 0.424 and RMSE = 13.36 while providing automatic feature selection. It identified the most important predictive features by setting less important coefficients to zero, making it valuable for feature selection insights.

**Ridge Regression:** Ridge regression provided a fast baseline with R² = 0.422 and RMSE = 13.38. Despite lower predictive power, it offers good interpretability and trains quickly, making it suitable for rapid prototyping.

**AdaBoost Regressor:** AdaBoost showed limited effectiveness with R² = 0.234 and RMSE = 15.41. This adaptive boosting algorithm failed to capture the complex relationships in the crime data effectively compared to other ensemble methods.

**Dummy Baseline:** The dummy baseline model achieved R² = -0.003 and RMSE = 17.64, simply predicting the mean crime count for all cases. This confirms that more sophisticated models are necessary for meaningful crime prediction.

## Model Performance Visualizations

### RMSE Comparison Across Models
<img src="images/rmse_comparison.png" alt="RMSE Comparison" width="1100">

*Training vs Test RMSE comparison across all machine learning models, showing model generalization performance and overfitting detection.*

### Actual vs Predicted Performance

#### Dummy Baseline Model
<img src="images/actual_vs_predicted_Dummy_Baseline.png" alt="Dummy Baseline Results" width="1000">

#### Ridge Regression Model  
<img src="images/actual_vs_predicted_Ridge_Regression.png" alt="Ridge Regression Results" width="1000">

#### Lasso Regression Model
<img src="images/actual_vs_predicted_Lasso_Regression.png" alt="Lasso Regression Results" width="1000">

#### Random Forest Model
<img src="images/actual_vs_predicted_RandomForest.png" alt="Random Forest Results" width="1000">

#### Gradient Boosting Model
<img src="images/actual_vs_predicted_GradientBoosting.png" alt="Gradient Boosting Results" width="1000">

#### XGBoost Model
<img src="images/actual_vs_predicted_XGBoost.png" alt="XGBoost Results" width="1000">

#### AdaBoost Model
<img src="images/actual_vs_predicted_AdaBoost.png" alt="AdaBoost Results" width="1000">

### Feature Importance Analysis

#### Ridge Regression Feature Importance
<img src="images/feature_importance_Ridge_Regression.png" alt="Ridge Feature Importance" width="1000">

#### Lasso Regression Feature Importance  
<img src="images/feature_importance_Lasso_Regression.png" alt="Lasso Feature Importance" width="1000">

#### Random Forest Feature Importance
<img src="images/feature_importance_RandomForest.png" alt="Random Forest Feature Importance" width="1000">

#### Gradient Boosting Feature Importance
<img src="images/feature_importance_GradientBoosting.png" alt="Gradient Boosting Feature Importance" width="1000">

#### XGBoost Feature Importance
<img src="images/feature_importance_XGBoost.png" alt="XGBoost Feature Importance" width="1000">

#### AdaBoost Feature Importance
<img src="images/feature_importance_AdaBoost.png" alt="AdaBoost Feature Importance" width="1000">

### Outline of project

main.ipynb - Complete analysis notebook with data preprocessing, model training, evaluation, and interactive Seattle crime hotspot map

data/spd_census_joined.csv - Combined Seattle crime and census demographic data (726K+ records)


equirements.txt - Python dependencies including scikit-learn, pandas, folium, matplotlib

images/ - Generated visualizations including crime prediction charts, neighborhood analysis, and model performance comparisons

