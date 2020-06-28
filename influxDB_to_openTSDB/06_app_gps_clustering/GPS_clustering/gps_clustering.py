#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import print_function
import time
import json
import pandas as pd
import sys
import requests
from sklearn.cluster import DBSCAN
import datetime
from collections import OrderedDict



# convert Time to Epoch
def convertTimeToEpoch(_time):
    date_time = "%s.%s.%s %s:%s:%s" %(_time[8:10], _time[5:7], _time[:4], _time[11:13], _time[14:16], _time[17:])
    pattern = "%d.%m.%Y %H:%M:%S"
    epoch = int (time.mktime(time.strptime(date_time, pattern)))
    return epoch

# convert Epoch to Time
def convertEpoch_datetime(unixtime):
    """Convert unixtime to datetime"""
    date = datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    return date # format : str




# openTSDB query하여 response return
def query_get_ids(_url, _query_params, _tags=None,_st=None,_en=None):
    headers = {'content-type': 'application/json'}

    dp = OrderedDict()    # dp (Data Point)
    dp["start"] = convertTimeToEpoch(_query_params["start"])
    dp["end"] = convertTimeToEpoch(_query_params["end"]) - int(1)   # not exactly required

    temp = OrderedDict()
    temp["aggregator"] = _query_params["aggregator"]
    temp["metric"] = _query_params["metric"]
    if _tags != None:
        temp["tags"] = _tags

    dp["queries"] = []
    dp["queries"].append(temp)
    # print(_url)
    #print " [Querying]" + json.dumps(dp, ensure_ascii=False, indent=4)
    response = requests.post(_url, data=json.dumps(dp), headers= headers)
    # print(dp)
    while response.status_code > 204:
        print(" [Bad Request] Query status: %s" % (response.status_code))
        print(" [Bad Request] We got bad request, Query will be restarted after 3 sec!\n")
        time.sleep(3)

        print(" [Querying]" + json.dumps(dp, ensure_ascii=False, indent=4))
        response = requests.post(_url, data=json.dumps(dp), headers= headers)

    res=response.json()
    dps_sum=0
    
    ve_dict=dict()
    # 차량 별 dps count 추출
    for i in range(len(res)):
        try:
            ve_dict[res[i]['tags']['VEHICLE_NUM']]+=len(res[i]['dps'])
        except KeyError:
            ve_dict[res[i]['tags']['VEHICLE_NUM']] = len(res[i]['dps'])

    print("[openTSDB query get ids]")
    print("- query time: %s ~ %s"%(_query_params['start'],_query_params['end']))
    print("- metric name: %s" %(_query_params['metric']))
    print("- fieldname: %s" % (_tags['fieldname']))
    print("- VEHICLE_NUM: %s" % (ve_dict.keys()))

    return ve_dict



# openTSDB query하여 response return
def query_openTSDB(_url, _query_params, _tags=None,_st=None,_en=None):
    headers = {'content-type': 'application/json'}

    dp = OrderedDict()    # dp (Data Point)
    dp["start"] = convertTimeToEpoch(_query_params["start"])
    dp["end"] = convertTimeToEpoch(_query_params["end"]) - int(1)   # not exactly required

    temp = OrderedDict()
    temp["aggregator"] = _query_params["aggregator"]
    temp["metric"] = _query_params["metric"]
    if _tags != None:
        temp["tags"] = _tags

    dp["queries"] = []
    dp["queries"].append(temp)
    # print(_url)
    #print " [Querying]" + json.dumps(dp, ensure_ascii=False, indent=4)
    response = requests.post(_url, data=json.dumps(dp), headers= headers)
    # print(dp)
    while response.status_code > 204:
        print(" [Bad Request] Query status: %s" % (response.status_code))
        print(" [Bad Request] We got bad request, Query will be restarted after 3 sec!\n")
        time.sleep(3)

        print(" [Querying]" + json.dumps(dp, ensure_ascii=False, indent=4))
        response = requests.post(_url, data=json.dumps(dp), headers= headers)

    res=response.json()
    dps_sum=0
    for r in res:
        dps_sum+=len(r['dps'])

    print("[openTSDB query]")
    print("- query time: %s ~ %s"%(_query_params['start'],_query_params['end']))
    print("- metric name: %s" %(_query_params['metric']))
    print("- fieldname: %s" % (_tags['fieldname']))
    print("- VEHICLE_NUM: %s" % (_tags['VEHICLE_NUM']))
    print("- aggregator: %s" % (_query_params['aggregator']))
    print("- dps sum: %d" % (dps_sum))
    return res


