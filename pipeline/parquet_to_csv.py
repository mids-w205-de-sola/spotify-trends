import pandas as pd
from datetime import datetime
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession

sc = SparkContext('local')
spark = SparkSession(sc)

read_playlists = spark.read.parquet('/tmp/extracted_playlists')
read_playlists_pd = read_playlists.toPandas()

filename = '{date:%Y-%m-%d_%H:%M:%S}.csv'.format(date=datetime.now())

read_playlists_pd.to_csv('/w205/final-project-scratchpad/csvs/' + filename, index=False)