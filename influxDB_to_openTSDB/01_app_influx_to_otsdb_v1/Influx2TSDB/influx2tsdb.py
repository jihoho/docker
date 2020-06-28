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



# convert Time to Epoch
def convertTimeToEpoch(_time):
    date_time = "%s.%s.%s %s:%s:%s" %(_time[8:10], _time[5:7], _time[:4], _time[11:13], _time[14:16], _time[17:])
    pattern = "%d.%m.%Y %H:%M:%S"
    epoch = int (time.mktime(time.strptime(date_time, pattern)))
    return epoch

'''
- RFC 3339 Date Formats
 ISO8601을 인터넷 프로토콜로 어떻게 다룰 것인지를 규정한 RFC 이다.
 ISO8601과 거의 비슷하며, 약간의 차이만 있을 뿐이다.
 예를 들면, RFC 3339에서는 'T'의 생략을 허용하지 않고, 날짜와 시간 사이의 공백을 허용한다.
 대부분의 경우, 이 둘을 상세하게 분리해서 생각하지 않아도 된다.
    '''
# convert RFC3339 to datetime
def convertRFC3339toDateTime(_time):
    date_time=datetime.datetime.strptime(_time, '%Y-%m-%dT%H:%M:%SZ')
    return date_time



# convert string to datetime
def str2datetime(dt_str):
    return datetime.datetime.strptime(dt_str, "%Y/%m/%d-%H:%M:%S")


# convert datetime to string
def datetime2str(dt):
    return dt.strftime('%Y/%m/%d-%H:%M:%S')

# string to RFC3339
# YYYY/mm/dd-HH:MM:SS -> YYYY-mm-ddTHH:MM:SSZ
def str2RFC3339(_time):
    rfc_time="%s-%s-%sT%s:%s:%sZ" %(_time[0:4],_time[5:7],_time[8:10],_time[11:13],_time[14:16],_time[17:])
    return rfc_time


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



# influxDB time 형식 YYYY-mm-ddTHH:MM:SSZ(RFC3339)
# YYYY-mm-ddTHH:MM:SSZ -> Epoch time
def convertRFC3339ToEpoch(_time):
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

    # convert query string time to RFC3339
    q_start=str2RFC3339(q_start)
    q_end=str2RFC3339(q_end)

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
    _query=make_query(fieldname,measurement,_id,q_start,q_end)
    result = client.query(_query)
    
    #dataframe으로 변환
    result = pd.DataFrame(result[measurement])
    # print('length:', len(result['time']))
    # print(result)
    _len=len(result)

    print("[influxDB query]")
    print("query time: %s ~ %s\nfieldname : %s\ntotal lines: %d\n\n" % (q_start, q_end,','.join(fieldname),_len))

    return result,_len


# json list(openTSDB put 형식)를 openTSDB에 http post
def put_openTSDB(_list, url, sess):
    headers = {'content-type': 'application/json'}


    try:
        response = sess.post(url, data=json.dumps(_list), headers=headers)

        while response.status_code > 204:
            print("[Bad Request] Put status: %s" % (response.status_code))
            print("[Bad Request] we got bad request, Put will be restarted after 3 sec!\n")
            time.sleep(3)

            print("[Put]" + json.dumps(_list, ensure_ascii=False, indent=4))
            response = sess.post(url, data=json.dumps(_list), headers=headers)

        # print ("[Put finish and out]")

    except Exception as e:
        print("[exception] : %s" % (e))



'''
    Dataframe을 json형식 (openTSDB put 형식) 으로 변환하여 buffer 50개씩 put_openTSDB 호출
    openTSDB put 형식
    [
    {
        "metric": "metric_name",
        "timestamp": "[epoch time]",
        "values": int or float,
        "tags": {
                    "VEHICLE_NUM": "[car id]",
                    "field_name": "[field name]"
                }
    },....
    ]
    '''
def df_to_openTSDB(df,meta):
    sess = requests.Session()
    tot_cnt=0
    _carid = df['car_id'].iloc[0]
    dftime = df['time'].tolist()

    print("[influx query data put openTSDB]")
    # print("car id : %s " % _carid)

    # meta['field'] : field name list
    for _field in meta['field']:
        dfval=df[_field].tolist()
        _buffer=[]
        count=0
        print("field name: %s" %_field)
        for i in range(len(dftime)):
            value = dfval[i]
            # skip NaN value & ts
            if value == 'nan' or dftime[i] == 'nan':
                continue
            elif value == 'NaN' or dftime[i] == 'NaN':
                continue
            ts = convertRFC3339ToEpoch(dftime[i])
            ts = str(ts)
            _dict = dict()
            _dict['metric'] = str(meta['metric'])
            _dict["tags"] = dict()

            _dict['timestamp'] = ts
            _dict["value"] = value

            _dict["tags"]['VEHICLE_NUM'] = _carid
            _dict["tags"]["fieldname"] = str(_field)

            _buffer.append(_dict)
            count+=1
            if len(_buffer) == 50:
                put_openTSDB(_buffer,meta["ots_url"],sess)
                print('put dps count: %8d' %count, end='\r')
                _buffer = []
        put_openTSDB(_buffer, meta["ots_url"], sess)
        print('put dps count: %8d' %count)
        tot_cnt+=count
    return tot_cnt



# influxDB connection 및 차량 별로 influxDB_query_by_timedelta 호출
def InfluxToTSDB(meta):
    #influxDB connection
    client=influxconnection(meta["in_ip"],meta['in_port'],meta['in_user'],meta['in_pass'],meta['in_db_name'])
    dps_total = 0
    s_time=time.time()
    
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
                id_dps_num+=df_to_openTSDB(queried_data, meta)
                print("dps sum: %d"%(id_dps_num))
                print("-------------------------------------------------------------")
            else:
                print("\n-------------------------------------------------------------")

            date_from=date_end
            # print("date_from: %s date_to :%s" %(date_from,date_to))
            # print(date_from<date_to)
        dps_total+=id_dps_num
    e_time=time.time()
    print("\n[influxDB -> OpenTSDB] done")
    print("total dps sum: %d " %dps_total)
    print("total run time : %.2f (sec) " %(e_time-s_time))


def brush_args():
    _len = len(sys.argv)

    if _len < 16:
        print(" 추가 정보를 입력해 주세요. 위 usage 설명을 참고해 주십시오")
        print(" python 실행파일을 포함하여 아규먼트 갯수 16개 필요 ")
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
    meta['carid'] = sys.argv[7].split('|')       # read 할 influxDB id list
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