# Traffic Prediction and Analysis using LSTM
**Route: Fire station  34 to  Old Concord Station**
Traffic Patterns from Monday to Friday

![](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431456200_2018-04-09.png)
![](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431456220_2018-04-10.png)
![](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431456226_2018-04-11.png)

![](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431456232_2018-04-12.png)
![](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431456254_2018-04-13.png)


Traffic Pattern on Saturday  and Sunday

![](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431470944_2018-04-14.png)
![](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431470950_2018-04-15.png)


All Patterns:

![](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1525409266720_TrafficPatterns.png)


**Prediction using Model trained on All Days(Left) vs Weekdays(Right)**
Training Set: March 17 to April 16 (31 days)
Test Set: April 17 (Tuesday)
Epochs : 10


![Random Seed 42](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431563288_Plot_All_days_Seed42.png)
![Random Seed 42](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431563294_Plot_Weekdays_Seed42.png)


 

![Seed 7](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431958660_Plot_All_days_Seed7.png)
![Seed 7](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524431958632_Plot_Weekdays_Seed7.png)

![Seed 64](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524432002896_Plot_All_days_Seed64.png)
![Seed 64](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1524432002906_Plot_Weekdays_Seed64.png)


Training Set: March 17 to April 30 (45 days)
Test Set: May 1 (Tuesday)
Epochs : 20


![Model Trained only on All days(45)](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1525404160200_Prediction_Alldays.png)
![Model Trained only on Weekdays(31)](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1525404147462_Prediction_Weekdays.png)



![Residual Plot](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1525404202382_ResidualPlots.png)
![Residual plot with area under curve](https://d2mxuefqeaa7sj.cloudfront.net/s_2A4C8D2C33085547EAB08B272E29146D6CF3300B24C3E967EA5E1CCBC653FCA7_1525404202416_ResidualPlots_Area.png)


