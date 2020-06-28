# influxDB_to_openTSDB

### ❖ 01_app_influx_to_otsdb
  - influxDB에서 특정 기간의 데이터를 분할 query 하여 openTSDB에 put (multiprocessing 미적용)

### ❖ 01_app_influx_to_otsdb_v2
  - influxDB에서 특정 기간의 데이터를 분할 query 하여 openTSDB에 put (multiprocessing 적용)

### ❖ 02_app_rm_outlier

  - opentsdb로 부터 주행 데이터를 쿼리하여 주행 구간 추출 및 다시 opentsdb로 put

### ❖ 03_app_get_driving

  - opentsdb로 부터 주행 데이터를 쿼리 하여 주행 구간 추출 및 다시 opentsdb로 put

### ❖ 04_app_get_stop

  - opentsdb로부터 주행 데이터와 주행 구간 데이터를 쿼리 하여 정차 구간 추출 및 다시 opentsdb로 put

### ❖ 05_app_get_parking

  - opentsdb로부터 주행 데이터를 쿼리 하여 주차 구간 추출 및 다시 opentsdb로 put

### ❖ 06_app_gps_clustering

  - opentsdb로부터 특정 구간 데이터와 구간의 GPS 데이터를 쿼리하여 clustering 하여 주요 거점(GPS)을 opentsdb에 put

### ❖ compose
  - 데이터 분석을 위해 influxDB에서 데이터를 query하여 openTSDB에 put 하는 컨테이너, openTSDB 컨테이너, 전처리 컨테이너로 docker-compose로 구성
