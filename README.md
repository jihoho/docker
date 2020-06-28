# docker-compose

### ❖ opentsdb_metric_copy
  - 특정 opentsdb의 metric을 쿼리해 리턴되는 데이터를 본인이 실행하는 docker opentsdb container로 복사

### ❖ apps
  - 특정 opentsdb의 metric을 쿼리해 리턴되는 데이터를 본인이 실행하는 docker opentsdb container로 복사하고 전처리후 다시 opentsdb에 data put

### ❖ csv_to_opentsdb
  - host에서 csv 파일을 읽어 docker opentsdb container로 push

### ❖ csv2tsdb_and_preprocessing
  - host에서 csv 파일을 읽어 docker opentsdb container로 put한 후 전처리
  
### ❖ csv2tsdb_and_preprocessing_v2
  - host에서 csv 파일을 읽어 docker opentsdb container로 put한 후 전처리
  
### ❖ influxDB_to_openTSDB
  - influxdb에서 데이터를 query하여 docker opentsdb container로 put
