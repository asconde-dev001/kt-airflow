docker build -t myairflow .

docker stop airflow_container

docker rm $(docker ps -a -q)

docker run -d \
    --name airflow_container \
    -p 8080:8080 \
    -v /Users/arielconde/Desktop/KT\ Sessions/airflow/airflow_home:/app/airflow \
    -v /Users/arielconde/Desktop/KT\ Sessions/airflow/datalake:/app/datalake \
    -v /Users/arielconde/Desktop/KT\ Sessions/airflow/source:/app/source \
    myairflow

docker exec -it airflow_container /bin/bash

