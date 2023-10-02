# Project Title: Ikman Crawler

This project is a web crawler for the website ikman.lk. It is built using AWS Lambda functions and Python.

## Dependencies

The project depends on the following Python libraries:

- boto3
- google-auth
- gspread
- requests
- beautifulsoup4

I also added the following AWS Systems Manager Parameters
Parameter Name | Type |
---|---|
ikman_crawler_from_email | String |
ikman_crawler_google_sheet | String |
ikman_crawler_to_emails | StringList |

The following AWS Secret to store the Google Cloud Service Account credentials.
arn:aws:secretsmanager:us-east-1:310340543340:secret:gsheet_client_secret-eq2CuG

## AWS Lambda Functions

These Lambdas will be updating [this Google Sheet](https://docs.google.com/spreadsheets/d/1FegF2xLs9dXpwhZxhd80Zz_rKIgoyygC2RpWODEZiHE/edit#gid=1932230916)

The project consists of the following AWS Lambda functions:

1. `house_crawler`: This is scheduled to run at 1:00 AM every day. It will go through multiple Ikman.lk ad list URLs can save them all in `New` tab.

2. `description_processor`: This is scheduled to run at 1:15 AM, 1:30 AM, and 1:45 AM every day. It will go through individual ads and copy the ad description to `Description` tab.

3. `duplicate_processor`: This is scheduled to run at 2:00 AM every day. It execute the below logic.

This is the prompt I used to write this code via ChatGPT.
```
I want you to iterate through all the data rows of New sheet.
Assume A is the current record of the iteration of New sheet.
For the A row, do a 1:1 mapping between New and Description sheet using the URL column and find the Description column value for the A row.
Then do a text diff comparison between A.Description and all the Description column values in the Description sheet and find all matching rows from the Description sheet. 
When doing this matching makesure line matching is 90% or more. 
When doing this matching, ignore the row where Description sheet.URL = A.URL.
Now we have a list of rows from Description sheet which has similar Description value compared to A row.
From this filtered list of Description sheet rows extract their URL column values. 
Do a 1:1 mapping between Description and New sheet and find Status, Total, Notes column values for each URL from the New sheet.
For each iteration of A row, check if A's Status is empty and execute below. 
Implement the following logic. Here I say B = all the matching rows from New sheet.
If all B rows, has empty Status
	Step Z - find the minimum Total amount from those rows with empty status. If there are multiple, just consider the 1st one.
	If the row found in Z's Total is less than to A row's Total value Then 		
		Update A's status = "Ignore", A's Notes = the URL value of the row found in Step Z
	If all B rows' Total value is greater than or equal to the A row's Total value Then
		Update B rows Status="Ignore" and Notes=A.URL
Else If one or more of the B rows has Status="Consider", then 
	Step X - find the minimum Total amount from those rows with "Consider" status. If there are multiple, just consider the 1st one.
	If A's Total is less than the minimum Total amount found in X
		Update A's status = "Consider"
	Else 
		Update A's status = "Ignore", A's Notes = the URL value of the row found in Step X
Else If one or more of the B rows has Status="Ignore", then 
	Step Y - find the minimum Total amount from those rows with "Ignore" status. If there are mulitple, just consider the 1st one.
	If A's Total greater than or equals to the  minimum Total amount found from Y then
		Update A's status = "Ignore", A's Notes = the URL value of the row found in Step Y
```


## Running the Project

To run the project, you need to deploy the AWS Lambda functions using the Serverless Framework. The `serverless.yml` file contains the configuration for the deployment.

## Contributing

If you wish to contribute to this project, please fork the repository and submit a pull request.
