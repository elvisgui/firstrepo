#!/usr/bin/env python3

import json
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import pymysql


def gettokenfromCP():

    client = BackendApplicationClient(client_id="RGU-xq-jXxa0gPkku")
    oauth = OAuth2Session(client=client)
    response = oauth.fetch_token(token_url="https://io.catchpoint.com/ui/api/token",
                                 client_id="RGU-xq-jXxa0gPkku",
                                 client_secret="dc32fc9a-82a3-4ff7-a161-f610c9e12008")
    token = response.get("access_token")
    return token


def getTemplate(testids, timeperiod, conn):

    for id in testids.keys():
        for time in timeperiod:
            start_date = time
            end_date = timeperiod[timeperiod.index(time) + 1]
            test_Template = "https://io.catchpoint.com/ui/api/v1/performance/aggregated?tests=" + id + "&aggregationType=Day&startTime=" + start_date + "&endTime=" + end_date
            try:
                response = requests.get(test_Template, headers={"Authorization": ("Bearer %s" % token)})
                test_details = response.content.decode('utf-8')
                t_json = json.loads(test_details)
                av = t_json['summary']['items'][0]['synthetic_metrics'][51]
                run = t_json['summary']['items'][0]['synthetic_metrics'][69]
                success_count = round(av / 100 * run)

                with conn:
                    cursor = conn.cursor()
                    sql1 = "INSERT INTO reportchart(`Date`,`TestID`,`TestName`,`Run`,`Success_Count`) VALUES('%s','%s','%s','%s','%s');" % (
                        start_date, id, testids[id], run, success_count)
                    cursor.execute(sql1)

                if start_date == "2020-02-29":
                    break
            except Exception as e:
                print(e)
                return False


def main():

    global token
    token = gettokenfromCP()
    testids = {#'419229': 'OLP Data Blob - China-PRD-GetVersionedBlob-SLA-Pri',
               #'461388': 'OLP Data Blob - China-PRD-PutVersionedBlob-SLA-Pri',
               #'513459': 'OLP 1.0 Ingestion - China-PRD-WriteStreamData-SLA-Pri',
               #'513463': 'OLP Data Stream - China-PRD-ReadStreamData-SLA-Pri',
               #'513468': 'OLP Data Volatile Blob - China-PRD-GetVolatileBlob-SLA-Pri',
               '513469': 'OLP Data Volatile Blob - China-PRD-PutVolatileBlob-SLA-Pri',
               '522541': 'OLP Pipeline Management - China-PRD-CreatePipeline-SLA-Pri'}

    timeperiod = ['2020-02-01', '2020-02-02', '2020-02-03', '2020-02-04', '2020-02-05', '2020-02-06', '2020-02-07', '2020-02-08', '2020-02-09','2020-02-10', '2020-02-11', '2020-02-12', '2020-02-13', '2020-02-14', '2020-02-15', '2020-02-16', '2020-02-17', '2020-02-18', '2020-02-19', '2020-02-20', '2020-02-21', '2020-02-22', '2020-02-23', '2020-02-24', '2020-02-25', '2020-02-26', '2020-02-27', '2020-02-28', '2020-02-29', '2020-03-01']
    conn = pymysql.connect(host="localhost", user='root', password='Ops1234$', database='mysql', charset='utf8')
    try:
        getTemplate(testids, timeperiod, conn)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()