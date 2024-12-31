# Ikman Crawler

This project is a web crawler for the website ikman.lk. It is built using AWS Lambda functions and Python.

In order for this to be deployed to AWS, the followings should be done.
1. Create 2 Github Actions secrets named `PROD_AWS_ACCESS_KEY_ID` & `PROD_AWS_SECRET_ACCESS_KEY`
2. Create a Google Cloud Service Account and store the credentials as an AWS Secret named `gsheet_client_secret`. The same secret ARN is mentioned as `arn:aws:secretsmanager:us-east-1:310340543340:secret:gsheet_client_secret-eq2CuG` in the serverless.yml file.
3. Add an verify either the same or 2 emails in Amazon SES. In my case, I use one Gmail for sending. My personl email for receiving.
4. Create the following AWS Systems Manager Parameters.


Parameter Name | Type | Explanation |
---|---|---|
ikman_crawler_from_email | String | Here I used a test Gmail I created. This has to be verified in AWS SES. |
ikman_crawler_to_emails | StringList | Here I use my personal Gmail. It is not required to verify this. |
ikman_crawler_google_sheet | String | Create a copy of [this Google sheet](https://docs.google.com/spreadsheets/d/1JotBJ0CEUzFIoZR5rwegxt65MbfhX8rL2LkAmkXMsPg/), and use the copy. Makesure the Google Cloud Service Account mentioned in #2 is an editor of the sheet. |


## AWS Lambda Functions

These Lambdas will be updating the copy of the Google Sheet created.

The project consists of the following AWS Lambda functions:

1. `house_crawler`: This is scheduled to run once a day. It will go through multiple Ikman.lk ad list URLs listed with `Source` key in [this tab](https://docs.google.com/spreadsheets/d/1JotBJ0CEUzFIoZR5rwegxt65MbfhX8rL2LkAmkXMsPg/edit?gid=921283701#gid=921283701). Here is an [example URL](https://ikman.lk/en/ads/nugegoda/houses-for-sale?enum.bathrooms=2,3,4,5,6,7,8,9,10,10+&enum.bedrooms=4,5,6,7,8,9,10,10+&money.price.minimum=15000000&money.price.maximum=80000000) which has house for sale ads in Nawala area with 2+ bathrooms, 3+ bedrooms and price between 15 to 80 million. This lambda will save all those ads in the `Sale` tab of the Google Sheet.

2. `description_processor`: This is scheduled to run 15 mins after the 1st one. It will go through individual ads and copy the ad description text to `Description` tab.

3. `duplicate_processor`: This is scheduled to run 15 min after the 2nd one. In the [Sale](https://docs.google.com/spreadsheets/d/1JotBJ0CEUzFIoZR5rwegxt65MbfhX8rL2LkAmkXMsPg/edit?gid=1932230916#gid=1932230916), there is a column named `Status`, a dropdown which you can manually select `Ignore` and `Consider` if you want to ignore that ad or consider to revisit the ad later. Based on your last selection, for a given ad if you have selected `Ignore`, `Consider` or EMPTY (haven't taken any action) before, based on that the following logic will be executed.

The following prompt was used to get this code written by ChatGPT. The same prompt explains the logic as well.
```
I want you to iterate through all the data rows of New sheet.
Assume A is the current record of the iteration.
For the A row, do a 1:1 mapping between New and Description sheet using the URL column and find the Description column value for the A row.
Then do a text diff comparison between A.Description and all the values in the Description column in the Description sheet and find all matching rows from the Description sheet.
When doing this matching makesure line matching is 90% or more. 
When doing this matching, ignore the row where Description sheet.URL = A.URL.
Now we have a list of rows from Description sheet which has similar Description value compared to A row.
From this filtered list of Description sheet rows extract their URL column values. I assume all those values = C.
Do a 1:1 mapping between Description and New sheet again and find Status, Total, Notes column values for C, from the New sheet. Here I assume all those matching rows from New sheet = B.
If A's Status column is empty Then execute below.
	If all B rows, has empty Status
		Step X - find the minimum Total amount B rows. If there are multiple rows with minimum Total amount, just consider the 1st one.
		If the row found in X's Total is less than to A row's Total value Then 		
			1. Update A's status = "Ignore", A's Notes = the URL value of the row found in Step X
		If all B rows' Total value is greater than or equal to the A row's Total value Then
			2. Update B rows Status="Ignore" and Notes=A.URL
	Else If one or more of the B rows has Status="Consider", Then
		Step Y - find the minimum Total amount from B with "Consider" status. If there are multiple rows with minimum Total amount, just consider the 1st one.
		If A's Total is less than the minimum Total amount found in Y
			3. Update A's status = "Consider"
		Else 
			4. Update A's status = "Ignore", A's Notes = the URL value of the row found in Step Y
	Else If one or more of the B rows has Status="Ignore", then 
		Step Z - find the minimum Total amount from B with "Ignore" status. If there are multiple rows with minimum Total amount, just consider the 1st one.
		If A's Total greater than or equals to the  minimum Total amount found from Z then
			5. Update A's status = "Ignore", A's Notes = the URL value of the row found in Step Z
```

As per the above logic there are 5 outcomes. Here are the explanations.
1. `Update A's status = "Ignore", A's Notes = the URL value of the row found in Step X` - All these matching ads are posted today. I haven't reviewed them before. That is why all of them has status as Empty. In this case A's Total is higher than others. So I am going to `Ignore` A. But I might be considering the same house from a different ad. For now, A is expensive.
2. `Update B rows Status="Ignore" and Notes=A.URL` - All these matching ads are posted today. I haven't reviewed them before. That is why all of them has status as Empty. In this case A's Total is lower than others. So I am going to `Ignore` others, and keeping A as empty, because I am going to check ads with empty status. A is not in `Consider` status yet, because I am doing that change manually if I like the house.
3. `Update A's status = "Consider"` - this means the same house has been marked as `Consider` before. This time, the new ad's total is lower than previous one. So this is defintely an ad to consider.
4. `Update A's status = "Ignore", A's Notes = the URL value of the row found in Step Y` - this means the same house has been marked as `Consider` before. This time the ad is same amount or more expensive. So not considering this ad.
5. `Update A's status = "Ignore", A's Notes = the URL value of the row found in Step Z` - this means the same house has been marked as `Ignore` before. This time the ad is same amount or more expensive. So not considering this ad.

## Running the Project

To run the project, you need to deploy the AWS Lambda functions using the Serverless Framework. The `serverless.yml` file contains the configuration for the deployment. You can simply uncomment the following line and run each lambda locally. Makesure you have AWS `config` and `credential` file in this location `C:\Users\<USERNAME>\.aws`.
```
handler({}, {})
```

## Contributing

If you wish to contribute to this project, please fork the repository and submit a pull request.
