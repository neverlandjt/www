import time
from structure import schema
from pyspark.sql.types import StringType
from pyspark.sql import SparkSession, SQLContext
from pyspark.sql.functions import col, from_json, window, month, dayofmonth, minute, hour, arrays_overlap, lit, array, \
    to_json, udf, collect_list, struct

if __name__ == '__main__':
    kafka_hosts = "172.31.64.180:9092,172.31.70.161:9092,172.31.64.76:9092"
    cassandra_cluster = '172.31.35.107'
    spark = SparkSession.builder.appName('WikiApp').config('spark.cassandra.connection.host', cassandra_cluster) \
        .config("spark.cassandra.auth.username", "cassandra") \
        .config("spark.cassandra.auth.password", "cassandra").getOrCreate()

    spark.conf.set('spark.sql.streaming.checkpointLocation', '/home/ubuntu/checkpoint')
    spark.conf.set('spark.cassandra.output.ignoreNulls', 'true')

    mtime_to_date = udf(lambda date: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(date / 1000)), StringType())

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_hosts) \
        .option('topic', 'wiki') \
        .option("subscribe", "wiki") \
        .load()

    ds = df.select(col("key").cast("string"), col("timestamp").cast("timestamp"),
                   from_json(col("value").cast("string"), schema).alias('value')) \
        .selectExpr('timestamp', ' value.*')

    users_query = ds.select(col("performer.user_id").alias("id"), col("performer.user_text").alias("name"),
                            col("page_id"), col("timestamp")).filter("id is not null") \
        .writeStream \
        .format("org.apache.spark.sql.cassandra") \
        .options(keyspace='project', table='users') \
        .start()

    pages_query = ds.select(col("page_id").alias("id"), col("meta.uri").alias("url"), col("page_title").alias("title"),
                            col("meta.domain").alias("domain"), col("page_namespace").alias("namespace")) \
        .writeStream \
        .format("org.apache.spark.sql.cassandra") \
        .options(keyspace='project', table='pages') \
        .start()

    spark.streams.awaitAnyTermination()
