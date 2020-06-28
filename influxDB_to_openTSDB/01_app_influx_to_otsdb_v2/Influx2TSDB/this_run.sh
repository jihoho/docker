#!/bin/bash

# 파이션 코드 실행스크립트
# version 1
# read 할 influxDB 정보
# [1]
#influx_ip="125.140.110.217"
influx_ip=$INFLUX_IP
# [2]
#influx_port=8999
influx_port=$INFLUX_PORT
# [3]
#influx_user='cschae'
influx_user=$INFLUX_USER
# [4]
#influx_pass='cschae'
influx_pass=$INFLUX_PASS
# [5]
#influx_db_name="SAMPYO_MONIT"
influx_db_name=$INFLUX_DB
# [6]
#influx_measuremet='MAIN3'
influx_measuremet=$INFLUX_MEASUREMENT
# [7] read 할 influxDB id count (데이터 수가 많은 순으로)
#id_cnt=2
id_cnt=$ID_CNT

# [8] query start time
time_start="2020/05/01-00:00:00"

# [9] query end time
time_end="2020/05/08-00:00:00"

# [10] target fieldname
#field="DRIVE_SPEED|RPM"
field= $FIELDNAME
# [11] write opentsdb metric
#metric="test.ho1"
metric=$METRIC_OUT

# [12] write opentsdb ip
#ots_ip='125.140.110.217'
ots_ip=db
# [13] write opentsdb port
#ots_port=54242
ots_port=4242
# read 단위를 결정, d 하루단위 tsdb read, h 시간단위, m 분단위
# [14]
timeunit='d'
# [15]
timelong='7'

# [16]
#pn=2
pn=$PN

# [17]
#cn=4
cn=$CN


echo ">>===================================================="
echo "실행 관련 주요 정보(this_run.sh)"
echo "influxDB ip  : "$influx_ip
echo "influxDB port   : "$influx_port
#echo "influxDB username   : "$influx_user
#echo "influxDB password   : "$influx_pass
echo "influxDB db name   : "$influx_db_name
echo "influxDB measurement name   : "$influx_measuremet
echo "influxDB id count   : "$id_cnt
echo "query start time   : "$time_start
echo "query end time   : "$time_end
echo "field    : "$field
echo
echo "openTSDB metric name     : "$metric
echo "openTSDB ip     : "$ots_ip
echo "openTSDB port     : "$ots_port
echo "time unit     : "$timeunit
echo "time long     : "$timelong
echo "producer count     : "$pn
echo "consumer count     : "$cn
echo "====================================================<<"


# time 은 스크립트 SW 실행 시간을 확인하기 위해 사용
# 인자값 7개
#                    [1]          [2]         [3]          [4]          [5]             [6]                [7]    [8]
python influx2tsdb.py $influx_ip $influx_port $influx_user $influx_pass $influx_db_name $influx_measuremet $id_cnt $time_start \
$time_end $field $metric $ots_ip $ots_port $timeunit $timelong $pn $cn
# [9]      [10]    [11]   [12]   [13]      [14]      [15]      [16][17]
echo " *** end script run for PYTHON *** "
