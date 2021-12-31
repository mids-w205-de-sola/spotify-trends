#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf

def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractPlaylistsJob") \
        .getOrCreate()

    raw_playlist = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "playlists") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()
    
    playlist = raw_playlist.select(raw_playlist.timestamp.cast('string'), raw_playlist.value.cast('string'))

    extracted_playlist = playlist \
        .rdd \
        .map(lambda r: Row(timestamp=r.timestamp, value=r.value)) \
        .toDF()
    extracted_playlist.show()

    extracted_playlist \
        .write \
        .mode("overwrite") \
        .parquet("/tmp/extracted_playlists")


if __name__ == "__main__":
    main()
