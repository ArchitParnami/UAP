# Urban Analytics Platform - Phase I

## Team:

Dr. Siddharth Krishnan,  Dr. Minwoo Jake Lee,  Dr. Srinivas Akella, Dr. Dimitris Papanikolaou,
Archit Parnami, Prajval Bavi


## Project Description:

Phase 1 aims at collecting data from different sources such as weather forecasts, traffic data, social media data etc and collectively synthesizing  this data towards building smart cities.


## Project Source:

https://bitbucket.org/uncc_uap/phase1


## **Collecting Live Traffic Data Using Google Traffic API**

 
Google Traffic API 
https://developers.google.com/maps/documentation/distance-matrix/

[Bitbucket Branch](https://bitbucket.org/uncc_uap/phase1/src/88f84843188caf8f0ad2d923e79ddb9b132eb7b1/GoogleTrafficAPI/?at=master)

Example:
Location -  1 Mile stretch on S Tyron Street in Downtown, Charlotte.

    origin = "35.223506,-80.848443"
    destination = "35.232499,-80.835559"


https://drive.google.com/file/d/1teMnlB8-rC1aH5WmcY00LbRiZIlazl-G/view?usp=sharing


Results:

https://drive.google.com/open?id=16EQfAW2Z9B4txc9R0P-Fkmybr0viZ2l0


Observations:

- The fluctuations in the ETA suggests that this is a busy street.
- The duration which the google API returns is estimated based on historical data and live traffic.


**Collecting Data from Charlotte Open Data Portal**
Charlotte Open Data Links: 

  There are two links, Charlotte is in the process of updating their website(Dr. Lee has been updated regarding the same), so the data is collected using two data sources.
1. https://opencharlotte-charlotte.opendata.arcgis.com/
2. https://clt-charlotte.opendata.arcgis.com/

[BitBucket Branch](https://bitbucket.org/uncc_uap/phase1/src/88f84843188caf8f0ad2d923e79ddb9b132eb7b1/open_data_portal/?at=master)

Observations:

1. A interesting dataset is Streets Detours and Street Closure. This gives the information regarding the which streets are closed and interval for which these are closed(includes future dates). We were able to extract the latitude and longitude location for the streets which are closed.

**Collecting weather data**

[OpenWeatherMap API](https://openweathermap.org/api) is used to get the weather data. We can get the current weather and also the forecast weather for 5days/3 hours interval.
Using the free API key, upto 60 calls per minute are allowed.
API calls can be made using Lat/Long, Zip, City Name, City ID. 
Right now we are using Lat/Long, so that to target the current or forecast weather for a specific area, as weather may not be similar across the city.

[BitBucket Branch](https://bitbucket.org/uncc_uap/phase1/src/88f84843188caf8f0ad2d923e79ddb9b132eb7b1/open_data_portal/?at=master)


# Charlotte Zoning Analysis For Traffic Data
- The light blue track on the map indicates the LYNX blue line extension. It starts from UNCC Campus  to Charlotte Transportation Center(CTC) in Uptown. This whole extension has 11 new stations. The existing blue line continues from CTC till 7th Street and has 15 stations.
  Total Stations = 26


![Charlotte divided into ~198 regions according to census 2010](https://d2mxuefqeaa7sj.cloudfront.net/s_9CBA0C32E3E0BE970DD00F736DAB4ACB1799FB3CB63CF644B704A3C447972EC0_1518722402399_Census+Tract.png)



![Charlotte divided into 78 regions according to Zip Codes](https://d2mxuefqeaa7sj.cloudfront.net/s_9CBA0C32E3E0BE970DD00F736DAB4ACB1799FB3CB63CF644B704A3C447972EC0_1518722784574_Zip+Codes.png)

![42 Fire Stations in Charlotte](https://d2mxuefqeaa7sj.cloudfront.net/s_9CBA0C32E3E0BE970DD00F736DAB4ACB1799FB3CB63CF644B704A3C447972EC0_1518722792254_Fire+stations.png)



![Traffic Signals  near light rail](https://d2mxuefqeaa7sj.cloudfront.net/s_9CBA0C32E3E0BE970DD00F736DAB4ACB1799FB3CB63CF644B704A3C447972EC0_1518722800644_Traffic+Signal.png)


Estimating the total number of requests / hour:-

  n =  number of regions
  p =  number of parking stations
  m = number of requests per hour
  **E = n x p x m** 
| **Zoning Type** | **Number of Regions** | **Parking Stations** | **Requests per hour** | **Total Requests Per hour** | **Total Requests Per Day** | **Cost per day for exceeding request limit of 2500 for Google API** |
| --------------- | --------------------- | -------------------- | --------------------- | --------------------------- | -------------------------- | ------------------------------------------------------------------- |
| Census 2010     | 198                   | 26                   | 4                     | 20,592                      | 494,208                    | $245.85                                                             |
| Zip Codes       | 78                    | 26                   | 4                     | 8,112                       | 194,688                    | $96.09                                                              |
| Fire Stations   | 42                    | 26                   | 4                     | 4,368                       | 104,832                    | $51.17                                                              |

[Excel Sheet](https://www.dropbox.com/s/16c4fk7ozzcqwl2/RequestEstimate.xlsx?dl=0)
[Google API Billing and Usage Limits](https://developers.google.com/maps/documentation/distance-matrix/usage-limits)


## **Waze Traffic API Analysis**
- Created a new package [WazeTrafficCalculator from the original WazeRouteCalculator](https://bitbucket.org/uncc_uap/phase1/src/856eecf9ce4a6418ca0c353ff84947928b5e00e1/WazeAPI/?at=master)
- The new package will let us query instantly based on latitude and longitude as opposed to original package which had 5 seconds of delay.
- Last night i.e 02/17/2018 I left the script running to collect traffic data between all the Fire and Rail Stations i.e 42 * 26 = 1092 requests per second were needed. We put a delay of 1 second after each request to prevent the request overload. Regardless the script crashed after 1400 requests due to overload. Here are results of those requests:
  Ti, Di → Travel Time, Travel Distance
https://drive.google.com/file/d/1YzDm0dbFahpv4TMWBVbpg3IGcRWZBGZq/view?usp=sharing

- Due to the request overload, I changed the script to sleep for 10 seconds every time Waze reported request overload. It worked initially but as the number of requests increased, the more frequent Waze started reporting overloads. 
- As an experiment i received 15 request overload error from Waze in a span of 150 requests. These requests were sent without any delay of 1 second as done previously. Here are the results of those requests:
  [Waze_Traffic_Results-2.txt](https://drive.google.com/open?id=1NYl_v91kTRu14Zybm-AfJaR_iGunU6jl)

  **Verdict:**

-   We can definitely try to get ETA data between any nodes we want using Waze but it is nearly impossible to get ETA between all the nodes at the same time unless we do some kind of distributed computing with parallelization. That means the requests have to be generated from different machines so that Waze Server couldn’t deny them. 
- We can send all requests with 1 seconds delay between each request. If we receive an overload  we can wait for 60 seconds and then start sending the requests again. This way we could collect all the data, but it would just not be at the same time.
- So collected data for 24 hours with 2 requests per second. The following plots describes the ETA from the nearest 5 fire stations to a rail station. Almost always the nearest fire station has the smallest ETA.
![Fire Stations to UNC Station by Fastest Route](https://d2mxuefqeaa7sj.cloudfront.net/s_9CBA0C32E3E0BE970DD00F736DAB4ACB1799FB3CB63CF644B704A3C447972EC0_1519151156591_Figure_1.png)
![Fire Stations to UNC Station by Shortest Route](https://d2mxuefqeaa7sj.cloudfront.net/s_9CBA0C32E3E0BE970DD00F736DAB4ACB1799FB3CB63CF644B704A3C447972EC0_1519151156607_Figure_2.png)

![Fire Stations to 9th Street Station by Fastest Route](https://d2mxuefqeaa7sj.cloudfront.net/s_9CBA0C32E3E0BE970DD00F736DAB4ACB1799FB3CB63CF644B704A3C447972EC0_1519151275669_Figure_3-1.png)
![Fire Stations to 9th Street Station by Shortest Route](https://d2mxuefqeaa7sj.cloudfront.net/s_9CBA0C32E3E0BE970DD00F736DAB4ACB1799FB3CB63CF644B704A3C447972EC0_1519151275717_Figure_3-2.png)


  


Continued Here:
[+Traffic Prediction and Analysis using LSTM](https://paper.dropbox.com/doc/Traffic-Prediction-and-Analysis-using-LSTM-alRPvlFwZTGEYPprfgVSL) 