'''
    시작과 끝 지점의 timestamp를 기반으로 openTSDB에서 GPS 데이터 QUERY
'''
def query_gps_to_df(_url,ts_dict,_query_params, _tags=None):
    headers = {'content-type': 'application/json'}

    dp = OrderedDict()  # dp (Data Point)

    temp = OrderedDict()
    temp["aggregator"] = _query_params["aggregator"]
    temp["metric"] = _query_params["metric"]
    if _tags != None:
        temp["tags"] = _tags

    dp["queries"] = []
    dp["queries"].append(temp)


    gps_dict=dict()
    gps_dict['time']=list()
    gps_dict['carid']=list()
    ts_keys=list(ts_dict.keys())
    for i in range(len(ts_dict[ts_keys[0]])):
        st=int(ts_dict[ts_keys[0]][i])
        en=int(ts_dict[ts_keys[1]][i])
        if st > en:
            st=int(ts_dict[ts_keys[1]][i])
            en=int(ts_dict[ts_keys[0]][i])
        ts= st
        # 시작 지점으로 query time 지정
        dp['start']=ts
        dp['end']=ts+1
        response = requests.post(_url, data=json.dumps(dp), headers=headers)
        check=0
        while response.status_code > 204:
            print(" [Bad Request]3 Query status: %s" % (response.status_code))
            print(" [Bad Request] We got bad request, Query will be restarted after 3 sec!\n")
            time.sleep(3)

            # 해당 timestamp에 GPS 데이터가 없을 경우 timestamp 1씩 증가 (end 지점 이전 까지)
            dp['start']+=1
            dp['end']+=1

            # 구간 내에 GPS 데이터가 없을 경우
            if dp['end'] > en:
                print("%s ~ %s  GPS data query error\n" %(convertEpoch_datetime(st),convertEpoch_datetime(en)))
                check=1
                break

            print(" [Querying]" + json.dumps(dp, ensure_ascii=False, indent=4))
            response = requests.post(_url, data=json.dumps(dp), headers=headers)

        if check==1:
            check=0
            continue
        res = response.json()
        gps_dict["time"].append(dp['start'])
        gps_dict["carid"].append(_tags['VEHICLE_NUM'])
        for i in range(len(res)):
            try:
                gps_dict[res[i]['tags']['fieldname']].append(res[i]['dps'].values()[0])
            except KeyError:
                gps_dict[res[i]['tags']['fieldname']]=[res[i]['dps'].values()[0]]

    df=pd.DataFrame(gps_dict)
    print("\n[openTSDB GPS query & convert DataFrame]")
    print("- metric name: %s" % (_query_params['metric']))
    print("- fieldname: %s" % (_tags['fieldname']))
    print("- VEHICLE_NUM: %s" % (_tags['VEHICLE_NUM']))
    print("- aggregator: %s" % (_query_params['aggregator']))
    print("- DataFrame length: %d" % (len(df)))
    return df


