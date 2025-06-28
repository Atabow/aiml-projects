# What drives the price of the car?

This project analyzes the `vehicles.csv` dataset, sourced from Kaggle, to understand the key factors that influence used car pricing. The analysis provides actionable insights for used car dealerships to optimize their inventory and pricing strategies.

#### 📂 Directory Structure

- Base Directory: `carprice-app2/`  
- Notebook: `carprice-app2/car_price.ipynb`  
- Dataset: `carprice-app2/data/vehicles.csv`  
- Visualizations: `carprice-app2/images/`

#### 🔍 Data Analysis

**Dataset Overview:**
- **Original Size:** 426,880 vehicles with 18 attributes
- **Final Clean Dataset:** 75,297 vehicles after comprehensive data cleaning
- **Key Features:** Price, age, odometer reading, make, model, condition, fuel type, transmission, drive type, cylinders, and regional data

**Data Preprocessing Highlights:**
- Extracted valuable information from the heterogeneous `model` column to fill missing values
- Implemented sophisticated outlier detection and removal (5th-95th percentile filtering)
- Advanced categorical imputation using mode-based grouping strategies
- Feature engineering: converted year to age, extracted numeric cylinders, combined state-region data
- Removed duplicate VINs and handled missing values systematically

**Modeling Approach:**
- **Algorithms:** Ridge and Lasso Regression with polynomial features (degree 2)
- **Target Transformation:** Log10 transformation for better model performance
- **Validation:** 90/10 train-test split with grid search optimization
- **Features:** 8 categorical variables (one-hot encoded) + 3 numerical variables

#### 🛠️ Data Preprocessing Pipeline

**Categorical Features Processing:**
- **Encoding Method:** OneHotEncoder for converting categorical variables to numerical format
- **Missing Value Imputation:** SimpleImputer with constant fill strategy for handling missing categorical values
- **Features Processed:** make, model, condition, cylinders, fuel, title_status, transmission, drive, type, paint_color, state

**Numerical Features Processing:**
- **Scaling Method:** StandardScaler for feature normalization to ensure equal importance across different scales
- **Missing Value Imputation:** SimpleImputer with constant fill strategy for handling missing numerical values
- **Features Processed:** age, odometer, price (target variable)

**Feature Engineering:**
- **Polynomial Features:** Applied polynomial transformation with degree 2 to capture non-linear relationships
- **Feature Interaction:** Second-degree polynomial features enable the model to learn complex interactions between variables
- **Dimensionality:** Enhanced feature space allows for better model accuracy and pattern recognition

#### 📊 Model Performance

**Both Ridge and Lasso achieved excellent results:**
- **RMSE:** ~$4,990 (Root Mean Square Error)
- **R²:** 67.1-67.2% (variance explained)
- **MAE:** ~$3,485 (Mean Absolute Error)
- **Model Calibration:** Well-balanced with no systematic bias

**Key Performance Insights:**
- 68% of predictions fall within ±$4,950 of actual price
- 95% of predictions fall within ±$9,900 of actual price
- Strong generalization with minimal overfitting

#### 📊 Visualizations

Visual outputs from the analysis are stored in the `images/` directory. These visualizations highlight:
- **Price Trends:** Age vs average price relationships across different vehicle attributes
- **Feature Importance:** Coefficient analysis showing impact of various factors
- **Distribution Analysis:** Patterns and trends in key pricing variables
- **Model Validation:** Actual vs predicted price scatter plots and residual analysis

#### 📌 Key Business Insights

**🔍 Major Price Drivers Identified:**

**📉 Depreciation Factors (Price Decreasing):**
- **Vehicle Age:** Most significant factor - each additional year reduces value substantially
- **High Mileage:** Strong negative correlation (-0.55) with price
- **Manufacturer Impact:** Dodge, Chrysler, and Nissan models show lower market values
- **Missing Condition Data:** Vehicles without condition information suffer price penalties
- **Automatic Transmission:** Counterintuitively valued less probably due to insufficient data in the dataset

**📈 Value Enhancement Factors (Price Increasing):**
- **Premium Manufacturers:** Toyota, Kia, Cadillac, and especially Lexus command higher prices
- **Vehicle Type:** Pickup trucks show significant price premiums
- **Drivetrain:** 4WD and RWD vehicles valued higher than FWD
- **Engine Size:** More cylinders correlate with higher prices (polynomial relationship)
- **Condition Status:** "Excellent" condition and "Clean" title significantly boost value
- **Regional Variations:** Hawaii and Alaska show positive price effects

**🎯 Strategic Recommendations for Used Car Dealers:**

**1. Inventory Optimization:**
- **Focus on Low-Mileage Vehicles:** Target cars under 90,000 miles for best profit margins
- **Age Sweet Spot:** Vehicles 5-12 years old offer optimal balance of affordability and value retention
- **Preferred Brands:** Prioritize Toyota, Kia, Lexus, and Cadillac in acquisition strategies
- **Vehicle Types:** Pickup trucks and SUVs consistently outperform sedans in pricing

**2. Pricing Strategy:**
- **Age Adjustment:** Apply aggressive age-based depreciation curves in pricing models
- **Mileage Penalties:** Implement clear mileage-based discounting (especially >100k miles)
- **Condition Premium:** Vehicles in "excellent" condition can command 15-25% price premiums
- **Regional Pricing:** Adjust pricing based on local market conditions and regional preferences

**3. Market Positioning:**
- **Avoid High-Depreciation Brands:** Be cautious with Dodge, Chrysler, and Nissan inventory
- **Feature Emphasis:** Highlight 4WD/AWD capabilities and higher cylinder counts in marketing

**4. Risk Management:**
- **Documentation Quality:** Ensure complete condition assessments to avoid "missing data" penalties
- **Title Verification:** Prioritize vehicles with clean titles; avoid salvage/rebuilt titles
- **Mileage Verification:** Implement strict odometer verification processes

**📊 Statistical Validation:**
- **Model Accuracy:** 67% of price variation explained by key factors
- **Prediction Reliability:** Average prediction error of ±$3,500
- **Business Impact:** Clear actionable insights for inventory decisions worth thousands per vehicle

**Note:** For detailed technical analysis including **data cleaning methodology, feature engineering techniques, Ridge and Lasso regression implementation, and comprehensive model evaluation**, please refer to the Jupyter notebook `car_price.ipynb`.

