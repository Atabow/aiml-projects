# Will customer subscribe to term deposit?
Develop machine learning model(s) to predict whether a bank customer will subscribe to a term deposit based on marketing campaign data. Compare the performance of K Nearest Neighbor, Logistic Regression, Decision Trees, and Support Vector Machines classifiers.

#### 📂 Directory Structure

- Base Directory: `bankcd-app3/`  
- Notebook: `bankcd-app3/main.ipynb`  
- Dataset: `bankcd-app3/data/bank-additional-full.csv`  
- Data Info: `bankcd-app3/data/bank-additional-names.txt`


#### 🔍 Data Analysis

**Dataset Overview:**
- **Source:** UCI Machine Learning Repository - Portuguese banking institution marketing campaigns
- **Original Size:** 41,188 rows with 21 attributes
- **Final Clean Dataset:** 32,474 rows post comprehensive data cleaning and feature engineering
- **Campaigns Covered:** 17 campaigns between May 2008 and November 2010

**Target Variable:**
- **Goal:** Predict if client will subscribe to a bank term deposit (`has_subscribed_term_deposit`)
- **Class Distribution:** Imbalanced dataset requiring careful evaluation metrics

**Key Features:**
- **Client Data:** age, job, marital status, education, credit default, housing loan, personal loan
- **Campaign Data:** contact communication type, last contact month/day, campaign contacts
- **Social/Economic Context:** employment variation rate, consumer price index, consumer confidence index
- **Previous Campaign:** number of contacts, days since contact, outcome

#### 🛠️ Data Preprocessing Pipeline

**Missing Data Handling:**
- **Job Type:** 246 missing values (0.76%) - filled with 'missing' category
- **Marital Status:** 60 missing values (0.18%) - filled with 'missing' category  
- **Education Level:** 1,263 missing values (3.89%) - filled with 'missing' category
- **Credit Default:** 6,803 missing values (20.95%) - filled with 'missing' category
- **Housing/Personal Loans:** 781 missing values (2.40%) - filled with 'missing' category
- **Previous Campaign Data:** 28,108 missing values (86.56%) - filled with 0 for contacts, 'missing' for outcome

**Feature Engineering:**
- **Previous Contact Timing Binning:** Categorized days since last contact into meaningful groups (never, 3-7 days, 7+ days)
- **Contact Duration Binning:** Grouped call durations into categories for better pattern recognition
- **Target Encoding:** Converted target variable to binary (0=No, 1=Yes)

**Categorical Features Processing:**
- **Encoding Method:** OneHotEncoder for converting categorical variables to numerical format
- **Missing Value Strategy:** Constant imputation with 'missing' category for interpretability
- **Features:** job_type, marital_status, education_level, has_credit_default, has_housing_loan, has_personal_loan, contact_communication_type, last_contact_month, last_contact_day_of_week, previous_campaign_outcome, previous_contact_timing_bin, last_contact_duration_bin

**Numerical Features Processing:**
- **Scaling Method:** StandardScaler for feature normalization to ensure equal importance across different scales
- **Missing Value Strategy:** Constant imputation with 0 for previous campaign contacts
- **Features:** age, current_campaign_num_contacts, previous_campaign_num_contacts, employment_variation_rate, consumer_price_index, consumer_confidence_index

#### 📊 Model Performance

**Evaluation Methodology:**
- **Primary Metric:** F1 Score (optimal for imbalanced classes and bank marketing use case)
- **Cross-Validation:** 5-fold stratified cross-validation with grid search
- **Train/Test Split:** 80/20 stratified split maintaining class distribution
- **Threshold Optimization:** F1-optimal thresholds determined for each model

**Model Comparison Results:**

| Model | Accuracy | Precision | Recall | F1 Score | AUC-ROC | Training Time (s) |
|-------|----------|-----------|--------|----------|---------|-------------------|
| **Logistic Regression** | 0.890 | 0.422 | **0.652** | **0.512** | 0.833 | 4.60 |
| Decision Tree | 0.892 | 0.424 | 0.603 | 0.498 | 0.829 | 2.86 |
| K-Nearest Neighbors | 0.880 | 0.388 | 0.603 | 0.473 | 0.784 | 283.85 |
| **Support Vector Machine** | **0.895** | **0.433** | 0.600 | 0.503 | 0.826 | 1290.65 |

**Winner: Logistic Regression** ⭐
- **Best F1 Score:** 0.512 (optimal balance of precision and recall)
- **Highest Recall:** 0.652 (captures most potential subscribers)
- **Fast Training:** 4.6 seconds (efficient for production)
- **Good Interpretability:** Feature coefficients provide business insights

**Alternative: Support Vector Machine**
- **Highest Accuracy:** 0.895 and **Precision:** 0.433
- **Best for Cost Control:** Minimizes false positives
- **Trade-off:** Lower recall but higher precision for targeted campaigns
#### 📌 Key Business Insights

**Most Important Predictive Features (Across All Models):**

1. **Employment Variation Rate** (Universal #1 Feature)
   - Economic stability strongly predicts subscription behavior
   - Negative employment variation (job security) increases subscription likelihood

2. **Previous Campaign Success** 
   - Customers with successful previous contacts are highly likely to subscribe again
   - Strong indicator for customer segmentation and targeting

3. **Consumer Confidence Index**
   - Economic sentiment directly impacts financial product adoption
   - Higher confidence correlates with term deposit subscriptions

4. **Contact Timing (Month)**
   - **March contacts** show highest conversion rates
   - **May contacts** show lower performance 
   - Seasonal patterns important for campaign scheduling

5. **Previous Contact Timing**
   - Recent contacts (3-7 days) more effective than longer intervals
   - "Never contacted" customers represent untapped potential

**Marketing Recommendations:**

✅ **Target Timing:** Schedule campaigns in March, August, October, December for best results

✅ **Economic Awareness:** Monitor employment and consumer confidence indicators to time campaigns

✅ **Customer Segmentation:** Prioritize customers with previous successful campaign interactions

✅ **Follow-up Strategy:** Contact prospects within 3-7 days for optimal conversion rates

✅ **Economic Context:** Launch campaigns during stable/improving economic conditions

**Model Deployment Strategy:**
- **Production Model:** Logistic Regression (balanced performance, fast, interpretable)
- **High-Precision Campaigns:** SVM (when minimizing false positives is critical)
- **Monitoring:** Track economic indicators and retrain quarterly
- **A/B Testing:** Compare model predictions against current campaign targeting methods