'''
 eps: 기준점으로 부터의 거리 값
 min_pit: epsilon 반경 내에 있는 점의 수 
 dataframe의 해당 column을 epsilon,min points 수를 기반으로 clustering하여 dataframe return
'''
def dbscan_gps(df,col,eps,min_pts):
    print("\n\n[DBSCAN_GPS]")
    model=DBSCAN(eps=eps,min_samples=min_pts)
    model.fit(df)
    y_predict=model.fit_predict(df[col])
    df['cluster']=y_predict
    result = df[df['cluster'] != -1]
    cluster=list(set(result['cluster'].tolist()))
    for cls in cluster:
        tmp=df[df['cluster']==cls]
        print("-------------------cluster%d (count: %d)-------------------" %(cls,len(tmp)))
        for i in range(len(tmp)):
            print(" carid: %s,  time: %s ,   GPS_LAT: %f ,   GPS_LONG : %f"%(tmp.iloc[i,2],convertEpoch_datetime(tmp.iloc[i,3]),tmp.iloc[i,0],tmp.iloc[i,1]))
        print("\n")

    return result



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
def dataset_to_json(dataset,meta):
    sess = requests.Session()
    dps_sum=0
    field_list=meta['gps_field'].split("|")
    dftime = dataset['time'].tolist()
    dfcluster = dataset['cluster'].tolist()
    dfid=dataset['carid'].tolist()
    print("[dataset put openTSDB]")

    for _field in field_list:
        print("field name: %s"%(_field))
        dfval=dataset[_field].tolist()
        _buffer=[]
        count=0
        for i in range(len(dftime)):
            value=dfval[i]
            if value == 'nan' or dftime[i] == 'nan':
                continue
            elif value == 'NaN' or dftime[i] == 'NaN':
                continue
            ts = str(int(dftime[i]))
            cluster=str(dfcluster[i])
            _carid=dfid[i]
            _dict = dict()
            _dict['metric'] = str(meta['out_metric'])
            _dict["tags"] = dict()

            _dict['timestamp'] = ts
            _dict["value"] = round(value,6)
            # _dict["value"] = float(value)

            _dict["tags"]['VEHICLE_NUM'] = _carid
            _dict["tags"]["fieldname"] = _field
            _dict["tags"]["cluster"]=cluster
            _buffer.append(_dict)
            count += 1
            if len(_buffer) == 50:
                put_openTSDB(_buffer, meta["out_url"], sess)
                print('put dps count: %8d' % count, end='\r')
                _buffer = []
        if len(_buffer)!=0:
            put_openTSDB(_buffer, meta["out_url"], sess)
            print('put dps count: %8d' % count)
        dps_sum += count
    print("dps sum: %d\n" %dps_sum)
    return dps_sum


