#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import print_function
import time
import json
import pandas as pd
import sys
import requests
from datetime import datetime
import influxdb
import datetime
import pcs


# convert Time to Epoch
def convertTimeToEpoch(_time):
    date_time = "%s.%s.%s %s:%s:%s" %(_time[8:10], _time[5:7], _time[:4], _time[11:13], _time[14:16], _time[17:])
    pattern = "%d.%m.%Y %H:%M:%S"
    epoch = int (time.mktime(time.strptime(date_time, pattern)))
    return epoch


# convert RFV3339 to datetime
def convertRFV3339toDateTime(_time):
    date_time=datetime.datetime.strptime(_time, '%Y-%m-%dT%H:%M:%SZ')
    return date_time



# convert string to datetime
def str2datetime(dt_str):
    return datetime.datetime.strptime(dt_str, "%Y/%m/%d-%H:%M:%S")


# convert datetime to string
def datetime2str(dt):
    return dt.strftime('%Y/%m/%d-%H:%M:%S')


#  YYYY/mm/dd-HH:MM:SS -> YYYY-mm-ddTHH:MM:SSZ
def str2RFV3339(_time):
    rfv_time="%s-%s-%sT%s:%s:%sZ" %(_time[0:4],_time[5:7],_time[8:10],_time[11:13],_time[14:16],_time[17:])
    return rfv_time


# YYYY/mm/dd-HH:MM:SS 형식의 string에 시간 단위를 더하여 return
def strday_delta(_s, _type, _h_scale):
    _dt  = str2datetime(_s)
    if _type == 'days' :
        _dt += datetime.timedelta(days = _h_scale)
    elif _type == 'hrs':
        _dt += datetime.timedelta(hours = _h_scale)
    elif _type == 'mins':
        _dt += datetime.timedelta(minutes = _h_scale)
    _str = datetime2str(_dt)
    return _str



# influxDB time 형식 YYYY-mm-ddTHH:MM:SSZ(RFV3339)
# YYYY-mm-ddTHH:MM:SSZ -> Epoch time
def convertRFV3339ToEpoch(_time):
    _time=str(_time)
    date_time = "%s.%s.%s %s:%s:%s" %(_time[8:10], _time[5:7], _time[:4], _time[11:13], _time[14:16], _time[17:19])
    pattern = "%d.%m.%Y %H:%M:%S"
    epoch = int (time.mktime(time.strptime(date_time, pattern)))
    return epoch



# influxDB connection
def influxconnection(ip,port,username,password,db_name):
    """데이터 저장을 위한 Influxdb client 연결"""

    in_client = influxdb.InfluxDBClient(host=ip,
                                            port=port,
                                            username=username,
                                            password=password,
                                            database=db_name
                                             )
    print('\n----------------------------------------------------')
    print('InfluxDB Client Connected')
    print('address:',ip+':'+str(port))
    print('databse:', db_name)
    print('----------------------------------------------------\n')
    return in_client


# field name, measurement(table), car id , query start time, query end time을 parameter로 DML 구문 생성 후 return
def make_query(field_list,measurement,_id,q_start,q_end):
    fieldname=','.join(field_list)

    # convert query string time to RFV3339
    q_start=str2RFV3339(q_start)
    q_end=str2RFV3339(q_end)

    _query='SELECT '+ fieldname + ', car_id'+' FROM %s' % measurement + " WHERE time >= '%s' and time < '%s' and car_id = '%s'" % (q_start, q_end, _id)
    # print(_query)
    return _query



'''
    쿼리 기간을 시간단위로 분할
    meta['timeunit'] d(하루), h(시간), m(분)
    meta['timelong'] 단위 계수
'''
def influxDB_query_by_timedelta(client,_id,_date, meta, dys=None, hrs=None, mins=None):
    if dys != None:
        _t_scale = meta['days']
        _type = 'days'
    elif hrs != None:
        _t_scale = meta['hrs']
        _type = 'hrs'
    elif mins != None:
        _t_scale = meta['mins']
        _type = 'mins'

    assert type(_t_scale) == int, 'not integer for t_scale'
    q_start = _date

    # delta 시간만큼 시간 변환한 string
    q_end = strday_delta(_date, _type, _t_scale)
    if q_end > meta['time_end']:
        q_end=meta['time_end']

    # influxDB query
    queried_data,_len=influxDB_query(client,meta['field'],meta['in_measurement'],_id,q_start,q_end)

    # influxDB result(dataframe), query end time return
    return queried_data,q_end


#influxDB 데이터 쿼리
def influxDB_query(client,fieldname,measurement,_id,q_start,q_end):
    """데이터 쿼리"""
    #DML 구문 생성
    _query = make_query(fieldname, measurement, _id, q_start, q_end)
    result = client.query(_query)
    
    #dataframe으로 변환
    result = pd.DataFrame(result[measurement])
    # print('length:', len(result['time']))
    # print(result)
    _len=len(result)

    print("[influxDB query]")
    print("query time: %s ~ %s\nfieldname : %s\ntotal lines: %d\n\n" % (q_start, q_end,','.join(fieldname),_len))

    return result,_len


