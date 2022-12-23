# Customer Segmentation Report for Arvato Financial Services
Capstone project for Udacity data scientist nanodegree program

## Project Description
This is a capstone project for the Udacity data science nanodegree program.

In this project, these steps will be performed:

1. analyze demographics data for customers of a mail-order sales company in Germany, comparing it against demographics information for the general population, and identifying the parts of the population that best describe the core customer base of the company.
2. apply what I've learned on a third dataset with demographics information for targets of a marketing campaign for the company, and use a model to predict which individuals are most likely to convert into becoming customers for the company.

There are four sections in this project:
  1. Get to know the data
  2. Customer segmentation report
  3. Supervised learning model
  4. Conclusion

## Dataset
There are four data files associated with this project:
- `Udacity_AZDIAS_052018.csv`: Demographics data for the general population of Germany; 891 211 persons (rows) x 366 features (columns).
- `Udacity_CUSTOMERS_052018.csv`: Demographics data for customers of a mail-order company; 191 652 persons (rows) x 369 features (columns).
- `Udacity_MAILOUT_052018_TRAIN.csv`: Demographics data for individuals who were targets of a marketing campaign; 42 982 persons (rows) x 367 (columns).
- `Udacity_MAILOUT_052018_TEST.csv`: Demographics data for individuals who were targets of a marketing campaign; 42 833 persons (rows) x 366 (columns).

There are also two Excel spreadsheets. 
- `DIAS Information Levels - Attributes 2017.xlsx` is a top-level list of attributes and descriptions, organized by informational category. 
- `DIAS Attributes - Values 2017.xlsx` is a detailed mapping of data values for each feature in alphabetical order.

The data is provided by Bertelsmann Arvato Analytics, and it cannot be publicly shared.

## File structure
``` markdown
│   Arvato Project Workbook.ipynb // Notebook, store reports and machine learning models
│   clean.py    // store cleaning functions
│   README.md
│   requirements.txt // required library for running the notebook
│
├───models
│       kmeans_18_clusters.pkl  // the trained KMeans models
│       pca_reduce.pkl          // the trained PCA model
│
└───results
        clustered_azdias        // label group for each individuals in `azdias`.
        clustered_customers     // label group for each customers in `customers`
        prediction.csv          // predictions whether an individual could be a new customers of the company.
```

## Results
The main findings are included in this [repo](https://github.com/milynox/Arvato-Project-Udacity-DS-final-project) and my [notion post](https://milynox.notion.site/milynox/Customer-Segmentation-Report-for-Arvato-Financial-Services-d27c54f19d144232b734a4ece0cf2598).

## License and Acknowledgement
This project is part of the Udacity Data Scientist Nanodegree program. Thanks Bertelsmann Arvato Analytics for providing the data.