def run_clustering(meta):
   
    """ 실제 작업에 필요한 query parameter 예 - 초기값 """
    query_parameter = {
        "start": "2014-06-01 00:00:00",
        "end": "2014-06-02 00:00:00",
        "aggregator": "none",
        "metric": "____test____"
    }

    """ 쿼리 하려는 tag """
    query_tags = {
        "fieldname": "",
        "VEHICLE_NUM": ""
    }

    query_parameter['start'] = meta['time_start']
    query_parameter['end'] = meta['time_end']
    query_parameter['aggregater'] = "none"

    # print(query_parameter)

    # 차량 별로 query 하여 dataset 생성
    tot_dps_sum=0

    # meta['id'] = none 일 경우 모든 차량 query
    if meta['id']=="*":
        query_parameter['metric'] = meta["startend_metric"]
        query_tags['VEHICLE_NUM'] = meta['id']
        # 구간의 start 지점 query
        _field = meta['startend_field']
        query_tags['fieldname'] = meta['startend_field']
        ve_dict=query_get_ids(meta['in_url'],query_parameter,query_tags)
        meta['id']=list(ve_dict.keys())

    tot_df=pd.DataFrame({"GPS_LAT":[],"GPS_LONG":[],"time":[],"carid":[]})
    
    # 차량 별로 dataset 구축
    for _id in meta['id']:
        print("\n***************************** id : %s*****************************" %_id)

        query_parameter['metric'] = meta["startend_metric"]
        query_tags['VEHICLE_NUM']=_id
        #구간의 start 지점 query
        _field=meta['startend_field']
        query_tags['fieldname']= meta['startend_field']

        # start, end 지점의 timestamp query
        res = query_openTSDB(meta['in_url'], query_parameter, query_tags)
        
        '''
         구간의 start 지점의 timestamp list, end 지점의 timestamp list로 구성된 dict 생성
             {    "STOP_START": ["timestamp_1","timestamp_2"....],
                  "STOP_END": ["timestamp_1","timestamp_2"....]    }
        '''
        ts_dict = {}
        for i in range(len(res)):
            ts_dict[res[i]['tags']['fieldname']]=sorted(res[i]['dps'].keys())


        query_parameter['metric']=meta['gps_metric']
        query_tags['fieldname']= meta['gps_field']

        # start, end timestamp 지점의 GPS 데이터 query 및 dataset(dataframe) 생성
        _dataset=query_gps_to_df(meta['in_url'],ts_dict, query_parameter, query_tags)
        # print(_dataset)
        tot_df=pd.concat([tot_df,_dataset])
    # dataset의 해당 column, epsilon, min point 수를 기반으로 DBSCAN 함수 호출
    result = dbscan_gps(tot_df, meta['gps_field'].split("|"), meta['eps'], meta['min_pts'])
    # print(result)
    # clustering 된 result(DataFrame)를 openTSDB put
    dps_sum = dataset_to_json( result, meta)
    tot_dps_sum += dps_sum
    return tot_dps_sum











def brush_args():
    _len = len(sys.argv)

    if _len < 15:
        print(" 추가 정보를 입력해 주세요. 위 usage 설명을 참고해 주십시오")
        print(" python 실행파일을 포함하여 아규먼트 갯수 15개 필요 ")
        print(" 현재 아규먼트 %s 개가 입력되었습니다." % (_len))
        print(" check *this_run.sh* file ")
        exit(" You need to input more arguments, please try again \n")

    # for i in range(_len):
    #     print("%d  %s" %(i,sys.argv[i]))
    meta=dict()
    meta['in_ip'] = sys.argv[1]    # read 할 openTSDB ip
    meta['in_port'] = sys.argv[2]    # read 할 openTSDB port
    meta['in_url'] = 'http://' + meta['in_ip'] + ':' + meta['in_port'] + str('/api/query')
    meta['startend_metric'] = sys.argv[3]    # read 할 startend metric name
    meta['startend_field'] = sys.argv[4]   # read 할 startend field list
    meta['gps_metric'] = sys.argv[5]     # read 할 gps metric name
    meta['gps_field'] = sys.argv[6]      # read 할 gps field list
    meta['time_start'] = sys.argv[7]      # openTSDB query start time
    meta['time_end'] = sys.argv[8]       # openTSDB query end time
    if sys.argv[9]=='none':
        meta['id']='*'
    else:
        meta['id'] = sys.argv[9].split("|")    # read 할 target id list


    meta['out_ip'] = sys.argv[10]       # write 할 OpenTSDB ip
    meta['out_port'] = sys.argv[11]       # write 할 OpenTSDB port
    meta['out_metric'] = sys.argv[12]       # write 할 OpenTSDB metric name
    meta['out_url'] = 'http://' + meta['out_ip'] + ':' + meta['out_port'] + str('/api/put')

    meta['eps'] = float(sys.argv[13])     # clustering epsilon
    meta['min_pts'] = int(sys.argv[14]) # clustering min points



    return meta


if __name__ == "__main__":

    meta=brush_args()
    # print(meta)

    s_time=time.time()
    dps=run_clustering(meta)
    e_time=time.time()
    
    print("total run time : %.2f (sec)" %(e_time-s_time))
    print("total put dps sum: %d " %dps)