# id 별 데이터 수 query 하여 dataframe return
def influxDB_query_id(client,measurement,_field,q_start,q_end,id_cnt):
    """데이터 쿼리"""
    # DML 구문 생성
    s_time=time.time()
    _query="SELECT * FROM (SELECT COUNT(%s) FROM %s WHERE time > '%s' AND time < '%s' GROUP BY %s)"\
    %(_field,measurement,str2RFV3339(q_start),str2RFV3339(q_end),"car_id")

    s_time=time.time()
    result = client.query(_query)
    result = pd.DataFrame(result[measurement])
    result = result.sort_values(by=['count'],ascending=False).reset_index(drop=True)
    _len=len(result)
    result = result[:id_cnt]
    # print(result)
    # print(_len)

    e_time=time.time()

    print("[influxDB query id]")
    print("query time: %s ~ %s"%(q_start, q_end))
    print("total id count: %d" %(_len))
    print("query id run time : %.2f(sec)\n" %(e_time-s_time))
    return result, _len


# influxDB connection 및 차량 별로 influxDB_query_by_timedelta 호출
def InfluxToTSDB(meta):
    #influxDB connection
    client=influxconnection(meta["in_ip"],meta['in_port'],meta['in_user'],meta['in_pass'],meta['in_db_name'])
    dps_total = 0
    s_time=time.time()
    _id_df,_=influxDB_query_id(client,meta['in_measurement'],meta['field'][0],meta['time_start'],meta['time_end'],meta['id_cnt'])

    print("get %d ids... " %(meta['id_cnt']))
    for i in range(len(_id_df)):
        print("%d. id : %s, count: %d" %(i+1,str(_id_df.iloc[i,0]),int(_id_df.iloc[i,1])))
    meta['carid']=list(_id_df['car_id'])
    print("\n")

    workers = pcs.Workers(meta['pn'], meta['cn'])
    works_basket_list = workers.start_work(meta)
    for _id in meta['carid']:
        # query start time
        date_from=meta['time_start']
        # query end time
        date_to= meta['time_end']
        #read할 단위 지정
        dys = meta['days']
        hrs = meta['hrs']
        mins = meta['mins']
        id_dps_num=0
        print('*'*30+"car id : %s"%_id+"*"*30)

        # query start time 부터 query end time 까지 read 단위 만큼 분할하여 query
        while(date_from!=None):
            queried_data, date_end=influxDB_query_by_timedelta(client,_id,date_from,meta, dys=dys, hrs=hrs, mins=mins)
            if date_to <= date_end: date_end = None
            if len(queried_data)!=0:
                start=0
                end=start+len(queried_data)//meta['pn']
                for idx in range(meta['pn']):
                    if idx == meta['pn']-1:
                        end= len(queried_data)
                    while (works_basket_list[idx].full()):
                        time.sleep(0.5)
                    works_basket_list[idx].put(queried_data[start:end])
                    start=end
                    end=start+len(queried_data)//meta['pn']

            date_from=date_end
            # print("date_from: %s date_to :%s" %(date_from,date_to))
            # print(date_from<date_to)
    lines=workers.report()
    totallines=0
    for line in lines:
        totallines+=line
    e_time=time.time()
    print("\n[influxDB -> OpenTSDB] done")
    print("total process lines: %d " %totallines)
    print("total run time : %.2f (sec) " %(e_time-s_time))


def brush_args():
    _len = len(sys.argv)

    if _len < 18:
        print(" 추가 정보를 입력해 주세요. 위 usage 설명을 참고해 주십시오")
        print(" python 실행파일을 포함하여 아규먼트 갯수 18개 필요 ")
        print(" 현재 아규먼트 %s 개가 입력되었습니다." % (_len))
        print(" check *this_run.sh* file ")
        exit(" You need to input more arguments, please try again \n")

    # for i in range(_len):
    #     print("%d  %s" %(i,sys.argv[i]))
    meta=dict()
    meta['in_ip'] = sys.argv[1]    # read 할 influxDB ip
    meta['in_port'] = sys.argv[2]    # read 할 influxDB port
    meta['in_user'] = sys.argv[3]    # read 할 influxDB user name
    meta['in_pass'] = sys.argv[4]    # read 할 influxDB password
    meta['in_db_name'] = sys.argv[5]     # read 할 influxDB database name
    meta['in_measurement'] = sys.argv[6]       # read 할 influxDB measurement(table) name
    meta['id_cnt'] = int(sys.argv[7])      # read 할 influxDB id count (데이터 수가 많은 순으로)
    meta['time_start'] = sys.argv[8]      # read 할 influxDB query start time
    meta['time_end'] = sys.argv[9]       # read 할 influxDB query end time
    meta['field'] = sys.argv[10].split('|')      # read 할 influxDB query target field name
    
    meta['metric'] = sys.argv[11]       # write 할 OpenTSDB metric name
    meta['ots_ip'] = sys.argv[12]       # write 할 OpenTSDB ip
    meta['ots_port'] = sys.argv[13]       # write 할 OpenTSDB port
    meta['ots_url'] = 'http://' + meta['ots_ip'] + ':' + meta['ots_port'] + str('/api/put')

    # read 단위, d(하루), h(시간), m(분)
    meta['timeunit'] =sys.argv[14]
    meta['timelong'] =sys.argv[15]
    meta['days'] = None
    meta['hrs'] = None
    meta['mins'] = None

    meta['pn']=int(sys.argv[16])
    meta['cn']=int(sys.argv[17])


    _tlong = meta['timelong']
    _tlong = int(_tlong, base=10)
    if meta['timeunit'] == 'd':
        meta['days'] = _tlong

    elif meta['timeunit'] == 'h':
        meta['hrs'] = _tlong

    elif meta['timeunit'] == 'm':
        meta['mins'] = _tlong

    return meta


if __name__ == "__main__":

    meta=brush_args()
    # print(meta)


    s_time=time.time()
    df= InfluxToTSDB(meta)
    e_time=time.time()
