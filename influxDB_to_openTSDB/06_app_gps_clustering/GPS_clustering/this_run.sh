#!/bin/bash


# read 할 open tsdb 정보
# [1]
#ip_in="125.140.110.217"
ip_in=db
# [2]
#port_in=60010
port_in=4242
# [3]
#startend_metric="stop_startend"
startend_metric=$STARTEND_METRIC
# [4]
#startend_field="STOP_START|STOP_END"
startend_field=$STARTEND_FIELD

# [5]
#gps_metric="csv_data2"
gps_metric=$GPS_METRIC
# [6]
#gps_field="GPS_LAT|GPS_LONG"
gps_field=$GPS_FIELD
# [7]
time_start='2020/05/01-00:00:00'
# [8]
time_end='2020/06/01-00:00:00'
# [9] id = 'none' 일 경우 전체 차량
#id='1225789009|1225789003'
id='none'
# write 할 open tsdb 정보
# [10]
#ip_out="125.140.110.217"
ip_out=db
# [11]
#port_out=54242
port_out=4242
# [12]
metric_out=$METRIC_OUT
#metric_out='stop_clustering_all_3'

# [13]
# 약 212m
#epsilon=0.002
epsilon=$EPS

# [14]
#min_pts=5
min_pts=$MIN_PTS



echo ">>===================================================="
echo "실행 관련 주요 정보(this_run.sh)"
echo "1.openTSDB input ip  : "$ip_in
echo "2.openTSDB input port   : "$port_in
echo "3.startend metric name   : "$startend_metric
echo "4.startend field name  : "$startend_field
echo "5.gps metric name   : "$gps_metric
echo "6.gps field name   : "$gps_field
echo "7.query start time   : "$time_start
echo "8.query end time   : "$time_end
echo "9.target id    : "$id
echo
echo "10.openTSDB output ip     : "$ip_out
echo "11.openTSDB output port     : "$port_out
echo "12.openTSDB output metric name    : "$metric_out
echo "13.clustering epsilon distance     : "$epsilon
echo "14.clustering min points    :  "$min_pts
echo "====================================================<<"


# time 은 스크립트 SW 실행 시간을 확인하기 위해 사용 
# 인자값 18개 
#                         [1]    [2]      [3]              [4]             [5]         [6]
python gps_clustering.py $ip_in $port_in $startend_metric $startend_field $gps_metric $gps_field \
$time_start $time_end $id $ip_out $port_out $metric_out $epsilon $min_pts
#[7]         [8]      [9] [10]     [11]      [12]

echo " *** end script run for PYTHON *** "