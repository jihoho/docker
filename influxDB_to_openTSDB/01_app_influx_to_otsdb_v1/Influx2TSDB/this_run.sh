#!/bin/bash

# 파이션 코드 실행스크립트
# version 1
# read 할 influxDB 정보
# [1]
# influxdb 서버 ip
influx_ip="125.140.110.217"
# [2]
# influxdb 서버 port
influx_port=8999
# [3]
# influxdb 서버 접속 username
influx_user='cschae'
# [4]
# influxdb 서버 접속 password
influx_pass='cschae'
# [5]
# influxdb DATABASES name
influx_db_name="SAMPYO_MONIT"
# [6]
# influxdb MEASUREMENTS name
influx_measuremet='MAIN3'
# [7]
# 차량 id
carid="01225789003"
#carid='01225789003|01225797247'

# [8] query start time
time_start="2020/05/01-00:00:00"

# [9] query end time
time_end="2020/05/30-00:00:00"

# [10] target fieldname
field="DRIVE_SPEED|RPM"

# [11] write opentsdb metric
metric="test"

# [12] write opentsdb ip
ots_ip='125.140.110.217'
# [13] write opentsdb port
ots_port=54242

# read 단위를 결정, d 하루단위 tsdb read, h 시간단위, m 분단위
# [14] 쿼리할 시간/기간 단위
timeunit='d'
# [15] 쿼리할 시간/기간
timelong='7'


echo ">>===================================================="
echo "실행 관련 주요 정보(this_run.sh)"
echo "influxDB ip  : "$influx_ip
echo "influxDB port   : "$influx_port
#echo "influxDB username   : "$influx_user
#echo "influxDB password   : "$influx_pass
echo "influxDB db name   : "$influx_db_name
echo "influxDB measurement name   : "$influx_measuremet
echo "influxDB carid   : "$carid
echo "query start time   : "$time_start
echo "query end time   : "$time_end
echo "field    : "$field
echo
echo "openTSDB metric name     : "$metric
echo "openTSDB ip     : "$ots_ip
echo "openTSDB port     : "$ots_port
echo "time unit     : "$timeunit
echo "time long     : "$timelong
echo "====================================================<<"


# time 은 스크립트 SW 실행 시간을 확인하기 위해 사용
# 인자값 7개
#                    [1]          [2]         [3]          [4]          [5]             [6]                [7]    [8]
python influx2tsdb.py $influx_ip $influx_port $influx_user $influx_pass $influx_db_name $influx_measuremet $carid $time_start \
$time_end $field $metric $ots_ip $ots_port $timeunit $timelong
# [9]      [10]    [11]   [12]   [13]      [14]      [15]
echo " *** end script run for PYTHON *** "